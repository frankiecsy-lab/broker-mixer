"""驗收共用圖表層：brokery/static/chart.js（唯一一份規格）與 brokery/chart.py（Python 入口）。

* Python 側：payload() 帶 columns 且保持 ts 升序（core 的契約）、NaN/Inf 變 null、overlay_rows()
  按 OVERLAY_COLUMNS 補齊欄位、render_js() 為可直接執行的呼叫、static_file() 不可走到 static 之外；
* 載體頁：本地 echarts.min.js 可用（無 CDN，故 GUI 與 Docker 離線都畫到圖）；
* x 軸的資料一律是原始 ts（UTC 秒），時間文字只由 formatter 產生 —— 這是疊加指標能對齊 bar 的前提；
* option() 產生 candlestick + 成交量兩條 series；疊加指標按行的 kind 分派，內置 zone/line，
  register 新的 kind 即多一條 series，未註冊的 kind 略過而不影響圖；
* store() 的合併規則：key=(code,ts)、同 ts 以新到者覆蓋、每個代碼只保留最新 N 根（串流的 update
  只帶最近 count 根，直接覆蓋會把 1000 根歷史縮返 60 根），合併後的序列以 payload() 還原成
  {columns, rows}，界面下方的 DF 照原欄位顯示；rowsDesc()/desc() 只屬顯示層的反序。

以腳本方式直接執行：
    python brokery/acceptance/run_chart_spec.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import pandas as pd

from brokery import chart
from brokery.brokers.base import K_COLUMNS, OVERLAY_COLUMNS

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

    try:
        chart.static_file("../core.py")
        escaped = True
    except FileNotFoundError:
        escaped = False
    check("static_file 只准取 static 目錄內的檔案",
          not escaped and chart.static_file("chart.js").is_file()
          and chart.host_page().name == "chart_host.html", "上層目錄被拒")

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

            drawn = page.evaluate(
                "([p]) => { const el = document.getElementById('chart'); "
                "const c = BrokeryChart.render(el, p, null, {ktype: '1m'}); "
                "return {same: c === echarts.getInstanceByDom(el), "
                "series: echarts.getInstanceByDom(el).getOption().series.length, "
                "canvas: Boolean(el.querySelector('canvas'))}; }", [payload])
            check("render() 真畫到嘢：同一個實例可重用（換標的唔會疊加舊圖）",
                  drawn["same"] and drawn["series"] == 2 and drawn["canvas"], str(drawn))

            formats = page.evaluate(
                "() => ({intraday: BrokeryChart.timeText(1760000000, true), "
                "day: BrokeryChart.timeText(1760000000, false)})")
            check("timeText 只影響顯示：intraday 帶時分，日線只到日期",
                  len(formats["day"]) == 10 and ":" not in formats["day"]
                  and len(formats["intraday"]) == 11 and ":" in formats["intraday"], str(formats))
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
                       "chart.py 的 payload/overlay_rows/render_js 與本地 echarts 載入"}


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
