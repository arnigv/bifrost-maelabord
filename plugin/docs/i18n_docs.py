#!/usr/bin/env python3
"""Leiðbeiningar á tveimur tungumálum (IS | EN) í sömu skrá.

Síðurnar eru skrifaðar á íslensku. Enska er orðabók í i18n/<síða>.en.json:
  {"blocks": {"<íslenskt innerHTML>": "<enskt innerHTML>"}, "attrs": {"<íslenskt gildi>": "<enskt>"},
   "js": {"<íslenskur strengur í forskrift>": "<enskur>"}}
Lykill er íslenski textinn sjálfur (bilum þjappað), svo breyting á íslenskum texta án
þýðingar finnst strax (`check`).

Notkun:
  i18n_docs.py units  <síða.html> <út.json>     textablokkir, eiginleikar og JS-strengir sem þarf að þýða
  i18n_docs.py check  <síða.html>              hvað vantar í orðabókina (útgangskóði 1 ef eitthvað)
  i18n_docs.py build  <síða.html>              setur orðabók og rofa inn í síðuna (endurtakanlegt)

Rofinn: IS | EN í hausnum. Sjálfgefið: íslenska ef vafrinn er á íslensku, annars enska;
val notanda er munað (localStorage, ef leyft). Slóð með ?lang=en eða #…&lang=en þvingar.
"""
import html.parser, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
INLINE = set('a abbr b bdi br cite code em i kbd mark q s small span strong sub sup time u wbr'.split())
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())
SKIP = {'script', 'style', 'noscript', 'template'}
ATTRS = ('title', 'aria-label', 'placeholder', 'alt', 'data-copy', 'data-q')
LETTER = re.compile(r'[A-Za-zÁÉÍÓÚÝÞÆÖÐáéíóúýþæöð]{2}')
WS = re.compile(r'\s+')
START, END = '<!--i18n:start-->', '<!--i18n:end-->'
JSTART, JEND = '/*i18n:start*/', '/*i18n:end*/'   # inni í <script> (<!-- væri JS-athugasemd)


def norm(s):
    return WS.sub(' ', s).strip()


class Node:
    def __init__(s, tag, attrs, a, b, parent):
        s.tag, s.attrs, s.a, s.b, s.parent = tag, attrs, a, b, parent   # a,b: upphaf/endir byrjunarmerkis
        s.kids, s.end = [], None   # kids: Node eða ('t', a, b)


class P(html.parser.HTMLParser):
    def __init__(s, src):
        super().__init__(convert_charrefs=False)
        s.src = src
        s.lines = [0]
        for m in re.finditer('\n', src):
            s.lines.append(m.end())
        s.root = Node('#root', [], 0, 0, None)
        s.cur = s.root
        s.skip = 0

    def off(s):
        l, c = s.getpos()
        return s.lines[l - 1] + c

    def handle_starttag(s, tag, attrs):
        a = s.off(); b = a + len(s.get_starttag_text())
        if s.skip:
            if tag in SKIP: s.skip += 1
            return
        n = Node(tag, attrs, a, b, s.cur)
        s.cur.kids.append(n)
        if tag in SKIP:
            s.skip = 1; s.skipnode = n
        elif tag not in VOID:
            s.cur = n

    def handle_startendtag(s, tag, attrs):
        a = s.off(); b = a + len(s.get_starttag_text())
        if not s.skip:
            s.cur.kids.append(Node(tag, attrs, a, b, s.cur))

    def handle_endtag(s, tag):
        a = s.off()
        if s.skip:
            if tag in SKIP:
                s.skip -= 1
            return
        n = s.cur
        while n is not s.root and n.tag != tag:
            n = n.parent
        if n is s.root:
            return
        x = s.cur
        while x is not n:   # óloknuð merki (t.d. <li>, <p>)
            x.end = a; x = x.parent
        n.end = a
        s.cur = n.parent

    def _text(s, data):
        if s.skip:
            return
        a = s.off()
        s.cur.kids.append(('t', a, a + len(data)))

    handle_data = _text
    def handle_entityref(s, name): s._text('&' + name + ';')
    def handle_charref(s, name): s._text('&#' + name + ';')


def parse(src):
    p = P(src); p.feed(src); p.close()
    return p.root


def text_of(src, n):
    if isinstance(n, tuple):
        return src[n[1]:n[2]]
    return ''.join(text_of(src, k) for k in n.kids)


def inline_only(n):
    """Aðeins texti og línumerki (inline) undir n."""
    for k in n.kids:
        if isinstance(k, tuple):
            continue
        if k.tag not in INLINE or not inline_only(k):
            return False
    return True


def inner(src, n):
    return src[n.b:n.end] if n.end is not None else ''


def body_of(root):
    stack = [root]
    while stack:
        n = stack.pop()
        if not isinstance(n, tuple):
            if n.tag == 'body':
                return n
            stack += n.kids
    return root


