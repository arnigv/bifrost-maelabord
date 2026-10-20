#!/usr/bin/env python3
"""Bifröst mælaborð: smíðar mælaborð úr föstu sniðmáti (alltaf sama útlit og virkni).

Gervigreindin skrifar ALDREI HTML mælaborðs sjálf. Hún fyllir aðeins gögnin (DATA) eftir
`template/schema.md` viðkomandi skills og keyrir þessa skriftu.

Notkun:
  render.py --dashboard stjorn --data stjorn.json --out build/stjorn.html [--subpage]
  render.py --dashboard stjorn --example --out /tmp/stjorn.html        # sýnidæmi (gullútgáfa)
  render.py --list
  render.py --dashboard stjorn --data stjorn.json --ext ext/stjorn.html --subpage --out build/stjorn.html

Sniðmát: ${PLUGIN}/skills/<dashboard>/template/
  template.html  heil síða með staðgenglum:
     {{THEME_CSS}}        innihald bifrost-maelabord/assets/theme.css
     {{COMPONENTS_JS}}    innihald bifrost-maelabord/assets/components.js
     {{DATA_JSON}}        gögnin (JSON, '<' sloppið)
     {{meta.<lykill>}}    gildi úr DATA["meta"] (HTML-sloppið), t.d. {{meta.company}}
     {{text.<lykill>}}    texti úr DATA["text"] (HTML-sloppið)
     {{{html.<lykill>}}}  HTML úr DATA["html"] (óbreytt; aðeins einfaldar merkingar <b>, <a href="x.html">);
                          listi eða hlutur verður JSON
     {{js.<lykill>}}      gildi úr DATA["js"] sem öruggur JS-bókstafur (json.dumps), t.d. inni í <script>
  example.json   gögn sýnidæmisins (gullútgáfan)
  schema.md      lýsing á hverjum lykli og hvaðan hann kemur úr BC

Villur: skriftan stöðvast ef lykil vantar í DATA (skv. example.json) eða staðgengill er ófylltur.
--subpage bætir <!doctype html> og viewport-meta framan við (undirsíða í miðstöðvar-artifacti).
"""
import argparse, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.normpath(os.path.join(HERE, '..', '..'))
ASSETS = os.path.join(HERE, '..', 'assets')
DASH = ['stjorn', 'sjodstreymi', 'tekjur', 'kostnadur', 'manadarlok', 'framlegd', 'spagerd', 'endurskodun']


def tdir(name):
    return os.path.join(SKILLS, name, 'template')


def shape_errors(ex, got, path='DATA', maps=()):
    """Ber saman lögun gagna við sýnidæmið (example.json).
    - Hlutir: allir lyklar sýnidæmisins verða að vera til (nema lyklar sem byrja á _).
    - Listar af hlutum: hver færsla þarf lyklana sem ALLAR færslur sýnidæmisins hafa.
    - Kort (lyklar eru gögn, t.d. mánuðir 'ÁÁÁÁ-MM' eða númer): aðeins tegund gilda athuguð.
      Kort eru greind sjálfkrafa (lykill með tölustaf) eða talin upp í example.json → "_maps": ["slóð", ...].
    """
    errs = []
    p = path[5:] if path.startswith('DATA.') else ''
    if got is None and isinstance(ex, (dict, list)) and path.count('.') > 1:
        return errs  # valfrjáls hlutur eða listi má vera null
    if isinstance(ex, dict):
        if not isinstance(got, dict):
            return [f'{path}: á að vera hlutur (object)']
        keys = [k for k in ex if not k.startswith('_')]
        is_map = p in maps or (keys and all(re.search(r'\d', k) for k in keys) and p not in ('meta', 'text', 'html'))
        if is_map:
            return errs
        for k in keys:
            if k not in got:
                errs.append(f'{path}.{k}: vantar')
            else:
                errs += shape_errors(ex[k], got[k], f'{path}.{k}', maps)
    elif isinstance(ex, list):
        if not isinstance(got, list):
            return [f'{path}: á að vera listi']
        dicts = [x for x in ex if isinstance(x, dict)]
        if dicts and len(dicts) == len(ex):
            common = set(dicts[0]).intersection(*[set(x) for x in dicts[1:]]) if len(dicts) > 1 else set(dicts[0])
            proto = {k: dicts[0][k] for k in dicts[0] if k in common}
            for i, item in enumerate(got[:200]):
                errs += shape_errors(proto, item, f'{path}[{i}]', maps)
    elif isinstance(ex, (int, float)) and not isinstance(ex, bool):
        if got is not None and not (isinstance(got, (int, float)) and not isinstance(got, bool)):
            errs.append(f'{path}: á að vera tala')
    elif isinstance(ex, str):
        if got is not None and not isinstance(got, str):
            errs.append(f'{path}: á að vera texti')
    return errs


