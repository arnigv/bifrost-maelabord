---
name: kostnadur
description: Kostnaðar- og innkaupamælaborð úr Business Central (2 flipar) — samþykkt reikninga (allir ósamþykktir innkaupareikningar, hver á eftir að samþykkja, gjalddagar) og birgjar og kostnaðarliðir með drill-down frá flokki í lykla og niður í einstakar færslur, og sparnaðarmat. Notaðu þegar beðið er um samþykkt reikninga, „hver á eftir að samþykkja“, birgja, innkaup, kostnað, kostnaðargreiningu, færslur á kostnaðarlykli eða sparnað.
---

# Kostnaður og innkaup

Svarar: **Hvað bíður samþykktar og hjá hverjum, í hvað fara peningarnir, og hvar getum við sparað?**

Fylgdu `bifrost-maelabord` og `bifrost-gogn`. **Aðeins lesið** — þetta skill samþykkir aldrei reikninga. Ef notandi vill samþykkja, vísaðu á BC eða sérstaka aðgerð með staðfestingu.

## 1. Gögn

**Samþykkt reikninga**
- `Approval Entry` (fields 1–5, 8–10, 15–17: tafla, tegund, skjal nr., röð, samþykktarkóði, samþykkjandi, staða, sent dags., upphæð, upphæð ISK, gjaldmiðill). Opnar = staða *Opið* (eða *Búið til* ef röð er í gangi).
- `Purchase Header` með `Status = Pending Approval` (*Bíður samþykkis*): lánardrottinn, gjalddagi, skjaldagur. Tengdu við `Approval Entry` á skjalanúmeri.
- Sami reikningur getur átt fleiri en eina færslu (hætt við og sent aftur). Notaðu nýjustu opnu færsluna á hvert skjal.
- `Incoming Document` sem ekki er orðið að reikningi (staða *Nýtt*): fylgiskjöl sem bíða skráningar.
- Ef engar samþykktarfærslur eru til: segðu að samþykktarferli sé ekki virkt í BC og sýndu í staðinn óbókaða innkaupareikninga.

**Birgjar**
- Innkaup síðustu 12 mánuði á birgja úr `Vendor Ledger Entry` (reikningar, upphæð í ISK) eða `Purch. Inv. Header`/`Value Entry` ef til.
- Opnar skuldir með `aging` (entity `vendor`).
- Ef innkaup eru bókuð beint í fjárhag (ekki á birgja): segðu það og notaðu kostnaðarlykla í staðinn.

**Kostnaðarliðir**
- `dataset.json`: kostnaðarlyklar á mánuði (vörunotkun, laun, húsnæði, annar rekstur), sama tímabil í fyrra.

## 2. Flipar (tveir)

**Samþykkt reikninga**
- Lykilmælar (hámark fjórir): fjöldi og upphæð í bið, þar af komið á gjalddaga, meðalbiðtími.
- Eftir samþykkjanda (hlutverk), tímalína gjalddaga og tafla með síu og leit. Smellt á birgi opnar alla reikninga hans.

**Birgjar og kostnaðarliðir**
- Stærstu kostnaðarliðir og birgjar, liðir sem vaxa hraðar en tekjur.
- **Drill-down:** kostnaðarflokkur → bókhaldslyklar → **færslur** (dagsetning, fylgiskjal, lýsing, birgir, fjárhæð) með leit og röðun; birgir → reikningar hans og lyklar. Færslur úr `G/L Entry` (reitir 3, 4, 6, 7, 17, 58) og `Vendor Ledger Entry`; ef margar, efstu 50 á lykil og „aðrar færslur“.
- **Sparnaður** er eitt kort neðst (fjöldi tækifæra og áætluð áhrif á ári, merkt *mat*), ekki sér flipi. Reglurnar um tækifæri: innkaupasamningar 2–3%, flutningur ~10%, orka ~10%, bílar, staðgreiðsluafslættir, tvíteknar áskriftir.

## 3. Persónuupplýsingar

Samþykkjandi er notandi í BC. Á mælaborði innan fyrirtækisins má sýna notandakenni. Ef mælaborð á að fara víðar: sýndu hlutverk eða kóða (t.d. *Samþykkjandi 1*). Kortareikningar og útlagður kostnaður starfsmanna: sýndu kóða, ekki nafn.

## 4. Sannreyning

- Upphæð í bið stemmir við summu opinna samþykktarfærslna (án tvítalningar).
- Kostnaðarliðir stemma við `dataset.json`.
- Sparnaður er alltaf merktur sem mat.

## Samstæða (nánar)

- Félagsval efst. Innbyrðis reikningar (lánardrottinn er félag í samstæðu) eru sýndir sér í samþykktarflipanum og ekki taldir með stærstu birgjum eða sparnaði samstæðu.
