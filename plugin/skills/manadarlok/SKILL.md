---
name: manadarlok
description: "Mælaborðið „Mánaðarlok og afstemmingar“ í Bifröst-mælaborðum (Lokun mánaðar, Afstemmingar, Opin atriði), smíðað úr föstu sniðmáti. Notaðu AÐEINS innan Bifröst-mælaborða: þegar notandinn biður um Bifröst-mælaborð eða þetta mælaborð með nafni, eða breytir mælaborði sem pluginið bjó til. Ekki fyrir almennar spurningar um rekstur eða Business Central, aðrar skýrslur, skjöl eða artifacts."
---

# Mánaðarlok og afstemmingar

> **Fast sniðmát.** Þetta mælaborð er smíðað úr `template/` (sjá `bifrost-maelabord`, *Föst sniðmát*). Skrifaðu ekki HTML. Safnaðu gögnunum eftir `template/schema.md` (sýnidæmi: `template/example.json`), og smíðaðu með `render.py --dashboard manadarlok` eða `bundle.py`. Við breytingu eða uppfærslu er **aðeins þetta mælaborð** endurgert og birt (og viðbætur þess í `ext/`), sjá *Umfang breytinga*. Lýsingin hér að neðan segir hvað sniðmátið sýnir og hvaðan gögnin koma.

Svarar: **Er síðasti mánuður lokaður, stemmir bókhaldið og hvað á eftir að gera, af hverjum?**

Fylgdu `bifrost-maelabord` (hönnun, ljóst sjálfgefið, leiðarstika, fótur) og `bifrost-gogn` (`dataset.json`). **Aðeins lesið.** Mælaborðið bókar ekkert, stemmir ekkert af, keyrir hvorki afskriftir né gengisendurmat og lokar engu tímabili í BC. Næstu skref eru tillögur til fólks. Ef notandi biður um aðgerð, staðfestu fyrst í spjalli.

## 1. Gögn

| Þörf | Heimild í BC / Bifröst |
|---|---|
| Hreyfingar á mánuð og lykil, fullbókaðir mánuðir | `dataset.json`: `months[].complete`, `incomplete_reason`, `accounts[].months` |
| Efnahagslyklar á mánaðarlokum, jöfnuður innan mánaðar | `dataset.json`: `balance.accounts[].levels`, `balance.stemming` |
| Bankareikningar, staða í dag, síðasta yfirlit | `Bank Account` (staða, „Last Statement No.“, „Balance Last Statement“), `Bank Account Statement`, `Bank Acc. Reconciliation` |
| Útistandandi færslur við síðustu afstemmingu | `Bank Account Ledger Entry` (opnar, óafstemmdar) |
| Greiðslukort (fyrirtækjakort) | Bankareikningar af tegundinni greiðslukort (skuld, kreditstaða) á móti kortalykli í fjárhag. Ekkert fyrirtækjakort: `banks_gl.kort` = 0, `kort_m` = 0 |
| Kortauppgjör (færsluhirðar) | Verslanir og aðrir sem taka við kortum: bankareikningar eða millireikningar fyrir uppgjör færsluhirða (debetstaða, gert upp innan fárra daga), `teg: "Kortauppgjör"`. Samtölur fyrst: staða úr `Bank Account` (Balance at Date) og lykli í `Bank Account Posting Group`; óuppgert = `Data.Totals.Get` á `Bank Account Ledger Entry` (Open = true, groupBy `Bank Account No.`); aldur elstu opnu færslu (`open_days`) úr einni færslu á reikning (`data_batch_records`, raðað eftir `Posting Date`, top 1). `lag_days` úr samningi eða miðgildi uppgjörstíma síðustu mánaða. Síðasta uppgjör færsluhirðis = `stmt_*` |
| Birgðir (aðeins ef félagið heldur birgðir) | Samtölur fyrst: `Data.Totals.Get` á `Value Entry` (summa `Cost Amount (Actual)`, og `Cost Amount (Expected)` ef áætlaður kostnaður er bókaður, Posting Date ≤ dagur) = `inventory.subledger`; staða birgðalykla úr `Inventory Posting Setup` („Inventory Account“, og „Inventory Account (Interim)“ ef notað) = `inventory.gl`. `Item Ledger Entry` aðeins ef rekja þarf mismun á vöru eða birgðageymslu. Hreyfing birgðabreytingar/vörunotkunar á mánuð úr `period_breakdown`. Engar birgðir (enginn `Value Entry` eða staða 0): sleppa `inventory` |
| Verk (aðeins ef verkbókhald er notað) | `jobs_n` = fjöldi opinna `Job`. 0 ef ekkert verk: verkatengd atriði (`verk`, áfangar, verk í vinnslu) falin |
| Viðskiptamenn og lánardrottnar á móti fjárhag | `aging` (eða `Cust./Vendor Ledger Entry`, opnar) á móti stöðu safnlykla (bókunarflokkar) sama dag |
| VSK | Útskattur, innskattur og uppgjörsreikningur VSK úr efnahag; tveggja mánaða tímabil, gjalddagi 5. annars mánaðar eftir tímabil |
| Gengismunur | `Cust./Vendor Ledger Entry` með `Currency Code`, `Currency Exchange Rate` (gengi á mánaðarlokum), `Exch. Rate Adjmt. Reg.` (hvort endurmat hefur verið keyrt) |
| Afskriftir | Afskriftalyklar í `dataset.json`; ef eignaskrá er notuð, `FA Ledger Entry` |
| Tímabil lokað | `General Ledger Setup` og `User Setup` („Allow Posting From/To“), `Accounting Period` (`Closed`, `New Fiscal Year`) |
| Ósamþykktir reikningar | `kostnadur` (innkaupareikningar í samþykkt, gjalddagar) |
| Óbókaðar greiðslur | `sjodstreymi` (`unbooked`: laun, staðgreiðsla, VSK, afborganir sem vantar í bankabók) |
| Færsluprófanir (handfærðar tekjur, tvíreikningsfærsla, helgarfærslur) | `endurskodun` |

