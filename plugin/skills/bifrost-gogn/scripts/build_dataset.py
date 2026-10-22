#!/usr/bin/env python3
"""Bifröst gagnalag: smíðar dataset.json úr hreyfingum fjárhagslykla.

Inntak (eitt eða fleiri):
  --pl  skrá með svari period_breakdown (field_type=net_change, G/L Account) — má gefa oft (t.d. í ár og í fyrra)
  --accounts  skrá með G/L Account færslum (svar data_batch_records) með Name og AccountSubcategoryDescript_
  --profile   valfrjáls JSON með fjölda færslna, t.d. {"jobs":15,"item_entries":16,"bank_accounts":6,...}
Úttak: dataset.json (--out)

Formerki: tekjur sem jákvæð tala, kostnaður sem jákvæð tala. Fjárhæðir í kr.
"""
import argparse, json, os, re, statistics, sys
from collections import defaultdict

CATS = ['tekjur', 'vorunotkun', 'laun', 'husnaedi', 'annar_rekstur', 'afskriftir', 'fjarmagn', 'oreglulegt', 'skattar']
LABEL = {'tekjur': 'Tekjur', 'vorunotkun': 'Vörunotkun og aðföng', 'laun': 'Laun og launatengd gjöld', 'husnaedi': 'Húsnæði',
         'annar_rekstur': 'Annar rekstrarkostnaður', 'afskriftir': 'Afskriftir', 'fjarmagn': 'Fjármagnsliðir',
         'oreglulegt': 'Óreglulegir liðir', 'skattar': 'Skattar'}

RULES = [  # (flokkur, regex á nafn + undirflokk), fyrsta samsvörun ræður
    ('afskriftir', r'afskrift|depreciat'),
    ('skattar', r'skattar ársins|(?<!fjármagns)tekjuskatt|income tax'),
    ('fjarmagn', r'arðstekj|arður|arðgreiðsl|hlutdeild í afkomu|dividend|vaxta|vextir|vaxtakostn|gengis|fjármagnstekju|dráttarvext|interest|exchange'),
    ('oreglulegt', r'óreglul|aðrar tekjur og útgjöld'),
    ('laun', r'laun|lífeyri|tryggingargjald|orlof|starfsm|dagpening|bifreiðahlunn|bifreiðastyrk|félagsgjöld|salar|payroll|wage|employee|personnel|pension|social security|staff'),
    ('husnaedi', r'húsaleig|húsnæð|^hiti|hiti |rafmagn(?!.*rafbíl)|þrif|fasteignagj|leigukostn|\brent\b|building|premises|electricity|heating|utilities|cleaning|property tax'),
    ('vorunotkun', r'vörukaup|vöruinnkaup|orkukaup|kaup á |kostnaðarverð|innkaup|birgð|flutningskostn|flutningur|aðflutn|hráefni|efni|aðföng|framleiðslukostn|verkkostn|kostnað(ur|ar) verka|seldar vörur|cost of goods|purchase|cost of sales|materials|freight|cogs'),
    ('tekjur', r'^sala|sala |tekjur|veittur afsl|seld verk|sales|revenue|income'),
]

# Flokkur lykils í BC (Account Category) er óháður tungumáli: notaður þegar heitið segir ekki til.
BC_INCOME = ('income', '4')
BC_COGS = ('cost of goods sold', '5')
BC_EXPENSE = ('expense', '6')


def categorize(name, sub, total, bccat=''):
    s = f'{name} | {sub}'.lower()
    bc = (bccat or '').strip().lower()
    first = [r for r in RULES if r[0] in ('afskriftir', 'skattar', 'fjarmagn', 'oreglulegt')]
    rest = [r for r in RULES if r[0] not in ('afskriftir', 'skattar', 'fjarmagn', 'oreglulegt')]
    for cat, rx in first:
        if re.search(rx, s):
            return cat
    # Sala/leiðréttingar sölu eru tekjur óháð formerki
    if re.search(r'sölu verka|sala verka|seld verk|leiðrétting sölu|mótreikningur sölu', s):
        return 'tekjur'
    # Heiti sem segir kostnaðarflokk ræður óháð formerki (t.d. bakfærð laun eða birgðaleiðrétting í kredit)
    for cat, rx in rest:
        if cat != 'tekjur' and re.search(rx, s):
            return cat
    # kreditstaða á óflokkuðum rekstrarlykli = tekjur, nema mótfærslur á kostnað
    if total < 0 and bc not in BC_EXPENSE + BC_COGS and not re.search(r'fengin|mótreikn|leiðrétt|endurgreidd|afsláttur af (vöru)?kaup', s):
        return 'tekjur'
    for cat, rx in rest:
        if cat == 'tekjur' and bc in BC_EXPENSE + BC_COGS:
            continue   # kostnaðarlykill í BC getur ekki verið tekjur þótt heitið nefni sölu
        if re.search(rx, s):
            return cat
    if bc in BC_COGS:
        return 'vorunotkun'
    if bc in BC_INCOME:
        return 'tekjur'
    return 'annar_rekstur'

