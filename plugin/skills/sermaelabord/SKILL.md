---
name: sermaelabord
description: Sérmælaborð eftir atvinnugrein (yfirflokkum ÍSAT) úr Business Central — flokkar félagið sjálfkrafa út frá ÍSAT-númeri og því sem er í notkun í BC (verk, tímaskráningar, birgðir, uppskriftir, endurteknir reikningar, eignir og lán, mörg félög) og smíðar sérmælaborð: Verk og útboð, Nýting og reikningsfærsla, Áskriftartekjur, Birgðir og lager, Verslanir og karfa, Nýting og bókanir, Afli afurðir og gengi, Framleiðsla og kostnaðarverð, Leigusafn, Samstæða, Floti og leiðir, Fjárheimildir. Notaðu þegar beðið er um mælaborð fyrir tiltekna atvinnugrein, „tillögur fyrir okkar félag“, „bættu við Verk og útboð“ (eða öðru sérmælaborði), ÍSAT, eða þegar miðstöðin þarf tillögur.
---

# Sérmælaborð eftir yfirflokkum

Svarar: **Hvaða mælikvarðar skipta mestu í þessari atvinnugrein, og hvernig stendur félagið á þeim?**

Fylgdu `bifrost-maelabord` (útlit og reglur 1.0: hámark fjórir flipar og fjórir lykilmælar, drill-down, engin tala tvisvar) og `bifrost-gogn` (gögn). Aðeins lesið úr BC.

## 1. Flokkun (gerð í ræsinum, áður en miðstöðin er smíðuð)

1. **ÍSAT-númer:** úr `Company Information` (atvinnugreinaflokkun ef útfyllt), annars spyrðu notanda eða flettu kennitölu upp í fyrirtækjaskrá Skattsins. Óþekkt: haltu áfram á notkun.
2. **Notkun í BC:** teldu með `data_record_count`: `Job`, `Job Ledger Entry`, `Resource`, `Time Sheet Header`, `Item`, `Item Ledger Entry`, `Production BOM Header`, `Standard Customer Sales Code`, `Location`, `Fixed Asset`; hlutfall fastafjármuna og langtímalána af efnahag úr `dataset.json`; fjöldi félaga í tenant (`Context_Companies_List`) og tengdir aðilar.
3. Keyrðu `python3 ${CLAUDE_SKILL_DIR}/scripts/flokka.py --signals signals.json [--isat NN.NN] --out tillogur.json`. Efstu 1–3 verða **„Tillögur fyrir þitt félag“**: í upphafsvali ræsisins (áður en keyrslan fer af stað) og efst í glugganum „Fleiri mælaborð“ í miðstöðinni, með ástæðu („15 verk og 51 verkbókarfærsla“).
4. Flokkun er tillaga, ekki niðurstaða: notandinn velur.

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
5. Birtu sem nýtt artifact `<Félag> · <Sérmælaborð>` og **uppfærðu miðstöðina**: nýtt spjald í „Mælaborðin þín“, merkt „Þegar bætt við“ í glugganum.

## 4. Sannreyning

- Tölur sem birtast líka í öðrum mælaborðum (tekjur, framlegð, verk) stemma við þau.
- Hvert „vantar gögn“-atriði segir nákvæmlega hvað þarf og hvar í BC.

## Dæmi: DT Vélsmiðjan (október 2026)

ÍSAT ekki skráð í BC. Notkun: 15 verk og 51 verkbókarfærsla, 6 forðar, 16 vörur með litla sölu, engar uppskriftir, 4 félög í tenant. Tillögur: **Verk og útboð** (verktakar; vélsmiðja í verkum), **Samstæða** (DT og Eyjavör eiga viðskipti), **Nýting og reikningsfærsla** (forðar á verkum).
