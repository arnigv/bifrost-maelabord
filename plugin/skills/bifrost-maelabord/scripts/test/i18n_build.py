#!/usr/bin/env python3
"""Smíðar orðabók (template/i18n/<lang>.json) úr þýðingum á textaeiningum.

Notkun:
  i18n_build.py units  <sniðmát> > units.json            # telur upp einingar (sjá i18n_units.py)
  i18n_build.py build  <sniðmát> units.json map.json out.json
map.json eða map.py (M = {númer: r"þýðing"}): {"<númer einingar>": "þýðing", ...} (einingar án þýðingar eru gögn/lyklar og haldast).
Hver þýðing verður að pari með samhengi (t.d. >texti<, 'texti', `texti`, ="texti") svo stuttir bútar
skiptist aðeins út þar sem þeir standa einir og sér, ekki inni í öðrum orðum eða kóða.
"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from i18n_units import units

LEFT = ['>', "'", '"', '`', '="']
RIGHT = ['<', "'", '"', '`', '"']


def contextual(src, u, t):
    pairs = []
    for l, r in zip(LEFT, RIGHT):
        a = l + u + r
        if a in src:
            tt = t
            if l in ("'", '`') and l in tt and ('\\' + l) not in u:  # gæsalappir í þýðingu inni í JS-streng
                tt = tt.replace(l, '\\' + l) if l == "'" else tt
            pairs.append([a, l + tt + r])
    if not pairs and u in src:
        pairs.append([u, t])  # sjaldgæft: eining án afmörkunar (t.d. hluti af lengri streng)
    return pairs


def build(tpl, U, M):
    src = open(tpl, encoding='utf-8').read()
    cand, seen = [], set()
    for k, t in M.items():
        if isinstance(k, str) and k.startswith('RAW:'):  # hrár bútur án samhengis (t.d. kóðabreyting fyrir snið)
            cand.append([k[4:], t]); seen.add(k[4:]); continue
        u = U[k] if isinstance(k, int) else k  # númer í units.json eða einingin sjálf
        for p in contextual(src, u, t):
            if p[0] not in seen:
                seen.add(p[0]); cand.append(p)
    # herma eftir translate() (lengstu fyrst) og halda aðeins pörum sem hafa áhrif
    out, cur = [], src
    for a, b in sorted(cand, key=lambda p: -len(p[0])):
        if a in cur:
            cur = cur.replace(a, b); out.append([a, b])
    return out


if __name__ == '__main__':
    if sys.argv[1] in ('units', 'all'):
        # 'all': allir strengir með bókstöfum (víðtækara; flokkaðu sjálf/ur hvað er texti og hvað kóði)
        import i18n_units as UN
        if sys.argv[1] == 'all':
            src0 = open(sys.argv[2], encoding='utf-8').read()
            # kóðaorð: auðkenni, CSS-klasar, lyklar í sýnidæmi -> ekki texti
            code = set(re.findall(r'\.([A-Za-z_]\w*)|\b([A-Za-z_]\w*)\s*[:=(]', src0))
            code = {a or b for a, b in code}
            code |= {c for m in re.finditer(r'class="([^"$]*)"', src0) for c in m.group(1).split()}
            code |= set(re.findall(r'[.#]([A-Za-z][\w-]*)', ''.join(re.findall(r'<style>(.*?)</style>', src0, re.S))))
            ex = os.path.join(os.path.dirname(sys.argv[2]), 'example.json')
            if os.path.exists(ex):
                code |= set(re.findall(r'"([A-Za-z_]\w*)"\s*:', open(ex, encoding='utf-8').read()))
                code |= set(re.findall(r':\s*"([a-z_]+)"', open(ex, encoding='utf-8').read()))
            def test(t):
                t2 = t.strip()
                if not re.search(r'[A-Za-zÀ-ÿ]{2}', t2):
                    return False
                if ' ' in t2 or t2[:1].isupper() or re.search(r'[À-ÿ]', t2):
                    return True
                return re.fullmatch(r'[a-z]{3,}', t2) is not None and t2 not in code
            UN.TEST = test
        print(json.dumps(units(open(sys.argv[2], encoding='utf-8').read()), ensure_ascii=False, indent=0))
    else:
        tpl, uf, mf, of = sys.argv[2:6]
        U = json.load(open(uf, encoding='utf-8'))
        if mf.endswith('.py'):
            ns = {}; exec(open(mf, encoding='utf-8').read(), ns); M = ns['M']
        else:
            M = json.load(open(mf, encoding='utf-8'))
        P = build(tpl, U, M)
        json.dump(P, open(of, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print(f'{len(P)} pör úr {len(M)} þýðingum')
