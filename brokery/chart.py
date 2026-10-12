"""圖表層的唯一 Python 入口。

規格只有一份 JS（static/chart.js，連同一份本地 echarts.min.js），三個界面載入同一份：閘道面板與
Web UI 以 <script src> 載入，桌面 GUI 由 QWebEngineView 載入 static/chart_host.html 再注入資料。
用同一份 JS 而不寫第二份翻譯器，日後疊加自定義指標（如 ICT 的 order block）才三處一致。

多週期界面（一格一週期）另有一份 static/chart_grid.js：它只排格子與每格的週期按鈕，圖形仍由同一份
chart.js 畫（opts.compact），所以兩個界面的多週期頁走同一條路徑，載體頁為 static/chart_grid.html。

指標本身是資料：由 pandas 算出 brokers.base.OVERLAY_COLUMNS 的行，本模組只把 DataFrame 變成
chart.js 的輸入，不含任何繪圖或指標算法。
"""
from __future__ import annotations

import json
import math
from collections.abc import Iterable, Mapping
from pathlib import Path

import pandas as pd

from .brokers.base import OVERLAY_COLUMNS

STATIC_DIR = Path(__file__).resolve().parent / "static"
CHART_JS = "chart.js"
ECHARTS_JS = "echarts.min.js"
HOST_PAGE = "chart_host.html"
GRID_PAGE = "chart_grid.html"


def static_dir() -> Path:
    """靜態資源目錄（界面由此取 chart.js 與 echarts.min.js，嚴禁寫死路徑）。"""
    return STATIC_DIR


def static_file(name: str) -> Path:
    """靜態資源的完整路徑；只准取本目錄的檔案，避免被查詢參數走到上層目錄。"""
    path = (STATIC_DIR / name).resolve()
    if STATIC_DIR not in path.parents or not path.is_file():
        raise FileNotFoundError(f"static_missing: {name}")
    return path


def host_page() -> Path:
    """GUI 載體頁（不含文字、不取數），由 QWebEngineView 以本地檔案載入。"""
    return static_file(HOST_PAGE)


def grid_page() -> Path:
    """多週期載體頁（不含文字、不取數）：格子佈局在頁內，資料一律由外層注入。"""
    return static_file(GRID_PAGE)


def _safe(value):
    """DataFrame 的值 → JSON 可序列化。NaN/Inf 一律變 null：JS 收到 NaN 會靜靜畫錯而不是報錯。"""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if hasattr(value, "item"):  # numpy 標量
        return _safe(value.item())
    if isinstance(value, pd.Timestamp):
        return value.isoformat(sep=" ")
    return str(value)


def payload(frame: pd.DataFrame) -> dict:
    """K 線 DataFrame → chart.js 的輸入。一律帶 columns，避免以欄位順序猜語義。"""
    rows = frame.itertuples(index=False, name=None) if len(frame) else []
    return {"columns": [str(name) for name in frame.columns],
            "rows": [[_safe(value) for value in row] for row in rows]}


def frame(payload: Mapping) -> pd.DataFrame:
    """{"columns","rows"} → DataFrame，即 payload() 的反向。

    桌面 GUI 的序列合併在 Python 側（BarStore），渲染前要還原成 DataFrame 才交得到 render_js；
    欄位以 payload 帶的 columns 為準，不靠順序猜語義。
    """
    return pd.DataFrame(payload.get("rows") or [],
                       columns=[str(name) for name in (payload.get("columns") or [])])


def overlay_rows(overlays: pd.DataFrame | Iterable[Mapping] | None) -> list[dict]:
    """疊加指標 → chart.js 的 rows（欄位即 OVERLAY_COLUMNS）。無指標時為空列表。"""
    if overlays is None or (isinstance(overlays, pd.DataFrame) and overlays.empty):
        return []
    if isinstance(overlays, pd.DataFrame):
        items = (dict(zip(overlays.columns, row))
                 for row in overlays.itertuples(index=False, name=None))
    else:
        items = overlays
    rows = []
    for item in items:
        row = {name: _safe(item.get(name)) for name in OVERLAY_COLUMNS}
        rows.append(row)
    return rows


REQUIRED = ("ts", "open", "high", "low", "close")


def _ts(value):
    """ts → 可比較的數值；取不到即 None（缺時間的 bar 無從排進序列，寧可丟掉也不憑空補）。"""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


