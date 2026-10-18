#!/usr/bin/env python3
"""Bifröst spálíkan: drifþáttaspá út árið og 12 mánuði fram, með óvissubili og bakprófun.

Inntak:  --data dataset.json (úr bifrost-gogn)  --assumptions assumptions.json  --out forecast.json
Líkan (útskýranlegt, ekki svartur kassi):
  Tekjur(m)   = grunnstig × árstíðastuðull(m) × (1 + dempaður leitni)^h × (1 + magn)^(h/12) × verðskrá(m) + þekktar pantanir(m)
  Vörunotkun  = Tekjur × efnishlutfall (síðustu 6 mán.) × (1 + aðfangaverð(m)) / verðskrá-yfirfærsla
  Laun        = grunnlaun × (1 + kjarasamningshækkun frá gildisdegi) × (1 + stöðugildabreyting)
  Húsnæði, annar rekstur = grunnur × (1 + verðbólga)^(h/12)
  Fjármagnsliðir = grunnur × (stýrivextir / stýrivextir í grunni)
  Afskriftir  = grunnur (flatt)
Óvissa: hlutfallslegt staðalfrávik leifa sögunnar × √h, P10/P50/P90.
Bakprófun: líkanið metið á gögnum fram að t−3 og spá borin saman við raun síðustu 3 fullbókaða mánuði (MAPE).
"""
import argparse, json, math, statistics
from datetime import date

CATS = ['tekjur', 'vorunotkun', 'laun', 'husnaedi', 'annar_rekstur', 'afskriftir', 'fjarmagn', 'oreglulegt']

def ym_add(ym, k):
    y, m = int(ym[:4]), int(ym[5:]); m += k
    while m > 12: m -= 12; y += 1
    while m < 1: m += 12; y -= 1
    return f'{y}-{m:02d}'

def seasonal(rows, key):
    """Margföldunarstuðlar á mánuð ársins. Þarf ≥ 13 mánuði, annars 1,0."""
    if len(rows) < 13:
        return {m: 1.0 for m in range(1, 13)}, False
    byM = {}
    vals = [r[key] for r in rows]
    for i, r in enumerate(rows):
        lo, hi = max(0, i - 6), min(len(rows), i + 6)
        avg = statistics.mean(vals[lo:hi]) or 1
        byM.setdefault(int(r['ym'][5:]), []).append(r[key] / avg)
    idx = {m: statistics.mean(byM.get(m, [1.0])) for m in range(1, 13)}
    s = statistics.mean(idx.values())
    return {m: v / s for m, v in idx.items()}, True

def fit(rows, A):
    """Metur grunnstig, leitni, hlutföll og leifar á gefnum fullbókuðum mánuðum."""
    si, has_season = seasonal(rows, 'tekjur')
    des = [r['tekjur'] / si[int(r['ym'][5:])] for r in rows]
    base = statistics.mean(des[-3:])
    n = min(12, len(des))
    xs, ys = list(range(n)), des[-n:]
    if n >= 4:
        mx, my = statistics.mean(xs), statistics.mean(ys)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sum((x - mx) ** 2 for x in xs) or 1)
        g = max(-0.015, min(0.015, slope / (my or 1)))  # hámark ±1,5% á mánuði
    else:
        g = 0.0
    resid = [abs(d - statistics.mean(des[max(0, i - 2):i + 1])) / (statistics.mean(des[max(0, i - 2):i + 1]) or 1) for i, d in enumerate(des)]
    sigma = max(0.03, statistics.pstdev(resid) + statistics.mean(resid))
    last6 = rows[-6:]
    mat_ratio = sum(r['vorunotkun'] for r in last6) / (sum(r['tekjur'] for r in last6) or 1)
    base3 = rows[-3:]
    fixed = {c: statistics.mean(r[c] for r in base3) for c in ('laun', 'husnaedi', 'annar_rekstur', 'afskriftir', 'fjarmagn')}
    return dict(si=si, season=has_season, base=base, g=g, sigma=sigma, mat=mat_ratio, fixed=fixed, last=rows[-1]['ym'])

