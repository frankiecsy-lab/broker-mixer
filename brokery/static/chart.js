/* BrokeryChart：一份 K 線圖規格，閘道面板、Web UI 與桌面 GUI 載入同一份。
   x 軸的資料一律是原始 ts（UTC 秒），時間文字只由 formatter 產生，因此疊加指標可以準確對齊 bar。
   疊加指標（如 ICT 的 order block）由 Python 以 pandas 算出 rows（brokers.base.OVERLAY_COLUMNS），
   本檔只把 rows 變成圖形，不含任何指標算法。 */
(function (global) {
  'use strict';

  const UP = '#e0524a', DOWN = '#2ea36f', DIM = '#8a97a8';   // 升紅跌綠，與界面主題一致
  const REQUIRED = ['ts', 'open', 'high', 'low', 'close'];

  const pad = (n) => String(n).padStart(2, '0');

  // 顯示格式屬顯示層：換 ktype 只換文字，不換 x 軸的鍵。
  function timeText(ts, intraday) {
    const d = new Date(Number(ts) * 1000);
    const date = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
    return intraday ? `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}` : date;
  }

  const byTs = (a, b) => (a.code === b.code ? a.ts - b.ts : String(a.code).localeCompare(String(b.code)));

  // 輸入可以是接口的 {columns, rows}，也可以是本檔已解析的 bar 陣列。
  function bars(input) {
    if (Array.isArray(input)) return input.slice().sort(byTs);
    const cols = (input && input.columns) || [];
    const at = (name) => cols.indexOf(name);
    if (REQUIRED.some((name) => at(name) < 0)) return [];
    return (input.rows || [])
      .map((r) => ({
        code: at('code') < 0 ? '' : r[at('code')],
        ts: Number(r[at('ts')]), open: Number(r[at('open')]), high: Number(r[at('high')]),
        low: Number(r[at('low')]), close: Number(r[at('close')]),
        volume: at('volume') < 0 ? 0 : Number(r[at('volume')]) || 0,
        raw: r,   // 原樣保留一行：合併後要還原成接口的 {columns, rows} 俾界面顯示 DF
      }))
      .filter((b) => Number.isFinite(b.ts))
      .sort(byTs);
  }

  // 表格顯示：最新在最上。DataFrame 本身仍按 ts 升序（圖表與跨券商對齊靠升序），故反序只喺呢度做。
  function desc(payload) {
    const cols = (payload && payload.columns) || [];
    const rows = ((payload && payload.rows) || []).slice();
    const at = cols.indexOf('ts');
    return { columns: cols, rows: at < 0 ? rows.reverse() : rows.sort((a, b) => Number(b[at]) - Number(a[at])) };
  }

  // 串流的 update 只帶最近 count 根，直接覆蓋會把 1000 根歷史縮返 60 根，故要有合併規則：
  // key = (code, ts)，新到者覆蓋同 ts 者，每個代碼只保留最新 limit 根，內部一律升序。
  function store(limit = 1000) {
    const kept = new Map();
    const keyOf = (b) => `${b.code}\u0000${b.ts}`;
    let columns = [];   // 最近一次輸入的欄位順序：還原 DF 時要照原欄位（含 time_str、source）
    return {
      add(input) {
        if (!Array.isArray(input) && (input.columns || []).length) columns = input.columns.slice();
        for (const b of bars(input)) kept.set(keyOf(b), b);
        for (const code of new Set([...kept.values()].map((b) => b.code))) {
          const mine = [...kept.values()].filter((b) => b.code === code).sort((a, b) => a.ts - b.ts);
          for (const b of mine.slice(0, Math.max(0, mine.length - limit))) kept.delete(keyOf(b));
        }
        return this.bars();
      },
      bars() { return [...kept.values()].sort(byTs); },
      // 合併後的序列還原成 {columns, rows}：界面下方的 DF 顯示原欄位，唔係圖表用的 bar。
      payload() {
        const at = (name) => columns.indexOf(name);
        return { columns: columns, rows: this.bars().map((b) => columns.map(
          (c) => (b.raw ? b.raw[at(c)] : b[c] === undefined ? null : b[c]))) };
      },
      rowsDesc() { return this.bars().reverse(); },
      clear() { kept.clear(); },
      get size() { return kept.size; },
    };
  }

  // 疊加指標的掛點：按 row 的 kind 分派，日後新增指標只係 register 一個新的 kind。
  const handlers = new Map();

  // 區間嘅端點未必剛好係某一根 bar（例如 order block 嘅起點喺歷史之外），取最接近嘅一根。
  function snap(ts, axis) {
    if (!axis.length) return null;
    if (ts <= axis[0]) return axis[0];
    if (ts >= axis[axis.length - 1]) return axis[axis.length - 1];
    let lo = 0, hi = axis.length - 1;
    while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (axis[mid] <= ts) lo = mid; else hi = mid; }
    return ts - axis[lo] <= axis[hi] - ts ? axis[lo] : axis[hi];
  }

  const sideColor = (side) => (side === 'bull' ? UP : side === 'bear' ? DOWN : DIM);

  // zone = 矩形（order block、供需區、FVG 都是區間）；line = 一段直線（均線、水平參考位）。
  handlers.set('zone', (rows, ctx) => ({
    markArea: rows.filter((r) => ctx.at(r.start_ts) !== null && ctx.at(r.end_ts) !== null).map((r) => [
      { xAxis: ctx.at(r.start_ts), yAxis: r.start_price,
        itemStyle: { color: `${sideColor(r.side)}22`, borderColor: sideColor(r.side) } },
      { xAxis: ctx.at(r.end_ts), yAxis: r.end_price },
    ]),
  }));
  handlers.set('line', (rows, ctx) => ({
    series: rows.filter((r) => ctx.at(r.start_ts) !== null && ctx.at(r.end_ts) !== null).map((r) => ({
      type: 'line', name: r.name || r.kind, showSymbol: false, silent: true, z: 6,
      lineStyle: { color: sideColor(r.side), width: 1.5, type: r.side ? 'solid' : 'dashed' },
      data: [[ctx.at(r.start_ts), r.start_price], [ctx.at(r.end_ts), r.end_price]],
    })),
  }));

  function option(input, overlays, opts) {
    const rows = bars(input);
    const axis = rows.map((b) => b.ts);
    const ctx = {
      axis: axis, bars: rows,
      at: (ts) => { const v = snap(Number(ts), axis); return v === null ? null : String(v); },
      color: sideColor,
    };
    const extra = { series: [], markArea: [] };
    const byKind = new Map();
    for (const row of overlays || []) {
      const kind = String((row && row.kind) || '');
      if (!kind) continue;
      if (!byKind.has(kind)) byKind.set(kind, []);
      byKind.get(kind).push(row);
    }
    for (const [kind, group] of byKind) {
      const fn = handlers.get(kind);
      if (!fn) continue;                       // 未註冊的 kind 略過：圖照畫，唔因為未知指標而空白
      const part = fn(group, ctx) || {};
      extra.series.push(...(part.series || []));
      extra.markArea.push(...(part.markArea || []));
    }
    const intraday = /^\d+[mh]$/.test(String((opts && opts.ktype) || ''));
    const label = (value) => timeText(value, intraday);
    return {
      backgroundColor: 'transparent', animation: false,
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross', label: { formatter: (p) => label(p.value) } } },
      axisPointer: { type: 'cross' },
      grid: [{ left: 62, right: 16, top: 16, height: '62%' }, { left: 62, right: 16, top: '76%', height: '18%' }],
      xAxis: [{ type: 'category', data: axis.map(String), axisLabel: { color: DIM, formatter: label } },
              { type: 'category', gridIndex: 1, data: axis.map(String), axisLabel: { show: false } }],
      yAxis: [{ scale: true, axisLabel: { color: DIM } }, { gridIndex: 1, axisLabel: { show: false } }],
      dataZoom: [{ type: 'inside', xAxisIndex: [0, 1], start: (opts && opts.start) || 60,
                   end: (opts && opts.end) || 100 }],
      series: [
        { name: 'K 線', type: 'candlestick', data: rows.map((b) => [b.open, b.close, b.low, b.high]),
          itemStyle: { color: UP, color0: DOWN, borderColor: UP, borderColor0: DOWN },
          markArea: extra.markArea.length ? { silent: true, data: extra.markArea } : undefined },
        { name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1,
          data: rows.map((b) => ({ value: b.volume, itemStyle: { color: b.close >= b.open ? UP : DOWN } })) },
        ...extra.series,
      ],
    };
  }

  function render(el, input, overlays, opts) {
    if (!global.echarts || !el) return null;
    el.setAttribute('_brokery_chart', '');   // 標記後 resize 由本檔統一處理，界面唔使各寫一次
    const chart = global.echarts.getInstanceByDom(el) || global.echarts.init(el);
    const zoom = (chart.getOption() || {}).dataZoom;
    const merged = Object.assign({ start: zoom && zoom[0] ? zoom[0].start : 60,
                                  end: zoom && zoom[0] ? zoom[0].end : 100 }, opts || {});
    // notMerge：換標的或換指標時舊 series 必須清走；但縮放範圍要保留，否則每次串流更新都跳返原位。
    chart.setOption(option(input, overlays, merged), { notMerge: true });
    return chart;
  }

  function resizeAll() {
    if (!global.echarts) return;
    for (const el of global.document.querySelectorAll('[_brokery_chart]')) {
      const chart = global.echarts.getInstanceByDom(el);
      if (chart) chart.resize();
    }
  }

  global.BrokeryChart = {
    bars: bars, desc: desc, store: store, option: option, render: render, resizeAll: resizeAll,
    timeText: timeText, colors: { up: UP, down: DOWN, dim: DIM },
    overlays: { register: (kind, fn) => handlers.set(String(kind), fn),
                kinds: () => [...handlers.keys()] },
  };
  global.addEventListener('resize', resizeAll);
})(typeof window !== 'undefined' ? window : this);
