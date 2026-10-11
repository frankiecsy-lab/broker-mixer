"""桌面 GUI：只負責載入 .ui 與接駁閘道，取數一律經 brokery_api。

界面與文字分離：.ui 檔內不寫任何文字，顯示文字一律由 i18n 按鍵取，故切換語言只重貼標籤，不需重建窗口。
表格欄位直接取自返回的 columns（即 core 的欄位契約），這裡不另定義欄位順序，也不重新解讀或湊數。
取數在背景執行緒進行：IB 連線可達 40s，界面若同步等待即凍結。
"""
from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader

from .api import GatewayClient
from .i18n import DEFAULT_LANGUAGE, LANGUAGES, Translator

UI_DIR = Path(__file__).with_name("ui")
# 「類型」選項 → 閘道的清單接口。只有這三項，其餘一律 unknown_kind，不猜用戶想要什麼。
SYMBOL_PATHS = {"stock": "/stocks", "future": "/futures", "index": "/indices"}
KINDS = tuple(SYMBOL_PATHS)
DEFAULT_BROKER = "futu"
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


class GatewayWorker(QtCore.QObject):
    """在背景執行一次閘道請求，完成後把信封交還主執行緒。"""

    finished = QtCore.Signal(dict)

    def __init__(self, client: GatewayClient, path: str, params: dict | None) -> None:
        super().__init__()
        self.client, self.path, self.params = client, path, params

    def run(self) -> None:
        self.finished.emit(self.client.get(self.path, self.params))


class DesktopGui:
    """主窗口：把 .ui、字庫與閘道客戶端接在一起。"""

    def __init__(self, client: GatewayClient | None = None, language: str = DEFAULT_LANGUAGE) -> None:
        self.client = client or GatewayClient()
        self.tr = Translator(language)
        self.window = load_ui("main_window.ui")
        self.accounts = load_ui("accounts_page.ui")
        self.symbols = load_ui("symbols_page.ui")
        self.window.tabs.addTab(self.accounts, "")
        self.window.tabs.addTab(self.symbols, "")
        self._jobs: set = set()
        self.broker_caps: dict[str, list[str]] = {}
        self.seen_markets: set[str] = set()
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

    def set_language(self, language: str) -> None:
        """切換語言：換字庫後重貼所有標籤與選項文字，不需重建窗口，也不重新取數。"""
        self.tr.set_language(language)
        self._retranslate()
        self.render_brokers()
        self.render_markets()

    def _retranslate(self) -> None:
        t = self.tr.t
        self.window.setWindowTitle(t("app.title"))
        self.window.languageLabel.setText(t("bar.language"))
        self.window.tabs.setTabText(0, t("tab.accounts"))
        self.window.tabs.setTabText(1, t("tab.symbols"))
        self.accounts.refreshButton.setText(t("accounts.refresh"))
        for label, key in ((self.symbols.kindLabel, "symbols.kind"), (self.symbols.marketLabel, "symbols.market"),
                           (self.symbols.brokerLabel, "symbols.broker")):
            label.setText(t(key))
        self.symbols.fetchButton.setText(t("symbols.fetch"))
        combo = self.symbols.kindCombo
        for i in range(combo.count()):
            combo.setItemText(i, t(f"kind.{combo.itemData(i)}"))

    # ---------------------------------------------------------------- 接駁
    def _connect(self) -> None:
        self.window.languageCombo.currentIndexChanged.connect(self._on_language)
        self.accounts.refreshButton.clicked.connect(self.request_accounts)
        self.window.tabs.currentChanged.connect(self._on_tab)
        self.symbols.fetchButton.clicked.connect(self.request_symbols)
        self.symbols.kindCombo.currentIndexChanged.connect(self._on_kind)
        self.symbols.marketCombo.currentIndexChanged.connect(self.request_symbols)
        self.symbols.brokerCombo.currentIndexChanged.connect(self.request_symbols)
        self._on_tab(self.window.tabs.currentIndex())

    def _on_language(self, index: int) -> None:
        self.set_language(self.window.languageCombo.itemData(index))

    def _on_tab(self, index: int) -> None:
        if index == 0:
            self.request_accounts()
        elif index == 1:
            self.request_capabilities()

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
        worker.finished.connect(on_done)
        worker.finished.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self._jobs.add((thread, worker))
        thread.finished.connect(lambda: self._jobs.discard((thread, worker)))
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
            self._report(envelope, self.symbols.messageLabel)
            return
        adapters = (envelope.get("data") or {}).get("adapters") or {}
        self.broker_caps = {name: list(info.get("capabilities") or []) for name, info in adapters.items()}
        self.render_brokers()
        self.request_symbols()

    def render_brokers(self) -> None:
        """不提供所選品種的券商標註原因並設為不可選，而不是讓用戶按了才知道會報 type_unsupported。"""
        combo = self.symbols.brokerCombo
        kind = self.symbols.kindCombo.currentData()
        current = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        for name, caps in self.broker_caps.items():
            supported = kind in caps
            label = (self.tr.t("symbols.broker_option", source=name) if supported else
                     self.tr.t("symbols.broker_unsupported", source=name, types=self.tr.t(f"kind.{kind}")))
            combo.addItem(label, name)
            combo.model().item(combo.count() - 1).setEnabled(supported)
        preferred = next((name for name in (current, DEFAULT_BROKER) if kind in self.broker_caps.get(name, [])),
                         next((n for n, c in self.broker_caps.items() if kind in c), None))
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
        self._request(SYMBOL_PATHS[kind], params, self.show_symbols)

    def show_symbols(self, envelope: dict) -> None:
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
