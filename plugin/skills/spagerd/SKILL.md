---
name: spagerd
description: "Mælaborðið „Spágerð“ í Bifröst-mælaborðum (spá með óvissubili, forsendur með heimildum, raun á móti spá, rekstrarhermir), smíðað úr föstu sniðmáti. Notaðu AÐEINS innan Bifröst-mælaborða: þegar notandinn biður um Bifröst-mælaborð eða þetta mælaborð með nafni, eða breytir mælaborði sem pluginið bjó til. Ekki fyrir almennar spurningar um rekstur eða Business Central, aðrar skýrslur, skjöl eða artifacts."
---

# Spágerð og rekstrarhermir

> **Fast sniðmát.** Þetta mælaborð er smíðað úr `template/` (sjá `bifrost-maelabord`, *Föst sniðmát*). Skrifaðu ekki HTML. Safnaðu gögnunum eftir `template/schema.md` (sýnidæmi: `template/example.json`), og smíðaðu með `render.py --dashboard spagerd` eða `bundle.py`. Við breytingu eða uppfærslu er **aðeins þetta mælaborð** endurgert og birt (og viðbætur þess í `ext/`), sjá *Umfang breytinga*. Lýsingin hér að neðan segir hvað sniðmátið sýnir og hvaðan gögnin koma.

**Valmælaborð** (ekki sjálfgefið í 1.0; bætt við úr miðstöð eða að beiðni).

Svarar: **Hvar endar árið, hversu viss erum við, á hvaða forsendum, og hvað gerist ef þær breytast?**

Fylgdu `bifrost-maelabord` og `bifrost-gogn`. Aðeins lesið úr BC.

## 1. Gögn

- `dataset.json` með **24–36 mánuðum** svo árstíðir sjáist (keyrðu `bifrost-gogn` fyrir í ár og tvö fyrri ár ef til). Færri en 13 mánuðir: spáin notar ekki árstíðir og segir það.
- Einskiptisliðir (`oneoffs`) eru teknir út úr grunni spárinnar.
- **Þekktar pantanir og verk:** opnar sölupantanir (`Sales Header`/`Sales Line`, tegund pöntun) eftir afhendingarmánuði, og eftirstöðvar samningsvirðis verka (`Job Planning Line`, reikningshæft ekki reikningsfært) eftir áætlunardegi. Fara í `thekktar_pantanir`.
- **Stöðugildi:** ef forðar eða launagögn eru til, fjöldi síðustu mánaða; annars notað hlutfall launa.

## 2. Forsendur — sóttar fyrir hverja keyrslu

Byrjaðu á `assets/assumptions.default.json` og **uppfærðu hverja forsendu** með leit (WebSearch) eða tóli áður en spáð er. Skráðu gildi, heimild og dagsetningu.

| Forsenda | Hvaðan | Sjálfgefið 16.10.2026 |
|---|---|---|
| Verðbólga (VNV, 12 mán.) og verðbólguspá | Hagstofa Íslands; Peningamál Seðlabanka | 5,9% (sept. 2026) |
| Stýrivextir og vaxtaferill | Seðlabanki Íslands, yfirlýsing peningastefnunefndar | 8,0% (7.10.2026) |
| Launahækkanir kjarasamninga | Kjarasamningar á almennum markaði 2024–2028 (SA/ASÍ), eða samningar sem eiga við félagið | 3,5% 1.1.2027 |
| Gengi (EUR/ISK o.fl.) fyrir innflutt aðföng | Bifröst `Reference.ExchangeRate.Get` | sótt við keyrslu |
| Eldsneyti | verðþróun eða forsenda notanda | 0% |
| Verðskrá félagsins | notandi (dagsetning og %) | engin breyting |
| Aðfangaverð | notandi / birgjar | engin breyting |
| Stöðugildi | notandi eða saga | óbreytt |

Ef forsenda finnst ekki: notaðu sjálfgefið gildi og merktu það **„óstaðfest“** í mælaborðinu.

## 3. Spálíkanið

Keyrðu `python3 ${CLAUDE_SKILL_DIR}/scripts/forecast.py --data dataset.json --assumptions assumptions.json --out forecast.json`.