def collect(src):
    """Skilar (blokkir, lausir textar, eiginleikar).
    blokk: Node sem hefur aðeins inline-innihald og bókstafi, og er ekki inline-barn slíkrar blokkar.
    laus texti: textabútur með bókstöfum beint undir blönduðu foreldri."""
    root = body_of(parse(src))
    blocks, loose, attrs = [], [], []

    def walk(n):
        for k in n.kids:
            if isinstance(k, tuple):
                if LETTER.search(src[k[1]:k[2]]):
                    loose.append(k)
                continue
            for an, av in k.attrs:
                if an in ATTRS and av and LETTER.search(av):
                    attrs.append((k, an, av))
            if k.tag in SKIP or any(an == 'data-noi18n' for an, _ in k.attrs):
                continue   # data-noi18n: forskrift skrifar innihaldið (tr())
            if k.end is not None and inline_only(k) and LETTER.search(text_of(src, k)) and k.tag not in ('option',):
                blocks.append(k)
                sub(k)
            else:
                walk(k)

    def sub(n):   # eiginleikar inni í blokk
        for k in n.kids:
            if not isinstance(k, tuple):
                for an, av in k.attrs:
                    if an in ATTRS and av and LETTER.search(av):
                        attrs.append((k, an, av))
                sub(k)

    walk(root)
    return blocks, loose, attrs


