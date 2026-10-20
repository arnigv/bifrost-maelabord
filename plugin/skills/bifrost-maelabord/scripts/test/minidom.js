// Lítið DOM fyrir node-prófanir á mælaborðum (engin ytri pakki). Styður það sem sniðmátin nota.
'use strict';
const VOID = new Set('area base br col embed hr img input link meta source track wbr'.split(' '));
const RAW = new Set(['script', 'style', 'textarea']);
const ENT = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', '#39': "'" };
const decode = s => s.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+\d*);/gi, (m, e) => {
  if (e[0] === '#') return String.fromCodePoint(e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : +e.slice(1));
  return ENT[e] != null ? ENT[e] : m;
});
const escT = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/ /g, '&nbsp;');
const escA = s => String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;');

class Text { constructor(t) { this.nodeType = 3; this.data = t; this.parentNode = null; } get textContent() { return this.data; } }

function parseInto(parent, html) {
  const re = /<!--[\s\S]*?-->|<![^>]*>|<\/([a-zA-Z][\w-]*)\s*>|<([a-zA-Z][\w-]*)((?:\s+[^\s=\/>]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?)*)\s*(\/?)>/g;
  const stack = [parent]; let last = 0, m;
  const top = () => stack[stack.length - 1];
  const text = t => { if (t) top()._add(new Text(decode(t))); };
  while ((m = re.exec(html))) {
    text(html.slice(last, m.index)); last = re.lastIndex;
    if (m[1]) { // sluttag
      const n = m[1].toLowerCase();
      for (let i = stack.length - 1; i > 0; i--) if (stack[i].localName === n) { stack.length = i; break; }
      continue;
    }
    if (!m[2]) continue;
    const name = m[2].toLowerCase(), el = new Element(name, parent.ownerDocument);
    const ar = /([^\s=\/>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g; let a;
    while ((a = ar.exec(m[3] || ''))) el._attrs.set(a[1].toLowerCase(), decode(a[2] ?? a[3] ?? a[4] ?? ''));
    // óbein lokun
    const t = top();
    if (name === 'option' && t.localName === 'option') stack.pop();
    if ((name === 'tr') && (top().localName === 'td' || top().localName === 'th')) { while (stack.length > 1 && top().localName !== 'tr') stack.pop(); stack.pop(); }
    if ((name === 'td' || name === 'th') && (top().localName === 'td' || top().localName === 'th')) stack.pop();
    if (name === 'li' && top().localName === 'li') stack.pop();
    top()._add(el);
    if (RAW.has(name)) {
      const end = html.toLowerCase().indexOf('</' + name, last);
      const body = end < 0 ? html.slice(last) : html.slice(last, end);
      if (body) el._add(new Text(name === 'textarea' ? decode(body) : body));
      el._raw = true;
      if (end < 0) { last = html.length; break; }
      const close = html.indexOf('>', end); last = close + 1; re.lastIndex = last;
      continue;
    }
    if (!VOID.has(name) && !m[4]) stack.push(el);
  }
  text(html.slice(last));
}

// ---- veljarar ----
function parseSel(sel) {
  return sel.split(/\s*,\s*(?![^\[]*\])(?![^(]*\))/).map(g => {
    const parts = []; let comb = ' ';
    const toks = g.trim().match(/(\s*>\s*|\s+|(?:[^\s>\[(]+|\[[^\]]*\]|\([^)]*\))+)/g) || [];
    for (const t of toks) {
      if (/^\s*>\s*$/.test(t)) { comb = '>'; continue; }
      if (/^\s+$/.test(t)) { if (comb !== '>') comb = ' '; continue; }
      parts.push({ comb, c: parseCompound(t) }); comb = ' ';
    }
    return parts;
  });
}
function parseCompound(s) {
  const c = { tag: null, id: null, cls: [], attrs: [], pseudo: [] };
  const re = /^(\*|[a-zA-Z][\w-]*)|#([\w-]+)|\.([\w-]+)|\[\s*([\w-]+)\s*(?:([\^$*~|]?=)\s*(?:"([^"]*)"|'([^']*)'|([^\]\s]*)))?\s*\]|:([\w-]+)(?:\(([^)]*)\))?/g;
  let m;
  while ((m = re.exec(s)) && m[0]) {
    if (m[1]) c.tag = m[1] === '*' ? null : m[1].toLowerCase();
    else if (m[2]) c.id = m[2];
    else if (m[3]) c.cls.push(m[3]);
    else if (m[4]) c.attrs.push({ n: m[4].toLowerCase(), op: m[5], v: m[6] ?? m[7] ?? m[8] });
    else if (m[9]) c.pseudo.push({ n: m[9], arg: m[10] });
  }
  return c;
}
function matchCompound(el, c) {
  if (c.tag && el.localName !== c.tag) return false;
  if (c.id && el.getAttribute('id') !== c.id) return false;
  if (c.cls.length) { const cl = (el.getAttribute('class') || '').split(/\s+/); if (!c.cls.every(x => cl.includes(x))) return false; }
  for (const a of c.attrs) {
    const v = el.getAttribute(a.n); if (v == null) return false;
    if (!a.op) continue;
    if (a.op === '=' && v !== a.v) return false;
    if (a.op === '^=' && !v.startsWith(a.v)) return false;
    if (a.op === '$=' && !v.endsWith(a.v)) return false;
    if (a.op === '*=' && !v.includes(a.v)) return false;
    if (a.op === '~=' && !v.split(/\s+/).includes(a.v)) return false;
  }
  for (const p of c.pseudo) {
    if (p.n === 'checked' && !el.checked) return false;
    if (p.n === 'not' && el.matches(p.arg)) return false;
    if (p.n === 'first-child' && el.parentNode && el.parentNode.children[0] !== el) return false;
    if (p.n === 'last-child' && el.parentNode && el.parentNode.children.at(-1) !== el) return false;
  }
  return true;
}
function matchParts(el, parts, i) {
  if (!matchCompound(el, parts[i].c)) return false;
  if (i === 0) return true;
  const comb = parts[i].comb;
  let p = el.parentNode;
  if (comb === '>') return p && p.nodeType === 1 && matchParts(p, parts, i - 1);
  while (p && p.nodeType === 1) { if (matchParts(p, parts, i - 1)) return true; p = p.parentNode; }
  return false;
}
const selCache = new Map();
function matches(el, sel) {
  if (!selCache.has(sel)) selCache.set(sel, parseSel(sel));
  return selCache.get(sel).some(parts => parts.length && matchParts(el, parts, parts.length - 1));
}

const camel2kebab = k => k.replace(/[A-Z]/g, c => '-' + c.toLowerCase());
class Element {
  constructor(name, doc) {
    this.nodeType = 1; this.localName = name; this.tagName = name.toUpperCase(); this.nodeName = this.tagName;
    this._attrs = new Map(); this.childNodes = []; this.parentNode = null; this.ownerDocument = doc; this._l = {};
    this.style = { setProperty(k, v) { this[k] = v; }, removeProperty(k) { delete this[k]; }, getPropertyValue(k) { return this[k] || ''; } };
    this.scrollTop = 0; this.scrollLeft = 0;
  }
  _add(n) { n.parentNode = this; this.childNodes.push(n); return n; }
  get children() { return this.childNodes.filter(n => n.nodeType === 1); }
  get parentElement() { return this.parentNode && this.parentNode.nodeType === 1 ? this.parentNode : null; }
  get firstElementChild() { return this.children[0] || null; }
  get lastElementChild() { return this.children.at(-1) || null; }
  get firstChild() { return this.childNodes[0] || null; }
  get nextElementSibling() { const s = this.parentNode ? this.parentNode.children : []; return s[s.indexOf(this) + 1] || null; }
  get previousElementSibling() { const s = this.parentNode ? this.parentNode.children : []; const i = s.indexOf(this); return i > 0 ? s[i - 1] : null; }
  getAttribute(k) { k = k.toLowerCase(); return this._attrs.has(k) ? this._attrs.get(k) : null; }
  setAttribute(k, v) { this._attrs.set(k.toLowerCase(), String(v)); }
  removeAttribute(k) { this._attrs.delete(k.toLowerCase()); }
  hasAttribute(k) { return this._attrs.has(k.toLowerCase()); }
  toggleAttribute(k, f) { const on = f === undefined ? !this.hasAttribute(k) : !!f; on ? this.setAttribute(k, '') : this.removeAttribute(k); return on; }
  get id() { return this.getAttribute('id') || ''; } set id(v) { this.setAttribute('id', v); }
  get className() { return this.getAttribute('class') || ''; } set className(v) { this.setAttribute('class', v); }
  get classList() {
    const el = this, get = () => (el.getAttribute('class') || '').split(/\s+/).filter(Boolean), put = a => el.setAttribute('class', a.join(' '));
    return { add: (...c) => put([...new Set(get().concat(c))]), remove: (...c) => put(get().filter(x => !c.includes(x))),
      toggle: (c, f) => { const has = get().includes(c), on = f === undefined ? !has : !!f; on ? put([...new Set(get().concat([c]))]) : put(get().filter(x => x !== c)); return on; },
      contains: c => get().includes(c), get length() { return get().length; } };
  }
  get dataset() {
    const el = this;
    return new Proxy({}, { get: (t, k) => typeof k === 'string' ? (el.getAttribute('data-' + camel2kebab(k)) ?? undefined) : undefined,
      set: (t, k, v) => { el.setAttribute('data-' + camel2kebab(k), v); return true; },
      has: (t, k) => el.hasAttribute('data-' + camel2kebab(k)),
      deleteProperty: (t, k) => { el.removeAttribute('data-' + camel2kebab(k)); return true; },
      ownKeys: () => [...el._attrs.keys()].filter(k => k.startsWith('data-')).map(k => k.slice(5).replace(/-([a-z])/g, (m, c) => c.toUpperCase())),
      getOwnPropertyDescriptor: () => ({ enumerable: true, configurable: true }) });
  }
  get hidden() { return this.hasAttribute('hidden'); } set hidden(v) { v ? this.setAttribute('hidden', '') : this.removeAttribute('hidden'); }
  get disabled() { return this.hasAttribute('disabled'); } set disabled(v) { v ? this.setAttribute('disabled', '') : this.removeAttribute('disabled'); }
  get open() { return this.hasAttribute('open'); } set open(v) { v ? this.setAttribute('open', '') : this.removeAttribute('open'); }
  get tabIndex() { return +(this.getAttribute('tabindex') ?? -1); } set tabIndex(v) { this.setAttribute('tabindex', v); }
  get title() { return this.getAttribute('title') || ''; } set title(v) { this.setAttribute('title', v); }
  get href() { return this.getAttribute('href') || ''; }
  get type() { return this.getAttribute('type') || ''; }
  get name() { return this.getAttribute('name') || ''; }
  get min() { return this.getAttribute('min') || ''; } get max() { return this.getAttribute('max') || ''; } get step() { return this.getAttribute('step') || ''; }
  get checked() { return this._checked !== undefined ? this._checked : this.hasAttribute('checked'); } set checked(v) { this._checked = !!v; }
  get selected() { return this._selected !== undefined ? this._selected : this.hasAttribute('selected'); } set selected(v) { this._selected = !!v; }
  get options() { return this.querySelectorAll('option'); }
  get selectedIndex() { const o = this.options; const i = o.findIndex(x => x.selected); return i < 0 ? (o.length ? 0 : -1) : i; }
  set selectedIndex(i) { this.options.forEach((o, j) => o.selected = j === i); }
  get value() {
    if (this.localName === 'select') { const o = this.options[this.selectedIndex]; return o ? o.value : ''; }
    if (this.localName === 'option') return this.getAttribute('value') ?? this.textContent;
    if (this.localName === 'textarea') return this._value ?? this.textContent;
    return this._value !== undefined ? this._value : (this.getAttribute('value') ?? (this.type === 'checkbox' || this.type === 'radio' ? 'on' : ''));
  }
  set value(v) {
    if (this.localName === 'select') { const o = this.options; let hit = false; o.forEach(x => { x.selected = !hit && x.value === String(v); if (x.selected) hit = true; }); if (!hit) o.forEach(x => x.selected = false), this._none = true; return; }
    this._value = String(v);
  }
  get valueAsNumber() { return +this.value; }
  get textContent() { return this.childNodes.map(n => n.textContent).join(''); }
  set textContent(t) { this.childNodes.forEach(n => n.parentNode = null); this.childNodes = []; if (t != null && t !== '') this._add(new Text(String(t))); }
  get innerText() { return this.textContent; } set innerText(t) { this.textContent = t; }
  get innerHTML() { return this.childNodes.map(n => ser(n, this._raw)).join(''); }
  set innerHTML(h) { this.childNodes.forEach(n => n.parentNode = null); this.childNodes = []; parseInto(this, String(h)); }
  get outerHTML() { return ser(this); }
  insertAdjacentHTML(pos, h) {
    const tmp = new Element('div', this.ownerDocument); parseInto(tmp, h); const nodes = tmp.childNodes;
    if (pos === 'beforeend') nodes.forEach(n => this._add(n));
    else if (pos === 'afterbegin') { nodes.forEach(n => n.parentNode = this); this.childNodes.unshift(...nodes); }
    else if (this.parentNode) { const s = this.parentNode.childNodes, i = s.indexOf(this) + (pos === 'afterend' ? 1 : 0); nodes.forEach(n => n.parentNode = this.parentNode); s.splice(i, 0, ...nodes); }
  }
  appendChild(n) { if (n.parentNode) n.parentNode.removeChild(n); return this._add(n); }
  append(...ns) { ns.forEach(n => this.appendChild(typeof n === 'string' ? new Text(n) : n)); }
  prepend(...ns) { ns.reverse().forEach(n => { n = typeof n === 'string' ? new Text(n) : n; n.parentNode = this; this.childNodes.unshift(n); }); }
  insertBefore(n, ref) { if (n.parentNode) n.parentNode.removeChild(n); const i = ref ? this.childNodes.indexOf(ref) : -1; n.parentNode = this; i < 0 ? this.childNodes.push(n) : this.childNodes.splice(i, 0, n); return n; }
  removeChild(n) { const i = this.childNodes.indexOf(n); if (i >= 0) this.childNodes.splice(i, 1); n.parentNode = null; return n; }
  replaceChildren(...ns) { this.childNodes = []; this.append(...ns); }
  remove() { if (this.parentNode) this.parentNode.removeChild(this); }
  contains(n) { while (n) { if (n === this) return true; n = n.parentNode; } return false; }
  cloneNode(deep) { const e = new Element(this.localName, this.ownerDocument); this._attrs.forEach((v, k) => e._attrs.set(k, v)); if (deep) parseInto(e, this.innerHTML); return e; }
  _all(out = []) { for (const c of this.childNodes) if (c.nodeType === 1) { out.push(c); c._all(out); } return out; }
  querySelectorAll(sel) { return this._all().filter(e => matches(e, sel)); }
  querySelector(sel) { return this._all().find(e => matches(e, sel)) || null; }
  getElementsByTagName(t) { return this._all().filter(e => t === '*' || e.localName === t.toLowerCase()); }
  getElementsByClassName(c) { return this.querySelectorAll('.' + c.trim().split(/\s+/).join('.')); }
  matches(sel) { return matches(this, sel); }
  closest(sel) { let e = this; while (e && e.nodeType === 1) { if (matches(e, sel)) return e; e = e.parentNode; } return null; }
  addEventListener(t, f) { (this._l[t] = this._l[t] || []).push(f); }
  removeEventListener(t, f) { this._l[t] = (this._l[t] || []).filter(x => x !== f); }
  dispatchEvent(ev) { return dispatch(this, ev); }
  click() { dispatch(this, mkEvent('click')); }
  focus() { this.ownerDocument.activeElement = this; } blur() {}
  scrollIntoView() {} scrollTo() {} scrollBy() {}
  showModal() { this.open = true; } show() { this.open = true; } close() { this.open = false; dispatch(this, mkEvent('close', false)); }
  getBoundingClientRect() { return { width: 300, height: 150, top: 0, left: 0, right: 300, bottom: 150, x: 0, y: 0 }; }
  get clientWidth() { return 300; } get clientHeight() { return 150; } get offsetWidth() { return 300; } get offsetHeight() { return 150; }
  get scrollWidth() { return 300; } get scrollHeight() { return 150; } get offsetTop() { return 0; } get offsetLeft() { return 0; }
  getContext() { return new Proxy({}, { get: (t, k) => k === 'measureText' ? () => ({ width: 10 }) : (k in t ? t[k] : () => ({ addColorStop() {} })), set: (t, k, v) => (t[k] = v, true) }); }
  animate() { return { finished: Promise.resolve(), cancel() {} }; }
}
function ser(n, raw) {
  if (n.nodeType === 3) return raw ? n.data : escT(n.data);
  let s = '<' + n.localName; n._attrs.forEach((v, k) => { s += ' ' + k + (v === '' ? '' : '="' + escA(v) + '"'); }); s += '>';
  if (VOID.has(n.localName)) return s;
  return s + n.childNodes.map(c => ser(c, n._raw)).join('') + '</' + n.localName + '>';
}
function mkEvent(type, bubbles = true, extra = {}) {
  return Object.assign({ type, bubbles, defaultPrevented: false, _stop: false, preventDefault() { this.defaultPrevented = true; }, stopPropagation() { this._stop = true; }, stopImmediatePropagation() { this._stop = true; } }, extra);
}
function dispatch(el, ev) {
  ev.target = ev.target || el;
  let cur = el;
  while (cur) {
    ev.currentTarget = cur;
    const h = cur['on' + ev.type]; if (typeof h === 'function') h.call(cur, ev);
    for (const f of (cur._l[ev.type] || []).slice()) f.call(cur, ev);
    if (!ev.bubbles || ev._stop) break;
    cur = cur.parentNode || (cur !== cur.ownerDocument && cur.nodeType === 1 ? cur.ownerDocument : null);
    if (cur && cur.nodeType === 9) { // document
      const h2 = cur['on' + ev.type]; if (typeof h2 === 'function') h2.call(cur, ev);
      for (const f of (cur._l[ev.type] || []).slice()) f.call(cur, ev);
      if (cur.defaultView && !ev._stop) for (const f of (cur.defaultView._wl[ev.type] || []).slice()) f.call(cur.defaultView, ev);
      break;
    }
  }
  return !ev.defaultPrevented;
}
class Document {
  constructor(html) {
    this.nodeType = 9; this._l = {}; this.activeElement = null;
    this._root = new Element('#root', this);
    parseInto(this._root, html);
    this.documentElement = this._root.querySelector('html') || this._root;
    this.body = this._root.querySelector('body') || this.documentElement;
    this.head = this._root.querySelector('head') || this.documentElement;
    this.documentElement.parentNode = null;
    this._root.childNodes.forEach(n => { if (n !== this.documentElement && this.documentElement !== this._root) {} });
  }
  getElementById(id) { return this._root.querySelector('#' + CSS_esc(id)) || this._root._all().find(e => e.getAttribute('id') === id) || null; }
  querySelector(s) { return this._root.querySelector(s); }
  querySelectorAll(s) { return this._root.querySelectorAll(s); }
  getElementsByTagName(t) { return this._root.getElementsByTagName(t); }
  getElementsByClassName(c) { return this._root.getElementsByClassName(c); }
  createElement(t) { return new Element(t.toLowerCase(), this); }
  createTextNode(t) { return new Text(t); }
  createDocumentFragment() { return new Element('#frag', this); }
  addEventListener(t, f) { (this._l[t] = this._l[t] || []).push(f); }
  removeEventListener(t, f) { this._l[t] = (this._l[t] || []).filter(x => x !== f); }
}
const CSS_esc = s => /^[\w-]+$/.test(s) ? s : '___no___';
module.exports = { Document, Element, Text, mkEvent, dispatch, ser };