def ym_of(rng):
    m = re.match(r'(\d{4})-(\d{2})-01\.\.', rng or '')
    return f'{m.group(1)}-{m.group(2)}' if m else None

def load(path):
    t = open(path, encoding='utf-8').read()
    return json.loads(t)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pl', action='append', required=True)
    ap.add_argument('--bs', action='append', help='period_breakdown net_change á efnahagslyklum (Balance Sheet)')
    ap.add_argument('--accounts')
    ap.add_argument('--profile')
    ap.add_argument('--company', default='')
    ap.add_argument('--env', default='')
    ap.add_argument('--asof', required=True, help='YYYY-MM-DD')
    ap.add_argument('--out', default='dataset.json')
    ap.add_argument('--lang', choices=['is', 'en'], help='þvinga tungumál; annars greint af heitum lykla')
    a = ap.parse_args()

    sub, bccat = {}, {}
    if a.accounts:
        acc = load(a.accounts)
        recs = acc['results'][0]['records'] if 'results' in acc else acc.get('records', acc)
        for r in recs:
            no = r['primaryKey']['No_'] if 'primaryKey' in r else r['no']
            f = r.get('fields', r)
            sub[no] = f.get('AccountSubcategoryDescript_', '') or ''
            bccat[no] = str(f.get('AccountCategory', f.get('Account_Category', f.get('Account Category', ''))) or '')

    acct = {}  # no -> {name, months{ym:amount}}
    for p in a.pl:
        d = load(p)
        keymap = {b['key']: ym_of(b.get('date_range')) for b in d.get('bucket_definitions', [])}
        for r in d['rows']:
            e = acct.setdefault(r['No_'], {'name': r.get('Name', ''), 'months': {}})
            for k, ym in keymap.items():
                if ym and k in r:
                    v = float(r[k])
                    if v:
                        e['months'][ym] = e['months'].get(ym, 0.0) + v

    asof_ym = a.asof[:7]
    all_m = sorted({ym for e in acct.values() for ym in e['months']} | {asof_ym})
    months = [m for m in all_m if m <= asof_ym]

    accounts = []
    for no, e in sorted(acct.items()):
        tot = sum(e['months'].values())
        cat = categorize(e['name'], sub.get(no, ''), tot, bccat.get(no, ''))
        accounts.append({'no': no, 'name': e['name'], 'subcategory': sub.get(no, ''), 'cat': cat,
                         'months': {m: round(e['months'].get(m, 0.0), 2) for m in months if e['months'].get(m)}})

    def msum(cat, m):
        s = sum(x['months'].get(m, 0.0) for x in accounts if x['cat'] == cat)
        return -s if cat in ('tekjur',) else s

    rows = []
    for m in months:
        r = {'ym': m}
        for c in CATS:
            r[c] = round(msum(c, m), 2)
        r['ebitda'] = round(r['tekjur'] - r['vorunotkun'] - r['laun'] - r['husnaedi'] - r['annar_rekstur'], 2)
        r['hagnadur_fs'] = round(r['ebitda'] - r['afskriftir'] - r['fjarmagn'] - r['oreglulegt'], 2)
        rows.append(r)

    # ófullbókuð tímabil
    def med(c):
        v = [r[c] for r in rows if r['tekjur'] > 0 and r[c] > 0]
        return statistics.median(v) if v else 0
    ml, mv = med('laun'), med('vorunotkun')
    for r in rows:
        why = []
        if r['tekjur'] > 0 and ml > 0 and r['laun'] < 0.2 * ml:
            why.append('laun vantar')
        if r['tekjur'] > 0 and mv > 0 and r['vorunotkun'] < 0.2 * mv:
            why.append('vörunotkun vantar')
        if r['ym'] == asof_ym:
            why.append('yfirstandandi mánuður')
        if all(abs(r[c]) < 1 for c in CATS):
            why.append('engar færslur')
        r['complete'] = not why
        r['incomplete_reason'] = ', '.join(why)

    # einskiptisliðir: lykill með hreyfingu í aðeins einum mánuði og ≥10% af tekjum mánaðarins
    oneoffs = []
    revm = {r['ym']: r['tekjur'] for r in rows if r['complete']}
    for x in accounts:
        act = {m: v for m, v in x['months'].items() if abs(v) >= 1}
        if len(act) == 1:
            m, v = next(iter(act.items()))
            if revm.get(m, 0) > 0 and abs(v) >= 0.10 * revm[m]:
                oneoffs.append({'no': x['no'], 'name': x['name'], 'cat': x['cat'], 'ym': m, 'amount': round(-v if x['cat'] == 'tekjur' else v, 2)})


    # efnahagur: staða í lok mánaðar = upphafsstaða (bil "..") + uppsöfnuð hreyfing
    balance = None
    if a.bs:
        # Íslensk og ensk heiti (CRONUS og staðlaðir undirflokkar BC: Cash, Receivables, Inventory, Fixed Assets …)
        BSR = [('fastafjarmunir', r'land|bygging|tækjab|tæki og|innrétt|bifreiðar$|^bifreiðar|uppsafnaðar afskr|fastafj|hugbúnaður \(eign|fixed asset|equipment|machinery|vehicles|accum\w*\.? deprec|leasehold'),
               ('birgdir', r'birgð|inventor|(?<!capital )\bstock\b|finished goods|raw material|\bwip\b'), ('krofur', r'viðskiptam|kröfur|fyrirframgr|receivable|customers|prepa'),
               ('handbaert_fe', r'^(?!.*(lán|loan|langtíma|long.term|ógreit|orlof|starfsmanna|payable|owed)).*(banki|bankareikn|sjóður|handbært|veltureikn|sparireikn|\bcash\b|\bbank|petty|liquid)'),
               ('eigid_fe', r'hlutafé|eigið fé|óráðstaf|varasjóð|lögbundinn|equity|share capital|capital stock|retained|reserve'),
               ('langtimaskuldir', r'langtíma|skuldabréf|long.term|mortgage|bonds'),
               ('skammtimaskuldir', r'vsk|virðisauka|staðgreiðsl|ógreitt|ógreidd|lánardrott|kreditkort|skammtíma|payable|vendors|\bvat\b|sales tax|accrued|current liabil|withholding')]
        bacct = {}
        for pth in a.bs:
            d = load(pth)
            km = {b['key']: ym_of(b.get('date_range')) for b in d.get('bucket_definitions', [])}
            open_key = [b['key'] for b in d.get('bucket_definitions', []) if (b.get('date_range') or '').startswith('..')]
            for r in d['rows']:
                e = bacct.setdefault(r['No_'], {'name': r.get('Name', ''), 'open': 0.0, 'mv': {}})
                for k, ym in km.items():
                    if ym and k in r and float(r[k]):
                        e['mv'][ym] = e['mv'].get(ym, 0.0) + float(r[k])
                for k in open_key:
                    if k in r and not e.get('_opened'):
                        e['open'] = float(r[k]); e['_opened'] = True
        first = months[0] if months else asof_ym
        balance = {'months': months, 'accounts': []}
        cats = defaultdict(lambda: [0.0] * len(months))
        for no, e in sorted(bacct.items()):
            s = f"{e['name']} | {sub.get(no, '')}".lower(); cat = None
            for c, rx in BSR:
                if re.search(rx, s): cat = c; break
            lvl = e['open'] + sum(v for m, v in e['mv'].items() if m < first)
            levels = []
            for m in months:
                lvl += e['mv'].get(m, 0.0); levels.append(round(lvl, 2))
            last_lvl = levels[-1] if levels else e['open']
            if cat is None:
                cat = 'skammtimaskuldir' if last_lvl < 0 else 'adrar_eignir'
            elif cat in ('langtimaskuldir', 'skammtimaskuldir') and last_lvl > 0 and re.search(r'skuldabréf|bonds|hlutabréf|shares', s):
                cat = 'adrar_eignir'   # skuldabréf/hlutabréf í debetstöðu eru eign (verðbréfaeign), ekki skuld
            elif cat == 'skammtimaskuldir' and last_lvl > 0 and re.search(r'kreditkort|debetkort|kortauppgj|greiðslukort|card', s):
                cat = 'krofur'         # kortauppgjör í debetstöðu (verslun) er krafa á færsluhirði, ekki kortaskuld
            balance['accounts'].append({'no': no, 'name': e['name'], 'cat': cat, 'levels': levels})
            for i, v in enumerate(levels): cats[cat][i] += v
        # eigið fé fær uppsafnaða afkomu ársins (rekstrarreikningur ekki lokaður)
        cum = 0.0
        res = []
        for r in rows:
            cum += r['hagnadur_fs'] - r['skattar']; res.append(cum)
        balance['categories'] = {c: [round(-v if c in ('eigid_fe', 'langtimaskuldir', 'skammtimaskuldir') else v, 2) for v in vals] for c, vals in cats.items()}
        balance['categories']['afkoma_arsins'] = [round(v, 2) for v in res]
        C = balance['categories']
        get = lambda k: C.get(k, [0.0] * len(months))
        eignir = [sum(get(k)[i] for k in ('fastafjarmunir', 'birgdir', 'krofur', 'handbaert_fe', 'adrar_eignir')) for i in range(len(months))]
        skuldir = [get('skammtimaskuldir')[i] + get('langtimaskuldir')[i] for i in range(len(months))]
        C['eignir'] = [round(v, 2) for v in eignir]
        C['eigid_fe_bokad'] = get('eigid_fe')
        # eigið fé sem mismunur eigna og skulda: nær líka yfir óuppgerða afkomu fyrri ára
        C['eigid_fe'] = [round(eignir[i] - skuldir[i], 2) for i in range(len(months))]
        # stemming innan mánaðar: summa efnahags + rekstrar hreyfinga á að vera 0
        diff = []
        for i, m in enumerate(months):
            bsm = sum(e['mv'].get(m, 0.0) for e in bacct.values())
            plm = sum(x['months'].get(m, 0.0) for x in accounts)
            diff.append({'ym': m, 'mismunur': round(bsm + plm, 2)})
        balance['stemming'] = [d for d in diff if abs(d['mismunur']) >= 1]

    def agg(sel):
        o = {c: round(sum(r[c] for r in sel), 2) for c in CATS + ['ebitda', 'hagnadur_fs']}
        o['months'] = [r['ym'] for r in sel]
        return o
    year = asof_ym[:4]
    comp = [r for r in rows if r['complete']]
    cy = [r for r in comp if r['ym'].startswith(year)]
    last_cy = cy[-1]['ym'] if cy else None
    py_same = [r for r in rows if last_cy and r['ym'].startswith(str(int(year) - 1)) and r['ym'][5:] <= last_cy[5:]]
    py_full = [r for r in rows if r['ym'].startswith(str(int(year) - 1))]

    out = {
        'company': a.company, 'environment': a.env, 'as_of': a.asof,
        'categories': {c: LABEL[c] for c in CATS},
        'months': rows,
        'ytd': agg(cy), 'py_same_period': agg(py_same) if py_same else None, 'py_full': agg(py_full) if py_full else None,
        'incomplete': [{'ym': r['ym'], 'reason': r['incomplete_reason']} for r in rows if not r['complete']],
        'oneoffs': oneoffs,
        'accounts': accounts,
        'profile': load(a.profile) if a.profile else None,
        'balance': balance,
    }
    # Tungumál grunngagna: íslensk lyklaheiti → 'is', annars 'en'. Mælaborðin opnast á þessu máli.
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'bifrost-maelabord', 'scripts'))
    try:
        import i18n as I
        out['lang'] = a.lang or I.detect_lang({'a': [x['name'] for x in accounts], 'c': a.company})
    except ImportError:
        out['lang'] = a.lang or 'is'
    n_moves = sum(len(x['months']) for x in accounts)
    out['n_complete'] = len(cy)
    if n_moves == 0:
        out['empty'] = True
        json.dump(out, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'TÓMT: {a.company} hefur engar bókaðar hreyfingar á tímabilinu. Ekki smíða mælaborð; segðu notandanum frá því '
              '(t.d. nýtt félag, rangt félag eða rangt umhverfi).')
        raise SystemExit(2)
    if len(cy) < 3:
        print(f'AÐVÖRUN: aðeins {len(cy)} fullbókaðir mánuðir {year}. Mælaborðin sýna „ónóg gögn“ þar sem samanburð vantar; spá krefst 6 mánaða.')
    json.dump(out, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    y = out['ytd']
    print(f"OK {a.company} [{out['lang']}]: {len(accounts)} lyklar, {len(rows)} mánuðir, fullbókað {len(cy)} í {year}. "
          f"Tekjur {y['tekjur']/1e6:.1f} m, EBITDA {y['ebitda']/1e6:.1f} m. Ófullbókað: {[i['ym'] for i in out['incomplete']]}. Einskipti: {len(oneoffs)}.")
    unk = [x['no'] + ' ' + x['name'] for x in accounts if x['cat'] == 'annar_rekstur' and not x['subcategory']]
    if unk:
        print('Athuga flokkun (enginn undirflokkur, settir í annan rekstur):', '; '.join(unk[:15]))

if __name__ == '__main__':
    main()
