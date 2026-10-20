# Bifröst mælaborð

Plugin frá Origo sem býr til vönduð, gagnvirk mælaborð úr Business Central viðskiptavinar í gegnum Bifröst.

**Útgáfa 1.0.0.** Miðstöð og **níu sjálfgefin mælaborð** í einu artifacti (Sjálfvirknivæðing alltaf nr. 9), einfaldari (hámark fjórir flipar og fjórir lykilmælar, engar tvítekningar). Sérmælaborð eftir atvinnugrein eru valin í upphafi (mælt með eftir ÍSAT og starfsemi) eða síðar með **+ Fleiri mælaborð** í miðstöðinni. Byggt á prófun notenda: drill-down í færslur, tímabilsval, stjórnarmál í Stjórn, nýtt mælaborð Mánaðarlok og afstemmingar, og skýrari kynning (tími, leyfisgluggar, umhverfi).

**Við uppsetningu:** skrifaðu t.d. „hvað gerir Bifröst-pluginið?“ eða „settu upp mælaborðin“. Claude sýnir þá töflu yfir öll mælaborðin með skýringum og leiðbeiningum um hvernig má vinna þau áfram (plugin getur ekki sent skilaboð sjálfkrafa við upphleðslu, svo fyrsta skilaboðið ræsir kynninguna).

**Byrjaðu svona:** eftir uppsetningu, skrifaðu `/maelabord` eða „settu upp Bifröst-mælaborðin“. Skillin eru aðeins notuð fyrir Bifröst-mælaborðin; almennar spurningar og önnur verkefni notandans eru óháð pluginu. Ræsirinn spyr hvort þú viljir **eitt félag eða samstæðu**. Ræsirinn sækir gögnin einu sinni, býr til öll mælaborðin sem eiga við og miðstöð sem tengir þau saman.

**Leiðbeiningar:** `docs/leidbeiningar.html` (uppsetning, fyrsta keyrsla, sýnidæmi á Vélsmiðjusamstæðunni, hvert mælaborð og hvað það þýðir, samstæður, skipanir, skills og samhengi, sjálfvirknivæðing, persónuverndarsíur Bifröst) og `docs/skills.html` (öll 14 skills). Báðar má líka hýsa á vefþjóni eða GitHub Pages.

## Innihald

**Sjálfgefin (níu):**

| Skill | Mælaborð | Flipar |
|---|---|---|
| `stjorn` | Stjórn | Yfirsýn (með árspá og óvissubili) · Rekstur (tímabil, samanburður við fyrra ár/áætlun/spá, hvað breyttist mest, lykilhlutföll, drill-down) · Efnahagur og sjóðstreymi · Áhættur |
| `sjodstreymi` | Sjóðstreymi og bankar | Staða í bönkum · 13 vikna spá · Innheimta |
| `kostnadur` | Kostnaður | Samþykkt reikninga · Birgjar og kostnaðarliðir (niður í færslur) |
| `manadarlok` | Mánaðarlok og afstemmingar | Lokun mánaðar · Afstemmingar · Opin atriði |
| `tekjur` | Tekjur | Yfirsýn · Viðskiptavinir (niður í reikninga og línur) · Vörur og þjónusta · Tekjuleki (`tekjuleki`) |
| `framlegd` | Framlegð og verk | Yfirsýn · Verk · Vörur og ABC · Herming |
| `spagerd` | Spágerð | Spá · Forsendur · Raun vs spá · Rekstrarhermir |
| `endurskodun` | Endurskoðun og ársreikningur | Stærðarflokkur · Ársreikningur · Undirbúningur · Færsluprófanir |
| `sjalfvirkni` | Sjálfvirknivæðing (nr. 9) | Yfirlit · Erindrekar · Handverk · Dagatal og saga (keyrsla læst þar til virkjað með ráðgjafa) |

**Sérmælaborð eftir atvinnugrein (`sermaelabord`):** 12 pakkar eftir yfirflokkum ÍSAT (Verk og útboð, Nýting og reikningsfærsla, Áskriftartekjur, Birgðir og lager, Verslanir og karfa, Nýting og bókanir, Afli afurðir og gengi, Framleiðsla og kostnaðarverð, Leigusafn, Samstæða, Floti og leiðir, Fjárheimildir). Félagið er flokkað sjálfkrafa (ÍSAT-númer + hvað er í notkun í BC). Í upphafi, áður en keyrslan fer af stað, er **mælt með** 1–3 pökkum fyrir félagið og hægt að velja hvern sem er af öllum 12. Sama val er efst í glugganum „Fleiri mælaborð“ í miðstöðinni.

**Fleiri mælaborð síðar:** „+“ í miðstöðinni opnar listann; **Afrita skipun** afritar skipunina, límdu hana í Claude og mælaborðið er smíðað (með réttu skilli) og birtist í miðstöðinni.

**Grunnskill:** `bifrost-skyndiuttekt` (ræsir og miðstöð), `bifrost-maelabord` (hönnun og reglur 1.0), `bifrost-gogn` (gögn úr BC, samstæða, áætlanir).

**Litaþemu:** Ljóst, Dökkt, Blátt og Jörð — valið efst á hverju mælaborði og gildir á þeim öllum.

**Samtölur fyrst:** Business Central leggur saman (`Data.Totals.Get`, `period_breakdown`, `aging`); færslur eru aðeins sóttar þar sem færslan sjálf skiptir máli (sjóðspá, færsluprófanir, drill-down á stærstu liðina). Mælaborðin virka því jafnt hjá stórum sem litlum félögum. Sjá `bifrost-gogn`, kafla 0.

**Í síma:** sama mælaborð lagar sig að skjánum (flipar neðst, lykiltölur 2×2, töflur sem spjöld). Miðstöðin og mælaborðin eru eitt fjölsíðu-artifact með afstæðum tenglum, svo farið er á milli þeirra án þess að fara úr Claude-appinu.

**Tími:** fyrsta mælaborð eftir um 5–10 mín., öll níu eftir um 35–40 mín., hvert sérmælaborð +3–5 mín. Veldu **Always allow** fyrir Bifröst í leyfisglugga; aðeins er lesið.

## Kröfur

- Claude (Team eða Enterprise fyrir dreifingu innan fyrirtækis) með Cowork og Skills virkt.
- **Bifröst-tengingin þarf að vera tengd** í Claude hjá viðskiptavininum. Pluginið inniheldur ekki tenginguna sjálfa í þessari útgáfu, sjá `mcp.example.json`.
- Notandi þarf lesaðgang að viðkomandi félagi í Business Central.

## Uppsetning (ZIP)

1. Stjórnandi fer í *Organization settings › Plugins & skills* og velur *Add › Upload a plugin*.
2. Hleður upp `bifrost-maelabord-1.0.0.zip`.
3. Stillir á *Installed by default*.

## Grundvallarreglur

- **Aðeins lesið.** Skillin skrifa aldrei í Business Central.
- **Gögn haldast hjá viðskiptavini.** Mælaborð eru birt í Claude-aðgangi viðskiptavinarins og eru lokuð þar til hann deilir þeim.
- **Gervigreind.** Hvert mælaborð er merkt þannig að það sé unnið með aðstoð gervigreindar og þurfi yfirferð áður en byggt er á því.

## Fyrirvari

Þetta er ekki opinber vara eða þjónusta Origo. Pluginið og leiðbeiningarnar eru birt til stuðnings og eru dæmi um hvernig nýta má Bifröst og Claude með Business Central. Sýnidæmin byggja á tilbúnum prófunargögnum úr Bifröst-sandkassa.

Origo ehf.
