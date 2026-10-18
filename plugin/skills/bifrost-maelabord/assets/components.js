/* Bifröst mælaborð · íhlutir 1.0 (með farsímareglum) — settu inn í script-tagi á eftir Chart.js 4.4.1 (cdnjs) */
const BF = (() => {
  const $ = id => document.getElementById(id);
  const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  /* Íslenskt talnasnið án toLocaleString */
  const fmt = (n, d = 1) => {
    if (n == null || isNaN(n)) return '–';
    const neg = n < 0 && Math.abs(n) >= Math.pow(10, -d) / 2;
    let [i, f] = Math.abs(n).toFixed(d).split('.');
    i = i.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return (neg ? '−' : '') + i + (f ? ',' + f : '');
  };
  const sg = (n, d = 1) => (n > 1e-9 ? '+' : '') + fmt(n, d);
  const mkr = (kr, d = 1) => fmt(kr / 1e6, d);
  const MON = ['jan', 'feb', 'mar', 'apr', 'maí', 'jún', 'júl', 'ágú', 'sep', 'okt', 'nóv', 'des'];
  const monLabel = ym => MON[+ym.slice(5, 7) - 1];
  const date = iso => iso ? `${iso.slice(8, 10)}.${iso.slice(5, 7)}.${iso.slice(0, 4)}` : '–';
  const alpha = (c, a) => { const h = c.replace('#', ''); if (h.length !== 6) return c; const n = parseInt(h, 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; };
  /* Farsími: true undir 640px. Gröf og útlit lesa þetta við hverja teikningu. */
  const MQ = window.matchMedia ? matchMedia('(max-width:640px)') : { matches: false };
  const mobile = () => MQ.matches;
  const chip = (d, goodWhenUp, txt) => { const c = Math.abs(d) < 1e-6 ? 'eq' : ((d > 0) === goodWhenUp ? 'up' : 'dn'); return `<span class="chip ${c}">${txt}</span>`; };

  /* Flipar: <div class="tabs" role="tablist"><button role="tab" aria-controls="t1">…</button></div><section id="t1" class="tab" role="tabpanel"> */
  function tabs(root, onShow) {
    const bs = root ? [...root.querySelectorAll('[role=tab]')] : [];
    if (!bs.length) { onShow && onShow(null); return () => {}; }
    /* Stutt heiti fyrir neðri flipastiku í síma: <button data-short="Efnahagur"> */
    bs.forEach(b => { if (!b.dataset.short) { const t = b.textContent.trim(); if (t.length > 14) b.dataset.short = t.split(/\s+/)[0]; }
      if (b.dataset.short && !b.querySelector('.t-l')) b.innerHTML = `<span class="t-l">${b.innerHTML}</span><span class="t-s">${b.dataset.short}</span>`; });
    const show = (id, user) => { if (user && mobile()) try { window.scrollTo({ top: 0, behavior: 'smooth' }); } catch (e) { window.scrollTo(0, 0); } bs.forEach(b => { const on = b.getAttribute('aria-controls') === id; b.setAttribute('aria-selected', on); b.tabIndex = on ? 0 : -1; $(b.getAttribute('aria-controls')).hidden = !on; }); try { history.replaceState(null, '', '#' + id); } catch (e) {} onShow && onShow(id); };
    bs.forEach((b, i) => { b.onclick = () => show(b.getAttribute('aria-controls'), true); b.onkeydown = e => { if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { const j = (i + (e.key === 'ArrowRight' ? 1 : -1) + bs.length) % bs.length; bs[j].focus(); show(bs[j].getAttribute('aria-controls')); } }; });
    const h = location.hash.slice(1); show(bs.some(b => b.getAttribute('aria-controls') === h) ? h : bs[0].getAttribute('aria-controls'));
    return show;
  }

  /* Smáferill á canvas: grunnur strikaður, raun/sviðsmynd heil */
  function spark(canvas, base, cur) {
    const r = canvas.getBoundingClientRect(), dpr = window.devicePixelRatio || 1; if (!r.width) return;
    canvas.width = r.width * dpr; canvas.height = r.height * dpr; const x = canvas.getContext('2d'); x.scale(dpr, dpr);
    const all = (base || []).concat(cur), mn = Math.min(...all), mx = Math.max(...all), w = r.width, h = r.height;
    const Y = v => h - 3 - (h - 6) * (v - mn) / ((mx - mn) || 1), X = i => 2 + (w - 4) * i / Math.max(1, cur.length - 1);
    if (base) { x.lineWidth = 1.25; x.setLineDash([3, 3]); x.strokeStyle = css('--base'); x.beginPath(); base.forEach((v, i) => i ? x.lineTo(X(i), Y(v)) : x.moveTo(X(i), Y(v))); x.stroke(); }
    x.setLineDash([]); x.lineWidth = 2; x.strokeStyle = css('--scen'); x.beginPath(); cur.forEach((v, i) => i ? x.lineTo(X(i), Y(v)) : x.moveTo(X(i), Y(v))); x.stroke();
    x.fillStyle = css('--scen'); x.beginPath(); x.arc(X(cur.length - 1), Y(cur.at(-1)), 2.5, 0, 7); x.fill();
  }

  /* Lykilmælir: el = .kpi element með .v, .d og valfrjálst canvas */
  function kpi(el, { value, base, delta, goodWhenUp = true, deltaText, series, baseSeries }) {
    el.querySelector('.v').textContent = value;
    el.querySelector('.d').innerHTML = (base != null ? `grunnur ${base} ` : '') + (delta != null ? chip(delta, goodWhenUp, deltaText) : '');
    const c = el.querySelector('canvas'); if (c && series) spark(c, baseSeries, series);
  }

  /* Láréttar súlur í HTML. rows: [{label, value, text?, color?}] — diverging=true teiknar út frá miðju */
  function hbars(el, rows, { diverging = false, color = '--brand' } = {}) {
    const mx = Math.max(1e-9, ...rows.map(r => Math.abs(r.value)));
    el.classList.add('hb');
    el.innerHTML = rows.map(r => {
      const w = (diverging ? 50 : 100) * Math.abs(r.value) / mx, c = r.color || (diverging ? (r.value < 0 ? '--dn' : '--up') : color);
      const pos = diverging ? (r.value < 0 ? `right:50%;width:${w}%` : `left:50%;width:${w}%`) : `left:0;width:${w}%`;
      return `<div class="r"><span title="${r.label}">${r.label}</span><div class="t"><span style="${pos};background:var(${c})"></span>${diverging ? '<i class="z"></i>' : ''}</div><span class="n">${r.text ?? fmt(r.value)}</span></div>`;
    }).join('');
  }

  const CH = {};
  function upsert(key, canvas, cfg) { if (CH[key]) { CH[key].data = cfg.data; CH[key].options = cfg.options; CH[key].update('none'); } else CH[key] = new Chart(canvas, cfg); return CH[key]; }
  function base() { const m = mobile(); Chart.defaults.color = css('--muted'); Chart.defaults.font.family = css('--f-body'); Chart.defaults.font.size = m ? 11 : 12;
    if (Chart.defaults.plugins && Chart.defaults.plugins.tooltip) { Chart.defaults.plugins.tooltip.padding = m ? 10 : 6; }
    return { grid: css('--line'), m, ticks: m ? 6 : 12 }; }

  /* Lína: grunnur strikaður, raun heil, bilið litað. unit: ' m.kr.' eða '%' */
  function lineCompare(key, canvas, { labels, base: b, cur, baseLabel = 'Grunnur', curLabel = 'Raun', unit = ' m.kr.', d = 1, fillGap = true, goodWhenUp = true }) {
    if (!window.Chart) return; const { grid, m, ticks } = base(); const up = css('--up'), dn = css('--dn');
    return upsert(key, canvas, { type: 'line', data: { labels, datasets: [
      ...(b ? [{ label: baseLabel, data: b, borderColor: css('--base'), borderDash: [6, 4], borderWidth: 2, pointRadius: 0, tension: .3 }] : []),
      { label: curLabel, data: cur, borderColor: css('--scen'), borderWidth: 2.5, pointRadius: m ? 2 : 3, pointHitRadius: 14, pointBackgroundColor: css('--scen'), pointBorderColor: css('--panel'), pointBorderWidth: 2, tension: .3,
        fill: b && fillGap ? { target: 0, above: alpha(goodWhenUp ? up : dn, .16), below: alpha(goodWhenUp ? dn : up, .16) } : false, spanGaps: false }] },
      options: { responsive: true, maintainAspectRatio: false, animation: { duration: 250 }, interaction: { mode: 'index', intersect: false }, layout: { padding: { right: 8 } },
        plugins: { legend: { display: false }, tooltip: { callbacks: { label: c => c.dataset.label + ': ' + fmt(c.raw, d) + unit } } },
        scales: { x: { grid: { display: false }, ticks: { autoSkip: true, maxRotation: 0, maxTicksLimit: ticks } }, y: { grid: { color: grid }, border: { display: false }, ticks: { maxTicksLimit: m ? 5 : 8, callback: v => fmt(v, 0) + (unit.trim() === '%' ? '%' : '') } } } } });
  }

  /* Brú: steps [{label, value, total?:true}] — total teiknast frá 0 */
  function bridge(key, canvas, steps, { unit = ' m.kr.', d = 1 } = {}) {
    if (!window.Chart) return; const { grid, m } = base();
    let run = 0; const data = [], col = [];
    steps.forEach(s => { if (s.total) { data.push([0, s.value]); run = s.value; col.push(css('--brand')); } else { data.push([run, run + s.value]); run += s.value; col.push(s.value >= 0 ? css('--up') : css('--dn')); } });
    const lows = data.map(x => Math.min(...x)), highs = data.map(x => Math.max(...x));
    const span = Math.max(...highs) - Math.min(...lows), yMin = Math.max(0, Math.min(...lows) - span * .15);
    return upsert(key, canvas, { type: 'bar', data: { labels: steps.map(s => s.label), datasets: [{ data, backgroundColor: col, borderRadius: 3, maxBarThickness: 44, borderSkipped: false }] },
      options: { responsive: true, maintainAspectRatio: false, animation: { duration: 250 }, plugins: { legend: { display: false }, tooltip: { callbacks: { label: c => { const s = steps[c.dataIndex]; return (s.total ? '' : (s.value >= 0 ? '+' : '')) + fmt(s.value, d) + unit; } } } },
        scales: { x: { grid: { display: false }, ticks: { autoSkip: false, maxRotation: m ? 60 : 40, font: { size: m ? 10 : 12 } } }, y: { min: yMin, grid: { color: grid }, border: { display: false }, ticks: { callback: v => fmt(v, 0) } } } } });
  }

  /* Röðun á töflu: <th data-sort="key"> + render(sortKey, dir) */
  function sortable(table, render) {
    let k = null, dir = 1;
    table.querySelectorAll('th[data-sort]').forEach(th => { th.tabIndex = 0; const go = () => { dir = k === th.dataset.sort ? -dir : 1; k = th.dataset.sort; render(k, dir); }; th.onclick = go; th.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); } }; });
  }

  /* Stikur: spec {key:{fmt:v=>txt, good:+1|-1, zero:0}} — input id="s-key", output id="o-key" */
  function bindSliders(spec, onChange) {
    const read = () => Object.fromEntries(Object.keys(spec).map(k => [k, +$('s-' + k).value]));
    const paint = p => Object.entries(spec).forEach(([k, s]) => { const o = $('o-' + k); if (!o) return; o.value = s.fmt(p[k]); const d = p[k] - (s.zero || 0); o.className = d === 0 ? '' : ((d > 0) === (s.good > 0) ? 'pos' : 'neg'); });
    const run = () => { const p = read(); paint(p); onChange(p); };
    Object.keys(spec).forEach(k => $('s-' + k).addEventListener('input', run));
    return { run, set: p => { Object.keys(spec).forEach(k => { if (p[k] != null) $('s-' + k).value = p[k]; }); run(); }, read };
  }

  /* Félagsval fyrir samstæðu: el = tómt div, names = ['Samstæða','Félag A',…], onPick(index) */
  function entityPicker(el, names, onPick) {
    el.className = 'seg'; el.setAttribute('role', 'group'); el.setAttribute('aria-label', 'Félag');
    el.innerHTML = names.map((n, i) => `<button type="button" aria-pressed="${i === 0}">${n}</button>`).join('');
    const bs = [...el.querySelectorAll('button')];
    bs.forEach((b, i) => b.onclick = () => { bs.forEach((x, j) => x.setAttribute('aria-pressed', j === i)); onPick(i); });
  }

  /* Litaþemu: Ljóst og Dökkt (Bifröst), Blátt og Jörð (úr grunnpallettu). Vistar val í localStorage. onChange() teiknar gröf upp á nýtt. */
  const THEMES = [['light', 'Ljóst', '#957f41'], ['dark', 'Dökkt', '#1e1e22'], ['blue', 'Blátt', '#326fa0'], ['earth', 'Jörð', '#6f743f']];
  function applyTheme(m) {
    const t = THEMES.some(x => x[0] === m) ? m : 'light', r = document.documentElement;
    r.setAttribute('data-bf', t === 'dark' ? 'dark' : 'light'); r.setAttribute('data-pal', t === 'blue' || t === 'earth' ? t : 'bifrost'); return t;
  }
  function themeToggle(el, onChange) {
    const set = m => { m = applyTheme(m); [...el.querySelectorAll('button')].forEach(b => b.setAttribute('aria-pressed', b.dataset.m === m)); try { localStorage.setItem('bf-theme-v5', m); } catch (e) {} };
    el.className = 'mode'; el.setAttribute('role', 'group'); el.setAttribute('aria-label', 'Litaþema');
    el.innerHTML = THEMES.map(([k, l, c]) => `<button type="button" data-m="${k}" title="Litaþema: ${l}" aria-label="Litaþema: ${l}"><i class="th-dot" style="background:${c}"></i><span class="th-l">${l}</span></button>`).join('');
    let m = 'light'; try { m = localStorage.getItem('bf-theme-v5') || 'light'; } catch (e) {}
    set(m);
    el.querySelectorAll('button').forEach(b => b.onclick = () => { set(b.dataset.m); Object.keys(CH).forEach(k => { CH[k].destroy(); delete CH[k]; }); onChange && onChange(); });
  }
  /* Gluggi fyrir drill-down: miðjaður á skjáborði, neðri gluggi (bottom sheet) í síma. BF.sheet('Lykill 3670', html) */
  function sheet(title, html) {
    let d = document.getElementById('bf-sheet');
    if (!d) { d = document.createElement('dialog'); d.id = 'bf-sheet'; d.className = 'sheet'; d.setAttribute('aria-labelledby', 'bf-sheet-t'); document.body.appendChild(d);
      d.addEventListener('click', e => { if (e.target === d) d.close(); }); }
    d.innerHTML = `<div class="sh-h"><b id="bf-sheet-t">${title}</b><button type="button" class="sh-x" aria-label="Loka">✕</button></div><div class="sh-b">${html}</div>`;
    d.querySelector('.sh-x').onclick = () => d.close();
    d.querySelectorAll('table').forEach(t => { t.classList.add('m-cards'); cardify(t); });
    if (d.showModal) d.showModal(); else d.setAttribute('open', '');
    return d;
  }
  /* Töflur sem spjöld í síma: <table class="m-cards">; setur data-label á reiti út frá dálkaheitum (keyrt sjálfkrafa) */
  function cardify(t) {
    const hs = [...t.querySelectorAll('thead th')].map(th => th.textContent.trim());
    if (!hs.length) return;
    t.querySelectorAll('tbody tr').forEach(tr => [...tr.children].forEach((td, i) => { if (!td.hasAttribute('data-label')) td.setAttribute('data-label', hs[i] || ''); }));
  }
  const cardAll = () => document.querySelectorAll('table.m-cards').forEach(cardify);
  if (window.MutationObserver) { let q = 0; new MutationObserver(() => { if (q) return; q = requestAnimationFrame(() => { q = 0; cardAll(); }); }).observe(document.documentElement, { childList: true, subtree: true }); }
  /* Skipt milli síma og skjáborðs (snúningur): teikna upp á nýtt með resize-atburði */
  if (MQ.addEventListener) MQ.addEventListener('change', () => { Object.keys(CH).forEach(k => { CH[k].destroy(); delete CH[k]; }); dispatchEvent(new Event('resize')); });

  /* Hallalitur undir línu: backgroundColor: BF.grad(BF.css('--s1')) */
  const grad = (c, a1 = .32, a2 = 0) => ctx => { const ch = ctx.chart, ar = ch.chartArea; if (!ar) return alpha(c, a1); const g = ch.ctx.createLinearGradient(0, ar.top, 0, ar.bottom); g.addColorStop(0, alpha(c, a1)); g.addColorStop(1, alpha(c, a2)); return g; };

  return { $, css, mobile, sheet, cardify, fmt, sg, mkr, MON, monLabel, date, alpha, chip, tabs, spark, kpi, hbars, lineCompare, bridge, sortable, bindSliders, entityPicker, themeToggle, grad };
})();

/* Tenglar milli mælaborða (data-nav): sama flipi ef leyft, annars nýr */
document.addEventListener('click', function (e) {
  var a = e.target.closest && e.target.closest('a[data-nav]'); if (!a) return;
  e.preventDefault();
  try { window.top.location.href = a.href; } catch (err) { window.open(a.href, '_blank', 'noopener'); }
});
