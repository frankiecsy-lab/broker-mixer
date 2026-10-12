"""驗收 `brokery_gui`（PySide6 桌面 GUI）：界面只負責顯示，資料一律經 brokery_api 閘道（以存根閘道提供
/accounts、/capabilities、三個清單接口、離線 CODES、/kline 與 /brokers/prefs，另以 QWebSocketServer 提供
/stream 存根；不連任何券商、不佔用 .env 的 API_PORT）。以 offscreen 方式離屏運行，不需顯示器。核對：

* 界面與文字分離：七個 .ui 檔內不含任何文字（<string>），顯示文字一律由 locales/<語言>.json 按鍵取；
  六個分頁（戶口／標的／K 線拉取／K 線串流／K 線串流（多週期）／BROKER 管理）的標題切換語言時全部重貼；
* 多語：繁體中文／简体中文／English 三份語言檔鍵集合一致，切換即時生效且不需重建窗口，界面用到的鍵無缺譯；
* 表格欄位與順序即 ACCOUNT_COLUMNS／COLUMNS（由返回的 columns 決定），取不到的金額顯示破折號、資金欄為
  千分位兩位小數、按來源統計條數；
* 券商選項只由 /capabilities 的能力聲明填充且默認 futu（不提供該品種者標註原因且不可選）、市場選項只由
  返回的 market 填充、轉類型即轉到對應接口並重設為全部市場；
* 標的頁分上下兩表：下表為統一格式（COLUMNS），上表為該券商自帶欄位；兩者以同一接口順序取兩次（第二次帶
  raw=1），上表的原因只寫在自己的標籤，不影響下表與狀態列；
* 標的頁另列一行顯示離線 CODES 快照的行數與距今時間，並點名是哪一家的檔（轉發 /codes/meta?broker=，離線讀回，
  不需券商連線；過舊與上次更新失敗以警告色而非錯誤色提示，因已存放的資料仍可用）；「讀取離線 CODES」只向
  /codes?broker= 送出並填下表（離線快照只有統一格式，故上表清空並說明原因）；「更新離線 CODES」只向
  /codes/refresh?broker= 送出且不带市場參數（快照即全量），完成後重讀該行；換券商即改讀該家的檔；切換語言時
  該行一併重貼，不需重新取數；
* 自動更新以秒數設定（QSpinBox），0 即不更新且為預設：為 0 時等兩秒不會多送任何請求；設為 1 秒後戶口頁會
  定時重取戶口；標的頁預設只重讀離線快照（不打券商），勾上「自動向券商重拉」才定時重取清單；定時器只針對
  當前分頁，且有在途請求時不觸發；
* K 線兩個分頁的預設值為 HK.HSImain／1m／1000（根數上限 1000）；週期與券商選項只由 /capabilities 填充
  （ktypes 原樣照用、被停用者不在選項內），取數只向 /kline 送出代碼／週期／根數，不由界面校验；
* 表格顯示的 K 線欄位即 K_COLUMNS，且按時間反序（最新在最上）：反序只在顯示層，序列本身與接口一樣為 ts 升序；
* 串流只經閘道的 /stream（QWebSocket 對存根）：訂閱即送出與協定相同的 subscribe，收到的 update 必須與已取得的
  序列合併（同 ts 覆蓋、行數不縮返最近幾根），訂閱期間「訂閱」不可再按，按「停止」即結束並解鎖；
* K 線串流分頁在 DF 上方畫圖：渲染視圖惰性建立（進入該頁才建立），起不來即說明原因而不是留一塊空白，下方 DF
  照常；每次取數與串流更新都以同一份序列渲染（只核對 brokery.chart 產生的 DataFrame 與注入呼叫，不核對像素）；
* K 線串流（多週期）分頁一格一週期、下方沒有 DF，根數為一個共用輸入（預設 300）：格子數與每格上方的週期按鈕只由
  該券商聲明的 stream_ktypes 決定（存根給 futu 九個、ib 三個），界面不自行排序、不憑空補週期，換券商即按該家聲明
  重建；一個「開始」先逐格順序取九份歷史，全部返回才開**一條** /stream 送九個訂閱（update 帧帶 ktype，按它路由
  到該格序列合併）；一格取唔到即只喺該格上方顯示原因，其餘各格照常取數與串流；逐格只有週期按鈕：換一格即只重取
  該格，只在舊週期已無人顯示時才退返該週期的串流，兩格揀同一週期時共用同一份推送而不另送訂閱；一個「停止」以裸
  stop 幀收掉全部格子並解鎖；
* 串流按「請求簽名」（券商、週期、代碼、根數、復權、raw）界定，同一券商同一週期可並行多條：多週期頁已佔住某週期
  時，另一頁照樣可訂閱（另開一條連接、不被拒、唔使等），兩邊各自收推送與合併，停其中一條唔影響另一條；協定錯誤
  （ktype_unsupported、broker_disabled、bad_request）原樣呈現且界面不自動重送，由用戶改參數；
* BROKER 管理頁列出全部券商（含 .env 未配置者：開關灰掉並讀原因），套用即向 /brokers/prefs/update 交完整名單，
  完成後以返回的行重畫開關，且各頁的券商下拉框即時不再列被停用者；
* 閘道不可達與金鑰不正確均明確報錯（狀態列為取數失敗、原因原樣顯示）；未設 API_KEY 即拒絕建立客戶端；
* `brokery_gui/run.py` 啟動後窗口會一直存活（頂層窗口無父，啟動腳本若不持有引用即被解構、事件循環 abort）。

以腳本方式直接執行：
    python brokery/acceptance/run_gui.py
"""
import inspect
import json
import os
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")  # 離屏運行，不需顯示器
# 離屏環境下 QtWebEngine 要關掉沙箱與 GPU，否則 K 線串流頁 DF 上方的圖表無法初始化（屬環境，不是代碼）。
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--no-sandbox --disable-gpu")

from PySide6 import QtCore, QtWidgets  # noqa: E402
from PySide6.QtNetwork import QHostAddress  # noqa: E402
from PySide6.QtWebSockets import QWebSocketServer  # noqa: E402

from brokery import chart  # noqa: E402
from brokery.brokers.base import ACCOUNT_COLUMNS, COLUMNS, K_COLUMNS  # noqa: E402
from brokery.core import CODES_META_COLUMNS, PREF_COLUMNS  # noqa: E402
from brokery_gui import app as gui_app  # noqa: E402
from brokery_gui.api import GatewayClient  # noqa: E402
from brokery_gui.app import COLOR_WARN, DesktopGui, cell_text  # noqa: E402
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
# 行必須嚴格對應 COLUMNS：不設到期月欄，券商原生標識只在 raw=1 的原生格式中出現；symbol_type
# 與真實閘道一致為大寫常量。
SYMBOL_ROWS = [
    ["HK.00700", "騰訊控股", "HK", "700", "STOCK", "HKD", "HKEX", "futu"],
    ["US.NVDA", "英偉達", "US", "NVDA", "STOCK", "USD", "NASDAQ", "futu"],
]
# raw=1 時閘道返回該券商自帶欄位：这里以 futu 的 basicinfo 欄位作代表，必須與 COLUMNS 完全不同。
RAW_COLUMNS = ["code", "name", "full_name", "last_trade_time", "lot_size"]
RAW_ROWS = [["00700", "騰訊控股", "騰訊控股股份有限公司", "2026-10-09 16:08:00", "N/A"],
            ["NVDA", "英偉達", "NVIDIA Corporation", "2026-10-09 20:00:00", "1"]]
# 能力聲明：ib 唔提供股票 → 該選項應標註原因且不可選（由適配器聲明，唔喺界面硬寫）。
# 值必須與真實閘道一致：capabilities 序列化自 SymbolBroker.capabilities，即 symbol_type 的大寫常量
# （codes.STOCK/FUTURE/INDEX）。存根若用細寫即掩蓋界面以 kind 直接比對的錯誤。
ADAPTER_CAPS = {"futu": ["STOCK", "FUTURE", "INDEX"], "ib": ["FUTURE", "INDEX"]}
# BROKER 開關：BROKERS 是所有可用券商（含 .env 未配置者），CONFIGURED 模擬 .env 只配置了兩家。
# 未配置者必須以 configured=False 列出（開關灰掉並讀原因），而不是從頁面上消失——被停用者要能重新啟用。
BROKERS = ["futu", "ib", "tiger", "webull"]
CONFIGURED = ["futu", "ib"]
DISABLED: set[str] = set()   # 存根狀態：只記被停用者，與 broker_prefs.json 同一口徑


def effective() -> list[str]:
    """生效的券商 = 已配置 − 已停用：/capabilities 只列生效者，三個下拉框因此自動跟隨開關。"""
    return [name for name in CONFIGURED if name not in DISABLED]


# 能力聲明的週期清單：刻意非排序（day 在前）且給齊九個（與真實閘道一樣為 brokers.KTYPE_ORDER 的九項）。
# 界面若自己排序、自行補週期或把預設改成第一項即會被發現。
KTYPES = ["day", "1m", "week", "5m", "month", "3m", "60m", "15m", "30m"]
# 各券商可串流的週期：真實閘道由適配器聲明（futu 九個、ib 只提供部分、tiger/webull 只有 1m）。多週期頁的格子數
# 與每格上方的週期按鈕只由這份聲明決定，且順序照返回者羅列：界面自己排九格、自己排序或憑空補週期即會被發現。
STREAM_KTYPES = {"futu": list(KTYPES), "ib": ["5m", "1m", "day"]}
# 某週期的 /kline 故意返回失敗：用以核對「取歷史失敗即不建立串流」。
KLINE_FAIL: set[str] = set()


def capabilities() -> dict:
    return {"sources": effective(), "ktypes": list(KTYPES),
            "adapters": {name: {"capabilities": ADAPTER_CAPS[name], "stream_ktypes": STREAM_KTYPES[name]}
                         for name in effective()}}


