---
name: kostnadur
description: "Mælaborðið „Kostnaður“ í Bifröst-mælaborðum (Samþykkt reikninga, Birgjar og kostnaðarliðir), smíðað úr föstu sniðmáti. Notaðu AÐEINS innan Bifröst-mælaborða: þegar notandinn biður um Bifröst-mælaborð eða þetta mælaborð með nafni, eða breytir mælaborði sem pluginið bjó til. Ekki fyrir almennar spurningar um rekstur eða Business Central, aðrar skýrslur, skjöl eða artifacts."
---

# Kostnaður og innkaup

> **Fast sniðmát.** Þetta mælaborð er smíðað úr `template/` (sjá `bifrost-maelabord`, *Föst sniðmát*). Skrifaðu ekki HTML. Safnaðu gögnunum eftir `template/schema.md` (sýnidæmi: `template/example.json`), og smíðaðu með `render.py --dashboard kostnadur` eða `bundle.py`. Við breytingu eða uppfærslu er **aðeins þetta mælaborð** endurgert og birt (og viðbætur þess í `ext/`), sjá *Umfang breytinga*. Lýsingin hér að neðan segir hvað sniðmátið sýnir og hvaðan gögnin koma.

Svarar: **Hvað bíður samþykktar og hjá hverjum, í hvað fara peningarnir, og hvar getum við sparað?**

Fylgdu `bifrost-maelabord` og `bifrost-gogn`. **Aðeins lesið** — þetta skill samþykkir aldrei reikninga. Ef notandi vill samþykkja, vísaðu á BC eða sérstaka aðgerð með staðfestingu.

## 1. Gögn

**Gögn: samtölur fyrst** (`bifrost-gogn`, kafli 0). Upphæðir á viðskiptavin, birgi, lykil, verk og vöru koma sem samtölur úr BC (`Data.Totals.Get`, `period_breakdown`, `aging`); færslur eru aðeins sóttar fyrir drill-down á stærstu liðina og athuganir sem þurfa færsluna sjálfa.

**Samþykkt reikninga**
- `Approval Entry` (fields 1–5, 8–10, 15–17: tafla, tegund, skjal nr., röð, samþykktarkóði, samþykkjandi, staða, sent dags., upphæð, upphæð ISK, gjaldmiðill). Opnar = staða *Opið* (eða *Búið til* ef röð er í gangi).
- `Purchase Header` með `Status = Pending Approval` (*Bíður samþykkis*): lánardrottinn, gjalddagi, skjaldagur. Tengdu við `Approval Entry` á skjalanúmeri.
- Sami reikningur getur átt fleiri en eina færslu (hætt við og sent aftur). Notaðu nýjustu opnu færsluna á hvert skjal.
- `Incoming Document` sem ekki er orðið að reikningi (staða *Nýtt*): fylgiskjöl sem bíða skráningar.
- Ef engar samþykktarfærslur eru til: segðu að samþykktarferli sé ekki virkt í BC og sýndu í staðinn óbókaða innkaupareikninga.

**Birgjar**
- Innkaup síðustu 12 mánuði á birgja: Innkaup (SGM), reitur 62 á `Vendor` með `Date Filter` (FlowField, eitt kall með heitum); varaleið `Data.Totals.Get` á `Vendor Ledger Entry` (`[18]` Purchase (LCY), formerki í mínus, `groupBy` `Vendor No.`). Berðu summuna saman við kostnaðarlyklana: innkaup í erlendri mynt eða úr almennri dagbók geta verið 0 í Purchase (LCY).
- Opnar skuldir með `aging` (entity `vendor`).
- Ef innkaup eru bókuð beint í fjárhag (ekki á birgja): segðu það og notaðu kostnaðarlykla í staðinn.

**Kostnaðarliðir**
- `dataset.json`: kostnaðarlyklar á mánuði (vörunotkun, laun, húsnæði, annar rekstur), sama tímabil í fyrra. Kostnaður á lykil fyrir annað tímabil: Hreyfing (reitur 32) á `G/L Account` með `Date Filter` (`bifrost-gogn`, kafli 0); varaleið `Data.Totals.Get` á `G/L Entry`.

## 2. Flipar (tveir)

**Samþykkt reikninga**
- Lykilmælar (hámark fjórir): fjöldi og upphæð í bið, þar af komið á gjalddaga, meðalbiðtími.
- Eftir samþykkjanda (hlutverk), tímalína gjalddaga og tafla með síu og leit. Smellt á birgi opnar alla reikninga hans.

**Birgjar og kostnaðarliðir**
- Stærstu kostnaðarliðir og birgjar, liðir sem vaxa hraðar en tekjur.
- **Drill-down:** kostnaðarflokkur → bókhaldslyklar → **færslur** (dagsetning, fylgiskjal, lýsing, birgir, fjárhæð) með leit og röðun; birgir → reikningar hans og lyklar. Færslur úr `G/L Entry` (reitir 3, 4, 6, 7, 17, 58) og `Vendor Ledger Entry` **sama drill-down og áður** (sjá `bifrost-gogn`, kafli 0: allar færslur ef þær eru ≤ 5.000 á tímabilinu, annars færslur stærstu liðanna). Sótt með síu á tímabil og kostnaðarlykla, ekki öll taflan.
- **Sparnaður** er eitt kort neðst (fjöldi tækifæra og áætluð áhrif á ári, merkt *mat*), ekki sér flipi. Reglurnar um tækifæri: innkaupasamningar 2–3%, flutningur ~10%, orka ~10%, bílar, staðgreiðsluafslættir, tvíteknar áskriftir.

## 3. Persónuupplýsingar

Samþykkjandi er notandi í BC. Á mælaborði innan fyrirtækisins má sýna notandakenni. Ef mælaborð á að fara víðar: sýndu hlutverk eða kóða (t.d. *Samþykkjandi 1*). Kortareikningar og útlagður kostnaður starfsmanna: sýndu kóða, ekki nafn.

## 4. Sannreyning

- Upphæð í bið stemmir við summu opinna samþykktarfærslna (án tvítalningar).
- Kostnaðarliðir stemma við `dataset.json`.
- Sparnaður er alltaf merktur sem mat.

## Samstæða (nánar)

- Félagsval efst. Innbyrðis reikningar (lánardrottinn er félag í samstæðu) eru sýndir sér í samþykktarflipanum og ekki taldir með stærstu birgjum eða sparnaði samstæðu.
