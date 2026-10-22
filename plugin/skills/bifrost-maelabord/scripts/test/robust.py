#!/usr/bin/env python3
"""Þolprófun mælaborða: sama sniðmát á gölluðum eða litlum gögnum.

Notkun:
  robust.py [mælaborð ...] [--lang is|en|both] [--keep DIR] [--baseline DIR | --compare DIR]

Afbrigði af example.json hvers mælaborðs:
  full        óbreytt sýnidæmi (DT); má ekki breytast milli útgáfa (--baseline / --compare)
  one_month   aðeins fyrsti mánuður fullbókaður (complete=True), hinir ekki
  no_month    enginn mánuður fullbókaður
  sparse      allir valfrjálsir listar tómir (verk, vörur, áætlanir, einskiptisliðir, aldur …) og null þar sem leyft
  zero        allar fjárhæðir 0 (tómt félag sem komst samt framhjá gagnalagi)

Hvert afbrigði er smíðað með render.py og keyrt í runtest.js. Fall = JS-villa eða grunsamlegt úttak
(undefined, NaN, Infinity, [object Object]) í sýnilegum texta. Útgangskóði 1 ef eitthvað fellur.
"""
import argparse, copy, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
SKILLS = os.path.normpath(os.path.join(SCRIPTS, '..', '..'))
DASH = ['stjorn', 'sjodstreymi', 'tekjur', 'kostnadur', 'manadarlok', 'framlegd', 'spagerd', 'endurskodun']
KEEP_LISTS = {'months', 'M', 'cash_hist', 'krofur_hist', 'labels', 'fc', 'accounts', 'banks', 'cats', 'rows', 'cy', 'py'}
SKIP = ('meta', 'text', 'html', 'js', 'i18n', '_maps')


def walk(o, fn, path=()):
    if isinstance(o, dict):
        for k in list(o):
            if path == () and k in SKIP:
                continue
            o[k] = walk(o[k], fn, path + (k,))
        return fn(o, path)
    if isinstance(o, list):
        return fn([walk(x, fn, path + ('[]',)) for x in o], path)
    return fn(o, path)


def months_complete(d, keep):
    n = [0]
    def fn(o, p):
        if isinstance(o, dict) and isinstance(o.get('complete'), bool):
            n[0] += 1
            o['complete'] = n[0] <= keep
            if not o['complete'] and 'reason' in o and not o['reason']:
                o['reason'] = 'laun vantar'
        return o
    walk(d, fn)
    return d


def sparse(d):
    def fn(o, p):
        if isinstance(o, list) and p and p[-1] not in KEEP_LISTS and p[-1] != '[]' and len(p) <= 3 and o and isinstance(o[0], (dict, list)):
            return []
        return o
    walk(d, fn)
    return d


def zero(d):
    def fn(o, p):
        if isinstance(o, (int, float)) and not isinstance(o, bool) and p and not re.search(r'(year|py|n|days|pct|share|rate|g|sigma|mat|delay|no)$', str(p[-1])):
            return 0
        return o
    walk(d, fn)
    return d


VARIANTS = {
    'full': lambda d: d,
    'one_month': lambda d: months_complete(d, 1),
    'no_month': lambda d: months_complete(d, 0),
    'sparse': sparse,
    'zero': zero,
}


def run(dash, variant, lang, out_dir):
    ex = json.load(open(os.path.join(SKILLS, dash, 'template', 'example.json'), encoding='utf-8'))
    data = VARIANTS[variant](copy.deepcopy(ex))
    os.makedirs(out_dir, exist_ok=True)
    dp = os.path.join(out_dir, f'{dash}.{variant}.json')
    json.dump(data, open(dp, 'w', encoding='utf-8'), ensure_ascii=False)
    hp = os.path.join(out_dir, f'{dash}.{variant}.{lang}.html')
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, 'render.py'), '--dashboard', dash, '--data', dp, '--lang', lang, '--out', hp],
                       capture_output=True, text=True)
    if r.returncode:
        return False, 'smíði: ' + (r.stderr or r.stdout).strip().splitlines()[-1][:300]
    sp = hp[:-5] + '.snap.json'
    t = subprocess.run(['node', os.path.join(HERE, 'runtest.js'), hp, '--snap', sp], capture_output=True, text=True, timeout=120)
    outp = (t.stdout + t.stderr).strip()
    ok = t.returncode == 0 and 'í lagi' in outp.splitlines()[0] and not re.search(r'undefined|NaN|Infinity|\[object', outp)
    return ok, outp


def visible(snap_path):
    s = json.load(open(snap_path, encoding='utf-8'))
    out = {}
    for k, h in s.items():
        if k.startswith('charts') or k == 'trace':
            continue
        out[k] = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', ' ', h)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dash', nargs='*')
    ap.add_argument('--lang', default='both')
    ap.add_argument('--keep', default=os.path.join('/tmp', 'bf_robust'))
    ap.add_argument('--variants', default=','.join(VARIANTS))
    ap.add_argument('--baseline', help='vista sýnilegan texta full-afbrigðis í þessa möppu')
    ap.add_argument('--compare', help='bera full-afbrigði saman við vistaðan grunn')
    a = ap.parse_args()
    dashes = a.dash or DASH
    langs = ['is', 'en'] if a.lang == 'both' else [a.lang]
    fails = 0
    for d in dashes:
        for v in a.variants.split(','):
            for L in langs:
                ok, msg = run(d, v, L, a.keep)
                line = msg.splitlines()[0] if msg else ''
                print(f"{'OK  ' if ok else 'FALL'} {d:<12} {v:<10} {L}  {line[:150]}")
                if not ok:
                    fails += 1
                    for x in msg.splitlines()[1:6]:
                        print('       ', x[:220])
                if v == 'full' and (a.baseline or a.compare):
                    snap = os.path.join(a.keep, f'{d}.{v}.{L}.snap.json')
                    vis = visible(snap)
                    ref = os.path.join(a.baseline or a.compare, f'{d}.{L}.visible.json')
                    if a.baseline:
                        os.makedirs(a.baseline, exist_ok=True)
                        json.dump(vis, open(ref, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
                    else:
                        base = json.load(open(ref, encoding='utf-8'))
                        diff = [k for k in set(base) | set(vis) if base.get(k) != vis.get(k)]
                        if diff:
                            fails += 1
                            print(f'BREYTT {d} {L}: sýnilegur texti DT-sýnidæmis breyttist í {sorted(diff)}')
    print(f'{fails} föll')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