def prefs_rows() -> list:
    return [[name, name in CONFIGURED and name not in DISABLED, name in CONFIGURED,
             "" if name in CONFIGURED else f"未在 API_SOURCES 中（.env 只啟用了 {', '.join(CONFIGURED)}）"]
            for name in BROKERS]


def prefs_envelope() -> dict:
    return {"status": True, "data": {"columns": list(PREF_COLUMNS), "rows": prefs_rows()},
            "message": f"ok: 生效 {len(effective())} 家（已停用 {', '.join(sorted(DISABLED)) or '無'}）"}


# K 線：ts 為 UTC 秒，行必須嚴格對應 K_COLUMNS（最後一欄 source 供界面按來源統計）。
K_BASE = 1_760_000_000


def kline_rows(start_index: int, count: int, close) -> dict:
    return {"columns": list(K_COLUMNS),
            "rows": [["HK.HSImain", K_BASE + i * 60, "2026-10-09 09:31:00", 100.0, 101.0, 99.0, close(i),
                      10 + i, 1000.0, "futu"] for i in range(start_index, start_index + count)]}


# 分頁標題以 .ui 的根物件名為鍵，故 addTab 的順序改了也不會錯位：這裡按順序核對六項。
TAB_TITLES = {"zh-Hant": ("戶口清單", "標的列表", "K 線拉取", "K 線串流", "K 線串流（多週期）", "BROKER 管理"),
              "zh-Hans": ("户口清单", "标的列表", "K 线拉取", "K 线串流", "K 线串流（多周期）", "BROKER 管理"),
              "en": ("Accounts", "Symbols", "K-line Pull", "K-line Stream", "K-line Stream (Multi-ktype)",
                     "Broker Settings")}
# 離線 CODES 快照的元資料：一行，欄位與順序即 CODES_META_COLUMNS。刻意給一筆超過 24 小時且上次更新失敗
# 的快照（距今 90000 秒 → 界面顯示「1 天前」），要驗的正是「過舊以警告色而非錯誤色提示」。
CODES_META_ROWS = [["futu_codes", 38569, 8, "2026-10-10T10:00:00+00:00", 90000.0, True, "futu",
                   "HK/US 全量 CODES", "futu: OpenD 未連接"]]
CODES_REFRESH = {"status": True, "data": {"columns": list(CODES_META_COLUMNS), "rows": CODES_META_ROWS},
                 "message": "ok: 已更新 38569 條 CODES（FUTURE 14079（+0），INDEX 740（+0），STOCK 23750（+0））"}
# 離線存放的 CODES 就是統一格式的行（欄位契約同 COLUMNS），沒有券商自帶欄位：這正是「讀取離線 CODES」後
# 上表必須清空並說明原因的原因。
CODES_ROWS = SYMBOL_ROWS + [["US.VIX", "VIX 波動率指數", "US", "VIX", "INDEX", "USD", "CBOE", "futu"]]


def codes_meta_rows(broker: str) -> list:
    """某券商那一檔的元資料：行數與上次失敗原因逐家不同（ib 只有期貨與指數，故行數明顯較少且沒有留痕）。
    距今一律 90000 秒（→「1 天前」）並標為過舊，要驗的正是「過舊以警告色而非錯誤色提示」。"""
    return [[f"{broker}_codes", 14819 if broker == "ib" else 38569, 8, "2026-10-10T10:00:00+00:00", 90000.0,
             True, broker, "HK/US 全量 CODES", "futu: OpenD 未連接" if broker == "futu" else ""]]


def query_params(path: str) -> dict[str, str]:
    """查詢串 → 參數：必須用 parse_qs，手動 split 會把 %2C（逗號）留成原樣，核對不到真實名單。"""
    found = parse_qs(path.split("?", 1)[1]) if "?" in path else {}
    return {name: values[0] for name, values in found.items()}


class Stub(BaseHTTPRequestHandler):
    """存根閘道：只提供戶口、能力、三個清單接口、離線 CODES、K 線與券商開關，並記錄收到的金鑰與完整路徑，
    足以核對請求口徑。"""

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
            body, code = {"status": True, "data": capabilities(), "message": "ok"}, 200
        elif path in ("/stocks", "/futures", "/indices"):
            # 同一接口按 raw 參數供兩種格式：界面必須自己各取一次，不能憑統一格式假設渲染上表。
            data = ({"columns": RAW_COLUMNS, "rows": RAW_ROWS} if "raw=1" in self.path
                    else {"columns": COLUMNS, "rows": SYMBOL_ROWS})
            body, code = {"status": True, "data": data, "message": "ok"}, 200
        elif path == "/accounts":
            body, code = {"status": True, "data": {"columns": ACCOUNT_COLUMNS, "rows": ACCOUNT_ROWS},
                          "message": MESSAGE}, 200
        elif path == "/codes":
            body, code = {"status": True, "data": {"columns": COLUMNS, "rows": CODES_ROWS},
                          "message": f"ok: 離線讀回 {len(CODES_ROWS)} 條 CODES"}, 200
        elif path == "/codes/meta":
            # 各券商各一檔：行數與留痕逐家不同，界面若把別家的數字留在當前券商那一行即會被發現。
            broker = dict(p.split("=", 1) for p in (self.path.split("?")[1:] or [""])).get("broker", "")
            body, code = {"status": True, "data": {"columns": list(CODES_META_COLUMNS),
                                                   "rows": codes_meta_rows(broker)}, "message": "ok"}, 200
        elif path == "/codes/refresh":
            body, code = CODES_REFRESH, 200
        elif path == "/kline":
            ktype = query_params(self.path).get("ktype", "")
            if ktype in KLINE_FAIL:   # 該週期取不到：串流頁不得只靠串流撐出序列
                body, code = {"status": False, "data": {"columns": [], "rows": []},
                              "message": f"code_error: 不支援的週期 {ktype}"}, 200
            else:
                body, code = {"status": True, "data": kline_rows(0, 4, lambda i: 100.0 + i),
                              "message": "ok: 4 根（futu）"}, 200
        elif path == "/brokers/prefs":
            body, code = prefs_envelope(), 200
        elif path == "/brokers/prefs/update":
            # 省略 enabled 即全部停用（與真實閘道一致）；名單不可經大寫化處理，未知者一律拒絕。
            given = query_params(self.path)
            names = [n for n in given["enabled"].split(",") if n] if "enabled" in given else []
            unknown = [n for n in names if n not in BROKERS]
            if unknown:
                body, code = {"status": False, "data": {"columns": [], "rows": []},
                              "message": f"unknown_source: {','.join(unknown)}"}, 200
            else:
                DISABLED.clear()
                DISABLED.update(name for name in CONFIGURED if name not in names)
                body, code = prefs_envelope(), 200
        else:
            body, code = {"detail": f"no such path: {self.path}"}, 404
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