Lesköll fara í gegnum Bifröst. Samtölur fyrst (`bifrost-gogn`, kafli 0): hvort mánuður er bókaður og hreyfing á lykil úr `period_breakdown` eða `Data.Totals.Get` (`G/L Entry`, `groupBy` `G/L Account No.`, sía á mánuðinn); summa bankahreyfinga á reikning úr `Data.Totals.Get` á `Bank Account Ledger Entry`; undirbækur með `aging`. Færslur (`data_batch_records`) aðeins fyrir opnar bankafærslur eftir síðustu afstemmingu og atriði sem þarf að sýna stök. Áætlaðar fjárhæðir (t.d. laun sem vantar) miðast við síðasta fullbókaða mánuð og eru merktar ≈.

## 2. Flipar (hámark 4 lykilmælar á flipa, engar tvítekningar)

**Lokun mánaðar**
- Hero í fullri breidd: „X af Y atriðum lokið fyrir <mánuð>“, ein setning um stöðuna og fjórar tölur (atriði sem vantar, ≈ óbókaður rekstrarkostnaður, síðasti fullbókaði mánuður, dagar frá mánaðarlokum).
- Mánaðaval: síðustu 6 mánuðir sem spjöld með *Fullbókaður / Ófullbókaður / Stendur yfir* og lítilli stiku (lokið · vantar · á ekki við). Sjálfgefið er síðasti mánuður sem á að vera lokaður (fyrri mánuður ef dagurinn í dag er í næsta mánuði).
- Gátlisti, hvert atriði með stöðu (*Lokið · Vantar · Á ekki við*), fjárhæð og ábyrgð (*Bókari / Fjármálastjóri*):
  1. Tekjur bókaðar (athuga ef langt undir meðaltali).
  2. Laun bókuð.
  3. Vörunotkun bókuð (aðeins ef félagið hefur vörunotkun; hjá félagi með birgðir „Birgðabreyting/vörunotkun bókuð“).
  - *Eftir rekstri:* „Birgðir stemma við fjárhag (birgðabók á móti birgðalykli)“ ef birgðir; „Verk í vinnslu og áfangar bókuð“ ef `jobs_n` > 0; „Kortauppgjör stemmir við uppgjör færsluhirðis“ ef kortauppgjör eru í `banks`. Sniðmátið felur þessi atriði ef gögnin sýna ekki viðkomandi rekstur.
  4. Afskriftir keyrðar.
  5. VSK-uppgjörsfærsla (aðeins í lok tveggja mánaða tímabils; annars *á ekki við*). Uppgjörsreikningur með stöðu sem hækkar sífellt bendir á að uppgjörsfærslur vanti.
  6. Gengismunur endurmetinn (*á ekki við* ef engar opnar færslur í erlendri mynt). Áætla áhrif með gengi mánaðarloka.
  7. Áfallið og fyrirframgreitt (fastur kostnaður eins og húsnæði og vextir kominn inn).
  8. Tímabil lokað í BC („Allow Posting From“ eftir mánuðinum, ekki tómt).

