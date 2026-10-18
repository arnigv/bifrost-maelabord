---
name: endurskodun
description: Mælaborðið „Endurskoðun og ársreikningur“ fyrir Business Central — stærðarflokkun skv. lögum um ársreikninga nr. 3/2006, endurskoðunarskylda, skilafrestur til ársreikningaskrár, drög að rekstrar- og efnahagsreikningi og sjóðstreymi, undirbúningslisti fyrir endurskoðanda (PBC), færsluprófanir og mikilvægi, og gátlisti um skýringar. Notaðu þegar beðið er um ársreikning, ársuppgjör, endurskoðun, undirbúning fyrir endurskoðanda, lög um ársreikninga, stærðarflokk, skilafrest eða færsluprófanir.
---

# Endurskoðun og ársreikningur (lög nr. 3/2006)

**Valmælaborð** (ekki sjálfgefið í 1.0; bætt við úr miðstöð eða að beiðni, sérstaklega fyrir árslok).

Svarar: **Hvaða kröfur gilda um félagið, hvar stendur ársreikningurinn, er bókhaldið tilbúið fyrir endurskoðanda og hvað þarf að laga fyrst?**

Fylgdu `bifrost-maelabord` (útlit, grunnpalletta, `<meta charset="utf-8">`) og `bifrost-gogn` (gögn, efnahagur með `--bs`). Aðeins lesið úr BC.

> Fyrirvari á hverri síðu: *Ekki lögfræði- eða endurskoðunarráðgjöf. Endurskoðandi og stjórn bera ábyrgð á ársreikningnum. Staðfestu gildandi lagatexta á althingi.is.*

## 1. Lagagrunnur (`assets/thresholds.json`)

Uppfærðu skrána fyrir hverja keyrslu (leit á althingi.is og skatturinn.is) og merktu gildi „staðfest“ eða „óstaðfest“.

- **Stærðarflokkar, 2. gr. 11. tölul.:** örfélag, lítið, meðalstórt, stórt. Tvö af þremur viðmiðum (heildareignir, hrein velta, meðalfjöldi ársverka) á reikningsskiladegi. Flokkur breytist aðeins ef farið er yfir eða undir tvö ár í röð. Einingar tengdar almannahagsmunum eru alltaf stórar.
- **Sjóðstreymi, 28. gr.:** skylt fyrir meðalstór og stór félög.
- **Endurskoðun, 98. gr.:** undanþága ef félag fer ekki yfir tvö af þremur mörkum tvö ár í röð. Þá nægir skoðunarmaður.
- **Skil, 109. gr.:** rafrænt til ársreikningaskrár innan mánaðar frá samþykkt aðalfundar og eigi síðar en 8 mánuðum eftir lok reikningsárs. Sekt vegna vanskila og möguleg krafa um slit.
- **Frumvörp í vinnslu:** ef breytingar á mörkum eða frestum liggja fyrir Alþingi, sýndu það sem gula ábendingu efst.

Keyrðu:
```
python3 ${CLAUDE_SKILL_DIR}/scripts/classify_size.py --thresholds ${CLAUDE_SKILL_DIR}/assets/thresholds.json \
  --assets <heildareignir> --revenue <velta 12 mán.> --fte <ársverk> [--prev-assets … --prev-revenue … --prev-fte …] --year-end 2026-12-31 --out size.json
```
Ársverk: úr launakerfi eða forðum ef til. Annars spyrðu notandann eða merktu „vantar“ og flokkaðu á tveimur viðmiðum.

## 2. Gögn úr BC

- `dataset.json` (rekstur + efnahagur) úr `bifrost-gogn`, helst líka fyrra ár.
- **Fjárhagsfærslur** (`G/L Entry`) fyrir færsluprófanir: reitir 3 lykill, 4 bókunardagur, 5 tegund, 6 fylgiskjal, 7 lýsing, 17 fjárhæð, 27 notandi, 28 upprunakóði. Sæktu í hlutum (tekjulyklar, færslur ≥ framkvæmdamikilvægi, síðustu 2 mánuðir ársins og fyrsti mánuður næsta árs).
- **Undirbækur:** aldursgreining viðskiptamanna og lánardrottna (`aging`), bankareikningar og afstemmingar (`Bank Acc. Reconciliation`, `Bank Account Ledger Entry`), fastafjármunir (`Fixed Asset`, `FA Ledger Entry`), birgðir (`Item Ledger Entry`), VSK-uppgjör.
- **Tengdir aðilar:** viðskiptamenn og lánardrottnar merktir sem tengdir, millifélagslyklar.

Breyttu í JSON-lista og keyrðu:
```
python3 ${CLAUDE_SKILL_DIR}/scripts/je_tests.py --entries gl.json --materiality <M> --year-end 2026-12-31 --revenue-accounts 1110,1120 --out je.json
```

## 3. Mikilvægi

