/* BrokeryChart：一份 K 線圖規格，閘道面板、Web UI 與桌面 GUI 載入同一份。
   x 軸的資料一律是原始 ts（UTC 秒），時間文字只由 formatter 產生，因此疊加指標可以準確對齊 bar。
   疊加指標（如 ICT 的 order block）由 Python 以 pandas 算出 rows（brokers.base.OVERLAY_COLUMNS），
   本檔只把 rows 變成圖形，不含任何指標算法。
   一張圖即一個實例（create）：界面只呼叫 update(payload)，縮放、平移與現價線由實例自己保持，
   三個界面走同一條路徑，日後新增指標亦只改呢度一次。 */
(function (global) {
  'use strict';

  const UP = '#e0524a', DOWN = '#2ea36f', DIM = '#8a97a8';   // 升紅跌綠，與界面主題一致
  const REQUIRED = ['ts', 'open', 'high', 'low', 'close'];
  const DEFAULT_START = 60;   // 預設只看最近 40%：1000 根全畫會睇唔清單根
  const FLASH_MS = 700;       // 現價更新時右上角大字的閃爍長度

  const pad = (n) => String(n).padStart(2, '0');

  // 顯示格式屬顯示層：換 ktype 只換文字，不換 x 軸的鍵。
  function timeText(ts, intraday) {
    const d = new Date(Number(ts) * 1000);
    const date = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
    return intraday ? `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}` : date;
  }

  const priceText = (v) => Number(v).toFixed(2);

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
    const trim = () => {
      for (const code of new Set([...kept.values()].map((b) => b.code))) {
        const mine = [...kept.values()].filter((b) => b.code === code).sort((a, b) => a.ts - b.ts);
        for (const b of mine.slice(0, Math.max(0, mine.length - limit))) kept.delete(keyOf(b));
      }
    };
    return {
      add(input) {
        if (!Array.isArray(input) && (input.columns || []).length) columns = input.columns.slice();
        for (const b of bars(input)) kept.set(keyOf(b), b);
        trim();
        return this.bars();
      },
      // 上限須跟隨界面請求的根數：寫死 1000 時取 3000 根會被裁返 1000 根（與 Python 側 BarStore.set_limit 同一口徑）。
      setLimit(next) { limit = Math.max(1, Number(next) || 1); trim(); return limit; },
      get limit() { return limit; },
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

  // 現價水平線：一律取序列最後一根的收盤價，故串流更新時線會自己移動，界面唔使另外傳值。
  function lastPrice(rows) {
    const last = rows[rows.length - 1];
    if (!last || !Number.isFinite(last.close)) return null;
    return { price: last.close, up: last.close >= last.open };
  }

  function option(input, overlays, opts) {
    opts = opts || {};
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
    const intraday = /^\d+[mh]$/.test(String(opts.ktype || ''));
    const label = (value) => timeText(value, intraday);
    // 緊湊模式（多週期界面：一格一週期、一屏九格）：只畫價格格，不畫成交量格與右上角現價大字，
    // 留位與字號一併收細。dataZoom 的索引不變（0 為 X、1 為 Y），故 create() 的滾輪分派不需要按模式分支。
    const compact = Boolean(opts.compact);
    // room.right：最新一根 bar 與右邊界的距離（現價數字就放喺呢條右邊界上面）。
    const room = compact ? { left: 46, right: 40, top: 10, size: 9 } : { left: 62, right: 64, top: 16, size: 12 };
    // 縮放與平移一律由 dataZoom 負責，界面唔使各寫一次：拖曳左右平移、復原由實例的 reset() 做（界面雙擊即呼叫）。
    // 滾輪不交給 dataZoom：它的 zoomOnMouseWheel 為 true 時不理修飾鍵（實測 Shift+滾輪會連 X 軸一齊縮），
    // 單軸縮小會變成兩軸一齊縮；故這裡一律關掉，由 create() 按修飾鍵自己分派。
    const zoom = [
      { type: 'inside', xAxisIndex: compact ? [0] : [0, 1], start: opts.start ?? DEFAULT_START, end: opts.end ?? 100,
        // throttle 預設 100ms：拖曳最後幾個平移動作會喺雙擊復原之後先送達，把復原靜靜蓋走（實測復原後
        // 範圍變返拖曳前那一段）。設 0 即即時生效，復原因此守得住。
        throttle: 0,
        zoomOnMouseWheel: false, moveOnMouseMove: true, moveOnMouseWheel: false },
      { type: 'inside', yAxisIndex: 0, filterMode: 'none', start: opts.yStart ?? 0, end: opts.yEnd ?? 100,
        zoomOnMouseWheel: false, moveOnMouseMove: false, moveOnMouseWheel: false },
    ];
    const last = lastPrice(rows);
    const markLine = last ? {
      silent: true, symbol: 'none', animation: false,
      lineStyle: { color: last.up ? UP : DOWN, width: 1, type: 'dashed' },
      label: { show: true, position: 'insideEndTop', color: last.up ? UP : DOWN,
               fontSize: compact ? 9 : 11, formatter: () => priceText(last.price) },
      data: [{ yAxis: last.price }],
    } : undefined;
    // 右上角現價大字：與現價線同一個來源（序列最後一根），故串流更新時數字自己跟住變，界面唔使另外傳值。
    // 右邊留位（room.right）同時是為呢個數字與最新一根 bar：bar 唔該貼住右邊，亦唔該被數字蓋住。
    // opts.flash 只換一次配色（本圖 animation 為 false，用唔到 ECharts 自己的過渡，計時由 create() 做）。
    const priceTag = last ? [{
      type: 'text', right: 8, top: 6, silent: true, z: 20,
      style: Object.assign({
        text: priceText(last.price), textAlign: 'right', fill: last.up ? UP : DOWN,
        fontSize: 22, fontWeight: 'bold',
      }, opts.flash ? { fill: '#fff', backgroundColor: last.up ? UP : DOWN,
                        padding: [3, 8], borderRadius: 4 } : {}),
    }] : [];
    const candle = { name: 'K 線', type: 'candlestick', data: rows.map((b) => [b.open, b.close, b.low, b.high]),
      itemStyle: { color: UP, color0: DOWN, borderColor: UP, borderColor0: DOWN },
      markArea: extra.markArea.length ? { silent: true, data: extra.markArea } : undefined,
      markLine: markLine };
    const volume = { name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1,
      data: rows.map((b) => ({ value: b.volume, itemStyle: { color: b.close >= b.open ? UP : DOWN } })) };
    const axisTime = { type: 'category', data: axis.map(String),
                       axisLabel: { color: DIM, fontSize: room.size, formatter: label } };
    const axisPrice = { scale: true, splitLine: { show: false }, axisLabel: { color: DIM, fontSize: room.size } };
    return {
      backgroundColor: 'transparent', animation: false,
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross', label: { formatter: (p) => label(p.value) } } },
      axisPointer: { type: 'cross' },
      // 緊湊時只有一格：下方留 26px 給時間標籤，整體高度由容器決定（界面排好九格，圖自己填滿一格）。
      grid: compact ? [{ left: room.left, right: room.right, top: room.top, bottom: 26 }]
                    : [{ left: room.left, right: room.right, top: room.top, height: '62%' },
                       { left: room.left, right: room.right, top: '76%', height: '18%' }],
      xAxis: compact ? [axisTime]
                     : [axisTime, { type: 'category', gridIndex: 1, data: axis.map(String), axisLabel: { show: false } }],
      // 兩格都唔畫 Y 軸的水平格線：K 線與成交量本身已經係密集的豎向資料，橫線只會壓住讀勢。
      yAxis: compact ? [axisPrice]
                     : [axisPrice, { gridIndex: 1, splitLine: { show: false }, axisLabel: { show: false } }],
      graphic: compact ? [] : priceTag,
      dataZoom: zoom,
      series: compact ? [candle, ...extra.series] : [candle, volume, ...extra.series],
    };
  }

  // 一個實例即一張圖：界面只送資料，縮放範圍由實例記住，所以串流每次更新唔會跳返原位。
  const instances = new Map();

  function create(el, opts) {
    if (!global.echarts || !el) return null;
    opts = opts || {};
    el.setAttribute('_brokery_chart', '');   // 標記後 resize 由本檔統一處理，界面唔使各寫一次
    const chart = global.echarts.getInstanceByDom(el) || global.echarts.init(el);
    const base = { start: opts.start ?? DEFAULT_START, end: opts.end ?? 100, yStart: 0, yEnd: 100 };
    const view = Object.assign({}, base);
    let spec = Object.assign({}, opts);   // 圖形規格（ktype）：換週期時照樣由 update 帶新值
    let input = null, overlays = null;
    let shown = null, flash = 0;   // 上一次的現價與未完成的閃爍計時

    const pane = {
      paint() {
        // notMerge：換標的或換指標時舊 series 必須清走；縮放範圍照 view 還原，唔會每次更新跳返原位。
        // 本圖 animation 為 false，用唔到 ECharts 自己的過渡，故現價變咗即自己計時閃一下右上角大字。
        // 只有現價真的改變先閃：每次串流 update 都會重畫，同一個價都閃會好煩；首次載入亦唔閃（冇上一個價可比）。
        const price = lastPrice(bars(input));
        const now = price ? price.price : null;
        const lit = shown !== null && now !== null && now !== shown;
        shown = now;
        global.clearTimeout(flash);
        chart.setOption(option(input, overlays, Object.assign({}, spec, view, {flash: lit})),
                       { notMerge: true });
        if (lit) flash = global.setTimeout(pane.paint, FLASH_MS);
        return pane;
      },
      update(payload, rows, opts) {
        input = payload;
        if (rows !== undefined) overlays = rows;
        if (opts) Object.assign(spec, opts);
        return pane.paint();
      },
      overlays(rows) { overlays = rows; return pane.paint(); },
      // 復原：x 軸回到預設範圍、y 軸取消單軸縮小（即交返俾自動縮放）。界面雙擊即呼叫呢個。
      reset() { Object.assign(view, base); return pane.paint(); },
      view: () => Object.assign({}, view),
      resize() { chart.resize(); },
      destroy() { global.clearTimeout(flash); instances.delete(el); el.removeAttribute('_brokery_chart'); chart.dispose(); },
      get echarts() { return chart; },
    };

    // 用戶以滾輪或拖曳改咗範圍：記返喺 view，先至唔會被下一次更新蓋走。
    chart.on('dataZoom', () => {
      const zoom = (chart.getOption() || {}).dataZoom || [];
      if (zoom[0]) { view.start = zoom[0].start; view.end = zoom[0].end; }
      if (zoom[1]) { view.yStart = zoom[1].start; view.yEnd = zoom[1].end; }
    });
    // 滾輪縮放按修飾鍵分工：滾輪只縮 X 軸、Shift+滾輪只縮 Y 軸（單軸）。以現窗的中點為縮放中心，
    // 範圍一律交回 dataZoom（即同一條 view 同步路徑），界面唔使知道縮放算式。
    // 必須用 capture：ECharts 自己喺同一個元素上先註冊咗滾輪 handler 並切斷其後嘅 listener，
    // 普通（bubble）註冊根本收唔到事件。
    el.addEventListener('wheel', (event) => {
      event.preventDefault();                       // 縮放時唔准頁面跟著郁
      const index = event.shiftKey ? 1 : 0;
      const from = index ? view.yStart : view.start, to = index ? view.yEnd : view.end;
      const half = Math.max(0.5, (to - from) * (event.deltaY > 0 ? 1.15 : 1 / 1.15) / 2);
      const mid = (from + to) / 2;
      chart.dispatchAction({ type: 'dataZoom', dataZoomIndex: index,
                             start: Math.max(0, mid - half), end: Math.min(100, mid + half) });
    }, { capture: true, passive: false });
    el.addEventListener('dblclick', pane.reset);
    instances.set(el, pane);
    return pane;
  }

  // 舊介面保留（同一元素重入即取返同一個實例）：既有頁面唔使改呼叫口徑。
  // opts 每次都要交落 update：圖形規格（ktype）屬該次輸入的一部分，只喺建立時給的話，換週期後 x 軸仍照舊週期格式。
  function render(el, input, overlays, opts) {
    if (!global.echarts || !el) return null;
    const pane = instances.get(el) || create(el, opts);
    pane.update(input, overlays, opts);
    return pane.echarts;
  }

  function resizeAll() {
    for (const pane of instances.values()) pane.resize();
  }

  global.BrokeryChart = {
    bars: bars, desc: desc, store: store, option: option, create: create, render: render,
    resizeAll: resizeAll, timeText: timeText, priceText: priceText,
    colors: { up: UP, down: DOWN, dim: DIM },
    overlays: { register: (kind, fn) => handlers.set(String(kind), fn),
                kinds: () => [...handlers.keys()] },
  };
  global.addEventListener('resize', resizeAll);
})(typeof window !== 'undefined' ? window : this);
