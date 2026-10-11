"""驗收 `brokery_webui`（Web UI）：以存根閘道（FastAPI + uvicorn，另佔一個系統分配的端口，不連任何
券商、不與 `.env` 的 API_PORT 相沖）提供 `/capabilities`、`/accounts`、`/stocks`（及 /futures、
/indices）、`/codes`、`/codes/meta`、`/codes/refresh`、`/kline`、`/brokers/prefs`、
`/brokers/prefs/update` 與 `/stream`（WebSocket，按閘道協定返回 subscribed/update/closed），
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
圖表規格：`/static/chart.js` 與 `brokery/static/` 內的檔案逐 byte 相同（只有一份，Web UI 不得另存副本）。
串流代理：以 WebSocket 客戶端連 `/ws/stream`，核對 subscribe 原樣送達上游、上游事件原樣返回，
上游不可達時返回明確的 gateway_unreachable 而不是無聲等待。
頁面（Chromium）：選單六項；戶口頁進入即取一次，欄位與順序即 ACCOUNT_COLUMNS、資金欄為千分位兩位小數、
取不到的金額顯示破折號、按來源統計戶口數；標的頁的券商選項按能力聲明標註（不提供該品種者不可選）、市場
選項只由返回的 market 填充，「讀取離線 CODES」只讀該家那一檔並標註未向券商取數，「更新離線 CODES」只向
該家重拉並重讀該家的快照狀態（過舊與上次更新失敗以警告色提示），換券商即改讀該家那一檔；兩頁的
「自動更新（秒）」預設 0（空轉數秒不得有任何請求），設 1 秒即定時重取（標的頁預設只重讀離線快照，勾上
「自動向券商重拉」才改為向券商取清單），改回 0 即停止；三個 K 線頁的預設值為 HK.HSImain／1m／1000／
生效的第一家，且進入頁面只填控件、不自動取數、亦無任何定時請求；取歷史後下方 DF 按時間反序（最新在
最上）；串流的 update 與已拉取的序列合併（同 ts 覆蓋、行數不縮減）；K 線圖頁以本地 echarts 畫出
canvas；BROKER 管理頁列出全部券商、未配置者灰掉並讀 detail，套用後各頁券商下拉框即時去掉被停用者。

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
from brokery.brokers.base import ACCOUNT_COLUMNS, COLUMNS, K_COLUMNS
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
                         "data": {"sources": names, "autype": "qfq", "ktypes": ["day", "1m"],
                                  "acc_filters": ["all"],
                                  "adapters": {n: {"capabilities": CAPABILITY_OF[n], "autypes": ["none"]}
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
        if code == "HK.DISABLED":  # 業務失敗：Web UI 必須原樣透傳，不得改寫成自己的訊息
            return envelope({"status": False, "data": {"columns": [], "rows": []},
                             "message": f"broker_disabled: {broker}（已在 BROKER 管理中停用）"})
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
        while True:
            try:
                action = await ws.receive_json()
            except Exception:  # 客戶端直接斷開：結束即可，不影響任何斷言
                return
            kind = str(action.get("action", "")).lower()
            if kind == "subscribe":
                SUBSCRIBES.append(action)
                broker = str(action.get("broker", ""))
                await ws.send_json({"event": "subscribed", "broker": broker,
                                    "codes": list(action.get("codes", [])),
                                    "ktype": action.get("ktype"), "seconds": 5})
                # 第一條帶完整的四根，第二條只帶最近三根（其中一根為新的）：客戶端必須合併而不是取代。
                await ws.send_json({"event": "update", "broker": broker, "code": "HK.HSImain",
                                    "data": kline_rows(0, 4, lambda i: 100.0 + i)})
                await ws.send_json({"event": "update", "broker": broker, "code": "HK.HSImain",
                                    "data": kline_rows(2, 3, lambda i: 9999.0)})
            elif kind == "stop":
                await ws.send_json({"event": "closed", "broker": str(action.get("broker", "")),
                                    "message": "已停止串流"})
                return
            else:
                await ws.send_json({"event": "error", "message": f"bad_action: {kind or '空'}"})

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
                        for prefix in ("kp", "ks", "kg")}
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
            page.click("#ks-start")
            page.wait_for_timeout(2000)
            stream_msgs = page.evaluate("() => window.__msgs")
            stream_msg = " | ".join(stream_msgs)
            merged_ts = page.eval_on_selector_all("#ks-table tbody tr td:nth-child(2)",
                                                  "els => els.map(e => Number(e.textContent))")
            merged_top = page.eval_on_selector("#ks-table tbody tr td:nth-child(7)", "e => e.textContent")
            store_size = page.evaluate("() => panes['kline-stream'].store.size")
            start_disabled = page.eval_on_selector("#ks-start", "e => e.disabled")
            page.click("#ks-stop")
            page.wait_for_timeout(800)
            stop_enabled = page.eval_on_selector("#ks-start", "e => e.disabled")

            page.click("nav button[data-page='kline-chart']")
            page.wait_for_timeout(300)
            page.click("#kg-load")
            page.wait_for_timeout(2000)
            canvases = len(page.query_selector_all("#kg-chart canvas"))
            chart_ts = page.eval_on_selector_all("#kg-table tbody tr td:nth-child(2)",
                                                 "els => els.map(e => Number(e.textContent))")

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
    check("選單為六項（四頁常設）",
          menu == ["accounts", "symbols", "kline-pull", "kline-stream", "kline-chart", "brokers"],
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

    # ---------- 三個 K 線頁與 BROKER 管理頁 ----------
    check("三個 K 線頁的預設值為 HK.HSImain／1m／1000／生效的第一家",
          all(v == ["HK.HSImain", "1m", "1000", "futu"] for v in defaults.values()), str(defaults))
    check("週期與券商選項由 /api/capabilities 填充，預設選中 1m 與 futu",
          ktype_options == ["day", "1m"] and broker_options == ["futu", "ib", "tiger"],
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
    check("訂閱即送出與閘道協定相同的 subscribe",
          SUBSCRIBES[-1:] and SUBSCRIBES[-1]["codes"] == ["HK.HSImain"]
          and SUBSCRIBES[-1]["ktype"] == "1m" and SUBSCRIBES[-1]["count"] == 1000,
          str(SUBSCRIBES[-1:]))
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
    check("K 線圖頁由本地 echarts 畫出 canvas（無 CDN）", canvases == 1, f"{canvases} 個 canvas")
    check("K 線圖頁的表格同樣反序", chart_ts == sorted(chart_ts, reverse=True) and len(chart_ts) == 4,
          ",".join(str(t) for t in chart_ts))
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
                        "服務端金鑰、一份 /static 圖表規格、WS 代理雙向透傳與上游不可達的明確錯誤、"
                        "六項選單、戶口與標的表格及來源統計、離線 CODES 按券商各讀各更新自己那一檔、"
                        "兩頁自動更新預設 0 時完全不打請求、四頁預設值與 DF 反序、串流合併、"
                        "BROKER 開關與下拉框即時更新均正常"}


if __name__ == "__main__":
    result = main()
    print(result["message"])
    raise SystemExit(0 if result["status"] else 1)
