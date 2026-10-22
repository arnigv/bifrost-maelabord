#!/usr/bin/env python3
"""Leifaprófun tungumáls: finnur íslensku í enskri síðu eftir að allar forskriftir hafa keyrt.

Notkun: i18n_check.py síða.html snap.json --dash <mælaborð> [--lang en]
  snap.json kemur úr `node runtest.js síða.html --snap snap.json` (allir flipar teknir upp).
  --dash: heiti mælaborðs (stjorn, sjodstreymi …, eða bifrost-skyndiuttekt fyrir miðstöð).

Lokaður orðaforði: hvert orð á síðunni (sýnilegum texta eftir hvern flipa og öllum strengjum í kóða)
verður að koma fyrir í (a) þýðingum orðabóka (template/i18n/en.json og sameiginlegu), (b) gögnum síðunnar
(DATA, eftir yfirlag) eða (c) grunnorðum hér að neðan. Íslensk orð án broddstafa (t.d. „krafna“) finnast því líka.
Útgangskóði 1 ef eitthvað finnst.
"""
import json, os, re, sys, html as H
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import i18n_units as UN
from i18n_units import units

SKILLS = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
IS_CH = re.compile(r'[áéíóúýþæöðÁÉÍÓÚÝÞÆÖÐ]')
BASE = set('''a an the and or of to in on at by for from with without is are was be not no yes this that it its as per vs
jan feb mar apr may jun jul aug sep oct nov dec january february march april june july august september october november december
q1 q2 q3 q4 ytd isk m eur usd sek dkk nok gbp vat bc ebitda ebit p10 p50 p90 kpi kpis abc wip mrr arr nrr adr revpar dso id no
light dark blue earth colour theme close company hub dashboards breadcrumb tabs language english íslenska is en pp d wk e g i ie etc
bifröst bifrost claude cowork ehf hf sf ai tekjuleki stjorn sjodstreymi kostnadur manadarlok framlegd spagerd endurskodun sermaelabord'''.split())
WORD = re.compile(r'[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\-]*')


def words(s):
    return [w.strip('-') for w in WORD.findall(s) if w.strip('-')]


def page_data(page):
    m = re.search(r'const DATA\s*=\s*', page)
    if not m:
        return None
    obj, _ = json.JSONDecoder().raw_decode(page[m.end():])
    return obj


def strings(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)
    elif isinstance(o, str):
        yield o


def visible(h):
    h = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', ' ', h)
    attrs = ' '.join(m.group(2) for m in re.finditer(r'\s(title|aria-label|placeholder|alt)="([^"]*)"', h))
    return H.unescape(re.sub(r'<[^>]+>', '\n', h) + '\n' + attrs)


def vocab(dash, lang, data):
    v = set(BASE)
    files = [os.path.join(SKILLS, dash, 'template', 'i18n', lang + '.json'), os.path.join(SKILLS, 'bifrost-maelabord', 'assets', 'i18n', lang + '.json')]
    for f in files:
        if os.path.exists(f):
            for a, b in json.load(open(f, encoding='utf-8')):
                v |= {w.lower() for w in words(re.sub(r'<[^>]*>', ' ', b))}
                v |= {w.lower() for m in re.finditer(r'(?:title|aria-label|placeholder|alt|data-short)="([^"]*)"', b) for w in words(m.group(1))}
    pk = os.path.join(SKILLS, 'sermaelabord', 'assets', 'pakkar.json')
    if dash == 'bifrost-skyndiuttekt' and os.path.exists(pk):
        for p in json.load(open(pk, encoding='utf-8')):
            for s in strings(p.get(lang) or {}):
                v |= {w.lower() for w in words(s)}
    for k, sub in (data or {}).items():
        for s in strings(sub):
            # textar gervigreindar (meta/text/html/js) teljast aðeins ef þeir eru ekki á íslensku (yfirlag vantar þá)
            if k in ('meta', 'text', 'html', 'js') and IS_CH.search(s) and not (k == 'meta' and s in [sub.get(x) for x in ('company', 'company_short', 'company_gen', 'company_acc') if isinstance(sub, dict)]):
                continue
            v |= {w.lower() for w in words(s)}
    return v


