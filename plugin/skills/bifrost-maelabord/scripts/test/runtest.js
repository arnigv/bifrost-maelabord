#!/usr/bin/env node
// Keyrir innbyggðar forskriftir mælaborðssíðu í node með litlu DOM (minidom.js).
// Notkun: node runtest.js síða.html [--snap snap.json] [--no-fuzz] [--quiet]
// Skref: (1) allar <script>-blokkir keyrðar í röð, (2) smellt á hvern flipa (role=tab) og skyndimynd tekin,
// (3) „fuzz“: smellt á hnappa/raðir/tengla, öll gildi í hverjum select og min/max/miðja á hverri stiku, Escape.
// Villur eru taldar upp; útgangskóði 1 ef einhver villa kom upp.
'use strict';
const fs = require('fs'), vm = require('vm'), path = require('path');
const { Document, mkEvent, dispatch } = require('./minidom.js');
const args = process.argv.slice(2);
const file = args[0];
const opt = k => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
const flag = k => args.includes(k);
const html = fs.readFileSync(file, 'utf8');
const doc = new Document(html);
const errors = [], cbErrors = [];
const charts = [];
const timers = [];
const W = {};
W._wl = {};
doc.defaultView = W;
const store = {};
Object.assign(global, {
  document: doc, window: global, self: global,
  matchMedia: () => ({ matches: false, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} }),
  scrollTo() {}, scrollBy() {}, devicePixelRatio: 1, innerWidth: 1200, innerHeight: 900,
  location: { hash: '', href: 'https://x/', pathname: '/', search: '' },
  history: { replaceState() {}, pushState() {} },
  localStorage: { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; } },
  sessionStorage: { getItem: () => null, setItem() {}, removeItem() {} },
  getComputedStyle: () => ({ getPropertyValue: k => (String(k).startsWith('--') ? '#336699' : '') }),
  requestAnimationFrame: f => { f(0); return 1; }, cancelAnimationFrame() {},
  setTimeout: (f, ms) => { timers.push(f); return timers.length; }, clearTimeout() {}, setInterval: () => 0, clearInterval() {},
  ResizeObserver: class { observe() {} unobserve() {} disconnect() {} },
  IntersectionObserver: class { observe() {} unobserve() {} disconnect() {} },
  MutationObserver: class { observe() {} disconnect() {} },
  addEventListener: (t, f) => { (W._wl[t] = W._wl[t] || []).push(f); }, removeEventListener() {},
  print() {}, alert() {}, confirm: () => true, open() {},
});
Object.defineProperty(global, 'navigator', { value: { userAgent: 'node', clipboard: { writeText: () => Promise.resolve() } }, configurable: true, writable: true });
global.Chart = class {
  constructor(el, cfg) { this.canvas = el; this.config = cfg; this.data = cfg.data; this.options = cfg.options; charts.push(this); this._probe(); }
  update() { this._probe(); } destroy() { const i = charts.indexOf(this); if (i >= 0) charts.splice(i, 1); } resize() {}
  _probe() { // kallar á svarföll (tooltip/ticks/label) með einföldu samhengi; villur hér skráðar sér
    try {
      const o = this.options || {}, ds = (this.data && this.data.datasets) || [];
      const ctx = (di, i) => ({ dataIndex: i, datasetIndex: di, dataset: ds[di] || {}, raw: ds[di] && ds[di].data ? ds[di].data[i] : 0,
        parsed: { x: i, y: ds[di] && ds[di].data ? +ds[di].data[i] || 0 : 0 }, label: this.data.labels ? this.data.labels[i] : '', formattedValue: '0', chart: this });
      const n = Math.min(3, (this.data.labels || []).length || (ds[0] && ds[0].data || []).length);
      const cbs = ((o.plugins || {}).tooltip || {}).callbacks || {};
      for (const [k, f] of Object.entries(cbs)) if (typeof f === 'function') for (let i = 0; i < n; i++) for (let d = 0; d < Math.max(1, ds.length); d++) {
        try { f.call({ chart: this }, /title|footer|after(Body|Title)|before(Body|Title)/.test(k) ? [ctx(d, i)] : ctx(d, i)); } catch (e) { cbErrors.push(`tooltip.${k}: ${e.message}`); }
      }
      for (const [ax, s] of Object.entries(o.scales || {})) if (s && s.ticks && typeof s.ticks.callback === 'function') for (let i = 0; i < Math.max(1, n); i++) {
        try { s.ticks.callback.call({ getLabelForValue: v => (this.data.labels || [])[v] }, i, i, []); } catch (e) { cbErrors.push(`scales.${ax}.ticks: ${e.message}`); }
      }
    } catch (e) { cbErrors.push('probe: ' + e.message); }
  }
};
global.Chart.defaults = { font: {}, plugins: { tooltip: {}, legend: { labels: {} } }, scale: { grid: {} }, elements: { line: {}, point: {}, bar: {} } };
global.Chart.register = () => {};
global.CSS = { escape: s => String(s) };