**Afstemmingar** — stöðuspjald grænt/gult/rautt með mismun í kr.:

| Athugun | Grænt þegar |
|---|---|
| Bankabók á móti bankalykli | Summa bankareikninga = fjárhagslykill |
| Kort á móti kortalykli | Summa korta = fjárhagslykill (aðeins ef fyrirtækjakort) |
| Kortauppgjör stemmir við uppgjör færsluhirðis | Óuppgert 0 kr. og engin færsla eldri en `lag_days` (aðeins ef kortauppgjör) |
| Birgðir á móti fjárhag | Birgðabók (`Value Entry`) = birgðalykill (aðeins ef birgðir) |
| Bankayfirlit á móti bankabók | Yfirlit + útistandandi = bankabók á síðasta afstemmingardegi |
| Bankafærslur eftir síðustu afstemmingu | Engar þekktar greiðslur vantar (laun, staðgreiðsla, VSK, lán) |
| Viðskiptamenn / lánardrottnar á móti fjárhag | `aging`-samtala = safnlyklar |
| VSK | Útskattur − innskattur stemmir við skilagreinar, uppgjörsreikningur hreinsast |
| Jöfnuður innan mánaðar | `balance.stemming` er 0 í hverjum mánuði (sýnt sem frávikssúlur) |
| Langtímalán | Staða = lánayfirlit (afborganir bókaðar) |

Tafla yfir banka, kortauppgjör og kort: staða í BC í dag, síðasta yfirlit (dags. og nr.), yfirlitsstaða, bankabók þá, óafstemmt og staða. Kort með númeri, aldrei nafn korthafa.

**Opin atriði** — samandreginn verkefnalisti úr hinum flipunum og úr `endurskodun`, `kostnadur` og `sjodstreymi`, aðeins þau sem eiga við félagið (t.d. tvíreikningsfærsla áfanga aðeins ef verk, með `"if": "jobs_n"`): óbókaðar greiðslur, VSK, ársuppgjör fyrra árs ólokað, ófullbókaður mánuður, möguleg tvíreikningsfærsla, handfærðar tekjur, ósamþykktir reikningar komnir á gjalddaga, gengismunur, lán, innbyrðis staða, opin tímabil. Hvert atriði: alvarleiki (rautt/gult), lýsing, **næsta skref**, ábyrgðarhlutverk og fjárhæð. Raðað eftir alvarleika og svo fjárhæð. Síur fyrir alvarleika og hlutverk.

## 3. Sannreyning

- Fullbókaðir mánuðir í mælaborði = `months[].complete` í `dataset.json`.
- Bankabók stemmir við bankalykil og kort við kortalykil upp á krónu (eða mismunurinn er sýndur rauður). `banks_gl.bankar` á ekki að innihalda lykla kortauppgjörs; þeir fara í `banks_gl.kortauppgjor`.
- Birgðir: `inventory.subledger` (Value Entry) á móti `inventory.gl` sama dag.
- `aging`-samtölur á móti safnlyklum sama dag; mismunur sýndur í kr.
- VSK-skuld á tímabil = breyting á útskatti − innskatti á tímabilinu; á að stemma við skilagrein (t.d. júl–ágú).
- Summa óbókaðra greiðslna = summa liða í `unbooked`.
- Keyrðu útreikningana með node áður en birt er og berðu lykiltölur saman við fjárhaginn.

## Samstæða

- Félagsval efst; gátlisti og afstemmingar eru á hvert félag. Mánuður er lokaður í samstæðu aðeins ef hann er lokaður í öllum félögum; segðu hjá hvaða félagi hann er opinn.
- Lína **Innbyrðis staða stemmir**: krafa félags A á B = skuld B við A og innbyrðis viðskipti mánaðarins (t.d. umsýslugjöld) eru eins bókuð hjá báðum, úr `eliminations.json` (tegund `stada` og `rekstur`). Mismunur rauður.
- Opin atriði sýna dálk *Félag*.
- Eitt félag: sýndu innbyrðis stöðu við tengd félög sem gula línu „ekki staðfest við gagnaðila“ nema bækur gagnaðila séu líka lesnar.
