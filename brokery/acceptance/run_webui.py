"""驗收 `brokery_webui`（Web UI）：以存根閘道（FastAPI + uvicorn，另佔一個系統分配的端口，不連任何
券商、不與 `.env` 的 API_PORT 相沖）提供 `/capabilities`、`/accounts`、`/stocks`（及 /futures、
/indices）、`/codes`、`/codes/meta`、`/codes/refresh`、`/kline`、`/brokers/prefs`、
`/brokers/prefs/update` 與 `/stream`（WebSocket，按閘道協定：一條連接容許多個訂閱，
subscribed/update/closed 一律帶 ktype，stop 可按 ktype 只停其中一個），
再以 `create_app(base_url=存根, api_key=測試金鑰)` 起真正的 Web UI 應用，核對：

轉發口徑：`/api/kline` 帶齊標的、週期、根數與券商；週期與根數省略時不得自行補上第二套預設；信封
（含 status=False 的業務失敗）原樣透傳；`/api/accounts` 與 `/api/symbols` 逐字透傳（欄位與順序即
ACCOUNT_COLUMNS／COLUMNS）；`/api/symbols` 按類型轉到 /stocks、/futures、/indices，市場與券商原樣傳為
markets／broker（能力閘在 core，本層不自選別家湊數），類型不認識即 unknown_kind；離線 CODES 三個接口
一律以 ?broker= 點名哪一档，/codes/refresh 不带市場參數（快照即全量）；鑑權失敗還原為同一信封而不是
HTTP 500；閘道不可達時點名原因；未設 API_KEY 即拒絕建立應用。
金鑰只在服務端送出（每次請求均帶 X-API-Key，且頁面內容完全不含金鑰）。
券商開關：`/api/brokers/prefs` 與 `/api/brokers/prefs/update` 原樣透傳（`enabled` 不得被大寫化或裁剪），
省略 `enabled` 即全部停用。
圖表規格：`/static/chart.js` 與 `/static/chart_grid.js` 與 `brokery/static/` 內的檔案逐 byte 相同（只有一份，
Web UI 不得另存副本；格子容器與桌面 GUI 讀的也是同一份 JS）。
串流代理：以 WebSocket 客戶端連 `/ws/stream`，核對 subscribe 原樣送達上游、上游事件原樣返回，
上游不可達時返回明確的 gateway_unreachable 而不是無聲等待。
頁面（Chromium）：選單六項；戶口頁進入即取一次，欄位與順序即 ACCOUNT_COLUMNS、資金欄為千分位兩位小數、
取不到的金額顯示破折號、按來源統計戶口數；標的頁的券商選項按能力聲明標註（不提供該品種者不可選）、市場
選項只由返回的 market 填充，「讀取離線 CODES」只讀該家那一檔並標註未向券商取數，「更新離線 CODES」只向
該家重拉並重讀該家的快照狀態（過舊與上次更新失敗以警告色提示），換券商即改讀該家那一檔；兩頁的
「自動更新（秒）」預設 0（空轉數秒不得有任何請求），設 1 秒即定時重取（標的頁預設只重讀離線快照，勾上
「自動向券商重拉」才改為向券商取清單），改回 0 即停止；三個 K 線頁的預設值為 HK.HSImain／生效的第一家
（兩個單格頁為 1m／1000 根，多週期頁為每格 300 根），根數可任填（上限 100000，與桌面 GUI 一致）並原樣送到閘道，合併器的上限亦跟隨它（寫死時
取 3000 根會被裁返 1000 根），且進入頁面只填控件、不自動取數、亦無任何定時請求；取歷史後下方 DF 列出
全部行（不截斷，原數據按時間反序，最新在最上）；串流的 update 與已拉取的序列合併（同 ts 覆蓋、行數不
縮減）；K 線串流頁在 DF 上方以本地 echarts 畫出 canvas，且圖與表格同一份序列，圖以 start: 0 開圖，即
所請求的根數全部喺圖上（不是預設的最近一段）；換週期後 x 軸格式跟住改（規格每次隨輸入交落同一實例）；
串流按「請求簽名」（券商、週期、代碼、根數、復權）界定，同一券商同一週期可並行多條：多週期頁已佔住某週期時，
K 線串流頁照樣可訂閱（另開一條連接、不被拒、唔使等），兩邊各自收到推送，停其中一條唔影響另一條；協定錯誤
（ktype_unsupported、broker_disabled、bad_request）原樣呈現且頁面不自動重送訂閱，由用戶改參數（撳「停止」即
收返呢條連接並解鎖按鈕）；
多週期頁的格子數與順序即該券商在 /capabilities 聲明的 stream_ktypes（界面不排序、不憑空補），
每格上方一排水平週期按鈕（只有該格現有的那個高亮），下方不列 DF，一格一個圖表實例與一份序列，並用緊湊
規格（一格只畫價格圖）；「開始」先逐格取歷史（各按自己嘅週期）全部返回先至訂閱，九個週期只用一條上游
WebSocket；update 按 ktype 只餵顯示該週期的格子；換一格只重取嗰格、只退該週期的串流，已有
另一格顯示同一週期時沿用同一份推送不重複訂閱，舊週期仍有另一格顯示時不退它；一個「停止」只送一次裸
stop 收齊全部格子；換券商即按聲明重建格子（ib 只聲明三個週期，且順序不照 KTYPE_ORDER）；BROKER 管理頁列出全部券商、
未配置者灰掉並讀 detail，套用後各頁券商下拉框即時去掉被停用者。

需要 Chromium（`pip install playwright` 後 `playwright install chromium`）；未安裝時跳過並返回成功。

以腳本方式直接執行：
    python brokery/acceptance/run_webui.py
"""
import asyncio
import json
import socket
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import httpx
import uvicorn
import websockets
from fastapi import FastAPI, WebSocket

from brokery import chart
from brokery.brokers.base import ACCOUNT_COLUMNS, COLUMNS, K_COLUMNS, KTYPE_ORDER
from brokery.core import CODES_META_COLUMNS, PREF_COLUMNS
from brokery_webui.app import create_app

KEY = "webui-test-key"
BROKERS = ["futu", "ib", "tiger", "webull"]
# 模擬 .env 只配置了三家：webull 必須以 configured=False 列出（開關灰掉並讀 detail），
# 而不是從 BROKER 管理頁消失——被停用者要能重新啟用，未配置者要能說明原因。
CONFIGURED = ["futu", "ib", "tiger"]
# 各家聲明的能力：ib 不提供股票 → 標的頁選股票時該選項要標註原因且不可選（由適配器聲明，
# 不在頁面硬寫）。值為大寫常量，與真實閘道一致，否則會掩蓋頁面以類型值直接比對能力聲明的錯誤。
CAPABILITY_OF = {"futu": ["STOCK", "FUTURE", "INDEX"], "ib": ["FUTURE", "INDEX"],
                 "tiger": ["STOCK"], "webull": ["STOCK"]}
# 各家聲明可串流的週期：多週期頁的格子數、格子順序與每格上方的週期按鈕完全照呢份名單同順序，
# 界面唔准自己排序或憑空補週期（futu 九個即 3×3；ib 得三個，而且順序刻意唔照 KTYPE_ORDER，
# 一排序就即刻露餂；tiger/webull 只有 1m，即得返一格）。
STREAM_KTYPES = {"futu": list(KTYPE_ORDER), "ib": ["5m", "1m", "day"],
                 "tiger": ["1m"], "webull": ["1m"]}
K_BASE = 1_760_000_000
# 戶口與標的清單的存根返回：欄位與順序即 ACCOUNT_COLUMNS／COLUMNS，行與 message 逐字透傳。
# ib 兩欄取唔到：必須原樣為 null，由頁面顯示破折號，唔准以任何數字湊出。
ACCOUNT_MESSAGE = "ok: 2 個戶口（來源 futu, ib, tiger）；注意：tiger: ConnectionError: 未連接"
ACCOUNT_ROWS = [
    ["futu", "1234567", "individual", "ACTIVE", "HKD",
     1000.0, 900.0, 100.0, 800.0, 500.0, 60.0, 40.0, 950.0, 12.5, 3.5],
    ["ib", "U11976982", "individual", "ACTIVE", "USD",
     2000.0, 1500.0, 500.0, 1500.0, None, None, None, 2000.0, -25.0, 0.0],
]
# 兩行、兩個市場：足以核對欄位契約與「市場選項只由返回的 market 填充」。行嚴格對應 COLUMNS
# （不設到期月欄，券商原生標識只在 raw 的原生格式中出現）。
SYMBOL_ROWS = [
    ["HK.00700", "騰訊控股", "HK", "700", "STOCK", "HKD", "HKEX", "futu"],
    ["US.NVDA", "英偉達", "US", "NVDA", "STOCK", "USD", "NASDAQ", "futu"],
]
# 存根狀態：只記被停用者，與 broker_prefs.json 同一口徑。
DISABLED: set[str] = set()
RAW: list[str] = []          # 含查詢參數，用以核對請求帶了邊啲參數
SEEN_KEYS: set[str] = set()  # 每次請求帶來的金鑰：核對只在服務端送出
SUBSCRIBES: list[dict] = []  # 上游實際收到的 subscribe 內容（核對原樣透傳）
STOPS: list[dict] = []       # 上游實際收到的 stop 內容：多週期頁換一格週期只准退該週期的串流
WS_SESSIONS: list[int] = []  # 上游被建立的 WebSocket 數：一個訂閱只准開一條
# 依序記錄閘道收到嘅取歷史與訂閱：串流只帶最近 count 根，「先取歷史、再開串流」的順序只能咁核對。
EVENTS: list[str] = []
# 仍開着的上游連接與各自的訂閱：/push 用以向所有正在串流某週期的連接各推一份 bar（真實閘道由券商推送
# 觸發，呢度由測試觸發）。同一券商同一週期的兩條串流必須各自收到推送，故要逐連接核對。
STREAM_LINKS: list[tuple] = []
# 協定錯誤（ktype_unsupported、broker_disabled、bad_request）只對 HK.BAD 發生：原因由閘道點名，參數由用戶改，
# 所以「被拒」由呢度決定，唔准由頁面自己判斷，亦唔准頁面自己重送訂閱。


