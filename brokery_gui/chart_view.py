"""K 線圖的渲染視圖：QWebEngineView 載入 brokery/static/chart_host.html，資料經 brokery.chart.render_js 注入。

之所以用 WebEngine 而不是 QtCharts：圖表規格只有一份 JS（static/chart.js），任何自定義指標（例如 ICT 的
order block）在三個界面看到的完全一樣，桌面端不需再寫一份 series 翻譯器。

KlineChart 是界面用的元件：一個有圖表區（chartBox）的分頁各持一個，載入、提示與失敗原因都在元件內部，
界面只在取得序列後交一份 DataFrame。視圖惰性建立：QtWebEngine 在無顯示環境（offscreen、部分 Docker 鏡像）
可能無法初始化，失敗時返回明確原因，界面顯示文字而不是留一塊空白，下方的 DF 照常。
"""
from __future__ import annotations

import pandas as pd
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget

from brokery import chart


class ChartView:
    """一個容器對應一個圖表視圖：render() 餵入 K 線，其餘（尺寸、座標軸、series）全由那份 JS 決定。

    on_state(原因) 為狀態回調：載入成功傳空字串、失敗傳原因。界面據此顯示或清走「正在載入圖表」的提示，
    故提示只屬狀態，唔使由界面去猜載入好未。
    """

    def __init__(self, container: QWidget, on_state=None) -> None:
        self.error = ""
        self.on_state = on_state
        self._ready = False
        self._pending = ""
        self._view = None
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
        except Exception as exc:  # 無 QtWebEngine（或不在 QApplication 建立前匯入）
            self.error = f"webengine_missing: {exc}"
            return
        self._view = QWebEngineView(container)
        # 圖要佔盡容器：QVBoxLayout 對 Preferred 的元件會同提示列各分一半，故明確標為 Expanding 並俾 stretch。
        self._view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._view.loadFinished.connect(self._on_loaded)
        self._view.load(QUrl.fromLocalFile(str(chart.host_page())))
        container.layout().addWidget(self._view, 1)

    @property
    def ready(self) -> bool:
        return self._ready

    def render(self, frame: pd.DataFrame, ktype: str | None = None, *,
               start: float | None = None, end: float | None = None) -> str:
        """渲染一份 K 線；返回空字串即成功，否則返回未能顯示圖表的原因。

        start/end 為縮放滑桿的初始窗口（百分比），只影響初始視圖；省略即沿用 chart.js 的預設。
        """
        if self._view is None:
            return self.error
        call = chart.render_js(frame, ktype=ktype, start=start, end=end)
        if not self._ready:
            # 載入未完成即注入會找不到 BrokeryChart：先留低最新一份，載入完成即補上。
            self._pending = call
            return ""
        self._view.page().runJavaScript(call)
        return ""

    def _notify(self) -> None:
        if self.on_state is not None:
            self.on_state(self.error)

    def _on_loaded(self, ok: bool) -> None:
        if not ok:
            self.error = f"host_load_failed: {chart.host_page().name}"
            self._notify()
            return
        # 載體頁自己回報 ECharts 與 BrokeryChart 是否可用：缺一樣即說明原因，不靠猜。
        self._view.page().runJavaScript("window.brokeryChartMissing || ''", self._on_probe)

    def _on_probe(self, missing) -> None:
        if missing:
            self.error = f"chart_js_missing: {missing}"
            self._notify()
            return
        self._ready = True
        self._notify()          # 載入成功：界面的「正在載入圖表」提示即應清走
        if self._pending:
            call, self._pending = self._pending, ""
            self._view.page().runJavaScript(call)


class KlineChart:
    """一個 K 線分頁對應一張圖：圖表區、提示列與惰性渲染視圖打包成可重用元件。

    界面只需在該頁有圖表區（chartBox + chartNoteLabel）時建立一個，之後交一份 DataFrame 即可；
    載入中、載入失敗與缺 QtWebEngine 的原因一律由本元件寫進該頁的提示列（提示由狀態驅動，界面不
    用猜載入好未），換語言時呼叫 note() 即照原樣重貼同一句。
    """

    def __init__(self, box: QWidget, note_label: QLabel, tr) -> None:
        self._box = box
        self._note = note_label
        self._tr = tr
        self._view: ChartView | None = None

    @property
    def view(self) -> ChartView | None:
        return self._view

    @property
    def error(self) -> str:
        return self._view.error if self._view is not None else ""

    @property
    def ready(self) -> bool:
        return self._view.ready if self._view is not None else False

    def ensure(self) -> ChartView:
        """惰性建立渲染視圖：起不來即說明原因，而不是留一塊空白（下方的 DF 照常）。"""
        if self._view is None:
            self._note.setText(self._tr("kline.chart_loading"))
            self._view = ChartView(self._box, on_state=self.note)
            self.note(self._view.error)   # 無 QtWebEngine 時即時返回原因，唔會等載入
        return self._view

    def render(self, frame: pd.DataFrame, ktype: str | None = None) -> None:
        """渲染一份 K 線：初始窗口取 0，即所請求的根數全部喺圖上（縮放滑桿照可再收窄）。"""
        self.note(self.ensure().render(frame, ktype=ktype, start=0))

    def note(self, detail: str = "") -> None:
        """圖表的狀態即提示列的內容：載入成功即清走，失敗即說明原因；換語言時重貼同一句。"""
        if self._view is None:
            return
        reason = detail or self._view.error
        if reason:
            self._note.setText(self._tr("kline.chart_note", detail=reason))
        elif not self._view.ready:
            self._note.setText(self._tr("kline.chart_loading"))
        else:
            self._note.setText("")
