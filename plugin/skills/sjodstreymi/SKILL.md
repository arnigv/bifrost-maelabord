---
name: sjodstreymi
description: Sjóðstreymi og bankar úr Business Central (3 flipar) — staða hvers bankareiknings og greiðslukorts í dag, 13 vikna sjóðspá með lægstu stöðu, útgreiðslum og reikningum í samþykkt, stikum og sviðsmyndum, og innheimta. Afstemmingar eru í Mánaðarlokum. Notaðu þegar beðið er um sjóðstreymi, sjóðspá, stöðu í bönkum, lausafé, greiðslugetu, innheimtu eða „eigum við fyrir launum“.
---

# Sjóðstreymi

Svarar: **Hvað eigum við í peningum næstu 13 vikur, hvar er lágpunkturinn og hvað getum við gert?**

Fylgdu `bifrost-maelabord` og `bifrost-gogn`. Aðeins lesið.

## 1. Gögn

- **Upphafsstaða:** staða bankareikninga í dag (`Bank Account` + `Bank Account Ledger Entry`, eða handbært fé úr efnahag í `dataset.json` ef engir bankareikningar eru í BC).
- **Innborganir:** opnar færslur í `Cust. Ledger Entry` með gjalddaga og eftirstöðvum. `aging` fyrir viðskiptamenn.
- **Útgreiðslur:** opnar færslur í `Vendor Ledger Entry` með gjalddaga og eftirstöðvum. `aging` fyrir lánardrottna.
- **Reikningar í samþykkt:** innkaupareikningar sem bíða samþykkis (sjá `kostnadur`) eru ekki enn í lánardrottnabók en eru væntanlegar greiðslur á gjalddaga. Taktu þá með í spánni sem sér lið.
- **Laun og fast:** meðaltal síðustu þriggja fullbókaðra mánaða af launum, launatengdum gjöldum (staðgreiðsla, lífeyrir, tryggingargjald), húsaleigu og afborgunum lána úr `dataset.json`. Laun greidd síðasta virka dag mánaðar, launatengd gjöld 15. næsta mánaðar.
- **VSK:** ef VSK-lyklar eru í efnahag, áætla greiðslu á gjalddögum (5. næsta mánaðar eftir tveggja mánaða tímabil).
- **Söguleg greiðsluhegðun:** meðaltöf viðskiptavina frá gjalddaga til greiðslu, úr lokuðum færslum síðustu 6 mánuði.

## 2. Spáin

- Vikur mánudag til sunnudags, 13 vikur fram.
- Innborganir dreifast eftir gjalddaga + sögulegri töf hvers viðskiptavinar. Gjaldfallnar kröfur: líkur á innheimtu eftir aldri (0–30 d.: 90%, 31–60: 70%, 61–90: 50%, > 90: 25%), stillanlegt.
- Nýjar tekjur: meðalsala á viku úr `dataset.json` × innheimtuhlutfall, frá og með þeim degi sem nýir reikningar falla á gjalddaga.
- Segðu skýrt hvaða forsendur eru notaðar.

## 3. Flipar (þrír)

**Staða í bönkum**
- Hver bankareikningur og greiðslukort með stöðu í dag (`Bank Account` reitir 1, 2, 22, 41, 58), síðasta yfirlit og hvort bankar stemma við bankalykla. Sjóðstaða í lok mánaðar. Korthafar sem „Greiðslukort 1, 2…“.

**13 vikna spá**
- Lína: sjóðstaða viku fyrir viku (vika byrjar á mánudegi) með lágpunkti og rauðu svæði undir lágmarksstöðu.
- Stikur: greiðsluhraði viðskiptavina, innheimtuhlutfall gjaldfallinna krafna, frestun greiðslna, lágmarksstaða. Sviðsmyndir: *Grunnur · Hæg innheimta · Átak í innheimtu*.
- **Útgreiðslur** (áður sér flipi) eru hér: skuldir eftir gjalddaga og reikningar sem bíða samþykkis, með rofa og töflu yfir í hvaða viku hver greiðist.

**Innheimta**
- Aldursgreining og stærstu skuldarar með upphæð, aldri og töf; áhrif á sjóð ef stærstu greiða í næstu viku.

Afstemmingar eru **ekki** hér heldur í `manadarlok`; vísaðu þangað með tengli (`data-nav`).

## 4. Sannreyning

- Upphafsstaða stemmir við bankalykla í fjárhag.
- Opnar kröfur og skuldir stemma við `aging`-samtölur.
- Spá er alltaf merkt sem spá, með forsendum neðst.

## Staða í bönkum (nánar)

Spjald **„Staða í bönkum“** undir lykilmælum: hver bankareikningur og greiðslukort með stöðu í dag (`Bank Account` reitir 1, 2, 22, 41, 58), dagsetningu og númeri síðasta afstemmda yfirlits og óafstemmdri fjárhæð þá. Fjórir smámælar: bankainnstæður, greiðslukort, nettó, og hvort bankar stemma við bankalykla í fjárhag. Korthafar og nöfn á reikningum birtast sem „Fyrirtækjakort 1, 2…“, aldrei nöfn einstaklinga.

## Samstæða

- Félagsval efst (`entityPicker`): *Samstæða · Félag 1 · Félag 2…*. Spá, bankar og afstemmingar fylgja valinu.
- **Bankar:** dálkur *Félag* í töflunni og samtala á félag. Í samstæðu er handbært fé summa félaganna; innbyrðis lán og millifærslur milli félaga eru dregnar út úr inn- og útgreiðslum spárinnar (úr `eliminations.json`, tegund `fjarmagn`/`stada`).
- **Innheimta og greiðslur:** innbyrðis kröfur og skuldir (viðskiptamenn/lánardrottnar sem eru félög í samstæðunni) eru sýndar sér og ekki taldar sem ytri innheimta.
- **Afstemmingar:** á hvert félag fyrir sig, auk línu *Innbyrðis staða stemmir* (krafa félags A á B = skuld B við A).
- Lágpunktur er reiknaður bæði fyrir samstæðu og hvert félag; félag undir lágmarki er dregið fram þótt samstæðan sé í lagi.
