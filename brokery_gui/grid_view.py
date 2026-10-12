"""多週期格子的渲染視圖：QWebEngineView 載入 brokery/static/chart_grid.html，格子與資料經 brokery.chart.grid_* 注入。

與 chart_view.py 同一條路徑：圖形仍由那一份 static/chart.js 畫（opts.compact），本模組只排格子、
逐格注入與取回被按下的週期切換，不含任何繪圖邏輯，所以桌面端與 Web UI 的多週期頁看到的完全一樣。

週期切換用輪詢而不是 QWebChannel：QWebChannel 在 offscreen 載入下會令 WebEngine 崩潰（實測過），
故由頁面把被按下的 [序號, ktype] 排進佇列，界面按定時取走。輪詢只在該分頁可見且頁面已就緒時進行。
"""
from __future__ import annotations

import pandas as pd
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget

from brokery import chart

POLL_MS = 500


class GridView:
    """一個容器對應一份多週期格子：build() 按傳入的週期清單排格，set_cell() 只重畫一格。

    on_state(原因) 為狀態回調：載入成功傳空字串、失敗傳原因。格子數與每格的週期按鈕全由那份 JS 按
    傳入清單生成，界面不另排次序，也不自己決定有幾多格。
    """

    def __init__(self, container: QWidget, on_state=None) -> None:
        self.error = ""
        self.on_state = on_state
        self._ready = False
        self._view = None
        # 載入未完成即注入會找不到 BrokeryGrid：留低待補的呼叫。逐格只留最新一份，唔會隨更新膨脹。
        self._build = ""
        self._cells: dict[int, str] = {}
        self._notes: dict[int, str] = {}
        self._poll: QTimer | None = None
        self._on_pick = None
        self._asking = False
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
        except Exception as exc:  # 無 QtWebEngine（或不在 QApplication 建立前匯入）
            self.error = f"webengine_missing: {exc}"
            return
        self._view = QWebEngineView(container)
        # 格子要佔盡容器：QVBoxLayout 對 Preferred 的元件會同提示列各分一半，故明確標為 Expanding 並俾 stretch。
        self._view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._view.loadFinished.connect(self._on_loaded)
        self._view.load(QUrl.fromLocalFile(str(chart.grid_page())))
        container.layout().addWidget(self._view, 1)

    @property
    def ready(self) -> bool:
        return self._ready

    def _send(self, call: str, key=None) -> str:
        """已就緒即即刻執行；未就緒即留低（同一 key 只留最新一份），載入完成即按序補上。"""
        if self._view is None:
            return self.error
        if self._ready:
            self._view.page().runJavaScript(call)
            return ""
        if key is None:
            self._build, self._cells, self._notes = call, {}, {}
        else:
            (self._cells if key[0] == "c" else self._notes)[key[1]] = call
        return ""

    def build(self, ktypes) -> str:
        """按傳入的週期清單建立格子（順序照傳入者）；重建會先收返舊實例，換券商即重建而唔會漏圖。"""
        return self._send(chart.grid_js(ktypes))

    def set_cell(self, index: int, frame: pd.DataFrame, ktype: str | None = None) -> str:
        """只重畫一格；ktype 省略即沿用該格現有週期（串流更新就是這種情況）。"""
        return self._send(chart.grid_set_js(index, frame, ktype), ("c", int(index)))

    def note_cell(self, index: int, text: str) -> str:
        """在某格顯示一行提示（例如該週期的名額尚未釋放）：逐格上報，不霸住整頁訊息列。"""
        return self._send(chart.grid_note_js(index, text), ("n", int(index)))

    def picks(self, on_pick) -> None:
        """開始輪詢被按下的週期切換：on_pick(序號, ktype)。只在頁面已就緒時送問，唔使喺後台空轉。"""
        self._on_pick = on_pick
        if self._poll is None:
            self._poll = QTimer()
            self._poll.setInterval(POLL_MS)
            self._poll.timeout.connect(self._ask)
        self._poll.start()

    def stop_picks(self) -> None:
        if self._poll is not None:
            self._poll.stop()

    def _ask(self) -> None:
        if not self._ready or self._on_pick is None or self._asking:
            return
        self._asking = True
        self._view.page().runJavaScript(chart.grid_picks_js(), self._got_picks)

    def _got_picks(self, rows) -> None:
        self._asking = False
        for row in rows or []:
            try:
                index, ktype = int(row[0]), str(row[1])
            except (TypeError, ValueError, IndexError):
                continue
            self._on_pick(index, ktype)

    def _notify(self) -> None:
        if self.on_state is not None:
            self.on_state(self.error)

    def _on_loaded(self, ok: bool) -> None:
        if not ok:
            self.error = f"grid_load_failed: {chart.grid_page().name}"
            self._notify()
            return
        # 載體頁自己回報 ECharts、BrokeryChart 與 BrokeryGrid 是否可用：缺一樣即說明原因，不靠猜。
        self._view.page().runJavaScript("window.brokeryGridMissing || ''", self._on_probe)

    def _on_probe(self, missing) -> None:
        if missing:
            self.error = f"grid_js_missing: {missing}"
            self._notify()
            return
        self._ready = True
        self._notify()          # 載入成功：界面的「正在載入圖表」提示即應清走
        if self._build:
            call, self._build = self._build, ""
            self._view.page().runJavaScript(call)
        for call in list(self._notes.values()) + list(self._cells.values()):
            self._view.page().runJavaScript(call)
        self._notes.clear()
        self._cells.clear()