Líkanið (útskýranlegt):
- **Tekjur** = grunnstig (meðaltal síðustu 3 fullbókaðra mánaða, án árstíða) × árstíðastuðull × dempuð leitni (hámark ±1,5% á mánuði, demping 0,85) × magnbreyting × verðskrá + þekktar pantanir.
- **Vörunotkun** = tekjur × efnishlutfall síðustu 6 mánaða × aðfangaverð, að frádreginni yfirfærslu í verð.
- **Laun** = grunnlaun × (1 + kjarasamningshækkun frá gildisdegi) × stöðugildi.
- **Húsnæði og annar rekstur** = grunnur × verðbólga (mánaðarleg uppsöfnun).
- **Fjármagnsliðir** = grunnur × (stýrivextir / stýrivextir í grunni).
- **Óvissubil:** P10 / P50 / P90 út frá sveiflu sögunnar, vex með √tíma.
- **Bakprófun:** líkanið metið án síðustu 3 mánaða og borið saman við raun. MAPE er sýnt í mælaborðinu. Ef MAPE á EBITDA er yfir 25%: segðu að spáin sé óviss og af hverju (t.d. sveiflukennd framlegð eða ófullbókaðir mánuðir).

## 4. Flipar

**Spá**
- Hero: áætluð EBITDA ársins (P50) með bilinu P10–P90.
- Lykilmælar: tekjur ársins, EBITDA-hlutfall, hagnaður, breyting frá fyrra ári.
- Lína: raun (heil) → spá (strikuð) með óvissuborða, fyrra ár til samanburðar.
- Niðurstöðusetning: „Árið stefnir í X m.kr. EBITDA (bil Y–Z). Stærsti óvissuþátturinn er …“

**Forsendur**
- Tafla: forsenda, gildi, heimild (hlekkur), dagsetning, staða (*staðfest / óstaðfest / notandi*).
- Bakprófun: MAPE tekna og EBITDA, og graf af spá á móti raun síðustu 3 mánaða.

**Rekstrarhermir**
- Stikur fyrir hverja forsendu (verðskrá, magn, ný gjöld, aðfangaverð og yfirfærsla, kjarasamningar, launaskrið, stöðugildi, verðbólga, eldsneyti, stýrivextir).
- Sviðsmyndir: *Grunnur · Kjarasamningar · Svartsýn · Sókn*, auk *Seðlabankaspá* ef verðbólguspá fannst.
- Lykilmælar (8): tekjur, EBITDA, EBITDA-hlutfall, hagnaður, framlegðarhlutfall, virðisauki á launakrónu, núllpunktur tekna, öryggisbil.
- Gröf: uppsöfnuð EBITDA (lína, bil litað), laun af tekjum, og áhrif hverrar forsendu á hagnað (láréttar súlur út frá miðju).
- Niðurstöðusetning með **verðhækkun sem þarf** til að halda EBITDA-hlutfalli grunns.

## 4b. Vista sem áætlun (valkvætt, skrif)

Notandi getur beðið um að spáin (P50) verði vistuð sem fjárhagsáætlun í BC. Sýndu fyrst hvað verður skrifað (áætlunarheiti, lyklar, mánuðir, samtölur), fáðu skýrt samþykki, og skrifaðu svo með `Finance.BudgetEntry.Set` í nýja áætlun (t.d. `SPA-2027`), aldrei yfir áætlun sem til er. Lestu aftur með `Finance.BudgetEntry.Get` til staðfestingar.

## 5. Sannreyning

- Grunnsviðsmynd hermis (allar stikur á sjálfgefnu) gefur sömu tölur og `forecast.json`.
- Raunmánuðir í línuriti stemma við `dataset.json`.
- Spá er alltaf merkt **spá** og forsendur með heimild neðst. Þetta er ekki fjárfestingar- eða lánaráðgjöf.

## Samstæða

- Spáin er keyrð á hvert félag (`forecast.py` á dataset hvers félags) og lögð saman eftir jöfnun; ekki á samanlögð gögn, því árstíðir og leitni eru ólík milli félaga.
- Hermirinn hefur félagsval: forsendur geta gilt fyrir öll félög eða eitt. Óvissubil samstæðu er reiknað af summu, ekki lagt saman beint.
