---
name: sjodstreymi
description: "Mælaborðið „Sjóðstreymi og bankar“ í Bifröst-mælaborðum (Staða í bönkum, 13 vikna spá, Innheimta), smíðað úr föstu sniðmáti. Notaðu AÐEINS innan Bifröst-mælaborða: þegar notandinn biður um Bifröst-mælaborð eða þetta mælaborð með nafni, eða breytir mælaborði sem pluginið bjó til. Ekki fyrir almennar spurningar um rekstur eða Business Central, aðrar skýrslur, skjöl eða artifacts."
---

# Sjóðstreymi

> **Fast sniðmát.** Þetta mælaborð er smíðað úr `template/` (sjá `bifrost-maelabord`, *Föst sniðmát*). Skrifaðu ekki HTML. Safnaðu gögnunum eftir `template/schema.md` (sýnidæmi: `template/example.json`), og smíðaðu með `render.py --dashboard sjodstreymi` eða `bundle.py`. Við breytingu eða uppfærslu er **aðeins þetta mælaborð** endurgert og birt (og viðbætur þess í `ext/`), sjá *Umfang breytinga*. Lýsingin hér að neðan segir hvað sniðmátið sýnir og hvaðan gögnin koma.

Svarar: **Hvað eigum við í peningum næstu 13 vikur, hvar er lágpunkturinn og hvað getum við gert?**

Fylgdu `bifrost-maelabord` og `bifrost-gogn`. Aðeins lesið.

## 1. Gögn

- **Upphafsstaða:** staða bankareikninga í dag (`Bank Account` + `Bank Account Ledger Entry`, eða handbært fé úr efnahag í `dataset.json` ef engir bankareikningar eru í BC).
- **Innborganir:** opnar færslur í `Cust. Ledger Entry` með gjalddaga og eftirstöðvum (færslur þarf hér, því spáin raðar á gjalddaga; aðeins `Open=CONST(true)` og reitir sem þarf). `aging` fyrir viðskiptamenn og sem stemming.
- **Söguleg innheimta og greiðsluhraði:** samtölur á mánuð (`Data.Totals.Get`), ekki allar greiddar færslur.
- **Útgreiðslur:** opnar færslur í `Vendor Ledger Entry` með gjalddaga og eftirstöðvum. `aging` fyrir lánardrottna.
- **Reikningar í samþykkt:** innkaupareikningar sem bíða samþykkis (sjá `kostnadur`) eru ekki enn í lánardrottnabók en eru væntanlegar greiðslur á gjalddaga. Taktu þá með í spánni sem sér lið.
- **Laun og fast:** meðaltal síðustu þriggja fullbókaðra mánaða af launum, launatengdum gjöldum (staðgreiðsla, lífeyrir, tryggingargjald), húsaleigu og afborgunum lána úr `dataset.json`. Laun greidd síðasta virka dag mánaðar, launatengd gjöld 15. næsta mánaðar.
- **VSK:** ef VSK-lyklar eru í efnahag, áætla greiðslu á gjalddögum (5. næsta mánaðar eftir tveggja mánaða tímabil).
- **Kortauppgjör (verslun, veitingar, þjónusta með posa):** bankareikningar eða fjárhagslyklar fyrir uppgjör færsluhirða (heiti eins og „Kreditkort“, „Debetkort“, „Kortauppgjör“, „Valitor“, „Rapyd“, „Teya“, „Borgun“, „SaltPay“, „Adyen“) með **debetstöðu** eru krafa á færsluhirði, ekki fyrirtækjakort. Skráðu þá í `banks[]` með `teg: "Kortauppgjör"` (eða `kind: "acquirer"`) og `lag_days` (dagar frá sölu til innborgunar, úr bankafærslum; sjálfgefið 2). Staðan fyrst úr samtölum (`Bank Account`, Balance at Date / `period_breakdown` á lyklinum). Fyrirtækjakort eru með **kreditstöðu** (skuld) og fá `teg: "Greiðslukort"`. Kortauppgjör fer ekki í `cash` né `banks_gl.bankar`/`kort`; gefðu `banks_gl.uppgjor` ef það á sér fjárhagslykil.
- **Staðgreiðsluviðskiptamenn:** viðskiptamenn sem halda utan um kassa- eða posasölu (t.d. „Staðgreiðsla <verslun>“, „Kassi“, „POS“, „Ýmsir viðskiptamenn“) fá `pos: true` í `custs[]`. Þeir eru ekki taldir stærstu skuldarar.
- **Aðgerðir í „Fyrst að gera“:** `js.act2_*` og `js.act3_*` eru skrifaðar út frá gögnunum (ekki afrita DT-textann). Ef ekkert réttlætir aðgerð (allt fullbókað, engar gjaldfallnar skuldir), settu titilinn `""`.
- **Lágmarksstaða:** `min_m` (m.kr.), u.þ.b. hálfs mánaðar útgreiðslur; vanti = 30.
- **Söguleg greiðsluhegðun:** meðaltöf viðskiptavina frá gjalddaga til greiðslu, úr lokuðum færslum síðustu 6 mánuði.

## 2. Spáin

- Vikur mánudag til sunnudags, 13 vikur fram.
- Innborganir dreifast eftir gjalddaga + sögulegri töf hvers viðskiptavinar. Gjaldfallnar kröfur: líkur á innheimtu eftir aldri (0–30 d.: 90%, 31–60: 70%, 61–90: 50%, > 90: 25%), stillanlegt.
- Nýjar tekjur: meðalsala á viku úr `dataset.json` × innheimtuhlutfall, frá og með þeim degi sem nýir reikningar falla á gjalddaga.
- Segðu skýrt hvaða forsendur eru notaðar.

## 3. Flipar (þrír)

**Staða í bönkum**
- Hver bankareikningur og greiðslukort með stöðu í dag (`Bank Account` reitir 1, 2, 22, 41, 58), síðasta yfirlit og hvort bankar stemma við bankalykla. Sjóðstaða í lok mánaðar. Korthafar sem „Greiðslukort 1, 2…“. Kortauppgjör (krafa á færsluhirði) er sér lína „Kortauppgjör á leiðinni“, utan handbærs fjár.

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
