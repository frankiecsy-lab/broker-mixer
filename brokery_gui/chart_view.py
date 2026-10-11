"""K 線圖的渲染視圖：QWebEngineView 載入 brokery/static/chart_host.html，資料經 brokery.chart.render_js 注入。

之所以用 WebEngine 而不是 QtCharts：圖表規格只有一份 JS（static/chart.js），任何自定義指標（例如 ICT 的
order block）在三個界面看到的完全一樣，桌面端不需再寫一份 series 翻譯器。

视图惰性建立：只在首次進入 K 線圖分頁時載入。QtWebEngine 在無顯示環境（offscreen、部分 Docker 鏡像）可能
無法初始化，失敗時本模組返回明確原因，界面顯示文字而不是留一塊空白，下方的 DF 照常。
"""
from __future__ import annotations

import pandas as pd
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QWidget

from brokery import chart


class ChartView:
    """一個容器對應一個圖表視圖：render() 餵入 K 線，其餘（尺寸、座標軸、series）全由那份 JS 決定。"""

    def __init__(self, container: QWidget) -> None:
        self.error = ""
        self._ready = False
        self._pending = ""
        self._view = None
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView
        except Exception as exc:  # 無 QtWebEngine（或不在 QApplication 建立前匯入）
            self.error = f"webengine_missing: {exc}"
            return
        self._view = QWebEngineView(container)
        self._view.loadFinished.connect(self._on_loaded)
        self._view.load(QUrl.fromLocalFile(str(chart.host_page())))
        container.layout().addWidget(self._view)

    @property
    def ready(self) -> bool:
        return self._ready

    def render(self, frame: pd.DataFrame, ktype: str | None = None) -> str:
        """渲染一份 K 線；返回空字串即成功，否則返回未能顯示圖表的原因。"""
        if self._view is None:
            return self.error
        call = chart.render_js(frame, ktype=ktype)
        if not self._ready:
            # 載入未完成即注入會找不到 BrokeryChart：先留低最新一份，載入完成即補上。
            self._pending = call
            return ""
        self._view.page().runJavaScript(call)
        return ""

    def _on_loaded(self, ok: bool) -> None:
        if not ok:
            self.error = f"host_load_failed: {chart.host_page().name}"
            return
        # 載體頁自己回報 ECharts 與 BrokeryChart 是否可用：缺一樣即說明原因，不靠猜。
        self._view.page().runJavaScript("window.brokeryChartMissing || ''", self._on_probe)

    def _on_probe(self, missing) -> None:
        if missing:
            self.error = f"chart_js_missing: {missing}"
            return
        self._ready = True
        if self._pending:
            call, self._pending = self._pending, ""
            self._view.page().runJavaScript(call)
