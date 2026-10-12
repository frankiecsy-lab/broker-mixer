"""驗收共用圖表層：brokery/static/chart.js（唯一一份規格）與 brokery/chart.py（Python 入口）。

* Python 側：payload() 帶 columns 且保持 ts 升序（core 的契約）、NaN/Inf 變 null、overlay_rows()
  按 OVERLAY_COLUMNS 補齊欄位、render_js() 為可直接執行的呼叫、static_file() 不可走到 static 之外；
* 載體頁：本地 echarts.min.js 可用（無 CDN，故 GUI 與 Docker 離線都畫到圖）；
* x 軸的資料一律是原始 ts（UTC 秒），時間文字只由 formatter 產生 —— 這是疊加指標能對齊 bar 的前提；
* option() 產生 candlestick + 成交量兩條 series；疊加指標按行的 kind 分派，內置 zone/line，
  register 新的 kind 即多一條 series，未註冊的 kind 略過而不影響圖；
* store() 的合併規則：key=(code,ts)、同 ts 以新到者覆蓋、每個代碼只保留最新 N 根（串流的 update
  只帶最近 count 根，直接覆蓋會把 1000 根歷史縮返 60 根），N 由 setLimit() 跟界面請求的根數調整
  （寫死時取 3000 根會被裁返 1000 根），合併後的序列以 payload() 還原成 {columns, rows}，
  界面下方的 DF 照原欄位顯示；rowsDesc()/desc() 只屬顯示層的反序；
* render() 每次都把規格（ktype）交落該實例的 update：圖形規格屬該次輸入的一部分，只喺開圖時給一次的話，
  界面換週期後 x 軸仍照舊週期格式；同一元素重入仍取返同一個實例（換標的唔會疊加舊圖）；
* create(el, opts) 實例：一格即一實例，縮放與平移的範圍由實例自己記住，故下一次 update（串流每次都會送）
  不會跳回原位。交互以真滾輪與真拖曳驅動：滾輪縮 X 軸、Shift+滾輪只縮 Y 軸（單軸）、拖曳左右平移、
  雙擊復原；現價水平線與右上角現價大字一律取序列最後一根的收盤價，因此串流更新時兩者自己移動，
  界面不需要另外傳值；大字只在現價真的改變時閃爍一次（首次載入與重複繪製同一價格均不閃），
  計時由實例負責（本圖 animation 為 false）；兩個 y 軸均不繪水平網格線，最新一根 K 線右側保留空間；
* opts.compact（多週期界面：一格一週期、一屏九格）只畫價格格：不生成成交量 series、第二格與右上角現價大字，
  留位與字號收細，但 dataZoom 的索引不變（0 為 X、1 為 Y），故 create() 的滾輪分派不需要按模式分支；
* static/chart_grid.js 的 BrokeryGrid：格子清單一律由界面傳入（即券商聲明的 stream_ktypes，本檔不排列），
  一格即一個 chart.js 實例（各自記住縮放），每格上方一排水平週期按鈕且只高亮自己嗰個；頁內零界面文字
  （按鈕只有 ktype 代號，換語言不需要重建格子），提示由 note() 送入；撳按鈕只經 takePicks() 上報
  「哪一格要轉哪個週期」（桌面 GUI 輪詢取走），set() 只重畫一格、省略 ktype 即沿用該格現有週期。

以腳本方式直接執行：
    python brokery/acceptance/run_chart_spec.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import pandas as pd

from brokery import chart
from brokery.brokers.base import K_COLUMNS, KTYPE_ORDER, OVERLAY_COLUMNS

BASE_TS = 1_760_000_000
LIMIT = 1000


def kframe(start_index: int, count: int, close_at) -> pd.DataFrame:
    rows = []
    for n in range(count):
        i = start_index + n
        rows.append(["HK.HSImain", BASE_TS + i * 60, "2026-10-09 09:30:00", 100.0, 101.0, 99.0,
                     close_at(i), 10 + n, 1000.0, "futu"])
    return pd.DataFrame(rows, columns=K_COLUMNS)


def main() -> dict:
    checks: list[tuple[str, bool, str]] = []

    def check(label: str, passed: bool, detail: str = "") -> None:
        checks.append((label, bool(passed), str(detail)))

    # ---------- Python 入口 ----------
    history = kframe(0, LIMIT, lambda i: float(100 + i))
    payload = chart.payload(history)
    ts_at = payload["columns"].index("ts")
    check("payload 帶 columns 且保持 ts 升序（core 契約，反序只屬顯示層）",
          payload["columns"] == K_COLUMNS and
          [r[ts_at] for r in payload["rows"]] == sorted(r[ts_at] for r in payload["rows"])
          and len(payload["rows"]) == LIMIT, f"{len(payload['rows'])} 根 {payload['columns'][:3]}")

    with_nan = kframe(0, 2, lambda i: float("nan"))
    check("NaN/Inf 一律變 null（JS 收到 NaN 會靜靜畫錯而不是報錯）",
          chart.payload(with_nan)["rows"][0][payload["columns"].index("close")] is None,
          str(chart.payload(with_nan)["rows"][0]))

    zone = {"code": "HK.HSImain", "kind": "zone", "name": "OB", "start_ts": BASE_TS + 60,
            "end_ts": BASE_TS + 120, "start_price": 1.5, "end_price": 2.4, "side": "bull"}
    rows = chart.overlay_rows(pd.DataFrame([dict.fromkeys(OVERLAY_COLUMNS, None) | zone]))
    check("overlay_rows 按 OVERLAY_COLUMNS 補齊欄位（缺值為 null，不憑空猜）",
          list(rows[0]) == OVERLAY_COLUMNS and rows[0]["name"] == "OB"
          and chart.overlay_rows(None) == [] and chart.overlay_rows(pd.DataFrame()) == [],
          str(rows[0]))

    call = chart.render_js(history, [zone], ktype="1m")
    check("render_js 產生可直接執行的呼叫（GUI 只 runJavaScript）",
          call.startswith('BrokeryChart.render(document.getElementById("chart"), {"columns"')
          and '"kind": "zone"' in call and '"ktype": "1m"' in call, f"{len(call)} 字節")

    # 初始窗口由調用方決定：桌面 GUI 傳 start=0，即所請求的根數全部喺圖上，唔係只顯最近幾十根。
    widened = chart.render_js(history, ktype="1m", start=0, end=100)
    check("render_js 把調用方給的初始窗口交俾 chart.js；省略時不帶該項（沿用 chart.js 的預設）",
          '"ktype": "1m"' in widened and '"start": 0' in widened and '"end": 100' in widened
          and '"start"' not in call and '"end"' not in call, widened[-60:])

    try:
        chart.static_file("../core.py")
        escaped = True
    except FileNotFoundError:
        escaped = False
    check("static_file 只准取 static 目錄內的檔案（多週期的 chart_grid.js/html 同樣受管）",
          not escaped and chart.static_file("chart.js").is_file()
          and chart.static_file("chart_grid.js").is_file()
          and chart.host_page().name == "chart_host.html"
          and chart.grid_page().name == "chart_grid.html", "上層目錄被拒")

    # 多週期界面：格子清單即 /capabilities 返回的 stream_ktypes，順序照返回者（base.py 的契約），本模組不排序。
    build_call = chart.grid_js(KTYPE_ORDER)
    check("grid_js 照傳入順序建立格子（不自行排列週期），載體頁只有一個容器故記喺 window.brokeryGrid",
          build_call == ('window.brokeryGrid = BrokeryGrid.build(document.getElementById("grid"), '
                         '{"ktypes": ["1m", "3m", "5m", "15m", "30m", "60m", "day", "week", "month"]})'),
          build_call[:70])
    one_cell = chart.grid_set_js(3, kframe(0, 2, lambda i: 1.0))
    check("grid_set_js 只重畫一格：序號由界面維持；ktype 省略即傳 null（串流更新唔使再報週期）",
          one_cell.startswith("window.brokeryGrid && window.brokeryGrid.set(3, {\"columns\"")
          and one_cell.endswith(", null, [])")
          and chart.grid_set_js(3, kframe(0, 2, lambda i: 1.0), "day").endswith(', "day", [])')
          and chart.grid_note_js(2, "名額未釋放").endswith('note(2, "名額未釋放")')
          and chart.grid_picks_js() == "window.brokeryGrid ? window.brokeryGrid.takePicks() : []",
          one_cell[:70])

    # 桌面 GUI 的序列合併在 Python 側（BarStore），渲染前要 frame() 還原成 DataFrame 先交得到 render_js。
    store = chart.BarStore(limit=LIMIT)
    store.add(payload)
    store.add(chart.payload(kframe(LIMIT - 70, 80, lambda i: 9999.0)))
    back = chart.frame(store.payload())
    check("frame() 還原 BarStore 的序列成 DataFrame（GUI 的圖表與表格同一份序列）",
          list(back.columns) == K_COLUMNS and len(back) == LIMIT
          and int(back["ts"].iloc[-1]) == BASE_TS + (LIMIT + 9) * 60
          and float(back["close"].iloc[-1]) == 9999.0, f"{len(back)} 根")

    # ---------- 載體頁與規格（真 ECharts，不驗像素） ----------
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(args=["--no-sandbox"])
        try:
            page = browser.new_page()
            page.goto(chart.host_page().as_uri(), timeout=30_000)
            page.wait_for_function("window.brokeryChartReady !== undefined", timeout=15_000)
            check("載體頁以本地 echarts.min.js 載入成功（無 CDN，離線可用）",
                  page.evaluate("window.brokeryChartReady") is True
                  and page.evaluate("window.brokeryChartMissing") == ""
                  and page.evaluate("echarts.version").startswith("5."),
                  f"echarts {page.evaluate('echarts.version')}")

            option = page.evaluate("([p]) => BrokeryChart.option(p, null, {ktype: '1m'})", [payload])
            kinds = [s["type"] for s in option["series"]]
            check("option() 產生 candlestick + 成交量兩條 series（價格 62% / 成交量 18%）",
                  kinds == ["candlestick", "bar"] and option["series"][1]["xAxisIndex"] == 1
                  and len(option["grid"]) == 2 and option["series"][0]["data"][0] == [100.0, 100.0, 99.0, 101.0],
                  f"{kinds} {option['series'][0]['data'][0]}")
            # 格線與留位屬圖表可讀性：K 線與成交量本身已是密集的豎向資料，橫線只會壓住讀勢；
            # 最新一根唔該貼住右邊界（現價大字就放喺呢條右邊界上面）。
            check("兩格都唔畫 Y 軸的水平格線，最新一根 bar 右邊留位（兩格右邊界一致，先至睇得齊）",
                  all(axis["splitLine"]["show"] is False for axis in option["yAxis"])
                  and len(option["grid"]) == 2 and option["grid"][0]["right"] >= 60
                  and option["grid"][1]["right"] == option["grid"][0]["right"],
                  f"{option['grid']}|{[a.get('splitLine') for a in option['yAxis']]}")

            # 緊湊模式（多週期界面：一格一週期、一屏九格）：只畫價格格，其餘一概唔生成；非緊湊時上面完全唔變。
            tight = page.evaluate("([p]) => BrokeryChart.option(p, null, {ktype: '1m', compact: true})", [payload])
            check("compact：只畫價格格（一條 series、一個 grid、無成交量、無右上角大字），留位與字號一併收細",
                  [s["type"] for s in tight["series"]] == ["candlestick"] and len(tight["grid"]) == 1
                  and len(tight["xAxis"]) == 1 and len(tight["yAxis"]) == 1 and tight["graphic"] == []
                  and tight["grid"][0]["right"] < option["grid"][0]["right"]
                  and tight["xAxis"][0]["axisLabel"]["fontSize"] < option["xAxis"][0]["axisLabel"]["fontSize"]
                  and tight["series"][0]["markLine"]["label"]["fontSize"]
                      < option["series"][0]["markLine"]["label"]["fontSize"],
                  f"{[s['type'] for s in tight['series']]} {tight['grid']}")
            check("compact 的 dataZoom 索引不變（0 為 X、1 為 Y）：故 create() 的滾輪分派唔使按模式分支",
                  len(tight["dataZoom"]) == 2 and tight["dataZoom"][0]["xAxisIndex"] == [0]
                  and tight["dataZoom"][1]["yAxisIndex"] == 0, str(tight["dataZoom"]))

            check("x 軸的資料是原始 ts（時間文字只由 formatter 產生，疊加指標才對得準）",
                  [int(v) for v in option["xAxis"][0]["data"]][:3] == [BASE_TS, BASE_TS + 60, BASE_TS + 120]
                  and page.evaluate("([p]) => typeof BrokeryChart.option(p, null, {})"
                                   ".xAxis[0].axisLabel.formatter", [payload]) == "function",
                  str(option["xAxis"][0]["data"][:3]))

            marked = page.evaluate("([p,o]) => BrokeryChart.option(p, o, {}).series[0].markArea",
                                  [payload, [zone]])
            check("內置 zone：OVERLAY_COLUMNS 的行變成 markArea（矩形即區間）",
                  marked and len(marked["data"]) == 1
                  and marked["data"][0][0]["xAxis"] == str(BASE_TS + 60)
                  and marked["data"][0][0]["yAxis"] == 1.5
                  and marked["data"][0][1]["xAxis"] == str(BASE_TS + 120), str(marked))

            outside = page.evaluate(
                "([p,o]) => BrokeryChart.option(p, o, {}).series[0].markArea.data[0][0].xAxis",
                [payload, [dict(zone, start_ts=BASE_TS - 10_000, end_ts=BASE_TS + 90_000)]])
            check("區間端點喺範圍外即貼到最接近嘅一根（唔會整塊指標消失）",
                  outside == str(BASE_TS), str(outside))

            registered = page.evaluate(
                "([p, row]) => { BrokeryChart.overlays.register('fvg', (rows, ctx) => ({series: rows.map("
                "(r) => ({type: 'line', name: r.name, data: [[ctx.at(r.start_ts), r.start_price], "
                "[ctx.at(r.end_ts), r.end_price]]}))})); "
                "const o = BrokeryChart.option(p, [row], {}); "
                "return {types: o.series.map((s) => s.type), names: o.series.map((s) => s.name), "
                "kinds: BrokeryChart.overlays.kinds()}; }",
                [payload, dict(zone, kind="fvg", name="FVG", start_price=1.0, end_price=2.0)])
            check("overlays.register 即掛點：新 kind 多一條 series，三處自動一樣",
                  registered["types"] == ["candlestick", "bar", "line"]
                  and registered["names"][2] == "FVG" and "fvg" in registered["kinds"],
                  str(registered))

            ignored = page.evaluate("([p]) => BrokeryChart.option(p, [{kind: 'nope'}], {}).series.length",
                                    [payload])
            check("未註冊的 kind 略過：圖照畫，唔會因為未知指標而空白", ignored == 2, f"{ignored} 條 series")

            merged = page.evaluate(
                "([a, b, limit]) => { const s = BrokeryChart.store(limit); s.add(a); const first = s.size; "
                "s.add(b); const bars = s.bars(); return {first, size: s.size, oldest: bars[0].ts, "
                "newest: bars[bars.length - 1], overwritten: bars.filter((x) => x.close === 9999).length, "
                "descFirst: s.rowsDesc()[0].ts}; }",
                [payload, chart.payload(kframe(LIMIT - 70, 80, lambda i: 9999.0)), LIMIT])
            check("store() 合併：同 ts 覆蓋、保留最新 N 根、內部升序（串流唔會把 1000 根縮返 60 根）",
                  merged["first"] == LIMIT and merged["size"] == LIMIT
                  and merged["oldest"] == BASE_TS + 10 * 60 and merged["overwritten"] == 80
                  and merged["newest"]["ts"] == BASE_TS + (LIMIT + 9) * 60, str(merged))
            restored = page.evaluate(
                "([a, b, limit]) => { const s = BrokeryChart.store(limit); s.add(a); s.add(b); "
                "const p = s.payload(); return {cols: p.columns, oldest: p.rows[0], "
                "newest: BrokeryChart.desc(p).rows[0]}; }",
                [payload, chart.payload(kframe(LIMIT - 70, 80, lambda i: 9999.0)), LIMIT])
            at = {name: index for index, name in enumerate(K_COLUMNS)}
            check("store().payload() 還原 {columns, rows}：界面 DF 顯示原欄位（含 time_str、source）",
                  restored["cols"] == K_COLUMNS and len(restored["oldest"]) == len(K_COLUMNS)
                  and restored["oldest"][at["ts"]] == BASE_TS + 10 * 60
                  and restored["oldest"][at["source"]] == "futu"
                  and restored["newest"][at["ts"]] == BASE_TS + (LIMIT + 9) * 60
                  and restored["newest"][at["close"]] == 9999.0,
                  f"{restored['cols'][:3]}… {restored['oldest'][:3]}")
            check("rowsDesc()/desc() 只屬顯示層：最新在最上，原序不變",
                  merged["descFirst"] == merged["newest"]["ts"]
                  and page.evaluate("([p]) => BrokeryChart.desc(p).rows[0][1]", [payload]) ==
                      BASE_TS + (LIMIT - 1) * 60
                  and page.evaluate("([p]) => BrokeryChart.option(p, null, {}).xAxis[0].data[0]",
                                   [payload]) == str(BASE_TS),
                  f"descFirst={merged['descFirst']}")

            # 上限要跟界面請求的根數：寫死 1000 時取 3000 根會被裁返 1000 根（與 Python 側 BarStore.set_limit 同一口徑）。
            raised = page.evaluate(
                "([a, deep]) => { const s = BrokeryChart.store(1000); s.add(a); const capped = s.size; "
                "const limit = s.setLimit(3000); s.add(deep); const full = {size: s.size, oldest: s.bars()[0].ts}; "
                "const shrunk = s.setLimit(10); return {capped, limit, full, shrunk, kept: s.size, "
                "newest: s.bars()[s.size - 1].ts}; }",
                [payload, chart.payload(kframe(LIMIT, 2000, lambda i: 9999.0))])
            check("store().setLimit()：上限跟界面請求的根數（取 3000 根唔會被裁返 1000），調低即裁走最舊",
                  raised["capped"] == LIMIT and raised["limit"] == 3000
                  and raised["full"] == {"size": 3000, "oldest": BASE_TS}
                  and raised["shrunk"] == 10 and raised["kept"] == 10
                  and raised["newest"] == BASE_TS + (LIMIT + 1999) * 60, str(raised))

            drawn = page.evaluate(
                "([p]) => { const el = document.getElementById('chart'); "
                "const c = BrokeryChart.render(el, p, null, {ktype: '1m'}); "
                "return {same: c === echarts.getInstanceByDom(el), "
                "series: echarts.getInstanceByDom(el).getOption().series.length, "
                "canvas: Boolean(el.querySelector('canvas'))}; }", [payload])
            check("render() 真畫到嘢：同一個實例可重用（換標的唔會疊加舊圖）",
                  drawn["same"] and drawn["series"] == 2 and drawn["canvas"], str(drawn))

            # 規格屬該次輸入的一部分：界面換週期係透過同一個 render() 重入，所以 ktype 要每次照樣交落去。
            relabel = page.evaluate(
                "([p]) => { const el = document.getElementById('chart');"
                "const a = BrokeryChart.render(el, p, null, {ktype: '1m'});"
                "const minute = a.getOption().xAxis[0].axisLabel.formatter(1760000000);"
                "const b = BrokeryChart.render(el, p, null, {ktype: 'day'});"
                "return {reused: a === b, minute, daily: b.getOption().xAxis[0].axisLabel.formatter(1760000000)}; }",
                [payload])
            check("render() 每次帶規格：換週期後 x 軸格式跟住改（只喺開圖時給一次即永遠照舊週期）",
                  relabel["reused"] and " " in relabel["minute"] and ":" in relabel["minute"]
                  and len(relabel["daily"]) == 10 and " " not in relabel["daily"]
                  and relabel["daily"].count("-") == 2, str(relabel))

            # ---------- 實例（create）：縮放、平移、雙擊復原、現價線 ----------
            # 界面一張圖即一個實例（K 線串流頁表格上方的圖即如此），故呢一段驗嘅係實際會發生嘅操作。
            made = page.evaluate(
                "([p]) => { const el = document.createElement('div');"
                "el.style.cssText = 'width:420px;height:300px'; document.body.appendChild(el);"
                "const host = document.getElementById('chart');"
                "window.pa = BrokeryChart.create(host, {ktype: '1m'}); window.pb = BrokeryChart.create(el, {ktype: '1m'});"
                "window.pa.update(p); window.pb.update(p);"
                "return {reuse: BrokeryChart.create(host).echarts === echarts.getInstanceByDom(host),"
                " own: window.pa !== window.pb, base: window.pa.view(), other: window.pb.view(),"
                " canvas: Boolean(host.querySelector('canvas')) && Boolean(el.querySelector('canvas')),"
                " series: echarts.getInstanceByDom(host).getOption().series.length}; }", [payload])
            check("create() 一張圖即一實例：各自畫圖、各自記範圍（兩張圖互不影響）",
                  made["reuse"] and made["own"] and made["canvas"] and made["series"] == 2
                  and made["base"] == {"start": 60, "end": 100, "yStart": 0, "yEnd": 100}
                  and made["other"] == made["base"], str(made))

            # 初始窗口由調用方給：桌面 GUI 傳 start: 0，即所請求的根數全部喺圖上（根數可任選先有意義）。
            widened = page.evaluate(
                "([p]) => { const el = document.createElement('div');"
                "el.style.cssText = 'width:420px;height:300px'; document.body.appendChild(el);"
                "const pc = BrokeryChart.create(el, {ktype: '1m', start: 0}); pc.update(p);"
                "return {view: pc.view(), bars: pc.echarts.getOption().series[0].data.length}; }", [payload])
            check("create() 照調用方給的初始窗口開圖：start: 0 即全部根數喺圖上（省略時仍只顯最近一段）",
                  widened["view"]["start"] == 0 and widened["view"]["end"] == 100
                  and widened["bars"] == LIMIT, str(widened))

            # 縮放與平移以真滾輪、真拖曳驅動（唔係直接改 option）：要驗嘅係界面實際會發生嘅操作。
            box = page.evaluate("() => { const r = document.getElementById('chart').getBoundingClientRect();"
                                "return {x: r.x + r.width / 2, y: r.y + r.height * 0.3}; }")
            page.mouse.move(box["x"], box["y"])
            page.mouse.wheel(0, -600)
            zoom_x = page.evaluate("() => window.pa.view()")
            kept = page.evaluate("([p]) => { window.pa.update(p); const z = window.pa.echarts.getOption().dataZoom;"
                                 "return {view: window.pa.view(), painted: {start: z[0].start, end: z[0].end}}; }",
                                [payload])
            check("滾輪縮放只改 X 軸，範圍由實例記住：下一次 update（串流每次都會送）唔會跳返原位",
                  zoom_x["end"] - zoom_x["start"] != made["base"]["end"] - made["base"]["start"]
                  and kept["view"] == zoom_x and kept["painted"] == {"start": zoom_x["start"],
                                                                     "end": zoom_x["end"]}
                  and page.evaluate("() => window.pb.view()") == made["base"], str([zoom_x, kept]))

            page.keyboard.down("Shift")
            page.mouse.wheel(0, -400)
            page.keyboard.up("Shift")
            zoom_y = page.evaluate("() => window.pa.view()")
            check("Shift+滾輪只縮 Y 軸（單軸縮小）：X 軸範圍完全唔郁",
                  (zoom_y["start"], zoom_y["end"]) == (zoom_x["start"], zoom_x["end"])
                  and (zoom_y["yStart"], zoom_y["yEnd"]) != (zoom_x["yStart"], zoom_x["yEnd"]), str(zoom_y))

            page.mouse.move(box["x"] - 150, box["y"])
            page.mouse.down()
            page.mouse.move(box["x"] + 150, box["y"], steps=10)
            page.mouse.up()
            panned = page.evaluate("() => window.pa.view()")
            # 寬度係由 ECharts 按像素換算，故只可比較到容差（實測差 1e-14 級），唔使為跑綠改圖。
            check("拖曳即左右平移：範圍整體郁而寬度唔變（唔會變成縮放）",
                  abs((panned["end"] - panned["start"]) - (zoom_y["end"] - zoom_y["start"])) < 1e-6
                  and panned["start"] != zoom_y["start"], str([zoom_y, panned]))

            page.mouse.dblclick(box["x"], box["y"])
            restored = page.evaluate("() => window.pa.view()")
            check("雙擊即復原：X 軸返預設範圍、Y 軸取消單軸縮小", restored == made["base"], str(restored))

            line = page.evaluate(
                "([p, falling]) => { const at = (o) => o.series[0].markLine;"
                "const up = at(BrokeryChart.option(p, null, {ktype: '1m'}));"
                "const down = at(BrokeryChart.option(falling, null, {}));"
                "return {price: up.data[0].yAxis, color: up.lineStyle.color, text: up.label.formatter(),"
                " type: up.lineStyle.type, downPrice: down.data[0].yAxis, downColor: down.lineStyle.color,"
                " empty: BrokeryChart.option({columns: ['ts','open','high','low','close'], rows: []}, null, {})"
                ".series[0].markLine === undefined}; }",
                [payload, chart.payload(kframe(0, 5, lambda i: 90.0 if i == 4 else 100.0))])
            check("現價水平線：一律取序列最後一根的收市價（升紅跌綠、虛線、標籤即價格），無資料時唔畫",
                  line["price"] == 100.0 + LIMIT - 1 and line["color"] == "#e0524a"
                  and line["text"] == f"{100.0 + LIMIT - 1:.2f}" and line["type"] == "dashed"
                  and line["downPrice"] == 90.0 and line["downColor"] == "#2ea36f" and line["empty"],
                  str(line))
            following = page.evaluate(
                "([a, b, limit]) => { const s = BrokeryChart.store(limit); s.add(a); s.add(b);"
                "return BrokeryChart.option(s.payload(), null, {}).series[0].markLine.data[0].yAxis; }",
                [payload, chart.payload(kframe(LIMIT - 70, 80, lambda i: 9999.0)), LIMIT])
            check("現價線跟住串流走：合併後最新一根即新價，界面唔使另外傳值",
                  following == 9999.0, str(following))

            # 右上角現價大字：與現價線同一個來源，故界面（三處）只需要送資料，唔使各處自己擺一個數字。
            tag = page.evaluate(
                "([p, falling]) => { const at = (o) => o.graphic[0];"
                "const up = at(BrokeryChart.option(p, null, {ktype: '1m'}));"
                "const down = at(BrokeryChart.option(falling, null, {}));"
                "const lit = at(BrokeryChart.option(p, null, {ktype: '1m', flash: true}));"
                "return {text: up.style.text, fill: up.style.fill, size: up.style.fontSize,"
                " align: up.style.textAlign, plainBg: up.style.backgroundColor === undefined,"
                " downText: down.style.text, downFill: down.style.fill,"
                " flashFill: lit.style.fill, flashBg: lit.style.backgroundColor,"
                " empty: BrokeryChart.option({columns: ['ts','open','high','low','close'], rows: []}, null, {})"
                ".graphic.length === 0}; }",
                [payload, chart.payload(kframe(0, 5, lambda i: 90.0 if i == 4 else 100.0))])
            check("右上角現價大字：取序列最後一根的收市價（大字、右對齊、升紅跌綠），無資料時唔畫",
                  tag["text"] == f"{100.0 + LIMIT - 1:.2f}" and tag["fill"] == "#e0524a"
                  and tag["size"] >= 18 and tag["align"] == "right" and tag["plainBg"]
                  and tag["downText"] == "90.00" and tag["downFill"] == "#2ea36f" and tag["empty"],
                  str(tag))
            check("flash 只換一次配色（本圖 animation 為 false，用唔到 ECharts 自己的過渡，計時由實例做）",
                  tag["flashFill"] == "#fff" and tag["flashBg"] == "#e0524a", str(tag))

            # 閃爍要由實例自己計時：串流每次 update 都會重畫，故要分清「價格真的改變」與「又重畫一次」。
            # 讀的是 ECharts 實際收到的圖形（getOption 會把 graphic 包一層 elements），唔係直接讀 option() 的返回值。
            page.evaluate("() => { window.tagOf = (name) => (window[name].echarts.getOption().graphic[0].elements"
                          " || [{}])[0].style; }")
            first = page.evaluate("() => { const g = window.tagOf('pb');"
                                  "return {text: g.text, fill: g.fill, plain: g.backgroundColor === undefined}; }")
            same = page.evaluate("([p]) => { window.pa.update(p); const g = window.tagOf('pa');"
                                 "return {fill: g.fill, plain: g.backgroundColor === undefined}; }", [payload])
            flashed = page.evaluate("([b]) => { window.pa.update(b); const g = window.tagOf('pa');"
                                    "return {text: g.text, fill: g.fill, bg: g.backgroundColor}; }",
                                   [chart.payload(kframe(LIMIT - 70, 80, lambda i: 9999.0))])
            page.wait_for_timeout(900)   # 超過 FLASH_MS：閃完要還原配色，唔該一直白底蓋住右上角
            settled = page.evaluate("() => { const g = window.tagOf('pa');"
                                    "return {fill: g.fill, plain: g.backgroundColor === undefined}; }")
            check("現價大字只在價格真的改變時閃一下：首次載入唔閃、重畫同一個價唔閃、900ms 後自己還原",
                  first["text"] == f"{100.0 + LIMIT - 1:.2f}" and first["plain"]
                  and same["plain"] and same["fill"] == "#e0524a"
                  and flashed["text"] == "9999.00" and flashed["fill"] == "#fff" and flashed["bg"] == "#e0524a"
                  and settled["plain"] and settled["fill"] == "#e0524a",
                  str([first, same, flashed, settled]))

            gone = page.evaluate("() => { window.pa.destroy(); window.pb.destroy();"
                                 "const el = document.getElementById('chart');"
                                 "return {marker: el.hasAttribute('_brokery_chart'),"
                                 " instance: echarts.getInstanceByDom(el) !== undefined}; }")
            check("destroy() 收返實例：元素標記移除、ECharts 實例釋放（換標的/換頁唔會漏圖）",
                  not gone["marker"] and not gone["instance"], str(gone))

            formats = page.evaluate(
                "() => ({intraday: BrokeryChart.timeText(1760000000, true), "
                "day: BrokeryChart.timeText(1760000000, false)})")
            check("timeText 只影響顯示：intraday 帶時分，日線只到日期",
                  len(formats["day"]) == 10 and ":" not in formats["day"]
                  and len(formats["intraday"]) == 11 and ":" in formats["intraday"], str(formats))

            # ---------- 多週期格子（BrokeryGrid）：一格一週期，圖仍由同一份 chart.js 畫 ----------
            # 呢度用真載體頁同真 ECharts：要驗嘅係桌面 GUI 與 Web UI 實際行嘅同一條路徑。
            nine = list(KTYPE_ORDER)
            grid = browser.new_page()
            grid.goto(chart.grid_page().as_uri(), timeout=30_000)
            grid.wait_for_function("window.brokeryGridReady !== undefined", timeout=15_000)
            check("多週期載體頁以本地 echarts.min.js + chart.js + chart_grid.js 載入成功",
                  grid.evaluate("window.brokeryGridReady") is True
                  and grid.evaluate("window.brokeryGridMissing") == "",
                  str(grid.evaluate("window.brokeryGridMissing")))

            grid.evaluate(build_call)
            built = grid.evaluate(
                "() => { const cells = [...document.querySelectorAll('.brokery-cell')];"
                "return {count: window.brokeryGrid.count(), cells: cells.length, "
                "ktypes: window.brokeryGrid.ktypes(), "
                "tabs: cells.map((c) => [...c.querySelectorAll('.brokery-tabs button')]"
                ".map((b) => b.dataset.ktype)), "
                "on: cells.map((c) => [...c.querySelectorAll('.brokery-tabs button.on')]"
                ".map((b) => b.dataset.ktype)), "
                # 數實例而唔係數 canvas：ECharts 未 setOption 之前唔會建 canvas，未畫嘅格都有實例。
                "instances: [...document.querySelectorAll('.brokery-pane')]"
                ".filter((el) => echarts.getInstanceByDom(el) !== undefined).length, "
                "text: document.body.innerText.replace(/\\s/g, '')}; }")
            check("BrokeryGrid.build：九格九實例（一格一週期、順序照傳入者），每格一排水平週期按鈕且只高亮自己嗰個",
                  built["count"] == 9 and built["cells"] == 9 and built["instances"] == 9
                  and built["ktypes"] == nine and all(tabs == nine for tabs in built["tabs"])
                  and built["on"] == [[k] for k in nine], str(built["on"]))
            check("載體頁零界面文字：按鈕只有 ktype 代號（換語言唔使重建格子，提示一律由 note() 送入）",
                  built["text"] == "".join(nine) * 9, f"{len(built['text'])} 字")

            grid.evaluate(chart.grid_set_js(0, history, "1m"))
            painted = grid.evaluate(
                "() => [...document.querySelectorAll('.brokery-pane')].map((el) => {"
                "const o = (echarts.getInstanceByDom(el) || {getOption: () => {}}).getOption() || {};"
                "return (((o.series || [])[0] || {}).data || []).length; })")
            check("grid_set_js 只重畫一格：其餘八格唔會因為一格有資料而被順帶畫出",
                  painted[0] == LIMIT and all(n == 0 for n in painted[1:]), str(painted))

            grid.evaluate(chart.grid_note_js(4, "1m 名額未釋放"))
            noted = grid.evaluate("() => [...document.querySelectorAll('.brokery-note')]"
                                  ".map((n) => n.textContent)")
            check("grid_note_js 只喺指定一格顯示提示（名額倒數逐格上報，唔使霸住整頁訊息列）",
                  noted[4] == "1m 名額未釋放" and all(text == "" for text in noted[:4] + noted[5:]),
                  str(noted))

            # 第二格照自己嘅週期畫：之後先至可以比較「換咗一格，其餘各格照自己嗰個」。
            grid.evaluate(chart.grid_set_js(1, history, "3m"))

            # 撳按鈕要經真點擊：要驗嘅係用戶喺格子上實際做嘅動作，而唔係直接調用 pick()。
            grid.locator(".brokery-cell").nth(0).locator("button[data-ktype='day']").click()
            picked = grid.evaluate(chart.grid_picks_js())
            marked = grid.evaluate(
                "() => { document.querySelectorAll('.brokery-cell')[0]"
                ".querySelector('button[data-ktype=\"day\"]').click();"
                "return {again: window.brokeryGrid.takePicks(), ktypes: window.brokeryGrid.ktypes(), "
                "on: [...document.querySelectorAll('.brokery-cell')[0]"
                ".querySelectorAll('.brokery-tabs button.on')].map((b) => b.dataset.ktype)}; }")
            check("撳一格嘅週期按鈕只上報意圖：takePicks() 返回 [序號, ktype] 並即刻清空，"
                  "重複撳同一週期唔再上報（取數與訂閱仍由界面決定）",
                  picked == [[0, "day"]] and marked["again"] == []
                  and marked["ktypes"][0] == "day" and marked["on"] == ["day"]
                  and grid.evaluate(chart.grid_picks_js()) == [], str([picked, marked["again"]]))

            # 換咗週期之後嘅重畫（取返歷史或串流 update）唔使再報週期：格子自己記住，先至唔會畫返舊格式。
            grid.evaluate(chart.grid_set_js(0, history))
            remembered = grid.evaluate(
                "() => { const c = echarts.getInstanceByDom(document.querySelectorAll('.brokery-pane')[0]);"
                "const o = c.getOption(); "
                "return {day: o.xAxis[0].axisLabel.formatter(1760000000), "
                "bars: o.series[0].data.length, other: echarts.getInstanceByDom("
                "document.querySelectorAll('.brokery-pane')[1]).getOption().xAxis[0].axisLabel"
                ".formatter(1760000000)}; }")
            check("grid_set_js 唔傳 ktype 即沿用該格現有週期：換週期後嘅重畫照新格式，其餘各格照自己嗰個",
                  len(remembered["day"]) == 10 and ":" not in remembered["day"]
                  and remembered["bars"] == LIMIT and len(remembered["other"]) == 11
                  and ":" in remembered["other"], str(remembered))

            # 容器改尺寸靠 window resize → resizeAll()：一格一實例先至唔會只縮返一格。
            grid.set_viewport_size({"width": 900, "height": 520})
            grid.wait_for_timeout(300)   # 視窗 resize 事件唔係同步送達：等一會先讀，唔使為跑綠改圖
            sized = grid.evaluate("() => [...document.querySelectorAll('.brokery-pane')]"
                                  ".map((el) => Math.abs(echarts.getInstanceByDom(el).getWidth()"
                                  " - el.clientWidth) <= 2)")
            check("resizeAll() 涵蓋多格：容器改尺寸後九格各自跟返（九個實例唔會漏圖或 init 兩次）",
                  len(sized) == 9 and all(sized), str(sized))

            released = grid.evaluate(
                "() => { window.brokeryGrid.destroy();"
                "return {cells: document.querySelectorAll('.brokery-cell').length, "
                "marker: document.querySelectorAll('[_brokery_chart]').length}; }")
            check("BrokeryGrid.destroy() 收返九個實例（換券商即重建格子，唔會漏圖）",
                  released == {"cells": 0, "marker": 0}, str(released))
            grid.close()

        finally:
            browser.close()

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": pd.DataFrame(), "message": "失敗：" + "；".join(failed)}
    return {"status": True, "data": pd.DataFrame(),
            "message": f"{len(checks)} 項檢查全過：一份 chart.js 規格（x 軸用原始 ts、candlestick+成交量、"
                       "overlays.register 掛點、未知 kind 略過）、store() 合併與顯示反序、"
                       "create() 實例的滾輪縮 X 軸/Shift+滾輪只縮 Y 軸/拖曳平移/雙擊復原與跨 update 保持、"
                       "初始窗口由調用方給（傳 start: 0 即全部根數喺圖上）、"
                       "現價水平線與右上角大字跟住最新一根走（只在新價改變時閃一次）、取消 y 軸水平格線與"
                       "最新一根右側留位、compact 只畫價格格而 dataZoom 索引不變、"
                       "BrokeryGrid 九格九實例（零界面文字、水平週期按鈕、takePicks 只上報意圖、"
                       "set 只重畫一格並記住該格週期、resizeAll 涵蓋多格）、"
                       "chart.py 的 payload/overlay_rows/render_js/grid_* 與本地 echarts 載入"}


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