class BarStore:
    """序列合併：key = (code, ts)，新到者覆蓋同 ts 者，每個代碼只保留最新 limit 根，內部一律升序。

    與 static/chart.js 的 store() 同一口徑：串流每次 update 只帶該代碼最近 count 根，直接覆蓋會把已取得的
    1000 根歷史縮返最近幾十根。欄位順序取最近一次輸入者，還原時照原欄位（含 time_str、source），界面顯示
    的 DF 與接口返回的一致；「最新在最上」屬顯示層，這裡不做反序。
    """

    def __init__(self, limit: int = 1000) -> None:
        self.limit = limit
        self._kept: dict[tuple[str, float], list] = {}
        self._columns: list[str] = []

    @property
    def size(self) -> int:
        return len(self._kept)

    def clear(self) -> None:
        self._kept.clear()

    def add(self, payload: Mapping) -> None:
        """併入一份 {"columns","rows"}；缺 OHLC 欄位即原樣忽略（不是把不完整的序列混進來）。"""
        columns = [str(name) for name in (payload.get("columns") or [])]
        if not columns:
            return
        at = {name: index for index, name in enumerate(columns)}
        if any(name not in at for name in REQUIRED):
            return
        self._columns = columns
        for row in payload.get("rows") or []:
            stamp = _ts(row[at["ts"]])
            if stamp is None:
                continue
            code = str(row[at["code"]]) if "code" in at else ""
            self._kept[(code, stamp)] = list(row)
        self._trim()

    def set_limit(self, limit: int) -> None:
        """改上限並即刻按新上限裁剪：上限須跟隨界面請求的根數，否則取 3000 根會被裁返 1000。"""
        self.limit = max(1, int(limit))
        self._trim()

    def _trim(self) -> None:
        by_code: dict[str, list[float]] = {}
        for code, stamp in self._kept:
            by_code.setdefault(code, []).append(stamp)
        for code, stamps in by_code.items():
            for stamp in sorted(stamps)[: max(0, len(stamps) - self.limit)]:
                del self._kept[(code, stamp)]

    def payload(self) -> dict:
        """合併後的序列 → {"columns","rows"}，按 ts 升序（圖表與跨券商對齊靠升序）。"""
        rows = [self._kept[key] for key in sorted(self._kept, key=lambda key: (key[1], key[0]))]
        return {"columns": self._columns, "rows": rows}


def render_js(frame: pd.DataFrame, overlays: pd.DataFrame | Iterable[Mapping] | None = (), *,
              element: str = "chart", ktype: str | None = None,
              start: float | None = None, end: float | None = None) -> str:
    """產生餵俾 QWebEngineView.runJavaScript 嘅呼叫；ktype 只影響時間軸嘅顯示格式。

    start/end 為縮放滑桿的初始窗口（百分比）。省略時沿用 chart.js 的預設（只顯示最近一段），
    傳 start=0 即顯示全部已取得的根數；兩者只影響初始視圖，不改變餵入的資料。
    """
    options: dict = {}
    if ktype:
        options["ktype"] = ktype
    if start is not None:
        options["start"] = start
    if end is not None:
        options["end"] = end
    return ("BrokeryChart.render(document.getElementById({el}), {bars}, {overlays}, {options})"
            .format(el=json.dumps(element), bars=json.dumps(payload(frame), ensure_ascii=False),
                    overlays=json.dumps(overlay_rows(overlays), ensure_ascii=False),
                    options=json.dumps(options, ensure_ascii=False)))


def grid_js(ktypes: Iterable[str], *, element: str = "grid") -> str:
    """建立多週期格子的呼叫：一格一週期，順序照傳入者（即 /capabilities 的 stream_ktypes），本函數不排序。

    載體頁只有一個容器，故把格子記在 window.brokeryGrid：後續注入只需要呼叫 grid_set_js，不需要再傳元素。
    """
    return ("window.brokeryGrid = BrokeryGrid.build(document.getElementById({el}), {options})"
            .format(el=json.dumps(element),
                    options=json.dumps({"ktypes": [str(k) for k in ktypes]}, ensure_ascii=False)))


def grid_set_js(index: int, frame: pd.DataFrame, ktype: str | None = None,
                overlays: pd.DataFrame | Iterable[Mapping] | None = ()) -> str:
    """只重畫一格：序號由界面維持（即該週期在格子清單中的位置），ktype 只影響時間軸的顯示格式。

    ktype 傳 None 即沿用該格現有週期（串流更新就是這種情況，格子自己記住是哪一个週期）。
    """
    return ("window.brokeryGrid && window.brokeryGrid.set({index}, {bars}, {ktype}, {overlays})"
            .format(index=int(index), bars=json.dumps(payload(frame), ensure_ascii=False),
                    ktype=json.dumps(ktype, ensure_ascii=False) if ktype else "null",
                    overlays=json.dumps(overlay_rows(overlays), ensure_ascii=False)))


def grid_note_js(index: int, text: str) -> str:
    """在某格顯示一行提示（例如該週期的串流名額尚未釋放）；文字由界面的字庫提供，載體頁本身不含文字。"""
    return ("window.brokeryGrid && window.brokeryGrid.note({index}, {text})"
            .format(index=int(index), text=json.dumps(str(text), ensure_ascii=False)))


def grid_picks_js() -> str:
    """取走格子上被按下的週期切換，返回 [[序號, ktype], ...] 並即刻清空。

    桌面 GUI 用輪詢而不是回調：QWebChannel 在離屏（offscreen）載入下會令 WebEngine 崩潰。
    """
    return "window.brokeryGrid ? window.brokeryGrid.takePicks() : []"
