---
name: tekjur
description: Tekjumælaborðið „Tekjur“ úr Business Central (4 flipar) — tekjur og sala tímabils á móti fyrra ári og áætlun, tekjustoðir eftir lyklum og tegund sölu, viðskiptavinir með þróun, nýjum viðskiptavinum og samþjöppun, drill-down frá viðskiptavini í reikninga og reikningslínur, vörur, þjónusta og verk, verð og afslættir, og tekjuleki (óreikningsfært, 0 kr. notkun, sækjanlegt strax) sem flipi. Notaðu þegar beðið er um tekjur, sölu, söluþróun, viðskiptavini, „hverjir kaupa mest“, samþjöppun viðskiptavina, tekjustoðir, verð og afslætti, sölu eftir vöru, þjónustu eða verki, eða tekjuleka.
---

# Tekjur

Svarar: **Hvað seljum við, hverjum og á hvaða verði, hvernig þróast salan á móti fyrra ári og áætlun, og hvaða tekjur erum við að missa?**

Spegilmynd Kostnaðar-mælaborðsins (sama hliðarspjald og drill-down). Fylgdu `bifrost-maelabord` (reglur 1.0: hámark 4 flipar og 4 lykilmælar á flipa, engin tala tvisvar á sama flipa, eitt tímabilsval, hero í fullri breidd) og `bifrost-gogn`. **Aðeins lesið** — þetta skill gefur aldrei út reikninga. Flipinn Tekjuleki fylgir skillinu **`tekjuleki`** fyrir athuganirnar (A–H).

## 1. Gögn

**Gögn: samtölur fyrst** (`bifrost-gogn`, kafli 0). Upphæðir á viðskiptavin, birgi, lykil, verk og vöru koma sem samtölur úr BC (`Data.Totals.Get`, `period_breakdown`, `aging`); færslur eru aðeins sóttar fyrir drill-down á stærstu liðina og athuganir sem þurfa færsluna sjálfa.

- `dataset.json` (`bifrost-gogn`): tekjulyklar á mánuði (`cat = tekjur`), fyrra ár, ófullbókaðir mánuðir, einskiptisliðir.
- **Samtölur:** sala á viðskiptavin = Sala (SGM), reitur 62 á `Customer` með `Date Filter` (FlowField, eitt kall skilar öllum viðskiptavinum með heiti; eitt fyrir tímabilið og eitt fyrir sama tímabil í fyrra; mánaðarþróun með `period_breakdown` á `Customer`). Varaleið: `Data.Totals.Get` á `Cust. Ledger Entry` (`[18]`, `groupBy` `Customer No.`). Tekjur á vöru, þjónustu eða verk = `Data.Totals.Get` á `Sales Invoice Line` (`groupBy` `No.` eða `Job No.`). Tekjur utan viðskiptamannabókar = tekjulyklar í `dataset.json` mínus summa viðskiptamannabókar.
- **Færslur, aðeins fyrir drill-down og stoðaflokkun:** `G/L Entry` á tekjulyklum (reitir 1, 3, 4, 6, 7, 17, 28, 58: færsla, lykill, dags., fylgiskjal, lýsing, fjárhæð, upprunakóði, upprunanr.). Allar ef ≤ 5.000; hjá stærra félagi færslur stærstu stoða og lykla (80% af upphæð). Lyklasía `WHERE(G/L Account No.=FILTER(1000..1999))` (bilið eftir bókhaldslyklum félagsins). Tekjur eru með mínus í BC; snúðu formerki.
- `Cust. Ledger Entry` (1, 3, 4, 5, 6, 7, 13, 14, 15, 18, 36) fyrir drill-down, **sama drill-down og áður** (sjá `bifrost-gogn`, kafli 0: allar færslur ef þær eru ≤ 5.000 á tímabilinu, annars færslur stærstu liðanna): reikningar á viðskiptavin, `Sales (LCY)` án VSK, `Original Amt. (LCY)` með VSK, opið/greitt.
- `Sales Invoice Line` (2, 3, 4, 5, 6, 11, 15, 22, 27, 28, 29, 45), línur þeirra reikninga sem fylgja drill-down: línur á reikning — tegund (vara, forði, fjárhagslykill), magn, einingarverð, afsláttur %, upphæð, verk. Reikningur í erlendri mynt: línur í mynt; umreiknaðu í kr. með hlutfalli `Sales (LCY)` / summa lína.
- Verk og verðskrá: `Job`, `Job Planning Line`, `Resource` (verð og kostnaður á klst.) — sömu gögn og `framlegd`.
- Áætlun: `G/L Budget Entry` ef til; annars drög úr Stjórn (merkt **drög** alls staðar þar sem hún birtist).

