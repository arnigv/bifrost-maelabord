---
name: bifrost-skyndiuttekt
description: Ræsir Bifröst-mælaborðapakkans — sýnir fyrst kynningu (sex sjálfgefin mælaborð, þrjú til viðbótar að vali, hve langan tíma það tekur og hvað á að velja í leyfisgluggum), spyr um eitt félag eða samstæðu, sækir gögnin einu sinni og býr til miðstöð og mælaborðin, með hnapp til að bæta fleirum við. Notaðu þegar notandi er nýbúinn að bæta pluginu við, ýtir á „Try“, spyr „hvað gerir þetta plugin“ eða „hvaða mælaborð eru til“, biður um „mælaborðin“, „settu upp mælaborðin“, „skyndiúttekt“, „keyrðu Bifröst“, „hvernig stendur félagið“, „bættu við mælaborði“, onboarding eða heildaryfirsýn yfir rekstur úr BC.
---

# Bifröst skyndiúttekt (ræsir) · útgáfa 1.0

Markmið: notandinn sér **fyrsta mælaborðið innan 10 mínútna** og öll sex sjálfgefnu innan um 25 mínútna, tengd í einni miðstöð. Fleiri bætast við að vali.

Fylgdu `bifrost-maelabord` (útlit, reglur 1.0) og `bifrost-gogn` (gögn). **Aðeins lesið úr BC.**

## 0. Kynning (alltaf fyrst, áður en gögn eru sótt)

Sendu þessa kynningu í spjallið (ekki artifact), á íslensku. Slepptu henni ef notandinn hefur séð hana í samtalinu.

> **Bifröst mælaborð: sex mælaborð og miðstöð úr Business Central**
>
> | # | Mælaborð | Flipar | Svarar |
> |---|---|---|---|
> | 1 | Stjórn | Yfirsýn · Rekstur · Efnahagur og sjóðstreymi · Áhættur | Er reksturinn á réttri leið, á móti fyrra ári, áætlun og spá? |
> | 2 | Sjóðstreymi og bankar | Staða í bönkum · 13 vikna spá · Innheimta | Hver er staðan í bönkum og eigum við fyrir næstu 13 vikum? |
> | 3 | Kostnaður | Samþykkt reikninga · Birgjar og kostnaðarliðir | Hvað bíður samþykkis, hvert fer kostnaðurinn (niður í færslur)? |
> | 4 | Mánaðarlok og afstemmingar | Lokun mánaðar · Afstemmingar · Opin atriði | Er mánuðurinn lokaður og stemmir bókhaldið? |
> | 5 | Tekjur | Yfirsýn · Viðskiptavinir · Vörur og þjónusta · Tekjuleki | Hvaðan koma tekjurnar (niður í reikninga) og hvaða tekjur erum við að missa af? |
> | 6 | Sjálfvirknivæðing | Yfirlit · Erindrekar · Handverk · Dagatal og saga | Hvaða verk má fela erindrekum og hvenær? (Keyrsla læst þar til virkjað með ráðgjafa.) |
> | ★ | Miðstöð | — | Allt á einni síðu, og hnappurinn **+ Bæta við mælaborði**. |
>
> **Bæta við síðar:** Framlegð og verk · Spágerð · Endurskoðun og ársreikningur · **sérmælaborð fyrir þína atvinnugrein** (t.d. Verk og útboð, Birgðir og lager, Áskriftartekjur, Leigusafn) · eða þitt eigið. Miðstöðin stingur upp á þeim sem passa félaginu.
>
> **Áður en þú byrjar:**
> - **Tími:** fyrsta mælaborðið birtist eftir um 5–10 mínútur, öll sex eftir um 20–25 mínútur. Þú getur skoðað hvert um leið og það birtist.
> - **Leyfisgluggar:** Claude biður um leyfi til að lesa úr Bifröst. Veldu **Always allow** fyrir Bifröst svo keyrslan stöðvist ekki. Aðeins er lesið, ekkert skrifað.
> - **Umhverfi:** ef þú ert beðin(n) að velja BC-umhverfi, veldu **Production** (raunveruleg gögn) nema þú sért að prófa; prófunarumhverfi heita oft *Sandbox*, *UAT* eða *Test*.
> - Öll mælaborðin virka fyrir **eitt félag** eða **samstæðu**.
>
> **Þú getur unnið þau áfram:** „bættu við flipa fyrir laun eftir deildum“, „berðu saman Q3 í ár og í fyrra“, „gerðu sama fyrir hitt félagið“, „uppfærðu tölurnar“. Breytingar birtast á sömu slóð.

