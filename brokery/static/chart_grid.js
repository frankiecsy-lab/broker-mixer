/* BrokeryGrid：多週期界面的容器（一格一週期，每格上方一排水平週期按鈕）。
   格子清單一律由界面傳入（即該券商聲明可串流的週期，順序照 /capabilities 返回者），本檔不自行排列週期。
   頁內不含任何界面文字：按鈕只用 ktype 本身（1m/3m/day…），因此換語言不需要重建格子；
   要顯示的提示一律由界面經 note() 送入。
   撳按鈕只記低「哪一格要轉哪個週期」，取數與訂閱仍由界面決定：Web UI 用 onPick 即時回調，
   桌面 GUI 用 takePicks() 輪詢取走（QWebChannel 在離屏載入下會令 WebEngine 崩潰，故不走回調）。 */
(function (global) {
  'use strict';

  const grids = new Map();   // 容器元素 -> 該頁的格子（一個頁面即一個容器）

  function dispose(el) {
    for (const cell of (grids.get(el) || { cells: [] }).cells) {
      if (cell.pane) cell.pane.destroy();
    }
    grids.delete(el);
    el.textContent = '';
  }

  function build(el, opts) {
    const chart = global.BrokeryChart;
    if (!chart || !el) return null;
    dispose(el);                                   // 換券商即重建：舊實例要先 dispose，否則同一元素會 init 兩次
    const ktypes = (opts && opts.ktypes) || [];
    const onPick = (opts && opts.onPick) || null;
    const picks = [];
    el.classList.add('brokery-grid');

    const cells = ktypes.map((ktype, index) => {
      const cell = global.document.createElement('div');
      cell.className = 'brokery-cell';
      const tabs = global.document.createElement('div');
      tabs.className = 'brokery-tabs';
      ktypes.forEach((name) => {
        const button = global.document.createElement('button');
        button.type = 'button';
        button.dataset.ktype = name;
        button.textContent = name;                 // 週期代號本身就是標籤：不需要翻譯
        button.className = name === ktype ? 'on' : '';
        button.addEventListener('click', () => pick(index, name));
        tabs.appendChild(button);
      });
      const note = global.document.createElement('div');
      note.className = 'brokery-note';
      const paneEl = global.document.createElement('div');
      paneEl.className = 'brokery-pane';
      cell.appendChild(tabs);
      cell.appendChild(note);
      cell.appendChild(paneEl);
      el.appendChild(cell);
      return { ktype, tabs, note, pane: chart.create(paneEl, { compact: true, ktype, start: 0 }) };
    });

    function mark(index, ktype) {
      const cell = cells[index];
      if (!cell) return;
      cell.ktype = ktype;
      for (const button of cell.tabs.children) {
        button.className = button.dataset.ktype === ktype ? 'on' : '';
      }
    }

    // 只上報意圖：换哪一格、轉哪個週期由界面去取數與訂閱，這裡不假裝已經換好。
    function pick(index, ktype) {
      const cell = cells[index];
      if (!cell || ktype === cell.ktype) return;
      mark(index, ktype);
      picks.push([index, ktype]);
      if (onPick) onPick(...picks.shift());
    }

    grids.set(el, { cells });
    return {
      ktypes: () => cells.map((cell) => cell.ktype),
      count: () => cells.length,
      // 只重畫一格：ktype 省略時沿用該格現有的週期（串流更新就是這種情況）。
      set(index, payload, ktype, overlays) {
        const cell = cells[index];
        if (!cell || !cell.pane) return null;
        if (ktype) mark(index, ktype);
        cell.pane.update(payload, overlays, { ktype: cell.ktype, compact: true });
        return this;
      },
      note(index, text) {
        const cell = cells[index];
        if (cell) cell.note.textContent = text || '';
        return this;
      },
      takePicks: () => picks.splice(0),
      destroy: () => dispose(el),
    };
  }

  global.BrokeryGrid = { build: build, destroy: dispose };
})(typeof window !== 'undefined' ? window : this);
