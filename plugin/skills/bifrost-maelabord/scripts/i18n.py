#!/usr/bin/env python3
"""Bifröst mælaborð: tungumál (íslenska / enska).

Sniðmátin eru skrifuð á íslensku. Önnur tungumál eru orðabækur með hráum bútum úr sniðmátinu:
  skills/<mælaborð>/template/i18n/<lang>.json   [[íslenskur bútur, þýðing], ...]
  skills/bifrost-maelabord/assets/i18n/<lang>.json   sameiginlegt (components.js, leiðarstika, rofi)
  skills/bifrost-maelabord/assets/i18n/accounts.<lang>.json   {íslenskt lyklaheiti: þýðing} (staðallyklarammi)
Orðabók er ströng: bútur sem finnst ekki í sniðmátinu stöðvar smíðina (orðabókin er þá úrelt).

Tungumál gagna:
  - `lang` í gögnum ræður ("is" / "en"), annars `detect_lang(gögn)`: íslenska ef heiti úr BC
    (lyklar, viðskiptavinir, birgjar, félag) eru að verulegu leyti á íslensku, annars enska.
  - Textar sem gervigreindin skrifar (meta, text, html, js) eru á tungumáli gagnanna.
    Hitt tungumálið kemur sem yfirlag: gögn["i18n"]["en"] = {"meta": {...}, "text": {...}, "js": {...}, "html": {...}, "names": {"íslenskur strengur": "þýðing"}}.
    `names` (og staðaltaflan accounts.<lang>.json) þýða heila strengi í gögnunum, t.d. lyklaheiti og heiti áætlana.
Smíðuð eru tvö eintök hverrar síðu: aðaltungumálið í `<síða>.html` og hitt í `<síða>.<lang>.html`,
með rofanum „IS | EN“ efst sem flytur á milli þeirra.
"""
import copy, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.normpath(os.path.join(HERE, '..', '..'))
ASSETS = os.path.join(HERE, '..', 'assets')
LANGS = ('is', 'en')
LABEL = {'is': 'IS', 'en': 'EN'}
NAME = {'is': 'Íslenska', 'en': 'English'}
IS_CH = re.compile(r'[áéíóúýþæðÁÉÍÓÚÝÞÆÐ]')   # ö er líka í sænsku/þýsku og telst ekki ein og sér
NON_IS = re.compile(r'[øåäüßñçèàâêôõãìòùÅÄØÜ]')  # stafir sem eru ekki í íslensku
IS_WORDS = set('''og eða er eru á í af til frá með um fyrir eftir án ekki sem
sala laun tekjur vörur vara kostnaður gjöld skuldir eignir eigið fé banki sjóður lán vextir
afskriftir húsaleiga rafmagn hiti tryggingar viðskiptamenn lánardrottnar innlendir erlendir tengdir
útskattur innskattur virðisaukaskattur vsk ehf hf sf samtals reikningur verk þjónusta efni
'''.split())
EN_WORDS = set('''and or of to from with for the in on at by sales revenue cost costs expense expenses
income salaries wages rent bank cash loan loans interest depreciation insurance customers vendors
payable receivable inventory tax vat total account service services materials other general
'''.split())


def other(lang):
    return 'en' if lang == 'is' else 'is'