function flush(ctx) { let n = 0; while (timers.length && n++ < 200) { const f = timers.shift(); try { typeof f === 'function' && f(); } catch (e) { err(ctx + ' (timer)', e); } } }
function err(ctx, e) { errors.push(`${ctx}: ${e && e.stack ? e.stack.split('\n').slice(0, 3).join(' | ') : e}`); }

// 1) forskriftir
const scripts = [...html.matchAll(/<script(\s[^>]*)?>([\s\S]*?)<\/script>/gi)].filter(m => !/\bsrc=/.test(m[1] || '')).map(m => m[2]);
scripts.forEach((s, i) => { try { new vm.Script(s, { filename: `script${i}.js` }).runInThisContext(); } catch (e) { err(`script ${i}`, e); } });
flush('init');
for (const f of (doc._l.DOMContentLoaded || [])) { try { f(mkEvent('DOMContentLoaded')); } catch (e) { err('DOMContentLoaded', e); } }
for (const f of (W._wl.load || [])) { try { f(mkEvent('load')); } catch (e) { err('load', e); } }
flush('init');

const chartSnap = () => charts.map(c => ({ type: c.config.type, labels: c.data && c.data.labels, ds: ((c.data && c.data.datasets) || []).map(d => ({ label: d.label, data: d.data })), y: c.options && c.options.scales && c.options.scales.y ? { min: c.options.scales.y.min, max: c.options.scales.y.max } : null }));
const chartSnap0 = () => charts.map(c => ({ type: c.config.type, labels: c.data && c.data.labels, ds: ((c.data && c.data.datasets) || []).map(d => ({ label: d.label, data: d.data })) }));
const snaps = { init: doc.body.innerHTML };
const tabs = doc.querySelectorAll('[role=tab]');
for (const t of tabs) {
  const id = t.getAttribute('aria-controls');
  try { t.click(); flush('tab ' + id); } catch (e) { err('tab ' + id, e); }
  snaps['tab:' + id] = doc.body.innerHTML;
  snaps['charts:' + id] = JSON.stringify(chartSnap());
}
snaps.charts = JSON.stringify(chartSnap());
// grunsamleg úttök (undefined/NaN/Infinity) í sýnilegum texta eftir flipum
const warns = [];
for (const [k, h] of Object.entries(snaps)) {
  if (k.startsWith('charts')) continue;
  const txt = h.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/g, ' ').replace(/<[^>]+>/g, ' ');
  for (const w of ['undefined', 'NaN', 'Infinity', '[object Object]', 'null m', '–Infinity']) {
    let i = txt.indexOf(w); if (i >= 0) warns.push(`${k}: „${w}“ … ${txt.slice(Math.max(0, i - 60), i + 30).replace(/\s+/g, ' ')}`);
  }
}

