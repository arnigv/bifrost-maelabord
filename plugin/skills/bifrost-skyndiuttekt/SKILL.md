---
name: bifrost-skyndiuttekt
description: "Ræsir Bifröst-mælaborða: kynning, val á félagi eða samstæðu, sérmælaborð eftir ÍSAT og smíði miðstöðvar með níu mælaborðum í einu artifacti. Notaðu þegar notandinn skrifar /maelabord, biður um að setja upp Bifröst-mælaborðin (t.d. „settu upp Bifröst-mælaborðin“, „set up the Bifröst dashboards“), spyr hvað Bifröst-mælaborð pluginið gerir eða hvaða mælaborð eru í því, eða vill bæta mælaborði við Bifröst-miðstöðina. Ekki fyrir almennar fjármálaspurningar, yfirlit eða skýrslur sem nefna ekki mælaborðin."
---

# Bifröst skyndiúttekt (ræsir) · útgáfa 1.0

Markmið: notandinn sér **fyrsta mælaborðið innan 10 mínútna** og öll níu sjálfgefnu innan um 35–40 mínútna, tengd í einni miðstöð. Sérmælaborð eftir atvinnugrein bætast við að vali.

Fylgdu `bifrost-maelabord` (útlit, reglur 1.0) og `bifrost-gogn` (gögn). **Aðeins lesið úr BC.**

## Ræsing

- **`/maelabord`** og **„Settu upp Bifröst-mælaborðin“** ræsa þetta skill frá kafla 0. Það er líka það sem leiðbeiningarnar segja notendum að skrifa fyrst.
- Beiðni sem nefnir ekki mælaborðin (t.d. almenn spurning um sjóðstreymi eða rekstur) er **ekki** ræsing: svaraðu henni eins og venjulega, án þessa plugins. Ef óljóst er hvort notandinn vill mælaborð má bjóða það í einni línu, en ekki byrja uppsetningu án þess að hann biðji um hana.

## 0. Kynning (alltaf fyrst, áður en gögn eru sótt)

Sendu þessa kynningu í spjallið (ekki artifact), á íslensku. Slepptu henni ef notandinn hefur séð hana í samtalinu.

> **Bifröst mælaborð: níu mælaborð og miðstöð úr Business Central**
>
> | # | Mælaborð | Flipar | Svarar |
> |---|---|---|---|
> | 1 | Stjórn | Yfirsýn · Rekstur · Efnahagur og sjóðstreymi · Áhættur | Er reksturinn á réttri leið, á móti fyrra ári, áætlun og spá? |
> | 2 | Sjóðstreymi og bankar | Staða í bönkum · 13 vikna spá · Innheimta | Hver er staðan í bönkum og eigum við fyrir næstu 13 vikum? |
> | 3 | Tekjur | Yfirsýn · Viðskiptavinir · Vörur og þjónusta · Tekjuleki | Hvaðan koma tekjurnar (niður í reikninga) og hvaða tekjur erum við að missa af? |
> | 4 | Kostnaður | Samþykkt reikninga · Birgjar og kostnaðarliðir | Hvað bíður samþykkis, hvert fer kostnaðurinn (niður í færslur)? |
> | 5 | Mánaðarlok og afstemmingar | Lokun mánaðar · Afstemmingar · Opin atriði | Er mánuðurinn lokaður og stemmir bókhaldið? |
> | 6 | Framlegð og verk | Yfirsýn · Verk · Vörur og ABC · Herming | Hvar verður framlegðin til og hvar lekur hún? |
> | 7 | Spágerð | Spá · Forsendur · Raun vs spá · Rekstrarhermir | Hvar endar árið og hvað ef forsendur breytast? |
> | 8 | Endurskoðun og ársreikningur | Stærðarflokkur · Ársreikningur · Undirbúningur · Færsluprófanir | Hvað þarf fyrir ársreikning og endurskoðanda? |
> | 9 | Sjálfvirknivæðing | Yfirlit · Erindrekar · Handverk · Dagatal og saga | Hvaða verk má fela erindrekum og hvenær? (Keyrsla læst þar til virkjað með ráðgjafa.) |
> | ★ | Miðstöð | — | Öll mælaborðin á einum stað, í einu artifacti: í síma er farið á milli þeirra án þess að fara úr Claude-appinu. |
>
> **Sérmælaborð eftir atvinnugrein:** áður en keyrslan hefst mæli ég með 1–3 pökkum sem passa félaginu (eftir ÍSAT-flokkun og því sem er í notkun í BC) og þú getur líka valið úr öllum 12 (t.d. Verk og útboð, Birgðir og lager, Áskriftartekjur, Leigusafn, Samstæða) eða bætt við þínu eigin síðar.
>
> **Áður en þú byrjar:**
> - **Tími:** fyrsta mælaborðið birtist eftir um 5–10 mínútur, öll níu eftir um 35–40 mínútur, og hvert sérmælaborð bætir við um 3–5 mínútum. Þú getur skoðað hvert um leið og það birtist.
> - **Leyfisgluggar:** Claude biður um leyfi til að lesa úr Bifröst. Veldu **Always allow** fyrir Bifröst svo keyrslan stöðvist ekki. Aðeins er lesið, ekkert skrifað.
> - **Umhverfi:** ef þú ert beðin(n) að velja BC-umhverfi, veldu **Production** (raunveruleg gögn) nema þú sért að prófa; prófunarumhverfi heita oft *Sandbox*, *UAT* eða *Test*.
> - Öll mælaborðin virka fyrir **eitt félag** eða **samstæðu**.
>
> **Þú getur unnið þau áfram:** „bættu við flipa fyrir laun eftir deildum“, „berðu saman Q3 í ár og í fyrra“, „gerðu sama fyrir hitt félagið“, „uppfærðu tölurnar“. Breytingar birtast á sömu slóð.

