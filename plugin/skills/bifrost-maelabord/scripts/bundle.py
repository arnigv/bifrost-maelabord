#!/usr/bin/env python3
"""Bifröst mælaborð: smíðar miðstöðvar-artifactið (eitt artifact, margar síður) úr gögnum.

Uppsetning (allt):
  bundle.py --hub hub.json --data stjorn=stjorn.json --data sjodstreymi=sjod.json ... --out build/
Breyting á EINU mælaborði (aðeins það er smíðað og birt):
  bundle.py --data tekjur=tekjur.json --out build/            # aðrar síður óbreyttar
  bundle.py --data tekjur=tekjur.json --hub hub.json --out build/   # ef lykiltala á spjaldi breyttist líka
Sýnidæmi:
  bundle.py --example --out /tmp/dt/

Í build/ verða:
  index.html, <mælaborð>.html   síðurnar
  data/<mælaborð>.json, data/hub.json   gögnin sem síðan var smíðuð úr (svo breyta megi einni síðu síðar án þess að sækja allt aftur)
  ext/<mælaborð>.html            viðbætur notanda (ef til; settar sjálfkrafa inn við hverja smíði)
  manifest.json                  yfirlit: síður, gagnadagsetningar, viðbætur, slóð Sjálfvirknivæðingar
Skriftan prentar `files` með AÐEINS þeim skrám sem breyttust; birtu með þeim (skrár sem ekki eru sendar haldast í artifactinu).
"""
import argparse, json, os, shutil, sys
from datetime import date
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render as R, render_hub as RH


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hub'); ap.add_argument('--data', action='append', default=[]); ap.add_argument('--example', action='store_true')
    ap.add_argument('--automation-url', help='slóð Sjálfvirknivæðingar (sér artifact)')
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
    changed = []
    for n, p in pages.items():
        data = json.load(open(p, encoding='utf-8'))
        extf = os.path.join(a.out, 'ext', n + '.html')
        ext = [open(extf, encoding='utf-8').read()] if os.path.exists(extf) else []
        out = R.render(n, data, subpage=True, ext=ext)
        open(os.path.join(a.out, n + '.html'), 'w', encoding='utf-8').write(out)
        dp = os.path.join(a.out, 'data', n + '.json')
        if os.path.abspath(p) != os.path.abspath(dp):
            shutil.copyfile(p, dp)
        man['pages'][n] = {'file': n + '.html', 'data': 'data/' + n + '.json', 'as_of': (data.get('meta') or {}).get('as_of') or data.get('as_of') or data.get('today'),
                           'ext': ['ext/' + n + '.html'] if ext else [], 'built': date.today().isoformat()}
        changed += [n + '.html', 'data/' + n + '.json'] + (['ext/' + n + '.html'] if ext else [])
        print(f'{n}.html  {len(out)//1024} KB' + ('  (+ viðbót notanda)' if ext else ''))
    if hub:
        H = json.load(open(hub, encoding='utf-8'))
        built = set(man['pages']) | set(pages)
        missing = [c['href'] for c in H['cards'] if not c['href'].startswith('http') and c['href'][:-5] not in built and not c['href'].startswith('ser-')]
        if missing:
            print('Aðvörun: spjöld vísa á síður sem eru ekki til:', missing)
        open(os.path.join(a.out, 'index.html'), 'w', encoding='utf-8').write(RH.build(H))
        dp = os.path.join(a.out, 'data', 'hub.json')
        if os.path.abspath(hub) != os.path.abspath(dp):
            shutil.copyfile(hub, dp)
        man['company'] = H['meta']['company']; man['as_of'] = H['meta']['as_of']
        changed += ['data/hub.json']
        print('index.html (miðstöð)')
    if a.automation_url:
        man['automation_url'] = a.automation_url
    json.dump(man, open(mpath, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    changed.append('manifest.json')
    print('Birta: file_path=' + os.path.join(a.out, 'index.html') + (' (óbreytt)' if not hub else ''), ' root=' + a.out)
    print('files =', json.dumps({f: f for f in changed}, ensure_ascii=False))


if __name__ == '__main__':
    main()
