#!/usr/bin/env python3
"""Stærðarflokkun, endurskoðunarskylda og skilafrestur skv. lögum nr. 3/2006.

Notkun:
  classify_size.py --thresholds thresholds.json --assets 826e6 --revenue 1620e6 --fte 45 \
      [--prev-assets ... --prev-revenue ... --prev-fte ...] [--year-end 2026-12-31] [--pie] [--out size.json]
Tvö af þremur viðmiðum ráða. Flokkur breytist aðeins ef farið er yfir/undir tvö ár í röð,
svo ef fyrra ár er gefið er það notað til að meta hvort flokkur sé staðfestur.
"""
import argparse, json
from datetime import date

ORDER = ['orfelag', 'litid', 'medalstort', 'stort']

def exceeds(T, a, r, f):
    return sum([a > T['heildareignir'], r > T['velta'], (f or 0) > T['arsverk']]) >= 2

def klass(S, a, r, f, pie=False):
    if pie: return 'stort'
    for k in ORDER[:3]:
        if not exceeds(S[k], a, r, f): return k
    return 'stort'

def add_months(d, m):
    y, mo = d.year + (d.month - 1 + m) // 12, (d.month - 1 + m) % 12 + 1
    import calendar
    return date(y, mo, min(d.day, calendar.monthrange(y, mo)[1]))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--thresholds', required=True)
    ap.add_argument('--assets', type=float, required=True); ap.add_argument('--revenue', type=float, required=True)
    ap.add_argument('--fte', type=float); ap.add_argument('--prev-assets', type=float); ap.add_argument('--prev-revenue', type=float); ap.add_argument('--prev-fte', type=float)
    ap.add_argument('--year-end', default=f'{date.today().year}-12-31'); ap.add_argument('--pie', action='store_true')
    ap.add_argument('--out', default='size.json')
    a = ap.parse_args()
    T = json.load(open(a.thresholds, encoding='utf-8')); S = T['staerdarflokkar']
    cur = klass(S, a.assets, a.revenue, a.fte, a.pie)
    prev = klass(S, a.prev_assets, a.prev_revenue, a.prev_fte, a.pie) if a.prev_assets is not None else None
    stadfest = prev == cur if prev else False
    E = T['endurskodunarskylda']
    yfir_end = exceeds(E, a.assets, a.revenue, a.fte)
    yfir_end_prev = exceeds(E, a.prev_assets, a.prev_revenue, a.prev_fte) if a.prev_assets is not None else True
    endurskodun = 'skyld' if (yfir_end or yfir_end_prev) else 'undanþegin (skoðunarmaður)'
    ye = date.fromisoformat(a.year_end); frestur = add_months(ye, T['skil']['manudir_eftir_arslok'])
    out = dict(
        flokkur=cur, flokkur_heiti=S[cur]['heiti'], fyrra_ar=prev, stadfest_tvo_ar=stadfest,
        fte_vantar=a.fte is None,
        vidmid=[dict(heiti=k, gildi=v, mork_litid=S['litid'][k2], mork_medal=S['medalstort'][k2])
                for k, v, k2 in (('Heildareignir', a.assets, 'heildareignir'), ('Hrein velta', a.revenue, 'velta'), ('Ársverk', a.fte, 'arsverk'))],
        endurskodun=endurskodun, endurskodun_stada=E.get('_stada', ''),
        sjodstreymi_skylt=cur in T['sjodstreymi']['skylt_fyrir'],
        skilafrestur=frestur.isoformat(), sekt_kr=T['skil']['sekt_kr'],
        slitakrafa_fra=add_months(frestur, T['skil']['slit_manudir_eftir_frest']).isoformat(),
        fyrirvari=T['_fyrirvari'], heimild=T['_heimild'])
    json.dump(out, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{out['flokkur_heiti']}{' (staðfest tvö ár)' if stadfest else ' (eitt ár, staðfesta)'}. Endurskoðun: {endurskodun}. "
          f"Sjóðstreymi: {'skylt' if out['sjodstreymi_skylt'] else 'ekki skylt'}. Skilafrestur {frestur:%d.%m.%Y}."
          + (' Ársverk vantar, flokkun byggir á tveimur viðmiðum.' if a.fte is None else ''))

if __name__ == '__main__':
    main()
