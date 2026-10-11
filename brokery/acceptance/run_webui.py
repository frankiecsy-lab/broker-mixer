"""驗收 `brokery_webui`：Web UI 只做頁面與轉發，資料一律經 brokery_api 閘道（不連任何券商、不佔用 .env 的
API_PORT）。以存根閘道提供 /accounts、/capabilities、三個清單接口與 /codes/meta、/codes/refresh，核對：

* 轉發原樣透傳信封：欄位與順序即 ACCOUNT_COLUMNS／COLUMNS、行與 message 逐字一致，並帶 X-API-Key 請求閘道；
* /api/symbols 按類型轉到對應的清單接口，并把市場與券商原樣傳為 markets／broker（能力閘在 core，Web UI
  不自行改選別家）；類型不認識即 unknown_kind，不猜用戶想要什麼；
* 金鑰不正確與閘道不可達均返回 status=False 並點名原因（不變成 HTTP 500）；未設 API_KEY 即拒絕建立應用；
* 頁面以 Chromium 載入後內聯腳本無語法錯誤：菜單兩項（戶口清單、標的列表）；戶口頁進入即取一次，欄位
  與順序即 ACCOUNT_COLUMNS、第一欄為來源、資金欄為千分位兩位小數、缺失值顯示破折號、按來源統計戶口數；
  標的頁的券商選項由 /capabilities 填充且默認 futu（不提供該品種者標註且不可選）、市場選項只由返回的
  market 填充、下方表格欄位即 COLUMNS、轉類型會重設為全部市場、向對應接口再取一次，選項再由新品种重建；
  標的頁另列一列顯示離線 CODES 快照的行數與距今時間（轉發 /codes/meta，離線讀回，不需券商連線，故與
  即時取數的統計分開），「更新離線 CODES」轉發 /codes/refresh 且不带市場參數（快照即全量）。

需要 Chromium（`pip install playwright` 後 `playwright install chromium`）；未安裝時跳過並返回成功。

以腳本方式直接執行：
    python brokery/acceptance/run_webui.py
"""
import json
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import uvicorn
from fastapi.testclient import TestClient

from brokery.brokers.base import ACCOUNT_COLUMNS, COLUMNS
from brokery.core import CODES_META_COLUMNS
from brokery_webui.app import create_app

KEY = "gui-acceptance-key-4f2a"
MESSAGE = "ok: 2 個戶口（來源 futu, ib, tiger, webull）；注意：tiger: ConnectionError: 未連接"
# ib 兩欄取唔到：必須原樣為 null，由頁面顯示破折號，唔准以任何數字湊出。
ACCOUNT_ROWS = [
    ["futu", "1234567", "individual", "ACTIVE", "HKD",
     1000.0, 900.0, 100.0, 800.0, 500.0, 60.0, 40.0, 950.0, 12.5, 3.5],
    ["ib", "U11976982", "individual", "ACTIVE", "USD",
     2000.0, 1500.0, 500.0, 1500.0, None, None, None, 2000.0, -25.0, 0.0],
]


# 標的清單的存根返回：兩行、兩個市場，足以核對欄位契約與「市場選項只由返回的 market 填充」。
# 行必須嚴格對應 COLUMNS：不設到期月欄，券商原生標識只在 raw 的原生格式中出現；symbol_type
# 與真實閘道一致為大寫常量。
SYMBOL_ROWS = [
    ["HK.00700", "騰訊控股", "HK", "700", "STOCK", "HKD", "HKEX", "futu"],
    ["US.NVDA", "英偉達", "US", "NVDA", "STOCK", "USD", "NASDAQ", "futu"],
]
# 能力聲明：ib 不提供股票 → 頁面上該選項應標註且不可選（由適配器聲明，不在頁面硬寫）。
# 值必須與真實閘道一致（symbol_type 的大寫常量），否則會掩蓋頁面以類型值直接比對能力聲明的錯誤。
CAPABILITIES = {
    "sources": ["futu", "ib"],
    "adapters": {
        "futu": {"capabilities": ["STOCK", "FUTURE", "INDEX"]},
        "ib": {"capabilities": ["FUTURE", "INDEX"]},
    },
}
# 離線 CODES 快照的元資料：一行，欄位與順序即 CODES_META_COLUMNS。刻意給一筆超過 24 小時且上次更新失敗
# 的快照（距今 90000 秒 → 頁面顯示「1 天前」），因為要驗的正是「過舊以警告色提示、並說明上次更新失敗」。
CODES_META_ROWS = [["futu_codes", 38569, 8, "2026-10-10T10:00:00+00:00", 90000.0, True, "futu",
                   "HK/US 全量 CODES", "futu: OpenD 未連接"]]
CODES_META = {"status": True, "data": {"columns": list(CODES_META_COLUMNS), "rows": CODES_META_ROWS},
              "message": "ok"}