def _strings(obj, skip=('meta', 'text', 'html', 'js', 'i18n', '_maps')):
    """Strengir úr gögnum sem koma úr BC (heiti), ekki textar gervigreindar."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in skip:
                continue
            if isinstance(v, str) and k.lower() in ('name', 'company', 'heiti', 'description', 'desc', 'nafn', 'customer', 'vendor', 'title', 'label'):
                out.append(v)
            else:
                out += _strings(v, ())
    elif isinstance(obj, list):
        for v in obj[:400]:
            out += [v] if isinstance(v, str) else _strings(v, ())
    return out


def detect_lang(data, default='is'):
    """Greinir tungumál grunngagna. Íslenska ef ≥ 25% heita bera íslensk einkenni og þau eru
    fleiri en ensk einkenni; annars enska. Of fá heiti (< 5): sjálfgefið."""
    names = [s for s in _strings(data) if isinstance(s, str) and re.search(r'[A-Za-zÀ-ÿ]{3}', s)]
    if len(names) < 5:
        return default
    isc = enc = 0
    for s in names:
        w = set(re.findall(r'[a-zà-ÿ]+', s.lower()))
        if NON_IS.search(s):
            enc += 1
        elif IS_CH.search(s) or (w & IS_WORDS):
            isc += 1
        elif w & EN_WORDS:
            enc += 1
    if isc / len(names) >= 0.25 and isc >= enc:
        return 'is'
    return 'en'


def data_lang(data, override=None):
    lang = override or data.get('lang') or (data.get('meta') or {}).get('lang') or detect_lang(data)
    return lang if lang in LANGS else 'en'


def _load(path, kind=list):
    return json.load(open(path, encoding='utf-8')) if os.path.exists(path) else kind()


def pairs_for(name, lang):
    if lang == 'is':
        return []
    return _load(os.path.join(SKILLS, name, 'template', 'i18n', lang + '.json'))


def shared_pairs(lang):
    if lang == 'is':
        return []
    return _load(os.path.join(ASSETS, 'i18n', lang + '.json'))


def account_names(lang):
    return {} if lang == 'is' else _load(os.path.join(ASSETS, 'i18n', 'accounts.' + lang + '.json'), dict)


def translate(text, pairs, where='', strict=True):
    """Skiptir hráum bútum út í röð (lengstu fyrst). strict: bútur sem finnst ekki = villa."""
    miss = []
    for a, b in sorted(pairs, key=lambda p: -len(p[0])):
        if a in text:
            text = text.replace(a, b)
        else:
            miss.append(a)
    if strict and miss:
        raise SystemExit(f'Orðabók {where}: {len(miss)} bútar finnast ekki í sniðmátinu (úrelt orðabók):\n  ' + '\n  '.join(m[:100] for m in miss[:15]))
    return text, miss


def _merge(base, over):
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _merge(base[k], v)
        else:
            base[k] = v


def localize_data(data, lang):
    """Gögn fyrir tungumál `lang`: yfirlag úr data['i18n'][lang] og þýðing lyklaheita."""
    d = copy.deepcopy(data)
    src = data_lang(data)
    d['lang'] = lang
    if lang == src:
        return d
    ov = (data.get('i18n') or {}).get(lang) or {}
    for sec in ('meta', 'text', 'html', 'js'):
        if sec in ov:
            d.setdefault(sec, {})
            _merge(d[sec], ov[sec])
    for k, v in ov.items():
        if k not in ('meta', 'text', 'html', 'js', 'names'):
            d[k] = v
    names = dict(account_names(lang))
    names.update(ov.get('names') or {})

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ('meta', 'text', 'html', 'js', 'i18n'):
                    continue
                if isinstance(v, str) and v in names:
                    o[k] = names[v]
                else:
                    walk(v)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                if isinstance(v, str) and v in names:
                    o[i] = names[v]
                else:
                    walk(v)
    if names:
        walk(d)
    return d


PROPER = {'company', 'company_short', 'short', 'environment', 'env', 'initials', 'entity'}


def missing_overlay(data, lang):
    """Hvaða textahlutar vantar í yfirlag fyrir `lang` (aðvörun, ekki villa)."""
    if lang == data_lang(data):
        return []
    ov = (data.get('i18n') or {}).get(lang) or {}
    out = []
    for sec in ('meta', 'text', 'html', 'js'):
        for k, v in (data.get(sec) or {}).items():
            if k in PROPER or k.startswith('company'):
                continue   # sérnöfn (félag, umhverfi) eru ekki þýdd
            if isinstance(v, str) and (IS_CH.search(v) if lang == 'en' else re.search(r'[A-Za-z]{3}', v)) and k not in (ov.get(sec) or {}):
                out.append(f'{sec}.{k}')
    return out


def alt_name(fname, lang, primary):
    """stjorn.html -> stjorn.en.html (ef lang er ekki aðaltungumál)."""
    if lang == primary:
        return fname
    root, ext = os.path.splitext(fname)
    return f'{root}.{lang}{ext}'


def relink(html, lang, primary, pages):
    """Afstæðir tenglar milli síðna í sama tungumáli."""
    if lang == primary:
        return html
    # Rofinn (nav.lang-sw) vísar viljandi á hitt málið og er ekki umskrifaður.
    parts = re.split(r'(<nav class="lang-sw".*?</nav>)', html, flags=re.S)
    for i in range(0, len(parts), 2):
        for p in pages:
            parts[i] = re.sub(r'href="' + re.escape(p) + r'(#[^"]*)?"', lambda m, p=p: f'href="{alt_name(p, lang, primary)}{m.group(1) or ""}"', parts[i])
    return ''.join(parts)


def switch_html(cur, hrefs):
    """Rofi efst: hrefs = {'is': 'stjorn.html', 'en': 'stjorn.en.html'}."""
    lab = 'Tungumál' if cur == 'is' else 'Language'
    items = ''.join(
        f'<a href="{hrefs[l]}" hreflang="{l}" lang="{l}" title="{NAME[l]}"' + (' aria-current="true"' if l == cur else '') + f'>{LABEL[l]}</a>'
        for l in LANGS if l in hrefs)
    return f'<nav class="lang-sw" aria-label="{lab}">{items}</nav>'


def inject_switch(html, cur, hrefs):
    if not hrefs or len(hrefs) < 2:
        return html
    sw = switch_html(cur, hrefs)
    if '<div id="mode"></div>' in html:
        return html.replace('<div id="mode"></div>', '<div id="mode"></div>' + sw, 1)
    i = html.find('<div class="wrap">')
    return html[:i + 18] + sw + html[i + 18:] if i >= 0 else sw + html