Reiknaðu bil úr `thresholds.json` (0,5–1% tekna, 5–10% hagnaðar fyrir skatta, 1–2% eigna). Veldu eina tölu og rökstyddu. Framkvæmdamikilvægi 75%, smávægilegt 5%. Merkt **tillaga, endurskoðandi ákveður**.

## 4. Flipar

**Yfirsýn**
- Hero: stærðarflokkur (stórt letur) og dagar til skilafrests.
- Fjögur kort: endurskoðun (skyld/undanþegin), sjóðstreymi (skylt/ekki), skilafrestur og sekt, tilbúið fyrir endurskoðun (% af PBC-lista lokið).
- Graf: félagið á móti mörkum (þrjár láréttar stikur, eignir/velta/ársverk, með lóðréttum línum við mörk lítils og meðalstórs félags).
- „Fyrst að laga“: 3–5 brýnustu atriðin úr flipunum hér að neðan.

**Ársreikningur (drög)**
- Rekstrarreikningur og efnahagsreikningur á uppsetningu laganna (fyrra ár til samanburðar ef til).
- Sjóðstreymi (óbein aðferð) ef skylt.
- Kennitölur: veltufjárhlutfall, eiginfjárhlutfall, arðsemi eigin fjár, innheimtutími.
- Merkt **drög, óendurskoðað**. Ef jöfnuður efnahags næst ekki án afgangsstærðar: sýna mismuninn sem ábendingu.

**Undirbúningur endurskoðunar (PBC)**
Gátlisti með stöðu (*lokið / í vinnslu / vantar*) og sönnunargögnum úr BC:
- Bankaafstemmingar allra reikninga á reikningsskiladegi.
- Viðskiptamenn: undirbók = fjárhagur, aldursgreining, niðurfærsla vafasamra krafna.
- Lánardrottnar: undirbók = fjárhagur, ógreiddir og ósamþykktir reikningar.
- Skurður (cut-off): sala og innkaup síðustu og fyrstu daga tímabils.
- Birgðir: talning, verðmat.
- Fastafjármunir: hreyfingar, afskriftir bókaðar alla mánuði.
- VSK: útskattur á móti tekjum, uppgjörsreikningur stemmir við skýrslur.
- Laun: launakostnaður á móti staðgreiðslu, tryggingagjaldi og lífeyri.
- Eigið fé: arðgreiðslur samþykktar á aðalfundi, hagnaður fyrra árs færður.
- Tengdir aðilar: skrá og fjárhæðir.
- Atburðir eftir reikningsskiladag og óvissar skuldbindingar.

**Færsluprófanir**
- Mikilvægi (heild, framkvæmda, smávægilegt).
- Niðurstöður `je_tests.py` sem kort með alvarleika: handfærðar tekjur, sléttar fjárhæðir, helgarfærslur, færslur yfir mikilvægi, seinar færslur, sjaldgæfir notendur, ójöfnuður innan fylgiskjala.
- Tafla með dæmum (fylgiskjal, dagsetning, lykill, fjárhæð, ástæða). Notendur sýndir sem hlutverk eða kóði, ekki nöfn.
- Orðalag: „ábending til skoðunar“, aldrei „misferli“.

**Skýringar**
- Gátlisti um upplýsingagjöf eftir stærðarflokki (reikningsskilaaðferðir, fastafjármunir, skuldir eftir gjalddaga, tengdir aðilar, meðalfjöldi starfa, laun stjórnenda, þóknun endurskoðanda, atburðir eftir uppgjörsdag, áframhaldandi rekstrarhæfi) og hvort gögn fyrir hverja eru til í BC.
- Skýrsla stjórnar: lykilatriði sem þarf að fjalla um.

## 5. Sannreyning

- Drög stemma við `dataset.json`; efnahagur jafnast.
- Stærðarflokkur endurreiknaður með handreikningi á tveimur af þremur viðmiðum.
- Hver lagavísun með grein og hlekk á althingi.is; óstaðfest gildi merkt.
- Persónuupplýsingar: engin nöfn notenda eða samþykkjenda, aðeins hlutverk.
- Fótur: heimildir, fyrirvari, og „Unnið með aðstoð gervigreindar (Claude). Yfirfarið áður en byggt er á tölunum.“

## Samstæða

- Stærðarflokkun samstæðu notar sömu mörk á samanteknum tölum (2. gr. og kafli laganna um samstæðureikningsskil; staðfestu greinanúmer á althingi.is); samstæðureikningsskil eru skyld nema undanþága eigi við. Sýndu bæði flokk samstæðu og hvers félags.
- Undirbúningslisti á hvert félag, auk samstæðuatriða: innbyrðis staða stemmir, jöfnunarfærslur skjalfestar, hlutdeild minnihluta, samræmdar reikningsskilaaðferðir.
- Færsluprófanir á hvert félag; innbyrðis færslur yfir mikilvægi eru sérstakt próf.
- Skilafrestur og stærð á hvert félag (hvert félag skilar eigin ársreikningi).