def render(name, data, subpage=False, strict=True, ext=None):
    d = tdir(name)
    tpl = open(os.path.join(d, 'template.html'), encoding='utf-8').read()
    ex = json.load(open(os.path.join(d, 'example.json'), encoding='utf-8'))
    if strict:
        errs = shape_errors(ex, data, maps=tuple(ex.get('_maps', [])))
        if errs:
            sys.exit('Gögn passa ekki við sniðmát ' + name + ':\n  ' + '\n  '.join(errs[:40]))
    css = open(os.path.join(ASSETS, 'theme.css'), encoding='utf-8').read()
    comp = open(os.path.join(ASSETS, 'components.js'), encoding='utf-8').read()
    dj = json.dumps({k: v for k, v in data.items() if not k.startswith('_')}, ensure_ascii=False).replace('<', '\\u003c')

    def get(section, key):
        cur = data.get(section, {})
        for part in key.split('.'):
            if not isinstance(cur, dict) or part not in cur:
                sys.exit(f'Vantar {section}.{key} í gögnum ({name}).')
            cur = cur[part]
        return cur

    for blk in re.findall(r'<script>(.*?)</script>', tpl, re.S):
        bad = re.findall(r'\{\{\{?(?:meta|text|html)\.[\w.]+\}?\}\}', blk)
        if bad:
            sys.exit(f'Sniðmát {name}: {bad[:3]} inni í <script> — notaðu {{{{js.x}}}}.')
    out = tpl.replace('{{THEME_CSS}}', css).replace('{{COMPONENTS_JS}}', comp)
    def raw(v):
        # listar og hlutir verða að gildu JSON/JS (t.d. fylki dagsetninga); annars óbreyttur texti
        return json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else str(v)
    out = re.sub(r'\{\{\{html\.([\w.]+)\}\}\}', lambda m: raw(get('html', m.group(1))), out)
    # {{js.x}}: gildi sem JS-bókstafur (strengur með gæsalöppum, tala, fylki), öruggt inni í forskrift
    out = re.sub(r'\{\{js\.([\w.]+)\}\}', lambda m: json.dumps(get('js', m.group(1)), ensure_ascii=False).replace('</', '<\\/'), out)
    out = re.sub(r'\{\{(meta|text)\.([\w.]+)\}\}', lambda m: html.escape(str(get(m.group(1), m.group(2))), quote=True), out)
    out = out.replace('{{DATA_JSON}}', dj)
    left = re.findall(r'\{\{\{?[A-Za-z_][\w.]*\}?\}\}', out.replace(dj, ''))
    if left:
        sys.exit(f'Ófylltir staðgenglar í {name}: {sorted(set(left))[:10]}')
    for snippet in (ext or []):
        # Viðbót notandans (ext/<síða>.html): sett inn á undan fæti síðunnar, svo hún lifir uppfærslur af
        block = '\n<!-- viðbót notanda -->\n' + snippet.strip() + '\n<!-- /viðbót notanda -->\n'
        i = out.rfind('<footer')
        out = out[:i] + block + out[i:] if i >= 0 else out + block
    if subpage and 'class="crumb"' not in out:
        # Allar undirsíður verða að hafa leið aftur í miðstöðina
        t = re.search(r'<title>(.*?)</title>', out)
        crumb = ('<nav class="crumb" aria-label="Leiðarstika"><a href="index.html">← Miðstöð<span class="c-l"> mælaborða</span></a>'
                 + (f'<span class="sep">/</span><span>{t.group(1)}</span>' if t else '') + '</nav>')
        i = out.find('<div class="wrap">')
        out = out[:i + 18] + '\n  ' + crumb + out[i + 18:] if i >= 0 else crumb + out
    if subpage and not out.lstrip().lower().startswith('<!doctype'):
        out = '<!doctype html>\n<html lang="is">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n' + out
    return out


def split_data(page):
    """Skilar (texti án DATA-blokkar, DATA-hlutur) fyrir samanburð."""
    m = re.search(r'const DATA\s*=\s*', page)
    if not m:
        return page, None
    obj, end = json.JSONDecoder().raw_decode(page[m.end():])
    return page[:m.end()] + '«DATA»' + page[m.end() + end:], obj


def check_golden(name, golden_path):
    """Ber útgáfu úr example.json saman við gullútgáfu: allt utan DATA eins, og DATA gullsins innifalið."""
    ex = json.load(open(os.path.join(tdir(name), 'example.json'), encoding='utf-8'))
    mine = render(name, ex, subpage=True)
    gold = open(golden_path, encoding='utf-8').read()
    a, da = split_data(mine)
    b, db = split_data(gold)
    ok = True
    if a != b:
        ok = False
        i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
        print(f'{name}: munur utan DATA við staf {i}:\n  sniðmát: {a[max(0,i-80):i+120]!r}\n  gull:    {b[max(0,i-80):i+120]!r}')
    if db is not None:
        miss = [k for k in db if k not in da or da[k] != db[k]]
        if miss:
            ok = False
            print(f'{name}: DATA-lyklar ólíkir gulli: {miss[:10]}')
    print(f'{name}: {"EINS OG GULLÚTGÁFAN" if ok else "MUNUR"}')
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dashboard')
    ap.add_argument('--data')
    ap.add_argument('--example', action='store_true')
    ap.add_argument('--out')
    ap.add_argument('--subpage', action='store_true')
    ap.add_argument('--ext', action='append', default=[], help='viðbót notanda (HTML-bútur), sett inn á undan fæti')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--check-golden', metavar='HTML', help='bera sýnidæmi saman við gullútgáfu')
    a = ap.parse_args()
    if a.list:
        for n in DASH:
            ok = os.path.exists(os.path.join(tdir(n), 'template.html'))
            print(f'{n:12} {"sniðmát til" if ok else "VANTAR"}')
        return
    if a.check_golden:
        sys.exit(0 if check_golden(a.dashboard, a.check_golden) else 1)
    if not a.dashboard or not a.out:
        ap.error('--dashboard og --out vantar')
    src = os.path.join(tdir(a.dashboard), 'example.json') if a.example else a.data
    data = json.load(open(src, encoding='utf-8'))
    out = render(a.dashboard, data, a.subpage, ext=[open(f, encoding='utf-8').read() for f in a.ext])
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, 'w', encoding='utf-8').write(out)
    print(f'{a.dashboard}: {len(out) // 1024} KB → {a.out}')


if __name__ == '__main__':
    main()
