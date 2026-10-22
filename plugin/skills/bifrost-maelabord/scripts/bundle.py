#!/usr/bin/env python3
"""Bifröst mælaborð: smíðar miðstöðvar-artifactið (eitt artifact, margar síður) úr gögnum.

Uppsetning (allt):
  bundle.py --hub hub.json --data stjorn=stjorn.json --data sjodstreymi=sjod.json ... --out build/
Breyting á EINU mælaborði (aðeins það er smíðað og birt):
  bundle.py --data tekjur=tekjur.json --out build/            # aðrar síður óbreyttar
  bundle.py --data tekjur=tekjur.json --hub hub.json --out build/   # ef lykiltala á spjaldi breyttist líka
Sýnidæmi:
  bundle.py --example --out /tmp/dt/

Tungumál (1.0):
  Aðaltungumál = `--lang` ef gefið, annars það sem er skráð í manifest.json, annars tungumál grunngagnanna
  (`lang` í gögnum eða sjálfvirk greining á heitum úr BC: íslensk heiti → íslenska, annars enska).
  Hver síða er smíðuð á báðum tungumálum: aðaltungumál í `<síða>.html`, hitt í `<síða>.<lang>.html`
  (t.d. stjorn.en.html eða stjorn.is.html), með rofanum „IS | EN“ efst. Tenglar haldast innan tungumáls.
  Textar gervigreindar á hinu tungumálinu koma úr `i18n.<lang>` í gögnunum (sjá schema.md); vanti þá er varað við.

Í build/ verða:
  index.html, <mælaborð>.html, og sömu síður á hinu tungumálinu (index.en.html, stjorn.en.html …)
  data/<mælaborð>.json, data/hub.json   gögnin sem síðan var smíðuð úr
  ext/<mælaborð>.html            viðbætur notanda (ef til; ext/<mælaborð>.<lang>.html fyrir hitt tungumálið)
  manifest.json                  yfirlit: síður, tungumál, gagnadagsetningar, viðbætur, slóð Sjálfvirknivæðingar
Skriftan prentar `files` með AÐEINS þeim skrám sem breyttust; birtu með þeim (skrár sem ekki eru sendar haldast í artifactinu).
"""
import argparse, json, os, shutil, sys
from datetime import date
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render as R, render_hub as RH, i18n as I


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hub'); ap.add_argument('--data', action='append', default=[]); ap.add_argument('--example', action='store_true')
    ap.add_argument('--automation-url', help='slóð Sjálfvirknivæðingar (sér artifact)')
    ap.add_argument('--lang', choices=I.LANGS, help='aðaltungumál (sjálfgefið: skráð í manifest eða greint úr gögnum)')
    ap.add_argument('--one-lang', action='store_true', help='smíða aðeins aðaltungumál (enginn rofi)')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, 'data'), exist_ok=True)
    mpath = os.path.join(a.out, 'manifest.json')
    man = json.load(open(mpath, encoding='utf-8')) if os.path.exists(mpath) else {'plugin': 'bifrost-maelabord', 'pages': {}}
    pages = {}
    if a.example:
        pages = {n: os.path.join(R.tdir(n), 'example.json') for n in R.DASH}
        hub = os.path.join(R.tdir('bifrost-skyndiuttekt'), 'example.json')
    else:
        hub = a.hub
        for d in a.data:
            n, p = d.split('=', 1)
            if n not in R.DASH:
                sys.exit(f'Óþekkt mælaborð: {n} (í boði: {", ".join(R.DASH)})')
            pages[n] = p
    loaded = {n: json.load(open(p, encoding='utf-8')) for n, p in pages.items()}
    H = json.load(open(hub, encoding='utf-8')) if hub else None
    # aðaltungumál: --lang > manifest > gögn (fyrsta síða, annars miðstöð)
    first = next(iter(loaded.values()), None) or H or {}
    primary = a.lang or man.get('lang') or I.data_lang(first)
    langs = [primary] if a.one_lang else [primary, I.other(primary)]
    man['lang'] = primary
    man['langs'] = langs
    files_all = ['index.html'] + [n + '.html' for n in sorted(set(man['pages']) | set(pages))]
    files_all += [f for f in os.listdir(a.out) if f.startswith('ser-') and f.endswith('.html') and f.count('.') == 1] if os.path.isdir(a.out) else []
    hrefs = lambda f: {l: I.alt_name(f, l, primary) for l in langs}
    changed = []
    for n, data in loaded.items():
        p = pages[n]
        exts = {}
        for L in langs:
            extf = os.path.join(a.out, 'ext', I.alt_name(n + '.html', L, primary))
            base = os.path.join(a.out, 'ext', n + '.html')
            exts[L] = extf if os.path.exists(extf) else (base if os.path.exists(base) else None)
            if L != primary and exts[L] == base:
                print(f'Aðvörun: {n}: viðbót notanda er aðeins til á {primary} (ext/{I.alt_name(n + ".html", L, primary)} vantar)')
        for L in langs:
            miss = I.missing_overlay(data, L)
            if miss:
                print(f'Aðvörun: {n} ({L}): þýðingu vantar í i18n.{L} fyrir {", ".join(miss[:8])}{" …" if len(miss) > 8 else ""}')
            ext = [open(exts[L], encoding='utf-8').read()] if exts[L] else []
            out = R.render(n, data, subpage=True, ext=ext, lang=L, hrefs=hrefs(n + '.html') if len(langs) > 1 else None, pages=files_all, primary=primary)
            fn = I.alt_name(n + '.html', L, primary)
            open(os.path.join(a.out, fn), 'w', encoding='utf-8').write(out)
            changed.append(fn)
            print(f'{fn}  {len(out)//1024} KB' + ('  (+ viðbót notanda)' if ext else ''))
        dp = os.path.join(a.out, 'data', n + '.json')
        if os.path.abspath(p) != os.path.abspath(dp):
            shutil.copyfile(p, dp)
        ext_files = sorted({os.path.relpath(f, a.out) for f in exts.values() if f})
        man['pages'][n] = {'file': n + '.html', 'files': {L: I.alt_name(n + '.html', L, primary) for L in langs}, 'data': 'data/' + n + '.json',
                           'as_of': (data.get('meta') or {}).get('as_of') or data.get('as_of') or data.get('today'),
                           'ext': ext_files, 'built': date.today().isoformat()}
        changed += ['data/' + n + '.json'] + ext_files
    if H is not None:
        built = set(man['pages']) | set(pages)
        missing = [c['href'] for c in H['cards'] if not c['href'].startswith('http') and c['href'][:-5] not in built and not c['href'].startswith('ser-')]
        if missing:
            print('Aðvörun: spjöld vísa á síður sem eru ekki til:', missing)
        for L in langs:
            miss = I.missing_overlay(H, L)
            if miss:
                print(f'Aðvörun: miðstöð ({L}): þýðingu vantar í i18n.{L} fyrir {", ".join(miss[:8])}')
            fn = I.alt_name('index.html', L, primary)
            html = RH.build(H, lang=L, hrefs=hrefs('index.html') if len(langs) > 1 else None, pages=files_all, primary=primary)
            if fn != 'index.html' and not html.lstrip().lower().startswith('<!doctype'):
                # miðstöð á hinu tungumálinu er undirsíða: fær ekki beinagrind í artifactinu
                html = (f'<!doctype html>\n<html lang="{L}">\n'
                        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n' + html)
            open(os.path.join(a.out, fn), 'w', encoding='utf-8').write(html)
            changed.append(fn)
            print(f'{fn} (miðstöð, {L})')
        dp = os.path.join(a.out, 'data', 'hub.json')
        if os.path.abspath(hub) != os.path.abspath(dp):
            shutil.copyfile(hub, dp)
        man['company'] = H['meta']['company']; man['as_of'] = H['meta']['as_of']
        changed += ['data/hub.json']
    if a.automation_url:
        man['automation_url'] = a.automation_url
    json.dump(man, open(mpath, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    changed.append('manifest.json')
    # index.html (aðaltungumál) er síðan sjálf í artifactinu; aðrar skrár fara í `files`
    files = {f: f for f in changed if f != 'index.html'}
    print('Tungumál: ' + ' + '.join(langs) + f' (aðal: {primary})')
    print('Birta: file_path=' + os.path.join(a.out, 'index.html') + (' (óbreytt)' if H is None else ''), ' root=' + a.out)
    print('files =', json.dumps(files, ensure_ascii=False))


if __name__ == '__main__':
    main()
