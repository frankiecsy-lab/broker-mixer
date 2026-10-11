"""FastAPI 閘道：把 Brokery 的統一輸出映射為 HTTP 接口，並提供網頁控制台。

只作映射：取數、複權校验、能力声明與錯誤口徑全部由 brokery.core.Brokery 決定，本模組不重複實現。
所有接口一律返回 {"status", "data", "message"}；data 為 DataFrame 時展開為 {"columns", "rows"}（缺失值
一律為 null），為元資料時為物件。業務失敗仍為 HTTP 200（由 status 表達），4xx 只用於請求本身不合法
與鑑權失敗，令客戶端只需看一個欄位。

連券商的取數接口一律受理 raw 查詢參數（?raw=1）：為真時 data 的欄位與值即該券商自帶的格式，信封與
狀態口徑完全不變，故同一接口可同時供出統一格式與原始格式。
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

from brokery import Brokery, CodeError, store
from brokery.brokers.base import (
    ACCOUNT_COLUMNS,
    BAR_MINUTES,
    BROKER_COLUMNS,
    COLUMNS,
    K_COLUMNS,
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


class StreamWorker:
    """一個券商一條 K 線串流：在後台執行緒中跑 Brokery.stream_kline，事件經佇列交回連接。

    Brokery 的串流會阻塞至 seconds 結束，且推送回呼在券商自己的執行緒到達，因此這裡只跳一次線程
    （call_soon_threadsafe），不在回呼內做任何耗時工作。同一券商只容許一條串流：富途的推送回調是按
    連線設置（set_handler），兩條同時進行會互相覆蓋，其中一條收尾時的 stop() 更會把另一條的訂閱一併
    退掉。名額因此要待執行緒真正結束才釋放（且先釋放才發 end/error），故 stop() 只標記結束並回報還差
    多少秒。
    """

    def __init__(self, brokery: Brokery, logger, broker: str, codes: tuple[str, ...], ktype: str,
                 count: int, autype: str | None, seconds: float, loop: asyncio.AbstractEventLoop,
                 queue: asyncio.Queue, *, raw: bool = False) -> None:
        self.broker, self.codes, self.ktype = broker, codes, ktype
        self._brokery, self._logger = brokery, logger
        self.count, self.autype, self.seconds = count, autype, seconds
        self.raw = raw
        self._loop, self._queue = loop, queue
        self._ends_at = time.monotonic() + seconds
        self._stopping = False
        self.on_done = None  # 由建立者指派：名額要待執行緒真正結束才歸還
        self._thread = threading.Thread(target=self._run, name=f"stream-{broker}", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def release_in(self) -> int:
        """還剩多少秒才會真正釋放該券商的串流名額。"""
        return max(0, round(self._ends_at - time.monotonic()))

    def stop(self) -> None:
        """請求結束。執行緒無法被強制中止，故只標記；名額在 _run 結束時才釋放。"""
        self._stopping = True

    def push(self, payload: dict) -> None:
        """由任意執行緒推入事件：只經一次 call_soon_threadsafe 進入事件循環。"""
        self._loop.call_soon_threadsafe(self._queue.put_nowait, payload)

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
            self.push({"event": event, "broker": self.broker, "message": str(result["message"])})

    def _on_update(self, code: str, rows: list[dict]) -> None:
        """券商推送：把該代碼目前完整的 bar 交回連接，客戶端以最新一份覆蓋整張圖。

        回呼送來的是字典列表（各券商的 BarMerger/NativeBars 即返回此形式），不是 DataFrame。
        """
        self.push({"event": "update", "broker": self.broker, "code": code,
                   "data": rows_payload(rows)})


def auto_refresh_codes(brokery: Brokery, logger) -> None:
    """快照過舊時在背景重拉全量 CODES；未過舊或已關閉自動更新時直接返回。

    只在啟動時做一次，絕不在請求內同步重拉：全量重拉實測約 6 秒，而離線讀回同一份快照只需
    0.03 秒，把更新放進請求路徑會令第一次搜尋慢兩百倍。閘道可能在重拉完成前已關閉，屆時本次
    更新只是失敗並記進快照的 last_refresh_error，不影響已存放的舊快照。
    """
    limit = codes_max_age_seconds()
    if limit <= 0:
        return
    try:
        meta = store.load_meta(store.CODES_DATASET)
    except store.StoreError:
        meta = {}  # 尚未有快照：視為最舊，沒有離線資料可用，必須拉一次
    if not store.meta_stale(meta, limit):
        return
    result = brokery.refresh_codes()
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
        """建立唯一的 Brokery 實例並全程複用：各適配器的連線為惰性，券商後端未啟動時仍能正常開機。"""
        app.state.brokery = Brokery(sources=sources, autype=autype)
        logger.info(
            "啟動：來源 %s，預設複權 %s，監聽 %s:%s，日誌 %s",
            ", ".join(sources) or "無", autype, settings.api_host, settings.api_port,
            settings.api_log_dir / api_log.LOG_FILE,
        )
        # 快照過舊才在背景重拉：不阻塞啟動，也不放進任何請求的路徑（見 auto_refresh_codes）
        if CODES_SOURCE in sources:
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

    @app.get("/health")
    def health() -> dict:
        """存活檢查：不需金鑰，只回報配置，不取任何券商資料。"""
        return {
            "status": True,
            "data": {
                "sources": list(sources),
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
                "ktypes": sorted(BAR_MINUTES),
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
    def codes(name: str | None = None) -> dict:
        """離線讀回已存放的 CODES（parquet），不需要任何券商連線。"""
        return guarded("/codes", lambda: app.state.brokery.get_code(name) if name else app.state.brokery.get_code())

    @app.get("/codes/meta", dependencies=[auth])
    def codes_meta(name: str | None = None) -> dict:
        """CODES 快照的元資料（行數、存放時間、距今秒數、是否過舊、上次更新失敗的原因）。
        單行 DataFrame，欄位為 core.CODES_META_COLUMNS；離線執行，不需要任何券商連線。"""
        return guarded("/codes/meta",
                       lambda: app.state.brokery.get_code_meta(name) if name
                       else app.state.brokery.get_code_meta())

    @app.get("/codes/refresh", dependencies=[auth])
    def codes_refresh(markets: str | None = None, force: bool = False) -> dict:
        """重拉全量 CODES 並更新離線快照（需券商連線，實測約 6 秒）。某品種明顯縮細時拒絕覆蓋，
        只向快照的來源券商取（core.CODES_SOURCE），不混入其他券商的標識体系。"""
        return guarded("/codes/refresh",
                       lambda: app.state.brokery.refresh_codes(_split(markets) or None, force=force))

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

    def release(broker: str, worker: StreamWorker) -> None:
        """歸還該券商的串流名額：只認得自己那一個，不會誤除後來者的註冊。"""
        if app.state.streams.get(broker) is worker:
            app.state.streams.pop(broker, None)

    @app.websocket("/stream")
    async def stream(ws: WebSocket) -> None:
        """K 線串流（WebSocket）。客戶端送 {"action":"subscribe","codes":[…],"ktype":…,"count":…,
        "broker":…,"autype":…,"seconds":…,"raw":…} 開始，{"action":"stop"} 結束；服务端返回
        {"event":"subscribed"|"update"|"closed"|"end"|"error"}。raw 為真時每次 update 的欄位即該
        券商 bar 的原生欄位（取數與推送語義不變）。

        歷史起點由 /kline 取，本處只推更新，每次 update 帶該代碼目前完整的 bar，客戶端整份覆蓋即可，
        不需要自己合併。ktype、autype 與代碼是否支持一律由 Brokery 判定，失敗以 error 事件原樣返回，
        這裡不重複判斷。
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
        current: StreamWorker | None = None
        try:
            while True:
                action = await ws.receive_json()
                kind = str(action.get("action", "")).lower()
                if kind == "stop":
                    if current is not None:
                        current.stop()
                        await ws.send_json({"event": "closed", "broker": current.broker,
                                            "release_in": current.release_in()})
                    continue
                if kind != "subscribe":
                    await ws.send_json({"event": "error", "message": f"bad_action: {kind or '空'}"})
                    continue

                broker = str(action.get("broker", "futu"))
                codes = tuple(action.get("codes") or ([str(action["code"])] if action.get("code") else []))
                busy = app.state.streams.get(broker)
                if busy is not None:
                    await ws.send_json({
                        "event": "error", "broker": broker,
                        "message": f"stream_busy: {broker} 已有串流（{','.join(busy.codes)} {busy.ktype}）；"
                                   f"同一券商只容許一條，約 {busy.release_in()} 秒後可重新訂閱",
                    })
                    continue
                try:
                    count = int(action.get("count", 60))
                    seconds = float(action.get("seconds") or settings.api_stream_seconds)
                except (TypeError, ValueError) as exc:
                    await ws.send_json({"event": "error", "broker": broker,
                                        "message": f"bad_request: {exc}"})
                    continue

                worker = StreamWorker(
                    app.state.brokery, logger, broker, codes, str(action.get("ktype", "1m")),
                    count, action.get("autype"), min(seconds, settings.api_stream_seconds),
                    loop, queue, raw=bool(action.get("raw", False)),
                )
                worker.on_done = lambda worker=worker: release(broker, worker)
                app.state.streams[broker] = worker
                logger.info("WS 訂閱：%s %s %s ×%d（%s 秒）", broker, ",".join(codes),
                            worker.ktype, count, worker.seconds)
                await ws.send_json({"event": "subscribed", "broker": broker, "codes": list(codes),
                                    "ktype": worker.ktype, "seconds": worker.seconds})
                worker.start()
                current = worker
        except (WebSocketDisconnect, RuntimeError) as exc:
            logger.info("WS 斷開：%s（%s）", peer, type(exc).__name__)
        finally:
            pumping.cancel()
            if current is not None:
                current.stop()

    return app
