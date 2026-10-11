"""桌面 GUI：只負責載入 .ui 與接駁閘道，取數一律經 brokery_api。

界面與文字分離：.ui 檔內不寫任何文字，顯示文字一律由 i18n 按鍵取，故切換語言只重貼標籤，不需重建窗口。
表格欄位直接取自返回的 columns（即 core 的欄位契約），這裡不另定義欄位順序，也不重新解讀或湊數。
取數在背景執行緒進行：IB 連線可達 40s，界面若同步等待即凍結。
標的頁分上下兩表：上表為該券商自帶的欄位與格式（同參數再取一次 raw=1），下表為統一格式。兩次取數必須順序，
同一券商的連線（IB 一條 socket、futu 一個 OpenD context）不接受並行請求。
"""
from __future__ import annotations

import math
from pathlib import Path

from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader

from .api import GatewayClient
from .i18n import DEFAULT_LANGUAGE, LANGUAGES, Translator

UI_DIR = Path(__file__).with_name("ui")
# 「類型」選項 → 閘道的清單接口。只有這三項，其餘一律 unknown_kind，不猜用戶想要什麼。
SYMBOL_PATHS = {"stock": "/stocks", "future": "/futures", "index": "/indices"}
KINDS = tuple(SYMBOL_PATHS)
# 能力聲明以 symbol_type 的大寫常量表達（見 brokers/codes.py），與界面用的 kind 值大小寫不同，
# 故必須顯式對應；以 kind 直接比對 capabilities 會永遠不成立，所有券商都被視為不可選。
KIND_CAPABILITIES = {"stock": "STOCK", "future": "FUTURE", "index": "INDEX"}
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
        self._symbols_seq = 0
        self.broker_caps: dict[str, list[str]] = {}
        self.seen_markets: set[str] = set()
        self.codes_snapshot: dict | None = None   # 離線 CODES 快照的元資料行；未讀到即為 None
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
        self.symbols.rawLabel.setText(t("symbols.raw_title"))
        self.symbols.unifiedLabel.setText(t("symbols.unified_title"))
        self.symbols.fetchButton.setText(t("symbols.fetch"))
        self.symbols.codesRefreshButton.setText(t("symbols.codes_refresh"))
        self.render_codes_state()
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
        self.symbols.codesRefreshButton.clicked.connect(self.request_codes_refresh)
        self._on_tab(self.window.tabs.currentIndex())

    def _on_language(self, index: int) -> None:
        self.set_language(self.window.languageCombo.itemData(index))

    def _on_tab(self, index: int) -> None:
        if index == 0:
            self.request_accounts()
        elif index == 1:
            self.request_capabilities()
            # 快照狀態與清單無關（離線讀回，不需券商連線），故同時取，不等清單完成才顯示。
            self.request_codes_meta()

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
        capability = KIND_CAPABILITIES.get(kind, "")
        current = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        for name, caps in self.broker_caps.items():
            supported = capability in caps
            label = (self.tr.t("symbols.broker_option", source=name) if supported else
                     self.tr.t("symbols.broker_unsupported", source=name, types=self.tr.t(f"kind.{kind}")))
            combo.addItem(label, name)
            combo.model().item(combo.count() - 1).setEnabled(supported)
        preferred = next((name for name in (current, DEFAULT_BROKER) if capability in self.broker_caps.get(name, [])),
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
    def request_codes_meta(self) -> None:
        """讀回離線 CODES 快照的元資料（行數、距今時間、是否過舊、上次更新失敗的原因）。
        閘道離線讀取，不需要任何券商連線，故與清單請求互不影響。"""
        self._request("/codes/meta", None, self.show_codes_meta)

    def show_codes_meta(self, envelope: dict) -> None:
        if not envelope.get("status"):
            self.codes_snapshot = None
            self.symbols.codesLabel.setText(
                self.tr.t("symbols.codes_error", detail=str(envelope.get("message") or "")))
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
        text = self.tr.t("symbols.codes_state", count=self.codes_snapshot.get("rows", 0),
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
        """重拉全量 CODES 並覆蓋離線快照（需券商連線，實測約數秒）。不帶市場參數：快照就是全量，
        只拉部分市場會被閘道的縮細防護拒絕。"""
        self.set_status(self.tr.t("status.loading"), "")
        self.symbols.codesRefreshButton.setEnabled(False)   # 重拉需數秒，期間不可重覆送出
        self.symbols.codesLabel.setText(self.tr.t("symbols.codes_refreshing"))
        self._request("/codes/refresh", None, self.show_codes_refresh)

    def show_codes_refresh(self, envelope: dict) -> None:
        self.symbols.codesRefreshButton.setEnabled(True)
        self._report(envelope, self.symbols.messageLabel)   # 拒絕覆蓋等原因原樣顯示，不掩飾
        # 成敗都要重讀快照狀態：失敗原因會記進 meta，成功時距今時間即變為「剛剛」。
        self.request_codes_meta()