class StreamStub:
    """/stream 的存根：按協定回應，並記錄收到的每一幀（用以核對訂閱內容原樣送出）。

    用 QWebSocketServer 而不是另起一個 asyncio 服務：桌面端的客戶端本身就是 QWebSocket，兩邊同一個事件循環，
    不需要線程，也不會出現「存根比界面慢」的假象。
    """

    def __init__(self) -> None:
        self.frames: list[dict] = []
        self.connections = 0   # 被接入的連接數：一個訂閱只准開一條連接
        self.sockets: list = []   # 已接入的連接：多週期一節要能主動向它們推送指定週期的 update
        # 逐連接記低佢自己開住嘅 (券商, 週期)：真實閘道逐連接管 worker，closed 只返畀送 stop 嗰條連接，故兩條
        # 連接同時串流同一週期時，停一條唔會令另一條收到 closed。同一週期可並行多條，故照實登記（唔去重）。
        # 鍵用 id(socket)：連接一律留在 sockets 裏，故 id 在存根存活期間不會被重用。
        self.opened: dict[int, list[tuple[str, str]]] = {}
        # closed 帧的 release_in：真實閘道用它說明自己幾秒後收尾（「停止」只是提前收尾）。界面不再據此倒數，
        # 故默認 0；設成非零只用於證明界面不會因為呢個秒數而唔肯即刻重連。
        self.release_in = 0
        # 一次性嘅協定錯誤：設了即對下一份 subscribe 返回原樣帶住呢句原因的 error 帧（真實閘道點名的
        # ktype_unsupported、broker_disabled 即如此，再無 stream_busy）。存根不自己判定原因，只照協定送一次
        # 該有的帧，用以核對界面的反應：原樣呈現、不自己重送。
        self.reject: str | None = None
        self.observer = None   # 每收到一幀即回呼：用以記低「那一刻」界面的狀態，而不是事後再推
        self.server = QWebSocketServer("stream-stub", QWebSocketServer.NonSecureMode)
        self.server.newConnection.connect(self._accept)
        # 這個 PySide6 沒有 serveNextPort()：端口由系統分配後自己 listen，失敗即說清楚，不靜默退回固定端口。
        if not self.server.listen(QHostAddress("127.0.0.1"), free_port()):
            raise RuntimeError(f"無法為串流存根監聽端口：{self.server.errorString()}")
        self.base = f"http://127.0.0.1:{self.server.serverPort()}"

    def _accept(self) -> None:
        # newConnection 不帶參數：待接入的連接要自己取，並立即接上收訊，否則第一幀即丟失。
        self.connections += 1
        socket = self.server.nextPendingConnection()
        self.sockets.append(socket)
        self.opened[id(socket)] = []
        socket.textMessageReceived.connect(lambda text, s=socket: self._receive(text, s))

    def _receive(self, text: str, socket) -> None:
        try:
            msg = json.loads(text)
        except ValueError:
            socket.sendTextMessage(json.dumps({"event": "error", "message": "bad_request: 不是 JSON"}))
            return
        self.frames.append(msg)
        if self.observer is not None:
            self.observer(msg)
        action = str(msg.get("action", "")).lower()
        if action == "subscribe":
            # closed 幀點名的是訂閱時所用的券商與週期（與真實閘道一致），不是 stop 幀裡的欄位——
            # stop 本來就不帶呢兩個欄位（見 stream.py 的 stop()）。
            broker = str(msg.get("broker") or "")
            ktype = str(msg.get("ktype") or "")
            if self.reject:   # 一次性的協定錯誤：原樣把原因送回，不自己判定（只送一次）
                detail, self.reject = self.reject, None
                socket.sendTextMessage(json.dumps({"event": "error", "broker": broker, "ktype": ktype,
                                                   "message": detail}))
                return
            self.opened.setdefault(id(socket), []).append((broker, ktype))
            socket.sendTextMessage(json.dumps({"event": "subscribed", "broker": broker,
                                              "codes": msg.get("codes"), "ktype": ktype, "seconds": 5}))
            # 與真實閘道一樣，update 是之後按間隔推送的，不是訂閱的一刻即送完：否則「訂閱成功」的訊息在界面
            # 出現的同一輪即被「已更新」蓋掉，驗收便分不開這兩步。
            QtCore.QTimer.singleShot(300, lambda s=socket, k=ktype: self._push(s, k))
        elif action == "stop":
            # 與真實閘道一致：逐個 worker 回覆 closed，帶的是訂閱時所用的券商與週期（stop 幀本身唔帶）。
            # 帶 ktype 即只收呢條連接上該週期的全部串流（多週期頁換一格週期即停該週期），裸 stop 才收全部訂閱。
            broker, ktype = str(msg.get("broker") or ""), str(msg.get("ktype") or "")
            own = self.opened.get(id(socket), [])
            for pair in [p for p in own
                         if (not broker or p[0] == broker) and (not ktype or p[1] == ktype)]:
                own.remove(pair)
                socket.sendTextMessage(json.dumps({"event": "closed", "broker": pair[0], "ktype": pair[1],
                                                  "release_in": self.release_in}))

    def push(self, ktype: str, start: int = 2, count: int = 3, close: float = 9999.0) -> None:
        """主動向仍開住的連接送一份指定週期的 update：多週期頁要分得開「update 按 ktype 只填進顯示該週期的
        格子」、「兩格同週期共用同一份推送」與「已冇格子顯示的週期即被丟掉」，故邊個週期被推、推幾次必須由
        測試自己點名，唔能使靠訂閱之後那兩次自動推送的先後次序。"""
        for socket in self.sockets:
            socket.sendTextMessage(json.dumps({"event": "update", "code": "HK.HSImain", "ktype": ktype,
                                              "data": kline_rows(start, count, lambda i: close)}))

    def _push(self, socket, ktype: str = "") -> None:
        # 每次 update 帶的是該代碼「目前完整」的 bar：第二次只有 3 根且收市價不同。界面必須經 BarStore
        # 合併（同 ts 覆蓋、其餘保留），否則已取的歷史會被縮返最近幾根。
        for start, count, close in ((0, 4, lambda i: 100.0 + i), (2, 3, lambda i: 9999.0)):
            socket.sendTextMessage(json.dumps({"event": "update", "code": "HK.HSImain", "ktype": ktype,
                                              "data": kline_rows(start, count, close)}))


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


def pump_for(qt, seconds: float) -> None:
    """空轉一段短時間（事件循環照常跑）：用來證明 0 秒設定下定時器確實沒有送出請求。"""
    deadline = time.time() + seconds
    while time.time() < deadline:
        qt.processEvents()
        time.sleep(0.05)


def wait_until(qt, predicate, seconds: float = 8.0) -> bool:
    """等某個條件成立（定時器按秒觸發，不能只 processEvents 一次）：有上限，超時即回報，不無限等待。"""
    deadline = time.time() + seconds
    while time.time() < deadline:
        qt.processEvents()
        if predicate():
            return True
        time.sleep(0.05)
    qt.processEvents()
    return bool(predicate())


def stream_after_history(target, ws_base: str, method: str) -> tuple[list[str], object]:
    """把「先取歷史、再開串流」的順序記低，並在歷史已返、未開串流那一刻才把地址指向 WS 存根。

    存根分兩條：HTTP 存根只懂 /kline，WS 存根只懂 /stream；真實閘道兩者同一地址，而桌面端的串流地址正是由
    HTTP 客戶端的 base_url 推出。先換指向即那次 /kline 打到只懂 WebSocket 的存根（取不到歷史即不會訂閱），
    後換即串流連錯端口，故只能在兩者之間換。
    """
    order: list[str] = []
    real = getattr(target, method)
    signature = inspect.signature(real)

    def request(*args, **kwargs):
        order.append("kline")
        # on_done 可以位置傳亦可以關鍵字傳（取數與訂閱兩個入口各一種寫法），先照原方法簽名歸一化再換成我們的
        # 回調，否則會變成同一個參數傳兩次。
        bound = signature.bind(*args, **kwargs)
        chained = bound.arguments.pop("on_done", None)

        def done():
            order.append("stream")
            # 只在那一瞬間指向 WS 存根：串流地址在 StreamClient 建立時即被讀走，之後的 /kline（例如「停止」後
            # 重按「訂閱」）仍要打到 HTTP 存根，否則兩件事分不開。
            http_base, target.client.base_url = target.client.base_url, ws_base
            try:
                if chained is not None:
                    chained()
            finally:
                target.client.base_url = http_base

        real(*bound.args, on_done=done, **bound.kwargs)

    setattr(target, method, request)
    return order, real


def headers(table) -> list[str]:
    return [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]


def cell(table, row: int, column: int) -> str:
    item = table.item(row, column)
    return item.text() if item else ""


def combo_items(combo) -> list[str]:
    return [f"{combo.itemText(i)}|{'可選' if combo.model().item(i).isEnabled() else '不可選'}"
            for i in range(combo.count())]


def combo_values(combo) -> list[str]:
    """下拉框各項的值（不是顯示文字）：週期與券商的選項由接口決定，要核對的是送出的值。"""
    return [str(combo.itemData(i)) for i in range(combo.count())]