> **Leiðbeiningar og góð ráð:** heil síða um uppsetningu, fyrstu keyrslu, sýnidæmi, skipanir og sjálfvirknivæðingu fylgir pluginu. Segðu „sýndu leiðbeiningarnar“.

Spyrðu svo með vali (ein spurning):
- **Öll níu** (mælt með)
- **Aðeins nokkur** — *veldu úr töflunni hér að ofan, t.d. „1, 2 og 5“*
- **Bara kynning, ekki núna**

Ef notandi velur „Aðeins nokkur“: sýndu strax valglugga (fjölval) með heitum mælaborðanna níu, ekki bara texta. Sjálfvirknivæðing er alltaf síðust (nr. 9).

## 0a. Leiðbeiningar

Ef notandi biður um leiðbeiningar, góð ráð eða „hvernig virkar þetta“: birtu `${CLAUDE_PLUGIN_ROOT}/docs/leidbeiningar.html` sem artifact (sjálfstæð síða, óbreytt) og segðu í einni setningu hvað er þar. Ef beðið er um skills („hvaða skills fylgja“): birtu `${CLAUDE_PLUGIN_ROOT}/docs/skills.html` á sama hátt. Ef báðar eru birtar, skiptu `skills.html`/`leidbeiningar.html`-tenglunum út fyrir slóðir artifactanna.

## 0b. Vinna áfram og bæta við (þegar notandi velur „+“ í miðstöð)

- **Breyting eða uppfærsla á einu mælaborði:** fylgdu *Umfang breytinga* í `bifrost-maelabord`. Lestu `manifest.json` og `data/` úr miðstöðvar-artifactinu, smíðaðu aðeins þá síðu og birtu aðeins skrárnar sem breyttust. Önnur mælaborð, miðstöðin og Sjálfvirknivæðing eru látin óhreyfð nema beðið sé um annað.
- **Þetta skill (uppsetningin) keyrir ekki aftur** við beiðni um breytingu; aðeins við „settu upp aftur“ eða nýtt félag.
- **Bæta við mælaborði** (beiðni sem miðstöðin afritaði, t.d. „Bættu *Verk og útboð* við Bifröst-miðstöðina fyrir <félag>“):
  1. Finndu miðstöðina (`Artifact list`/`read`) og `dataset.json` ef það er til í lotunni; annars sæktu gögnin aftur (aðeins það sem mælaborðið þarf).
  2. Notaðu **skillið sem á við**: `framlegd`, `spagerd`, `endurskodun`, eða `sermaelabord` fyrir sérmælaborð (pakkinn úr `pakkar.json`).
  3. Bættu nýja mælaborðinu við **miðstöðvar-artifactið** sem nýrri skrá (föst mælaborð með `render.py`; sérmælaborð frá `assets/template.html`) (`ser-<id>.html` eða `<heiti>.html`) með afstæðri leiðarstiku (`index.html`).
  4. **Uppfærðu miðstöðina í sömu birtingu** (bættu spjaldi í `hub.json` og keyrðu `render_hub.py`): nýtt spjald undir „Mælaborðin þín“ (á undan Sjálfvirknivæðingu, sem er alltaf síðust) og merktu það „Þegar bætt við“ í glugganum.
  5. Ein lína í spjall: hvað var búið til og að það sé komið í miðstöðina.