> **Leiðbeiningar og góð ráð:** heil síða um uppsetningu, fyrstu keyrslu, sýnidæmi, skipanir og sjálfvirknivæðingu fylgir pluginu. Segðu „sýndu leiðbeiningarnar“.

Spyrðu svo með vali (ein spurning):
- **Öll sex** (mælt með)
- **Aðeins nokkur** — *veldu úr töflunni hér að ofan, t.d. „1, 2 og 5“*
- **Bara kynning, ekki núna**

Ef notandi velur „Aðeins nokkur“: sýndu strax valglugga (fjölval) með heitum mælaborðanna sex, ekki bara texta.

## 0a. Leiðbeiningar

Ef notandi biður um leiðbeiningar, góð ráð eða „hvernig virkar þetta“: birtu `${CLAUDE_PLUGIN_ROOT}/docs/leidbeiningar.html` sem artifact (sjálfstæð síða, óbreytt) og segðu í einni setningu hvað er þar. Ef beðið er um skills („hvaða skills fylgja“): birtu `${CLAUDE_PLUGIN_ROOT}/docs/skills.html` á sama hátt. Ef báðar eru birtar, skiptu `skills.html`/`leidbeiningar.html`-tenglunum út fyrir slóðir artifactanna.

## 0b. Vinna áfram og bæta við (þegar notandi velur „+“ í miðstöð)

- Breyting: finndu artifactið (sama samtal: sama skrá; annars `Artifact list` og `read`), byggðu á núverandi útgáfu, birtu á sömu slóð og segðu í einni setningu hvað breyttist.
- **Bæta við mælaborði** (beiðni sem miðstöðin afritaði, t.d. „Bættu *Verk og útboð* við Bifröst-miðstöðina fyrir <félag>“):
  1. Finndu miðstöðina (`Artifact list`/`read`) og `dataset.json` ef það er til í lotunni; annars sæktu gögnin aftur (aðeins það sem mælaborðið þarf).
  2. Notaðu **skillið sem á við**: `framlegd`, `spagerd`, `endurskodun`, eða `sermaelabord` fyrir sérmælaborð (pakkinn úr `pakkar.json`).
  3. Birtu nýja mælaborðið sem **nýtt artifact** með leiðarstiku á miðstöðina.
  4. **Uppfærðu miðstöðina á sömu slóð**: nýtt spjald undir „Mælaborðin þín“ og merktu það „Þegar bætt við“ í glugganum (merkt „Bætt við · Opna“).
  5. Ein lína í spjall: hvað var búið til og að það sé komið í miðstöðina.
- Eigið mælaborð („laun eftir deildum“): fylgdu `bifrost-maelabord`, reglur 1.0, og bættu því við miðstöðina.

## 1. Upphaf

1. Sýndu félögin (`Context_Companies_List`) og spyrðu: **„Eitt félag eða samstæða?“** Samstæða: félög og eignarhlutur (sjálfgefið 100%), sjá `bifrost-gogn` kafla 1b og 7.
2. **Flokkun (fljótleg, áður en keyrslan fer af stað):** keyrðu kafla 1 í `sermaelabord` (ÍSAT + talningar í BC, nokkrar sekúndur).
3. **Bjóddu aukamælaborð** í einni spurningu með fjölvali (valgluggi, ekki texti), með tillögurnar efst:
   - *Tillögur fyrir þitt félag:* 1–3 sérmælaborð úr flokkuninni, hvert með stuttri ástæðu (t.d. „Verk og útboð — 15 verk og 51 verkbókarfærsla“).
   - *Önnur:* Framlegð og verk · Spágerð · Endurskoðun og ársreikningur.
   - *Ekkert aukalega* (sjálfgefið). Segðu að hvert aukamælaborð bæti við um 3–5 mínútum og að alltaf megi bæta við síðar úr miðstöðinni.
