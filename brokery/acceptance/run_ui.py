"""驗收 `brokery_api/ui.html` 的客戶端行為：以存根閘道（不連任何券商、不佔用 `.env` 的 API_PORT）
提供 `/`、`/health`、`/capabilities`、`/brokers`、`/logs`、`/accounts`、`/stocks`、`/codes`、
`/codes/meta`、`/codes/refresh`，再用
Chromium 載入頁面，核對內聯腳本無語法錯誤、頂欄按 `/brokers` 渲染四家連線指示（可連顯示延遲毫秒、
斷開顯示「斷開」並在懸停顯示原因）、金鑰填入後存入 localStorage 並在重新載入後自動回填，探測只由
載入與「探測連線」按鈕觸發（不輪詢）。
戶口頁另驗：沒有「來源」選擇器且請求不含 broker 參數（一律一次取四家）、首次進入即取一次、自動更新以
秒為單位且預設 0（0 時空轉亦不得有任何定時請求，設 1 秒即定時重取，改回 0 即停止）、按來源汇总並點名
無返回者、個別券商失敗時以警告色顯示。
標的頁另驗：一次點擊即按來源分四區同時填充，各區如實顯示「N 條／無返回／不提供此清單」（後兩者
含義不同，且依能力聲明判定，未聲明者不得顯示為無返回）、區內不重複 source 欄；標的頁不再有「統一格式
輸出」面板（即時清單只以分區呈現，不得另設單一合併表格）；離線 CODES 不分區，以單一表格顯示，其欄位
與順序必須與接口原樣返回的 COLUMNS 完全一致。
離線快照另驗：各券商各存一檔，故券商選擇器由 /capabilities 填充、預設為閘道的預設券商，「讀取離線 CODES」
只向 /codes?broker=… 與其元資料送出，換券商即改讀該家那一檔，快照一行必須點名該家並只顯示該家的行數；
由 /codes/meta 顯示距今時間，過舊以警告色（非錯誤色）提示；「更新離線 CODES」只向 /codes/refresh?broker=…
送出且不带市場參數（快照即全量），完成後重讀該家的快照與表格；搜尋零結果且快照過舊時必須提示按
「更新離線 CODES」（查唔到往往只係快照冇咗新上市的代碼）。標的頁的定時更新預設只重讀離線快照（不打券商），
勾上「自動向券商重拉」才改為向券商取清單。
讀取提示另驗：請求進行時訊息位與各區均顯示讀取中（存根對 /stocks 故意延遲 0.8 秒以便觀察）。

需要 Chromium（`pip install playwright` 後 `playwright install chromium`）；未安裝時跳過並返回成功。

以腳本方式直接執行：
    python brokery/acceptance/run_ui.py
"""
import json
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

from brokery.brokers.base import ACCOUNT_COLUMNS, BROKER_COLUMNS, COLUMNS
from brokery.core import CODES_META_COLUMNS

UI = Path(__file__).resolve().parents[2] / "brokery_api" / "ui.html"
ROWS = [["futu", True, 178.066, 2, "", 1791696259],
        ["ib", True, 542.042, 1, "", 1791696259],
        ["tiger", True, 1215.842, 1, "", 1791696260],
        ["webull", False, None, 0, "timeout", 1791696260]]
# 兩間有戶口、兩間無返回：汇总必須點名後兩者，否則用戶只見到「少咗一间」。acc_type 一律用
# individual（IB 原樣透傳的寫法），核對卡片照樣顯示該值而不被歸類或丟走。
ACCOUNT_ROWS = [["futu", "1234567", "individual", "ACTIVE", "HKD"] + [1000.0] * 10,
                ["ib", "U11976982", "individual", "ACTIVE", "USD"] + [2000.0] * 10]
# 股票清單只當富途有返回；ib 未聲明 STOCK 能力（應顯示「不提供此清單」），tiger 與 webull 聲明咗但
# 本次冇返回（應顯示「無返回」）— 兩者含義不同，必須分得開。行必須嚴格為 COLUMNS（見 brokers.base）：
# 不設到期月欄，券商原生標識只在 raw=True 的原生格式中出現。
STOCK_ROWS = [["HK.00700", "騰訊控股", "HK", "00700", "STOCK", "HKD", "HKEX", "futu"],
              ["US.AAPL", "蘋果", "US", "AAPL", "STOCK", "USD", "NASDAQ", "futu"]]