CODES_REFRESH = {"status": True, "data": {"columns": list(CODES_META_COLUMNS), "rows": CODES_META_ROWS},
                 "message": "ok: 已更新 38569 條 CODES（FUTURE 14079（+0），INDEX 740（+0），STOCK 23750（+0））"}


class Stub(BaseHTTPRequestHandler):
    """存根閘道：只提供戶口、能力、三個清單接口與離線 CODES 的兩個接口，並記錄收到的金鑰與完整路徑，
    足以核對轉發口徑。"""

    hits: list[str] = []
    keys: list[str] = []
    queries: list[str] = []

    def log_message(self, *args) -> None:
        pass

    def do_GET(self) -> None:
        supplied = self.headers.get("x-api-key") or ""
        Stub.keys.append(supplied)
        Stub.hits.append(self.path.split("?")[0])
        Stub.queries.append(self.path)
        if supplied != KEY:
            body, code = {"detail": "forbidden: API Key 不正確"}, 403
        elif self.path.split("?")[0] == "/capabilities":
            body, code = {"status": True, "data": CAPABILITIES, "message": "ok"}, 200
        elif self.path.split("?")[0] in ("/stocks", "/futures", "/indices"):
            body, code = {"status": True, "data": {"columns": COLUMNS, "rows": SYMBOL_ROWS},
                          "message": "ok"}, 200
        elif self.path.split("?")[0] == "/accounts":
            body, code = {"status": True, "data": {"columns": ACCOUNT_COLUMNS, "rows": ACCOUNT_ROWS},
                          "message": MESSAGE}, 200
        elif self.path.split("?")[0] == "/codes/meta":
            body, code = CODES_META, 200
        elif self.path.split("?")[0] == "/codes/refresh":
            body, code = CODES_REFRESH, 200
        else:
            body, code = {"detail": f"no such path: {self.path}"}, 404
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def free_port() -> int:
    """取一個系統分配但已釋放的端口：用作「那裡沒有閘道」的反例。"""
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def serve(app) -> tuple[uvicorn.Server, int]:
    """在系統分配的端口上啟動應用（不與 .env 的 GUI_PORT 相沖），返回服務與端口。"""
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=0, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.time() + 15  # 有上限：啟動失敗要立刻回報，不能無限等待
    while not server.started and time.time() < deadline:
        time.sleep(0.05)
    if not server.started:
        raise RuntimeError("Web UI 應用在 15 秒內未啟動")
    return server, server.servers[0].sockets[0].getsockname()[1]


