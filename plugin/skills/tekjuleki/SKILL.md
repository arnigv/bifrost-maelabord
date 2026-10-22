---
name: tekjuleki
description: "Athuganir fyrir flipann Tekjuleki í mælaborðinu Tekjur í Bifröst-mælaborðum (óreikningsfært, 0 kr. notkun, verðfrávik, rof í endurteknum reikningum). Innra skill Bifröst-mælaborða: notað af hinum skillum pluginsins við smíði mælaborða. Ekki nota það eitt og sér og ekki fyrir önnur verkefni."
---

# Tekjuleki

Sterkasta „wow“-mælaborðið: það finnur krónur sem viðskiptavinurinn vissi ekki af. Allt á að vera rekjanlegt niður á verk, færslu eða viðskiptamann svo hann geti brugðist við strax.

**Fylgdu `bifrost-maelabord` fyrir útlit og gæði og `bifrost-gogn` fyrir gagnaöflun.** Aðeins lesið úr BC.

## 1. Gögn

1. Keyrðu `bifrost-gogn` (eða notaðu `dataset.json` lotunnar). Lestu `profile` til að vita hvaða athuganir eiga við.
2. Sæktu eftir þörf (sjá töflu í `bifrost-gogn`, kafla 6):
   - **Ef verk:** `Job`, `Job Task`, `Job Planning Line`; notkun og sala á verk sem samtölur (`Data.Totals.Get` á `Job Ledger Entry`, `groupBy` `Job No.`). Notkun á 0 kr.: sæktu aðeins færslur með `Total Price=CONST(0)` og `Entry Type=CONST(Usage)`.
   - **Alltaf:** `aging` fyrir viðskiptamenn (`as_of_date` = í dag), og opnar `Cust. Ledger Entry`.
   - **Ef vörur:** sölufærslur í `Value Entry` (vara, magn, söluupphæð, afsláttur) síðustu 6 mánuði. Samtölur fyrst: `Data.Totals.Get` á `Value Entry` (`Item Ledger Entry Type=CONST(Sale)`, `groupBy` `Item No.`) fyrir `Sales Amount (Actual)`, `Cost Amount (Actual)`, `Discount Amount`, `Invoiced Quantity`. Færslur aðeins fyrir frávikin: 0 kr. sölulínur (`Sales Invoice Line` með `Type=CONST(Item)` og `Amount=CONST(0)`) og línur með `Line Discount %` yfir viðmiði. Listaverð úr `Item` (`Unit Price`, `Unit Cost`) og `Price List Line` ef verðlistar eru notaðir.
   - Tekjur á viðskiptamann á mánuði síðustu 12 mánuði, til að finna rof: `Data.Totals.Get` á `Cust. Ledger Entry` (`groupBy` `Customer No.`), eitt kall á mánuð.

## 2. Athuganir

Reiknaðu hverja athugun, skráðu **fjárhæð án VSK**, **vissu** (Staðfest / Líklegt / Athuga), **uppruna** (verk, færsla, viðskiptamaður) og **næsta skref**.

| # | Athugun | Hvernig | Vissa |
|---|---|---|---|
| A | **Reikningshæft en óreikningsfært** | Samningslínur í `Job Planning Line` (Contract Line) með dagsetningu liðna og ekki reikningsfærðar; eða verk með notkun en engum sölufærslum. | Staðfest |
| B | **Notkun á 0 kr. söluverði** | `Job Ledger Entry` notkun (efni, fjárhagslínur, akstur) með Total Price = 0 á verkum sem eru reikningsfærð eftir notkun. | Líklegt |
| C | **Verk sem eru búin en opin** | Verk með lokadag liðinn og stöðu Opið, eða notkun eftir lokadag samnings. Fjárhæð = reikningshæf notkun eftir lokadag. | Líklegt |
| D | **Gjaldfallnar kröfur** | `aging`: gjaldfallið eftir aldri. Sýna sérstaklega > 60 daga og viðskiptamenn sem fá nýja reikninga þrátt fyrir vanskil. | Staðfest (innheimta) |
| E | **Afslættir og verðfrávik** | Sama vara/þjónusta seld á meira en 15% lægra verði en miðgildi; afsláttarhlutfall sem hækkar milli tímabila. Fjárhæð = munur á móti miðgildi. | Athuga |
| F | **Rof í endurteknum reikningum** | Viðskiptamaður reikningsfærður ≥ 4 mánuði í röð en ekki í síðasta fullbókaða mánuði. Fjárhæð = meðalreikningur. | Athuga |
| G | **Tímar umfram fast verð** | Föst mánaðargjöld þar sem tímar á verðskrá fara yfir gjaldið (t.d. rammasamningar). Fjárhæð = munur. | Líklegt |
| H | **Samkeyrsla við ytri kerfi** | Aðeins ef notandi hefur tengt annað kerfi (t.d. mæla, áskriftir): notkun þar sem enginn reikningur er í BC. | Eftir gögnum |

Slepptu athugunum sem eiga ekki við og segðu það í *Aðferð* í fæti („Engin verk í BC, verkathuganir eiga ekki við“).

**Félag án verka (verslun, heildsala).** A, C og G eiga ekki við (staða `Á ekki við`, niðurstaða „Engin verk í BC.“); `leakJobs`/`openJobs` = `null`. Athuganirnar á vörusölu:

