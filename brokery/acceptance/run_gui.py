"""驗收 `brokery_gui`（PySide6 桌面 GUI）：界面只負責顯示，資料一律經 brokery_api 閘道（以存根閘道提供
/accounts、/capabilities 與三個清單接口，不連任何券商、不佔用 .env 的 API_PORT）。以 offscreen 方式離屏運行，
不需顯示器。核對：

* 界面與文字分離：三個 .ui 檔內不含任何文字（<string>），顯示文字一律由 locales/<語言>.json 按鍵取；
* 多語：繁體中文／简体中文／English 三份語言檔鍵集合一致，切換即時生效且不需重建窗口，界面用到的鍵無缺譯；
* 表格欄位與順序即 ACCOUNT_COLUMNS／COLUMNS（由返回的 columns 決定），取不到的金額顯示破折號、資金欄為
  千分位兩位小數、按來源統計條數；
* 券商選項只由 /capabilities 的能力聲明填充且默認 futu（不提供該品種者標註原因且不可選）、市場選項只由
  返回的 market 填充、轉類型即轉到對應接口並重設為全部市場；
* 閘道不可達與金鑰不正確均明確報錯（狀態列為取數失敗、原因原樣顯示）；未設 API_KEY 即拒絕建立客戶端。

以腳本方式直接執行：
    python brokery/acceptance/run_gui.py
"""
import json
import os
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")  # 離屏運行，不需顯示器

from PySide6 import QtWidgets  # noqa: E402

from brokery.brokers.base import ACCOUNT_COLUMNS, COLUMNS  # noqa: E402
from brokery_gui.api import GatewayClient  # noqa: E402
from brokery_gui.app import DesktopGui, cell_text  # noqa: E402
from brokery_gui.i18n import LOCALE_DIR, Translator, available, load  # noqa: E402

KEY = "gui-acceptance-key-9c31"
MESSAGE = "ok: 2 個戶口（來源 futu, ib）；注意：ib: ConnectionError: 未連接"
# ib 兩欄取唔到：必須原樣為 null，由界面顯示破折號，唔准以任何數字湊出。
ACCOUNT_ROWS = [
    ["futu", "1234567", "individual", "ACTIVE", "HKD",
     1000.0, 900.0, 100.0, 800.0, 500.0, 60.0, 40.0, 950.0, 12.5, 3.5],
    ["ib", "U11976982", "individual", "ACTIVE", "USD",
     2000.0, 1500.0, 500.0, 1500.0, None, None, None, 2000.0, -25.0, 0.0],
]
SYMBOL_ROWS = [
    ["HK.00700", "騰訊控股", "HK", "700", "stock", "HKD", "HKEX", "", "futu", "700"],
    ["US.NVDA", "英偉達", "US", "NVDA", "stock", "USD", "NASDAQ", "", "futu", "NVDA"],
]
# 能力聲明：ib 唔提供股票 → 該選項應標註原因且不可選（由適配器聲明，唔喺界面硬寫）。
CAPABILITIES = {
    "sources": ["futu", "ib"],
    "adapters": {
        "futu": {"capabilities": ["stock", "future", "index"]},
        "ib": {"capabilities": ["future", "index"]},
    },
}


class Stub(BaseHTTPRequestHandler):
    """存根閘道：只提供戶口、能力與三個清單接口，並記錄收到的金鑰與完整路徑，足以核對請求口徑。"""

    hits: list[str] = []
    queries: list[str] = []
    keys: list[str] = []

    def log_message(self, *args) -> None:
        pass

    def do_GET(self) -> None:
        supplied = self.headers.get("x-api-key") or ""
        path = self.path.split("?")[0]
        Stub.keys.append(supplied)
        Stub.hits.append(path)
        Stub.queries.append(self.path)
        if supplied != KEY:
            body, code = {"detail": "forbidden: API Key 不正確"}, 403
        elif path == "/capabilities":
            body, code = {"status": True, "data": CAPABILITIES, "message": "ok"}, 200
        elif path in ("/stocks", "/futures", "/indices"):
            body, code = {"status": True, "data": {"columns": COLUMNS, "rows": SYMBOL_ROWS},
                          "message": "ok"}, 200
        elif path == "/accounts":
            body, code = {"status": True, "data": {"columns": ACCOUNT_COLUMNS, "rows": ACCOUNT_ROWS},
                          "message": MESSAGE}, 200
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


