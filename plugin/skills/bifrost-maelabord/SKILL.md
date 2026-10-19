---
name: bifrost-maelabord
description: Hönnunarkerfi og gæðareglur fyrir öll Bifröst-mælaborð úr Business Central: grunnpalletta, letur, ljóst og dökkt útlit, farsímaútlit, flipar, gröf, stikur, leiðarstika aftur á miðstöð og „ekkert út fyrir“. Notaðu ALLTAF þegar búið er til eða breytt mælaborði, skýrslu, hermi eða myndrænni framsetningu á BC-gögnum sem artifact, hvort sem það er stjórn, tekjuleki, sjóðstreymi, kostnaður, framlegð og verk, mánaðarlok, spágerð, endurskoðun, sjálfvirknivæðing eða miðstöð. Önnur skill í þessu plugini vísa hingað.
---

# Bifröst mælaborð: hönnunarkerfi og gæðareglur

Markmiðið er að viðskiptavinur sjái **sínar eigin tölur í vönduðu, gagnvirku mælaborði** og fái „wow“ frá fyrstu sýn. Hvert mælaborð á að líta út eins og hluti af einni vöru, svara raunverulegum spurningum stjórnanda og stemma við bókhaldið upp á krónu.

## Vinnuröð (fylgdu henni alltaf)

1. **Gögn fyrst.** Keyrðu `bifrost-gogn` (eða notaðu `dataset.json` sem þegar er til í lotunni). Aldrei teikna áður en tölurnar eru komnar og stemmdar.
2. **Spurningin.** Skrifaðu fyrir þig, í einni línu, hvaða ákvörðun mælaborðið á að styðja og hver aðalniðurstaðan er í krónum.
3. **Form.** Veldu gröf eftir töflunni hér að neðan. Graf sem styður ekki ákvörðun fer út.
4. **Smíði.** Byrjaðu á `assets/template.html`. Settu innihald `assets/theme.css` og `assets/components.js` **inn í síðuna sjálfa** (artifacts leyfa aðeins forskriftir af CDN, ekki eigin skrár). Gögnin fara inn sem `const DATA = {...}`.
5. **Sannreyning.** Keyrðu útreikningana einu sinni (t.d. með node) og berðu lykiltölur saman við `dataset.json` og fjárhaginn. Samtölur verða að stemma.
6. **Útlit.** Taktu eitt skjáskot ef lotan leyfir það, lagaðu það sem sést og birtu svo. Ekki endurtaka endalaust.
7. **Birting.** Birtu sem artifact. Lýstu í einni setningu hvað það sýnir og hver aðalniðurstaðan er.

## Reglur útgáfu 1.0 (einfaldleiki — byggt á prófun notenda)

- **Hámark fjórir flipar** á mælaborð og **hámark fjórir lykilmælar** á flipa. **Engin tala tvisvar** á sama flipa.
- **Hero í fullri breidd**, ein setning og fjórar tölur; næsta kort fyrir neðan, líka í fullri breidd.
- **Eitt tímabilsval** sem öll gröf og töflur á flipanum fylgja; „Bera saman við“ sem einn veljari frekar en sér flipar.
- **Drill-down:** frá lið í lykla og frá lykli í færslur (dagsetning, fylgiskjal, lýsing, mótaðili, fjárhæð) þar sem það á við. Tölurnar koma sem **samtölur úr BC** (`bifrost-gogn`, kafli 0), en drill-down helst óbreytt: allir liðir opnast niður í lykla og færslur. Ef færslur á tímabilinu eru fleiri en 5.000 fylgja færslur stærstu liðanna (80% af upphæð) með, og aðrir liðir sýna samtölu og línuna „Spurðu gervigreindina: *sýndu færslurnar á bak við <liður>*“, svo síðan vaxi ekki endalaust með stærð félagsins.
- **Stjórnarmál í Stjórn**, bókhaldsmál í Mánaðarlokum. Engir rofar sem breyta tölum hljóðlega (t.d. með/án einskiptis): merktu frekar í töflu.
- Efnahagur og sjóðstreymi sem **töflur**, ekki gröf; lykilmælikvarðar ofan á.
- Leiðarstika á miðstöð efst; tengill á annað mælaborð þegar efni á heima þar (t.d. „Afstemmingar: sjá Mánaðarlok“).