**Tekjustoðir.** Flokkaðu hverja tekjufærslu í stoð (t.d. tilboðsverk, þjónusta og útköll, smíði, varahlutir og efni, einskiptissala, aðrar tekjur og endurrukkun, afslættir): fyrst eftir lykli (sér lykill = sér stoð), svo eftir lýsingu dagbókarfærslu eða reikningslínu. Segðu í skýringu að flokkunin sé eftir lýsingu.

## 2. Flipar (fjórir)

**Tímabilsval** efst (Mánuður · Ársfjórðungur · Ár til dags · Valið bil) gildir fyrir fyrstu þrjá flipana. Ár til dags = fullbókaðir mánuðir. Bráðabirgðamánuðir eru valanlegir en merktir og sýndir daufir.

1. **Yfirsýn**
   - Hero: tekjur tímabils, ein setning, og fjórar tölur (breyting frá fyrra ári í kr., meðaltal á mánuði, án einskiptis, besti mánuður).
   - Fjórir lykilmælar: vöxtur án einskiptis á móti fyrra ári · á móti áætlun (merkt drög) · hlutdeild þriggja stærstu viðskiptavina · sækjanlegt strax úr tekjuleka.
   - Tekjur á mánuði á móti fyrra ári (raunmánuðir ef til, annars ársheild / 12 strikuð) og áætlun. Einskiptissala sem sér litur, merkt **1×**.
   - Tekjustoðir sem smellanlegar láréttar súlur → færslur.
2. **Viðskiptavinir**
   - Gagnagæðaborði efst ef hluti tekna er ekki á viðskiptavin (sjá 3).
   - Lykilmælar: sala á viðskiptamannabók (og % af tekjum) · fjöldi viðskiptavina með reikning, nýir, tengdir aðilar · hlutdeild stærsta · fjöldi reikninga og meðalreikningur.
   - Samþjöppun sem ein stika (stærsti · næstu tveir · aðrir), listi með þróun á mánuði og merkjum (*nýr*, *1×*, *tengdur aðili*), og sér línan **„Óskráð á viðskiptavin“** með færslum.
   - Graf: hvernig salan er skráð (reikningar á móti dagbók) á mánuði.
   - Nýir = fyrsti reikningur á árinu og engin staða í árslok fyrra árs. Tapaðir = sala í fyrra en engin í ár — aðeins ef fyrra ár er á viðskiptavini; annars segðu að það sé ekki hægt.
   - Tenglar: „Handfærðar tekjur: sjá Mánaðarlok“ og „Innheimta og gjaldfallnar kröfur: sjá Sjóðstreymi og bankar“. **Innheimta er ekki hér.**
3. **Vörur og þjónusta**
   - Lykilmælar: tekjur bókaðar á verk · verðskrá vinnu · afslættir · hlutfall reikningslína á vöru eða forða.
   - Tré: stoð → lykill → færslur, með hlutdeild á tímabili og hlutdeild í fyrra (breyting á samsetningu).
   - Verk: samningur og reikningsfært til dags; framlegð og framvinda vísa á `framlegd`.
   - Verð og afslættir: einingarverð af reikningslínum (klst., mánaðargjald, mynt) og afslættir (lykill og línuafsláttur). Ef línur eru á fjárhagslykil en ekki vöru: segðu að verðfrávik á einingu sé ekki hægt að greina.
