---
name: sermaelabord
description: "Sérmælaborð eftir atvinnugrein (12 pakkar eftir ÍSAT) í Bifröst-mælaborðum, og flokkun félags fyrir tillögur í miðstöðinni. Notaðu AÐEINS þegar notandinn bætir sérmælaborði við Bifröst-miðstöðina eða ræsirinn þarf tillögur. Ekki fyrir almennar atvinnugreinagreiningar eða önnur verkefni."
---

# Sérmælaborð eftir yfirflokkum

Svarar: **Hvaða mælikvarðar skipta mestu í þessari atvinnugrein, og hvernig stendur félagið á þeim?**

Fylgdu `bifrost-maelabord` (útlit og reglur 1.0: hámark fjórir flipar og fjórir lykilmælar, drill-down, engin tala tvisvar) og `bifrost-gogn` (gögn). Aðeins lesið úr BC.

## 1. Flokkun (gerð í ræsinum, áður en miðstöðin er smíðuð)

1. **ÍSAT-númer:** úr `Company Information` (atvinnugreinaflokkun ef útfyllt), annars spyrðu notanda eða flettu kennitölu upp í fyrirtækjaskrá Skattsins. Óþekkt: haltu áfram á notkun.
2. **Notkun í BC:** teldu með `data_record_count`: `Job`, `Job Ledger Entry`, `Resource`, `Time Sheet Header`, `Item`, `Item Ledger Entry`, `Production BOM Header`, `Standard Customer Sales Code`, `Location`, `Fixed Asset`; hlutfall fastafjármuna og langtímalána af efnahag úr `dataset.json`; fjöldi félaga í tenant (`Context_Companies_List`) og tengdir aðilar.
3. Keyrðu `python3 ${CLAUDE_SKILL_DIR}/scripts/flokka.py --signals signals.json [--isat NN.NN] --out tillogur.json`. Efstu 1–3 verða **„Mælt með fyrir þitt félag“**: í upphafsvali ræsisins (áður en keyrslan fer af stað) og efst í glugganum „Fleiri mælaborð“ í miðstöðinni, með ástæðu („15 verk og 51 verkbókarfærsla“). Allir 12 pakkarnir eru alltaf til vals þar fyrir neðan (*Aðrir atvinnugreinapakkar*).
4. Flokkun er tillaga, ekki niðurstaða: notandinn velur.

Merki fyrir `flokka.py` (sjá haus skriftunnar): `related_companies` eru félög sem félagið á **viðskipti** við (tengdir viðskiptamenn/lánardrottnar), ekki fjöldi félaga í tenant, því sandkassar geyma mörg óskyld félög. Fyrir verslun: `store_dimension`, `pos_customers`, `card_settlement_accounts` og `locations`, svo smásala þekkist líka án ÍSAT.

## 2. Pakkarnir

`assets/pakkar.json` geymir fyrir hvern pakka: yfirflokk, dæmi, heiti mælaborðs, fjóra flipa, lykilmælikvarða, BC-gögn og ÍSAT-forskeyti.

