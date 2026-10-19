---
name: stjorn
description: Stjórnarmælaborð úr Business Central (4 flipar) — Yfirsýn með innsýn á stjórnarmáli, Rekstur með tímabilsvali, samanburði við fyrra tímabil, fyrra ár, fjárhagsáætlun eða spá, rekstrarreikningi með drill-down á lykla og EBITDA-brú, Efnahagur og sjóðstreymi sem töflur með lykilmælikvörðum, og Áhættur. Notaðu þegar beðið er um stjórnarmælaborð, stjórnaryfirlit, „hvernig gengur“, samanburð tímabila, „hvað breyttist“, raun vs áætlun eða spá, fjárhagsáætlun, efnahag og sjóðstreymi, mánaðar- eða ársfjórðungsyfirlit, eða yfirlit fyrir eigendur.
---

# Stjórnarmælaborð

Stjórn þarf að sjá á 30 sekúndum hvort reksturinn er á réttri leið, hvað breyttist og hvað kallar á ákvörðun. Mælaborðið á að vera hógvært í orðalagi og nákvæmt í tölum.

**Fylgdu `bifrost-maelabord` og `bifrost-gogn`.** Aðeins lesið.

## 1. Gögn

- `dataset.json` úr `bifrost-gogn` (í ár og fyrra ár).
- Efnahagur: `period_breakdown` á `G/L Account` með `field_type:"balance"` og `Income/Balance=CONST(Balance Sheet)`, staða í lok hvers mánaðar. Flokkaðu í handbært fé, kröfur, birgðir, fastafjármuni, skammtímaskuldir, langtímaskuldir og eigið fé eftir undirflokki og nafni.
- `aging` fyrir viðskiptamenn og lánardrottna.
- Samþjöppun viðskiptavina og „hvað breyttist mest“ á lykil: samtölur (`Data.Totals.Get`), ekki færslur. Drill-down í Rekstri er óbreytt: liður → lyklar (úr `dataset.json`, alltaf heilt) → færslur, **sama drill-down og áður** (sjá `bifrost-gogn`, kafli 0: allar færslur ef þær eru ≤ 5.000 á tímabilinu, annars færslur stærstu liðanna).
- Ef verk: fjöldi opinna verka, óreikningsfært (úr `tekjuleki` ef keyrt).

## 2. Flipar (fjórir)

**Yfirsýn**
- Hero í fullri breidd með fjórum lykilmælum (EBITDA, tekjur og breyting, EBITDA-hlutfall, handbært fé). **Engin tala tvisvar** á flipanum.
- **Innsýn fyrir stjórn** í 3–4 liðum á stjórnarmáli (afkoma, sjóður, viðskiptavinir, áhætta), hver merktur *Til ákvörðunar · Til umræðu · Til upplýsingar*. **Ekkert bókhaldsmál** (ófullbókað, ójöfnuður, afstemmingar) — það fer í `manadarlok`.
- **„Árið stefnir í“:** EBITDA ársins (P50) með P10–P90 bili og tekjur ársins úr `spagerd`; graf raun (súlur) + spá (strikuð) með óvissuborða; ein setning um hvar óvissan liggur; tengill „Nánar: Spágerð →“.
- Tvö gröf: þróun á mánuði og hagnaður á móti sjóði.