- Eigið mælaborð („laun eftir deildum“): fylgdu `bifrost-maelabord`, reglur 1.0, og bættu því við miðstöðina.

## 1. Upphaf

1. Sýndu félögin (`Context_Companies_List`) og spyrðu: **„Eitt félag eða samstæða?“** Samstæða: félög og eignarhlutur (sjálfgefið 100%), sjá `bifrost-gogn` kafla 1b og 7.
2. **Flokkun (fljótleg, áður en keyrslan fer af stað):** keyrðu kafla 1 í `sermaelabord` (ÍSAT + talningar í BC, nokkrar sekúndur).
3. **Sérmælaborð eftir atvinnugrein** — tvær spurningar í sama valglugga (`AskUserQuestion`, fjölval), ekki texti:
   - **„Mælt með fyrir þitt félag“:** 1–3 pakkar úr flokkuninni, hver merktur *(mælt með)* með stuttri ástæðu (t.d. „Verk og útboð — 15 verk og 51 verkbókarfærsla“). Sjálfgefið: allir sem mælt er með. Síðasti valkostur: *Ekkert sérmælaborð*.
   - **„Aðrir atvinnugreinapakkar“:** hinir af 12 pökkum `pakkar.json` (heiti og eitt dæmi um félag). AskUserQuestion tekur 2–4 valkosti: sýndu þá 3 sem næst koma í flokkuninni og *Sýna alla* (þá lista í næstu spurningu, í hópum). Sjálfgefið: enginn.
   Segðu að hvert sérmælaborð bæti við um 3–5 mínútum og að alltaf megi bæta við síðar úr miðstöðinni.
   *Dæmi (DT Vélsmiðjan):* mælt með **Verk og útboð**, **Samstæða** og **Nýting og reikningsfærsla**; aðrir pakkar til vals.
4. Ein lína: „Ég sæki gögnin einu sinni og bý til miðstöð með níu mælaborðum og þeim sérmælaborðum sem þú valdir. Fyrsta birtist eftir nokkrar mínútur.“
5. **Hraðfasi:** sæktu fyrst það sem Stjórn þarf (rekstur 24 mán., efnahagur, aldur krafna) og birtu Stjórn. Sæktu svo restina (bankar, lánardrottnar, færslur kostnaðar, verk, áætlanir).

## 2. Mælaborðin

| # | Skill | Sjálfgefið | Á við ef |
|---|---|---|---|
| 1 | `stjorn` | já | alltaf |
| 2 | `sjodstreymi` | já | alltaf |
| 3 | `kostnadur` | já | alltaf |
| 4 | `manadarlok` | já | alltaf |
| 5 | `tekjur` (flipinn Tekjuleki fylgir `tekjuleki`) | já | alltaf; segðu hve stór hluti tekna er á viðskiptamannabók |
| 6 | `framlegd` | já | alltaf; sýn eftir starfsemi (verk, vörur eða þjónusta) |
| 7 | `spagerd` | já | alltaf; færri en 6 fullbókaðir mánuðir: segðu að óvissan sé meiri |
| 8 | `endurskodun` | já | alltaf |
| 9 | `sjalfvirkni` | já | alltaf, **síðast** (notar niðurstöður hinna); keyrsla læst |
| + | `sermaelabord` | mælt með / val | eftir flokkun (ÍSAT + notkun í BC): 1–3 mælt með, allir 12 til vals |

## 3. Smíði og röð