| Yfirflokkur | Sérmælaborð | Lykilmælikvarðar (úrval) |
|---|---|---|
| Verktakar og mannvirkjagerð | Verk og útboð | Vinningshlutfall tilboða, framlegð í tilboði á móti raun, framvinda á móti kostnaði, WIP, aukaverk, geymslufé, verðbætur skv. byggingavísitölu, nýting tækja |
| Sérfræðiþjónusta | Nýting og reikningsfærsla | Reikningshæft hlutfall, raunverð á tíma, óreikningsfærðir og afskrifaðir tímar, tekjur á starfsmann |
| SaaS og hugbúnaður | Áskriftartekjur | MRR/ARR, brottfall, NRR, endurnýjanir 90 daga, frestaðar tekjur |
| Heildsala og innflutningur | Birgðir og lager | Birgðadagar, hægfara vörur, framlegð eftir vöruflokki og birgi, gengisáhrif, vörur í hafi |
| Smásala | Verslanir og karfa | Sala á m² og verslun, meðalkarfa, rýrnun, launahlutfall |
| Ferðaþjónusta og veitingar | Nýting og bókanir | Nýting, ADR, RevPAR, bókunarstaða, fyrirframgreiðslur, gistináttaskattur |
| Sjávarútvegur og fiskvinnsla | Afli, afurðir og gengi | Aflaverðmæti, nýting hráefnis, afurðaverð í EUR/USD, veiðigjöld, gengisnæmni |
| Framleiðsla og iðnaður | Framleiðsla og kostnaðarverð | Kostnaðarverð á einingu, frávik frá uppskrift, sóun, orka |
| Fasteignir og leiga | Leigusafn | Útleiguhlutfall, leigutekjur eftir eign, vísitölutenging, vanskil, veðsetning |
| Eignarhald og samstæður | Samstæða | Innbyrðis viðskipti og jöfnun, arður, lán milli félaga |
| Flutningar og dreifing | Floti og leiðir | Kostnaður á km eða sendingu, eldsneyti, nýting bíla |
| Félagasamtök og opinber rekstur | Fjárheimildir | Raun á móti fjárheimild, samningar, kostnaður á þjónustuþega |

## 3. Smíði sérmælaborðs

1. Lestu pakkann úr `pakkar.json`. Notaðu flipana fjóra og veldu **fjóra lykilmælikvarða** sem gögnin í BC styðja. Mælikvarði sem vantar gögn fyrir (t.d. tilboð sem eru ekki skráð í BC, bókunarkerfi utan BC) fer í kort **„Vantar gögn“** með því hvað þarf að skrá, ekki tilbúin tala.
2. **Samtölur fyrst** (`bifrost-gogn`, kafli 0): t.d. WIP og kostnaður á verk, sala á verslun eða vöruflokk, leigutekjur á eign og kostnaður á bíl sem `Data.Totals.Get` með `groupBy` á viðkomandi reit (verk, vídd, staðsetning, vöruflokkur). Færslur aðeins fyrir drill-down á stærstu liðina.
3. Endurnýttu gögn og útreikninga annarra skilla þar sem þau skarast (verk úr `framlegd`, birgðir úr `framlegd` vörusýn, samstæða úr `bifrost-gogn` kafla 7, áætlanir úr `stjorn`) svo tölur stemmi milli mælaborða.
4. Leiðarstika á miðstöðina, fótur með heimild og gervigreindarmerkingu.
5. Bættu því við **miðstöðvar-artifactið** sem skrá `ser-<id>.html` (afstæð leiðarstika `index.html`, sjá `bifrost-skyndiuttekt`, kafli 3) og **uppfærðu miðstöðina í sömu birtingu**: nýtt spjald í „Mælaborðin þín“ á undan Sjálfvirknivæðingu, merkt „Þegar bætt við“ í glugganum.
6. **Tungumál:** skrifaðu á máli gagnanna (`lang`), settu `BF_LANG` í síðuna og smíðaðu hina útgáfuna sem `ser-<id>.<lang>.html` með rofanum IS | EN (`bifrost-maelabord`, *Tungumál*). Heiti og lýsingar pakka á ensku eru í `pakkar.json` undir `en`.

## 4. Sannreyning

- Tölur sem birtast líka í öðrum mælaborðum (tekjur, framlegð, verk) stemma við þau.
- Hvert „vantar gögn“-atriði segir nákvæmlega hvað þarf og hvar í BC.

## Dæmi: DT Vélsmiðjan (október 2026)

ÍSAT ekki skráð í BC. Notkun: 15 verk og 51 verkbókarfærsla, 6 forðar, 16 vörur með litla sölu, engar uppskriftir, 4 félög í tenant. Tillögur: **Verk og útboð** (verktakar; vélsmiðja í verkum), **Samstæða** (DT og Eyjavör eiga viðskipti), **Nýting og reikningsfærsla** (forðar á verkum).
