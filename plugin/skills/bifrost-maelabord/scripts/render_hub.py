#!/usr/bin/env python3
"""Bifröst mælaborð: smíðar miðstöðina (index.html) úr föstu sniðmáti og hub.json.

Notkun:
  render_hub.py --data hub.json --out build/index.html
  render_hub.py --example --out /tmp/index.html

hub.json (sjá skills/bifrost-skyndiuttekt/template/schema.md):
  meta:  company, company_acc (þolfall, „fyrir DT Vélsmiðjuna ehf.“), initials, as_of (DD.MM.ÁÁÁÁ),
         source_dates (texti í fæti, t.d. „16.–17.10.2026“)
  hero:  title, sub, text, figures [[gildi, skýring] × 4]
  top:   [{sev: h|m|l, title, text, src}]  3–5 brýnustu atriðin, raðað eftir áhrifum
  cards: [{title, tabs, label, value, note, href, color (--s1…--s7), status: up|warn|dn|info, pill?}]
         href afstætt (stjorn.html …) eða slóð artifacts (Sjálfvirknivæðing, opnast með data-nav)
  recommended: [{id, reasons: [..]}]  úr sermaelabord/flokka.py (efstu 1–3)
Pakkarnir koma úr skills/sermaelabord/assets/pakkar.json.
"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render as R

SKILLS = R.SKILLS
PILL = dict(up='l', warn='m', dn='h', info='i', opt='i')
PTXT = dict(up='í lagi', warn='athuga', dn='bregðast við', info='frumgerð', opt='valið')


def fragments(H):
    PK = json.load(open(os.path.join(SKILLS, 'sermaelabord', 'assets', 'pakkar.json'), encoding='utf-8'))
    pk = {p['id']: p for p in PK}
    CO = H['meta']['company_acc']
    esc = lambda x: x.replace('"', '&quot;')
    prm = lambda heiti: f'Bættu mælaborðinu „{heiti}“ við Bifröst-miðstöðina fyrir {CO} (skill: sermaelabord).'
    cards = ''.join(
        f'''<a class="card hub" href="{c['href']}"{' data-nav' if c['href'].startswith('http') else ''} style="--c:var({c['color']})"><div class="ch"><h2><span class="num">{i+1}</span>{c['title']}</h2><span class="pill {PILL[c['status']]}">{c.get('pill') or PTXT[c['status']]}</span></div>
<div class="kv"><span class="sub">{c['label']}</span><b>{c['value']}</b><span class="sub">{c['note']}</span></div><p class="sub tabsline">{c['tabs']}</p><span class="go">Opna →</span></a>''' for i, c in enumerate(H['cards']))
    TL = [dict(r, heiti=pk[r['id']]['heiti']) for r in H.get('recommended', [])[:3] if r['id'] in pk]
    tids = [t['id'] for t in TL]
    tlist = ''.join(f"""<li data-q="{(t['heiti']+' '+pk[t['id']]['flokkur']).lower()}" class="tl"><div><b>{t['heiti']}</b><p class="sub">{pk[t['id']]['flokkur']}: {', '.join(pk[t['id']]['kpi'][:3]).lower()}.</p><p class="why">Af hverju: {'; '.join(t['reasons'])}.</p></div><div class="addact"><button class="btn" type="button" data-prompt="{esc(prm(t['heiti']))}">Afrita skipun</button></div></li>""" for t in TL)
    ind = ''.join(f"""<li data-q="{(p['heiti']+' '+p['flokkur']+' '+p['daemi']).lower()}"><div><b>{p['heiti']}</b><p class="sub">{p['flokkur']} · {p['daemi']}</p></div><div class="addact"><button class="btn ghost" type="button" data-prompt="{esc(prm(p['heiti']))}">Afrita skipun</button></div></li>""" for p in PK if p['id'] not in tids)
    add = f'<li class="grp">Mælt með fyrir þitt félag · ÍSAT og starfsemi í BC</li>{tlist}<li class="grp">Aðrir atvinnugreinapakkar</li>{ind}<li class="grp">Annað</li>'
    chips = ''.join(f'<span class="pill m">{t["heiti"]}</span>' for t in TL)
    top = ''.join(f'<div class="d-item"><span class="d-ico {t["sev"]}">{i+1}</span><div><b>{t["title"]}</b><p>{t["text"]}</p></div><span class="amt">{t["src"]}</span></div>' for i, t in enumerate(H['top']))
    row = ''.join(f'<div><b>{v}</b><span>{l}</span></div>' for v, l in H['hero']['figures'])
    return dict(cards=cards, add=add, chips=chips, top=top, hero_row=row,
                prompt_other=esc(f'Búðu til nýtt Bifröst-mælaborð fyrir {CO} og bættu því í miðstöðina (skill: bifrost-maelabord): '))


def build(H):
    html = fragments(H)
    data = {'meta': H['meta'], 'text': {'hero_title': H['hero']['title'], 'hero_sub': H['hero']['sub'], 'hero_text': H['hero']['text']}, 'html': html}
    ex = json.load(open(os.path.join(R.tdir('bifrost-skyndiuttekt'), 'example.json'), encoding='utf-8'))
    errs = R.shape_errors({k: ex[k] for k in ('meta', 'hero', 'top', 'cards')}, H)
    if errs:
        sys.exit('hub.json passar ekki við sniðmát:\n  ' + '\n  '.join(errs[:30]))
    return R.render('bifrost-skyndiuttekt', data, strict=False)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--data'); ap.add_argument('--example', action='store_true'); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    src = os.path.join(R.tdir('bifrost-skyndiuttekt'), 'example.json') if a.example else a.data
    H = json.load(open(src, encoding='utf-8'))
    out = build(H)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, 'w', encoding='utf-8').write(out)
    print(f'miðstöð: {len(out)//1024} KB → {a.out}')


if __name__ == '__main__':
    main()