# 能力聲明為各家實際聲明者（實測），非湊齊：ib 冇股票清單、webull 冇指數清單。
CAPS = {"sources": ["futu", "ib", "tiger", "webull"], "ktypes": ["day", "1m"],
        "acc_filters": ["all", "cash", "margin"],
        "adapters": {"futu": {"autypes": ["none", "qfq"], "capabilities": ["STOCK", "FUTURE", "INDEX"]},
                     "ib": {"autypes": [], "capabilities": ["FUTURE", "INDEX"]},
                     "tiger": {"autypes": [], "capabilities": ["STOCK", "FUTURE", "INDEX"]},
                     "webull": {"autypes": [], "capabilities": ["STOCK", "FUTURE"]}}}
# 離線快照的元資料：一行，欄位與順序即 CODES_META_COLUMNS。刻意給一筆超過 24 小時的快照（距今 90000 秒
# → 頁面顯示「1 天前」），因為本頁要驗的正是「過舊以警告色提示」與「搜尋零結果時提示按『更新 CODES』」。
def codes_meta_rows(broker: str) -> list:
    """各券商各存一檔，行數與留痕逐家不同（ib 不提供股票，故行數明顯較少），故元資料必須按請求的
    broker 返回——若頁面把別家的行數顯示在當前券商那一行，一眼就能看出來。"""
    return [[f"{broker}_codes", 14819 if broker == "ib" else 38569, 8, "2026-10-10T10:00:00+00:00",
             90000.0, True, broker, "HK/US 全量 CODES", ""]]


def param_of(path: str, name: str) -> str:
    from urllib.parse import parse_qs
    return (parse_qs(path.split("?")[1]).get(name) or [""])[0] if "?" in path else ""


KEY = "my-secret-key"


