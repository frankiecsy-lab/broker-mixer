"""FastAPI 閘道：把 Brokery 的統一輸出映射為 HTTP 接口，並提供網頁控制台。

只作映射：取數、複權校验、能力声明與錯誤口徑全部由 brokery.core.Brokery 決定，本模組不重複實現。
所有接口一律返回 {"status", "data", "message"}；data 為 DataFrame 時展開為 {"columns", "rows"}（缺失值
一律為 null），為元資料時為物件。業務失敗仍為 HTTP 200（由 status 表達），4xx 只用於請求本身不合法
與鑑權失敗，令客戶端只需看一個欄位。

連券商的取數接口一律受理 raw 查詢參數（?raw=1）：為真時 data 的欄位與值即該券商自帶的格式，信封與
狀態口徑完全不變，故同一接口可同時供出統一格式與原始格式。

券商開關喜好（broker_prefs.json）只由本模組讀寫：Brokery 只接受 disabled= 參數並在呼叫時統一拒絕被停用
者，不讀寫任何檔案，因此三個界面共用同一份喜好而 core 仍可在離線腳本中直接構造。
"""
from __future__ import annotations

import asyncio
import hmac
import math
import threading
import time
from contextlib import asynccontextmanager
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Request, Security, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

from brokery import Brokery, CodeError, chart, prefs, store
from brokery.brokers.base import (
    ACCOUNT_COLUMNS,
    BROKER_COLUMNS,
    COLUMNS,
    K_COLUMNS,
    KTYPE_ORDER,
    native_columns,
)
from brokery.config import get_settings
from brokery.core import ACC_FILTERS, CODES_SOURCE, codes_max_age_seconds

from . import log as api_log

UI_FILE = Path(__file__).with_name("ui.html")
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
BEARER = HTTPBearer(auto_error=False)
SECRET_QUERY_KEYS = ("api_key", "key")  # 日誌中一律遮罩的查詢參數


def _json_value(value):
    """單個欄位值 → JSON 可序列化的值。

    必須逐值轉型：pandas 的 numpy 標量（int64/float64）不是 JSON 可序列化物件，而 float("nan") 會令
    json.dumps 輸出非法的 NaN。缺失值一律為 null，不以任何數字湊出。
    """
    if value is None or value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return None if math.isnan(value) else float(value)
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return int(pd.Timestamp(value).timestamp())
    if isinstance(value, str):
        return value
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):  # 非标量（如 list）：pd.isna 會回傳陣列
        pass
    return str(value)


def frame_payload(frame: pd.DataFrame) -> dict:
    """DataFrame → {"columns": [...], "rows": [[...]]}：欄位順序固定，空表亦保留欄位。"""
    return {
        "columns": [str(name) for name in frame.columns],
        "rows": [[_json_value(value) for value in row] for row in frame.itertuples(index=False)],
    }


def rows_payload(rows: list[dict]) -> dict:
    """bar 字典 → {"columns": [...], "rows": [[...]]}：欄位即各行的鍵。

    串流的回呼為字典而非 DataFrame（見 brokers.base 的 BarMerger/NativeBars），欄位由資料本身決定：
    統一格式時即 K_COLUMNS，raw=True 時即該券商自帶的鍵，這裡不憑格式假設補欄位。
    """
    columns = native_columns(rows)
    return {
        "columns": columns,
        "rows": [[_json_value(row.get(name)) for name in columns] for row in rows],
    }


def envelope(result: dict) -> dict:
    """Brokery 的返回信封 → JSON 可序列化結構。"""
    return {
        "status": bool(result["status"]),
        "data": frame_payload(result["data"]),
        "message": str(result["message"]),
    }


def _split(value: str | None) -> tuple[str, ...]:
    """逗號分隔的查詢參數 → 名單（大寫為統一市場/種子名稱）。"""
    return tuple(item.strip().upper() for item in (value or "").split(",") if item.strip())


def _names(value: str | None) -> tuple[str, ...]:
    """逗號分隔的券商名稱 → 名單。不可經 _split：券商名稱是小寫標識（futu），大寫化即變成不存在的名字。"""
    return tuple(item.strip().lower() for item in (value or "").split(",") if item.strip())