4. Ein lína: „Ég sæki gögnin einu sinni og bý til miðstöð, sex mælaborð og þau sem þú valdir. Fyrsta birtist eftir nokkrar mínútur.“
5. **Hraðfasi:** sæktu fyrst það sem Stjórn þarf (rekstur 24 mán., efnahagur, aldur krafna) og birtu Stjórn. Sæktu svo restina (bankar, lánardrottnar, færslur kostnaðar, verk, áætlanir).

## 2. Mælaborðin

| # | Skill | Sjálfgefið | Á við ef |
|---|---|---|---|
| 1 | `stjorn` | já | alltaf |
| 2 | `sjodstreymi` | já | alltaf |
| 3 | `kostnadur` | já | alltaf |
| 4 | `manadarlok` | já | alltaf |
| 5 | `tekjur` (flipinn Tekjuleki fylgir `tekjuleki`) | já | alltaf; segðu hve stór hluti tekna er á viðskiptamannabók |
| 6 | `sjalfvirkni` | já | alltaf, síðast (notar niðurstöður hinna); keyrsla læst |
| + | `framlegd` | val | vörur, verk eða þjónusta |
| + | `spagerd` | val | ≥ 6 fullbókaðir mánuðir |
| + | `endurskodun` | val | alltaf (sérstaklega fyrir árslok) |
| + | `sermaelabord` | tillaga | eftir flokkun (ÍSAT + notkun í BC); efstu 1–3 sýndar sem tillögur |

## 3. Smíði og röð

1. **Miðstöðin fyrst**, með tómum spjöldum („í smíðum“), til að fá slóð hennar.
2. Stjórn → Sjóðstreymi og bankar → Tekjur → Kostnaður → Mánaðarlok → valin aukamælaborð → Sjálfvirknivæðing. Hvert með leiðarstiku á miðstöðina.
3. Eftir hvert: ein lína („Stjórn tilbúin (1/6). Næst: sjóðstreymi, um 3 mín.“) og **uppfærðu miðstöðina** með lykiltölu og slóð.
4. Skráðu lykiltölu og eina setningu úr hverju fyrir miðstöðina og „síðustu greiningu“ fyrir Sjálfvirknivæðingu.

## 4. Miðstöðin

- Haus: félag, staða (dagsetning), útgáfa.
- Hero í fullri breidd: heildarmynd í einni setningu og fjórar tölur.
- **„Byrjaðu hér“:** 3–5 brýnustu atriðin úr öllum mælaborðunum, raðað eftir áhrifum, með uppruna.
- **Mælaborðin þín:** spjald á hvert (heiti, flipar, lykiltala, setning, merki, `data-nav`-tengill).
- **Mælaborðin þín:** sex sjálfgefin og þau aukamælaborð sem valin voru, sama spjaldaútlit (aukamælaborð merkt „valið“). **Engar tillögur á forsíðunni.**
- Síðasta spjaldið: **„+ Fleiri mælaborð“** (stórt, með brotalínu) og „+“-hnappur við fyrirsögnina; báðir opna sama gluggann.
- **Glugginn „Fleiri mælaborð“:** efst *Tillögur fyrir þitt félag* (úr `sermaelabord`, með ástæðu), svo *Þegar bætt við* (Opna), *Fyrir aðrar atvinnugreinar* og *Annað* (eigið mælaborð), með leit. Hnappurinn heitir **„Afrita skipun“**, því síðan getur hvorki ræst Claude né búið til mælaborð sjálf: hún afritar skipunina, notandinn límir hana í Claude, og Claude fylgir kafla 0b, smíðar mælaborðið og uppfærir miðstöðina á sömu slóð.
- Fótur: heimild, dagsetning og gervigreindarmerking.

## 5. Í lokin

Eitt svar, þrjár til fjórar línur: hve mörg mælaborð, aðalniðurstaðan í krónum, hvar á að byrja, og að fleiri megi bæta við með hnappnum. Bjóddu að uppfæra mánaðarlega (áætlað verkefni).
