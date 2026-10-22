#!/usr/bin/env python3
"""Flokkar félag í sérpakka (yfirflokka) út frá ÍSAT-númeri og notkun í BC.

Notkun:
  flokka.py --signals signals.json [--isat 43.21] [--out tillogur.json]

signals.json (talningar úr BC, `data_record_count`):
  {"jobs": 15, "job_ledger_entries": 51, "resources": 6, "time_sheets": 0, "items": 16,
   "item_ledger_entries": 16, "production_boms": 0, "standard_sales_codes": 0, "locations": 1,
   "fixed_assets": 4, "fa_share_of_assets": 0.25, "lt_loans_share": 0.15, "companies_in_tenant": 4,
   "related_companies": 2, "deferred_revenue_balance": 0, "fx_share_of_sales": 0.02,
   "store_dimension": 0, "pos_customers": 0, "card_settlement_accounts": 0}
  related_companies: tengdir viðskiptamenn/lánardrottnar eða IC-aðilar sem félagið á VIÐSKIPTI við (ekki fjöldi félaga í tenant).
  store_dimension: 1 ef vídd lýsir verslunum/útibúum; pos_customers: staðgreiðsluviðskiptamenn á verslun; card_settlement_accounts: kortauppgjörslyklar.
Skilar raðaðri tillögu: [{id, heiti, stig, ástæður}], efstu 3 eru tillögur í miðstöð.
"""
import argparse, json, os
H = os.path.dirname(os.path.abspath(__file__))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--signals', required=True); ap.add_argument('--isat'); ap.add_argument('--out')
    a = ap.parse_args()
    S = json.load(open(a.signals, encoding='utf-8')); P = json.load(open(os.path.join(H, '..', 'assets', 'pakkar.json'), encoding='utf-8'))
    g = lambda k: S.get(k, 0) or 0
    isat = (a.isat or '').strip()
    sc = {p['id']: [0.0, []] for p in P}
    def add(i, v, why): sc[i][0] += v; sc[i][1].append(why)
    # 1) ÍSAT gefur fyrstu ágiskun (lengsta forskeyti vinnur)
    if isat:
        best = None
        for p in P:
            for pre in p['isat']:
                if isat.startswith(pre) and (best is None or len(pre) > best[1]): best = (p['id'], len(pre))
            for pre in p.get('isat_ef_verk', []):
                if isat.startswith(pre) and g('jobs') > 0: add(p['id'], 3, f'ÍSAT {isat} og verk í notkun')
        if best: add(best[0], 4, f'ÍSAT {isat}')
    # 2) Notkun í BC staðfestir
    if g('job_ledger_entries') >= 20 or g('jobs') >= 5: add('verktakar', 3, f"{g('jobs')} verk og {g('job_ledger_entries')} verkbókarfærslur")
    if g('time_sheets') > 0: add('serfraedi', 3, f"{g('time_sheets')} tímaskráningar")
    elif g('resources') >= 3 and g('job_ledger_entries') > 0: add('serfraedi', 1, f"{g('resources')} forðar bókaðir á verk")
    if g('standard_sales_codes') > 0 or g('deferred_revenue_balance') > 0: add('saas', 2, 'endurteknir reikningar eða fyrirframinnheimtar tekjur'); add('fasteignir', 1, 'endurteknir reikningar')
    if g('item_ledger_entries') >= 500: add('heildsala', 3, f"{g('item_ledger_entries')} birgðafærslur")
    if g('production_boms') > 0: add('framleidsla', 3, f"{g('production_boms')} uppskriftir (BOM)")
    if g('locations') >= 3 and (g('item_ledger_entries') >= 100 or g('store_dimension') or g('pos_customers') >= 2 or g('card_settlement_accounts')):
        add('smasala', 3 if g('item_ledger_entries') >= 500 else 2, f"{g('locations')} staðsetningar" + (', verslunarvídd' if g('store_dimension') else '') + (f", {g('pos_customers')} staðgreiðsluviðskiptamenn" if g('pos_customers') >= 2 else ''))
    if g('fa_share_of_assets') >= 0.5 and g('lt_loans_share') >= 0.3: add('fasteignir', 3, 'eignir og langtímalán vega þungt')
    if g('fx_share_of_sales') >= 0.5 and g('item_ledger_entries') > 0: add('sjavarutvegur', 1, 'meirihluti sölu í erlendri mynt')
    # Samstæða aðeins ef félagið á viðskipti við önnur félög (tengdir viðskiptamenn/lánardrottnar, IC-aðilar).
    # Fjöldi félaga í tenant einn og sér segir ekkert (sandkassar og prófunarfélög).
    if g('related_companies') >= 1: add('samstaeda', 2 + (1 if g('companies_in_tenant') >= 2 else 0), f"{g('related_companies')} tengd félög í viðskiptum")
    out = sorted([dict(id=p['id'], heiti=p['heiti'], flokkur=p['flokkur'], stig=sc[p['id']][0], astaedur=sc[p['id']][1]) for p in P if sc[p['id']][0] > 0], key=lambda x: -x['stig'])
    if a.out: json.dump(out, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for o in out[:5]: print(f"{o['stig']:>4.0f}  {o['heiti']:<32} {'; '.join(o['astaedur'])}")
    if not out: print('Engin skýr flokkun: bjóddu notanda að velja úr lista.')

if __name__ == '__main__':
    main()