def masked_query(request: Request) -> str:
    """請求的查詢串，鑑權參數遮罩：日誌要能重現請求，但不能把金鑰寫進檔案。"""
    parts = [
        f"{name}={'***' if name.lower() in SECRET_QUERY_KEYS else value}"
        for name, value in request.query_params.multi_items()
    ]
    return "?" + "&".join(parts) if parts else ""


def ws_key_ok(ws: WebSocket, api_key: str) -> bool:
    """WebSocket 的鑑權：瀏覽器無法為握手自訂標頭，故除 X-API-Key 與 Bearer 外亦受理 ?api_key=。"""
    supplied = ws.query_params.get("api_key") or ws.headers.get("x-api-key")
    if not supplied:
        header = ws.headers.get("authorization", "")
        supplied = header[7:].strip() if header.lower().startswith("bearer ") else None
    return bool(supplied) and hmac.compare_digest(supplied, api_key)


def stream_key(broker: str, ktype: str, codes: tuple[str, ...], count: int,
               autype: str | None, raw: bool) -> tuple:
    """一份串流請求的簽名：同簽名即同一份請求（共用或接手），簽名不同即另一條可並行的串流。

    代碼先排序，故只換代碼順序仍算同一份。券商與週期是簽名的前兩項，界面按這兩項停某一格時照樣
    可比對（見 /stream 的 stop）。
    """
    return (broker, ktype, tuple(sorted(codes)), int(count), autype or "", bool(raw))