## Litaþemu (fjögur) <!-- Fjögur litaþemu -->

Rofinn efst (`BF.themeToggle`) býður **Ljóst** (sjálfgefið), **Dökkt**, **Blátt** og **Jörð**. Ljóst og Dökkt nota Bifröst-áherslur (gull og grænblátt); Blátt notar bláu þrepin úr grunnpallettu (`--blue-*`, `--sci-*`, `--navy`) og Jörð ólífu og ryð (`--olive-*`, `--rust-*`). Útfært með `data-bf` (light/dark) og `data-pal` (bifrost/blue/earth) á `<html>`; forskriftin strax á eftir `<meta charset>` setur bæði. Valið er geymt í `localStorage` (`bf-theme-v5`) og gildir á öllum mælaborðum. Litir eru alltaf sóttir úr táknum (`--s1`…`--s7`, `--brand`, `--hero`), svo öll gröf fylgja þemanu.

## Hönnunarkerfi (v4, grunnpalletta)

- **Sjálfgefið ljóst**, með rofa efst til hægri (`themeToggle`: *○ Ljóst / ● Dökkt*). Settu stutta forskrift strax á eftir `<meta charset>` sem setur `data-bf="light"` á `<html>` (sjá `template.html`) svo síðan blikki ekki dökk. Valið er munað í vafranum. Við skipti eru gröf teiknuð upp á nýtt (rofinn sér um það).
- **Tákn:** aðeins breyturnar í `theme.css`. Engir litir skrifaðir beint og engir litir utan pallettunnar.

### Grunnpalletta (skylda í öllum mælaborðum)

Átta flokkalitir. Hver hefur þriggja þrepa gagnaskala: `-1` dökkt, `-2` miðja, `-3` ljóst.

| Flokkur | Valmynd/merki | Gagnaskali 1 · 2 · 3 | Hlutverk í mælaborði |
|---|---|---|---|
| Gull | `--gold` #D1A730 | #957F41 · #CBAA4C · #E0CA8D | **Aðallitur** (`--brand`), virkur flipi, raun/aðalröð (`--s1`) |
| Grænblár | `--teal` #33796A | #487569 · #87BAAD · #D4E7E2 | Hero-flötur, annar litur (`--brand2`, `--s2`) |
| Vínrauður | `--maroon` #733C4A | #6C3D49 · #B07D87 · #E4D3D6 | Þriðja röð (`--s3`), áhætta í töflum |
| Ólífugrænn | `--olive` #929C4A | #6F743F · #969F55 · #D9DEB8 | **Gott** (`--up`), fjórða röð |
| Ryðrauður | `--rust` #A35A27 | #A55A28 · #D49971 · #F1DECF | **Slæmt** (`--dn`), fimmta röð |
| Appelsínugulur | `--orange` #EA9E2F | — | **Athygli** (`--warn`) |
| Plóma / grár | — | #736A7E · #ABA7B3 · #C6C3CE / #6E6E70 · #969696 · #DCDCDC | Fyrra ár, grunnur, áætlun (`--base`, `--s6`) |
| Blár | `--cyan` #048FC2, `--navy` #00669B | #326FA0 · #80AFD3 · #CCDFEB | Aðeins sem sjöunda gagnaröð (`--s7`), aldrei sem þema |

Reglur:
- **Pörun:** röð í grafi notar þrep úr sama flokki: dökkt þrep fyrir raun, miðju fyrir spá, ljóst fyrir óvissubil eða bakgrunn. Annar flokkur bætist við aðeins þegar önnur vídd kemur inn (t.d. fyrra ár í plómu/gráu).
- Í dökku þema eru `-2` þrepin notuð á línur og súlur (sjást betur), í ljósu þema `-1` þrepin.
- Hero-kort á dökkum grænbláum halla með gullnum áherslum.
- **Letur:** IBM Plex Sans (allt) og IBM Plex Mono (tölur í töflum), með `latin-ext` svo íslenskir stafir (ð, þ, æ, ö) birtist rétt. Google Fonts með varaletri.
- **Stafatafla:** fyrsta lína hverrar síðu er alltaf `<meta charset="utf-8">`. Án hennar brenglast íslenskir stafir í forskoðun og þegar skrá er opnuð beint.
- **Uppbygging síðu:**
  - Efst: merki (upphafsstafir félags í hallalituðum reit), nafn félags, tímabil, og pillur: *þema-rofi · Tengt BC · Staða dags.*
  - Flipar sem pillur (`.tabs`), virkur flipi í hallalit.
  - **Hero-kort** á fyrsta flipa: aðaltalan stór á hallalituðum fleti (`--brand` → `--brand2`), ein setning og 3–4 lykiltölur.
  - **Lykilmælar sem kort** (`.card.kpi`) með smáferli sem hefur hallalit undir línu.
  - Gröf: línur með `tension .4`, hallalitur undir (`BF.grad`), engir ásar, dökkt sprettigluggaspjald, súlur með ávölum hornum.
  - Listar sem kort með tákni (`.d-item`), fjárhæð í pillu.
  - Aldursgreining sem ein lárétt stika skipt í hluta (`.stack`) með skýringum undir.
  - Röðunarlistar með upphafsstöfum í hring og framvindustiku (`.prow`).