def main() -> dict:
    checks: list[tuple[str, bool, str]] = []

    def check(label: str, passed: bool, detail: str = "") -> None:
        checks.append((label, bool(passed), str(detail)))

    stub = ThreadingHTTPServer(("127.0.0.1", 0), Stub)
    threading.Thread(target=stub.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{stub.server_address[1]}"

    client = TestClient(create_app(base_url=base, api_key=KEY))
    Stub.hits.clear()
    Stub.keys.clear()
    got = client.get("/api/accounts").json()
    check("轉發原樣透傳信封（欄位、行與 message 逐字一致）",
          got.get("status") is True and got["data"]["columns"] == ACCOUNT_COLUMNS
          and got["data"]["rows"] == ACCOUNT_ROWS and got["message"] == MESSAGE,
          f"status={got.get('status')} 欄={got['data']['columns'][:2]} 行={len(got['data']['rows'])}")
    check("轉發時帶 X-API-Key（金鑰只在服務端）", Stub.keys == [KEY], ",".join(Stub.keys))
    check("頁面本身不含金鑰", KEY not in client.get("/").text, "已核對 / 的原始碼")

    Stub.hits.clear()
    Stub.queries.clear()
    symbols = client.get("/api/symbols", params={"kind": "stock", "market": "HK", "broker": "futu"}).json()
    check("標的清單按類型轉到 /stocks，市場與券商原樣傳為 markets／broker",
          Stub.queries == ["/stocks?broker=futu&markets=HK"], ",".join(Stub.queries))
    check("標的清單原樣透傳信封（欄位即 COLUMNS）",
          symbols.get("status") is True and symbols["data"]["columns"] == COLUMNS
          and symbols["data"]["rows"] == SYMBOL_ROWS, f"欄={symbols['data']['columns'][:3]}")
    caps = client.get("/api/capabilities").json()
    check("能力聲明轉發（券商選項由此填充，不在 Web UI 硬寫）",
          caps.get("status") is True and caps["data"]["sources"] == ["futu", "ib"],
          str(caps["data"].get("sources")))

    # 離線快照的兩個接口：元資料離線讀回、重拉需券商連線，兩者均必須原樣透傳，Web UI 不自行解讀。
    Stub.queries.clear()
    codes_meta = client.get("/api/codes/meta").json()
    check("離線 CODES 元資料轉發 /codes/meta（欄位即 CODES_META_COLUMNS）",
          Stub.queries == ["/codes/meta"] and codes_meta.get("status") is True
          and codes_meta["data"]["columns"] == list(CODES_META_COLUMNS)
          and codes_meta["data"]["rows"] == CODES_META_ROWS, ",".join(Stub.queries))
    Stub.queries.clear()
    codes_refresh = client.get("/api/codes/refresh").json()
    check("更新離線 CODES 轉發 /codes/refresh 且不带市場參數（快照即全量，只拉部分市場會被縮細防護拒絕）",
          Stub.queries == ["/codes/refresh"] and codes_refresh.get("status") is True
          and codes_refresh["message"] == CODES_REFRESH["message"], ",".join(Stub.queries))
    for kind, path in (("future", "/futures"), ("index", "/indices")):
        Stub.queries.clear()
        client.get("/api/symbols", params={"kind": kind}).json()
        check(f"類型 {kind} 轉到 {path}（默認券商 futu）", Stub.queries == [f"{path}?broker=futu"],
              ",".join(Stub.queries))
    bogus = client.get("/api/symbols", params={"kind": "option"}).json()
    check("類型不認識即 unknown_kind（不猜用戶想要什麼）",
          bogus["status"] is False and bogus["message"].startswith("unknown_kind"), bogus["message"])

    wrong = TestClient(create_app(base_url=base, api_key="wrong-key")).get("/api/accounts").json()
    check("金鑰不正確時明確返回 status=False（不變成 HTTP 500）",
          wrong["status"] is False and "gateway_http_403" in wrong["message"], wrong["message"])
    down = TestClient(create_app(base_url=f"http://127.0.0.1:{free_port()}", api_key=KEY))
    unreachable = down.get("/api/accounts").json()
    check("閘道不可達時點名原因", unreachable["status"] is False
          and unreachable["message"].startswith("gateway_unreachable:"), unreachable["message"])
    try:
        create_app(base_url=base, api_key="")
        refused = False
    except RuntimeError as exc:
        refused = "API_KEY" in str(exc)
    check("未設 API_KEY 即拒絕建立應用", refused, "已拒绝")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("SKIP 未安裝 playwright（pip install playwright && playwright install chromium）")
        return {"status": True, "data": None, "message": "跳過：未安裝 playwright"}

    server = None
    errors: list[str] = []
    try:
        server, port = serve(create_app(base_url=base, api_key=KEY))
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except Exception as exc:  # 未下載瀏覽器
                print(f"SKIP 未安裝 Chromium：{exc}")
                return {"status": True, "data": None, "message": "跳過：未安裝 Chromium"}
            page = browser.new_page()
            page.on("pageerror", lambda e: errors.append(str(e)))
            Stub.hits.clear()
            page.goto(f"http://127.0.0.1:{port}/", timeout=30000)
            page.wait_for_timeout(1500)
            loaded = list(Stub.hits)
            menu = page.eval_on_selector_all("#menu button", "els => els.map(e => e.dataset.page + '|' + e.textContent)")
            head = page.eval_on_selector_all("#a-table th", "els => els.map(e => e.textContent)")
            rows = page.eval_on_selector_all("#a-table tbody tr", "els => els.map(e => [...e.cells].map(c => c.textContent))")
            chips = page.eval_on_selector_all("#a-sources .chip", "els => els.map(e => e.textContent)")
            status = page.eval_on_selector("#status", "e => e.textContent")
            msg = page.eval_on_selector("#a-msg", "e => e.className + '|' + e.textContent")
            Stub.hits.clear()
            page.click("#a-refresh")
            page.wait_for_timeout(800)
            refreshed = list(Stub.hits)

            Stub.hits.clear()
            Stub.queries.clear()
            page.click('#menu button[data-page="symbols"]')
            page.wait_for_timeout(1500)
            sym_hits = list(Stub.hits)
            broker_opts = page.eval_on_selector_all(
                "#s-broker option",
                "els => els.map(e => e.value + '|' + e.textContent + '|' + (e.disabled ? '不可選' : '可選'))")
            broker_value = page.eval_on_selector("#s-broker", "e => e.value")
            market_opts = page.eval_on_selector_all("#s-market option", "els => els.map(e => e.value)")
            sym_head = page.eval_on_selector_all("#s-table th", "els => els.map(e => e.textContent)")
            sym_chips = page.eval_on_selector_all("#s-sources .chip", "els => els.map(e => e.textContent)")
            snapshot_line = page.eval_on_selector("#s-snapshot", "e => e.className + '|' + e.textContent")
            Stub.queries.clear()
            page.click("#s-codes-refresh")
            page.wait_for_timeout(1200)
            codes_query = list(Stub.queries)
            refresh_msg = page.eval_on_selector("#s-msg", "e => e.className + '|' + e.textContent")
            Stub.queries.clear()
            page.select_option("#s-market", "HK")
            page.wait_for_timeout(800)
            market_query = list(Stub.queries)
            Stub.queries.clear()
            page.select_option("#s-kind", "index")
            page.wait_for_timeout(800)
            kind_query = list(Stub.queries)
            market_after_kind = page.eval_on_selector("#s-market", "e => e.value")
            markets_after_kind = page.eval_on_selector_all("#s-market option", "els => els.map(e => e.value)")
            browser.close()
    finally:
        if server is not None:
            server.should_exit = True
        stub.shutdown()

    check("內聯腳本無語法錯誤", not errors, "; ".join(errors) or "無 pageerror")
    check("上方菜單兩項：戶口清單、標的列表", menu == ["accounts|戶口清單", "symbols|標的列表"],
          ",".join(menu))
    check("進入即取一次戶口", loaded == ["/accounts"], ",".join(loaded))
    check("表格欄位與順序即 ACCOUNT_COLUMNS", head == ACCOUNT_COLUMNS, ",".join(head[:3]))
    check("第一欄為來源，兩間各一行", len(rows) == 2 and rows[0][0] == "futu" and rows[1][0] == "ib",
          f"{len(rows)} 行")
    check("資金欄為千分位兩位小數", rows[0][5] == "1,000.00" and rows[1][5] == "2,000.00",
          rows[0][5] if rows else "")
    check("取不到的金額顯示破折號（不湊數）", rows[1][9] == "—" and rows[1][10] == "—",
          rows[1][9] if len(rows) > 1 else "")
    check("按來源統計戶口數", chips == ["futu1 個戶口", "ib1 個戶口"], ",".join(chips))
    check("個別券商失敗時以警告色顯示（仍算成功）", "msg warn" in msg and "注意" in msg, msg)
    check("狀態列顯示已連接閘道", status == "已連接閘道", status)
    check("「重新整理」會再取一次", refreshed == ["/accounts"], ",".join(refreshed))

    # 快照狀態與清單無關（離線讀回，不需券商連線），故兩者在進入該頁時同時送出，順序不作要求。
    check("進入標的頁先取能力聲明再取清單",
          [h for h in sym_hits if h != "/codes/meta"] == ["/capabilities", "/stocks"], ",".join(sym_hits))
    check("進入標的頁同時讀離線快照狀態（不需券商連線）", "/codes/meta" in sym_hits, ",".join(sym_hits))
    check("快照一行顯示行數與距今時間，過舊及上次更新失敗以警告色提示",
          "msg warn" in snapshot_line and "38569 條" in snapshot_line and "1 天前" in snapshot_line
          and "上次更新失敗" in snapshot_line, snapshot_line)
    check("「更新離線 CODES」只向 /codes/refresh 送出（不带市場參數），完成後重讀快照狀態",
          codes_query[:1] == ["/codes/refresh"] and all("?" not in q for q in codes_query)
          and "/codes/meta" in codes_query, ",".join(codes_query))
    check("更新的結果原樣顯示（含各品種增減）", "已更新 38569 條 CODES" in refresh_msg, refresh_msg)
    check("券商選項由能力聲明填充，默認 futu", broker_value == "futu"
          and broker_opts == ["futu|futu|可選", "ib|ib（不提供股票）|不可選"], ",".join(broker_opts))
    check("下方表格欄位即 COLUMNS", sym_head == COLUMNS, ",".join(sym_head[:3]))
    check("市場選項只由返回的 market 填充", market_opts == ["", "HK", "US"], ",".join(market_opts))
    check("按來源統計條數", sym_chips == ["futu2 條"], ",".join(sym_chips))
    check("選市場後只向該市場再取一次", market_query == ["/stocks?broker=futu&markets=HK"],
          ",".join(market_query))
    # 轉類型後市場重設為全部，選項再由新品种返回的 market 重建（不是沿用上一品種的清單）。
    check("轉類型即轉到對應接口，市場重設為全部",
          kind_query == ["/indices?broker=futu"] and market_after_kind == ""
          and markets_after_kind == ["", "HK", "US"],
          f"{','.join(kind_query)} 選中={market_after_kind or '全部'} 選項={','.join(markets_after_kind)}")

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": None, "message": "失敗：" + "；".join(failed)}
    return {"status": True, "data": None,
            "message": f"{len(checks)} 項檢查全過：菜單兩項、轉發原樣透傳信封、類型與市場/券商正確轉傳、"
                       "金鑰不正確與閘道不可達均明確報錯、戶口與標的表格及來源統計正常、"
                       "離線 CODES 快照年齡與更新按鈕轉發正常"}


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