| # | Athugun á vörusölu | Hvernig | Vissa | `src.g` |
|---|---|---|---|---|
| B | **0 kr. sölulínur** | Reikningslínur á vöru (`Type=Item`) með upphæð 0 þar sem varan hefur listaverð > 0 í `Item`/`Price List Line`. Fjárhæð = magn × listaverð. Sleppa línum merktum gjöf/kynningu ef lýsing segir það. | Líklegt | `zero` |
| E | **Afsláttur umfram venju** | `Line Discount %` á línu meira en 10 prósentustigum yfir miðgildi viðskiptavinar (eða vöruflokks). Fjárhæð = munur á móti venjulegum afslætti. | Athuga | `price` |
| E | **Verð undir kostnaði eða verðskrá** | Einingarverð undir `Unit Cost` vörunnar, eða meira en 15% undir listaverði án skráðs afsláttar. Fjárhæð = munur. | Athuga | `price` |
| F | **Rof í endurteknum reikningum** | Eins og að ofan (á líka við um áskriftir og fasta viðskiptavini heildsölu). Staðgreiðsluviðskiptavinum (`pos`) er sleppt. | Athuga | `rof` |

Í mælaborðinu birtast þá síurnar *Allt · 0 kr. sölulínur · Verð og afslættir · Rof í reikningum*, dálkurinn Klst. fellur út, og hero tekjuleka telur upp þær athuganir sem eiga ekki við. *Sækjanlegt strax* = B (staðfest og líklegt); E og F eru *til athugunar*.

**Tvítalning:** gjaldfallnar kröfur (D) eru *innheimta*, ekki leki. Sýndu þær sér og teldu þær ekki með í „sækjanlegt strax“ nema notandi biðji um það.

## 3. Mælaborðið

Einfalt: **þrír flipar**, engin tala sýnd tvisvar á sama flipa, og ekkert bókhaldslegt orðalag í hero.

Flipar: **Yfirsýn · Uppruni · Aðgerðir**

**Yfirsýn**
- **Hero í fullri breidd:** *Sækjanlegt strax* (A+B+C+G, staðfest og líklegt) sem stór tala og ein setning á mæltu máli („vinna sem er unnin en ekki rukkuð“, ekki „óreikningsfærð verkfærsla“). Engar lykiltölur inni í hero.
- **Hámark 4 lykilmælar** sem endurtaka ekki hero-töluna, t.d. *Til athugunar* (E+F og óvissir 0 kr. liðir), *Endurtekur sig á ári*, *Verk og samningar með leka* (fjöldi af opnum).
- **Stærstu lekarnir** (`.items`): vissa, lýsing, verk og viðskiptavinur, fjárhæð og næsta skref.
- Gjaldfallnar kröfur (D) eru innheimta, ekki tekjuleki: í mesta lagi **ein lína** með tengli (`data-nav`) „Gjaldfallnar kröfur: sjá Sjóðstreymi og bankar“ á mælaborðið `sjodstreymi`. Engin aldursgreining hér.

**Uppruni:** ein raðanleg tafla yfir allar línur (verk, lýsing, viðskiptavinur, tegund, klst., fjárhæð í kr., vissa) með samtölu og **síu á tegund**: *Allt · Verk og tímar* (óreikningsfært, umfram fast gjald, eftir samningslok) *· 0 kr. notkun · Verð og afslættir* (ef vörur eða verðskrá; annars stutt skýring á því hvers vegna ekkert birtist).

**Aðgerðir:** tækifæri til tekjuaukningar, hvert með áhrifum í kr. (einskiptis og á ári), átaki, vissu og næsta skrefi — rukka óreikningsfært, rukka 0 kr. notkun, endursemja föst gjöld, hækka verð þar sem framlegð er undir markmiði (úr `framlegd`), draga úr afslætti. Gátreitir þar sem notandi velur aðgerðir og samtalan uppfærist. Engir hermar eða stikur.

**Aðferð** er ekki flipi heldur fellanlegur texti (`<details>`) í fæti: hvaða athuganir voru gerðar, hverjar áttu ekki við og hvaða forsendur voru notaðar.

## 4. Sannreyning

- Hver fjárhæð á að vera rekjanleg á færslur. Taktu 2–3 stærstu atriðin og staðfestu þau með beinu kalli.
- Engin tvítalning milli A, B, C og G (sama færsla má aðeins vera í einni).
- Segðu frá því sem er óvíst.

## Dæmi úr prófunum (október 2026)

- **Vélsmiðja (verk):** lokið en óreikningsfært um 14,4 m.kr.: tíu tímaverk frá ágúst (9,9 m.kr., A), akstur janúar–ágúst bókaður á 0 kr. (3,6 m.kr. með álagi, B) og sérfræðivinna eftir lok samnings á 0 kr. (1,0 m.kr., B og C). Tímar á föstu mánaðargjaldi fóru í 168% af gjaldinu (G).
- **Orkufyrirtæki (veita):** heimtaugarverk óreikningsfært (2,1 m.kr., A), tveir mælar með notkun en enga gjaldskrá (0,17 m.kr., H). Innheimta sýnd sér: heimtaugarreikningur 74 daga gjaldfallinn (2,6 m.kr.) og orkukröfur (0,46 m.kr.).

## Samstæða

- Félagsval efst. Tekjuleki er fundinn á hvert félag og lagður saman; innbyrðis sala (milli félaga í samstæðu) telst **ekki** tekjuleki og er sleppt.
- Tafla og listar fá dálkinn *Félag*. Gjaldfallnar kröfur á félög innan samstæðu birtast sér.