class GridChart:
    """一個多週期分頁對應一份格子：載體區、提示列、惰性建立與週期切換輪詢打包成可重用元件。

    界面只需在該頁有載體區（gridBox + gridNoteLabel）時建立一個，之後 build(ktypes) 排格、
    set_cell(序號, DataFrame) 逐格注入即可；載入中、載入失敗與缺 QtWebEngine 的原因一律由本元件
    寫進該頁的提示列，換語言時呼叫 note() 即照原樣重貼同一句。
    """

    def __init__(self, box: QWidget, note_label: QLabel, tr) -> None:
        self._box = box
        self._note = note_label
        self._tr = tr
        self._view: GridView | None = None

    @property
    def view(self) -> GridView | None:
        return self._view

    @property
    def error(self) -> str:
        return self._view.error if self._view is not None else ""

    @property
    def ready(self) -> bool:
        return self._view.ready if self._view is not None else False

    def ensure(self) -> GridView:
        """惰性建立渲染視圖：起不來即說明原因，而不是留一塊空白。"""
        if self._view is None:
            self._note.setText(self._tr("kline.chart_loading"))
            self._view = GridView(self._box, on_state=self.note)
            self.note(self._view.error)   # 無 QtWebEngine 時即時返回原因，唔會等載入
        return self._view

    def build(self, ktypes) -> None:
        self.note(self.ensure().build(ktypes))

    def set_cell(self, index: int, frame: pd.DataFrame, ktype: str | None = None) -> None:
        self.note(self.ensure().set_cell(index, frame, ktype))

    def note_cell(self, index: int, text: str) -> None:
        self.ensure().note_cell(index, text)

    def watch_picks(self, on_pick) -> None:
        self.ensure().picks(on_pick)

    def stop_picks(self) -> None:
        if self._view is not None:
            self._view.stop_picks()

    def note(self, detail: str = "") -> None:
        """載體頁的狀態即提示列的內容：載入成功即清走，失敗即說明原因；換語言時重貼同一句。"""
        if self._view is None:
            return
        reason = detail or self._view.error
        if reason:
            self._note.setText(self._tr("kline.chart_note", detail=reason))
        elif not self._view.ready:
            self._note.setText(self._tr("kline.chart_loading"))
        else:
            self._note.setText("")
