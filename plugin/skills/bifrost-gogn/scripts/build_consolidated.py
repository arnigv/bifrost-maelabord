#!/usr/bin/env python3
"""Bifröst gagnalag: samstæða úr mörgum dataset.json.

Inntak:
  --entity  NAFN=slóð/dataset.json[@eignarhlutur]   (oft; eignarhlutur 0–1, sjálfgefið 1.0)
  --elim    eliminations.json   (valfrjálst) listi af jöfnunarfærslum:
            {"desc": "...", "type": "rekstur"|"fjarmagn"|"ardur"|"stada",
             "seller": "NAFN", "buyer": "NAFN", "seller_cat": "tekjur", "buyer_cat": "annar_rekstur",
             "months": {"2026-01": 2400000, ...}}            # fyrir rekstur/fjarmagn/ardur
            {"desc": "...", "type": "stada", "seller": "...", "buyer": "...", "amount": 372000}  # innbyrðis kröfur/skuldir
  --name    heiti samstæðu
  --out     consolidated.json
Úttak: sama snið og dataset.json (months, ytd, balance …) auk 'entities' og 'eliminations'.
Ef eignarhlutur < 1 er hlutdeild minnihluta reiknuð af hagnaði og sýnd sér (full samstæðuaðferð).
"""
import argparse, json
from collections import defaultdict

CATS = ['tekjur', 'vorunotkun', 'laun', 'husnaedi', 'annar_rekstur', 'afskriftir', 'fjarmagn', 'oreglulegt', 'skattar']