JS_STR = re.compile(r"'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"|`((?:[^`\\]|\\.)*)`")
IS_CH = re.compile(r'[áéíóúýþæöðÁÉÍÓÚÝÞÆÖÐ]')


def js_strings(src):
    """Strengir sem forskriftir þýða með tr(): tr('…'), heiti í DEMO ("n", "d") og línuheiti í rows."""
    out = []
    for m in re.finditer(r'<script>(.*?)</script>', src, re.S):
        code = m.group(1)
        if code.startswith('/* I18N */'):
            continue
        out += re.findall(r"tr\('((?:[^'\\]|\\.)*)'\)", code)
        out += re.findall(r'"[nd]": "([^"]+)"', code)
        out += re.findall(r"\['([^']+)',\s*'[a-z_]+',\s*-?1", code)
    seen, res = set(), []
    for v in out:
        if v not in seen:
            seen.add(v); res.append(v)
    return res


def dict_path(page):
    return os.path.join(HERE, 'i18n', os.path.splitext(os.path.basename(page))[0] + '.en.json')


def strip_built(src):
    src = re.sub(re.escape(JSTART) + r'.*?' + re.escape(JEND) + r'\n?', '', src, flags=re.S)
    return re.sub(re.escape(START) + r'.*?' + re.escape(END), '', src, flags=re.S)


def units(page):
    src = unmark(open(page, encoding='utf-8').read())
    blocks, loose, attrs = collect(src)
    B = []
    for n in blocks:
        k = norm(inner(src, n))
        if k not in B: B.append(k)
    for t in loose:
        k = norm(src[t[1]:t[2]])
        if k not in B: B.append(k)
    A = []
    for _, an, av in attrs:
        if av not in A: A.append(av)
    return {'blocks': B, 'attrs': A, 'js': js_strings(src)}


def check(page):
    u = units(page)
    D = json.load(open(dict_path(page), encoding='utf-8')) if os.path.exists(dict_path(page)) else {}
    miss = {k: [x for x in u[k] if x not in (D.get(k) or {})] for k in u}
    stale = {k: [x for x in (D.get(k) or {}) if x not in u[k]] for k in u}
    return miss, stale


RUNTIME = r"""
(function () {
  var D = JSON.parse(document.getElementById('i18n-en').textContent), cur = 'is';
  var B = [].map.call(document.querySelectorAll('[data-tr]'), function (el) { return [el, el.innerHTML, D.b[el.getAttribute('data-tr')]]; });
  var A = [].map.call(document.querySelectorAll('[data-tra]'), function (el) {
    var m = D.a[el.getAttribute('data-tra')] || {}, o = {}; Object.keys(m).forEach(function (k) { o[k] = el.getAttribute(k); }); return [el, o, m]; });
  var TITLE = document.title;
  window.I18N_T = function (s) { return cur === 'en' && D.js[s] != null ? D.js[s] : s; };
  function set(l) {
    cur = l;
    document.documentElement.lang = l;
    B.forEach(function (x) { x[0].innerHTML = l === 'en' && x[2] != null ? x[2] : x[1]; });
    A.forEach(function (x) { Object.keys(x[2]).forEach(function (k) { x[0].setAttribute(k, l === 'en' ? x[2][k] : x[1][k]); }); });
    document.title = l === 'en' && D.title ? D.title : TITLE;
    document.querySelectorAll('.lang-sw button').forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.l === l); });
    try { localStorage.setItem('bf-guide-lang', l); } catch (e) {}
    (window.I18N_ON || []).forEach(function (f) { f(l); });
  }
  window.I18N_SET = set;
  window.I18N_LANG = function () { return cur; };
  document.querySelectorAll('.lang-sw button').forEach(function (b) { b.onclick = function () { set(b.dataset.l); }; });
  var q = (location.search + location.hash).match(/lang=(is|en)/), l = q && q[1];
  if (!l) { try { l = localStorage.getItem('bf-guide-lang'); } catch (e) {} }
  if (!l) l = /^is\b/i.test(navigator.language || '') ? 'is' : 'en';
  window.I18N_INIT = function () { set(l); };
})();
"""

SWITCH = ('<div class="lang-sw" role="group" aria-label="Tungumál · Language">'
          '<button type="button" data-l="is" lang="is" title="Íslenska">IS</button>'
          '<button type="button" data-l="en" lang="en" title="English">EN</button></div>')
CSS = ('<style>.lang-sw{display:inline-flex;background:var(--panel);border:1px solid var(--line);border-radius:999px;padding:3px;flex:none}'
       '.lang-sw button{font:inherit;font-size:.78rem;font-weight:700;letter-spacing:.03em;border:0;background:none;color:var(--muted);padding:6px 11px;border-radius:999px;cursor:pointer;min-height:36px}'
       '.lang-sw button[aria-pressed="true"]{background:var(--brand);color:#fff}'
       '.lang-sw button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}'
       '@media (max-width:760px){.lang-sw{order:2}.lang-sw button{padding:6px 9px}}</style>')


def unmark(src):
    src = strip_built(src)
    src = re.sub(r'<span data-trw="\d+">(.*?)</span data-trw>', r'\1', src, flags=re.S)
    src = re.sub(r' data-tra?="\d+"', '', src)
    return src


def build(page):
    src = unmark(open(page, encoding='utf-8').read())
    open(page, 'w', encoding='utf-8').write(src)
    miss, _ = check(page)
    n = sum(len(v) for v in miss.values())
    if n:
        sys.exit(f'{page}: {n} þýðingar vantar (keyrðu check)')
    D = json.load(open(dict_path(page), encoding='utf-8'))
    blocks, loose, attrs = collect(src)
    ins = []          # (staða, texti) innsetningar
    Bn, An = {}, {}
    for i, nd in enumerate(blocks):
        ins.append((nd.b - 1 if src[nd.b - 2] != '/' else nd.b - 2, f' data-tr="{i}"'))
        Bn[str(i)] = D['blocks'][norm(inner(src, nd))]
    j = len(blocks)
    for t in loose:
        raw = src[t[1]:t[2]]; k = norm(raw)
        lead = raw[:len(raw) - len(raw.lstrip())]; trail = raw[len(raw.rstrip()):]
        ins.append((t[1] + len(lead), f'<span data-trw="{j}" data-tr="{j}">'))
        ins.append((t[2] - len(trail), '</span data-trw>'))
        Bn[str(j)] = D['blocks'][k]; j += 1
    byel = {}
    for nd, an, av in attrs:
        byel.setdefault(id(nd), (nd, {}))[1][an] = D['attrs'][av]
    for i, (nd, m) in enumerate(byel.values()):
        pos = nd.b - 1 if src[nd.b - 2] != '/' else nd.b - 2
        ins.append((pos, f' data-tra="{i}"')); An[str(i)] = m
    for pos, txt in sorted(ins, key=lambda x: -x[0]):
        src = src[:pos] + txt + src[pos:]
    U = units(page)
    data = json.dumps({'b': Bn, 'a': An, 'js': {x: D['js'][x] for x in U['js']}, 'title': D.get('title')}, ensure_ascii=False).replace('</', '<\\/')
    js = RUNTIME
    src = re.sub(r'(<div class="tg" role="group".*?</div>)', lambda m: m.group(1) + START + SWITCH + END, src, count=1, flags=re.S)
    tail = (START + CSS + f'<script type="application/json" id="i18n-en">{data}</script>\n'
            f'<script>/* I18N */{js}</script>' + END)
    i = src.rfind('<script>\n')
    src = src[:i] + tail + src[i:]
    # síðasta forskriftin ræsir tungumálið þegar allt er tilbúið
    k = src.rfind('</script>')
    src = src[:k] + JSTART + "if (window.I18N_INIT) I18N_INIT();" + JEND + "\n" + src[k:]
    open(page, 'w', encoding='utf-8').write(src)
    print(f'{os.path.basename(page)}: {len(Bn)} bútar, {len(An)} eiginleikar, {len(U["js"])} JS-strengir · IS | EN')


if __name__ == '__main__':
    cmd, page = sys.argv[1], sys.argv[2]
    if cmd == 'units':
        u = units(page)
        json.dump(u, open(sys.argv[3], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print({k: len(v) for k, v in u.items()})
    elif cmd == 'check':
        miss, stale = check(page)
        for k in miss:
            for x in miss[k]:
                print(f'vantar {k}: {x[:120]}')
            for x in stale[k]:
                print(f'úrelt {k}: {x[:120]}')
        n = sum(len(v) for v in miss.values())
        print(f'{os.path.basename(page)}: {n} vantar, {sum(len(v) for v in stale.values())} úrelt')
        sys.exit(1 if n else 0)
    elif cmd == 'build':
        build(page)