**Rekstur**
- **Tímabilsval** (mánuður, ársfjórðungur, ár til dags, valið bil) sem gildir fyrir allt á flipanum.
- **„Bera saman við“** (einn veljari): *fyrra tímabil · sama tímabil í fyrra · áætlun (val um áætlun úr BC eða drög) · spá* (`spagerd`). Kemur í stað fyrri flipa Samanburðar, Raun vs spá og Áætlunar.
- Rekstrarreikningur sem skrollar lárétt (fyrra ár og allir mánuðir), með raun, viðmiði, fráviki og %. **Drill-down:** smellt á lið opnar lyklana á bak við hann.
- EBITDA-brú frá viðmiði til raunar, fylgir valinu.
- **Hvað breyttist mest:** 10 stærstu lyklar eftir áhrifum á afkomu á móti viðmiði (spá: eftir liðum).
- **Raun á móti spá eftir mánuðum** þegar spá er viðmið (frávik, innan/utan bils, „hvar skeikaði“).
- **Lykilhlutföll á mánuði:** framlegð, laun af tekjum, EBITDA-hlutfall, fyrra ár strikað.
- Einskiptisliðir merktir í töflunni („1×“) og neðanmálsgrein með niðurstöðu án þeirra. **Enginn rofi með/án.**
- Áætlanir: `G/L Budget Name` og `Finance.Budget.Compare` / `Finance.BudgetEntry.Get`. Tóm áætlun: segðu það og bjóddu drög (fyrra ár × forsendur), merkt *drög, ekki í BC*. Skrif í áætlun (`Finance.BudgetEntry.Set`) aðeins með skýru samþykki.

**Efnahagur og sjóðstreymi**
- **Engin gröf.** Fjórir mælikvarðar: veltufé, handbært fé frá rekstri (sjóðsmyndun), innheimtutími, eiginfjárhlutfall/skuldsetning.
- Efnahagsreikningur sem tafla (opnanlegur niður á lykla) og **sjóðstreymi (óbein aðferð) sem tafla fyrir neðan**, sem stemmir frá upphafs- til lokastöðu handbærs fjár.

**Áhættur**
- Aldur krafna (ein stika), stærstu skuldarar, samþjöppun viðskiptavina og áhættuskrá með alvarleika og viðbragði.

**Samstæða** (ef `consolidated: true`)
- Félagsval efst, og flipi **Félög**: framlag hvers félags til tekna, EBITDA og hagnaðar, og þróun hvers félags á mánuði.
- Brú: summa félaga → innbyrðis viðskipti → arður → samstæða.
- Innbyrðis kröfur og skuldir sýndar sér á efnahagsflipa.
- Tímabilsval og „Bera saman við“ fylgja félagsvalinu; í samstæðu eru tímabil borin saman eftir jöfnun og spá samstæðu er summa spáa félaganna.

## 3. Orðalag

- Hógvært og nákvæmt: „Tekjur eru 20% hærri en á sama tíma í fyrra.“ Ekki „frábær árangur“.
- Á eftir góðri niðurstöðu kemur fyrirvari ef hann á við: „Hluti skýrist af einskiptissölu í ágúst.“
- Merktu einskiptisliði í töflu og gefðu leiðrétta tölu í neðanmálsgrein, ekki með rofa.
- Stjórnarmál, ekki bókhaldsmál: „Hagnaðurinn skilar sér ekki í reiðufé“, ekki „ójöfnuður innan mánaðar“.

## 4. Það sem stjórn missir oft af

Prófun á vélsmiðju sýndi 21% EBITDA-hlutfall og hagnað upp á 258 m.kr., en handbært fé hafði lækkað um 337 m.kr. frá maí og 90% krafna voru gjaldfallnar. Stjórnarmælaborðið á alltaf að setja **hagnað og sjóðstöðu hlið við hlið** svo slíkt sjáist strax.

## 5. Sannreyning

- Tekjur, EBITDA og hagnaður stemma við `dataset.json` og samtölu fjárhags.
- Efnahagur stemmir (eignir = skuldir + eigið fé) í hverjum mánuði, annars er það sagt.
- Samanburður við fyrra ár notar sömu mánuði.

## Dæmi úr prófun (vélsmiðja, jan–ágú 2026)

Tekjur 1.295,6 m.kr. (+20% m.v. sama tíma 2025), EBITDA 271,5 m.kr. (21,0%), hagnaður fyrir skatta 257,8 m.kr. September ófullbókaður (engin laun né vörukaup). Einskiptissala án VSK 31,0 m.kr. í ágúst; án hennar er EBITDA ágústmánaðar um 22% í stað 35%.