def derive(r):
    r['ebitda'] = round(r['tekjur'] - r['vorunotkun'] - r['laun'] - r['husnaedi'] - r['annar_rekstur'], 2)
    r['hagnadur_fs'] = round(r['ebitda'] - r['afskriftir'] - r['fjarmagn'] - r['oreglulegt'], 2)
    return r

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--entity', action='append', required=True)
    ap.add_argument('--elim')
    ap.add_argument('--name', default='Samstæða')
    ap.add_argument('--out', default='consolidated.json')
    a = ap.parse_args()

    ents = []
    for e in a.entity:
        name, rest = e.split('=', 1)
        path, share = rest.rsplit('@', 1) if '@' in rest else (rest, '1')
        ents.append({'name': name, 'data': json.load(open(path, encoding='utf-8')), 'share': float(share)})

    months = sorted({r['ym'] for e in ents for r in e['data']['months']})
    by = {e['name']: {r['ym']: r for r in e['data']['months']} for e in ents}
    complete = {m: all(by[e['name']].get(m, {'complete': True}).get('complete', True) for e in ents) for m in months}

    cons = {m: {c: 0.0 for c in CATS} for m in months}
    for e in ents:
        for m in months:
            r = by[e['name']].get(m)
            if r:
                for c in CATS:
                    cons[m][c] += r[c]

    elims = json.load(open(a.elim, encoding='utf-8')) if a.elim else []
    elim_rows = []
    bal_elim = 0.0
    for el in elims:
        t = el['type']
        if t == 'stada':
            bal_elim += el['amount']
            elim_rows.append({'desc': el['desc'], 'type': t, 'total': el['amount']})
            continue
        tot = 0.0
        for m, v in el.get('months', {}).items():
            if m not in cons:
                continue
            tot += v
            if t == 'rekstur':          # innbyrðis sala: lækkar tekjur seljanda og kostnað kaupanda jafnt
                cons[m][el.get('seller_cat', 'tekjur')] -= v
                cons[m][el.get('buyer_cat', 'annar_rekstur')] -= v
            elif t == 'fjarmagn':       # innbyrðis vextir: fjármunatekjur (neikvæðar) og fjármagnsgjöld (jákvæð) jafnast
                cons[m]['fjarmagn'] += v   # fellir út tekjuhlið
                cons[m]['fjarmagn'] -= v   # og gjaldahlið (nettó 0 í samstæðu)
            elif t == 'ardur':          # arður frá dótturfélagi: fellur út úr fjármunatekjum móðurfélags
                cons[m]['fjarmagn'] += v
        elim_rows.append({'desc': el['desc'], 'type': t, 'seller': el.get('seller'), 'buyer': el.get('buyer'), 'total': round(tot, 2)})

    rows = []
    for m in months:
        r = {'ym': m, **{c: round(cons[m][c], 2) for c in CATS}}
        derive(r)
        r['complete'] = complete[m]
        rows.append(r)

    # hlutdeild minnihluta (full samstæðuaðferð): (1 − hlutur) × hagnaður dótturfélags
    minority = {m: 0.0 for m in months}
    for e in ents:
        if e['share'] < 1:
            for m in months:
                r = by[e['name']].get(m)
                if r:
                    minority[m] += (1 - e['share']) * r['hagnadur_fs']
    for r in rows:
        r['hlutdeild_minnihluta'] = round(minority[r['ym']], 2)

    def agg(sel):
        o = {c: round(sum(r[c] for r in sel), 2) for c in CATS + ['ebitda', 'hagnadur_fs', 'hlutdeild_minnihluta']}
        o['months'] = [r['ym'] for r in sel]
        return o
    comp = [r for r in rows if r['complete']]
    year = max(m[:4] for m in months)
    cy = [r for r in comp if r['ym'].startswith(year)]

    # efnahagur: summa félaga að frádregnum innbyrðis stöðum
    balance = None
    bals = [e['data'].get('balance') for e in ents if e['data'].get('balance')]
    if bals:
        bm = sorted({m for b in bals for m in b['months']})
        cat = defaultdict(lambda: [0.0] * len(bm))
        for b in bals:
            for c, vals in b['categories'].items():
                for i, m in enumerate(b['months']):
                    cat[c][bm.index(m)] += vals[i]
        if bal_elim:
            for c in ('krofur', 'skammtimaskuldir', 'eignir'):
                if c in cat:
                    cat[c] = [v - bal_elim for v in cat[c]]
        balance = {'months': bm, 'categories': {c: [round(v, 2) for v in vals] for c, vals in cat.items()},
                   'stemming': [s for b in bals for s in b.get('stemming', [])]}

    out = {
        'company': a.name, 'consolidated': True, 'environment': ents[0]['data'].get('environment', ''),
        'as_of': max(e['data'].get('as_of', '') for e in ents),
        'categories': ents[0]['data'].get('categories'),
        'entities': [{'name': e['name'], 'share': e['share'], 'ytd': e['data'].get('ytd'),
                      'months': [{k: r[k] for k in ('ym', 'tekjur', 'ebitda', 'hagnadur_fs', 'complete') if k in r} for r in e['data']['months']]} for e in ents],
        'eliminations': elim_rows,
        'months': rows, 'ytd': agg(cy),
        'incomplete': [{'ym': r['ym'], 'reason': 'ófullbókað hjá a.m.k. einu félagi'} for r in rows if not r['complete']],
        'oneoffs': [dict(o, entity=e['name']) for e in ents for o in e['data'].get('oneoffs', [])],
        'balance': balance,
        'profile': {e['name']: e['data'].get('profile') for e in ents},
    }
    json.dump(out, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    y = out['ytd']
    s = sum(by[e['name']][m]['tekjur'] for e in ents for m in y['months'] if m in by[e['name']])
    print(f"OK {a.name}: {len(ents)} félög, fullbókað {len(cy)} mán. í {year}. Tekjur félaga samtals {s/1e6:.1f} m → samstæða {y['tekjur']/1e6:.1f} m, "
          f"EBITDA {y['ebitda']/1e6:.1f} m, hagnaður {y['hagnadur_fs']/1e6:.1f} m. Jöfnunarfærslur: {len(elim_rows)}.")

if __name__ == '__main__':
    main()
