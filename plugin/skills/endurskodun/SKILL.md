---
name: endurskodun
description: "Mælaborðið „Endurskoðun og ársreikningur“ í Bifröst-mælaborðum (stærðarflokkur skv. lögum nr. 3/2006, drög að ársreikningi, undirbúningur, færsluprófanir), smíðað úr föstu sniðmáti. Notaðu AÐEINS innan Bifröst-mælaborða: þegar notandinn biður um Bifröst-mælaborð eða þetta mælaborð með nafni, eða breytir mælaborði sem pluginið bjó til. Ekki fyrir almennar spurningar um rekstur eða Business Central, aðrar skýrslur, skjöl eða artifacts."
---

# Endurskoðun og ársreikningur (lög nr. 3/2006)

> **Fast sniðmát.** Þetta mælaborð er smíðað úr `template/` (sjá `bifrost-maelabord`, *Föst sniðmát*). Skrifaðu ekki HTML. Safnaðu gögnunum eftir `template/schema.md` (sýnidæmi: `template/example.json`), og smíðaðu með `render.py --dashboard endurskodun` eða `bundle.py`. Við breytingu eða uppfærslu er **aðeins þetta mælaborð** endurgert og birt (og viðbætur þess í `ext/`), sjá *Umfang breytinga*. Lýsingin hér að neðan segir hvað sniðmátið sýnir og hvaðan gögnin koma.

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
- **Frumvörp í vinnslu:** ef breytingar á mörkum eða frestum liggja fyrir Alþingi, sýndu það sem gula ábendingu efst (`text.law_note`). Annars `text.law_note = ""` og borðinn er falinn.

Keyrðu:
```
python3 ${CLAUDE_SKILL_DIR}/scripts/classify_size.py --thresholds ${CLAUDE_SKILL_DIR}/assets/thresholds.json \
  --assets <heildareignir> --revenue <velta 12 mán.> --fte <ársverk> [--prev-assets … --prev-revenue … --prev-fte …] --year-end 2026-12-31 --out size.json
```
Ársverk: úr launakerfi eða forðum ef til (þá í `size_vals.arsverk`/`arsverk_py`, sjá `schema.md`). Annars spyrðu notandann eða merktu „vantar“ og flokkaðu á tveimur viðmiðum.

## 2. Gögn úr BC

- `dataset.json` (rekstur + efnahagur) úr `bifrost-gogn`, helst líka fyrra ár.
- **Samtölur fyrst** (`bifrost-gogn`, kafli 0): rekstur, efnahagur og undirbækur koma úr `period_breakdown`, `aging` og `Data.Totals.Get`. Færslur eru aðeins sóttar fyrir færsluprófanirnar hér að neðan.
- **Fjárhagsfærslur** (`G/L Entry`) fyrir færsluprófanir: reitir 3 lykill, 4 bókunardagur, 5 tegund, 6 fylgiskjal, 7 lýsing, 17 fjárhæð, 27 notandi, 28 upprunakóði. Sæktu í hlutum (tekjulyklar, færslur ≥ framkvæmdamikilvægi, síðustu 2 mánuðir ársins og fyrsti mánuður næsta árs).
- **Undirbækur:** aldursgreining viðskiptamanna og lánardrottna (`aging`), bankareikningar og afstemmingar (`Bank Acc. Reconciliation`, `Bank Account Ledger Entry`), fastafjármunir (`Fixed Asset`, `FA Ledger Entry`), birgðir (`Item Ledger Entry`), VSK-uppgjör.
- **Tengdir aðilar:** viðskiptamenn og lánardrottnar merktir sem tengdir, millifélagslyklar.

- **Birgðir:** ef `Item Ledger Entry` > 0 í `profile.json` eða `dataset.balance.categories.birgdir` er ekki 0, settu `birgdir` í `bs_jan` og `bs_aug` (staða á upphafs- og lokadegi úr `dataset.balance`, samtölur fyrst) og línuna „Breyting birgða“ í `cf`. `eignir` er heildareignir með birgðum. Félag án birgða: slepptu lyklinum (sýnin er þá eins og áður).
- **Lánssala** (valkvætt, `cy.lanssala`): ef verulegur hluti sölu er staðgreiddur (kassakerfi, kort), sæktu samtölu reikningsfærðrar sölu á tímabilinu úr `Cust. Ledger Entry` (`Sales (LCY)`, tegund Reikningur), án staðgreiðsluviðskiptamanna kassakerfis. Annars er innheimtutími reiknaður af öllum tekjum og verður villandi lágur.