class StreamWorker:
    """一份請求一條 K 線串流：在後台執行緒中跑 Brokery.stream_kline，事件經佇列交回連接。

    Brokery 的串流會阻塞至 seconds 結束，且推送回呼在券商自己的執行緒到達，因此這裡只跳一次線程
    （call_soon_threadsafe），不在回呼內做任何耗時工作。一份串流由請求簽名界定（見 stream_key）：
    同簽名即同一份請求，向券商只訂閱一次並送給所有在收的連接；簽名不同即另一條串流，故同一券商
    同一週期亦可並行多條（富途的推送自帶 k_type 與代碼，各份只收自己那份，見 brokers.futu_broker）。
    名額要待執行緒真正結束才釋放（且先釋放才發 end/error），故 stop() 只標記結束並回報還差多少秒。
    也正因為該執行緒仍在跑，同一份請求再訂閱時可接手呢條仍未走完嘅串流（見 join），唔使重新排隊。

    一條串流可同時送給多條連接（見 _subs）：桌面 GUI 與 Web UI 同睇同一份 bar 時，向券商只訂閱一次，
    兩邊各自收到同一份 update。最後一條連接退出才真正結束該串流（見 leave），否則先退出者會把別家嘅
    串流一併停掉。
    """

    def __init__(self, brokery: Brokery, logger, broker: str, codes: tuple[str, ...], ktype: str,
                 count: int, autype: str | None, seconds: float, loop: asyncio.AbstractEventLoop,
                 queue: asyncio.Queue, *, raw: bool = False) -> None:
        self.broker, self.codes, self.ktype = broker, codes, ktype
        self._brokery, self._logger = brokery, logger
        self.count, self.autype, self.seconds = count, autype, seconds
        self.raw = raw
        # 收呢條串流嘅連接：佇列 → 該佇列所屬嘅事件循環。建立時即綁住創建它嘅連接。
        self._subs: dict[asyncio.Queue, asyncio.AbstractEventLoop] = {queue: loop}
        self._ends_at = time.monotonic() + seconds
        self._stopping = False
        self.on_done = None  # 由建立者指派：名額要待執行緒真正結束才歸還
        self._thread = threading.Thread(target=self._run, name=f"stream-{broker}", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def release_in(self) -> int:
        """還剩多少秒才會真正歸還該份請求的串流名額。"""
        return max(0, round(self._ends_at - time.monotonic()))

    def stop(self) -> None:
        """請求結束。執行緒無法被強制中止，故只標記；名額在 _run 結束時才釋放。"""
        self._stopping = True

    @property
    def watchers(self) -> int:
        """而家有多少條連接在收呢條串流。"""
        return len(self._subs)

    def join(self, loop: asyncio.AbstractEventLoop, queue: asyncio.Queue) -> bool:
        """多一條連接收呢條串流：串流本身照跑，只是多送一份事件。

        回傳是否由「沒有人收」回到有（即接手呢條仍在跑的串流）：該情況下要撤銷 stop()，
        因為用戶重新訂閱即表示要繼續收，同一條串流不需要重新向券商訂閱。
        """
        revived = not self._subs
        self._subs[queue] = loop
        if revived:
            self._stopping = False
        return revived

    def leave(self, queue: asyncio.Queue) -> bool:
        """一條連接不再收呢條串流（客戶端停止或連線已斷開）。

        回傳是否已沒有人收：只有最後一個退出才結束該串流，先退出者不該把別家仍在看的串流停掉。
        """
        self._subs.pop(queue, None)
        if not self._subs:
            self.stop()
            return True
        return False

    def push(self, payload: dict) -> None:
        """由任意執行緒推入事件：每條在收的連接各經一次 call_soon_threadsafe 進入其事件循環。
        已請求停止即不再推送：按「停止」之後不該再收到 bar（名額仍照原時窗計算，見 stop）。
        訂閱者由事件循環增減、本處在券商執行緒，故先取快照再送，避免邊送邊變。"""
        if self._stopping:
            return
        for queue, loop in list(self._subs.items()):
            loop.call_soon_threadsafe(queue.put_nowait, payload)

    def _run(self) -> None:
        try:
            result = self._brokery.stream_kline(
                self.codes, ktype=self.ktype, count=self.count, broker=self.broker,
                autype=self.autype, seconds=self.seconds, on_update=self._on_update,
                raw=self.raw,
            )
        except Exception as exc:  # 串流在後台執行緒，抛出到這裡才不會靜靜消失
            result = {"status": False, "message": f"stream_failed: {type(exc).__name__}: {exc}"}
        self._logger.info("串流 %s %s（%s）→ status=%s %s", self.broker, ",".join(self.codes),
                          self.ktype, bool(result["status"]), result["message"])
        if self.on_done is not None:  # 先歸還名額再發 end/error：客戶端收到收尾事件即代表可重新訂閱
            self.on_done()
        if not self._stopping:
            event = "end" if result["status"] else "error"
            self.push({"event": event, "broker": self.broker, "ktype": self.ktype,
                       "message": str(result["message"])})

    def _on_update(self, code: str, rows: list[dict]) -> None:
        """券商推送：把該代碼目前完整的 bar 交回連接，客戶端以最新一份覆蓋整張圖。

        回呼送來的是字典列表（各券商的 BarMerger/NativeBars 即返回此形式），不是 DataFrame。
        一條連接可同時有多個週期的串流，故每個事件一律帶 ktype，客戶端按此分派返對應嘅圖。
        """
        self.push({"event": "update", "broker": self.broker, "ktype": self.ktype, "code": code,
                   "data": rows_payload(rows)})


def auto_refresh_codes(brokery: Brokery, logger) -> None:
    """預設券商的快照過舊時在背景重拉全量 CODES；未過舊或已關閉自動更新時直接返回。

    只在啟動時做一次，絕不在請求內同步重拉：全量重拉實測約 6 秒，而離線讀回同一份快照只需
    0.03 秒，把更新放進請求路徑會令第一次搜尋慢兩百倍。只更新 CODES_SOURCE 一檔：各家重拉都要
    數秒，啟動時逐家拉會把啟動拖成十幾秒，其他券商的快照由界面上的「更新離線 CODES」按需拉。
    閘道可能在重拉完成前已關閉，屆時本次更新只是失敗並記進快照的 last_refresh_error，
    不影響已存放的舊快照。

    該券商已在 BROKER 管理中停用時直接返回：被停用者不經過任何動作，啟動日誌也不該留一條無意義的
    警告（重新啟用後下一次啟動照常自動更新）。
    """
    if CODES_SOURCE not in brokery.sources():
        return
    limit = codes_max_age_seconds()
    if limit <= 0:
        return
    try:
        meta = store.load_meta(store.codes_dataset(CODES_SOURCE))
    except store.StoreError:
        meta = {}  # 尚未有快照：視為最舊，沒有離線資料可用，必須拉一次
    if not store.meta_stale(meta, limit):
        return
    result = brokery.refresh_codes(broker=CODES_SOURCE)
    line = f"CODES 自動更新 → status={bool(result['status'])} {result['message']}"
    if result["status"]:
        logger.info(line)
    else:
        logger.warning(line)


def create_app(sources: tuple[str, ...] | None = None, autype: str | None = None,
               api_key: str | None = None) -> FastAPI:
    """建立應用；參數省略時一律取 .env（測試可直接傳入）。

    API_KEY 未設定時拒絕建立應用：閘道在同一個 HTTP 端口上返回戶口與資金，未設金鑰即等同
    把戶口開放給整個網路。
    """
    settings = get_settings()
    sources = tuple(settings.api_sources) if sources is None else tuple(sources)
    autype = settings.api_autype if autype is None else autype
    api_key = settings.api_key if api_key is None else api_key
    if not api_key:
        raise RuntimeError(
            "API_KEY 未設定：請在 .env 加上 API_KEY=<自訂金鑰> 後重新啟動"
            "（閘道會返回戶口與資金，未設金鑰即拒絕啟動，避免未鑑權即可讀到戶口資料）"
        )

    recent_logs = api_log.setup_logging(settings.api_log_level, settings.api_log_dir)
    logger = api_log.get_logger()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """建立唯一的 Brokery 實例並全程複用：各適配器的連線為惰性，券商後端未啟動時仍能正常開機。

        生效集合由 .env 的 API_SOURCES 與 broker_prefs.json 共同決定：本處只讀檔並把被停用者交予
        Brokery，之後的開關由 /brokers/prefs/update 即時套用，不需重建實例（重建會令 app.state.streams
        中的舊適配器變成孤兒，連線也洩漏）。
        """
        disabled = prefs.load_disabled()
        app.state.brokery = Brokery(sources=sources, autype=autype, disabled=disabled)
        logger.info(
            "啟動：來源 %s（已停用 %s），預設複權 %s，監聽 %s:%s，日誌 %s",
            ", ".join(app.state.brokery.sources()) or "無",
            ", ".join(sorted(disabled)) or "無", autype, settings.api_host, settings.api_port,
            settings.api_log_dir / api_log.LOG_FILE,
        )
        # 快照過舊才在背景重拉：不阻塞啟動，也不放進任何請求的路徑（見 auto_refresh_codes）
        if CODES_SOURCE in app.state.brokery.sources():
            threading.Thread(target=auto_refresh_codes, args=(app.state.brokery, logger),
                             name="codes-refresh", daemon=True).start()
        yield
        app.state.brokery.close()
        logger.info("關閉：已斷開所有券商連線")

    app = FastAPI(
        title="brokery api",
        description="把 Brokery 的統一輸出（標的清單、K 線、串流、戶口與資金）映射為 HTTP/WebSocket。",
        lifespan=lifespan,
    )
    app.state.api_key = api_key
    app.state.recent_logs = recent_logs
    app.state.settings = settings
    app.state.streams = {}

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """每個請求記錄一行：方法、路徑、查詢（金鑰遮罩）、狀態碼與耗時。"""
        started = time.monotonic()
        response = await call_next(request)
        logger.info(
            "%s %s%s → HTTP %d（%.0f ms）",
            request.method, request.url.path, masked_query(request),
            response.status_code, (time.monotonic() - started) * 1000,
        )
        return response

    async def require_key(
        header_key: str | None = Security(API_KEY_HEADER),
        credential: HTTPAuthorizationCredentials | None = Security(BEARER),
    ) -> None:
        """自訂金鑰：X-API-Key 與 Authorization: Bearer 兩者其一，常數時間比較。"""
        supplied = header_key or (credential.credentials if credential else None)
        if supplied is None:
            raise HTTPException(
                status_code=401,
                detail="unauthorized: 需要 API Key（X-API-Key 或 Authorization: Bearer）",
            )
        if not hmac.compare_digest(supplied, api_key):
            raise HTTPException(status_code=403, detail="forbidden: API Key 不正確")

    auth = Depends(require_key)

    def logged(path: str, result: dict) -> dict:
        """記錄業務結果（status=False 為 WARNING，因為它不會抛異常），並轉為 JSON 信封。"""
        line = f"{path} → status={bool(result['status'])} {result['message']}"
        if result["status"]:
            logger.info(line)
        else:
            logger.warning(line)
        return envelope(result)

    def guarded(path: str, call) -> dict:
        """把 CodeError 等輸入錯誤還原為統一信封：業務失敗由 status 表達，不變成 HTTP 500。"""
        try:
            result = call()
        except (CodeError, ValueError) as exc:
            result = {"status": False, "data": pd.DataFrame(), "message": str(exc)}
        except Exception as exc:
            result = {"status": False, "data": pd.DataFrame(),
                      "message": f"api_failed: {type(exc).__name__}: {exc}"}
        return logged(path, result)

    # ---------- 控制台與元資料 ----------

    @app.get("/", include_in_schema=False)
    def console() -> FileResponse:
        """網頁控制台。頁面本身不含資料，資料仍由帶金鑰的接口取得，故不需鑑權。"""
        return FileResponse(UI_FILE)

    @app.get("/static/{name}", include_in_schema=False)
    def static_asset(name: str) -> FileResponse:
        """界面共用的靜態資源（chart.js 與 echarts.min.js）：圖表規格只有一份，三個界面載入同一份，
        嚴禁各自複製。與控制台頁面一樣不需鑑權，路徑由 brokery.chart.static_dir() 決定。"""
        try:
            path = chart.static_file(name)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"static_missing: {name}")
        return FileResponse(path)

    @app.get("/health")
    def health() -> dict:
        """存活檢查：不需金鑰，只回報配置，不取任何券商資料。sources 為生效集合（已扣除被停用者）。"""
        return {
            "status": True,
            "data": {
                "sources": app.state.brokery.sources(),
                "prefs_file": str(prefs.prefs_path()),
                "autype": autype,
                "log_file": str(settings.api_log_dir / api_log.LOG_FILE),
                "stream_seconds": settings.api_stream_seconds,
            },
            "message": "ok",
        }

    @app.get("/capabilities", dependencies=[auth])
    def capabilities() -> dict:
        """各券商的能力聲明與固定欄位：呼叫其他接口前可先查支援範圍，不支持的組合一律明確報錯。"""
        adapters = app.state.brokery.adapters()
        return {
            "status": True,
            "data": {
                "sources": list(adapters),
                "autype": app.state.brokery.autype,
                "columns": {
                    "codes": list(COLUMNS),
                    "kline": list(K_COLUMNS),
                    "accounts": list(ACCOUNT_COLUMNS),
                    "brokers": list(BROKER_COLUMNS),
                },
                # 週期按由短至長返回：界面（含多週期頁的九個週期）照單羅列，唔准各處自己排
                "ktypes": list(KTYPE_ORDER),
                "acc_filters": list(ACC_FILTERS),
                "adapters": {
                    name: {
                        "capabilities": list(adapter.capabilities),
                        "kline_symbol_types": list(adapter.kline_symbol_types),
                        "autypes": list(adapter.autypes),
                        "stream_ktypes": list(adapter.stream_ktypes),
                        "stream_autypes": list(adapter.stream_autypes),
                        "acc_types": list(adapter.acc_types),
                        "kline_anchor": adapter.kline_anchor,
                    }
                    for name, adapter in adapters.items()
                },
            },
            "message": "ok",
        }

    @app.get("/brokers", dependencies=[auth])
    def brokers(broker: str | None = None) -> dict:
        """各券商的連線狀態與探測延遲，欄位固定為 BROKER_COLUMNS。以一次戶口查詢探測（只需連線與
        鑑權，不需要行情權限），各家並行，連不上者 connected=False、latency_ms 為 null。"""
        return guarded("/brokers", lambda: app.state.brokery.get_brokers(broker=broker))

    @app.get("/brokers/prefs", dependencies=[auth])
    def brokers_prefs() -> dict:
        """券商開關喜好（全域，三界面共用）：欄位為 core.PREF_COLUMNS，一律列出全部可用券商而不只係
        生效者，否則被停用者喺頁面上消失、無法重新啟用。只讀檔與讀內建狀態，不取任何券商資料。"""
        return guarded("/brokers/prefs", lambda: app.state.brokery.get_broker_prefs())

    @app.get("/brokers/prefs/update", dependencies=[auth])
    def brokers_prefs_update(enabled: str | None = None) -> dict:
        """設定生效的券商並寫檔：enabled 為逗號分隔的完整生效名單（省略即全部停用，與界面取消全部
        開關一致）。即時生效，不需重建 Brokery；返回與 /brokers/prefs 同樣的清單，界面一次呼叫即重畫。
        名稱不在可用券商內時明確報錯且不改變任何狀態。"""
        names = _names(enabled)

        def apply() -> dict:
            result = app.state.brokery.set_broker_enabled(names)
            if result["status"]:  # 失敗時 core 已不改狀態，檔也不該跟着變
                prefs.save_disabled([name for name in sources if name not in names])
            return result

        return guarded("/brokers/prefs/update", apply)

    @app.get("/logs", dependencies=[auth])
    def logs(limit: int = 200) -> dict:
        """最近若干條閘道日誌（由新到舊），對應 OpenD/IB Gateway 的日誌窗。"""
        records = list(reversed(app.state.recent_logs.tail(limit)))
        return {
            "status": True,
            "data": {
                "columns": ["ts", "time", "level", "message"],
                "rows": [[r["ts"], r["time"], r["level"], r["message"]] for r in records],
            },
            "message": f"ok: {len(records)} 條日誌",
        }

    # ---------- 清單與代碼 ----------

    @app.get("/codes", dependencies=[auth])
    def codes(broker: str = CODES_SOURCE) -> dict:
        """離線讀回某券商存放的 CODES（parquet），不需要任何券商連線。各券商各一檔，互不混雜。"""
        return guarded("/codes", lambda: app.state.brokery.get_code(broker))

    @app.get("/codes/meta", dependencies=[auth])
    def codes_meta(broker: str = CODES_SOURCE) -> dict:
        """某券商 CODES 快照的元資料（行數、存放時間、距今秒數、是否過舊、上次更新失敗的原因）。
        單行 DataFrame，欄位為 core.CODES_META_COLUMNS；離線執行，不需要任何券商連線。"""
        return guarded("/codes/meta", lambda: app.state.brokery.get_code_meta(broker))

    @app.get("/codes/refresh", dependencies=[auth])
    def codes_refresh(broker: str = CODES_SOURCE, markets: str | None = None,
                      force: bool = False) -> dict:
        """向某券商重拉全量 CODES 並更新該券商的離線快照（需券商連線，實測約 6 秒）。
        某品種明顯縮細時拒絕覆蓋；快照內容由該券商聲明的能力決定（不提供股票者只含期貨與指數）。"""
        return guarded("/codes/refresh",
                       lambda: app.state.brokery.refresh_codes(_split(markets) or None,
                                                               broker=broker, force=force))

    @app.get("/stocks", dependencies=[auth])
    def stocks(markets: str | None = None, broker: str | None = None,
               raw: bool = False) -> dict:
        """股票清單。markets 為逗號分隔的統一市場前綴（如 HK,US），省略時用 Brokery 的預設；
        broker 只向該券商取，未啟用或不提供該品種時明確報錯。"""
        return guarded("/stocks", lambda: app.state.brokery.list_stocks(
            _split(markets) or None, broker=broker, raw=raw
        ))

    @app.get("/futures", dependencies=[auth])
    def futures(roots: str | None = None, markets: str | None = None,
                broker: str | None = None, raw: bool = False) -> dict:
        """期貨清單（含主連與各到期月）。roots 為逗號分隔的期貨 root（如 ES,HNQ）；
        markets 只取屬於該市場的合約（期貨接口本身沒有市場參數，故由 Brokery 按市場篩掉種子）。"""
        return guarded("/futures", lambda: app.state.brokery.list_futures(
            _split(roots) or None, markets=_split(markets) or None, broker=broker, raw=raw
        ))

    @app.get("/indices", dependencies=[auth])
    def indices(symbols: str | None = None, markets: str | None = None,
                broker: str | None = None, raw: bool = False) -> dict:
        """指數清單。symbols 為逗號分隔的指數符號；markets 的處理同期貨清單。"""
        return guarded("/indices", lambda: app.state.brokery.list_indices(
            _split(symbols) or None, markets=_split(markets) or None, broker=broker, raw=raw
        ))

    @app.get("/all", dependencies=[auth])
    def all_codes(markets: str | None = None, raw: bool = False) -> dict:
        """一次取得股票、期貨與指數。"""
        return guarded("/all", lambda: app.state.brokery.list_all(
            markets if markets is None else _split(markets), raw=raw
        ))

    @app.get("/convert", dependencies=[auth])
    def convert(code: str, source: str = "ib") -> dict:
        """統一代碼 → 該券商原生合約。"""
        return guarded("/convert", lambda: app.state.brokery.convert(code, source))

    # ---------- K 線與戶口 ----------

    @app.get("/kline", dependencies=[auth])
    def kline(code: str, ktype: str = "day", count: int = 60, broker: str = "futu",
              autype: str | None = None, raw: bool = False) -> dict:
        """K 線，欄位固定為 K_COLUMNS（raw=True 時為該券商 bar 的原生欄位）。autype 省略時用
        API_AUTYPE；不支持的複權或品種由 Brokery 明確返回 status=False，不會靜靜改用另一種價格。"""
        return guarded("/kline", lambda: app.state.brokery.get_kline(
            code, ktype=ktype, count=count, broker=broker, autype=autype, raw=raw
        ))

    @app.get("/accounts", dependencies=[auth])
    def accounts(broker: str | None = None, acc_type: str = "all", currency: str | None = None,
                 raw: bool = False) -> dict:
        """戶口與資金，欄位固定為 ACCOUNT_COLUMNS（raw=True 時為各券商戶口的原生記錄）；一律只列
        真實且已啟用的戶口。raw=True 時不可按 acc_type 過濾（原生記錄沒有該欄位），由 Brokery 明確
        返回 status=False。"""
        return guarded("/accounts", lambda: app.state.brokery.get_accounts(
            broker=broker, acc_type=acc_type, currency=currency, raw=raw
        ))

    # ---------- 串流 ----------

    def release(key: tuple, worker: StreamWorker) -> None:
        """歸還該份請求的串流名額：只認得自己那一個，不會誤除同簽名後來者的註冊。"""
        if app.state.streams.get(key) is worker:
            app.state.streams.pop(key, None)

    @app.websocket("/stream")
    async def stream(ws: WebSocket) -> None:
        """K 線串流（WebSocket）。客戶端送 {"action":"subscribe","codes":[…],"ktype":…,"count":…,
        "broker":…,"autype":…,"seconds":…,"raw":…} 開始，{"action":"stop","broker":…,"ktype":…} 結束
        （省略 ktype 即停該券商在本連接上的全部串流，同一週期有幾條即一併停）；服务端返回
        {"event":"subscribed"|"update"|"closed"|"end"|"error"}。raw 為真時每次 update 的欄位即該
        券商 bar 的原生欄位（取數與推送語義不變）。

        歷史起點由 /kline 取，本處只推更新，每次 update 帶該代碼目前完整的 bar，客戶端整份覆蓋即可，
        不需要自己合併。ktype、autype 與代碼是否支持一律由 Brokery 判定，失敗以 error 事件原樣返回，
        這裡不重複判斷。

        一條連接可同時訂閱多個週期（各週期各自一條串流執行緒），所有事件一律帶 ktype 供客戶端分派。
        呢樣係多週期界面（例如 3×3）只用一條 WS 嘅依據：瀏覽器每來源的併發連線得約 6 條，九格各開
        一條會排到塞住。

        一份串流由請求簽名（券商、週期、代碼、根數、復權、raw）界定：同簽名即同一份請求，閘道只向
        券商訂閱一次，每條連接各收到同一份 update，故桌面 GUI 與 Web UI 可同時睇同一張圖而唔使互相等
        名額；其中一方停止或斷線不影響另一方，最後一方退出才結束該串流。簽名不同即另一條串流，同一
        券商同一週期亦可並行多條（例如兩格同週期但代碼不同），不會再返回 stream_busy。
        """
        if not ws_key_ok(ws, api_key):
            await ws.close(code=4403)  # 未鑑權：不返回任何券商資料
            return
        await ws.accept()
        peer = ws.client.host if ws.client else "?"
        logger.info("WS 連線：%s", peer)

        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_running_loop()

        async def pump() -> None:
            """把佇列中的事件送出；連接斷開即結束。"""
            while True:
                await ws.send_json(await queue.get())

        pumping = asyncio.create_task(pump())
        workers: dict[tuple, StreamWorker] = {}   # 本連接上的訂閱：請求簽名 → 串流（同一週期可有多條）
        try:
            while True:
                action = await ws.receive_json()
                kind = str(action.get("action", "")).lower()
                if kind == "stop":
                    broker = str(action.get("broker", ""))
                    ktype = str(action.get("ktype", ""))
                    for key, worker in list(workers.items()):
                        if (broker and key[0] != broker) or (ktype and key[1] != ktype):
                            continue
                        # 先由本連接的訂閱表除名：執行緒要收尾先歸還名額（app.state.streams），但已指示
                        # 停止的訂閱不能再被下一次 stop 重複發 closed。同一週期有幾條即逐條停、逐條發 closed。
                        workers.pop(key, None)
                        # 本連接不再收呢條串流：仍有別條連接在收即照跑，最後一個退出才真正結束
                        worker.leave(queue)
                        await ws.send_json({"event": "closed", "broker": worker.broker,
                                            "ktype": worker.ktype, "release_in": worker.release_in()})
                    continue
                if kind != "subscribe":
                    await ws.send_json({"event": "error", "message": f"bad_action: {kind or '空'}"})
                    continue

                broker = str(action.get("broker", "futu"))
                codes = tuple(action.get("codes") or ([str(action["code"])] if action.get("code") else []))
                ktype = str(action.get("ktype", "1m"))
                try:
                    count = int(action.get("count", 60))
                    seconds = float(action.get("seconds") or settings.api_stream_seconds)
                except (TypeError, ValueError) as exc:
                    await ws.send_json({"event": "error", "broker": broker,
                                        "message": f"bad_request: {exc}"})
                    continue
                autype, raw = action.get("autype"), bool(action.get("raw", False))
                key = stream_key(broker, ktype, codes, count, autype, raw)

                running = app.state.streams.get(key)
                left = running.release_in() if running is not None else 0
                if running is not None and left > 0:
                    # 同一份請求已有串流在跑即加入佢：向券商只訂閱一次，每條連接各收一份 update。呢個正正
                    # 係桌面 GUI 與 Web UI 可以同時睇同一張圖嘅依據，唔使互相等名額。
                    # 「停止」只標記結束，該執行緒其實仍在推送（Brokery.stream_kline 要待 seconds 走完才返回），
                    # 故一時無人收嘅串流照樣可被接手（resumed），就是用戶要嘅「繼續」；否則只會白得一段
                    # 睇唔到最新價嘅空窗。
                    # 簽名不同（換代碼、根數、復權或 raw）即另一份請求：唔使等佢，直接另起一條並行。
                    revived = running.join(loop, queue)
                    workers[key] = running
                    logger.info("WS %s現有串流：%s %s %s（尚餘 %d 秒，%d 條連接在收）",
                                "接手" if revived else "加入", broker, ",".join(codes), ktype,
                                left, running.watchers)
                    await ws.send_json({"event": "subscribed", "broker": broker,
                                        "codes": list(codes), "ktype": running.ktype,
                                        "seconds": left, "resumed": revived,
                                        "shared": running.watchers > 1})
                    continue

                worker = StreamWorker(
                    app.state.brokery, logger, broker, codes, ktype,
                    count, autype, min(seconds, settings.api_stream_seconds),
                    loop, queue, raw=raw,
                )
                worker.on_done = lambda worker=worker, key=key: release(key, worker)
                # 同簽名但時窗已走完（left 為 0）時即覆蓋：release() 只認得自己嗰個，舊執行緒收尾唔會誤除
                # 呢一份新註冊。
                app.state.streams[key] = worker
                workers[key] = worker
                logger.info("WS 訂閱：%s %s %s ×%d（%s 秒）", broker, ",".join(codes),
                            worker.ktype, count, worker.seconds)
                await ws.send_json({"event": "subscribed", "broker": broker, "codes": list(codes),
                                    "ktype": worker.ktype, "seconds": worker.seconds})
                worker.start()
        except (WebSocketDisconnect, RuntimeError) as exc:
            logger.info("WS 斷開：%s（%s）", peer, type(exc).__name__)
        finally:
            pumping.cancel()
            for worker in workers.values():
                # 斷開不等於券商已退訂：仍有別條連接在收即照跑，無人收時 leave 已標記結束，
                # 其後任何連接再訂閱同一份請求即接手，唔使等時窗走完
                worker.leave(queue)

    return app
