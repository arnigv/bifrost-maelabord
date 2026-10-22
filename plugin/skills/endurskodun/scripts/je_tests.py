#!/usr/bin/env python3
"""Færsluprófanir (journal entry testing) á fjárhagsfærslum úr BC.

Inntak: --entries gl.json — listi af færslum með lyklunum
  account, date (YYYY-MM-DD), doc_type, doc_no, description, amount, user, source_code, created (valkvætt)
--materiality M (kr.)  --year-end YYYY-MM-DD  --revenue-accounts 1110,1120,...  --out je.json
Snið félags (valkvætt; sjálfgefið = óbreytt hegðun):
  --weekend-ok            helgarsala er eðlileg (smásala, veitingar, gisting): helgarprófið flaggar þá aðeins
                          handfærslur (upprunakóði utan sjálfvirkra kóða), ekki sjálfvirkar sölu-/kassafærslur.
  --auto-sources A,B      viðbótarupprunakóðar sem teljast sjálfvirkir (kassakerfi/POS, bankainnlestur, yfirlit),
                          úr töflunni Source Code í BC. Bætast við AUTO_SOURCES, koma ekki í stað þeirra.
  --profile F             dataset.json (lesið úr lyklinum `profile`) eða profile.json. Lyklar:
                          weekend_trading / retail / hospitality (true = --weekend-ok),
                          auto_sources / pos_sources (listi kóða = --auto-sources). CLI-rofar bætast við.
Prófanir (ISA 240): handfærðar tekjur, sléttar fjárhæðir, færslur um helgar, færslur yfir framkvæmdamikilvægi,
seinar færslur (eftir lok tímabils), sjaldgæfir notendur, ójöfnuður innan dagsetningar/fylgiskjals, tómar lýsingar.
Niðurstaða er listi af ábendingum með alvarleika, ekki niðurstaða um misferli.
"""
import argparse, json, collections
from datetime import date

AUTO_SOURCES = {'SALA', 'SALES', 'INNKAUP', 'PURCHASES', 'BIRGÐIR', 'INVENTORY', 'FASTAFJ', 'FA', 'GREIÐSLA', 'PAYMENTS', 'INNGR', 'CASHRECJNL'}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--entries', required=True); ap.add_argument('--materiality', type=float, required=True)
    ap.add_argument('--year-end', required=True); ap.add_argument('--revenue-accounts', default='')
    ap.add_argument('--perf', type=float, default=0.75); ap.add_argument('--out', default='je.json')
    ap.add_argument('--weekend-ok', action='store_true'); ap.add_argument('--auto-sources', default='')
    ap.add_argument('--profile')
    a = ap.parse_args()
    E = json.load(open(a.entries, encoding='utf-8'))
    prof = {}
    if a.profile:
        P = json.load(open(a.profile, encoding='utf-8'))
        prof = (P.get('profile') if 'profile' in P else P) or {}
        if not isinstance(prof, dict): prof = {}
    weekend_ok = a.weekend_ok or any(bool(prof.get(k)) for k in ('weekend_trading', 'retail', 'hospitality'))
    extra = {x.strip().upper() for x in a.auto_sources.split(',') if x.strip()}
    for k in ('auto_sources', 'pos_sources'):
        v = prof.get(k) or []
        extra |= {str(x).strip().upper() for x in (v.split(',') if isinstance(v, str) else v) if str(x).strip()}
    auto = AUTO_SOURCES | extra
    pm = a.materiality * a.perf
    rev = set(x.strip() for x in a.revenue_accounts.split(',') if x.strip())
    ye = date.fromisoformat(a.year_end)
    users = collections.Counter(e.get('user', '') for e in E)
    rare = {u for u, n in users.items() if n <= max(3, len(E) * 0.005)}
    flags = collections.defaultdict(list)
    for e in E:
        d = date.fromisoformat(e['date'][:10]); amt = abs(e['amount']); src = (e.get('source_code') or '').upper()
        if e['account'] in rev and src not in auto:
            flags['handfaerdar_tekjur'].append(e)
        if amt >= 1_000_000 and amt % 1_000_000 == 0:
            flags['slettar_fjarhaedir'].append(e)
        if d.weekday() >= 5 and not (weekend_ok and src in auto):
            flags['helgar'].append(e)
        if amt >= pm:
            flags['yfir_mikilvaegi'].append(e)
        if e.get('created') and date.fromisoformat(e['created'][:10]) > ye and d <= ye:
            flags['seinar_faerslur'].append(e)
        if e.get('user') in rare:
            flags['sjaldgaefir_notendur'].append(e)
        if not (e.get('description') or '').strip():
            flags['an_lysingar'].append(e)
    bal = collections.defaultdict(float)
    for e in E: bal[(e['date'][:10], e.get('doc_no'))] += e['amount']
    flags['ojofnudur'] = [dict(date=k[0], doc_no=k[1], amount=v) for k, v in bal.items() if abs(v) > 1]
    LEVEL = dict(handfaerdar_tekjur='hátt', seinar_faerslur='hátt', ojofnudur='hátt', slettar_fjarhaedir='miðlungs',
                 yfir_mikilvaegi='miðlungs', sjaldgaefir_notendur='miðlungs', helgar='lágt', an_lysingar='lágt')
    out = dict(materiality=a.materiality, performance_materiality=pm, fjoldi=len(E),
               profanir=[dict(prof=k, alvarleiki=LEVEL.get(k, 'lágt'), fjoldi=len(v),
                              upphaed=sum(abs(x.get('amount', 0)) for x in v), daemi=v[:25]) for k, v in flags.items()])
    if weekend_ok or extra:  # aðeins skráð ef vikið er frá sjálfgefnu, svo úttak sjálfgefinnar keyrslu er óbreytt
        out['stillingar'] = dict(helgar_edlilegar=weekend_ok, vidbotar_upprunakodar=sorted(extra))
    json.dump(out, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    for p in out['profanir']:
        print(f"{p['prof']:<22} {p['alvarleiki']:<9} {p['fjoldi']:>5} færslur  {p['upphaed']/1e6:>10.1f} m")

if __name__ == '__main__':
    main()