Breyttu í JSON-lista og keyrðu:
```
python3 ${CLAUDE_SKILL_DIR}/scripts/je_tests.py --entries gl.json --materiality <M> --year-end 2026-12-31 --revenue-accounts 1110,1120 \
  [--weekend-ok] [--auto-sources KASSI,BANKI] [--profile dataset.json] --out je.json
```

**Snið félags í færsluprófunum (gervigreindin verður að meta þetta fyrir hverja keyrslu):**
- `--weekend-ok` (eða `profile.weekend_trading`/`retail`/`hospitality: true` í `dataset.json`): **skylt** hjá smásölu, veitingum, gistingu, afþreyingu og öðrum sem selja um helgar (ÍSAT 47, 55, 56, 90–93, eða sala í kassakerfi á laugardögum/sunnudögum). Þá flaggar helgarprófið aðeins handfærslur, ekki sjálfvirkar sölufærslur. Hjá öðrum félögum (verkstæði, heildsala, þjónusta) er sjálfgefið óbreytt: allar helgarfærslur flaggaðar.
- `--auto-sources` (eða `profile.auto_sources`/`pos_sources`, listi): upprunakóðar sem koma úr kassakerfi (POS), bankainnlestri, færsluhirðum, yfirlitum eða öðrum samþættingum. Sæktu töfluna `Source Code` (reitir 1 kóði, 2 lýsing) og teldu fjölda `G/L Entry` á tekjulyklum eftir upprunakóða (samtölur, ekki færslur); kóðar sem bera nær alla sölu og lýsing bendir til sjálfvirkni fara hér inn. Án þeirra flaggast öll kassasala sem „handfærðar tekjur“. Kóðarnir bætast við innbyggða listann (`AUTO_SOURCES`), koma ekki í stað hans. Nefndu valda kóða í lýsingu prófsins í `je_js`.
- Sjálfgefið (enginn rofi, enginn `profile`-lykill) gefur nákvæmlega sömu niðurstöðu og áður. Ef vikið er frá sjálfgefnu skráir `je.json` það í `stillingar`.

## 3. Mikilvægi

Reiknaðu bil úr `thresholds.json` (0,5–1% tekna, 5–10% hagnaðar fyrir skatta, 1–2% eigna). Veldu eina tölu og rökstyddu. Framkvæmdamikilvægi 75%, smávægilegt 5%. Merkt **tillaga, endurskoðandi ákveður**.

## 4. Flipar

**Yfirsýn**
- Hero: stærðarflokkur (stórt letur) og dagar til skilafrests.
- Fjögur kort: endurskoðun (skyld/undanþegin), sjóðstreymi (skylt/ekki), skilafrestur og sekt, tilbúið fyrir endurskoðun (% af PBC-lista lokið).
- Graf: félagið á móti mörkum (þrjár láréttar stikur, eignir/velta/ársverk, með lóðréttum línum við mörk lítils og meðalstórs félags).
- „Fyrst að laga“: 3–5 brýnustu atriðin úr flipunum hér að neðan.

**Ársreikningur (drög)**
- Rekstrarreikningur og efnahagsreikningur á uppsetningu laganna (fyrra ár til samanburðar ef til). Birgðalína aðeins ef `birgdir` > 0; vörunotkunarlína falin ef hún er 0 bæði árin. Dálkar efnahags heita eftir dagsetningum (`js.bs_start`, `js.bs_end`), ekki mánuðum; `bs_jan`/`bs_aug` merkja aðeins upphafs- og lokastöðu.
- Sjóðstreymi (óbein aðferð) ef skylt.
- Kennitölur: veltufjárhlutfall, eiginfjárhlutfall, arðsemi eigin fjár, innheimtutími.
- Merkt **drög, óendurskoðað**. Ef jöfnuður efnahags næst ekki án afgangsstærðar: sýna mismuninn sem ábendingu.

**Undirbúningur endurskoðunar (PBC)**
Gátlisti með stöðu (*lokið / í vinnslu / vantar*) og sönnunargögnum úr BC:
- Bankaafstemmingar allra reikninga á reikningsskiladegi.
- Viðskiptamenn: undirbók = fjárhagur, aldursgreining, niðurfærsla vafasamra krafna.
- Lánardrottnar: undirbók = fjárhagur, ógreiddir og ósamþykktir reikningar.
- Skurður (cut-off): sala og innkaup síðustu og fyrstu daga tímabils.
- Birgðir: talning, verðmat (aðeins ef félagið á birgðir; hjá smásölu einnig rýrnun og talning í hverri verslun). Annars sleppt eða „Á ekki við“.
- Kortagreiðslur og kassakerfi (smásala, veitingar): uppgjörsreikningar færsluhirða stemma, dagsuppgjör kassakerfis á móti tekjum.
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