**Allar síður eru smíðaðar úr föstum sniðmátum** (`bifrost-maelabord`, *Föst sniðmát*): fyrir hvert mælaborð skilarðu `<skill>.json` eftir `template/schema.md`, miðstöðin er `hub.json` (`template/schema.md` í þessu skilli). Smíði og prófun:

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/bifrost-maelabord/scripts/bundle.py --hub hub.json --data stjorn=stjorn.json [--data …] --out build/
node ${CLAUDE_PLUGIN_ROOT}/skills/bifrost-maelabord/scripts/test/runtest.js build/<síða>.html
```
Birtu miðstöðina fyrst (með þeim spjöldum sem eru tilbúin, hin merkt „í smíðum“ í `note`), og svo aftur á sömu slóð eftir hvert mælaborð, með nýju skránni í `files`. `bundle.py` vistar `data/*.json` og `manifest.json` með síðunum; birtu þær líka (þær gera síðari breytingar á einu mælaborði mögulegar án þess að sækja allt aftur). Gefðu `--automation-url` þegar Sjálfvirknivæðing hefur fengið slóð.


1. **Miðstöðin fyrst**, með tómum spjöldum („í smíðum“), til að fá slóð hennar.
2. Stjórn → Sjóðstreymi og bankar → Tekjur → Kostnaður → Mánaðarlok → Framlegð og verk → Spágerð → Endurskoðun → valin sérmælaborð → Sjálfvirknivæðing (alltaf nr. 9 í miðstöðinni). Hvert með leiðarstiku á miðstöðina.
3. Eftir hvert: ein lína („Stjórn tilbúin (1/9). Næst: sjóðstreymi, um 3 mín.“) og **uppfærðu miðstöðina** með lykiltölu.

**Eitt artifact, margar síður (svo notandi haldist í Claude-appinu).** Tenglar á annað artifact opnast í vafra í síma. Því eru miðstöðin og mælaborðin birt sem **eitt fjölsíðu-artifact**:
- Miðstöðin er síðan sjálf (`file_path`), hvert mælaborð er sér skrá í `files`: `stjorn.html`, `sjodstreymi.html`, `tekjur.html`, `kostnadur.html`, `manadarlok.html`, `framlegd.html`, `spagerd.html`, `endurskodun.html`, og sérmælaborð sem `ser-<id>.html`.
- Hver undirsíða byrjar á `<!doctype html>`, `<meta charset="utf-8">` og `<meta name="viewport" …>` (undirsíður fá ekki beinagrind).
- Tenglar milli síðna eru **afstæðir** (`href="stjorn.html"`, leiðarstika `href="index.html"`), **án** `data-nav`. Þá fer síminn á milli síðna innan sama glugga í appinu.
- Birtu fyrst miðstöðina eina til að fá slóðina; bættu svo hverju mælaborði við **á sömu slóð** (`url` + `files` með nýju skránni; skrár sem ekki eru sendar haldast).
- **Sjálfvirknivæðing** er sér artifact, því hún vistar stillingar sjálf (`artifact`-hæfni). Spjaldið í miðstöðinni vísar á hana með `data-nav`; segðu notandanum að í síma geti sú eina síða opnast í vafra.
4. Skráðu lykiltölu og eina setningu úr hverju fyrir miðstöðina og „síðustu greiningu“ fyrir Sjálfvirknivæðingu.

## 4. Miðstöðin

- Haus: félag, staða (dagsetning), útgáfa.
- Hero í fullri breidd: heildarmynd í einni setningu og fjórar tölur.
- **„Byrjaðu hér“:** 3–5 brýnustu atriðin úr öllum mælaborðunum, raðað eftir áhrifum, með uppruna.
- **Mælaborðin þín:** spjald á hvert (heiti, flipar, lykiltala, setning, merki, `data-nav`-tengill).
- **Mælaborðin þín:** níu sjálfgefin, valin sérmælaborð á undan Sjálfvirknivæðingu, sem er alltaf síðust. Spjöld vísa með afstæðum tenglum á undirsíður. **Engar tillögur á forsíðunni.**
- Síðasta spjaldið: **„+ Fleiri mælaborð“** (stórt, með brotalínu) og „+“-hnappur við fyrirsögnina; báðir opna sama gluggann.
- **Glugginn „Fleiri mælaborð“:** efst *Mælt með fyrir þitt félag* (úr `sermaelabord`, með ástæðu), svo *Aðrir atvinnugreinapakkar* (allir 12 að frádregnum þeim sem eru komnir) og *Annað* (eigið mælaborð), með leit. Hnappurinn heitir **„Afrita skipun“**, því síðan getur hvorki ræst Claude né búið til mælaborð sjálf: hún afritar skipunina, notandinn límir hana í Claude, og Claude fylgir kafla 0b, smíðar mælaborðið og uppfærir miðstöðina á sömu slóð.
- Fótur: heimild, dagsetning og gervigreindarmerking.

## 5. Í lokin

Eitt svar, þrjár til fjórar línur: hve mörg mælaborð, aðalniðurstaðan í krónum, hvar á að byrja, og að fleiri megi bæta við með hnappnum. Bjóddu að uppfæra mánaðarlega (áætlað verkefni).