def main() -> dict:
    checks: list[tuple[str, bool, str]] = []

    def check(label: str, passed: bool, detail: str = "") -> None:
        checks.append((label, bool(passed), str(detail)))

    ui_dir = Path(__file__).resolve().parents[2] / "brokery_gui" / "ui"
    texts = {p.name: p.read_text(encoding="utf-8") for p in sorted(ui_dir.glob("*.ui"))}
    check("界面與文字分離：六個頁面 .ui 檔齊全且檔內不含任何文字",
          set(texts) == {"accounts_page.ui", "main_window.ui", "symbols_page.ui",
                         "kline_pull_page.ui", "kline_stream_page.ui", "kline_grid_page.ui",
                         "brokers_page.ui"}
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

    # 六頁常設：分頁標題以 .ui 的根物件名為鍵，故按 addTab 的順序逐項核對，順序改了也不會錯位。
    check("六個分頁齊全，標題一律由字庫按鍵取（.ui 內不含文字）",
          gui.window.tabs.count() == 6
          and tuple(gui.window.tabs.tabText(i) for i in range(6)) == TAB_TITLES["zh-Hant"],
          "；".join(gui.window.tabs.tabText(i) for i in range(gui.window.tabs.count())))

    # 預設值在建立時即填好，不等閘道回應：開頁即能直接按「取得」，不需要先讀一次能力聲明。
    kline_pages = (gui.kline_pull, gui.kline_stream)
    check("兩個 K 線頁的標的預設 HK.HSImain、根數預設 1000 且可任選大於 1000 的數字",
          all(p.codeEdit.text() == "HK.HSImain" and p.countSpin.value() == 1000
              and p.countSpin.maximum() >= 100000 for p in kline_pages),
          "；".join(f"{p.codeEdit.text()}={p.countSpin.value()}/{p.countSpin.maximum()}"
                    for p in kline_pages))
    # 週期在建立時即有預設；券商名單由 /capabilities 決定，其預設要讀過能力聲明才成立（見 K 線拉取頁）。
    check("K 線頁的週期下拉框在取數前已有預設 1m（券商則待能力聲明，見下）",
          all(p.ktypeCombo.currentData() == "1m" for p in kline_pages),
          "；".join(str(p.ktypeCombo.currentData()) for p in kline_pages))

    # 多週期頁：逐格只有上方的週期按鈕，故沒有週期下拉框；下方不列 DF，故沒有表格。根數為一個共用輸入。
    grid_page = gui.kline_grid
    check("多週期頁沒有週期下拉框也沒有表格（逐格只有上方的週期按鈕，下方不列 DF）",
          grid_page.findChild(QtWidgets.QComboBox, "ktypeCombo") is None
          and grid_page.findChild(QtWidgets.QTableWidget) is None,
          f"ktypeCombo={grid_page.findChild(QtWidgets.QComboBox, 'ktypeCombo')} "
          f"表格={grid_page.findChild(QtWidgets.QTableWidget)}")
    check("多週期頁的標的預設 HK.HSImain、根數為一個共用輸入且預設 300（可任選大於 1000 的數字）",
          grid_page.codeEdit.text() == "HK.HSImain" and grid_page.gridCountSpin.value() == 300
          and grid_page.gridCountSpin.maximum() >= 100000,
          f"{grid_page.codeEdit.text()}={grid_page.gridCountSpin.value()}/{grid_page.gridCountSpin.maximum()}")

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

    # 自動更新以秒為單位，0 即不更新且為預設：用戶要的是「唔好偷偷打券商」，預設必須是 0。
    check("戶口頁有自動更新秒數設定，最小 0 且預設為 0",
          gui.accounts.autoIntervalSpin.value() == 0 and gui.accounts.autoIntervalSpin.minimum() == 0
          and gui.accounts.autoIntervalLabel.text() == "自動更新（秒）",
          f"{gui.accounts.autoIntervalSpin.value()} 秒／{gui.accounts.autoIntervalLabel.text()}")
    Stub.queries.clear()
    pump_for(qt, 2.0)
    check("秒數為 0 時不會定時重取（空轉兩秒沒有新請求）", not Stub.queries, ",".join(Stub.queries))
    gui.accounts.autoIntervalSpin.setValue(1)
    check("設為 1 秒後戶口頁會定時重取",
          wait_until(qt, lambda: "/accounts" in Stub.queries), ",".join(Stub.queries))
    Stub.queries.clear()
    gui.accounts.autoIntervalSpin.setValue(0)
    pump_for(qt, 2.0)
    check("改回 0 即停止定時重取", not Stub.queries, ",".join(Stub.queries))

    gui.window.tabs.setCurrentIndex(1)
    pump(qt, gui)
    # 快照狀態與清單無關（離線讀回，不需券商連線），進入該頁時兩者同時送出，順序不作要求。
    list_hits = [h for h in Stub.hits if h != "/codes/meta"]
    check("進入標的頁先取能力聲明，再順序取清單兩次（統一＋原始）",
          list_hits[-3:] == ["/capabilities", "/stocks", "/stocks"], ",".join(list_hits[-4:]))
    check("進入標的頁同時讀離線 CODES 快照狀態（不需券商連線）",
          Stub.hits.count("/codes/meta") == 1, ",".join(Stub.hits))
    codes_line = gui.symbols.codesLabel.text()
    check("快照一行顯示行數與距今時間，過舊及上次更新失敗以警告色（非錯誤色）提示",
          "38569" in codes_line and "1 天前" in codes_line and "上次更新失敗" in codes_line
          and "b26a00" in gui.symbols.codesLabel.styleSheet(), codes_line)
    broker_combo = gui.symbols.brokerCombo
    check("券商選項由能力聲明填充，默認 futu，不提供股票者標註原因且不可選",
          broker_combo.currentData() == "futu"
          and combo_items(broker_combo) == ["futu|可選", "ib（不提供股票）|不可選"],
          ",".join(combo_items(broker_combo)))
    check("標的表格欄位即 COLUMNS", headers(gui.symbols.symbolsTable) == COLUMNS,
          ",".join(headers(gui.symbols.symbolsTable)[:3]))
    check("標的頁上下兩表：上表為券商原始欄位、下表仍為 COLUMNS",
          headers(gui.symbols.rawTable) == RAW_COLUMNS and headers(gui.symbols.symbolsTable) == COLUMNS,
          "上=" + ",".join(headers(gui.symbols.rawTable)) + " 下=" + ",".join(headers(gui.symbols.symbolsTable)[:2]))
    check("同一接口順序取兩次：先統一格式，再同參數 raw=1",
          Stub.queries[-2:] == ["/stocks?broker=futu", "/stocks?broker=futu&raw=1"], ",".join(Stub.queries[-2:]))
    check("兩表各有標題，文字由字庫按鍵取",
          gui.symbols.rawLabel.text() == "原始格式（券商自帶欄位）" and gui.symbols.unifiedLabel.text() == "統一格式",
          gui.symbols.rawLabel.text() + " / " + gui.symbols.unifiedLabel.text())
    check("上表按原始欄位填充，缺失值不受下表格式影響",
          cell(gui.symbols.rawTable, 0, 4) == "N/A" and cell(gui.symbols.rawTable, 0, 2) == "騰訊控股股份有限公司",
          cell(gui.symbols.rawTable, 0, 4))
    check("市場選項只由返回的 market 填充",
          [gui.symbols.marketCombo.itemData(i) for i in range(gui.symbols.marketCombo.count())] == ["", "HK", "US"],
          ",".join(gui.symbols.marketCombo.itemData(i) for i in range(gui.symbols.marketCombo.count())))
    Stub.queries.clear()
    gui.symbols.marketCombo.setCurrentIndex(gui.symbols.marketCombo.findData("HK"))
    pump(qt, gui)
    check("選市場後即向該市場重取兩次（統一＋原始）",
          Stub.queries == ["/stocks?broker=futu&markets=HK", "/stocks?broker=futu&markets=HK&raw=1"],
          ",".join(Stub.queries))
    Stub.queries.clear()
    gui.symbols.kindCombo.setCurrentIndex(gui.symbols.kindCombo.findData("index"))
    pump(qt, gui)
    check("轉類型即轉到 /indices，市場重設為全部",
          Stub.queries == ["/indices?broker=futu", "/indices?broker=futu&raw=1"]
          and gui.symbols.marketCombo.currentData() == "", ",".join(Stub.queries))
    check("轉類型後不提供該品種的券商變為可選",
          combo_items(broker_combo) == ["futu|可選", "ib|可選"], ",".join(combo_items(broker_combo)))
    Stub.queries.clear()
    gui.symbols.fetchButton.click()
    pump(qt, gui)
    check("「取得」按鈕會再取一次（統一＋原始）",
          Stub.queries == ["/indices?broker=futu", "/indices?broker=futu&raw=1"], ",".join(Stub.queries))

    # 重拉全量並覆蓋快照：只向 /codes/refresh 送出且不带市場參數（快照即全量，只拉部分市場會被縮細防護
    # 拒絕）；完成後必須重讀快照狀態，失敗原因亦會記進 meta，故成敗都要重讀。
    Stub.queries.clear()
    gui.symbols.codesRefreshButton.click()
    pump(qt, gui)
    check("「更新離線 CODES」只向所選券商的 /codes/refresh 送出（不带市場參數）",
          [q for q in Stub.queries if q.startswith("/codes")] == ["/codes/refresh?broker=futu",
                                                                  "/codes/meta?broker=futu"],
          ",".join(Stub.queries))
    check("更新的結果原樣顯示（含各品種增減），並重讀快照一行",
          "已更新 38569 條 CODES" in gui.symbols.messageLabel.text()
          and "futu 的離線 CODES：38569" in gui.symbols.codesLabel.text()
          and gui.symbols.codesRefreshButton.isEnabled(), gui.symbols.messageLabel.text()[:60])

    # 讀取離線 CODES：只讀該家存放的一檔，不打券商；快照只有統一格式，故上表清空並說明原因。
    Stub.queries.clear()
    gui.symbols.codesLoadButton.click()
    pump(qt, gui)
    check("「讀取離線 CODES」只向 /codes 送出並帶所選券商",
          Stub.queries == ["/codes?broker=futu"], ",".join(Stub.queries))
    check("離線讀回後下表為統一格式的 CODES，上表清空並說明原因",
          headers(gui.symbols.symbolsTable) == COLUMNS
          and gui.symbols.symbolsTable.rowCount() == len(CODES_ROWS) and gui.symbols.rawTable.rowCount() == 0
          and "不含券商自帶的原始欄位" in gui.symbols.rawMessageLabel.text(),
          f"下 {gui.symbols.symbolsTable.rowCount()} 行／上 {gui.symbols.rawTable.rowCount()} 行")
    check("離線讀取明確標明未向券商取數", "離線讀取，未向券商取數" in gui.symbols.messageLabel.text(),
          gui.symbols.messageLabel.text()[:60])

    # 各券商各一檔：換券商即改讀這一檔，不能把別家的行數留在當前券商那一行。
    Stub.queries.clear()
    broker_combo.setCurrentIndex(broker_combo.findData("ib"))
    pump(qt, gui)
    check("換券商即改向該家取清單並改讀該家的快照",
          sorted(Stub.queries) == sorted(["/indices?broker=ib", "/indices?broker=ib&raw=1",
                                          "/codes/meta?broker=ib"]), ",".join(Stub.queries))
    check("快照一行改點名當前券商並顯示該家自己的行數與留痕",
          gui.symbols.codesLabel.text().startswith("ib 的離線 CODES：14819")
          and "38569" not in gui.symbols.codesLabel.text()
          and "上次更新失敗" not in gui.symbols.codesLabel.text(), gui.symbols.codesLabel.text())
    Stub.queries.clear()
    gui.symbols.codesRefreshButton.click()
    pump(qt, gui)
    check("「更新離線 CODES」只重拉當前所選券商那一檔",
          [q for q in Stub.queries if q.startswith("/codes")] == ["/codes/refresh?broker=ib",
                                                                  "/codes/meta?broker=ib"],
          ",".join(Stub.queries))

    # 標的頁的定時更新：預設只重讀離線快照（不打券商），勾開關才向券商重取清單。
    check("標的頁有自動更新秒數設定與「自動向券商重拉」開關，預設 0 秒且不勾",
          gui.symbols.autoIntervalSpin.value() == 0 and not gui.symbols.liveRefreshCheck.isChecked()
          and gui.symbols.autoIntervalLabel.text() == "自動更新（秒）"
          and gui.symbols.liveRefreshCheck.text() == "自動向券商重拉",
          f"{gui.symbols.autoIntervalSpin.value()} 秒／{gui.symbols.liveRefreshCheck.text()}")
    Stub.queries.clear()
    gui.symbols.autoIntervalSpin.setValue(1)
    check("標的頁定時更新預設只重讀離線快照（不打券商）",
          wait_until(qt, lambda: any(q.startswith("/codes?broker=ib") for q in Stub.queries))
          and not any(q.startswith("/indices") for q in Stub.queries), ",".join(Stub.queries))
    Stub.queries.clear()
    gui.symbols.liveRefreshCheck.setChecked(True)
    check("勾上「自動向券商重拉」後定時更新改為向該家重取清單",
          wait_until(qt, lambda: any(q.startswith("/indices?broker=ib") for q in Stub.queries)),
          ",".join(Stub.queries))
    # 重拉是「清單＋原始」兩趟，第二趟在首趟回應後才送出：兩趟都送達才清單，否則會把尾巴誤判為仍在定時更新。
    wait_until(qt, lambda: any(q.endswith("&raw=1") for q in Stub.queries))
    pump(qt, gui)
    Stub.queries.clear()
    gui.symbols.liveRefreshCheck.setChecked(False)
    gui.symbols.autoIntervalSpin.setValue(0)
    pump_for(qt, 2.0)
    check("標的頁改回 0 秒即停止定時更新", not Stub.queries, ",".join(Stub.queries))

    # ------------------------------------------------------------------- K 線拉取
    # 進入 K 線頁只重讀能力聲明（週期與券商的選項由它決定），取數仍由按鈕觸發：開頁即打券商會白付連線成本。
    Stub.queries.clear()
    gui.window.tabs.setCurrentWidget(gui.kline_pull)
    pump(qt, gui)
    check("進入 K 線頁只重讀能力聲明，不自行取數", Stub.queries == ["/capabilities"], ",".join(Stub.queries))
    check("週期選項只由 /capabilities 的 ktypes 填充且順序原樣（不自行排序、不憑空補週期），預設仍為 1m",
          all(combo_values(p.ktypeCombo) == KTYPES and p.ktypeCombo.currentData() == "1m"
              for p in kline_pages),
          "；".join(",".join(combo_values(p.ktypeCombo)) for p in kline_pages))
    check("K 頁的券商下拉框只列生效的券商並預設 futu（未配置者不出現，且不像標的頁那樣按品種過濾）",
          all(combo_values(p.brokerCombo) == ["futu", "ib"] and p.brokerCombo.currentData() == "futu"
              for p in kline_pages),
          "；".join(f"{','.join(combo_values(p.brokerCombo))}->{p.brokerCombo.currentData()}"
                    for p in kline_pages))

    Stub.queries.clear()
    gui.kline_pull.loadButton.click()
    check("按「取得」即按控制列現值向 /kline 送出（參數原樣交閘道判定，界面不另設一套）",
          wait_until(qt, lambda: Stub.queries)
          and Stub.queries[0] == "/kline?code=HK.HSImain&ktype=1m&count=1000&broker=futu" and pump(qt, gui),
          ",".join(Stub.queries))
    table = gui.kline_pull.klineTable
    check("K 線表格欄位即 K_COLUMNS（含 source，供界面按來源統計）",
          headers(table) == K_COLUMNS, ",".join(headers(table)))
    stored = gui.panes["KlinePullPage"].store.payload()
    check("表格按時間反序（最新在最上），存放仍為 ts 升序：反序只屬顯示層，圖表與跨券商對齊不受影響",
          [row[1] for row in stored["rows"]] == [K_BASE + i * 60 for i in range(4)]
          and [cell(table, r, 1) for r in range(4)] == [str(K_BASE + i * 60) for i in range(3, -1, -1)],
          ",".join(cell(table, r, 1) for r in range(table.rowCount())))
    check("按來源統計根數", "共 4 根" in gui.kline_pull.summaryLabel.text()
          and "futu：4 根" in gui.kline_pull.summaryLabel.text(), gui.kline_pull.summaryLabel.text())
    # 根數可任選：大過 1000 的數字原樣送出，序列合併器的上限同步跟隨（否則取 3000 根會被裁返預設的 1000 根）。
    Stub.queries.clear()
    gui.kline_pull.countSpin.setValue(3000)
    gui.kline_pull.loadButton.click()
    check("根數可任選大於 1000 的數字：原樣交閘道，且序列合併器的上限同步跟隨本次請求的根數",
          wait_until(qt, lambda: Stub.queries)
          and Stub.queries[0] == "/kline?code=HK.HSImain&ktype=1m&count=3000&broker=futu" and pump(qt, gui)
          and gui.panes["KlinePullPage"].store.limit == 3000,
          f"{','.join(Stub.queries)}|limit={gui.panes['KlinePullPage'].store.limit}")
    gui.kline_pull.countSpin.setValue(1000)

    # ------------------------------------------------------------------- K 線串流
    stream = StreamStub()
    Stub.queries.clear()
    gui.window.tabs.setCurrentWidget(gui.kline_stream)
    pump(qt, gui)
    check("進入 K 線串流頁只重讀能力聲明、不自行取數，未訂閱時「停止」不可按",
          Stub.queries == ["/capabilities"] and gui.kline_stream.startButton.isEnabled()
          and not gui.kline_stream.stopButton.isEnabled(),
          ",".join(Stub.queries))
    # 圖表惰性建立且每頁各持一個：只有帶圖表區（chartBox）的分頁先會有一張圖，界面本身不再持有圖表實例。
    pane = gui.panes["KlineStreamPage"]
    check("K 圖是可重用元件：有圖表區的分頁各持一個並惰性建立視圖，沒有圖表區的分頁不建立，界面不另持單一實例",
          type(pane.chart).__name__ == "KlineChart" and pane.chart.view is not None
          and gui.panes["KlinePullPage"].chart is None and not hasattr(gui, "_chart"),
          f"chart={type(pane.chart).__name__}"
          f"|view={type(pane.chart.view).__name__ if pane.chart.view else '未建立'}"
          f"|pull={gui.panes['KlinePullPage'].chart}")
    # 記低每次渲染收到嘅序列與初始窗口：要驗嘅係圖表與下方 DF 用同一份序列、且所請求嘅根數全部喺圖上。
    painted: dict = {"frames": [], "ktypes": [], "starts": []}
    if pane.chart.view is not None:
        real_render = pane.chart.view.render

        def record(frame, ktype=None, **kw):
            painted["frames"].append(frame)
            painted["ktypes"].append(ktype)
            painted["starts"].append(kw.get("start"))
            return real_render(frame, ktype=ktype, **kw)

        pane.chart.view.render = record
    order, real_request = stream_after_history(gui, stream.base, "request_kline")
    Stub.queries.clear()
    gui.kline_stream.startButton.click()
    check("按「訂閱」先向 /kline 取歷史，歷史已在圖上才建立串流（不是只靠串流撐出一張只有最近幾十根的圖）",
          wait_until(qt, lambda: stream.frames)
          and Stub.queries == ["/kline?code=HK.HSImain&ktype=1m&count=1000&broker=futu"]
          and order == ["kline", "stream"], f"{','.join(Stub.queries)}|{','.join(order)}")
    check("按「訂閱」即按控制列現值向 /stream 送出訂閱幀（只經閘道，桌面端不直接連券商，且只開一條連接）",
          stream.frames[0] == {"action": "subscribe", "codes": ["HK.HSImain"], "ktype": "1m",
                               "count": 1000, "broker": "futu"} and stream.connections == 1,
          f"{json.dumps(stream.frames[:1])}|{stream.connections} 條")
    check("訂閱成功即說明會自動結束的秒數",
          wait_until(qt, lambda: "已訂閱 futu HK.HSImain 1m" in gui.kline_stream.messageLabel.text())
          and "秒後自動結束" in gui.kline_stream.messageLabel.text(), gui.kline_stream.messageLabel.text())
    check("訂閱期間「訂閱」不可再按（同一頁再起一條連接只會接手同一份請求，界面上會多出一條用戶看不見的連接）",
          not gui.kline_stream.startButton.isEnabled() and gui.kline_stream.stopButton.isEnabled(),
          f"start={gui.kline_stream.startButton.isEnabled()} stop={gui.kline_stream.stopButton.isEnabled()}")
    check("收到的 update 經序列合併：同 ts 覆蓋、其餘保留（已取的歷史不會被縮返最近幾根）",
          wait_until(qt, lambda: pane.store.size == 5), f"{pane.store.size} 根")
    merged = pane.store.payload()
    check("合併後為 ts 升序的完整序列，同 ts 者以新到者為準",
          [row[1] for row in merged["rows"]] == [K_BASE + i * 60 for i in range(5)]
          and [row[6] for row in merged["rows"]][2:] == [9999.0] * 3, json.dumps(merged["rows"][2:]))
    check("串流更新後表格仍按時間反序，最新一根在首行",
          cell(gui.kline_stream.klineTable, 0, 1) == str(K_BASE + 4 * 60)
          and cell(gui.kline_stream.klineTable, 0, 6) == "9999.0",
          cell(gui.kline_stream.klineTable, 0, 1))
    check("更新訊息點名本次與合併後的根數",
          "已更新 HK.HSImain" in gui.kline_stream.messageLabel.text()
          and "本次 3 根" in gui.kline_stream.messageLabel.text()
          and "合併後 5 根" in gui.kline_stream.messageLabel.text(), gui.kline_stream.messageLabel.text())
    # DF 上方的圖：每次取數與每次串流更新都照同一份序列渲染，桌面端不另寫一套圖表、亦不為圖另取一次數。
    # 初始窗口取 0：所請求的根數要全部喺圖上（縮放滑桿照可再收窄），唔可以得返最近幾十根。
    js = chart.render_js(chart.frame(pane.store.payload()), ktype="1m", start=0)
    check("桌面端只交一份 DataFrame 給那份共用的 chart.js（座標軸與 series 全由它決定），並要求顯示全部根數",
          js.startswith('BrokeryChart.render(document.getElementById("chart")')
          and json.dumps(list(K_COLUMNS)) in js and '"ktype": "1m"' in js and '"start": 0' in js, js[:100])
    check("圖與表格同一份序列：渲染的根數與 DF 一致、照控制列的週期顯示時間軸，且初始窗口為全部根數",
          bool(painted["frames"]) and len(painted["frames"][-1]) == pane.store.size
          == gui.kline_stream.klineTable.rowCount() and painted["ktypes"][-1] == "1m"
          and painted["starts"][-1] == 0,
          f"{[len(f) for f in painted['frames']]}|{painted['ktypes']}|{painted['starts']}")
    note = gui.kline_stream.chartNoteLabel.text()
    check("圖表載入成功即清走「正在載入圖表」的提示（提示由載入狀態驅動，不由界面猜）；起不來時以明確原因提示，下方 DF 照常",
          (not pane.chart.error and (note == "" if pane.chart.ready else note.startswith("正在載入")))
          or note.startswith("無圖表："),
          f"error={pane.chart.error}|ready={pane.chart.ready}|{note[:60]}")
    # 圖要佔盡上方空間：窗口未顯示時 Qt 唔會落佈局，故量高度之前先 show（離屏照樣計尺寸）。
    # 呢度只驗圖表區內部（提示列唔該同圖平分高度）；圖表區與 DF 的比例屬 .ui，另在界面可見。
    gui.window.show()
    gui.window.resize(1280, 800)
    wait_until(qt, lambda: gui.kline_stream.chartBox.height() > 0)
    box = gui.kline_stream.chartBox.height()
    view = pane.chart.view._view.height() if pane.chart.view._view is not None else 0
    check("K 線圖佔盡圖表區的高度（提示列不與圖平分空間，上方空間要用滿）",
          box > 0 and view >= int(box * 0.8), f"view={view}/box={box}")
    # 用戶要嘅係「K 圖佔高度一半以上」，故直接以整頁高度為準斷言（比例由 .ui 的 verstretch 3:2 決定）。
    table = gui.kline_stream.klineTable.height()
    page = gui.kline_stream.height()
    check("K 線串流頁：K 圖佔頁面高度的一半以上（圖比下方 DF 大，唔係各佔一半）",
          box > 0 and page > 0 and box > table and box > page * 0.5,
          f"chart={box}/table={table}/page={page}（圖佔頁 {box / page:.0%}）")
    gui.kline_stream.stopButton.click()
    check("按「停止」即送 stop 幀、說明已停止並解鎖按鈕（換參數要重連，故不能留在鎖定狀態）",
          wait_until(qt, lambda: pane.stream is None)
          and "已停止 futu 串流" in gui.kline_stream.messageLabel.text()
          and any(f.get("action") == "stop" for f in stream.frames)
          and gui.kline_stream.startButton.isEnabled() and not gui.kline_stream.stopButton.isEnabled(),
          gui.kline_stream.messageLabel.text())
    # 「停止」之後再按「訂閱」是換了參數的新連接：先取歷史這一步要照樣發生，不能被上一條連接的殘留擋住。
    Stub.queries.clear()
    stream.frames.clear()
    gui.kline_stream.startButton.click()
    check("停止後再按「訂閱」即重新先取歷史、再開新連接（不是按了無反應）",
          wait_until(qt, lambda: stream.frames)
          and Stub.queries == ["/kline?code=HK.HSImain&ktype=1m&count=1000&broker=futu"],
          f"{','.join(Stub.queries)}|{json.dumps(stream.frames[:1])}")
    gui.kline_stream.stopButton.click()
    wait_until(qt, lambda: pane.stream is None)   # 等連接真正收尾，先至做下一個反例
    # 閘道按「請求簽名」（券商、週期、代碼、根數、復權、raw）界定一份串流：同簽名即接手仍在推送嘅那一條，
    # 不同簽名即另起一條，同一券商同一週期可並行多條，再無 stream_busy，界面也沒有名額可等。
    # 呢一節先驗用戶投訴過嘅情況沒有返來——「停止」之後再按「訂閱」即刻重連，唔會因為 closed 帧的收尾秒數而
    # 倒數；再驗真被協定錯誤拒絕時，界面原樣呈現閘道點名的原因，並等用戶改參數，不自動重送訂閱。
    # 呢一節把串流地址固定指向 WS 存根（取歷史照樣打 HTTP 存根）：真實閘道 /kline 與 /stream 同一地址，
    # 本來無此問題，但界面若自己重送訂閱就會繞過 stream_after_history 嗰一次性的地址換指向。
    real_stream_client = gui_app.StreamClient
    gui_app.StreamClient = lambda **kw: real_stream_client(**dict(kw, base_url=stream.base))
    stream.release_in = 4
    Stub.queries.clear()
    stream.frames.clear()
    gui.kline_stream.startButton.click()
    # 要等到訂閱真的送達存根才按「停止」：連接未建立時 stop 幀會被丟掉（見 stream.py 的 stop()），
    # closed 帧亦唔會返，後面嘅「即刻再訂閱」便變咗測試自己造成嘅假失敗。
    wait_until(qt, lambda: any(f.get("action") == "subscribe" for f in stream.frames))
    gui.kline_stream.stopButton.click()
    check("按「停止」後即刻可以再按「訂閱」：closed 帧雖說明閘道尚有幾秒才收尾，同一份請求由它接手，界面唔該倒數",
          wait_until(qt, lambda: pane.stream is None)
          and "秒後自動訂閱" not in gui.kline_stream.messageLabel.text()
          and gui.kline_stream.startButton.isEnabled(),
          gui.kline_stream.messageLabel.text())
    Stub.queries.clear()
    stream.frames.clear()
    gui.kline_stream.startButton.click()
    check("「停止」後再按「訂閱」即刻送訂閱幀、即刻串流：用戶要嘅「訂閱咗就唔好再訂閱，直接串流」由閘道接手，"
          "界面不自己倒數",
          wait_until(qt, lambda: any(f.get("action") == "subscribe" for f in stream.frames))
          and Stub.queries == ["/kline?code=HK.HSImain&ktype=1m&count=1000&broker=futu"]
          and pane.stream is not None,
          f"{','.join(Stub.queries)}|{json.dumps([f.get('action') for f in stream.frames])}")
    # 再無 stream_busy：會話參數由用戶改，界面自己重送只會出現用戶看不見嘅訂閱，故協定錯誤（ktype_unsupported、
    # broker_disabled、bad_request）一律原樣呈現、不重送。呢度照真實協定送一次帶原因的 error 帧（只送一次）。
    # 先收返呢條連接：串流中「訂閱」本来就唔可再按，被拒嘅反例要由一次新訂閱開始。
    gui.kline_stream.stopButton.click()
    wait_until(qt, lambda: pane.stream is None)
    stream.reject = "ktype_unsupported: 不支援的週期 1m"
    Stub.queries.clear()
    stream.frames.clear()
    gui.kline_stream.startButton.click()
    check("被閘道以協定錯誤拒絕即原樣顯示它點名的原因（界面不自造原因、不代用戶改參數，亦唔只寫「串流失敗」了事）",
          wait_until(qt, lambda: "ktype_unsupported: 不支援的週期 1m" in gui.kline_stream.messageLabel.text()),
          gui.kline_stream.messageLabel.text())
    pump_for(qt, 3.0)   # 界面若自己重送訂閱會喺呢段時間內出現，故要空轉一段先至驗到「真係只送咗一次」
    check("協定錯誤不會被界面自動重送：用戶改參數之前重送只會再撞同一個錯誤，故只送一次訂閱",
          [f.get("action") for f in stream.frames] == ["subscribe"],
          json.dumps([f.get("action") for f in stream.frames]))
    # 被拒之後連接仍然開住（閘道只回一帧 error），故要由「停止」收走呢條連接：「訂閱」要即刻可以再按，用戶先改
    # 到參數；原因要留住喺提示上，唔該被一句必然落空嘅收尾訊息蓋走。
    gui.kline_stream.stopButton.click()
    note = gui.kline_stream.messageLabel.text()
    check("被拒之後按「停止」即收走連接並解鎖按鈕，讓用戶改參數重試（原因仍留在提示上）",
          wait_until(qt, lambda: pane.stream is None)
          and [f.get("action") for f in stream.frames] == ["subscribe", "stop"]
          and gui.kline_stream.startButton.isEnabled() and not gui.kline_stream.stopButton.isEnabled()
          and "ktype_unsupported" in note,
          f"{json.dumps([f.get('action') for f in stream.frames])}|{note}")
    stream.release_in = 0
    gui_app.StreamClient = real_stream_client
    # 取歷史失敗：不得只靠串流撐出一張圖——那會得返最近幾十根，卻會被誤認為完整歷史。
    KLINE_FAIL.add("1m")
    pane.store.clear()
    Stub.queries.clear()
    stream.frames.clear()
    gui.kline_stream.startButton.click()
    check("取歷史失敗即不建立串流，並解鎖按鈕讓用戶改參數重試",
          wait_until(qt, lambda: Stub.queries) and pump(qt, gui)
          and not stream.frames and not pane.store.size and pane.stream is None
          and gui.kline_stream.startButton.isEnabled() and not gui.kline_stream.stopButton.isEnabled(),
          json.dumps(stream.frames))
    KLINE_FAIL.clear()
    gui.request_kline = real_request
    stream.server.close()

    # --------------------------------------------------------- K 線串流（多週期）：一格一週期、下方不列 DF
    # 用戶要嘅係「同時串流 3×3 個 K 線圖」：格子數與每格上方的週期按鈕只由該券商聲明的 stream_ktypes 決定
    # （存根給 futu 九個、ib 三個），一個「開始／停止」管全部格子，逐格只有週期切換。下面核對嘅依次係：格子
    # 照聲明排、九份歷史全部回到圖上才開一條 WS、update 按 ktype 只填進該格、換一格只重取該格並只退該週期、
    # 兩格揀同一週期共用同一份推送而不另送訂閱、以及一格失敗只寫喺嗰格上面而不拖住其餘各格。
    grid_stream = StreamStub()
    gui_app.StreamClient = lambda **kw: real_stream_client(**dict(kw, base_url=grid_stream.base))
    grid = gui.grid
    # 記低每次逐格渲染與逐格提示：要驗嘅係「只重畫嗰一格」與「原因寫喺嗰格上面」，事後從界面推不出來。
    painted_grid: dict = {"cells": [], "notes": []}
    real_paint, real_note = grid.chart.set_cell, grid.chart.note_cell

    def paint_cell(index, frame, ktype=None):
        painted_grid["cells"].append((int(index), len(frame), ktype))
        return real_paint(index, frame, ktype)

    def note_cell(index, text):
        painted_grid["notes"].append((int(index), text))
        return real_note(index, text)

    grid.chart.set_cell, grid.chart.note_cell = paint_cell, note_cell
    Stub.queries.clear()
    gui.window.tabs.setCurrentWidget(gui.kline_grid)
    pump(qt, gui)
    check("格子數與每格上方的週期按鈕只由該券商聲明的 stream_ktypes 決定（九格、順序照返回者，界面不自己排、"
          "不憑空補週期），進入該頁只重讀能力聲明而不自行取數",
          Stub.queries == ["/capabilities"] and grid.layout == STREAM_KTYPES["futu"]
          and grid.ktypes == STREAM_KTYPES["futu"] and grid.built_with == STREAM_KTYPES["futu"]
          and len(grid.stores) == 9 and gui.kline_grid.startButton.isEnabled()
          and not gui.kline_grid.stopButton.isEnabled(),
          f"{','.join(Stub.queries)}|{json.dumps(grid.layout)}")
    check("控制列即說明格子數與每格根數（呢頁沒有 DF，用戶要一眼知會取幾多份、每份幾多根）",
          "9 格" in gui.kline_grid.summaryLabel.text() and "每格 300 根" in gui.kline_grid.summaryLabel.text(),
          gui.kline_grid.summaryLabel.text())
    # 先取歷史呢一步喺多週期頁係逐格串起來嘅（同一券商的連線不接受並行請求），故用 observer 喺「第一份訂閱送達
    # 那一刻」記低已送咗幾多份 /kline：呢度要嘅係順序證明，而不是事後再推。
    seen: list[int] = []
    grid_stream.observer = lambda msg: seen.append(sum(1 for q in Stub.queries if q.startswith("/kline")))
    Stub.queries.clear()
    grid_stream.frames.clear()
    painted_grid["cells"].clear()
    gui.kline_grid.startButton.click()
    check("按「開始」即逐格向 /kline 取歷史：九格共用同一個根數，且順序照聲明的週期（界面不自己排）",
          wait_until(qt, lambda: len([q for q in Stub.queries if q.startswith("/kline")]) == 9)
          and [q.split("ktype=")[1].split("&")[0] for q in Stub.queries if q.startswith("/kline")]
          == STREAM_KTYPES["futu"]
          and all("code=HK.HSImain" in q and "count=300" in q and "broker=futu" in q
                  for q in Stub.queries if q.startswith("/kline")), ",".join(Stub.queries))
    check("九份歷史全部回到圖上才建立串流（不是靠串流撐出九張只有最近幾十根的圖），九個週期只經一條 WS",
          wait_until(qt, lambda: len(grid_stream.frames) >= 9) and seen[:1] == [9] and grid_stream.connections == 1,
          f"{seen[:1]}|{grid_stream.connections} 條")
    check("九個訂閱在同一條連接上逐個送出（訂閱幀帶自己嘅週期與共用的根數）：九個週期共用一條連接，連線數唔係九",
          [f.get("ktype") for f in grid_stream.frames if f.get("action") == "subscribe"]
          == STREAM_KTYPES["futu"]
          and all(f.get("codes") == ["HK.HSImain"] and f.get("count") == 300 and f.get("broker") == "futu"
                  for f in grid_stream.frames if f.get("action") == "subscribe"),
          json.dumps(grid_stream.frames[:2]))
    check("收到的 update 按 ktype 路由到該格：九格各自合併（已取的歷史不會被縮返最近幾十根），且只重畫該格",
          wait_until(qt, lambda: all(store.size == 5 for store in grid.stores))
          and {i: n for i, n, _ in painted_grid["cells"]} == {i: 5 for i in range(9)},
          f"{[store.size for store in grid.stores]}|{json.dumps(painted_grid['cells'][:6])}")
    # 九格各自收推送，最後送達的是邊一格不由測試決定，故只核對「訊息點名了九個週期之一」而不是某一個。
    check("更新訊息點名本次與合併後的根數，並說明是哪個週期（九格同屏，唔點名即分不清邊格更新）",
          any(f"已更新 {k}（本次" in gui.kline_grid.messageLabel.text() for k in grid.layout)
          and "本次 3 根" in gui.kline_grid.messageLabel.text()
          and "合併後 5 根" in gui.kline_grid.messageLabel.text(), gui.kline_grid.messageLabel.text())
    # 換一格嘅週期：呢格只重取自己、只退舊週期的串流；新週期已由別格顯示時唔另送訂閱（同一份請求由閘道接手，
    # 推送本來只有一份）。呢度順帶令該格的新週期取唔到歷史，先至分得開「失敗只寫喺嗰格上面」。
    KLINE_FAIL.add("week")
    frames_mark, notes_mark = len(grid_stream.frames), len(painted_grid["notes"])
    Stub.queries.clear()
    painted_grid["cells"].clear()
    grid.chart.view._got_picks([[0, "week"]])   # 載體頁回報：第 0 格撳咗「week」按鈕（takePicks 輪詢取回）
    check("格子上方的週期按鈕經輪詢回到界面即只重取該格（/kline 只送該格的新週期一次），其餘各格不再取數",
          wait_until(qt, lambda: Stub.queries)
          and Stub.queries == ["/kline?code=HK.HSImain&ktype=week&count=300&broker=futu"],
          ",".join(Stub.queries))
    check("換週期只退該週期的串流（stop 幀帶券商與週期），其餘各格的串流不受影響；新週期已由別格顯示即不另送訂閱",
          wait_until(qt, lambda: grid.ktypes[0] == "week")
          and [f for f in grid_stream.frames[frames_mark:] if f.get("action") == "stop"]
          == [{"action": "stop", "broker": "futu", "ktype": "day"}]
          and not [f for f in grid_stream.frames[frames_mark:] if f.get("action") == "subscribe"]
          and grid.stream is not None, json.dumps(grid_stream.frames[frames_mark:]))
    check("該格取歷史失敗即只喺嗰格上方顯示原因，不霸住整頁訊息列，也不拖住其餘各格（八格序列與串流照常）",
          wait_until(qt, lambda: painted_grid["notes"][notes_mark + 1:])
          and any("不支援的週期 week" in text for _, text in painted_grid["notes"][notes_mark:])
          and all(index == 0 for index, _ in painted_grid["notes"][notes_mark:])
          and grid.stores[0].size == 0 and all(grid.stores[i].size == 5 for i in range(1, 9))
          and "不支援的週期" not in gui.kline_grid.messageLabel.text(),
          json.dumps(painted_grid["notes"][notes_mark:]))
    KLINE_FAIL.clear()
    painted_grid["cells"].clear()
    grid_stream.push("5m")   # 只有第 3 格顯示 5m
    check("update 只填進顯示該週期的格子：推 5m 即只有第 3 格被重畫，其餘各格不動",
          wait_until(qt, lambda: painted_grid["cells"])
          and sorted({i for i, _, _ in painted_grid["cells"]}) == [3], json.dumps(painted_grid["cells"]))
    frames_mark = len(grid_stream.frames)
    painted_grid["cells"].clear()
    grid.chart.view._got_picks([[0, "5m"]])   # 第 0 格改擡 5m：已由第 3 格訂閱；week 仍由第 2 格顯示
    check("兩格揀同一週期時共用同一份推送：不另送訂閱，舊週期仍由別格顯示時亦不退它",
          wait_until(qt, lambda: grid.ktypes[0] == "5m" and grid.stores[0].size == 4)
          and not [f for f in grid_stream.frames[frames_mark:] if f.get("action") in ("subscribe", "stop")],
          json.dumps(grid_stream.frames[frames_mark:]))
    grid_stream.push("5m")
    check("同一份推送填進每一格：兩格各自合併與重畫，唔會得返第一格更新",
          wait_until(qt, lambda: grid.stores[0].size == 5 and grid.stores[3].size == 5)
          and sorted({i for i, _, _ in painted_grid["cells"]}) == [0, 3],
          f"{[grid.stores[0].size, grid.stores[3].size]}|{json.dumps(painted_grid['cells'])}")
    painted_grid["cells"].clear()
    grid_stream.push("day")   # 已冇格子顯示 day：呢一帧屬舊格子
    pump_for(qt, 0.6)
    check("已冇格子顯示的週期，其 update 被丟掉（換咗週期的格子不會被舊推送畫返）",
          not painted_grid["cells"] and grid.stores[0].size == 5, json.dumps(painted_grid["cells"]))
    frames_mark = len(grid_stream.frames)
    grid.chart.view._got_picks([[0, "day"]])   # 改返去冇其他格子顯示的週期：要照同一條連接再訂閱
    check("換到冇其他格子顯示的週期即照同一條連接再送訂閱（不另開連接、不重取其他格），連接數仍為一",
          wait_until(qt, lambda: any(f.get("action") == "subscribe" for f in grid_stream.frames[frames_mark:]))
          and [f.get("ktype") for f in grid_stream.frames[frames_mark:] if f.get("action") == "subscribe"]
          == ["day"] and not [f for f in grid_stream.frames[frames_mark:] if f.get("action") == "stop"]
          and grid_stream.connections == 1, json.dumps(grid_stream.frames[frames_mark:]))
    # 用戶要嘅核心：同一券商同一週期可以同時有幾條串流。多週期頁已佔住 futu 的 1m（第 2 格，300 根），呢度照樣
    # 喺「K 線串流」頁訂閱同一券商同一週期（1000 根即另一份請求）：兩邊要各自收推送，停其中一條唔影響另一條。
    gui.window.tabs.setCurrentWidget(gui.kline_stream)
    pump(qt, gui)   # 進入該頁會重讀能力聲明：先排走，先至分得清 /kline
    Stub.queries.clear()
    grid_stream.frames.clear()
    gui.kline_stream.startButton.click()
    check("同一券商同一週期已由多週期頁佔住時，K 線串流頁照樣可訂閱：另開一條連接，不被拒、唔使等",
          wait_until(qt, lambda: any(f.get("action") == "subscribe" for f in grid_stream.frames)
                     and "已訂閱 futu HK.HSImain 1m" in gui.kline_stream.messageLabel.text())
          and Stub.queries == ["/kline?code=HK.HSImain&ktype=1m&count=1000&broker=futu"]
          and grid_stream.connections == 2,
          f"{grid_stream.connections} 條|{','.join(Stub.queries)}|{gui.kline_stream.messageLabel.text()}")
    check("同一週期的兩條串流各自收到推送：兩頁的序列各自合併，唔會得返第一條更新",
          wait_until(qt, lambda: pane.store.size == 5 and grid.stores[1].size == 5) and grid.stream is not None,
          f"{pane.store.size}|{grid.stores[1].size}")
    grid_stream.push("1m", start=5, count=2, close=1234.0)
    check("一份推送填進同一週期的兩條串流：兩邊各自 +2 根（第 2 格與 K 線串流頁都照實更新）",
          wait_until(qt, lambda: grid.stores[1].size == 7 and pane.store.size == 7),
          f"{grid.stores[1].size}|{pane.store.size}")
    gui.kline_stream.stopButton.click()
    check("停其中一條唔影響另一條：K 線串流頁收返自己嗰條連接，多週期頁嗰條照樣開住",
          wait_until(qt, lambda: pane.stream is None) and grid.stream is not None,
          f"stream={pane.stream}|grid={grid.stream}")
    grid_stream.push("1m", start=7, count=2, close=4321.0)
    check("已收返嘅連接不會再被填：只有仍開住嗰條繼續收到推送",
          wait_until(qt, lambda: grid.stores[1].size == 9) and pane.store.size == 7,
          f"{grid.stores[1].size}|{pane.store.size}")
    gui.window.tabs.setCurrentWidget(gui.kline_grid)
    pump(qt, gui)
    frames_mark = len(grid_stream.frames)
    gui.kline_grid.stopButton.click()
    check("一個「停止」收晒全部格子：只送一條裸 stop 幀（逐格只有週期按鈕，沒有逐格停止），並解鎖按鈕",
          wait_until(qt, lambda: grid.stream is None)
          and [f for f in grid_stream.frames[frames_mark:] if f.get("action") == "stop"] == [{"action": "stop"}]
          and "已停止 futu 串流" in gui.kline_grid.messageLabel.text()
          and gui.kline_grid.startButton.isEnabled() and not gui.kline_grid.stopButton.isEnabled(),
          json.dumps(grid_stream.frames[frames_mark:]))
    # 換券商：格子要照新聲明重建（IB 只提供部分週期），唔使用戶自己湊九格再逐格睇錯誤。
    gui.kline_grid.brokerCombo.setCurrentIndex(gui.kline_grid.brokerCombo.findData("ib"))
    gui.window.tabs.setCurrentWidget(gui.accounts)
    pump(qt, gui)
    Stub.queries.clear()
    gui.window.tabs.setCurrentWidget(gui.kline_grid)
    check("換券商即按該券商聲明的 stream_ktypes 重建格子：三格且順序照返回者，界面不憑空補到九格，也不自行取數",
          wait_until(qt, lambda: grid.layout == STREAM_KTYPES["ib"])
          and grid.ktypes == STREAM_KTYPES["ib"] and grid.built_with == STREAM_KTYPES["ib"]
          and len(grid.stores) == 3 and not [q for q in Stub.queries if q.startswith("/kline")],
          f"{json.dumps(grid.layout)}|{','.join(Stub.queries)}")
    check("週期切換的輪詢只在該分頁可見時進行（離開即停止，唔使喺後台空轉）",
          grid.chart.view._poll is not None and grid.chart.view._poll.isActive(),
          f"poll={grid.chart.view._poll}")
    gui.window.tabs.setCurrentWidget(gui.accounts)
    check("離開該分頁即停止輪詢", grid.chart.view._poll is not None and not grid.chart.view._poll.isActive(),
          f"poll={grid.chart.view._poll}")
    pump(qt, gui)   # 進入戶口頁會照例讀能力與戶口：先排走，先至分得清下一節「只讀開關狀態」
    grid.chart.set_cell, grid.chart.note_cell = real_paint, real_note
    grid_stream.server.close()
    gui_app.StreamClient = real_stream_client

    # ----------------------------------------------------------------- BROKER 管理
    Stub.queries.clear()
    gui.window.tabs.setCurrentWidget(gui.brokers)
    pump(qt, gui)
    check("進入 BROKER 管理頁即讀開關狀態", Stub.queries == ["/brokers/prefs"], ",".join(Stub.queries))
    check("開關列出全部可用券商（含未配置者，否則被停用者會從頁面上消失、無法再啟用）",
          sorted(gui._pref_boxes) == ["futu", "ib", "tiger", "webull"], ",".join(sorted(gui._pref_boxes)))
    check("已生效者可勾選，未配置者不可勾選（那不是開關能改的事）",
          gui._pref_boxes["futu"].isChecked() and gui._pref_boxes["ib"].isChecked()
          and not gui._pref_boxes["tiger"].isChecked()
          and not gui._pref_boxes["tiger"].isEnabled() and not gui._pref_boxes["webull"].isEnabled(),
          "；".join(f"{n}={b.isChecked()}/{b.isEnabled()}" for n, b in gui._pref_boxes.items()))
    details = "；".join(label.text() for label in gui.brokers.findChildren(QtWidgets.QLabel))
    check("不可勾選的原因原樣顯示在同一行（由接口給，不是界面自己編）", "API_SOURCES" in details, details[:80])
    check("統計生效的家數", gui.brokers.summaryLabel.text() == "生效 2 家", gui.brokers.summaryLabel.text())

    Stub.queries.clear()
    gui._pref_boxes["ib"].setChecked(False)
    gui.brokers.applyButton.click()
    check("「應用」一次交齊完整生效名單（不是只交改動的那一個開關）",
          wait_until(qt, lambda: Stub.queries) and Stub.queries[0] == "/brokers/prefs/update?enabled=futu"
          and pump(qt, gui), ",".join(Stub.queries))
    check("寫入成功的回應即最新狀態：開關即時重畫，不需再讀一次",
          not gui._pref_boxes["ib"].isChecked() and gui._pref_boxes["ib"].isEnabled()
          and gui.brokers.summaryLabel.text() == "生效 1 家", gui.brokers.summaryLabel.text())
    check("開關一改即重讀能力聲明：被停用者即時從各頁（含多週期頁）的券商下拉框消失",
          all(combo_values(p.brokerCombo) == ["futu"] for p in kline_pages)
          and combo_values(gui.kline_grid.brokerCombo) == ["futu"]
          and combo_items(gui.symbols.brokerCombo) == ["futu|可選"],
          "；".join(",".join(combo_values(p.brokerCombo)) for p in (*kline_pages, gui.kline_grid)))

    for language, titles, kind0 in (("zh-Hans", TAB_TITLES["zh-Hans"], "股票"),
                                   ("en", TAB_TITLES["en"], "Stocks")):
        gui.set_language(language)
        qt.processEvents()
        check(f"切換語言即時生效（{language}）：六個分頁標題全部重貼且不需重建窗口",
              tuple(gui.window.tabs.tabText(i) for i in range(len(titles))) == titles
              and gui.symbols.kindCombo.itemText(0) == kind0
              and gui.kline_pull.codeLabel.text() == {
                  "zh-Hans": "代码", "en": "Code"}[language]
              and gui.kline_grid.gridCountLabel.text() == {
                  "zh-Hans": "根数（每格）", "en": "Bars (per cell)"}[language]
              and id(gui.window) == window_id,
              "；".join(gui.window.tabs.tabText(i) for i in range(gui.window.tabs.count())))
    check("切換語言後快照一行一併重貼（重貼標籤即重繪快照狀態，不需重新取數）",
          gui.symbols.codesLabel.text().startswith("ib offline CODES"), gui.symbols.codesLabel.text())
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

    # 啟動腳本必須自己持有窗口引用：頂層窗口無父，引用一沒即被解構，事件循環隨即 abort（0xC0000005）。
    root = Path(__file__).resolve().parents[2]
    proc = subprocess.Popen([sys.executable, str(root / "brokery_gui" / "run.py")], cwd=str(root),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time.sleep(8)
    alive = proc.poll() is None
    if alive:
        proc.terminate()
    out = proc.communicate(timeout=20)[0] or ""
    check("啟動腳本會保住窗口（不持有引用即窗口被解構、事件循環 abort）", alive, out.strip()[:120])

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）", flush=True)
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": None, "message": "失敗：" + "；".join(failed)}
    return {"status": True, "data": None,
            "message": f"{len(checks)} 項檢查全過：六頁 .ui 不含文字、三種語言鍵集合一致且六頁標題即時切換、"
                       "表格欄位即欄位契約、缺失值破折號、券商選項由能力聲明填充、市場選項只由返回值填充、"
                       "離線 CODES 按券商各一檔（讀取／更新兩個按鈕均只針對當前券商）、自動更新秒數預設 0 且 0 即不更新、"
                       "兩個 K 線頁預設 HK.HSImain/1000 且取數只由按鈕觸發、DF 按時間反序而存放仍為升序、"
                       "串流經 /stream 且 update 按 (code,ts) 合併不縮返、取歷史失敗即不建立串流、"
                       "K 線串流頁 DF 上方的圖惰性建立、起不來即說明原因，且與表格同一份序列"
                       "（只交一份 DataFrame 給共用的 chart.js）、"
                       "多週期頁的格子只由券商聲明的 stream_ktypes 決定（九格一條 WS、update 按 ktype 只填該格、"
                       "換一格只重取該格並只退該週期的串流、兩格同週期共用同一份推送、一格失敗只寫喺嗰格上面）、"
                       "同一券商同一週期可並行多條（另一頁照樣訂閱、各自收推送、停一條唔影響另一條）、"
                       "協定錯誤原樣呈現且不被界面自動重送、"
                       "BROKER 開關寫入後各頁下拉框即時跟隨、閘道不可達與金鑰不正確均明確報錯"}


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