// 3) fuzz
let nAct = 0;
if (!flag('--no-fuzz')) {
  const seen = new Set();
  const label = el => `${el.localName}${el.id ? '#' + el.id : ''}${el.className ? '.' + el.className.split(/\s+/).join('.') : ''}${[...el._attrs.keys()].filter(k => k.startsWith('data-')).map(k => `[${k}=${el.getAttribute(k)}]`).join('')}`;
  const crypto = require('crypto'); snaps.trace = [];
  const act = (ctx, fn) => { nAct++; try { fn(); flush(ctx); } catch (e) { err(ctx, e); }
    snaps.trace.push(ctx + ' → ' + crypto.createHash('md5').update(doc.body.innerHTML.replace(/<script[\s\S]*?<\/script>/g, '')).digest('hex').slice(0, 10)); };
  for (const t of tabs.length ? tabs : [null]) {
    const tid = t ? t.getAttribute('aria-controls') : 'page';
    if (t) act('tab ' + tid, () => t.click());
    const panel = t ? doc.getElementById(tid) : doc.body;
    if (!panel) continue;
    // selects og stikur
    for (const s of panel.querySelectorAll('select')) {
      const vals = s.options.map(o => o.value);
      for (const v of vals) act(`${tid} select#${s.id}=${v}`, () => { s.value = v; dispatch(s, mkEvent('change')); dispatch(s, mkEvent('input')); });
    }
    for (const r of panel.querySelectorAll('input')) {
      const ty = r.type;
      if (ty === 'range' || ty === 'number') {
        const mn = +r.min || 0, mx = r.max !== '' ? +r.max : mn + 10, orig = r.value;
        for (const v of [mn, mx, (mn + mx) / 2, orig]) act(`${tid} input#${r.id}=${v}`, () => { r.value = v; dispatch(r, mkEvent('input')); dispatch(r, mkEvent('change')); });
      } else if (ty === 'checkbox' || ty === 'radio') {
        act(`${tid} check#${r.id}`, () => { r.checked = !r.checked; dispatch(r, mkEvent('change')); dispatch(r, mkEvent('click')); });
        act(`${tid} check#${r.id}`, () => { r.checked = !r.checked; dispatch(r, mkEvent('change')); });
      } else if (ty === 'text' || ty === 'search' || ty === '') {
        act(`${tid} text#${r.id}`, () => { r.value = 'a'; dispatch(r, mkEvent('input')); r.value = ''; dispatch(r, mkEvent('input')); });
      }
    }
    // smellanleg
    const sel = 'button,a,[data-go],[data-nav],[data-k],[data-c],[data-s],[data-i],[data-j],[data-id],[data-acc],[data-cust],[data-v],[data-sort],[data-pt],[data-tab],tr[tabindex],[role=button],.drill,tr.cat,tr.click,[onclick]';
    let round = 0;
    const clicked = new Set();
    while (round++ < 3) {
      const els = panel.querySelectorAll(sel).filter(e => e.getAttribute('role') !== 'tab');
      let any = false;
      for (const el of els.slice(0, 300)) {
        const key = tid + label(el) + el.textContent.slice(0, 40);
        if (clicked.has(key)) continue; clicked.add(key); any = true;
        if (el.closest('[hidden]') && !el.closest('dialog')) continue;
        act(`${tid} click ${label(el)} "${el.textContent.trim().slice(0, 30)}"`, () => {
          el.click();
          dispatch(el, mkEvent('keydown', true, { key: 'Enter' }));
        });
        act(`${tid} Escape`, () => dispatch(doc.body, mkEvent('keydown', true, { key: 'Escape' })));
      }
      if (!any) break;
    }
    // selects aftur (valkostir geta hafa orðið til við smelli, t.d. ársfjórðungar)
    const inScope = e => panel.contains(e) || !e.closest('[role=tabpanel]');
    for (const b of doc.body.querySelectorAll('[data-pt]').filter(inScope)) {
      act(`${tid} click ${label(b)}`, () => b.click());
      for (const s of doc.body.querySelectorAll('select').filter(inScope)) for (const v of s.options.map(o => o.value)) act(`${tid} ${label(b)} select#${s.id}=${v}`, () => { s.value = v; dispatch(s, mkEvent('change')); });
    }
  }
}
const uniq = [...new Set(errors)];
const out = { file: path.basename(file), errors: uniq, warns, cbErrors: [...new Set(cbErrors)], actions: nAct, tabs: tabs.length, charts: charts.length };
if (opt('--snap')) fs.writeFileSync(opt('--snap'), JSON.stringify(snaps));
if (!flag('--quiet')) {
  console.log(`${out.file}: ${uniq.length ? uniq.length + ' VILLUR' : 'í lagi'} · flipar ${out.tabs} · aðgerðir ${nAct} · gröf ${charts.length}${out.cbErrors.length ? ' · svarfallsvillur ' + out.cbErrors.length : ''}`);
  uniq.slice(0, 30).forEach(e => console.log('  ✗ ' + e));
  out.cbErrors.slice(0, 10).forEach(e => console.log('  ~ ' + e));
  [...new Set(warns)].slice(0, 12).forEach(e => console.log('  ? ' + e));
}
if (flag('--json')) console.log(JSON.stringify(out));
process.exit(uniq.length ? 1 : 0);
