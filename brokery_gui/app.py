"""桌面 GUI：只負責載入 .ui 與接駁閘道，取數一律經 brokery_api。

界面與文字分離：.ui 檔內不寫任何文字，顯示文字一律由 i18n 按鍵取，故切換語言只重貼標籤，不需重建窗口。
表格欄位直接取自返回的 columns（即 core 的欄位契約），這裡不另定義欄位順序，也不重新解讀或湊數。
取數在背景執行緒進行：IB 連線可達 40s，界面若同步等待即凍結。
標的頁分上下兩表：上表為該券商自帶的欄位與格式（同參數再取一次 raw=1），下表為統一格式。兩次取數必須順序，
同一券商的連線（IB 一條 socket、futu 一個 OpenD context）不接受並行請求。
自動更新以秒為單位，0 即不更新（預設 0）：定時器只在當前分頁、且沒有任何在途請求時觸發，否則慢的券商請求會
層層疊加，把同一條連線堵死。
K 線兩個單週期分頁的序列一律經 brokery.chart.BarStore 合併（與 static/chart.js 同一口徑），表格列全部行並把合併
後的序列反序顯示；串流只經閘道的 /stream（.stream.StreamClient）。有圖表區的分頁在表格上方畫圖：圖表只渲染那份
共用的 chart.js（.chart_view.KlineChart，每頁各持一個，惰性建立，起不來即說明原因而不是留一塊空白），與表格同一份序列。
多週期分頁一格一週期、下方無表格：一格一份 BarStore，九格共用一條 /stream（update 帧按 ktype 分派），格子數與
每格的週期按鈕只由該券商聲明的 stream_ktypes 決定（.grid_view.GridChart）。
"""
from __future__ import annotations

import math
import time
from pathlib import Path

from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader

from brokery import chart
from brokery.chart import BarStore

from .api import GatewayClient
from .chart_view import KlineChart
from .grid_view import GridChart
from .i18n import DEFAULT_LANGUAGE, LANGUAGES, Translator
from .stream import StreamClient

UI_DIR = Path(__file__).with_name("ui")
# 「類型」選項 → 閘道的清單接口。只有這三項，其餘一律 unknown_kind，不猜用戶想要什麼。
SYMBOL_PATHS = {"stock": "/stocks", "future": "/futures", "index": "/indices"}
KINDS = tuple(SYMBOL_PATHS)
# 能力聲明以 symbol_type 的大寫常量表達（見 brokers/codes.py），與界面用的 kind 值大小寫不同，
# 故必須顯式對應；以 kind 直接比對 capabilities 會永遠不成立，所有券商都被視為不可選。
KIND_CAPABILITIES = {"stock": "STOCK", "future": "FUTURE", "index": "INDEX"}
DEFAULT_BROKER = "futu"
# K 線頁的預設值：恒指主力期貨四家都有，開窗即有一頁可用；週期與根數只是初始值，
# 可不支持由接口判定（ktype_unsupported、count 上限），界面不自訂第二套規則。
DEFAULT_CODE = "HK.HSImain"
DEFAULT_KTYPE = "1m"
DEFAULT_COUNT = 1000
# 分頁標題以 .ui 的根物件名為鍵：addTab 的順序改了也不會錯位，索引不可當作鍵。
PAGE_TITLES = {"AccountsPage": "tab.accounts", "SymbolsPage": "tab.symbols",
               "KlinePullPage": "tab.kline_pull", "KlineStreamPage": "tab.kline_stream",
               "KlineGridPage": "tab.kline_grid", "BrokersPage": "tab.brokers"}
PAGE_UI_FILES = ("accounts_page.ui", "symbols_page.ui", "kline_pull_page.ui", "kline_stream_page.ui",
                 "kline_grid_page.ui", "brokers_page.ui")
# 這三頁取 K 線：前兩頁有 ktypeCombo 與 klineTable（一個週期一份序列），串流頁另有 chartBox，故該分頁各持
# 一張圖（由 KlinePane 建立，見 chart_view.KlineChart）。多週期頁一格一週期、下方無表格，狀態逐格而非逐頁
# （見 GridPane 與 grid_view.GridChart）。
KLINE_PAGES = ("KlinePullPage", "KlineStreamPage")
GRID_PAGE_NAME = "KlineGridPage"
# 多週期頁的根數預設：九格 × 1000 根會令上游逐格分頁，首次開始明顯慢；300 根九格仍可在數秒內完成。
GRID_DEFAULT_COUNT = 300
DASH = "—"
# 資金欄位按數值顯示（千分位與兩位小數）；其餘欄位一律按原樣文字顯示。
MONEY_COLUMNS = frozenset({"net_liquidation", "cash", "market_value", "available_funds", "buying_power",
                           "init_margin", "maint_margin", "equity_with_loan", "unrealized_pnl", "realized_pnl"})
COLOR_WARN = "color:#b26a00"
COLOR_ERROR = "color:#c0392b"


def load_ui(name: str) -> QtWidgets.QWidget:
    """載入一個 .ui 界面檔：失敗即點名檔案與原因，不返回半個界面。"""
    path = UI_DIR / name
    loader = QUiLoader()
    widget = loader.load(str(path))
    if widget is None:
        raise RuntimeError(f"ui_load_failed: {path.name}（{loader.errorString()}）")
    return widget


def cell_text(value, column: str) -> str:
    """單格顯示：缺失值一律破折號，不以任何數字湊出。"""
    if value is None:
        return DASH
    if column in MONEY_COLUMNS:
        try:
            return f"{float(value):,.2f}"
        except (TypeError, ValueError):
            return str(value)
    return str(value)


def fill_table(table: QtWidgets.QTableWidget, data: dict) -> None:
    """按返回的 columns/rows 填充表格：欄位順序即欄位契約，空表也只留表頭。"""
    columns = list(data.get("columns") or [])
    rows = data.get("rows") or []
    table.clear()
    table.setColumnCount(len(columns))
    table.setRowCount(len(rows))
    table.setHorizontalHeaderLabels(columns)
    for r, row in enumerate(rows):
        for c, value in enumerate(row[:len(columns)]):
            table.setItem(r, c, QtWidgets.QTableWidgetItem(cell_text(value, columns[c])))


def count_by_source(data: dict) -> list[tuple[str, int]]:
    """按來源統計條數：只由返回的行統計，沒返回的來源不會出現，避免憑空列出一間「0 條」。"""
    columns = list(data.get("columns") or [])
    if "source" not in columns:
        return []
    index = columns.index("source")
    counts: dict[str, int] = {}
    for row in data.get("rows") or []:
        if index < len(row):
            counts[str(row[index])] = counts.get(str(row[index]), 0) + 1
    return list(counts.items())


def clear_layout(layout: QtWidgets.QLayout) -> None:
    """清走一個佈局內的所有控件：開關列表每次按接口返回的行重建，不留上一次的控件。"""
    while layout.count():
        item = layout.takeAt(0)
        if item.widget() is not None:
            item.widget().deleteLater()
        elif item.layout() is not None:
            clear_layout(item.layout())


def row_lookup(data: dict) -> dict[str, int]:
    """欄位名 → 位置：讀返回的行一律按名字取值，不靠順序猜（與 fill_table 同一前提）。"""
    return {str(name): index for index, name in enumerate(data.get("columns") or [])}


class GatewayWorker(QtCore.QObject):
    """在背景執行一次閘道請求，完成後把信封交還主執行緒。"""

    finished = QtCore.Signal(dict)

    def __init__(self, client: GatewayClient, path: str, params: dict | None) -> None:
        super().__init__()
        self.client, self.path, self.params = client, path, params

    def run(self) -> None:
        self.finished.emit(self.client.get(self.path, self.params))