class Stub(BaseHTTPRequestHandler):
    """只提供頁面與固定信封，足以驅動 dashboard 的載入與探測流程。"""

    hits: list[str] = []
    raw: list[str] = []          # 含查詢參數，用以核對請求帶了邊啲參數
    SLOW = {"/stocks": 0.8}      # 讀取提示只在請求較慢時需要觀察，故對該路徑故意延遲

    def log_message(self, *args) -> None:
        pass

    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        Stub.hits.append(path)
        meta_rows = codes_meta_rows(param_of(self.path, "broker") or "futu")
        Stub.raw.append(self.path)
        if path in Stub.SLOW:
            time.sleep(Stub.SLOW[path])
        if path == "/":
            raw, ctype = UI.read_bytes(), "text/html; charset=utf-8"
        else:
            body = {
                "/health": {"status": True, "data": {}, "message": "ok"},
                "/capabilities": {"status": True, "data": CAPS, "message": "ok"},
                "/brokers": {"status": True,
                             "data": {"columns": BROKER_COLUMNS, "rows": ROWS}, "message": "ok"},
                "/logs": {"status": True, "data": {"columns": ["ts", "level", "message"], "rows": []},
                          "message": "ok"},
                "/accounts": {"status": True, "data": {"columns": ACCOUNT_COLUMNS, "rows": ACCOUNT_ROWS},
                              "message": "ok: 2 個戶口（來源 futu, ib, tiger, webull）"
                                         "；注意：tiger: ConnectionError: 未連接"},
                "/stocks": {"status": True, "data": {"columns": COLUMNS, "rows": STOCK_ROWS},
                            "message": "ok（2 條）"},
                # 離線 CODES 為存放快照，唔涉及即時取數：客戶端應以單一表格顯示，唔分四區。
                "/codes": {"status": True, "data": {"columns": COLUMNS, "rows": STOCK_ROWS},
                           "message": "ok（2 條，來源 futu）"},
                "/codes/meta": {"status": True, "data": {"columns": list(CODES_META_COLUMNS),
                                                         "rows": meta_rows}, "message": "ok"},
                "/codes/refresh": {"status": True,
                                   "data": {"columns": list(CODES_META_COLUMNS), "rows": meta_rows},
                                   "message": "ok: 已更新 2 條 CODES（STOCK 2（+0））"},
            }.get(path, {"status": False, "data": {}, "message": "stub"})
            raw, ctype = json.dumps(body, ensure_ascii=False).encode("utf-8"), "application/json"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def main() -> dict:
    checks: list[tuple[str, bool, str]] = []

    def check(label: str, passed: bool, detail: str = "") -> None:
        checks.append((label, bool(passed), str(detail)))

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("SKIP 未安裝 playwright（pip install playwright && playwright install chromium）")
        return {"status": True, "data": None, "message": "跳過：未安裝 playwright"}

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Stub)  # 由系統分配端口，不與 .env 的 API_PORT 相沖
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    errors: list[str] = []
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except Exception as exc:  # 未下載瀏覽器
                print(f"SKIP 未安裝 Chromium：{exc}")
                return {"status": True, "data": None, "message": "跳過：未安裝 Chromium"}
            page = browser.new_page()
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(f"{base}/", timeout=30000)
            page.wait_for_timeout(2500)
            chips = page.eval_on_selector_all("#brokers .chip", "els => els.map(e => e.textContent + '|' + e.title)")
            status = page.eval_on_selector("#status", "e => e.textContent")
            at_load = list(Stub.hits)

            page.fill("#key", KEY)
            page.click("#connect")
            page.wait_for_timeout(1500)
            stored = page.evaluate("() => localStorage.getItem('gw_key')")
            Stub.hits.clear()
            page.click("#b-probe")
            page.wait_for_timeout(1500)
            probe_hits = list(Stub.hits)

            page.reload(timeout=30000)
            page.wait_for_timeout(1500)
            refilled = page.eval_on_selector("#key", "e => e.value")

            Stub.hits.clear()
            Stub.raw.clear()
            page.click("nav button[data-tab='accounts']")
            page.wait_for_timeout(1200)
            acc_first = list(Stub.hits)
            has_src_select = page.evaluate("() => !!document.getElementById('a-broker')")
            acc_chips = page.eval_on_selector_all("#a-sources .chip", "els => els.map(e => e.textContent)")
            acc_head = page.eval_on_selector_all("#a-table th", "els => els.map(e => e.textContent)")
            acc_card = page.eval_on_selector("#a-cards .card span", "e => e.textContent")
            acc_msg = page.eval_on_selector("#a-msg", "e => e.className + '|' + e.textContent")
            # 自動更新以秒為單位、預設 0（不更新）：先確認 0 秒時完全沒有定時請求，再設 1 秒確認會定時重取。
            acc_interval = page.eval_on_selector("#a-interval", "e => e.value")
            Stub.hits.clear()
            page.wait_for_timeout(2500)
            acc_zero = list(Stub.hits)
            Stub.hits.clear()
            page.fill("#a-interval", "1")
            page.wait_for_timeout(2500)
            acc_auto = list(Stub.hits)
            Stub.hits.clear()
            page.fill("#a-interval", "0")
            page.wait_for_timeout(2500)
            acc_idle = list(Stub.hits)

            acc_query = [p for p in Stub.raw if p.startswith("/accounts")]

            Stub.hits.clear()
            page.click("nav button[data-tab='codes']")
            page.click("button[data-list='stocks']")
            page.wait_for_timeout(300)  # 存根故意延遲 0.8 秒：此時請求仍進行中，可觀察讀取提示
            busy_msg = page.eval_on_selector("#c-msg", "e => e.className + '|' + e.textContent")
            busy_heads = page.eval_on_selector_all("#c-panels .phead i", "els => els.map(e => e.textContent)")
            page.wait_for_timeout(1500)
            panels = page.eval_on_selector_all(
                "#c-panels .srcp",
                "els => els.map(e => [e.dataset.src, e.querySelector('.phead i').textContent,"
                " e.querySelectorAll('tbody tr').length, [...e.querySelectorAll('th')].map(t => t.textContent)])")
            no_unified = page.query_selector("#c-unified") is None
            raw_hidden = page.eval_on_selector("#c-raw", "e => e.hidden")
            # 「讀取離線 CODES」只讀所選券商存放的那一档，不向券商取數。
            Stub.raw.clear()
            page.click("button[data-list='codes']")
            page.wait_for_timeout(900)
            offline_raw = [p for p in Stub.raw if p.startswith("/codes")]
            offline_panels = len(page.query_selector_all("#c-panels .srcp"))
            offline_head = page.eval_on_selector_all("#c-raw-table th", "els => els.map(e => e.textContent)")
            offline_rows = len(page.query_selector_all("#c-raw-table tbody tr"))
            offline_title = page.eval_on_selector("#c-raw-title", "e => e.textContent")
            offline_info = page.eval_on_selector("#c-raw-info", "e => e.textContent")
            broker_options = page.eval_on_selector_all("#c-broker option", "els => els.map(o => o.value)")
            broker_selected = page.eval_on_selector("#c-broker", "e => e.value")
            interval_default = page.eval_on_selector("#c-interval", "e => e.value")
            live_default = page.eval_on_selector("#c-live", "e => e.checked")

            # 快照年齡與搜尋零結果的提示：兩者都只讀離線快照，不涉及任何券商連線。
            snapshot_line = page.eval_on_selector("#c-snapshot", "e => e.className + '|' + e.textContent")
            page.fill("#c-filter", "zzzz")
            page.wait_for_timeout(300)
            zero_hint = page.eval_on_selector("#c-count", "e => e.textContent")
            page.fill("#c-filter", "")

            # 各券商各存一檔：換券商即改讀該家那一檔，別家的行數不得留在當前券商這一行之上。
            Stub.raw.clear()
            page.select_option("#c-broker", "ib")
            page.wait_for_timeout(1200)
            switch_raw = [p for p in Stub.raw if p.startswith("/codes")]
            ib_line = page.eval_on_selector("#c-snapshot", "e => e.textContent")

            Stub.raw.clear()
            page.click("#c-refresh")
            page.wait_for_timeout(1500)
            refresh_raw = [p for p in Stub.raw if p.startswith("/codes")]
            refresh_msg = page.eval_on_selector("#c-msg", "e => e.textContent")

            # 標的頁的定時更新：預設 0 秒；設 1 秒時只重讀離線快照，勾上「自動向券商重拉」才向券商重取。
            Stub.raw.clear()
            page.fill("#c-interval", "1")
            page.wait_for_timeout(2500)
            auto_codes = [p for p in Stub.raw if p.startswith("/codes") or p.startswith("/all")]
            Stub.raw.clear()
            page.check("#c-live")
            page.wait_for_timeout(2500)
            live_codes = [p for p in Stub.raw if p.startswith("/codes") or p.startswith("/all")]
            Stub.raw.clear()
            page.fill("#c-interval", "0")
            page.wait_for_timeout(2500)
            codes_idle = [p for p in Stub.raw if p.startswith("/codes") or p.startswith("/all")]
            browser.close()
    finally:
        srv.shutdown()

    check("內聯腳本無語法錯誤（函數均已定義）", not errors, "; ".join(errors) or "無 pageerror")
    check("頂欄渲染四家連線指示", len(chips) == 4, f"{len(chips)} 個指示")
    got = " ".join(chips)
    check("可連者顯示延遲毫秒", all(f"{n}{ms}ms" in got for n, ms in (("futu", 178), ("ib", 542), ("tiger", 1216))),
          got)
    down = next((c for c in chips if c.startswith("webull")), "")
    check("斷開者顯示「斷開」且懸停為原因", "斷開" in down and down.endswith("|timeout"), down)
    check("狀態顯示已連接", status == "已連接", status)
    check("載入時即探測一次連線", at_load.count("/brokers") == 1, ",".join(at_load))
    check("金鑰填入後存入 localStorage", stored == KEY, str(stored))
    check("「探測連線」只重發 /brokers", probe_hits == ["/brokers"], ",".join(probe_hits))
    check("重新載入後自動回填金鑰", refilled == KEY, str(refilled))

    check("首次進入戶口頁即取一次戶口", acc_first.count("/accounts") == 1, ",".join(acc_first))
    check("戶口頁沒有「來源」選擇器（一律四家一同顯示）", not has_src_select, f"a-broker={has_src_select}")
    check("戶口請求不含 broker 參數", bool(acc_query) and not any("broker=" in q for q in acc_query),
          ",".join(acc_query[:2]))
    got_acc = " ".join(acc_chips)
    check("戶口頁按來源汇总，無返回者點名", len(acc_chips) == 4 and "futu1" in got_acc
          and "tiger0 · 無返回" in got_acc and "webull0 · 無返回" in got_acc, got_acc)
    check("戶口表第一欄為來源", acc_head[:1] == ["source"], ",".join(acc_head))
    check("卡片照樣顯示券商原樣的戶口性質", "individual" in acc_card, acc_card)
    check("個別券商失敗時以警告色顯示（仍算成功）", "msg warn" in acc_msg, acc_msg)
    check("戶口頁的自動更新以秒為單位，預設 0（不更新）", acc_interval == "0", f"預設 {acc_interval} 秒")
    check("秒數為 0 時不會定時重取（空轉 2.5 秒沒有新請求）", not acc_zero, ",".join(acc_zero))
    check("設為 1 秒後戶口頁會定時重取", acc_auto.count("/accounts") >= 1, ",".join(acc_auto))
    check("改回 0 即停止定時重取", not acc_idle, ",".join(acc_idle))

    heads = {p[0]: p[1] for p in panels}
    counts = {p[0]: p[2] for p in panels}
    check("一次點擊即按來源分四區同時返回", [p[0] for p in panels] == list(CAPS["sources"]),
          ",".join(p[0] for p in panels))
    check("有返回者顯示行數", heads.get("futu") == "2 條" and counts.get("futu") == 2, str(heads))
    check("未聲明該品種者顯示「不提供此清單」", heads.get("ib") == "不提供此清單", str(heads))
    check("聲明咗但冇返回者顯示「無返回」",
          heads.get("tiger") == "無返回" and heads.get("webull") == "無返回", str(heads))
    check("區內不重複 source 欄", all("source" not in p[3] for p in panels),
          ",".join(panels[0][3]) if panels else "")
    check("請求進行時訊息位顯示讀取中", "msg busy" in busy_msg and "讀取" in busy_msg, busy_msg)
    check("請求進行時四區各自顯示讀取中", busy_heads == ["讀取中…"] * len(CAPS["sources"]),
          ",".join(busy_heads))
    check("標的頁冇咗「統一格式輸出」面板", no_unified, "已移除")
    check("即時清單唔另設單一合併表格（只按來源分區）", raw_hidden is True, str(raw_hidden))
    check("離線 CODES 唔分區，以單一表格顯示",
          offline_panels == 0 and offline_head == COLUMNS and offline_rows == len(STOCK_ROWS),
          f"分區={offline_panels} 欄={offline_head[:2]} 行={offline_rows}")
    check("單一表格標示離線 CODES 與所調用的端點",
          offline_title == "離線 CODES" and offline_info.startswith("GET /codes"),
          f"{offline_title} | {offline_info}")
    check("「讀取離線 CODES」只讀所選券商那一檔（含其元資料）",
          offline_raw == ["/codes?broker=futu", "/codes/meta?broker=futu"], ",".join(offline_raw))
    check("券商選擇器由能力聲明填充，預設為閘道的預設券商",
          broker_options == list(CAPS["sources"]) and broker_selected == "futu",
          f"{broker_options} 選中 {broker_selected}")
    check("標的頁的自動更新以秒為單位，預設 0 且不向券商重拉",
          interval_default == "0" and live_default is False, f"{interval_default} 秒／重拉={live_default}")
    # 各券商各一檔：當前券商那一行只能出現該家的行數，否則會誤導成「呢家都有咁多」。
    check("換券商即改讀該家那一檔，快照一行點名該家與該家的行數",
          switch_raw == ["/codes?broker=ib", "/codes/meta?broker=ib"]
          and "ib 的快照 14819" in ib_line and "38569" not in ib_line,
          f"{','.join(switch_raw)} | {ib_line}")
    # 快照過舊不是失敗（已存放的資料仍可用），故以警告色而非錯誤色顯示。
    check("離線 CODES 頁點名券商並顯示快照行數與距今時間，過舊以警告色提示",
          "msg warn" in snapshot_line and "futu 的快照 38569 條" in snapshot_line
          and "1 天前" in snapshot_line, snapshot_line)
    check("搜尋零結果且快照過舊時提示按「更新離線 CODES」",
          "0 / 2 條" in zero_hint and "快照已過舊" in zero_hint, zero_hint)
    check("「更新離線 CODES」只向所選券商重拉（不带市場參數，快照即全量）",
          refresh_raw[:1] == ["/codes/refresh?broker=ib"] and all("markets" not in p for p in refresh_raw),
          ",".join(refresh_raw))
    check("更新完成後原樣顯示結果並重讀該家的快照與表格",
          "已更新 2 條 CODES" in refresh_msg and "/codes/meta?broker=ib" in refresh_raw,
          f"{refresh_msg} | {','.join(refresh_raw)}")
    check("標的頁定時更新預設只重讀離線快照（不打券商）",
          bool(auto_codes) and all(p.startswith("/codes") for p in auto_codes), ",".join(auto_codes))
    check("勾上「自動向券商重拉」後定時更新改為向券商取清單",
          any(p.startswith("/all") for p in live_codes) and not any(p.startswith("/codes") for p in live_codes),
          ",".join(live_codes))
    check("標的頁改回 0 秒即停止定時更新", not codes_idle, ",".join(codes_idle))

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": chips, "message": "失敗：" + "；".join(failed)}
    return {"status": True, "data": chips,
            "message": f"{len(checks)} 項檢查全過：四家指示、金鑰記憶、戶口頁按秒自動更新（0 即不更新）與來源汇总、"
                       "標的來源標示與離線 CODES 表格、按券商各讀各更新一檔、快照年齡顯示均正常"}


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