- Merkingarlitir (`--up`, `--dn`, `--warn`) aðeins fyrir gott, slæmt og athygli, alltaf með texta.
- **Fótur:** heimild (BC-umhverfi, félag, dagsetning), fyrirvarar, og alltaf: „Unnið með aðstoð gervigreindar. Yfirfarið áður en byggt er á tölunum.“

## Samstæða

Ef `dataset.json` er samstæða (`consolidated: true`):
- Haus sýnir heiti samstæðu og félögin sem hún nær yfir.
- **Félagsval** efst (hnappar eða fellilisti): *Samstæða · Félag 1 · Félag 2 …*. Allir lykilmælar og gröf fylgja valinu. Gögn hvers félags eru í `entities`.
- Á yfirsýn: **framlag hvers félags** (láréttar súlur) til tekna, EBITDA og hagnaðar.
- **Jöfnunarfærslur** sýndar sér (lítil tafla eða brú: *summa félaga → innbyrðis viðskipti → samstæða*), svo tölurnar séu rekjanlegar.
- Hlutdeild minnihluta sýnd sér ef eignarhlutur er undir 100%.
- Ófullbókaður mánuður hjá einu félagi gerir mánuðinn ófullbókaðan í samstæðu. Segðu hjá hvaða félagi.

## Íslenskt snið

- Tölur: `1.234.567` og `1.234,5`. Notaðu `fmt()` úr `components.js`, ekki `toLocaleString` (sumir vafrar hafa ekki `is-IS`).
- Fjárhæðir á mælaborðum í **m.kr.** með einum aukastaf, í töflum í kr. án aukastafa.
- Dagsetningar `16.10.2026`, mánuðir `jan, feb, mar, apr, maí, jún, júl, ágú, sep, okt, nóv, des`, vikan byrjar á mánudegi.
- Formerki á breytingu: `+3,2%`, `−1,4 m.kr.`, `+0,8 pp` fyrir prósentustig.

## Rétt graf fyrir spurninguna

| Spurning | Form | Athugasemd |
|---|---|---|
| Hvernig þróast þetta? | **Lína** | Grunnur strikaður og grár, sviðsmynd/raun heil í áherslulit, bilið litað grænt/rautt (`lineCompare`). |
| Hvað breyttist og af hverju? | **Brú (fossgraf)** | Frá upphafstölu að lokatölu, hver liður sem súla upp/niður (`bridge`). |
| Hvað er stærst? | **Láréttar súlur í HTML** | Raðað, tala hægra megin (`hbars`). Fara aldrei út fyrir. |
| Hvernig skiptist heildin? | Staflað | Aðeins ef hlutarnir mynda raunverulega heild. |
| Hvað þarf athygli? | **Listi með merki** | Alvarleiki, fjárhæð, næsta skref, ábyrgð. |
| Ein tala skiptir mestu | **Lykilmælir** | Stór tala, grunnur, breyting sem flaga og lítill ferill (`kpi`). |

**Bannað:** tvö y-ásar á sama grafi, kökurit með fleiri en 4 sneiðum, regnbogalitir, þrívídd, gröf sem endurtaka sömu tölur og tafla við hliðina, næmni- og núllpunktsgröf sem stjórnandi getur ekki brugðist við.

## Lykilmælar

Veldu mælikvarða sem greinin notar í raun, ekki bara tekjur. Dæmi:

- **Rekstur:** tekjur, EBITDA og EBITDA-hlutfall, hagnaður fyrir skatta, framlegðarhlutfall (tekjur að frádregnum breytilegum kostnaði), laun af tekjum, virðisauki á launakrónu ((tekjur − aðföng) / laun).
- **Sjóður og kröfur:** handbært fé, DSO, gjaldfallið hlutfall krafna, lágpunktur sjóðs næstu 13 vikur.
- **Verk:** framvinda á móti tíma, óreikningsfært, framlegð verks.
- **Vörur:** framlegð eftir vöru, birgðadagar, hægfara vörur.

Hver lykilmælir sýnir **gildi, grunn (fyrra ár eða áætlun), breytingu sem flögu** og helst lítinn feril.

## Flipar, stikur og gagnvirkni

- **Flipar** (`tabs()`) þegar mælaborð hefur fleiri en tvær sjálfstæðar spurningar, t.d. *Yfirsýn · Greining · Sviðsmyndir · Aðgerðir*. Fyrsti flipi er alltaf yfirsýn. Flipi man stöðu í `#hash`.
- **Stikur** þar sem þær breyta niðurstöðu (verð, magn, laun, aðföng, vísitala, eldsneyti, vextir, greiðsluhraði). Hver stika uppfærir lykilmæla og gröf **strax**. Sýndu gildið við stikuna með formerki og lit.
- **Tilbúnar sviðsmyndir** alltaf með stikum: *Grunnur · Kjarasamningar · Svartsýn · Sókn*.
- **Niðurstöðusetning** efst sem uppfærist með stikum, í krónum: „EBITDA lækkar um 19,6 m.kr. Til að halda 21,0% EBITDA-hlutfalli þarf verðskrá vinnu að hækka um 4,2%.“
- **Töflur** með röðun og síum. Langar töflur skrollast innan síns ramma.

## Farsímar (sama mælaborð, lagar sig að skjánum)

Ekkert sér mobile-mælaborð: sama artifact og sama slóð, útlitið breytist undir 640 px. Reglurnar eru í `theme.css` (kaflinn *Farsímar*) og `components.js`; fylgdu þessum merkingum í HTML svo þær virki:

| Í síma | Hvernig |
|---|---|
| Flipar verða **stika neðst á skjánum** | Sjálfvirkt fyrir `.tabs`. Gefðu löngum heitum `data-short` (t.d. `data-short="Efnahagur"` á „Efnahagur og sjóðstreymi“, `data-short="Samþykkt"`). Í mesta lagi 12 stafir; án þess er fyrsta orðið notað ef heitið er lengra en 14 stafir. Flipaskipti skruna efst. |
| Leiðarstika styttist í **← Miðstöð** | `<a …>← Miðstöð<span class="c-l"> mælaborða</span></a>` |
| Litaþema sem **fjórir litaðir punktar** | Sjálfvirkt í `themeToggle`. |
| **Hero:** ein tala og í mesta lagi þrjár línur af texta | Sjálfvirkt; settu aðalniðurstöðuna fremst í setninguna. |
| Lykilmælar **2×2** | Sjálfvirkt fyrir `.kpis` og `.g4`. Hafðu gildi stutt („271,5 m“, ekki „271.512.000 kr.“). |
| Gröf **220 px** há (`.cv-tall`: 300 px), færri ásmerki | Sjálfvirkt fyrir `.cv` með hæð; `lineCompare` og `bridge` lesa `BF.mobile()`. Í eigin Chart.js-gröfum: `maxTicksLimit: BF.mobile() ? 6 : 12`, `pointHitRadius: 14`. Ekkert sem sést aðeins við hover. |
| Töflur: **fastur fyrsti dálkur**, flett til hliðar | Sjálfvirkt inni í `.scroll`. Rekstrarreikningur, efnahagur og mánaðartöflur halda þessu. |
| Listatöflur verða **spjöld** | `class="m-cards"` á töflur með einni línu á hlut (reikningar, birgjar, verk, opin atriði). Dálkaheiti verða merkingar sjálfkrafa. |
| Drill-down og „Fleiri mælaborð“ sem **neðri gluggi** | Notaðu `BF.sheet(titill, html)` fyrir drill-down; `<dialog>` verður neðri gluggi sjálfkrafa. |
| Val (tímabil, félag) **flett til hliðar** | Sjálfvirkt fyrir `.seg`. Fleiri en 5 valkostir: notaðu `<select>`. |
| **Snertisvæði minnst 44 px**, letur í reitum 16 px | Sjálfvirkt á snertiskjá. |
| Fela aukaatriði | `class="m-hide"` (t.d. „Tengt BC“-flaga, aukadálkar); `class="m-only"` fyrir það sem á aðeins við í síma. |