class ReplyRelay(QtCore.QObject):
    """把背景執行緒返回的信封交還主執行緒：更新控件（尤其是 QWebEngine）只容許在主執行緒進行。

    信號若直接 connect 一般函數，該函數會在發送者所屬的執行緒執行；這裡每次請求配一個屬主執行緒的
    接收物件，Qt 便會把呼叫排隊交回主執行緒。少了這一層，表格與標籤看似更新正常，實則一直跨執行緒，
    直到圖表頁调用 runJavaScript 才以進程中止暴露出來。
    """

    def __init__(self, on_done, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self.on_done = on_done

    @QtCore.Slot(dict)
    def deliver(self, envelope: dict) -> None:
        self.on_done(envelope)


class KlinePane:
    """一個 K 線分頁的狀態：合併器、該序列所屬的 (code, ktype)、該頁的串流連接。

    兩個分頁的取數與合併口徑相同，故只有一份；分別只在有無串流按鈕與有無圖表，那由該頁的 .ui 決定：
    有圖表區（chartBox）即各持一個 KlineChart，沒有即為 None。
    """

    def __init__(self, page: QtWidgets.QWidget, tr) -> None:
        self.page = page
        self.store = BarStore(DEFAULT_COUNT)
        self.chart = KlineChart(page.chartBox, page.chartNoteLabel, tr) if hasattr(page, "chartBox") else None
        self.key: tuple[str, str] = ()
        self.stream: StreamClient | None = None
        self.wants_stream = False        # 已按「訂閱實時」但歷史未返：期間按「停止」即取消這次訂閱

    def select(self, code: str, ktype: str, count: int) -> None:
        """換標的或週期即丟掉舊序列：不同週期的 bar 混進同一條序列，畫出來就是一條錯的圖。

        合併器的上限跟隨本次請求的根數：否則取 3000 根會被裁返預設的 1000 根，根數可任選即失去意義。
        """
        self.store.set_limit(count)
        if (code, ktype) != self.key:
            self.store.clear()
            self.key = (code, ktype)


class GridPane:
    """多週期分頁的狀態：一格一週期一份序列，全部格子共用一條串流連接。

    KlinePane 假設一頁只有一個週期下拉框、一份序列；多週期頁逐格有週期按鈕、逐格各自一份序列，所以狀態
    必須逐格。layout 記的是排格子所照的週期清單（即該券商聲明的 stream_ktypes），ktypes 記的是各格現在顯示
    的週期（用戶換咗某一格即只改其中一格），後者是 update 帧的路由表。
    """

    def __init__(self, page: QtWidgets.QWidget, tr) -> None:
        self.page = page
        self.chart = GridChart(page.gridBox, page.gridNoteLabel, tr)
        self.layout: list[str] = []
        self.ktypes: list[str] = []
        self.keys: list[tuple[str, str]] = []
        self.stores: list[BarStore] = []
        self.built_with: list[str] = []      # 已排入載體頁的格子：相同即唔使重建（重建會清走各格序列）
        self.stream: StreamClient | None = None
        self.wants = False                   # 已按「開始」：取歷史期間按「停止」即一併取消


class DesktopGui:
    """主窗口：把 .ui、字庫與閘道客戶端接在一起。"""

    def __init__(self, client: GatewayClient | None = None, language: str = DEFAULT_LANGUAGE) -> None:
        self.client = client or GatewayClient()
        self.tr = Translator(language)
        self.window = load_ui("main_window.ui")
        self.pages = [load_ui(name) for name in PAGE_UI_FILES]
        (self.accounts, self.symbols, self.kline_pull, self.kline_stream, self.kline_grid,
         self.brokers) = self.pages
        for page in self.pages:
            self.window.tabs.addTab(page, "")
        self._jobs: set = set()
        self._symbols_seq = 0
        self._inflight = 0                    # 在途請求數：自動更新只在全無在途請求時才觸發
        self._last_auto = {page.objectName(): 0.0 for page in self.pages}  # 各分頁上次自動更新的時刻（秒）
        # 每個 K 線分頁一份狀態；該頁有圖表區才有一張圖（見 KlinePane），界面不再持有共用的圖表實例
        self.panes = {page.objectName(): KlinePane(page, self.tr.t) for page in self.pages
                      if page.objectName() in KLINE_PAGES}
        self.grid = GridPane(self.kline_grid, self.tr.t)
        self._pref_boxes: dict[str, QtWidgets.QCheckBox] = {}
        self.broker_caps: dict[str, list[str]] = {}
        self.ktypes: list[str] = [DEFAULT_KTYPE]  # 週期選項由 /capabilities 的 ktypes 決定，這裡只留初始值
        # 多週期頁的格子與每格的週期按鈕只由該券商聲明的 stream_ktypes 決定：不支持的週期唔會出現，
        # 亦唔會憑空排九格再逐格報錯（能力不支持由適配器聲明，見 brokers/base.stream_ktypes）。
        self.stream_ktypes: dict[str, list[str]] = {}
        self.seen_markets: set[str] = set()
        self.codes_snapshot: dict | None = None   # 離線 CODES 快照的元資料行；未讀到即為 None
        self.codes_snapshot_source = ""           # 該快照所屬的券商：各券商各存一檔，狀態必須點名是哪一档
        self._fill_combos()
        self._retranslate()
        self._connect()
        self.set_status(self.tr.t("status.idle"), "")

    def show(self) -> None:
        self.window.show()

    # ---------------------------------------------------------------- 語言
    def _fill_combos(self) -> None:
        """選項的「值」在此寫死（語言碼、品種、券商由接口決定），文字一律由字庫填。"""
        combo = self.window.languageCombo
        for code, display in LANGUAGES.items():
            combo.addItem(display, code)
        combo.setCurrentIndex(combo.findData(self.tr.language))
        for kind in KINDS:
            self.symbols.kindCombo.addItem("", kind)
        for pane in self.panes.values():
            pane.page.codeEdit.setText(DEFAULT_CODE)
            pane.page.countSpin.setValue(DEFAULT_COUNT)
        self.kline_grid.codeEdit.setText(DEFAULT_CODE)
        self.kline_grid.gridCountSpin.setValue(GRID_DEFAULT_COUNT)
        self.render_ktypes()

    def set_language(self, language: str) -> None:
        """切換語言：換字庫後重貼所有標籤與選項文字，不需重建窗口，也不重新取數。"""
        self.tr.set_language(language)
        self._retranslate()
        self.render_brokers()
        self.render_ktypes()
        self.render_markets()

    def _retranslate(self) -> None:
        t = self.tr.t
        self.window.setWindowTitle(t("app.title"))
        self.window.languageLabel.setText(t("bar.language"))
        for index in range(self.window.tabs.count()):
            key = PAGE_TITLES.get(self.window.tabs.widget(index).objectName(), "")
            if key:
                self.window.tabs.setTabText(index, t(key))
        self.accounts.refreshButton.setText(t("accounts.refresh"))
        self.accounts.autoIntervalLabel.setText(t("accounts.auto_interval"))
        for label, key in ((self.symbols.kindLabel, "symbols.kind"), (self.symbols.marketLabel, "symbols.market"),
                           (self.symbols.brokerLabel, "symbols.broker")):
            label.setText(t(key))
        self.symbols.rawLabel.setText(t("symbols.raw_title"))
        self.symbols.unifiedLabel.setText(t("symbols.unified_title"))
        self.symbols.fetchButton.setText(t("symbols.fetch"))
        self.symbols.autoIntervalLabel.setText(t("symbols.auto_interval"))
        self.symbols.liveRefreshCheck.setText(t("symbols.live_refresh"))
        self.symbols.codesLoadButton.setText(t("symbols.codes_load"))
        self.symbols.codesRefreshButton.setText(t("symbols.codes_refresh"))
        for page in (self.kline_pull, self.kline_stream):
            for label, key in ((page.codeLabel, "kline.code"), (page.ktypeLabel, "kline.ktype"),
                               (page.countLabel, "kline.count"), (page.brokerLabel, "kline.broker")):
                label.setText(t(key))
        self.kline_pull.loadButton.setText(t("kline.fetch"))
        self.kline_stream.startButton.setText(t("kline.subscribe"))
        self.kline_stream.stopButton.setText(t("kline.stop"))
        # 多週期頁沒有週期下拉框：格子與每格的按鈕由 JS 按 ktype 代號排（語言中性），所以換語言唔使重建格子
        for label, key in ((self.kline_grid.codeLabel, "kline.code"),
                           (self.kline_grid.gridCountLabel, "kline.grid_count"),
                           (self.kline_grid.brokerLabel, "kline.broker")):
            label.setText(t(key))
        self.kline_grid.startButton.setText(t("kline.grid_start"))
        self.kline_grid.stopButton.setText(t("kline.stop"))
        self.paint_grid_summary(self.grid)
        self.brokers.applyButton.setText(t("brokers.apply"))
        self.brokers.reloadButton.setText(t("brokers.reload"))
        self.brokers.noteLabel.setText(t("brokers.note"))
        for pane in self.panes.values():   # 圖表的提示（載入中／起不來的原因）要留在原處，換語言即照原樣重貼
            if pane.chart is not None:
                pane.chart.note()
        self.grid.chart.note()
        self.render_codes_state()
        combo = self.symbols.kindCombo
        for i in range(combo.count()):
            combo.setItemText(i, t(f"kind.{combo.itemData(i)}"))

    # ---------------------------------------------------------------- 接駁
    def _connect(self) -> None:
        self.window.languageCombo.currentIndexChanged.connect(self._on_language)
        self.accounts.refreshButton.clicked.connect(self.request_accounts)
        self.accounts.autoIntervalSpin.valueChanged.connect(lambda _value: self._reset_auto(self.accounts))
        self.window.tabs.currentChanged.connect(self._on_tab)
        self.symbols.fetchButton.clicked.connect(self.request_symbols)
        self.symbols.kindCombo.currentIndexChanged.connect(self._on_kind)
        self.symbols.marketCombo.currentIndexChanged.connect(self.request_symbols)
        self.symbols.brokerCombo.currentIndexChanged.connect(self._on_broker)
        self.symbols.codesLoadButton.clicked.connect(self.request_codes_load)
        self.symbols.codesRefreshButton.clicked.connect(self.request_codes_refresh)
        self.symbols.autoIntervalSpin.valueChanged.connect(lambda _value: self._reset_auto(self.symbols))
        self.kline_pull.loadButton.clicked.connect(
            lambda _=False: self.request_kline(self.panes["KlinePullPage"]))
        pane = self.panes["KlineStreamPage"]
        pane.page.startButton.clicked.connect(lambda _=False, p=pane: self.start_stream(p))
        pane.page.stopButton.clicked.connect(lambda _=False, p=pane: self.stop_stream(p))
        self.set_stream_buttons(pane.page, False)   # 未訂閱即只有「訂閱」可用
        # 一個「開始／停止」管全部格子：逐格只有週期按鈕（換格子週期由載體頁上報，見 _on_tab 的輪詢）。
        self.kline_grid.startButton.clicked.connect(lambda _=False: self.start_grid(self.grid))
        self.kline_grid.stopButton.clicked.connect(lambda _=False: self.stop_grid(self.grid))
        self.set_stream_buttons(self.kline_grid, False)
        self.kline_grid.brokerCombo.currentIndexChanged.connect(lambda _=False: self.render_grid())
        self.kline_grid.gridCountSpin.valueChanged.connect(lambda _value: self.paint_grid_summary(self.grid))
        self.brokers.applyButton.clicked.connect(self.apply_prefs)
        self.brokers.reloadButton.clicked.connect(self.request_prefs)
        # 一跳一秒，由 _tick 判斷該分頁是否已到間隔：如此 0 即真的沒有定時器，各分頁亦互不影響。
        self._ticker = QtCore.QTimer(self.window)
        self._ticker.timeout.connect(self._tick)
        self._ticker.start(1000)
        self._on_tab(self.window.tabs.currentIndex())

    def _on_language(self, index: int) -> None:
        self.set_language(self.window.languageCombo.itemData(index))

    def _on_tab(self, index: int) -> None:
        page = self.window.tabs.widget(index)
        self._reset_auto(page)
        name = page.objectName()
        if name != GRID_PAGE_NAME:
            self.grid.chart.stop_picks()   # 唔喺多週期頁即唔使喺後台空轉問頁面有冇撳咗週期按鈕
        if name == "AccountsPage":
            self.request_accounts()
        elif name == "SymbolsPage":
            self.request_capabilities()
            # 快照狀態與清單無關（離線讀回，不需券商連線），故同時取，不等清單完成才顯示。
            self.request_codes_meta()
        elif name == GRID_PAGE_NAME:
            # 格子數與每格的週期按鈕由該券商聲明的 stream_ktypes 決定，故進頁先重讀能力；取數仍由「開始」觸發。
            self.grid.chart.ensure()
            self.grid.chart.watch_picks(lambda cell, ktype: self.pick_grid_cell(self.grid, cell, ktype))
            self.request_capabilities()
        elif name in KLINE_PAGES:
            # 週期與券商的選項一律由能力聲明決定（被停用者不在選項內），故進頁先重讀能力；取數仍由按鈕觸發。
            pane = self.panes.get(name)
            if pane is not None and pane.chart is not None:   # 有圖表區即先載入視圖，取數完成時無需再等載入
                pane.chart.ensure()
            self.request_capabilities()
        elif name == "BrokersPage":
            self.request_prefs()

    def _on_broker(self, _index: int) -> None:
        """換券商即重取清單與該家的快照：各券商各一檔，留著上一家的快照會令人以為那是當前券商的資料。"""
        self.request_symbols()
        self.request_codes_meta()

    def _reset_auto(self, page: QtWidgets.QWidget) -> None:
        """切分頁或改間隔即重新計時：由現在起計，而不是沿用上一輪的時刻去湊新間隔。"""
        self._last_auto[page.objectName()] = time.monotonic()

    def _tick(self) -> None:
        """自動更新：只針對當前分頁。標的頁預設重讀離線快照（不打券商），勾上「自動向券商重拉」才即時取清單。

        K 線兩個分頁沒有自動更新：1000 根要數秒，定時重取會把同一條券商連線長期佔住。
        """
        page = self.window.tabs.currentWidget()
        spinner = getattr(page, "autoIntervalSpin", None)
        gap = spinner.value() if spinner is not None else 0
        key = page.objectName()
        if not gap or self._inflight or time.monotonic() - self._last_auto.get(key, 0.0) < gap:
            return
        self._last_auto[key] = time.monotonic()
        if page is self.accounts:
            self.request_accounts()
        elif self.symbols.liveRefreshCheck.isChecked():
            self.request_symbols()
        else:
            self.request_codes_load()

    def _on_kind(self, _index: int) -> None:
        """轉類型時清空市場選項：各品種返回的市場不同，留著上一品種的市場只會白得一個 empty_list。"""
        self.seen_markets.clear()
        self.render_markets()
        self.render_brokers()
        self.request_symbols()

    def _request(self, path: str, params: dict | None, on_done) -> None:
        thread = QtCore.QThread(self.window)
        worker = GatewayWorker(self.client, path, params)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)

        def deliver(envelope: dict) -> None:
            self._inflight -= 1
            on_done(envelope)

        relay = ReplyRelay(deliver, self.window)      # 屬主執行緒：故 finished 的信封由 Qt 排隊交回
        worker.finished.connect(relay.deliver)
        worker.finished.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(relay.deleteLater)
        self._jobs.add((thread, worker))
        thread.finished.connect(lambda: self._jobs.discard((thread, worker)))
        self._inflight += 1
        thread.start()

    def set_status(self, text: str, color: str) -> None:
        self.window.statusLabel.setText(text)
        self.window.statusLabel.setStyleSheet(color)

    def _report(self, envelope: dict, label: QtWidgets.QLabel) -> None:
        """狀態與原因一律原樣顯示：失敗就是失敗；個別券商失敗時閘道仍返回已取得的資料，故以警告色提示。"""
        message = str(envelope.get("message") or "")
        label.setText(message)
        if not envelope.get("status"):
            label.setStyleSheet(COLOR_ERROR)
            self.set_status(self.tr.t("status.failed"), COLOR_ERROR)
            return
        label.setStyleSheet(COLOR_WARN if message else "")
        self.set_status(self.tr.t("status.ok"), "")

    # ---------------------------------------------------------------- 戶口
    def request_accounts(self) -> None:
        self.set_status(self.tr.t("status.loading"), "")
        self._request("/accounts", None, self.show_accounts)

    def show_accounts(self, envelope: dict) -> None:
        data = envelope.get("data") or {"columns": [], "rows": []}
        fill_table(self.accounts.accountsTable, data)
        self.accounts.summaryLabel.setText(self._summary(data, "accounts.summary", "accounts.by_source"))
        self._report(envelope, self.accounts.messageLabel)

    def _summary(self, data: dict, total_key: str, by_source_key: str) -> str:
        parts = [self.tr.t(total_key, count=len(data.get("rows") or []))]
        parts += [self.tr.t(by_source_key, source=src, count=n) for src, n in count_by_source(data)]
        return "；".join(parts)

    # ---------------------------------------------------------------- 標的
    def request_capabilities(self) -> None:
        """券商選項只由能力聲明填充：桌面端不硬寫券商名單。"""
        self.set_status(self.tr.t("status.loading"), "")
        self._request("/capabilities", None, self.show_capabilities)

    def show_capabilities(self, envelope: dict) -> None:
        if not envelope.get("status"):
            self._report(envelope, self._message_label())
            return
        data = envelope.get("data") or {}
        adapters = data.get("adapters") or {}
        self.broker_caps = {name: list(info.get("capabilities") or []) for name, info in adapters.items()}
        self.ktypes = list(data.get("ktypes") or self.ktypes)
        self.stream_ktypes = {name: [str(k) for k in (info.get("stream_ktypes") or [])]
                              for name, info in adapters.items()}
        self.render_brokers()
        self.render_ktypes()
        self.render_grid()
        if self.window.tabs.currentWidget() is not self.symbols:
            return   # K 線分頁只是要重讀週期與券商選項：標的頁的清單與快照與它們無關
        # 選項填好後才核對快照：選中的若不是剛才讀的那一家，必須改讀這一檔，否則顯示的是別家的行數。
        if self._codes_broker() != self.codes_snapshot_source:
            self.request_codes_meta()
        self.request_symbols()

    def _message_label(self) -> QtWidgets.QLabel:
        """能力聲明的失敗要顯示在觸發它的那一頁：K 線頁與標的頁各自有 messageLabel。"""
        return getattr(self.window.tabs.currentWidget(), "messageLabel", self.accounts.messageLabel)

    def render_ktypes(self) -> None:
        """週期選項只由 /capabilities 的 ktypes 填充，預設選 1m；不支持的週期由接口報錯，這裡不自行過濾。"""
        for page in (self.kline_pull, self.kline_stream):
            combo = page.ktypeCombo
            current = combo.currentData()
            combo.blockSignals(True)
            combo.clear()
            for ktype in self.ktypes:
                combo.addItem(ktype, ktype)
            preferred = current if current in self.ktypes else DEFAULT_KTYPE
            index = combo.findData(preferred if preferred in self.ktypes else self.ktypes[0])
            if index >= 0:
                combo.setCurrentIndex(index)
            combo.blockSignals(False)

    def render_brokers(self) -> None:
        """券商下拉框只由能力聲明填充：被停用的券商不在聲明內，故三處下拉框同時不再列它，這裡不需自己記開關。

        標的頁另按所選品種標註不可選的原因，而不是讓用戶按了才知道會報 type_unsupported；K 線三個分頁沒有
        品種限制，只列生效者。
        """
        kind = self.symbols.kindCombo.currentData()
        self._fill_broker_combo(self.symbols.brokerCombo, KIND_CAPABILITIES.get(kind, ""),
                                self.tr.t(f"kind.{kind}") if kind else "")
        for page in (self.kline_pull, self.kline_stream, self.kline_grid):
            self._fill_broker_combo(page.brokerCombo, "", "")

    def _fill_broker_combo(self, combo: QtWidgets.QComboBox, capability: str, kind_label: str) -> None:
        current = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        for name, caps in self.broker_caps.items():
            supported = not capability or capability in caps
            label = (self.tr.t("symbols.broker_option", source=name) if supported else
                     self.tr.t("symbols.broker_unsupported", source=name, types=kind_label))
            combo.addItem(label, name)
            combo.model().item(combo.count() - 1).setEnabled(supported)
        preferred = next((name for name in (current, DEFAULT_BROKER)
                          if not capability or capability in self.broker_caps.get(name, [])),
                         next((n for n, c in self.broker_caps.items() if capability in c), None))
        index = combo.findData(preferred)
        if index >= 0:
            combo.setCurrentIndex(index)
        combo.blockSignals(False)

    def render_markets(self) -> None:
        """市場選項只由返回過的行填充，不憑空給出選項。"""
        combo = self.symbols.marketCombo
        current = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        combo.addItem(self.tr.t("symbols.all_markets"), "")
        for market in sorted(self.seen_markets):
            combo.addItem(market, market)
        index = combo.findData(current if current in self.seen_markets else "")
        combo.setCurrentIndex(max(index, 0))
        combo.blockSignals(False)

    def request_symbols(self) -> None:
        kind = self.symbols.kindCombo.currentData()
        params = {"broker": self.symbols.brokerCombo.currentData() or DEFAULT_BROKER}
        market = self.symbols.marketCombo.currentData()
        if market:
            params["markets"] = market
        self.set_status(self.tr.t("status.loading"), "")
        # 轉類型／市場／券商即作廢上一輪：晚到的舊回應不得覆蓋當前兩張表。
        self._symbols_seq += 1
        seq = self._symbols_seq
        path = SYMBOL_PATHS[kind]
        self._request(path, params, lambda envelope: self.show_symbols(envelope, path, params, seq))

    def show_symbols(self, envelope: dict, path: str, params: dict, seq: int) -> None:
        if seq != self._symbols_seq:
            return
        data = envelope.get("data") or {"columns": [], "rows": []}
        fill_table(self.symbols.symbolsTable, data)
        columns = list(data.get("columns") or [])
        if "market" in columns:
            index = columns.index("market")
            self.seen_markets.update(str(row[index]) for row in data.get("rows") or [] if index < len(row))
        self.render_markets()
        self.symbols.summaryLabel.setText(self._summary(data, "symbols.summary", "accounts.by_source"))
        if envelope.get("status") and not (data.get("rows") or []):
            envelope = {**envelope, "message": self.tr.t("symbols.no_rows")}
        self._report(envelope, self.symbols.messageLabel)
        # 下表完成後才取上表：兩次同參數，只差 raw=1，且必須順序而非並行。
        self._request(path, {**params, "raw": "1"}, lambda raw: self.show_raw_symbols(raw, seq))

    def show_raw_symbols(self, envelope: dict, seq: int) -> None:
        """上表：欄位與值一律按該券商返回的原樣填充。原因只寫在本表的標籤，不影響下表與狀態列。"""
        if seq != self._symbols_seq:
            return
        fill_table(self.symbols.rawTable, envelope.get("data") or {"columns": [], "rows": []})
        message = str(envelope.get("message") or "")
        self.symbols.rawMessageLabel.setText(message)
        self.symbols.rawMessageLabel.setStyleSheet(
            COLOR_ERROR if not envelope.get("status") else (COLOR_WARN if message else ""))

    # ------------------------------------------------------------ 離線 CODES 快照
    def _codes_broker(self) -> str:
        """離線 CODES 一律按當前所選券商：各券商各存一檔，讀取與更新都只針對這一家。"""
        return self.symbols.brokerCombo.currentData() or DEFAULT_BROKER

    def request_codes_load(self) -> None:
        """離線讀回所選券商存放的 CODES（不打券商，實測 0.03s），填下表。同時作進行中的清單請求：
        晚到的券商回應不得蓋掉用戶剛按的離線讀取。"""
        self._symbols_seq += 1
        seq = self._symbols_seq
        self.set_status(self.tr.t("status.loading"), "")
        self._request("/codes", {"broker": self._codes_broker()},
                      lambda envelope: self.show_codes_load(envelope, seq))

    def show_codes_load(self, envelope: dict, seq: int) -> None:
        if seq != self._symbols_seq:
            return
        data = envelope.get("data") or {"columns": [], "rows": []}
        fill_table(self.symbols.symbolsTable, data)
        # 快照只存放統一格式，沒有券商自帶的欄位：上表清空並說明原因，不留上一家的欄位在這裡。
        fill_table(self.symbols.rawTable, {"columns": [], "rows": []})
        self.symbols.rawMessageLabel.setText(self.tr.t("symbols.codes_raw_note"))
        self.symbols.rawMessageLabel.setStyleSheet(COLOR_WARN)
        self.symbols.summaryLabel.setText(self._summary(data, "symbols.summary", "accounts.by_source"))
        self._report({**envelope, "message": f"{envelope.get('message') or ''}{self.tr.t('symbols.codes_loaded')}"},
                     self.symbols.messageLabel)

    def request_codes_meta(self) -> None:
        """讀回所選券商離線 CODES 快照的元資料（行數、距今時間、是否過舊、上次更新失敗的原因）。
        閘道離線讀取，不需要任何券商連線，故與清單請求互不影響。"""
        broker = self._codes_broker()
        # 先記下問的是哪一档：標籤在回應送達前也要點名券商，且能力聲明完成時不會再誤判為「未讀過」。
        self.codes_snapshot_source = broker
        self._request("/codes/meta", {"broker": broker},
                      lambda envelope: self.show_codes_meta(envelope, broker))

    def show_codes_meta(self, envelope: dict, broker: str) -> None:
        if broker != self._codes_broker():
            return   # 期間已轉券商：上一檔的回應不得蓋上新一檔的狀態
        if not envelope.get("status"):
            # 該家尚未存放（各券商各一檔，新券商本就沒有檔）：明確點名是哪一家，不顯示上一家的數字。
            self.codes_snapshot = None
            self.symbols.codesLabel.setText(
                self.tr.t("symbols.codes_error", source=broker, detail=str(envelope.get("message") or "")))
            self.symbols.codesLabel.setStyleSheet(COLOR_ERROR)
            return
        data = envelope.get("data") or {}
        self.codes_snapshot = dict(zip(list(data.get("columns") or []), (data.get("rows") or [[]])[0]))
        self.render_codes_state()

    def render_codes_state(self) -> None:
        """快照狀態一行：行數與距今時間。過舊或上次更新失敗以警告色提示——快照往往是唯一的離線副本，
        過舊時會查唔到新上市的代碼，但已存放的資料仍然可用，故不是失敗。"""
        if not self.codes_snapshot:
            return
        text = self.tr.t("symbols.codes_state", source=self.codes_snapshot_source,
                         count=self.codes_snapshot.get("rows", 0),
                         age=self._age_text(self.codes_snapshot.get("age_seconds")))
        if self.codes_snapshot.get("last_refresh_error"):
            text += self.tr.t("symbols.codes_last_error")
        self.symbols.codesLabel.setText(text)
        self.symbols.codesLabel.setStyleSheet(
            COLOR_WARN if self.codes_snapshot.get("stale") or self.codes_snapshot.get("last_refresh_error") else "")

    def _age_text(self, seconds) -> str:
        """距今時間以「N 小時前」這類粗粒度顯示：用戶要判斷的是「幾時更新過」，不是精確秒數。
        無存放時間（含缺失或不可解析）一律明說，不湊成「剛剛」。"""
        try:
            seconds = float(seconds)
        except (TypeError, ValueError):
            return self.tr.t("age.unknown")
        if not math.isfinite(seconds):
            return self.tr.t("age.unknown")
        for key, size in (("age.days", 86400), ("age.hours", 3600), ("age.minutes", 60)):
            if seconds >= size:
                return self.tr.t(key, count=int(seconds // size))
        return self.tr.t("age.just_now")

    def request_codes_refresh(self) -> None:
        """向所選券商重拉全量 CODES 並覆蓋該家的離線快照（需券商連線，實測約數秒）。不帶市場參數：
        快照就是全量，只拉部分市場會被閘道的縮細防護拒絕。"""
        broker = self._codes_broker()
        self.set_status(self.tr.t("status.loading"), "")
        self.symbols.codesRefreshButton.setEnabled(False)   # 重拉需數秒，期間不可重覆送出
        self.symbols.codesLabel.setText(self.tr.t("symbols.codes_refreshing", source=broker))
        self._request("/codes/refresh", {"broker": broker}, self.show_codes_refresh)

    def show_codes_refresh(self, envelope: dict) -> None:
        self.symbols.codesRefreshButton.setEnabled(True)
        self._report(envelope, self.symbols.messageLabel)   # 拒絕覆蓋等原因原樣顯示，不掩飾
        # 成敗都要重讀快照狀態：失敗原因會記進 meta，成功時距今時間即變為「剛剛」。
        self.request_codes_meta()

    # ---------------------------------------------------------------- K 線
    def _kline_controls(self, page: QtWidgets.QWidget) -> tuple[str, str, int, str]:
        """讀一頁控制列的值：參數原樣交閘道判定（不支持即 ktype_unsupported、被停用即 broker_disabled），
        本層不校验，也不另設一套預設。"""
        return (page.codeEdit.text().strip(),
                page.ktypeCombo.currentData() or DEFAULT_KTYPE,
                page.countSpin.value(),
                page.brokerCombo.currentData() or DEFAULT_BROKER)

    def request_kline(self, pane: KlinePane, on_done=None) -> None:
        """向所選券商取歷史 K 線。1000 根要數秒，故期間狀態列寫明在向哪一家取什麼，免得看似卡住。

        on_done 於回覆處理完之後執行：「訂閱實時」正是用它把「先取歷史」接上「再開串流」。
        """
        page = pane.page
        code, ktype, count, broker = self._kline_controls(page)
        pane.select(code, ktype, count)
        page.messageLabel.setText(self.tr.t("kline.pulling", source=broker, code=code, ktype=ktype, count=count))
        self.set_status(self.tr.t("status.loading"), "")
        self._request("/kline", {"code": code, "ktype": ktype, "count": count, "broker": broker},
                      lambda envelope: self.show_kline(envelope, pane, on_done))

    def show_kline(self, envelope: dict, pane: KlinePane, on_done=None) -> None:
        if envelope.get("status"):
            pane.store.add(envelope.get("data") or {})
            if not pane.store.size:
                envelope = {**envelope, "message": self.tr.t("kline.no_rows")}
        self._report(envelope, pane.page.messageLabel)
        self.paint_kline(pane)
        if on_done is not None:
            on_done()

    def paint_kline(self, pane: KlinePane) -> None:
        """表格顯示合併後的序列，按時間反序（最新在最上）：反序只在顯示層做，序列本身與接口一樣是 ts 升序。"""
        page = pane.page
        payload = pane.store.payload()
        fill_table(page.klineTable, {"columns": payload["columns"], "rows": list(reversed(payload["rows"]))})
        page.summaryLabel.setText(self._summary(payload, "kline.summary", "kline.by_source"))
        # 有圖表區的分頁即畫同一份序列：座標軸、series、縮放全由那份共用的 chart.js 決定，桌面端不另寫一套圖表
        if pane.chart is not None:
            pane.chart.render(chart.frame(payload), ktype=pane.key[1] if pane.key else None)

    # ---------------------------------------------------------------- K 線串流
    def start_stream(self, pane: KlinePane) -> None:
        """先取歷史再開串流：串流的 update 只帶最近 count 根，直接訂閱即得返一張只有最近幾十根的圖，
        與普通行情軟件「歷史 + 實時」一條連續序列的做法相反。故一律先取歷史，回覆後才建立連接。"""
        if pane.wants_stream or pane.stream is not None:
            return
        pane.wants_stream = True
        self.set_stream_buttons(pane.page, True)   # 取歷史期間不可重覆送出；期間按「停止」即取消這次訂閱
        self.request_kline(pane, lambda: self.open_stream(pane))

    def open_stream(self, pane: KlinePane) -> None:
        """歷史已在圖上，現在才訂閱：之後的 update 一律經 BarStore 合併進同一條序列。
        沒有歷史即不訂閱——留下的會是一張只有實時 bar、卻會被誤認為完整歷史的圖（原因已由取數點名）。

        只經閘道的 /stream，桌面端不直接連券商（理由與 api.py 相同）。
        先「停止」再「訂閱」照樣送到閘道：同一份請求由它接手仍在推送嘅串流，即刻繼續收，唔使等上一條嘅
        時窗走完。換咗參數即係另一條串流，同一券商同一週期可並行多條，不會被拒。失敗（ktype_unsupported、
        broker_disabled）原樣顯示，不自動重連，免得出現用戶看不見嘅連接。
        """
        page = pane.page
        if not pane.wants_stream:
            self.set_stream_buttons(page, False)   # 取歷史期間已按「停止」：不再建立連接
            return
        if not pane.store.size:
            self.end_stream(pane)
            return
        code, ktype, count, broker = self._kline_controls(page)
        pane.select(code, ktype, count)
        try:
            # parent 係必須的：由 Qt（主窗口）持有呢個物件，界面先至敢在 finished 的信號鏈中途放手（見 end_stream）。
            client = StreamClient(base_url=self.client.base_url, api_key=self.client.api_key,
                                  parent=self.window)
        except Exception as exc:   # 沒有 API_KEY 即連不上閘道：點名原因，而不是靜靜不動作
            self._on_stream_failed(pane, str(exc))
            return
        pane.stream = client
        client.subscribed.connect(lambda msg: self._on_subscribed(pane, msg))
        client.update.connect(lambda msg: self._on_stream_update(pane, msg))
        client.closed.connect(lambda msg: self._on_stream_closed(pane, msg))
        client.error.connect(lambda msg: self._on_stream_error(pane, msg))
        client.failed.connect(lambda detail: self._on_stream_failed(pane, detail))
        client.finished.connect(lambda: self.end_stream(pane))
        self.set_stream_buttons(page, True)
        client.start(code, ktype, count, broker)

    def stop_stream(self, pane: KlinePane) -> None:
        pane.wants_stream = False   # 取消仍在途的「先取歷史」：那時連連接都未建立
        if pane.stream is not None:
            pane.stream.stop()

    def end_stream(self, pane: KlinePane) -> None:
        """串流已結束（用戶停止、閘道收尾或連線斷開）：解鎖按鈕，並放棄仍在途的訂閱。

        連接要一併丟掉：「停止」後再按「訂閱」是換了參數的新連接，留著舊對象只會被 here 的防重入擋住。
        但放手要交 Qt 排期：呢個回調係由該連接自己的 finished 發出的，即時析構會在信號鏈中途拆掉發射者。
        """
        pane.wants_stream = False
        client, pane.stream = pane.stream, None
        if client is not None:
            client.deleteLater()
        self.set_stream_buttons(pane.page, False)

    def set_stream_buttons(self, page: QtWidgets.QWidget, streaming: bool) -> None:
        """訂閱期間「訂閱」不可再按：同一頁再起一條連接只會接手同一份請求，界面上多出一條用戶看不見的連接。"""
        page.startButton.setEnabled(not streaming)
        page.stopButton.setEnabled(streaming)

    def _on_subscribed(self, pane: KlinePane, msg: dict) -> None:
        """訂閱成功即說明會自動結束的秒數：閘道到時自己收尾，用戶不需要一直按停止。"""
        pane.page.messageLabel.setText(
            self.tr.t("kline.subscribed", source=str(msg.get("broker") or ""),
                      code=", ".join(str(c) for c in (msg.get("codes") or [])),
                      ktype=str(msg.get("ktype") or ""), seconds=msg.get("seconds", "")))
        self.set_status(self.tr.t("status.ok"), "")

    def _on_stream_update(self, pane: KlinePane, msg: dict) -> None:
        """每次 update 帶的是該代碼目前完整的 bar：必須經 BarStore 合併，否則已取的 1000 根會縮返最近幾十根。"""
        data = msg.get("data") or {}
        count = len(data.get("rows") or [])
        pane.store.add(data)
        self.paint_kline(pane)
        pane.page.messageLabel.setText(self.tr.t("kline.updated", code=str(msg.get("code") or ""),
                                                 count=count, total=pane.store.size))
        self.set_status(self.tr.t("status.ok"), "")

    def _on_stream_closed(self, pane: KlinePane, msg: dict) -> None:
        """正常結束只報收尾：呢度唔預先記低 closed 帧給嘅收尾秒數。「停止」之後再按「訂閱」係同一份請求，
        閘道會接手仍在推送嘅串流；換咗參數即另一條，本來就可以並行，沒有需要等的東西。"""
        broker = str(msg.get("broker") or "")
        pane.page.messageLabel.setText(self.tr.t("kline.stopped", source=broker))

    def _on_stream_error(self, pane: KlinePane, msg: dict) -> None:
        """協定錯誤原樣呈現，原因由閘道點名（ktype_unsupported、broker_disabled、bad_request），界面不自造，
        也不代它重試：會話參數由用戶改，界面自己重送只會出現用戶看不見嘅訂閱。"""
        self._on_stream_failed(pane, str(msg.get("message") or "stream_error"))

    def _on_stream_failed(self, pane: KlinePane, detail: str) -> None:
        pane.page.messageLabel.setText(self.tr.t("kline.stream_failed", detail=detail))
        pane.page.messageLabel.setStyleSheet(COLOR_ERROR)
        self.set_status(self.tr.t("status.failed"), COLOR_ERROR)

    # ---------------------------------------------------------------- K 線串流（多週期）
    def _grid_controls(self, page: QtWidgets.QWidget) -> tuple[str, int, str]:
        """多週期頁只有一個共用根數：九格同一根數，逐格再填一次沒有意義。週期不喺呢度讀——一格一週期。"""
        return (page.codeEdit.text().strip(), page.gridCountSpin.value(),
                page.brokerCombo.currentData() or DEFAULT_BROKER)

    def render_grid(self) -> None:
        """格子按所選券商聲明的 stream_ktypes 排（順序照返回者，本層不排序、不自訂週期）：不支持的週期唔會
        出現，亦唔會憑空排九格再逐格報錯。清單或券商一改即重建格子；能力聲明每次進頁都會重讀，故清單未變時
        唔可以重建（重建會清走各格已取嘅序列）。"""
        declared = [str(k) for k in (self.stream_ktypes.get(self.kline_grid.brokerCombo.currentData()
                                                            or DEFAULT_BROKER) or [])]
        pane = self.grid
        if pane.layout != declared:
            self.stop_grid(pane)
            pane.layout, pane.ktypes = list(declared), list(declared)
            count = self.kline_grid.gridCountSpin.value()
            pane.stores = [BarStore(count) for _ in declared]
            pane.keys = [(self.kline_grid.codeEdit.text().strip(), k) for k in declared]
        if pane.chart.view is not None and pane.built_with != pane.layout:
            pane.chart.build(pane.layout)
            pane.built_with = list(pane.layout)
        self.paint_grid_summary(pane)

    def paint_grid_summary(self, pane) -> None:
        """格子數與每格根數即寫喺控制列：呢頁冇表格，用戶要一眼知會取幾多份、每份幾多根。"""
        self.kline_grid.summaryLabel.setText(self.tr.t("kline.grid_summary", cells=len(pane.layout),
                                                       count=self.kline_grid.gridCountSpin.value()))

    def start_grid(self, pane) -> None:
        """同單週期頁一樣先取歷史再開串流，但逐格順序取：同一券商的連線（IB 一條 socket、futu 一個 OpenD
        context）不接受並行請求，九份同時送出只會互相拖慢（見 request_kline 所在的 K 線段說明）。"""
        if pane.wants or pane.stream is not None or not pane.layout:
            return
        pane.wants = True
        self.set_stream_buttons(self.kline_grid, True)
        self.pull_grid_cell(pane, 0)

    def pull_grid_cell(self, pane, index: int) -> None:
        """取第 index 格的歷史，回覆後先至取下一格：一格失敗唔拖住其餘各格（原因寫喺嗰格上面）。"""
        if not pane.wants:
            self.set_stream_buttons(self.kline_grid, False)   # 取歷史期間已按「停止」
            return
        if index >= len(pane.ktypes):
            self.open_grid_stream(pane)
            return
        code, count, broker = self._grid_controls(self.kline_grid)
        ktype = pane.ktypes[index]
        self.kline_grid.messageLabel.setText(self.tr.t("kline.pulling", source=broker, code=code,
                                                       ktype=ktype, count=count))
        self.set_status(self.tr.t("status.loading"), "")
        self._request("/kline", {"code": code, "ktype": ktype, "count": count, "broker": broker},
                      lambda envelope: self.show_grid_cell(pane, index, envelope,
                                                           lambda: self.pull_grid_cell(pane, index + 1)))

    def show_grid_cell(self, pane, index: int, envelope: dict, then=None) -> None:
        """一格一份序列：失敗或無資料只喺嗰格顯示原因，唔霸住整頁訊息列（其餘各格照樣取數、照樣串流）。
        格子若中途被重建（換咗券商），呢個回覆已屬舊格子，丟掉。"""
        code, count, _broker = self._grid_controls(self.kline_grid)
        if index >= len(pane.stores):
            return
        store = pane.stores[index]
        store.set_limit(count)
        pane.keys[index] = (code, pane.ktypes[index])
        if envelope.get("status"):
            store.add(envelope.get("data") or {})
        if not store.size:
            self.grid.chart.note_cell(index, str(envelope.get("message") or self.tr.t("kline.no_rows")))
        else:
            self.grid.chart.note_cell(index, "")
            self.paint_grid_cell(pane, index)
        if then is not None:
            then()

    def paint_grid_cell(self, pane, index: int) -> None:
        """只重畫一格：唔傳 ktype，格子自己記住係邊個週期（換咗週期嘅格即照新格式畫）。"""
        self.grid.chart.set_cell(index, chart.frame(pane.stores[index].payload()))

    def open_grid_stream(self, pane) -> None:
        """九格全部取完歷史先開一條連接：update 帧一律帶 ktype 供分派，故多週期只用一條 WS（見
        brokery_api/app.py 的 /stream）。無 bar 嘅格唔訂閱——留下的會是一張只有實時 bar、
        卻會被誤認為完整歷史嘅圖（原因已由取數點名）。"""
        page = self.kline_grid
        if not pane.wants:
            self.set_stream_buttons(page, False)
            return
        wanted = [i for i, store in enumerate(pane.stores) if store.size]
        if not wanted:
            self.end_grid(pane)
            return
        if pane.stream is None:
            try:
                # parent 係必須的：由 Qt（主窗口）持有呢個物件，界面先至敢在 finished 的信號鏈中途放手。
                client = StreamClient(base_url=self.client.base_url, api_key=self.client.api_key,
                                      parent=self.window)
            except Exception as exc:   # 沒有 API_KEY 即連不上閘道：點名原因，而不是靜靜不動作
                self._on_grid_failed(pane, str(exc))
                return
            pane.stream = client
            client.subscribed.connect(lambda msg: self._on_grid_subscribed(pane, msg))
            client.update.connect(lambda msg: self._on_grid_update(pane, msg))
            client.closed.connect(lambda msg: self._on_grid_closed(pane, msg))
            client.error.connect(lambda msg: self._on_grid_error(pane, msg))
            client.failed.connect(lambda detail: self._on_grid_failed(pane, detail))
            client.finished.connect(lambda: self.end_grid(pane))
            self.set_stream_buttons(page, True)
        self.subscribe_grid_cells(pane, wanted)

    def subscribe_grid_cells(self, pane, indexes) -> None:
        """逐格送 subscribe 幀：第一條會開啟連接，其餘照同一條排隊（見 stream.subscribe）。"""
        code, count, broker = self._grid_controls(self.kline_grid)
        for index in indexes:
            if self.grid_cells_with(pane, pane.ktypes[index], skip=index):
                continue      # 該週期已由別格訂閱：同一份請求會接手同一條串流，再送一次只是多一份訂閱
            pane.stream.subscribe(code, pane.ktypes[index], count, broker)

    def subscribe_grid_cell(self, pane, index: int) -> None:
        """一格重新訂閱（換咗該格嘅週期之後）：連接仲喺度即照同一條再送 subscribe 幀；連接已結束即重新建立
        並照樣逐格訂閱（歷史已在圖上，唔使再取一次歷史）。"""
        if not pane.wants or index >= len(pane.ktypes):
            return
        if pane.stream is None:
            self.open_grid_stream(pane)
            return
        code, count, broker = self._grid_controls(self.kline_grid)
        if self.grid_cells_with(pane, pane.ktypes[index], skip=index):
            return            # 該週期已由別格訂閱，呢格照它的推送畫，不需要（也不應該）再送一份
        pane.stream.subscribe(code, pane.ktypes[index], count, broker)

    def stop_grid(self, pane) -> None:
        """一個「停止」收晒九格：裸 stop 幀停呢條連接全部訂閱（逐格只有週期按鈕，冇逐格停止）。
        根本未建立連接時（取歷史期間已按「停止」）沒有 finished 信號經 end_grid 解鎖按鈕，要喺呢度自行收尾，
        否則「開始」一直停用。"""
        pane.wants = False
        if pane.stream is None:
            self.kline_grid.messageLabel.setText(
                self.tr.t("kline.stopped", source=self._grid_controls(self.kline_grid)[2]))
            self.kline_grid.messageLabel.setStyleSheet("")
            self.set_status(self.tr.t("status.idle"), "")
            self.set_stream_buttons(self.kline_grid, False)
            return
        pane.stream.stop()

    def end_grid(self, pane) -> None:
        """連接已結束（用戶停止、閘道收尾或斷開）：解鎖按鈕，並放棄仍在途的訂閱。
        連接要一併丟掉：「停止」後再按「開始」是換了參數的新連接，留著舊對象只會被 here 的防重入擋住。
        但放手要交 Qt 排期：呢個回調係由該連接自己的 finished 發出的，即時析構會在信號鏈中途拆掉發射者。"""
        pane.wants = False
        client, pane.stream = pane.stream, None
        if client is not None:
            client.deleteLater()
        self.set_stream_buttons(self.kline_grid, False)

    @staticmethod
    def grid_cells_with(pane, ktype: str, skip: int | None = None) -> list[int]:
        """顯示該週期的格子（update 帧的 ktype → 格子）：一格一週期，唔按它路由就會九格混進同一條序列。
        兩格可以揀同一個週期，而同一份請求（同代碼、同週期、同根數）在閘道只有一条串流，故呢啲格子共用同一份
        序列：update 填進每一格，訂閱只送一次（見 subscribe_grid_cell 與 pick_grid_cell）。"""
        return [i for i, k in enumerate(pane.ktypes) if k == ktype and i != skip]

    def _on_grid_subscribed(self, pane, msg: dict) -> None:
        """一格訂閱成功即說明會自動結束的秒數：閘道到時自己收尾，用戶不需要一直按停止。"""
        self.kline_grid.messageLabel.setText(
            self.tr.t("kline.subscribed", source=str(msg.get("broker") or ""),
                      code=", ".join(str(c) for c in (msg.get("codes") or [])),
                      ktype=str(msg.get("ktype") or ""), seconds=msg.get("seconds", "")))
        self.set_status(self.tr.t("status.ok"), "")

    def _on_grid_update(self, pane, msg: dict) -> None:
        """按 msg["ktype"] 路由到該格序列合併（update 帶的是該代碼目前完整的 bar，不合併即會縮返最近幾十根），
        再只重畫嗰格。冇格子顯示該週期即該格已換咗週期，呢一帧屬舊格子，丟掉。"""
        indexes = self.grid_cells_with(pane, str(msg.get("ktype") or ""))
        if not indexes:
            return
        data = msg.get("data") or {}
        count = len(data.get("rows") or [])
        for index in indexes:      # 同一週期由兩格顯示時共用同一份推送，逐格合併，唔會得返第一格更新
            store = pane.stores[index]
            store.add(data)
            self.paint_grid_cell(pane, index)
            self.kline_grid.messageLabel.setText(self.tr.t("kline.grid_updated",
                                                           ktype=str(msg.get("ktype") or ""),
                                                           count=count, total=store.size))
        self.set_status(self.tr.t("status.ok"), "")

    def _on_grid_closed(self, pane, msg: dict) -> None:
        """正常結束只報收尾：呢度唔預先記低 closed 帧給嘅收尾秒數。「停止」之後再按「開始」係同一份請求，
        閘道會接手仍在推送嘅串流；換咗參數即另一條，本來就可以並行，沒有需要等的東西。"""
        self.kline_grid.messageLabel.setText(self.tr.t("kline.stopped", source=str(msg.get("broker") or "")))

    def _on_grid_error(self, pane, msg: dict) -> None:
        """協定錯誤原樣呈現，原因由閘道點名（ktype_unsupported、broker_disabled、bad_request），界面不自造，
        也不代它重送：會話參數由用戶改，界面自己重送只會出現用戶看不見嘅訂閱。"""
        self._on_grid_failed(pane, str(msg.get("message") or "stream_error"))

    def _on_grid_failed(self, pane, detail: str) -> None:
        self.kline_grid.messageLabel.setText(self.tr.t("kline.stream_failed", detail=detail))
        self.kline_grid.messageLabel.setStyleSheet(COLOR_ERROR)
        self.set_status(self.tr.t("status.failed"), COLOR_ERROR)

    def pick_grid_cell(self, pane, index: int, ktype: str) -> None:
        """一格上方嘅週期按鈕：只換嗰格。舊週期若已無人顯示即停返它（stop 幀帶 broker/ktype，只停該週期），
        其餘各格唔受影響；新週期要重新取歷史——一格一週期一份序列，換咗即無歷史可畫（同「先取歷史再開串流」
        同一口徑）。揀咗別格已顯示的週期時不另送訂閱，兩格共用同一份推送。"""
        if index >= len(pane.ktypes) or ktype not in pane.layout or ktype == pane.ktypes[index]:
            return
        code, count, broker = self._grid_controls(self.kline_grid)
        previous = pane.keys[index][1]
        pane.ktypes[index] = ktype
        pane.keys[index] = (code, ktype)
        pane.stores[index].clear()
        pane.stores[index].set_limit(count)
        self.grid.chart.note_cell(index, "")
        streaming = pane.wants
        if pane.stream is not None and not self.grid_cells_with(pane, previous):
            # 仍有別格顯示舊週期即唔好停它：stop 帶 ktype 會停該週期喺呢條連接上嘅全部串流，一停連嗰格嘅推送
            # 一併冇咗
            pane.stream.unsubscribe(broker, previous)
        self.kline_grid.messageLabel.setText(self.tr.t("kline.pulling", source=broker, code=code,
                                                       ktype=ktype, count=count))
        self.set_status(self.tr.t("status.loading"), "")
        self._request("/kline", {"code": code, "ktype": ktype, "count": count, "broker": broker},
                      lambda envelope: self.show_grid_cell(pane, index, envelope,
                                                           lambda: self.resume_grid_cell(pane, index, streaming)))

    def resume_grid_cell(self, pane, index: int, streaming: bool) -> None:
        """換咗週期嘅格重新訂閱：退掉舊週期可能令連接上最後一個訂閱也結束（StreamClient 收口 → end_grid），
        那時 wants 已被清掉，但用戶冇按「停止」，所以要照剛才的意圖重新建立連接。"""
        if not streaming:
            return
        pane.wants = True
        self.subscribe_grid_cell(pane, index)

    # ---------------------------------------------------------------- BROKER 開關
    def request_prefs(self) -> None:
        """開關狀態列出全部可用券商（含被停用者），否則被停用者會喺頁面上消失、無法重新啟用。"""
        self.set_status(self.tr.t("status.loading"), "")
        self._request("/brokers/prefs", None, self.show_prefs)

    def show_prefs(self, envelope: dict) -> None:
        self._report(envelope, self.brokers.messageLabel)
        self.render_prefs(envelope.get("data") or {})

    def render_prefs(self, data: dict) -> None:
        """開關按返回的行重建：.env 未包含者（configured=False）不可勾選並在同一行讀原因，
        因為那不是開關能改的事。"""
        clear_layout(self.brokers.prefsLayout)
        self._pref_boxes = {}
        at = row_lookup(data)
        if "source" not in at:
            return
        for row in data.get("rows") or []:
            source = str(row[at["source"]])
            box = QtWidgets.QCheckBox(source)
            box.setChecked(bool(row[at["enabled"]]))
            box.setEnabled(bool(row[at["configured"]]))
            row_layout = QtWidgets.QHBoxLayout()
            row_layout.addWidget(box)
            detail = str(row[at["detail"]] or "")
            if detail:
                note = QtWidgets.QLabel(detail)   # 原因是接口給的，不是界面文字
                note.setStyleSheet(COLOR_WARN)
                row_layout.addWidget(note)
            row_layout.addStretch(1)
            self.brokers.prefsLayout.addLayout(row_layout)
            self._pref_boxes[source] = box
        enabled = [name for name, box in self._pref_boxes.items() if box.isChecked()]
        self.brokers.summaryLabel.setText(
            self.tr.t("brokers.summary", count=len(enabled)) if enabled else self.tr.t("brokers.none"))

    def apply_prefs(self) -> None:
        """一次交齊完整生效名單：寫檔與即時套用由 core 一處完成，改完所有動作即不再經過被停用者。"""
        enabled = [name for name, box in self._pref_boxes.items() if box.isChecked()]
        # 全不勾即省略參數：與閘道「省略即全部停用」一致；名單不可經大寫化處理，故不經 _split。
        self._request("/brokers/prefs/update", {"enabled": ",".join(enabled)} if enabled else None,
                      self.show_prefs_update)

    def show_prefs_update(self, envelope: dict) -> None:
        self._report(envelope, self.brokers.messageLabel)
        if not envelope.get("status"):
            return
        self.render_prefs(envelope.get("data") or {})   # 寫入成功的回應即最新狀態，不需再讀一次
        # 開關一改即重讀能力聲明：被停用者要即時從各頁的券商下拉框消失。
        self.request_capabilities()
