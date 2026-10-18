#!/usr/bin/env python3
"""Smíðar sjálfvirknisíðuna (sjálfvistandi artifact).

Notkun:
  build.py --config config.json --out sjalfvirkni.html [--prefix prefix.txt]

config.json:
  {"company": "Félag ehf.", "initials": "FÉ", "hub_url": "https://claude.ai/artifact/…",
   "source_date": "17.10.2026", "companies": ["Félag ehf.", "Samstæða: …"],
   "find": {"afstemmingar": ["h", "texti"], …},       # niðurstöður síðustu greiningar (valkvætt)
   "sched": {"afstemmingar": {"on": true, "freq": "weekly", "wd": "1", "time": "07:00", "mode": "propose", "rc": "Bókari"}, …}}
--prefix: beinagrind síðunnar eins og birtingartólið vefur hana (allt fram að og með <body>,
  auk '\\n<meta charset="utf-8">\\n'). Fengið með því að birta einu sinni án hennar og lesa síðuna aftur.
  Án prefix virkar síðan en vistar ekki breytingar.
"""
import argparse, json, os
H = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(H, '..', 'assets')
T_ASSETS = os.path.join(H, '..', '..', 'bifrost-maelabord', 'assets')
DEFAULT = {
 'manadarlok': dict(freq='workday', md='3', time='08:00', mode='notify', rc='Bókari'),
 'afstemmingar': dict(freq='weekly', wd='1', time='07:00', mode='propose', rc='Bókari'),
 'faersluvakt': dict(freq='event', ev='Bókun í fjárhag', mode='notify', rc='Fjármálastjóri'),
 'innheimta': dict(freq='weekly', wd='1', time='08:00', mode='propose', rc='Fjármálastjóri'),
 'samthykkt': dict(freq='daily', time='08:00', mode='notify', rc='Bókari'),
 'reikningsfaersla': dict(freq='weekly', wd='5', time='09:00', mode='propose', rc='Bókari'),
 'sjodstada': dict(freq='weekly', wd='1', time='07:30', mode='notify', rc='Fjármálastjóri'),
 'bankabirgja': dict(freq='event', ev='Breyting á lánardrottni', mode='notify', rc='Fjármálastjóri'),
}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--config', required=True); ap.add_argument('--out', required=True); ap.add_argument('--prefix')
    a = ap.parse_args(); C = json.load(open(a.config, encoding='utf-8'))
    css = open(os.path.join(T_ASSETS, 'theme.css'), encoding='utf-8').read(); comp = open(os.path.join(T_ASSETS, 'components.js'), encoding='utf-8').read()
    extra = open(os.path.join(A, 'extra.css'), encoding='utf-8').read()
    body = open(os.path.join(A, 'body.html'), encoding='utf-8').read()
    esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;')
    opts = ''.join(f'<option>{esc(c)}</option>' for c in (C.get('companies') or [C['company']]))
    for k, v in {'{{HUB_URL}}': C.get('hub_url', '#'), '{{INITIALS}}': esc(C.get('initials', C['company'][:2])), '{{COMPANY}}': esc(C['company']),
                 '{{SOURCE_DATE}}': esc(C.get('source_date', '')), '{{COMPANY_OPTIONS}}': opts}.items():
        body = body.replace(k, v)
    if not C.get('hub_url'):
        body = body.replace('<nav class="crumb"', '<nav hidden class="crumb"', 1)
    app = open(os.path.join(A, 'app.js'), encoding='utf-8').read()
    T = f'''<title>Sjálfvirknivæðing</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&subset=latin,latin-ext&display=swap">
<script>(function(){{var m="light";try{{m=localStorage.getItem("bf-theme-v5")||"light"}}catch(e){{}}var r=document.documentElement;r.setAttribute("data-bf",m==="dark"?"dark":"light");r.setAttribute("data-pal",(m==="blue"||m==="earth")?m:"bifrost")}})()</script>
<style>
{css}
{extra}
</style>
{body}
<script>
{comp}
const PREFIX=%%PREFIX%%;
const TEMPLATE=%%TEMPLATE%%;
const STATE=%%STATE%%;
{app}
</script>
'''
    for t in ('%%PREFIX%%', '%%TEMPLATE%%', '%%STATE%%'):
        assert T.count(t) == 1, t
    sched = {}
    for k, v in (C.get('sched') or DEFAULT).items():
        sched[k] = dict(dict(on=True, freq='manual', time='07:00', mode='notify', sc=C['company'], rc='Fjármálastjóri'), **v)
    state = dict(company=C['company'], updated=None, queue=[], sched=sched, find=C.get('find', {}),
                 log=[dict(id=k, at=C.get('source_iso', ''), s=v[0], txt=v[1]) for k, v in C.get('find', {}).items() if C.get('source_iso')])
    j = lambda v: json.dumps(v, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    prefix = open(a.prefix, encoding='utf-8').read() if a.prefix else ''
    page = T.replace('%%PREFIX%%', j(prefix), 1).replace('%%STATE%%', j(state), 1).replace('%%TEMPLATE%%', j(T), 1)
    open(a.out, 'w', encoding='utf-8').write('<meta charset="utf-8">\n' + page)
    print(f'OK {a.out} ({len(page)//1024} kB). Vistun {"virk" if prefix else "óvirk (vantar --prefix)"}.')
if __name__ == '__main__':
    main()