Prófaðu alltaf á **375 px** breidd áður en birt er: ekkert lárétt skrun á síðunni, flipastikan hylur ekki efni neðst, og fyrsta skjámynd sýnir aðalniðurstöðuna.

## Ekkert fer út fyrir (skilyrði fyrir birtingu)

- Ytri rammi: `.wrap{overflow-x:clip}` og hliðarbil 16 px.
- Öll grid- og flex-börn með texta, töflum eða gröfum fá `min-width:0` og dálka sem `minmax(0,1fr)`.
- Chart.js: `responsive:true, maintainAspectRatio:false`, hæð á umbúðum (`.cv`), aldrei á `canvas`. `canvas{max-width:100%}`.
- Töflur inni í `.scroll{overflow-x:auto}`.
- Súlur og stikur í HTML eru reiknaðar sem % af hámarki svo þær fari aldrei yfir 100%.
- Prófaðu við 375 px breidd (sjá *Farsímar*).

## Traust á tölunum

- Allar tölur koma úr `dataset.json` eða beinum BC-köllum í sömu lotu. Aldrei giska.
- **Ófullbókuð tímabil** (t.d. sala en engin laun) eru sýnd dauf og ekki talin með í samtölum, og það er sagt berum orðum.
- **Einskiptisliðir** eru merktir og hægt að sleppa þeim með rofa.
- Hermd gögn eða forsendur eru merkt *Hermt* eða *Forsenda* þar sem þau birtast.
- **Aðeins lesið.** Aldrei skrifa í BC úr mælaborðaskilli. Ef notandi biður um aðgerð (t.d. gefa út reikning), staðfestu fyrst í spjalli.
- Nöfn einstaklinga (t.d. á kortareikningum eða forðum) eru ekki sýnd á mælaborðum sem eiga að fara víðar. Notaðu kóða.

## Gæðalisti fyrir birtingu

- [ ] Aðalniðurstaðan sést í fyrstu sýn, í krónum.
- [ ] Samtölur stemma við fjárhag.
- [ ] Ekkert fer út fyrir ramma; töflur skrollast innan ramma.
- [ ] Ljóst og dökkt þema virka.
- [ ] Virkar á 375 px: flipastika neðst, lykilmælar 2×2, engin lárétt skrun, langir flipar með `data-short`.
- [ ] Íslenskt talna- og dagsetningasnið alls staðar.
- [ ] Ófullbókað og einskipti merkt.
- [ ] Fótur með heimild og gervigreindarmerkingu.

## Skrár

- `assets/theme.css`: tákn, letur, útlit hluta.
- `assets/components.js`: `fmt`, `sg`, `tabs`, `kpi`, `spark`, `hbars`, `lineCompare`, `bridge`, `sortable`, `bindSliders`, `entityPicker` (félagsval í samstæðu), `themeToggle` (fjögur þemu), `grad` (hallalitur í gröfum), `mobile()` (sími?), `sheet()` (drill-down sem neðri gluggi í síma), `cardify()` (töflur sem spjöld; keyrt sjálfkrafa fyrir `table.m-cards`).
- `assets/template.html`: grunnsíða með haus, flipum, lykilmælum, grafi, töflu og fæti.

## Leiðir milli mælaborða

- Þegar mælaborð tilheyrir miðstöð: efst er leiðarstika `← Miðstöð mælaborða / <heiti>` (`.crumb`, sjá `template.html`) með slóð miðstöðvarinnar.
- Spjöld í miðstöðinni og leiðarstikan nota `data-nav` og litla forskrift neðst á síðunni sem opnar í sama flipa ef hægt er, annars í nýjum (sjá `components.js`, neðst).
- Röð við smíði: búðu fyrst til miðstöðina (tóma eða með bráðabirgðatölum) til að fá slóðina, smíðaðu svo mælaborðin með leiðarstiku og uppfærðu loks miðstöðina með lykiltölum og slóðum.