def project(F, A, months):
    out = []
    phi = A.get('demping_leitni', 0.9)
    vol = A.get('magnbreyting_arleg', 0.0)
    for h, ym in enumerate(months, start=1):
        mo = int(ym[5:])
        damp = sum(phi ** k for k in range(1, h + 1))
        price = 1 + sum(p['breyting'] for p in A.get('verdskra', []) if ym >= p['fra'][:7])
        rev = F['base'] * F['si'][mo] * (1 + F['g']) ** damp * (1 + vol) ** (h / 12) * price
        rev += sum(o['upphaed'] for o in A.get('thekktar_pantanir', []) if o['manudur'] == ym)
        matp = 1 + sum(p['breyting'] for p in A.get('adfangaverd', []) if ym >= p['fra'][:7])
        pass_through = A.get('yfirfaersla_efnis', 0.5)
        cogs = rev / price * F['mat'] * matp * price ** pass_through
        wage = F['fixed']['laun'] * (1 + sum(k['haekkun'] for k in A.get('kjarasamningar', []) if ym >= k['fra'][:7])) * (1 + A.get('stodugildi_breyting', 0.0))
        infl = (1 + A.get('verdbolga', 0.0)) ** (h / 12)
        house = F['fixed']['husnaedi'] * infl
        other = F['fixed']['annar_rekstur'] * infl * (1 + A.get('eldsneyti_hlutur', 0.0) * A.get('eldsneyti_breyting', 0.0))
        fin = F['fixed']['fjarmagn'] * (A.get('styrivextir', 1) / (A.get('styrivextir_grunnur') or A.get('styrivextir', 1)))
        dep = F['fixed']['afskriftir']
        eb = rev - cogs - wage - house - other
        np_ = eb - dep - fin
        s = F['sigma'] * math.sqrt(h)
        out.append(dict(ym=ym, tekjur=rev, vorunotkun=cogs, laun=wage, husnaedi=house, annar_rekstur=other, afskriftir=dep, fjarmagn=fin,
                        ebitda=eb, hagnadur_fs=np_, tekjur_p10=rev * (1 - 1.2816 * s), tekjur_p90=rev * (1 + 1.2816 * s),
                        ebitda_p10=eb - 1.2816 * s * rev * (1 - F['mat']), ebitda_p90=eb + 1.2816 * s * rev * (1 - F['mat'])))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True); ap.add_argument('--assumptions', required=True); ap.add_argument('--out', default='forecast.json')
    ap.add_argument('--horizon', type=int, default=12)
    a = ap.parse_args()
    D = json.load(open(a.data, encoding='utf-8')); A = json.load(open(a.assumptions, encoding='utf-8'))
    # einskiptisliðir teknir út úr grunni
    one = {}
    for o in D.get('oneoffs', []):
        if o['cat'] == 'tekjur': one[o['ym']] = one.get(o['ym'], 0) + o['amount']
    rows = [dict(r) for r in D['months'] if r.get('complete')]
    for r in rows:
        o = one.get(r['ym'], 0)
        r['tekjur'] -= o; r['ebitda'] -= o; r['hagnadur_fs'] = r.get('hagnadur_fs', 0) - o  # einskipti út úr grunni og bakprófun
    if len(rows) < 6:
        raise SystemExit('Of fáir fullbókaðir mánuðir (< 6) fyrir spá.')
    F = fit(rows, A)
    year = F['last'][:4]
    months = [ym_add(F['last'], k) for k in range(1, a.horizon + 1)]
    fc = project(F, A, months)
    # bakprófun
    bt = None
    if len(rows) >= 8:
        Fb = fit(rows[:-3], A)
        pb = project(Fb, dict(A, verdskra=[], adfangaverd=[], kjarasamningar=[], thekktar_pantanir=[]), [r['ym'] for r in rows[-3:]])
        mape = lambda k: statistics.mean(abs(p[k] - r[k]) / (abs(r[k]) or 1) for p, r in zip(pb, rows[-3:]))
        bt = dict(manudir=[r['ym'] for r in rows[-3:]], mape_tekjur=round(mape('tekjur'), 4), mape_ebitda=round(mape('ebitda'), 4))
    actual_y = [r for r in D['months'] if r.get('complete') and r['ym'].startswith(year)]
    rest_y = [f for f in fc if f['ym'].startswith(year)]
    def tot(lst, k): return sum(x[k] for x in lst)
    ar = dict(raun_tekjur=tot(actual_y, 'tekjur'), raun_ebitda=tot(actual_y, 'ebitda'),
              spa_tekjur=tot(rest_y, 'tekjur'), spa_ebitda=tot(rest_y, 'ebitda'),
              p10_ebitda=tot(rest_y, 'ebitda_p10'), p90_ebitda=tot(rest_y, 'ebitda_p90'))
    ar['ar_tekjur'] = ar['raun_tekjur'] + ar['spa_tekjur']; ar['ar_ebitda'] = ar['raun_ebitda'] + ar['spa_ebitda']
    out = dict(company=D.get('company'), as_of=D.get('as_of'), model=dict(arstidir=F['season'], grunnstig=F['base'], leitni_man=F['g'], sigma=F['sigma'], efnishlutfall=F['mat']),
               assumptions=A, forecast=[{k: round(v, 2) if isinstance(v, float) else v for k, v in f.items()} for f in fc], backtest=bt, year=ar, oneoffs_excluded=one)
    json.dump(out, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"OK spá {months[0]}–{months[-1]}. Árstíðir: {'já' if F['season'] else 'nei (< 13 mán.)'}. Leitni {F['g']*100:.2f}%/mán, σ {F['sigma']*100:.1f}%. "
          f"Árið {year}: tekjur {ar['ar_tekjur']/1e6:.1f} m, EBITDA {ar['ar_ebitda']/1e6:.1f} m (bil {(ar['raun_ebitda']+ar['p10_ebitda'])/1e6:.1f}–{(ar['raun_ebitda']+ar['p90_ebitda'])/1e6:.1f}). "
          f"Bakprófun: {bt}")

if __name__ == '__main__':
    main()