def pump(qt, gui, seconds: int = 20) -> bool:
    """等背景請求完成（含能力聲明後接續的清單請求）：有上限，超時即回報，不無限等待。"""
    deadline = time.time() + seconds
    while gui._jobs and time.time() < deadline:
        qt.processEvents()
        time.sleep(0.02)
    for _ in range(5):  # 讓已排入隊列的信號先送達
        qt.processEvents()
    return not gui._jobs


def headers(table) -> list[str]:
    return [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]


def cell(table, row: int, column: int) -> str:
    item = table.item(row, column)
    return item.text() if item else ""


def combo_items(combo) -> list[str]:
    return [f"{combo.itemText(i)}|{'可選' if combo.model().item(i).isEnabled() else '不可選'}"
            for i in range(combo.count())]


def main() -> dict:
    checks: list[tuple[str, bool, str]] = []

    def check(label: str, passed: bool, detail: str = "") -> None:
        checks.append((label, bool(passed), str(detail)))

    ui_dir = Path(__file__).resolve().parents[2] / "brokery_gui" / "ui"
    texts = {p.name: p.read_text(encoding="utf-8") for p in sorted(ui_dir.glob("*.ui"))}
    check("界面與文字分離：三個 .ui 檔齊全且檔內不含任何文字",
          set(texts) == {"accounts_page.ui", "main_window.ui", "symbols_page.ui"}
          and all("<string>" not in t for t in texts.values()), ",".join(sorted(texts)))

    keysets = {lang: set(load(lang)) for lang in available()}
    check("三種語言各一個 .json 且鍵集合一致",
          len(keysets) == 3 and len({frozenset(s) for s in keysets.values()}) == 1,
          "；".join(f"{k}={len(v)}" for k, v in keysets.items()))
    translator = Translator("en")
    check("缺譯時返回鍵名本身（不憑空造一句湊數）",
          translator.t("no.such.key") == "no.such.key" and translator.missing == ["no.such.key"],
          f"語言檔目錄 {LOCALE_DIR.name}")

    try:
        GatewayClient(base_url="http://127.0.0.1:1", api_key="")
        refused = False
    except RuntimeError as exc:
        refused = "API_KEY" in str(exc)
    check("未設 API_KEY 即拒絕建立客戶端", refused, "已拒絕")

    stub = ThreadingHTTPServer(("127.0.0.1", 0), Stub)
    threading.Thread(target=stub.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{stub.server_address[1]}"
    qt = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    gui = DesktopGui(GatewayClient(base_url=base, api_key=KEY))
    window_id = id(gui.window)
    check("進入戶口頁即取一次並完成", pump(qt, gui), "背景請求未在 20 秒內完成")
    table = gui.accounts.accountsTable
    check("戶口表格欄位與順序即 ACCOUNT_COLUMNS", headers(table) == ACCOUNT_COLUMNS, ",".join(headers(table)[:3]))
    check("行數與返回一致", table.rowCount() == len(ACCOUNT_ROWS), f"{table.rowCount()} 行")
    check("請求時帶 X-API-Key", Stub.keys == [KEY], ",".join(Stub.keys))
    check("資金欄為千分位兩位小數", cell(table, 0, 5) == "1,000.00" and cell(table, 1, 5) == "2,000.00",
          cell(table, 0, 5))
    check("取不到的金額顯示破折號（不湊數）", cell(table, 1, 9) == "—" and cell(table, 1, 10) == "—",
          cell(table, 1, 9))
    check("非資金欄按原樣顯示", cell(table, 0, 0) == "futu" and cell(table, 0, 1) == "1234567", cell(table, 0, 1))
    summary = gui.accounts.summaryLabel.text()
    check("按來源統計戶口數", "futu：1 個戶口" in summary and "ib：1 個戶口" in summary, summary)
    check("狀態列顯示已連接閘道", gui.window.statusLabel.text() == "已連接閘道", gui.window.statusLabel.text())
    check("個別券商失敗時原因原樣顯示且以警告色提示", "注意" in gui.accounts.messageLabel.text()
          and "b26a00" in gui.accounts.messageLabel.styleSheet(), gui.accounts.messageLabel.text()[:40])

    gui.window.tabs.setCurrentIndex(1)
    pump(qt, gui)
    check("進入標的頁先取能力聲明再取清單", Stub.hits[-2:] == ["/capabilities", "/stocks"],
          ",".join(Stub.hits[-3:]))
    broker_combo = gui.symbols.brokerCombo
    check("券商選項由能力聲明填充，默認 futu，不提供股票者標註原因且不可選",
          broker_combo.currentData() == "futu"
          and combo_items(broker_combo) == ["futu|可選", "ib（不提供股票）|不可選"],
          ",".join(combo_items(broker_combo)))
    check("標的表格欄位即 COLUMNS", headers(gui.symbols.symbolsTable) == COLUMNS,
          ",".join(headers(gui.symbols.symbolsTable)[:3]))
    check("市場選項只由返回的 market 填充",
          [gui.symbols.marketCombo.itemData(i) for i in range(gui.symbols.marketCombo.count())] == ["", "HK", "US"],
          ",".join(gui.symbols.marketCombo.itemData(i) for i in range(gui.symbols.marketCombo.count())))
    Stub.queries.clear()
    gui.symbols.marketCombo.setCurrentIndex(gui.symbols.marketCombo.findData("HK"))
    pump(qt, gui)
    check("選市場後只向該市場再取一次", Stub.queries == ["/stocks?broker=futu&markets=HK"], ",".join(Stub.queries))
    Stub.queries.clear()
    gui.symbols.kindCombo.setCurrentIndex(gui.symbols.kindCombo.findData("index"))
    pump(qt, gui)
    check("轉類型即轉到 /indices，市場重設為全部",
          Stub.queries == ["/indices?broker=futu"] and gui.symbols.marketCombo.currentData() == "",
          ",".join(Stub.queries))
    check("轉類型後不提供該品種的券商變為可選",
          combo_items(broker_combo) == ["futu|可選", "ib|可選"], ",".join(combo_items(broker_combo)))
    Stub.queries.clear()
    gui.symbols.fetchButton.click()
    pump(qt, gui)
    check("「取得」按鈕會再取一次", Stub.queries == ["/indices?broker=futu"], ",".join(Stub.queries))

    for language, tab0, kind0 in (("zh-Hans", "户口清单", "股票"), ("en", "Accounts", "Stocks")):
        gui.set_language(language)
        qt.processEvents()
        check(f"切換語言即時生效（{language}）且不需重建窗口",
              gui.window.tabs.tabText(0) == tab0 and gui.symbols.kindCombo.itemText(0) == kind0
              and id(gui.window) == window_id, gui.window.tabs.tabText(0))
    check("界面用到的鍵在三種語言下均無缺譯", gui.tr.missing == [], ",".join(gui.tr.missing))

    down = DesktopGui(GatewayClient(base_url=f"http://127.0.0.1:{free_port()}", api_key=KEY))
    pump(qt, down)
    check("閘道不可達時明確報錯（狀態列為取數失敗，原因原樣顯示）",
          down.window.statusLabel.text() == "取數失敗"
          and down.accounts.messageLabel.text().startswith("gateway_unreachable:"),
          down.accounts.messageLabel.text()[:60])
    wrong = DesktopGui(GatewayClient(base_url=base, api_key="wrong-key"))
    pump(qt, wrong)
    check("金鑰不正確時明確報錯並點名 403",
          wrong.window.statusLabel.text() == "取數失敗" and "gateway_http_403" in wrong.accounts.messageLabel.text(),
          wrong.accounts.messageLabel.text()[:60])
    check("資金欄格式化不誤傷文字", cell_text("N/A", "cash") == "N/A", cell_text("N/A", "cash"))

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": None, "message": "失敗：" + "；".join(failed)}
    return {"status": True, "data": None,
            "message": f"{len(checks)} 項檢查全過：.ui 不含文字、三種語言鍵集合一致且即時切換、表格欄位即欄位契約、"
                       "缺失值破折號、券商選項由能力聲明填充、市場選項只由返回值填充、閘道不可達與金鑰不正確均明確報錯"}


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