4. **Tekjuleki** — innihald `tekjuleki`-mælaborðsins í einum flipa: hero *sækjanlegt strax*, þrír lykilmælar, rofi **Aðgerðir | Uppruni** (gátreitir sem uppfæra samtölu; upprunatafla með síu), og „Aðferð og athuganir“ í fellanlegum texta. Gjaldfallnar kröfur eru ekki taldar með.

## 3. Drill-down

Sama hliðarspjald og í Kostnaði (leit, röðun, samtala neðst, Esc lokar):
- **Viðskiptavinur → reikningar** (dags., reikningur, lýsing, lykill, án VSK, með VSK, opið/greitt) → **reikningslínur** (lína, lykill, lýsing, magn, einingarverð, afsláttur, upphæð, verk) með „← Til baka“.
- **Stoð eða lykill → færslur** (dags., fylgiskjal, lýsing, lykill, viðskiptavinur eða *dagbók*, fjárhæð).
- **Óskráð á viðskiptavin → dagbókarfærslur.**
Drill-down fylgir völdu tímabili. Allir liðir eru smellanlegir eins og áður; hjá félagi með fleiri en 5.000 færslur á tímabilinu sýna minnstu liðirnir samtölu og „spurðu gervigreindina um færslurnar“ (`bifrost-gogn`, kafli 0).

## 4. Gagnagæði: tekjur utan viðskiptamannabókar

Algengt er að sala sé bókuð með dagbók (t.d. upprunakóði `FHFBOK`) beint á tekjulykil án viðskiptavinar. Þá:
- Reiknaðu hlutfall tekna á viðskiptamannabók **fyrir sama tímabil** í teljara og nefnara (ekki reikninga jan–okt á móti tekjum jan–ágú).
- Sýndu „Óskráð á viðskiptavin“ sem sér línu, aldrei falið í „Aðrir“.
- Segðu berum orðum að sala á viðskiptavin, þróun og samþjöppun eigi aðeins við um reikningsfærðu söluna.
- Vísaðu á Mánaðarlok fyrir handfærðar tekjur.
- Athugaðu hvort fyrra ár sé til á mánuði í `G/L Entry` (dagbókarfærslur) áður en þú segir að það sé aðeins ársheild.

## 5. Samstæða

- Félagsval efst (`entityPicker`). Innbyrðis sala (viðskiptavinur er félag í samstæðunni) er merkt *tengdur aðili* hjá hverju félagi og **jöfnuð út** í samstæðu: sýndu brú *summa félaga → innbyrðis sala → samstæða*.
- Samþjöppun og stærstu viðskiptavinir í samstæðu eru án innbyrðis viðskipta.
- Ófullbókaður mánuður hjá einu félagi gerir mánuðinn ófullbókaðan í samstæðu.

## 6. Sannreyning

- Tekjur á mánuði og lykil stemma við `dataset.json` upp á krónu; summa stoða = tekjur tímabils.
- Summa reikninga í viðskiptamannabók (`Sales (LCY)`) = summa tekjufærslna með upprunakóða sölu (`SALA`); reikningslínur stemma við reikning.
- Fyrra ár stemmir við ársheild; áætlun er merkt drög ef hún er ekki í BC.
- Sækjanlegt strax stemmir við `tekjuleki` (sama tala í miðstöð).
- Engin nöfn einstaklinga: forðar og starfsmenn sem kóðar eða verðflokkar, ekki upphafsstafir.

## Dæmi úr prófunum (október 2026, DT Vélsmiðjan)

Tekjur jan–ágú 1.295,6 m.kr. (+20,0% á móti 2025 × 8/12, +17,1% án einskiptissölu 31,0 m.kr. í ágúst). Aðeins 417,1 m.kr. á viðskiptamannabók jan–okt (31% af tekjum jan–okt); afgangurinn mánaðarleg söludagbók á 1110. Allar 41 reikningslínur á fjárhagslykil, engir línuafslættir. Sækjanlegt strax úr tekjuleka 15,2 m.kr.
