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
import render as R, i18n as I

SKILLS = R.SKILLS
PILL = dict(up='l', warn='m', dn='h', info='i', opt='i')
T = {
    'is': dict(ptxt=dict(up='í lagi', warn='athuga', dn='bregðast við', info='frumgerð', opt='valið'), open='Opna →', why='Af hverju',
               copy='Afrita skipun', g_rec='Mælt með fyrir þitt félag · ÍSAT og starfsemi í BC', g_other='Aðrir atvinnugreinapakkar', g_misc='Annað',
               prm=lambda h, co: f'Bættu mælaborðinu „{h}“ við Bifröst-miðstöðina fyrir {co} (skill: sermaelabord).',
               prm_other=lambda co: f'Búðu til nýtt Bifröst-mælaborð fyrir {co} og bættu því í miðstöðina (skill: bifrost-maelabord): '),
    'en': dict(ptxt=dict(up='on track', warn='check', dn='act now', info='prototype', opt='selected'), open='Open →', why='Why',
               copy='Copy prompt', g_rec='Recommended for your company · ISAT and BC activity', g_other='Other industry packs', g_misc='Other',
               prm=lambda h, co: f'Add the “{h}” dashboard to the Bifröst hub for {co} (skill: sermaelabord).',
               prm_other=lambda co: f'Create a new Bifröst dashboard for {co} and add it to the hub (skill: bifrost-maelabord): '),
}
PTXT = T['is']['ptxt']


def fragments(H, lang='is'):
    PK = json.load(open(os.path.join(SKILLS, 'sermaelabord', 'assets', 'pakkar.json'), encoding='utf-8'))
    if lang != 'is':
        PK = [dict(p, **(p.get(lang) or {})) for p in PK]
    pk = {p['id']: p for p in PK}
    L = T[lang]
    CO = H['meta']['company_acc']
    esc = lambda x: x.replace('"', '&quot;')
    prm = lambda heiti: L['prm'](heiti, CO)
    cards = ''.join(
        f'''<a class="card hub" href="{c['href']}"{' data-nav' if c['href'].startswith('http') else ''} style="--c:var({c['color']})"><div class="ch"><h2><span class="num">{i+1}</span>{c['title']}</h2><span class="pill {PILL[c['status']]}">{c.get('pill') or L['ptxt'][c['status']]}</span></div>
<div class="kv"><span class="sub">{c['label']}</span><b>{c['value']}</b><span class="sub">{c['note']}</span></div><p class="sub tabsline">{c['tabs']}</p><span class="go">{L['open']}</span></a>''' for i, c in enumerate(H['cards']))
    TL = [dict(r, heiti=pk[r['id']]['heiti']) for r in H.get('recommended', [])[:3] if r['id'] in pk]
    tids = [t['id'] for t in TL]
    tlist = ''.join(f"""<li data-q="{(t['heiti']+' '+pk[t['id']]['flokkur']).lower()}" class="tl"><div><b>{t['heiti']}</b><p class="sub">{pk[t['id']]['flokkur']}: {', '.join(pk[t['id']]['kpi'][:3]).lower()}.</p><p class="why">{L['why']}: {'; '.join(t['reasons'])}.</p></div><div class="addact"><button class="btn" type="button" data-prompt="{esc(prm(t['heiti']))}">{L['copy']}</button></div></li>""" for t in TL)
    ind = ''.join(f"""<li data-q="{(p['heiti']+' '+p['flokkur']+' '+p['daemi']).lower()}"><div><b>{p['heiti']}</b><p class="sub">{p['flokkur']} · {p['daemi']}</p></div><div class="addact"><button class="btn ghost" type="button" data-prompt="{esc(prm(p['heiti']))}">{L['copy']}</button></div></li>""" for p in PK if p['id'] not in tids)
    add = f'<li class="grp">{L["g_rec"]}</li>{tlist}<li class="grp">{L["g_other"]}</li>{ind}<li class="grp">{L["g_misc"]}</li>'
    chips = ''.join(f'<span class="pill m">{t["heiti"]}</span>' for t in TL)
    top = ''.join(f'<div class="d-item"><span class="d-ico {t["sev"]}">{i+1}</span><div><b>{t["title"]}</b><p>{t["text"]}</p></div><span class="amt">{t["src"]}</span></div>' for i, t in enumerate(H['top']))
    row = ''.join(f'<div><b>{v}</b><span>{l}</span></div>' for v, l in H['hero']['figures'])
    return dict(cards=cards, add=add, chips=chips, top=top, hero_row=row,
                prompt_other=esc(L['prm_other'](CO)))


def build(H, lang=None, hrefs=None, pages=None, primary=None):
    """lang: tungumál miðstöðvar (sjálfgefið: tungumál hub.json). Yfirlag fyrir hitt tungumálið: H['i18n'][lang]
    með sömu lögun og hub.json (meta, hero, top, cards, recommended), sjá schema.md."""
    src = I.data_lang(H)
    lang = lang or src
    primary = primary or src
    if lang != src:
        ov = (H.get('i18n') or {}).get(lang) or {}
        H = dict(H)
        for k in ('meta', 'hero'):
            if k in ov: H[k] = dict(H[k], **ov[k])
        for k in ('top', 'cards', 'recommended'):
            if k in ov: H[k] = [dict(a, **b) for a, b in zip(H[k], ov[k])] + H[k][len(ov[k]):]
    html = fragments(H, lang)
    data = {'lang': lang, 'meta': H['meta'], 'text': {'hero_title': H['hero']['title'], 'hero_sub': H['hero']['sub'], 'hero_text': H['hero']['text']}, 'html': html}
    ex = json.load(open(os.path.join(R.tdir('bifrost-skyndiuttekt'), 'example.json'), encoding='utf-8'))
    errs = R.shape_errors({k: ex[k] for k in ('meta', 'hero', 'top', 'cards')}, H)
    if errs:
        sys.exit('hub.json passar ekki við sniðmát:\n  ' + '\n  '.join(errs[:30]))
    return R.render('bifrost-skyndiuttekt', data, strict=False, lang=lang, hrefs=hrefs, pages=pages, primary=primary)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--data'); ap.add_argument('--example', action='store_true'); ap.add_argument('--out', required=True); ap.add_argument('--lang', choices=I.LANGS)
    a = ap.parse_args()
    src = os.path.join(R.tdir('bifrost-skyndiuttekt'), 'example.json') if a.example else a.data
    H = json.load(open(src, encoding='utf-8'))
    out = build(H, lang=a.lang)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, 'w', encoding='utf-8').write(out)
    print(f'miðstöð: {len(out)//1024} KB → {a.out}')


if __name__ == '__main__':
    main()