def main():
    page_f, snap_f = sys.argv[1], sys.argv[2]
    opt = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    lang, dash = opt('--lang', 'en'), opt('--dash')
    page = open(page_f, encoding='utf-8').read()
    snaps = json.load(open(snap_f, encoding='utf-8'))
    data = page_data(page)
    extra = opt('--data')  # miðstöð: gögn (hub.json eftir yfirlag) sem orðaforði
    if extra:
        data = json.load(open(extra, encoding='utf-8'))
    V = vocab(dash, lang, data) if dash else None
    bad = {}

    def check(text, ctx):
        for w in words(text):
            lw = w.lower()
            if re.fullmatch(r'[A-ZÁÉÍÓÚÝÞÆÖÐ]{1,4}\d*', w) or len(lw) < 3:
                continue
            if lang == 'en' and (IS_CH.search(w) or V is not None) and not (V is not None and lw in V):
                bad.setdefault(w, ctx[:120])

    tonly = '--template-only' in sys.argv  # sleppa línum sem koma úr gögnum (til að prófa orðabók sniðmáts eina sér)
    dstr = [x for x in strings(data or {}) if len(x) > 3] if tonly else []
    texts = [visible(page)] + [visible(v) for k, v in snaps.items() if isinstance(v, str) and not k.startswith('charts') and k != 'trace']
    for t in texts:
        for line in t.split('\n'):
            if line.strip():
                ls = line.strip()
                if tonly and any(ls in x or (len(x) > 12 and x in ls) for x in dstr):
                    continue
                check(line, ls)
    if lang == 'en':
        code = re.sub(r'const DATA\s*=\s*\{.*?\};\n', '', page, flags=re.S)
        code = re.sub(r"const BF_LANG = '\w+';.*?\n\}\)\(\);", '', code, flags=re.S)  # components.js geymir bæði tungumál
        for u in units(code):
            if re.fullmatch(r'[a-z0-9_\-]+', u) or re.search(r'^[#.\[]|\[data-|\[role', u) or (' ' not in u.strip() and re.search(r'[:(]', u)) or re.match(r'\s*[\w-]+="', u):
                continue
            vis = re.sub(r'\$\{[^}]*\}', ' ', u)
            check(re.sub(r'<[^>]*>', ' ', vis), 'kóði: ' + u)
        # íslensk orð án broddstafa: orðaforði íslenska sniðmátsins sem er ekki enskur
        if dash and V is not None:
            tpl = os.path.join(SKILLS, dash, 'template', 'template.html')
            isv = {w.lower() for u in units(open(tpl, encoding='utf-8').read()) for w in words(re.sub(r'<[^>]*>|\{\{[^}]*\}\}', ' ', UN.strip_expr(u)))} - V
            UN.TEST = lambda t: bool(re.search(r'[A-Za-zÀ-ÿ]{2}', t))
            try:
                for u in units(code):
                    if re.fullmatch(r'[a-z0-9_\-]+', u) or re.search(r'^[#.\[]|\[data-|\[role', u) or (' ' not in u.strip() and re.search(r'[:(]', u)) or re.match(r'\s*[\w-]+="', u):
                        continue  # lyklar og veljarar, ekki texti
                    vis = re.sub(r'<[^>]*>', ' ', UN.strip_expr(u))
                    for w in words(vis):
                        if w.lower() in isv:
                            bad.setdefault(w, 'kóði: ' + u[:110])
            finally:
                UN.TEST = None
    if bad:
        print(f'{page_f}: {len(bad)} orð utan orðaforða ({lang})')
        for w, ctx in list(bad.items())[:60]:
            print(f'  ✗ {w:22} … {ctx}')
        sys.exit(1)
    print(f'{page_f}: engin íslenska utan sérnafna ({lang})')


if __name__ == '__main__':
    main()
