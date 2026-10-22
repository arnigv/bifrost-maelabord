#!/usr/bin/env python3
"""Textaeiningar í sniðmáti: dregur út hráa búta (HTML-texta, eigindi, JS-strengi, heila sniðstrengi) sem innihalda íslensku.
Notað til að smíða orðabækur (template/i18n/<lang>.json) og í leifaprófun."""
import re, json, sys
IS_CH = re.compile(r'[áéíóúýþæöðÁÉÍÓÚÝÞÆÖÐ]')
IS_W = set('''og eða er eru á í af til frá með við um fyrir eftir án ekki sem var hefur
tekjur laun verk sala samtals raun spá áætlun lykill liður flokkur staða mánuður ár
dagar dagur viðskiptavinur viðskiptavinir birgir birgjar reikningur reikningar opið opna loka
yfirsýn rekstur kostnaður framlegð vörur vara sjóður banki bankar innheimta tími tímar nýtt
grunnur sviðsmynd stikur forsendur heildar alls hlutfall breyting fyrra næsta síðasta
eignir skuldir hagnaður tap greitt ógreitt gjaldfallið samþykkt samþykkja bíður
'''.split())
TEST = None  # sett tímabundið til að draga út alla strengi (prófun)

def is_text(t):
    if TEST is not None:
        return TEST(t)
    t2 = t.strip()
    if not t2 or not re.search(r'[A-Za-zÀ-ÿ]', t2): return False
    if IS_CH.search(t2): return True
    ws = re.findall(r'[A-Za-zÀ-ÿ]+', t2.lower())
    return any(w in IS_W for w in ws) and not re.fullmatch(r'[a-z_]+', t2)  # sleppa gagnalyklum eins og 'tekjur'

def lit_end(js, i):
    """js[i]=='`' -> vísir á lokandi `"""
    j = i + 1; n = len(js)
    while j < n:
        c = js[j]
        if c == '\\': j += 2; continue
        if c == '`': return j
        if js.startswith('${', j):
            k = j + 2; d = 1
            while k < n and d:
                ch = js[k]
                if ch in "'\"":
                    m = k + 1
                    while m < n and js[m] != ch: m += 2 if js[m] == '\\' else 1
                    k = m + 1; continue
                if ch == '`': k = lit_end(js, k) + 1; continue
                if ch == '{': d += 1
                elif ch == '}': d -= 1
                k += 1
            j = k; continue
        j += 1
    return n

def exprs(s):
    """Innihald allra ${...} í sniðstreng (efsta stig)."""
    out, i = [], 0
    while i < len(s):
        if s.startswith('${', i):
            k = i + 2; d = 1
            while k < len(s) and d:
                ch = s[k]
                if ch in "'\"":
                    m = k + 1
                    while m < len(s) and s[m] != ch: m += 2 if s[m] == '\\' else 1
                    k = m + 1; continue
                if ch == '`': k = lit_end(s, k) + 1; continue
                if ch == '{': d += 1
                elif ch == '}': d -= 1
                k += 1
            out.append(s[i + 2:k - 1]); i = k; continue
        i += 1
    return out


def strip_expr(s):
    out, i, d = '', 0, 0
    while i < len(s):
        if s.startswith('${', i):
            d = 1; i += 2
            while i < len(s) and d:
                if s[i] == '{': d += 1
                elif s[i] == '}': d -= 1
                i += 1
            out += ' '; continue
        out += s[i]; i += 1
    return out

def visible(s):
    t = re.sub(r'<[^>]*>', ' ', strip_expr(s))
    return t

def js_units(js, acc):
    i, n = 0, len(js)
    while i < n:
        c = js[i]
        if js.startswith('/*', i):
            j = js.find('*/', i + 2); i = n if j < 0 else j + 2; continue
        if js.startswith('//', i) and (i == 0 or js[i-1] in ' \n\t;{}(),'):
            j = js.find('\n', i); i = n if j < 0 else j; continue
        if c in "'\"":
            j = i + 1
            while j < n and js[j] != c and js[j] != '\n': j += 2 if js[j] == '\\' else 1
            body = js[i+1:j]
            if is_text(visible(body)): acc.append(body)
            i = j + 1; continue
        if c == '`':
            j = lit_end(js, i); body = js[i+1:j]
            if IS_CH.search(visible(body)) or is_text(visible(body)): acc.append(body)
            for ex in exprs(body):  # strengir inni í ${...}
                js_units(ex, acc)
            for am in re.finditer(r'(?:title|aria-label|placeholder)="([^"]*)"', body):  # eigindi í HTML inni í streng
                if IS_CH.search(strip_expr(am.group(1))) or is_text(strip_expr(am.group(1))): acc.append(am.group(1))
            i = j + 1; continue
        i += 1

def html_units(h, acc):
    h = re.sub(r'<style.*?</style>', '', h, flags=re.S)
    h = re.sub(r'<!--.*?-->', '', h, flags=re.S)
    for m in re.finditer(r'<title>([^<]+)</title>', h):  # titill síðu alltaf
        acc.append(m.group(1))
    for m in re.finditer(r'>([^<>]+)<', h):
        if is_text(re.sub(r'\{\{.*?\}\}', '', m.group(1))): acc.append(m.group(1))
    for m in re.finditer(r'(title|aria-label|placeholder|alt|data-short|data-prompt|data-q)="([^"]*)"', h):
        if is_text(re.sub(r'\{\{.*?\}\}', '', m.group(2))): acc.append(m.group(2))

def units(src, kind='html'):
    acc = []
    if kind == 'js':
        js_units(src, acc)
    else:
        pos = 0
        for m in re.finditer(r'<script[^>]*>(.*?)</script>', src, re.S):
            html_units(src[pos:m.start()], acc)
            js_units(m.group(1).replace('{{COMPONENTS_JS}}', ''), acc)
            pos = m.end()
        html_units(src[pos:], acc)
    seen, res = set(), []
    for u in acc:
        if u.strip() and u not in seen: seen.add(u); res.append(u)
    return res

if __name__ == '__main__':  # units.py skrá [skrá2 ...] > units.json
    allu = []
    for f in sys.argv[1:]:
        s = open(f, encoding='utf-8').read()
        allu += units(s, 'js' if f.endswith('.js') else 'html')
    json.dump(allu, sys.stdout, ensure_ascii=False, indent=0)