def kline_rows(start_index: int, count: int, close) -> dict:
    rows = [["HK.HSImain", K_BASE + i * 60, "2026-10-09 09:31:00", 100.0, 101.0, 99.0, close(i),
             10 + i, 1000.0, "futu"] for i in range(start_index, start_index + count)]
    return {"columns": list(K_COLUMNS), "rows": rows}


def kline_payload(start_index: int, count: int, close) -> dict:
    return {"status": True, "data": kline_rows(start_index, count, close), "message": f"ok（{count} 根）"}


def prefs_rows() -> list:
    return [[name, name in CONFIGURED and name not in DISABLED, name in CONFIGURED,
             "" if name in CONFIGURED else f"未在 API_SOURCES 中（.env 只啟用了 {', '.join(CONFIGURED)}）"]
            for name in BROKERS]


def effective() -> list[str]:
    """生效的券商 = 已配置 − 已停用：/capabilities 只列生效者，界面下拉框因此自動跟隨。"""
    return [name for name in CONFIGURED if name not in DISABLED]


# 離線 CODES 按券商各存一檔，檔名、行數與留痕逐家不同（ib 不提供股票，故行數明顯較少），故元資料必須按
# 請求的 broker 返回——若頁面把別家的行數顯示在當前券商那一行，一眼就能看出來。futu 一筆刻意給成超過 24
# 小時且上次更新失敗（距今 90000 秒 → 頁面顯示「1 天前」），因為要驗的正是「過舊與上次更新失敗以警告色
# 提示」；ib 一筆則沒有失敗留痕，故該行不應出現「上次更新失敗」。
def codes_meta_rows(broker: str) -> list:
    return [[f"{broker}_codes", 14819 if broker == "ib" else 38569, 8, "2026-10-10T10:00:00+00:00",
             90000.0, True, broker, "HK/US 全量 CODES",
             "" if broker == "ib" else "futu: OpenD 未連接"]]


def codes_rows(broker: str) -> list:
    """某券商離線快照的讀回內容：行嚴格對應 COLUMNS，内容由該家聲明的能力決定（ib 不提供股票），
    故兩家的行一眼可辨——讀錯檔會立刻看出來。"""
    if broker == "ib":
        return [["HK.HSI", "恒生指數", "HK", "HSI", "INDEX", "HKD", "HKEX", broker],
                ["US.ES", "標普 500 期貨", "US", "ES", "FUTURE", "USD", "CME", broker]]
    return [["HK.00700", "騰訊控股", "HK", "700", "STOCK", "HKD", "HKEX", broker],
            ["US.NVDA", "英偉達", "US", "NVDA", "STOCK", "USD", "NASDAQ", broker],
            ["US.VIX", "VIX 波動率指數", "US", "VIX", "INDEX", "USD", "CBOE", broker]]


class Recorder:
    """純 ASGI 中間件：記錄 HTTP 請求的原始查詢串與金鑰。

    只處理 http scope：串流握手的金鑰在查詢串（瀏覽器不能自訂標頭），若連 websocket scope 一起攔，
    握手會被拒（403），代理一段便永遠測不到。查詢串取 scope 的原始位元組，即 %2C 未被解碼，
    正好核對 Web UI 沒有改寫 enabled 的大小寫與分隔符。
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        query = scope["query_string"].decode()
        RAW.append(f"{scope['path']}?{query}" if query else scope["path"])
        headers = {k.decode().lower(): v.decode() for k, v in scope["headers"]}
        SEEN_KEYS.add(headers.get("x-api-key", ""))
        if headers.get("x-api-key") != KEY:
            await json_response({"detail": "invalid_api_key"}, 401)(scope, receive, send)
            return
        await self.app(scope, receive, send)


def build_stub() -> FastAPI:
    """存根閘道：只提供信封與一條協定相同的串流，不連任何券商。"""
    app = FastAPI()

    app.add_middleware(Recorder)

    def envelope(body):
        return json_response(body)

    @app.get("/capabilities")
    def capabilities():
        names = effective()
        return envelope({"status": True,
                         # ktypes 與真實閘道一致：統一由 KTYPE_ORDER 決定（不是存根自己湊兩項），
                         # 兩個 K 線頁的週期下拉框正是照呢份名單生成。stream_ktypes 則逐家不同，
                         # 多週期頁的格子與每格上方的週期按鈕只照呢份聲明生成。
                         "data": {"sources": names, "autype": "qfq", "ktypes": list(KTYPE_ORDER),
                                  "acc_filters": ["all"],
                                  "adapters": {n: {"capabilities": CAPABILITY_OF[n], "autypes": ["none"],
                                                   "stream_ktypes": STREAM_KTYPES[n]}
                                              for n in names}},
                         "message": "ok"})

    @app.get("/accounts")
    def accounts():
        return envelope({"status": True,
                         "data": {"columns": list(ACCOUNT_COLUMNS), "rows": ACCOUNT_ROWS},
                         "message": ACCOUNT_MESSAGE})

    # 三個清單接口：內容相同，但要能核對 /api/symbols 按類型轉到了哪一個。
    @app.get("/stocks")
    @app.get("/futures")
    @app.get("/indices")
    def symbols(broker: str = "futu", markets: str | None = None):
        return envelope({"status": True, "data": {"columns": list(COLUMNS), "rows": SYMBOL_ROWS},
                         "message": "ok"})

    # 離線快照的三個接口：讀回與元資料離線執行、重拉需券商連線，三者均以 ?broker= 點名哪一档。
    @app.get("/codes")
    def codes(broker: str = "futu"):
        return envelope({"status": True, "data": {"columns": list(COLUMNS), "rows": codes_rows(broker)},
                         "message": "ok"})

    @app.get("/codes/meta")
    def codes_meta(broker: str = "futu"):
        return envelope({"status": True,
                         "data": {"columns": list(CODES_META_COLUMNS), "rows": codes_meta_rows(broker)},
                         "message": "ok"})

    @app.get("/codes/refresh")
    def codes_refresh(broker: str = "futu"):
        rows = codes_meta_rows(broker)
        return envelope({"status": True, "data": {"columns": list(CODES_META_COLUMNS), "rows": rows},
                         "message": f"ok: 已更新 {rows[0][1]} 條 CODES（FUTURE 14079（+0），"
                                   f"INDEX 740（+0），STOCK 23750（+0））"})

    @app.get("/kline")
    def kline(code: str, ktype: str | None = None, count: int | None = None, broker: str = "futu"):
        EVENTS.append("kline")
        if code == "HK.DISABLED":  # 業務失敗：Web UI 必須原樣透傳，不得改寫成自己的訊息
            return envelope({"status": False, "data": {"columns": [], "rows": []},
                             "message": f"broker_disabled: {broker}（已在 BROKER 管理中停用）"})
        # 較長的序列：用以核對界面把返回的行全部列出，而不是只列最近若干行（用戶要的是原數據）
        if code == "HK.MANY":
            return kline_payload(0, 120, lambda i: 100.0 + i)
        return kline_payload(0, 4, lambda i: 100.0 + i)

    @app.get("/brokers/prefs")
    def brokers_prefs():
        return envelope({"status": True,
                         "data": {"columns": list(PREF_COLUMNS), "rows": prefs_rows()},
                         "message": f"ok: {len(BROKERS)} 個券商（生效 {', '.join(effective()) or '無'}）"})

    @app.get("/brokers/prefs/update")
    def brokers_prefs_update(enabled: str | None = None):
        names = [n.strip().lower() for n in (enabled or "").split(",") if n.strip()]
        unknown = sorted(n for n in names if n not in BROKERS)
        if unknown:
            return envelope({"status": False, "data": {"columns": list(PREF_COLUMNS), "rows": []},
                             "message": f"unknown_source: {', '.join(unknown)}"})
        DISABLED.clear()
        DISABLED.update(n for n in CONFIGURED if n not in names)
        return brokers_prefs()

    @app.websocket("/stream")
    async def stream(ws: WebSocket) -> None:
        await ws.accept()
        WS_SESSIONS.append(1)
        # 與真實閘道一致：一條連接可同時有多個訂閱（一份串流由請求簽名界定），每個事件一律帶 ktype；
        # stop 可只停一個週期，全部停完才收線。
        active: list[dict] = []
        STREAM_LINKS.append((ws, active))
        try:
            while True:
                try:
                    action = await ws.receive_json()
                except Exception:  # 客戶端直接斷開：結束即可，不影響任何斷言
                    return
                kind = str(action.get("action", "")).lower()
                if kind == "subscribe":
                    SUBSCRIBES.append(action)
                    EVENTS.append("subscribe")
                    broker = str(action.get("broker", ""))
                    ktype = str(action.get("ktype", ""))
                    codes = [str(c) for c in action.get("codes", [])]
                    # 協定錯誤：帧內帶 broker/ktype 點名原因，並且不收線（連接仍可用），參數由用戶改。
                    if "HK.BAD" in codes:
                        await ws.send_json({"event": "error", "broker": broker, "ktype": ktype,
                                            "message": f"ktype_unsupported: {broker} 未聲明可串流的週期 {ktype}"})
                        continue
                    # 同一券商同一週期照樣可並行多條（另一條連接以不同根數或代碼訂閱）：呢度接手同一份推送。
                    active.append({"broker": broker, "ktype": ktype})
                    await ws.send_json({"event": "subscribed", "broker": broker,
                                        "codes": list(action.get("codes", [])),
                                        "ktype": ktype, "seconds": 5})
                    # 第一條帶完整的四根，第二條只帶最近三根（其中一根為新的）：客戶端必須合併而不是取代。
                    await ws.send_json({"event": "update", "broker": broker, "ktype": ktype,
                                        "code": "HK.HSImain", "data": kline_rows(0, 4, lambda i: 100.0 + i)})
                    await ws.send_json({"event": "update", "broker": broker, "ktype": ktype,
                                        "code": "HK.HSImain", "data": kline_rows(2, 3, lambda i: 9999.0)})
                elif kind == "stop":
                    STOPS.append(action)
                    broker, ktype = str(action.get("broker", "")), str(action.get("ktype", ""))
                    kept = [a for a in active
                            if (broker and a["broker"] != broker) or (ktype and a["ktype"] != ktype)]
                    for a in [a for a in active if a not in kept]:
                        await ws.send_json({"event": "closed", "broker": a["broker"], "ktype": a["ktype"],
                                            "message": "已停止串流"})
                    active[:] = kept      # 就地改：/push 讀嘅係同一個 list
                    if not active:
                        return
                else:
                    await ws.send_json({"event": "error", "message": f"bad_action: {kind or '空'}"})
        finally:
            STREAM_LINKS[:] = [link for link in STREAM_LINKS if link[0] is not ws]

    @app.get("/push")
    async def push(ktype: str = "1m", start: int = 10):
        """向所有正在串流該週期的連接各推兩根新的 bar（start 決定時間戳，故每次調用推嘅係新根）：
        同一週期的兩條串流必須各自收到，收返咗嘅連接不再被填。"""
        hit = 0
        for ws, active in list(STREAM_LINKS):
            if any(a["ktype"] == ktype for a in active):
                hit += 1
                await ws.send_json({"event": "update", "broker": "futu", "ktype": ktype,
                                    "code": "HK.HSImain",
                                    "data": kline_rows(start, 2, lambda i: 5555.0)})
        return envelope({"status": True, "data": {"columns": [], "rows": []}, "message": f"pushed:{hit}"})

    return app


def json_response(body: dict, status: int = 200):
    from fastapi.responses import JSONResponse
    return JSONResponse(body, status_code=status)


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def serve(app: FastAPI, port: int) -> tuple[uvicorn.Server, threading.Thread]:
    """在背景執行緒起服務並等待就緒：兩個應用都要能被真實的 HTTP/WebSocket 客戶端連到。"""
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(100):
        if server.started:
            return server, thread
        time.sleep(0.1)
    raise RuntimeError(f"服務未能啟動（端口 {port}）")


def stop(server: uvicorn.Server, thread: threading.Thread) -> None:
    server.should_exit = True
    thread.join(timeout=5)


def proxy_roundtrip(ws_url: str) -> list[dict]:
    """以原始 WebSocket 客戶端經 Web UI 連存根：收到的事件序列原樣交回，由呼叫方逐項核對。"""

    async def run() -> list[dict]:
        got: list[dict] = []
        async with websockets.connect(ws_url, max_size=8 * 2 ** 20) as ws:
            await ws.send(json.dumps({"action": "subscribe", "codes": ["HK.HSImain"],
                                      "ktype": "1m", "count": 1000, "broker": "futu"}))
            for _ in range(3):  # subscribed + 兩條 update
                got.append(json.loads(await asyncio.wait_for(ws.recv(), timeout=10)))
            await ws.send(json.dumps({"action": "stop"}))
            got.append(json.loads(await asyncio.wait_for(ws.recv(), timeout=10)))
        return got

    return asyncio.run(asyncio.wait_for(run(), timeout=20))


def main() -> dict:
    checks: list[tuple[str, bool, str]] = []

    def check(label: str, passed: bool, detail: str = "") -> None:
        checks.append((label, bool(passed), str(detail)))

    stub_port, web_port = free_port(), free_port()
    stub_server = web_server = None
    stub_thread = web_thread = None
    try:
        stub_server, stub_thread = serve(build_stub(), stub_port)
        base = f"http://127.0.0.1:{stub_port}"
        web_server, web_thread = serve(create_app(base_url=base, api_key=KEY), web_port)
        web = f"http://127.0.0.1:{web_port}"

        # ---------- 轉發口徑（不经瀏覽器）----------
        client = httpx.Client(timeout=20)
        full = client.get(f"{web}/api/kline", params={"code": "HK.HSImain", "ktype": "1m",
                                                      "count": 1000, "broker": "ib"}).json()
        # 參數順序由 forward() 的字典順序決定（code、broker 先，其後才是可選項），故逐字比對。
        kline_raw = [p for p in RAW if p.startswith("/kline")]
        RAW.clear()
        client.get(f"{web}/api/kline", params={"code": "HK.HSImain"}).json()
        omit_raw = [p for p in RAW if p.startswith("/kline")]
        RAW.clear()
        failed = client.get(f"{web}/api/kline", params={"code": "HK.DISABLED"}).json()

        # 戶口、標的清單與離線 CODES：逐個接口清一次記錄，即可核對轉到了哪一條路徑、帶了哪些參數。
        accounts = client.get(f"{web}/api/accounts").json()
        accounts_raw = [p for p in RAW if p.startswith("/accounts")]
        RAW.clear()
        symbols = client.get(f"{web}/api/symbols", params={"kind": "stock", "market": "HK",
                                                           "broker": "futu"}).json()
        stock_raw = [p for p in RAW if p.startswith("/stocks")]
        RAW.clear()
        kind_raw: dict[str, list[str]] = {}
        for kind, path in (("future", "/futures"), ("index", "/indices")):
            client.get(f"{web}/api/symbols", params={"kind": kind}).json()
            kind_raw[kind] = [p for p in RAW if p.startswith(path)]
            RAW.clear()
        bogus = client.get(f"{web}/api/symbols", params={"kind": "option"}).json()
        codes_meta = client.get(f"{web}/api/codes/meta").json()
        meta_raw = [p for p in RAW if p.startswith("/codes/meta")]
        RAW.clear()
        other_meta = client.get(f"{web}/api/codes/meta", params={"broker": "ib"}).json()
        other_meta_raw = [p for p in RAW if p.startswith("/codes/meta")]
        RAW.clear()
        offline = client.get(f"{web}/api/codes", params={"broker": "ib"}).json()
        offline_raw = [p for p in RAW if p.startswith("/codes?")]
        RAW.clear()
        codes_refresh = client.get(f"{web}/api/codes/refresh", params={"broker": "ib"}).json()
        refresh_raw = [p for p in RAW if p.startswith("/codes/refresh")]
        RAW.clear()

        prefs = client.get(f"{web}/api/brokers/prefs").json()
        RAW.clear()
        applied = client.get(f"{web}/api/brokers/prefs/update", params={"enabled": "futu,ib"}).json()
        apply_raw = [p for p in RAW if p.startswith("/brokers/prefs/update")]
        RAW.clear()
        caps = client.get(f"{web}/api/capabilities").json()
        omitted = client.get(f"{web}/api/brokers/prefs/update").json()
        omitted_raw = [p for p in RAW if p.startswith("/brokers/prefs/update")]
        RAW.clear()
        bad_name = client.get(f"{web}/api/brokers/prefs/update", params={"enabled": "FUTU,nope"}).json()
        bad_raw = [p for p in RAW if p.startswith("/brokers/prefs/update")]
        client.get(f"{web}/api/brokers/prefs/update", params={"enabled": ",".join(CONFIGURED)})
        RAW.clear()
        check("轉發時帶上服務端金鑰（X-API-Key）", SEEN_KEYS == {KEY}, ",".join(sorted(SEEN_KEYS)))
        check("/api/kline 帶齊標的、週期、根數與券商",
              kline_raw == ["/kline?code=HK.HSImain&broker=ib&ktype=1m&count=1000"]
              and full["status"] and len(full["data"]["rows"]) == 4, ",".join(kline_raw))
        check("週期與根數省略時不自訂第二套預設（交閘道決定）",
              omit_raw == ["/kline?code=HK.HSImain&broker=futu"], ",".join(omit_raw))
        check("業務失敗原樣透傳（broker_disabled 不改寫）",
              failed["status"] is False and failed["message"].startswith("broker_disabled:"),
              failed["message"])
        check("轉發原樣透傳信封（欄位、行與 message 逐字一致）",
              accounts["status"] and accounts["data"]["columns"] == list(ACCOUNT_COLUMNS)
              and accounts["data"]["rows"] == ACCOUNT_ROWS
              and accounts["message"] == ACCOUNT_MESSAGE and accounts_raw == ["/accounts"],
              f"欄={accounts['data']['columns'][:2]} 行={len(accounts['data']['rows'])}")
        check("標的清單按類型轉到 /stocks，市場與券商原樣傳為 markets／broker",
              stock_raw == ["/stocks?broker=futu&markets=HK"], ",".join(stock_raw))
        check("標的清單原樣透傳信封（欄位即 COLUMNS）",
              symbols["status"] and symbols["data"]["columns"] == list(COLUMNS)
              and symbols["data"]["rows"] == SYMBOL_ROWS, f"欄={symbols['data']['columns'][:3]}")
        check("類型 future 轉到 /futures、index 轉到 /indices（省略券商即默認那家）",
              kind_raw["future"] == ["/futures?broker=futu"]
              and kind_raw["index"] == ["/indices?broker=futu"], str(kind_raw))
        check("類型不認識即 unknown_kind（不猜用戶想要什麼）",
              bogus["status"] is False and bogus["message"].startswith("unknown_kind"), bogus["message"])
        check("離線 CODES 元資料轉發 /codes/meta（欄位即 CODES_META_COLUMNS，省略 broker 即預設那家）",
              meta_raw == ["/codes/meta?broker=futu"] and codes_meta["status"]
              and codes_meta["data"]["columns"] == list(CODES_META_COLUMNS)
              and codes_meta["data"]["rows"] == codes_meta_rows("futu"), ",".join(meta_raw))
        check("?broker= 即改讀該家那一檔（檔名與行數都屬該家）",
              other_meta_raw == ["/codes/meta?broker=ib"]
              and other_meta["data"]["rows"] == codes_meta_rows("ib"), ",".join(other_meta_raw))
        check("讀取離線 CODES 轉發 /codes?broker=（欄位即 COLUMNS，內容屬該家）",
              offline_raw == ["/codes?broker=ib"] and offline["status"]
              and offline["data"]["columns"] == list(COLUMNS)
              and offline["data"]["rows"] == codes_rows("ib"), ",".join(offline_raw))
        check("更新離線 CODES 轉發 /codes/refresh?broker= 且不带市場參數（快照即全量，"
              "只拉部分市場會被縮細防護拒絕）",
              refresh_raw == ["/codes/refresh?broker=ib"] and codes_refresh["status"]
              and "14819" in codes_refresh["message"], ",".join(refresh_raw))
        check("/api/brokers/prefs 返回 PREF_COLUMNS 且列出全部券商（含未配置者）",
              prefs["status"] and prefs["data"]["columns"] == list(PREF_COLUMNS)
              and [r[0] for r in prefs["data"]["rows"]] == BROKERS
              and [r[2] for r in prefs["data"]["rows"]] == [True, True, True, False],
              str([r[:3] for r in prefs["data"]["rows"]]))
        check("/api/brokers/prefs/update 原樣透傳名單（不被大寫化或裁剪）",
              apply_raw == ["/brokers/prefs/update?enabled=futu%2Cib"] and applied["status"]
              and [r[1] for r in applied["data"]["rows"]] == [True, True, False, False],
              f"{','.join(apply_raw)} {str([r[:2] for r in applied['data']['rows']])}")
        check("省略 enabled 即全部停用（與界面取消全部開關一致）",
              omitted_raw == ["/brokers/prefs/update"]
              and [r[1] for r in omitted["data"]["rows"]] == [False, False, False, False],
              f"{','.join(omitted_raw)} {str([r[:2] for r in omitted['data']['rows']])}")
        check("名單原樣送達（大小寫不改）；不存在的券商明確報錯",
              bad_raw == ["/brokers/prefs/update?enabled=FUTU%2Cnope"]
              and bad_name["status"] is False and bad_name["message"] == "unknown_source: nope",
              f"{','.join(bad_raw)} | {bad_name['message']}")
        check("被停用者不再出現在 /api/capabilities（下拉框因此自動跟隨）",
              caps["data"]["sources"] == ["futu", "ib"], str(caps["data"]["sources"]))

        js = client.get(f"{web}/static/chart.js").content
        check("/static/chart.js 與 brokery/static 內的檔案逐 byte 相同（只有一份）",
              js == chart.static_file("chart.js").read_bytes(), f"{len(js)} bytes")
        # 格子（多週期頁）與桌面 GUI 讀的是同一份 JS：呢度再另寫一份就會兩邊走樣。
        grid_js = client.get(f"{web}/static/chart_grid.js").content
        check("/static/chart_grid.js 與 brokery/static 內的檔案逐 byte 相同（只有一份）",
              grid_js == chart.static_file("chart_grid.js").read_bytes(), f"{len(grid_js)} bytes")
        echarts = client.get(f"{web}/static/echarts.min.js")
        check("本地 echarts 由同一條 /static 路由提供（無 CDN）",
              echarts.status_code == 200 and len(echarts.content) > 100_000,
              f"{len(echarts.content)} bytes")
        missing = client.get(f"{web}/static/nope.js")
        check("不存在的圖表規格明確返回 static_missing",
              missing.status_code == 404 and "static_missing" in missing.text, missing.text[:80])

        events = proxy_roundtrip(f"ws://127.0.0.1:{web_port}/ws/stream")
        check("串流代理把 subscribe 原樣送到上游",
              SUBSCRIBES[-1:] == [{"action": "subscribe", "codes": ["HK.HSImain"],
                                   "ktype": "1m", "count": 1000, "broker": "futu"}],
              str(SUBSCRIBES[-1:]))
        check("上游事件原樣返回（subscribed/update 的欄位與內容不變）",
              [e["event"] for e in events] == ["subscribed", "update", "update", "closed"]
              and events[1]["data"]["columns"] == list(K_COLUMNS)
              and [len(e["data"]["rows"]) for e in events[1:3]] == [4, 3],
              ",".join(e["event"] for e in events))

        # ---------- 閘道不可達與鑑權失敗（進程內應用，不需另起服務）----------
        from fastapi.testclient import TestClient
        with TestClient(create_app(base_url="http://127.0.0.1:9", api_key=KEY)) as dead:
            unreachable = dead.get("/api/kline", params={"code": "HK.HSImain"}).json()
            with TestClient(create_app(base_url=base, api_key="wrong-key")) as wrong:
                denied = wrong.get("/api/accounts").json()
        check("閘道不可達時點名原因而不是 HTTP 500",
              unreachable["status"] is False and unreachable["message"].startswith("gateway_unreachable:"),
              unreachable["message"][:90])
        check("鑑權失敗還原為同一信封（gateway_http_401）",
              denied["status"] is False and "gateway_http_401" in denied["message"], denied["message"][:90])
        with TestClient(create_app(base_url="http://127.0.0.1:9", api_key=KEY)) as dead_ws:
            with dead_ws.websocket_connect("/ws/stream") as ws:
                ws_event = ws.receive_json()
        check("上游不可達時串流代理返回明確 error（不讓頁面空白等待）",
              ws_event.get("event") == "error" and "gateway_unreachable" in ws_event["message"],
              str(ws_event)[:120])
        try:
            create_app(base_url=base, api_key="")
            refused = False
        except RuntimeError as exc:
            refused = "API_KEY" in str(exc)
        check("未設 API_KEY 即拒絕建立應用（金鑰不可缺，也不可寫死在頁面）", refused, "已拒絕")
        client.close()
    except Exception as exc:  # 服務起不來即屬環境問題，必須點名而不是靜靜跳過
        for server, thread in ((stub_server, stub_thread), (web_server, web_thread)):
            if server is not None:
                stop(server, thread)
        return {"status": False, "data": None, "message": f"存根或 Web UI 啟動失敗：{type(exc).__name__}: {exc}"}

    # ---------- 頁面（Chromium）----------
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("SKIP 未安裝 playwright（pip install playwright && playwright install chromium）")
        stop(stub_server, stub_thread)
        stop(web_server, web_thread)
        return {"status": True, "data": None, "message": "跳過：未安裝 playwright"}

    errors: list[str] = []
    page_raw: list[str] = []  # 瀏覽器實際送出的請求（/api/* 只到 Web UI，存根看不到，故在頁面側記錄）
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except Exception as exc:  # 未下載瀏覽器
                print(f"SKIP 未安裝 Chromium：{exc}")
                return {"status": True, "data": None, "message": "跳過：未安裝 Chromium"}
            page = browser.new_page()
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("request", lambda r: page_raw.append(r.url.replace(web, "")))
            RAW.clear()
            page.goto(f"{web}/", timeout=30000)
            page.wait_for_timeout(1500)
            loaded = list(RAW)
            menu = page.eval_on_selector_all("#menu button", "els => els.map(e => e.dataset.page)")
            page_html = page.content()
            head = page.eval_on_selector_all("#a-table th", "els => els.map(e => e.textContent)")
            rows = page.eval_on_selector_all("#a-table tbody tr",
                                             "els => els.map(e => [...e.cells].map(c => c.textContent))")
            account_chips = page.eval_on_selector_all("#a-sources .chip",
                                                       "els => els.map(e => e.textContent)")
            status = page.eval_on_selector("#status", "e => e.textContent")
            account_msg = page.eval_on_selector("#a-msg", "e => e.className + '|' + e.textContent")
            RAW.clear()
            page.click("#a-refresh")
            page.wait_for_timeout(800)
            refreshed = list(RAW)

            # 自動更新以秒為單位，預設 0（不更新）：0 時不得有任何空轉的請求；設 1 秒即定時重取；改回 0
            # 即停止。改秒數後由現在重新計時，故不會因為「剛切換頁面」而補打一次。
            interval_default = page.eval_on_selector("#a-interval", "e => [e.value, e.min]")
            RAW.clear()
            page.wait_for_timeout(2500)
            idle_accounts = list(RAW)
            page.fill("#a-interval", "1")
            page.wait_for_timeout(2500)
            auto_accounts = list(RAW)
            page.fill("#a-interval", "0")
            RAW.clear()  # 只核對改回 0 之後有否再打請求
            page.wait_for_timeout(2500)
            stopped_accounts = list(RAW)

            RAW.clear()
            page.click("nav button[data-page='symbols']")
            page.wait_for_timeout(1500)
            sym_hits = list(RAW)
            broker_opts = page.eval_on_selector_all(
                "#s-broker option",
                "els => els.map(e => e.value + '|' + e.textContent + '|' + (e.disabled ? '不可選' : '可選'))")
            broker_value = page.eval_on_selector("#s-broker", "e => e.value")
            market_opts = page.eval_on_selector_all("#s-market option", "els => els.map(e => e.value)")
            sym_head = page.eval_on_selector_all("#s-table th", "els => els.map(e => e.textContent)")
            sym_chips = page.eval_on_selector_all("#s-sources .chip", "els => els.map(e => e.textContent)")
            snapshot_line = page.eval_on_selector("#s-snapshot", "e => e.className + '|' + e.textContent")
            symbols_interval = page.eval_on_selector("#s-interval", "e => [e.value, e.min]")
            live_default = page.eval_on_selector("#s-live", "e => e.checked")
            # 「讀取離線 CODES」：只讀所選券商那一檔，不打券商，也不需要連線；讀回的內容即下方表格。
            RAW.clear()
            page.click("#s-codes-load")
            page.wait_for_timeout(900)
            offline_query = list(RAW)
            offline_rows = page.eval_on_selector_all("#s-table tbody tr",
                                                      "els => els.map(e => e.cells[0].textContent)")
            offline_msg = page.eval_on_selector("#s-msg", "e => e.textContent")
            RAW.clear()
            page.click("#s-codes-refresh")
            page.wait_for_timeout(1200)
            codes_query = list(RAW)
            refresh_msg = page.eval_on_selector("#s-msg", "e => e.className + '|' + e.textContent")
            RAW.clear()
            page.select_option("#s-market", "HK")
            page.wait_for_timeout(800)
            market_query = list(RAW)
            RAW.clear()
            page.select_option("#s-kind", "index")
            page.wait_for_timeout(800)
            kind_query = list(RAW)
            market_after_kind = page.eval_on_selector("#s-market", "e => e.value")
            markets_after_kind = page.eval_on_selector_all("#s-market option", "els => els.map(e => e.value)")

            # 換到 ib（指數為其能力所及，故選項可選）：清單與快照狀態都要改讀 ib 那一檔，否則顯示的是
            # 另一家的代碼表。兩個請求並行送達，故只比集合不比先后。
            RAW.clear()
            page.select_option("#s-broker", "ib")
            page.wait_for_timeout(900)
            switch_query = sorted(RAW)
            ib_line = page.eval_on_selector("#s-snapshot", "e => e.textContent")
            RAW.clear()
            page.click("#s-codes-refresh")
            page.wait_for_timeout(1200)
            ib_refresh = list(RAW)

            # 標的頁的定時更新：預設只重讀離線快照（不打券商）；勾上「自動向券商重拉」才改為向券商取清單。
            RAW.clear()
            page.fill("#s-interval", "1")
            page.wait_for_timeout(2500)
            auto_offline = list(RAW)
            page.check("#s-live")
            page.wait_for_timeout(1200)  # 先讓上一輪的離線讀取完成，才清記錄，免得把尾巴算進下一段
            RAW.clear()
            page.wait_for_timeout(2500)
            auto_live = list(RAW)
            page.uncheck("#s-live")
            page.fill("#s-interval", "0")
            RAW.clear()  # 只核對改回 0 之後有否再打請求
            page.wait_for_timeout(2500)
            stopped_symbols = list(RAW)

            page.click("nav button[data-page='kline-pull']")
            page.wait_for_timeout(1200)
            defaults = {prefix: [page.eval_on_selector(f"#{prefix}-{field}", "e => e.value")
                                 for field in ("code", "ktype", "count", "broker")]
                        for prefix in ("kp", "ks")}
            count_max = {prefix: page.eval_on_selector(f"#{prefix}-count", "e => e.max")
                         for prefix in ("kp", "ks")}
            ktype_options = page.eval_on_selector_all("#kp-ktype option", "els => els.map(o => o.value)")
            broker_options = page.eval_on_selector_all("#kp-broker option", "els => els.map(o => o.value)")
            RAW.clear()
            page.wait_for_timeout(2500)  # 進入頁面只填控件：不得自動取數，亦不得有任何定時請求
            idle_requests = list(RAW)

            page_raw.clear()
            RAW.clear()
            page.click("#kp-load")
            page.wait_for_timeout(1500)
            pull_page_raw = [p for p in page_raw if p.startswith("/api/kline")]
            pull_raw = [p for p in RAW if p.startswith("/kline")]
            pull_head = page.eval_on_selector_all("#kp-table th", "els => els.map(e => e.textContent)")
            pull_ts = page.eval_on_selector_all("#kp-table tbody tr td:nth-child(2)",
                                                "els => els.map(e => Number(e.textContent))")
            chips = page.eval_on_selector_all("#kp-sources .chip", "els => els.map(e => e.textContent)")
            # 較長的序列：表格必須列出全部行（原數據），不得只列最近若干行
            page.fill("#kp-code", "HK.MANY")
            page.click("#kp-load")
            page.wait_for_timeout(2000)
            many_rows = len(page.query_selector_all("#kp-table tbody tr"))
            many_ts = page.eval_on_selector_all("#kp-table tbody tr td:nth-child(2)",
                                               "els => [Number(els[0].textContent), Number(els.at(-1).textContent)]")
            page.fill("#kp-code", "HK.HSImain")
            # 根數可任選：3000 要原樣送到閘道，合併器的上限亦要跟住 3000（寫死 1000 即被裁返 1000 根）。
            page.fill("#kp-count", "3000")
            page_raw.clear()
            RAW.clear()
            page.click("#kp-load")
            page.wait_for_timeout(1500)
            deep_page_raw = [p for p in page_raw if p.startswith("/api/kline")]
            deep_raw = [p for p in RAW if p.startswith("/kline")]
            deep_limit = page.evaluate("() => panes['kline-pull'].store.limit")
            page.fill("#kp-count", "1000")

            page.click("nav button[data-page='kline-stream']")
            page.wait_for_timeout(300)
            SUBSCRIBES.clear()
            # 提示只有一行、後者蓋走前者，故先裝 MutationObserver：已訂閱與已更新都必須出現過
            page.evaluate("""() => {
                window.__msgs = [];
                new MutationObserver(() => window.__msgs.push(document.querySelector('#ks-msg').textContent))
                    .observe(document.querySelector('#ks-msg'),
                             {childList: true, characterData: true, subtree: true});
            }""")
            EVENTS.clear()
            WS_SESSIONS.clear()
            page.click("#ks-start")
            page.wait_for_timeout(2000)
            stream_subscribe = list(SUBSCRIBES)
            stream_events = list(EVENTS)
            stream_sessions = len(WS_SESSIONS)
            stream_msgs = page.evaluate("() => window.__msgs")
            stream_msg = " | ".join(stream_msgs)
            merged_ts = page.eval_on_selector_all("#ks-table tbody tr td:nth-child(2)",
                                                  "els => els.map(e => Number(e.textContent))")
            merged_top = page.eval_on_selector("#ks-table tbody tr td:nth-child(7)", "e => e.textContent")
            store_size = page.evaluate("() => panes['kline-stream'].store.size")
            # DF 上方的圖：以本地 echarts 畫出 canvas，且位置在表格之前（同一頁、同一份序列）。
            stream_canvases = len(page.query_selector_all("#ks-chart canvas"))
            chart_above_table = page.evaluate(
                "() => { const c = document.querySelector('#ks-chart'), t = document.querySelector('#ks-table');"
                " return !!c && !!t && !!(c.compareDocumentPosition(t) & Node.DOCUMENT_POSITION_FOLLOWING); }")
            # 所請求的根數全部喺圖上：開圖窗口為 start: 0（預設只顯最近一段），故圖上的 bar 數即合併後的根數。
            chart_view = page.evaluate(
                "() => { const o = echarts.getInstanceByDom(document.querySelector('#ks-chart')).getOption();"
                " return {start: o.dataZoom[0].start, bars: o.series[0].data.length,"
                " store: panes['kline-stream'].store.size}; }")
            start_disabled = page.eval_on_selector("#ks-start", "e => e.disabled")
            page.click("#ks-stop")
            page.wait_for_timeout(800)
            stop_enabled = page.eval_on_selector("#ks-start", "e => e.disabled")
            # 換週期即換咗該次輸入：圖照新週期重畫（x 軸格式跟住改），唔係只喺開圖時給一次規格。
            page.select_option("#ks-ktype", "day")
            page.click("#ks-start")
            page.wait_for_timeout(1500)
            relabel = page.evaluate(
                "() => { const o = echarts.getInstanceByDom(document.querySelector('#ks-chart')).getOption();"
                " return {label: o.xAxis[0].axisLabel.formatter(1760000000),"
                " ktype: document.querySelector('#ks-ktype').value}; }")
            page.click("#ks-stop")
            page.wait_for_timeout(800)
            page.select_option("#ks-ktype", "1m")
            # 取歷史失敗：不得只靠串流撐出一張圖（那會得返最近幾十根），亦不得留返舊標的的 bar。
            page.fill("#ks-code", "HK.DISABLED")
            SUBSCRIBES.clear()
            EVENTS.clear()
            page.click("#ks-start")
            page.wait_for_timeout(1500)
            failed_events = list(EVENTS)
            failed_subscribes = list(SUBSCRIBES)
            failed_store = page.evaluate("() => panes['kline-stream'].store.size")
            failed_msg = page.eval_on_selector("#ks-msg", "e => e.textContent")
            failed_enabled = page.eval_on_selector("#ks-start", "e => e.disabled")
            # 再無 stream_busy：會話參數由用戶改，界面自己重送只會出現用戶看不見嘅訂閱，故協定錯誤
            # （ktype_unsupported、broker_disabled、bad_request）一律原樣呈現、不重送（與桌面 GUI 同一口徑）。
            page.fill("#ks-code", "HK.BAD")
            SUBSCRIBES.clear()
            STOPS.clear()
            EVENTS.clear()
            page.evaluate("() => { window.__msgs = []; }")
            page.click("#ks-start")
            page.wait_for_timeout(1500)   # 錯誤帧已到：呢一刻只准見到原樣嘅原因，未重送訂閱
            bad_msgs = page.evaluate("() => window.__msgs")
            bad_subscribes = list(SUBSCRIBES)
            bad_events = list(EVENTS)
            bad_msg = page.eval_on_selector("#ks-msg", "e => e.textContent")
            bad_locked = page.eval_on_selector("#ks-start", "e => e.disabled")
            page.click("#ks-stop")
            page.wait_for_timeout(800)
            bad_reopen = page.eval_on_selector("#ks-start", "e => e.disabled")
            bad_stops = list(STOPS)
            page.fill("#ks-code", "HK.HSImain")

            # ---------- 多週期頁：格子即該券商聲明可串流的週期，下方無 DF ----------
            page_raw.clear()
            RAW.clear()
            page.click("nav button[data-page='kline-grid']")
            page.wait_for_timeout(1500)
            grid_idle = list(RAW)  # 進入本頁只按能力聲明起格子：不得自動取數，亦不得有任何定時請求
            grid_controls = {field: page.eval_on_selector(f"#kg-{field}", "e => e.value")
                             for field in ("code", "count", "broker")}
            grid_count_max = page.eval_on_selector("#kg-count", "e => e.max")
            grid_layout = page.evaluate("() => panes['kline-grid'].layout")
            grid_cells = len(page.query_selector_all("#kg-grid .brokery-cell"))
            # 未 setOption 前 ECharts 不生成 canvas，故數實例而不是數 canvas：九格即九個實例，各自獨立。
            grid_instances = page.evaluate(
                "() => [...document.querySelectorAll('#kg-grid .brokery-pane')]"
                ".filter(e => !!echarts.getInstanceByDom(e)).length")
            # 每格上方一排水平按鈕：九個週期全列出，只有該格現有的那個高亮（* 為高亮標記）。
            grid_tabs = page.eval_on_selector_all(
                "#kg-grid .brokery-cell",
                "els => els.map(e => [...e.querySelectorAll('.brokery-tabs button')]"
                ".map(b => b.dataset.ktype + (b.className === 'on' ? '*' : '')))")
            grid_tab_rows = page.evaluate(  # 同一格內的按鈕必須同一水平線（水平舖，不是直排）
                "() => [...document.querySelectorAll('#kg-grid .brokery-cell')].map(e =>"
                " new Set([...e.querySelectorAll('.brokery-tabs button')].map(b => b.offsetTop)).size)")
            grid_no_table = page.evaluate("() => !document.querySelector('#page-kline-grid table')")
            grid_summary = page.eval_on_selector_all("#kg-sources .chip", "els => els.map(e => e.textContent)")

            SUBSCRIBES.clear()
            STOPS.clear()
            EVENTS.clear()
            WS_SESSIONS.clear()
            page_raw.clear()
            RAW.clear()
            page.click("#kg-start")
            page.wait_for_timeout(4000)  # 九格逐格取歷史（同一連線不接受並行請求），全部返回先至開一條串流
            grid_pull = [p for p in RAW if p.startswith("/kline")]
            grid_pull_page = [p for p in page_raw if p.startswith("/api/kline")]
            grid_events = list(EVENTS)
            grid_sessions = len(WS_SESSIONS)
            grid_subscribes = list(SUBSCRIBES)
            grid_stores = page.evaluate("() => panes['kline-grid'].stores.map(s => s.size)")
            # 九格收到的資料一模一樣，所以分派是否正確只能由圖表規格核對：日線格與分鐘格格式化同一個
            # 時間戳必然不同（每份 update 自帶 ktype，只准餵顯示該週期的格子）。
            # 順帶核對本頁用的是緊湊規格：一格只畫價格圖一個 grid，唔帶成交量格與現價大字。
            grid_cells_spec = page.evaluate(
                "() => [...document.querySelectorAll('#kg-grid .brokery-pane')].map(e => {"
                " const o = echarts.getInstanceByDom(e).getOption();"
                " return {label: o.xAxis[0].axisLabel.formatter(1760000000),"
                " grid: o.grid.length, series: o.series.length}; })")
            grid_running = page.eval_on_selector("#kg-start", "e => e.disabled")

            # 換一格嘅週期：只重取嗰格、只退該週期的串流。day 已由第七格顯示，故唔准重複訂閱。
            SUBSCRIBES.clear()
            STOPS.clear()
            page_raw.clear()
            RAW.clear()
            page.evaluate("""() => document.querySelectorAll('#kg-grid .brokery-cell')[0]
                             .querySelector('[data-ktype="day"]').click()""")
            page.wait_for_timeout(1500)
            pick_pull = [p for p in RAW if p.startswith("/kline")]
            pick_stops = list(STOPS)
            pick_subscribes = list(SUBSCRIBES)
            pick_sessions = len(WS_SESSIONS)
            pick_current = page.evaluate("() => panes['kline-grid'].current")
            pick_stores = page.evaluate("() => panes['kline-grid'].stores.map(s => s.size)")
            # 換返 1m：這一刻已沒有其他格子顯示 1m，故要補訂閱；而 day 仍有第七格顯示，故不退它。
            SUBSCRIBES.clear()
            STOPS.clear()
            page.evaluate("""() => document.querySelectorAll('#kg-grid .brokery-cell')[0]
                             .querySelector('[data-ktype="1m"]').click()""")
            page.wait_for_timeout(1500)
            back_stops = list(STOPS)
            back_subscribes = list(SUBSCRIBES)
            back_current = page.evaluate("() => panes['kline-grid'].current")
            back_stores = page.evaluate("() => panes['kline-grid'].stores.map(s => s.size)")

            # 用戶要嘅核心：同一券商同一週期可以同時有幾條串流。多週期頁已佔住 futu 的 1m（第一格，300 根），
            # 呢度照樣喺「K 線串流」頁訂閱同一券商同一週期（1000 根即另一份請求）：兩邊要各自收到推送，
            # 停其中一條唔影響另一條。呢度唔清 WS_SESSIONS：要數到兩條連接同時開住。
            page.click("nav button[data-page='kline-stream']")
            page.wait_for_timeout(500)
            SUBSCRIBES.clear()
            STOPS.clear()
            EVENTS.clear()
            page_raw.clear()
            RAW.clear()
            page.click("#ks-start")
            page.wait_for_timeout(2500)   # 先取歷史再開串流：呢度係第二條上游連接
            concurrent_sessions = len(WS_SESSIONS)
            concurrent_subscribes = list(SUBSCRIBES)
            concurrent_pull = [p for p in RAW if p.startswith("/kline")]
            concurrent_store = page.evaluate("() => panes['kline-stream'].store.size")
            # 由測試觸發推送（真實閘道由券商推送觸發）：存根按 x-api-key 鑑權，同其他請求一樣要帶。
            pushed_first = httpx.get(f"{base}/push", params={"ktype": "1m"},
                                     headers={"x-api-key": KEY}, timeout=10).json()["message"]
            page.wait_for_timeout(1500)
            both_grown = page.evaluate("() => ({grid: panes['kline-grid'].stores[0].size,"
                                       " stream: panes['kline-stream'].store.size})")
            page.click("#ks-stop")
            page.wait_for_timeout(800)
            concurrent_stops = list(STOPS)
            grid_still_streaming = page.eval_on_selector("#kg-start", "e => e.disabled")
            # start 換到 20：推送必須係新根（同一時間戳只係覆蓋，不會多兩根）。
            pushed_second = httpx.get(f"{base}/push", params={"ktype": "1m", "start": 20},
                                     headers={"x-api-key": KEY}, timeout=10).json()["message"]
            page.wait_for_timeout(1500)
            after_stop = page.evaluate("() => ({grid: panes['kline-grid'].stores[0].size,"
                                       " stream: panes['kline-stream'].store.size})")
            page.click("nav button[data-page='kline-grid']")
            page.wait_for_timeout(800)

            # 一個「停止」收齊全部格子：只送一次裸 stop，逐格只有週期按鈕，沒有逐格停止。
            STOPS.clear()
            page.click("#kg-stop")
            page.wait_for_timeout(800)
            grid_stops = list(STOPS)
            grid_reopen = page.eval_on_selector("#kg-start", "e => e.disabled")
            grid_stop_msg = page.eval_on_selector("#kg-msg", "e => e.textContent")

            # 換券商即換咗可串流的週期清單：格子要即刻跟住重建，而且照聲明的順序（ib 呢度刻意唔排序）。
            page.select_option("#kg-broker", "ib")
            page.wait_for_timeout(1200)
            ib_layout = page.evaluate("() => panes['kline-grid'].layout")
            ib_cells = len(page.query_selector_all("#kg-grid .brokery-cell"))
            page.select_option("#kg-broker", "futu")
            page.wait_for_timeout(1200)

            page.click("nav button[data-page='brokers']")
            page.wait_for_timeout(1200)
            switches = page.eval_on_selector_all(
                "#b-list label.switch",
                "els => els.map(e => [e.querySelector('input').dataset.broker,"
                " e.querySelector('input').checked, e.querySelector('input').disabled,"
                " e.querySelector('i').textContent])")
            page.uncheck("#b-list input[data-broker='tiger']")
            page_raw.clear()
            RAW.clear()
            page.click("#b-apply")
            page.wait_for_timeout(1500)
            apply_page_raw = [p for p in page_raw if p.startswith("/api/brokers/prefs/update")]
            stub_apply_raw = [p for p in RAW if p.startswith("/brokers/prefs/update")]
            after = page.eval_on_selector_all(
                "#b-list input[data-broker]",
                "els => els.map(e => [e.dataset.broker, e.checked, e.disabled])")
            page.click("nav button[data-page='kline-pull']")
            page.wait_for_timeout(1200)
            broker_after = page.eval_on_selector_all("#kp-broker option", "els => els.map(o => o.value)")
            browser.close()
    finally:
        stop(stub_server, stub_thread)
        stop(web_server, web_thread)

    check("內聯腳本無語法錯誤（無 pageerror）", not errors, "; ".join(errors) or "無 pageerror")
    check("選單為六項（多週期頁排在串流頁之後、BROKER 管理仍列最後）",
          menu == ["accounts", "symbols", "kline-pull", "kline-stream", "kline-grid", "brokers"],
          ",".join(menu))
    check("金鑰不出現在頁面中（只在服務端使用）", KEY not in page_html, "已檢查整頁 HTML")

    # ---------- 戶口頁 ----------
    check("進入即取一次戶口", loaded == ["/accounts"], ",".join(loaded))
    check("表格欄位與順序即 ACCOUNT_COLUMNS", head == list(ACCOUNT_COLUMNS), ",".join(head[:3]))
    check("第一欄為來源，兩間各一行", len(rows) == 2 and rows[0][0] == "futu" and rows[1][0] == "ib",
          f"{len(rows)} 行")
    check("資金欄為千分位兩位小數", rows[0][5] == "1,000.00" and rows[1][5] == "2,000.00",
          rows[0][5] if rows else "")
    check("取不到的金額顯示破折號（不湊數）", rows[1][9] == "—" and rows[1][10] == "—",
          rows[1][9] if len(rows) > 1 else "")
    check("按來源統計戶口數", account_chips == ["futu1 個戶口", "ib1 個戶口"], ",".join(account_chips))
    check("個別券商失敗時以警告色顯示（仍算成功）", "msg warn" in account_msg and "注意" in account_msg,
          account_msg)
    check("狀態列顯示已連接閘道", status == "已連接閘道", status)
    check("「重新整理」會再取一次", refreshed == ["/accounts"], ",".join(refreshed))
    check("戶口頁的自動更新以秒為單位，預設 0（不更新）", interval_default == ["0", "0"],
          str(interval_default))
    check("秒數為 0 時不會定時重取（空轉 2.5 秒沒有新請求）", not idle_accounts, ",".join(idle_accounts))
    check("設為 1 秒後戶口頁會定時重取", auto_accounts and all(h == "/accounts" for h in auto_accounts),
          ",".join(auto_accounts))
    check("改回 0 即停止定時重取", not stopped_accounts, ",".join(stopped_accounts))

    # ---------- 標的頁（含離線 CODES 兩個按鈕的分工）----------
    # 快照狀態與清單無關（離線讀回，不需券商連線），故兩者在進入該頁時同時送出，順序不作要求。
    check("進入標的頁先取能力聲明再取清單",
          [h for h in sym_hits if not h.startswith("/codes/meta")] == ["/capabilities",
                                                                       "/stocks?broker=futu"],
          ",".join(sym_hits))
    check("進入標的頁同時讀離線快照狀態（不需券商連線）",
          any(h.startswith("/codes/meta") for h in sym_hits), ",".join(sym_hits))
    check("快照一行點名券商並顯示其行數與距今時間，過舊及上次更新失敗以警告色提示",
          "msg warn" in snapshot_line and "futu 的離線 CODES：38569 條" in snapshot_line
          and "1 天前" in snapshot_line and "上次更新失敗" in snapshot_line, snapshot_line)
    check("標的頁的自動更新以秒為單位，預設 0 且不向券商重拉",
          symbols_interval == ["0", "0"] and live_default is False,
          f"{symbols_interval} 向券商重拉={live_default}")
    check("「讀取離線 CODES」只讀所選券商那一檔（不打券商，也不重讀快照狀態）",
          offline_query == ["/codes?broker=futu"], ",".join(offline_query))
    check("離線讀回的內容填入下方表格（欄位即 COLUMNS）",
          len(offline_rows) == 3 and offline_rows[0] == "HK.00700", ",".join(offline_rows))
    check("離線讀取明確標註未向券商取數", "離線讀取，未向券商取數" in offline_msg, offline_msg)
    check("「更新離線 CODES」只向所選券商重拉（不带市場參數），完成後重讀該家的快照狀態",
          codes_query[:1] == ["/codes/refresh?broker=futu"] and all("markets" not in q for q in codes_query)
          and "/codes/meta?broker=futu" in codes_query, ",".join(codes_query))
    check("更新的結果原樣顯示（含各品種增減）", "已更新 38569 條 CODES" in refresh_msg, refresh_msg)
    check("券商選項由能力聲明填充，默認 futu（不提供該品種者標註原因且不可選）",
          broker_value == "futu" and broker_opts == ["futu|futu|可選", "ib|ib（不提供股票）|不可選",
                                                    "tiger|tiger|可選"], ",".join(broker_opts))
    check("下方表格欄位即 COLUMNS", sym_head == list(COLUMNS), ",".join(sym_head[:3]))
    check("市場選項只由返回的 market 填充", market_opts == ["", "HK", "US"], ",".join(market_opts))
    check("按來源統計條數", sym_chips == ["futu2 條"], ",".join(sym_chips))
    check("選市場後只向該市場再取一次", market_query == ["/stocks?broker=futu&markets=HK"],
          ",".join(market_query))
    # 轉類型後市場重設為全部，選項再由新品种返回的 market 重建（不是沿用上一品種的清單）。
    check("轉類型即轉到對應接口，市場重設為全部",
          kind_query == ["/indices?broker=futu"] and market_after_kind == ""
          and markets_after_kind == ["", "HK", "US"],
          f"{','.join(kind_query)} 選中={market_after_kind or '全部'} 選項={','.join(markets_after_kind)}")
    # 各券商各存一檔：換券商即換了一檔快照，清單與快照狀態都必須跟著改，否則顯示的是另一家的代碼表。
    check("換券商即改讀該家那一檔，快照一行點名該家與其行數（不含別家的行數）",
          switch_query == sorted(["/indices?broker=ib", "/codes/meta?broker=ib"])
          and "ib 的離線 CODES：14819" in ib_line and "38569" not in ib_line
          and "上次更新失敗" not in ib_line, f"{','.join(switch_query)}｜{ib_line}")
    check("「更新離線 CODES」只向所選的 ib 重拉（不带市場參數）",
          ib_refresh[:1] == ["/codes/refresh?broker=ib"] and all("markets" not in q for q in ib_refresh),
          ",".join(ib_refresh))
    check("標的頁定時更新預設只重讀離線快照（不打券商）",
          auto_offline and all(q == "/codes?broker=ib" for q in auto_offline), ",".join(auto_offline))
    check("勾上「自動向券商重拉」後定時更新改為向券商取清單",
          auto_live and all(q.startswith("/indices?") for q in auto_live), ",".join(auto_live))
    check("標的頁改回 0 秒即停止定時更新", not stopped_symbols, ",".join(stopped_symbols))

    # ---------- 兩個 K 線頁與 BROKER 管理頁 ----------
    check("兩個 K 線頁的預設值為 HK.HSImain／1m／1000／生效的第一家",
          all(v == ["HK.HSImain", "1m", "1000", "futu"] for v in defaults.values()), str(defaults))
    check("週期與券商選項由 /api/capabilities 填充，預設選中 1m 與 futu",
          ktype_options == list(KTYPE_ORDER) and broker_options == ["futu", "ib", "tiger"],
          f"週期={ktype_options} 券商={broker_options}")
    check("進入 K 線頁不自動取數，亦沒有任何定時請求", not idle_requests, ",".join(idle_requests))
    check("取歷史經 /api/kline 轉發，閘道收到所選標的、週期、根數與券商",
          pull_page_raw == ["/api/kline?code=HK.HSImain&ktype=1m&count=1000&broker=futu"]
          and pull_raw == ["/kline?code=HK.HSImain&broker=futu&ktype=1m&count=1000"],
          f"{','.join(pull_page_raw)} → {','.join(pull_raw)}")
    check("下方 DF 按時間反序：最新在最上",
          pull_head[:3] == K_COLUMNS[:3] and pull_ts == sorted(pull_ts, reverse=True) and len(pull_ts) == 4,
          ",".join(str(t) for t in pull_ts))
    check("按來源統計只列有返回者", chips == ["futu4 根"], ",".join(chips))
    # 用戶要的是原數據：接口返回 120 根，表格即 120 行，不得只列最近若干行
    check("DF 列出接口返回的全部行（不截斷），仍按時間反序",
          many_rows == 120 and many_ts == [K_BASE + 119 * 60, K_BASE], f"{many_rows} 行 {many_ts}")
    check("訂閱即送出與閘道協定相同的 subscribe（且只開一條上游 WebSocket）",
          stream_subscribe[-1:] and stream_subscribe[-1]["codes"] == ["HK.HSImain"]
          and stream_subscribe[-1]["ktype"] == "1m" and stream_subscribe[-1]["count"] == 1000
          and stream_sessions == 1,
          f"{stream_subscribe[-1:]}｜{stream_sessions} 條")
    # 串流的 update 只帶最近 count 根：一律先取歷史再開串流，先至係一條連續序列（普通行情軟件嘅做法）。
    check("撳「訂閱實時」先取歷史、先至建立串流（/kline 在 subscribe 之前）",
          stream_events == ["kline", "subscribe"], ",".join(stream_events))
    check("取歷史失敗即唔訂閱，並清走舊標的的序列（不留一張只有實時 bar 的圖）",
          failed_events == ["kline"] and not failed_subscribes and failed_store == 0
          and failed_enabled is False and "broker_disabled" in failed_msg,
          f"{','.join(failed_events)} 訂閱={len(failed_subscribes)} 序列={failed_store} {failed_msg}")
    check("已訂閱與已更新的提示如實顯示",
          any("已訂閱 futu HK.HSImain 1m" in m and "秒後自動結束" in m for m in stream_msgs)
          and any("已更新 HK.HSImain" in m and "本次 3 根" in m and "合併後 5 根" in m for m in stream_msgs),
          stream_msg)
    check("update 與已收到的序列合併（同 ts 覆蓋，行數不縮減）",
          merged_ts == [K_BASE + i * 60 for i in (4, 3, 2, 1, 0)] and store_size == 5
          and float(merged_top) == 9999.0,
          f"ts={merged_ts} size={store_size} top={merged_top}")
    check("訂閱期間「訂閱」停用，按「停止」後可再訂閱",
          start_disabled is True and stop_enabled is False, f"進行中={start_disabled} 停止後={stop_enabled}")
    check("K 線串流頁在 DF 上方以本地 echarts 畫出 canvas（無 CDN）",
          stream_canvases == 1 and chart_above_table,
          f"{stream_canvases} 個 canvas／圖在表格前={chart_above_table}")
    check("圖與表格同一份序列：表格行數即合併後的根數",
          len(merged_ts) == store_size == 5, f"表格 {len(merged_ts)} 行／序列 {store_size} 根")
    # 根數可任選（用戶要求）：頁面不得把根數寫死成 1000 —— 請求、合併上限與圖的窗口三者都要跟隨它。
    check("根數可任填（上限 100000，與桌面 GUI 一致）；3000 原樣送到閘道，合併器上限跟住 3000",
          all(v == "100000" for v in count_max.values())
          and deep_page_raw == ["/api/kline?code=HK.HSImain&ktype=1m&count=3000&broker=futu"]
          and deep_raw == ["/kline?code=HK.HSImain&broker=futu&ktype=1m&count=3000"]
          and deep_limit == 3000,
          f"{count_max}｜{','.join(deep_raw)}｜上限={deep_limit}")
    check("所請求的根數全部喺圖上：開圖窗口 start: 0，圖上的 bar 數即合併後的根數",
          chart_view["start"] == 0 and chart_view["bars"] == chart_view["store"] == 5, str(chart_view))
    check("換週期即換該次輸入：x 軸格式跟住改（日線只到日期，唔係照開圖時的週期）",
          relabel["ktype"] == "day" and len(relabel["label"]) == 10 and " " not in relabel["label"],
          str(relabel))
    check("被閘道以協定錯誤拒絕即原樣顯示它點名的原因（界面不自造原因、不代用戶改參數，亦唔只寫「串流失敗」了事）",
          any("ktype_unsupported: futu 未聲明可串流的週期 1m" in m for m in bad_msgs)
          and "ktype_unsupported" in bad_msg,
          bad_msg)
    check("協定錯誤不會被界面自動重送：用戶改參數之前重送只會再撞同一個錯誤，故只送一次訂閱",
          len(bad_subscribes) == 1 and bad_events == ["kline", "subscribe"],
          f"{len(bad_subscribes)} 次訂閱／{','.join(bad_events)}")
    check("被拒之後撳「停止」即收返呢條連接並解鎖按鈕（原因仍留在提示上），界面唔會自己解鎖",
          bad_locked is True and bad_reopen is False and "ktype_unsupported" in bad_msg
          and bad_stops == [{"action": "stop"}],
          f"進行中={bad_locked} 停止後={bad_reopen}｜{bad_stops}")
    # ---------- 多週期頁（3×3）：格子即券商聲明可串流的週期 ----------
    nine = list(KTYPE_ORDER)
    day_at = nine.index("day")
    check("進入多週期頁只按聲明起格子：不自動取數，亦沒有任何定時請求",
          not grid_idle, ",".join(grid_idle))
    check("多週期頁的預設值為 HK.HSImain／每格 300 根／生效的第一家，根數上限 100000（與其它頁一致）",
          grid_controls == {"code": "HK.HSImain", "count": "300", "broker": "futu"}
          and grid_count_max == "100000", f"{grid_controls} 上限={grid_count_max}")
    check("格子數與順序即該券商聲明的 stream_ktypes（界面不自選別家、不排序、不憑空補週期）",
          grid_layout == STREAM_KTYPES["futu"] == nine and grid_cells == 9,
          f"{grid_cells} 格 {grid_layout}")
    check("九格九個圖表實例，各自獨立（一格一序列）", grid_instances == 9, f"{grid_instances} 個實例")
    check("每格上方一排水平週期按鈕：九個週期全列出，只有該格現有的那個高亮，且同一格內同一水平線",
          grid_tabs == [[k + ("*" if k == grid_layout[i] else "") for k in nine]
                        for i in range(len(grid_layout))]
          and all(len(row) == 9 for row in grid_tabs) and grid_tab_rows == [1] * 9,
          f"{grid_tabs[:1]}｜水平={grid_tab_rows}")
    check("下方不列 DF（本頁只有格子，沒有表格）", grid_no_table, "無 table")
    check("九格沒有表格，故以格子數與每格根數作摘要",
          grid_summary == ["9 格每格 300 根"], ",".join(grid_summary))
    check("緊湊規格：一格只畫價格圖（一個 grid、一條 series），不帶成交量格與現價大字",
          all(c["grid"] == 1 and c["series"] == 1 for c in grid_cells_spec),
          str([(c["grid"], c["series"]) for c in grid_cells_spec[:2]]))
    check("撳「開始」先逐格取歷史（九格各按自己嘅週期），全部返回先至訂閱",
          grid_pull_page == [f"/api/kline?code=HK.HSImain&ktype={k}&count=300&broker=futu" for k in nine]
          and grid_pull == [f"/kline?code=HK.HSImain&broker=futu&ktype={k}&count=300" for k in nine]
          and grid_events == ["kline"] * 9 + ["subscribe"] * 9,
          f"{len(grid_pull)} 次取數／{','.join(grid_events[:3])}…")
    check("九個週期只用一條上游 WebSocket，訂閱照各格顯示的週期各送一次",
          grid_sessions == 1 and [s["ktype"] for s in grid_subscribes] == nine
          and all(s["codes"] == ["HK.HSImain"] and s["count"] == 300 and s["broker"] == "futu"
                  for s in grid_subscribes),
          f"{len(grid_subscribes)} 個訂閱／{grid_sessions} 條連接")
    check("九格各自合併到 5 根（同 ts 覆蓋、行數不縮減）",
          grid_stores == [5] * 9, str(grid_stores))
    check("update 按 ktype 分派到該格：日線格與分鐘格的 x 軸格式不同",
          grid_cells_spec[day_at]["label"] != grid_cells_spec[0]["label"]
          and len(grid_cells_spec[day_at]["label"]) == 10 and " " not in grid_cells_spec[day_at]["label"],
          f"1m={grid_cells_spec[0]['label']} day={grid_cells_spec[day_at]['label']}")
    check("訂閱期間「開始」停用，按「停止」後可再開始",
          grid_running is True and grid_reopen is False, f"進行中={grid_running} 停止後={grid_reopen}")
    check("換一格嘅週期只重取嗰格：只多一個該週期的請求，其餘八格的序列不動",
          pick_pull == ["/kline?code=HK.HSImain&broker=futu&ktype=day&count=300"]
          and pick_current[0] == "day" and pick_stores == [4] + [5] * 8,
          f"{','.join(pick_pull)}｜各格={pick_stores}")
    check("換一格只退該週期的串流（裸 stop 只帶 broker/ktype），而且唔再開第二條連接",
          pick_stops == [{"action": "stop", "broker": "futu", "ktype": "1m"}] and pick_sessions == grid_sessions,
          f"{pick_stops}｜由開始至今 {pick_sessions} 條（原本 {grid_sessions} 條）")
    check("該週期已有另一格顯示即沿用同一份推送，唔重複訂閱",
          not pick_subscribes, f"{len(pick_subscribes)} 個訂閱")
    check("換返一個已無格子顯示的週期即補訂閱，而舊週期仍有另一格顯示即不退它",
          back_stops == [] and [s["ktype"] for s in back_subscribes] == ["1m"]
          and back_current[0] == "1m" and back_stores == [5] * 9,
          f"退={back_stops} 補={[s['ktype'] for s in back_subscribes]}")
    # 用戶要嘅核心：一份串流由請求簽名界定，同一券商同一週期可並行多條，兩邊界面都唔使等。
    check("多週期頁已佔住 futu 的 1m，K 線串流頁照樣訂閱同一券商同一週期（另開一條連接、唔被拒、唔使等）",
          concurrent_sessions == 2
          and concurrent_pull == ["/kline?code=HK.HSImain&broker=futu&ktype=1m&count=1000"]
          and [s["ktype"] for s in concurrent_subscribes] == ["1m"]
          and all(s["codes"] == ["HK.HSImain"] and s["count"] == 1000 and s["broker"] == "futu"
                  for s in concurrent_subscribes),
          f"{concurrent_sessions} 條連接｜{','.join(concurrent_pull)}")
    check("同一週期的兩條串流各自收到推送（各 +2 根），互不取代",
          concurrent_store == 5 and pushed_first == "pushed:2"
          and both_grown == {"grid": 7, "stream": 7},
          f"{concurrent_store} → {both_grown}｜{pushed_first}")
    check("停其中一條只收返該條：另一條照舊串流並繼續收推送，已收返嘅連接唔再被填",
          concurrent_stops == [{"action": "stop"}] and grid_still_streaming is True
          and pushed_second == "pushed:1" and after_stop == {"grid": 9, "stream": 7},
          f"{concurrent_stops}｜收返後={after_stop}｜{pushed_second}")
    check("一個「停止」收齊全部格子：只送一次裸 stop，其後提示已停止",
          grid_stops == [{"action": "stop"}] and "已停止 futu 串流" in grid_stop_msg,
          f"{grid_stops}｜{grid_stop_msg}")
    check("換券商即按聲明重建格子，並照返回嘅順序（ib 只聲明三個週期，順序唔照 KTYPE_ORDER）",
          ib_layout == STREAM_KTYPES["ib"] == ["5m", "1m", "day"] and ib_cells == 3,
          f"{ib_layout} {ib_cells} 格")
    check("BROKER 管理頁列出全部券商，未配置者灰掉並讀 detail",
          [s[0] for s in switches] == BROKERS and [s[1] for s in switches] == [True, True, True, False]
          and [s[2] for s in switches] == [False, False, False, True]
          and "API_SOURCES" in switches[3][3], str(switches))
    check("套用開關只經本應用的 /api/brokers/prefs/update，並原樣轉給閘道",
          apply_page_raw == ["/api/brokers/prefs/update?enabled=futu%2Cib"]
          and stub_apply_raw == ["/brokers/prefs/update?enabled=futu%2Cib"],
          f"{','.join(apply_page_raw)} → {','.join(stub_apply_raw)}")
    check("寫入後開關頁以回應重畫（tiger 已停用、webull 仍不可勾）",
          [s[1] for s in after] == [True, True, False, False], str(after))
    check("被停用者即時從各頁的券商下拉框消失",
          broker_after == ["futu", "ib"], ",".join(broker_after))

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": None, "message": "失敗：" + "；".join(failed)}
    return {"status": True, "data": None,
            "message": f"{len(checks)} 項檢查全過：轉發口徑（含省略參數、業務失敗與鑑權還原）、"
                        "服務端金鑰、一份 /static 圖表規格（含格子容器）、WS 代理雙向透傳與上游不可達的明確錯誤、"
                        "六項選單、戶口與標的表格及來源統計、離線 CODES 按券商各讀各更新自己那一檔、"
                        "兩頁自動更新預設 0 時完全不打請求、各頁預設值與 DF 反序、"
                        "DF 列出接口返回的全部行（原數據不截斷）、串流合併、"
                        "K 線串流頁 DF 上方的圖與表格同一份序列、"
                        "多週期頁按聲明起九格、九個訂閱只用一條連接、逐格取數與逐格退該週期的串流、"
                        "同一券商同一週期可並行多條（兩邊各自收推送、停一條唔影響另一條）、"
                        "換券商即按聲明重建格子、"
                        "BROKER 開關與下拉框即時更新均正常"}


if __name__ == "__main__":
    result = main()
    print(result["message"])
    raise SystemExit(0 if result["status"] else 1)
