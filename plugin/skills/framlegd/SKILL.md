---
name: framlegd
description: "Mælaborðið „Framlegð og verk“ í Bifröst-mælaborðum (Yfirsýn, Verk, Vörur og ABC, Herming), smíðað úr föstu sniðmáti. Notaðu AÐEINS innan Bifröst-mælaborða: þegar notandinn biður um Bifröst-mælaborð eða þetta mælaborð með nafni, eða breytir mælaborði sem pluginið bjó til. Ekki fyrir almennar spurningar um rekstur eða Business Central, aðrar skýrslur, skjöl eða artifacts."
---

# Framlegð og verk

> **Fast sniðmát.** Þetta mælaborð er smíðað úr `template/` (sjá `bifrost-maelabord`, *Föst sniðmát*). Skrifaðu ekki HTML. Safnaðu gögnunum eftir `template/schema.md` (sýnidæmi: `template/example.json`), og smíðaðu með `render.py --dashboard framlegd` eða `bundle.py`. Við breytingu eða uppfærslu er **aðeins þetta mælaborð** endurgert og birt (og viðbætur þess í `ext/`), sjá *Umfang breytinga*. Lýsingin hér að neðan segir hvað sniðmátið sýnir og hvaðan gögnin koma.

**Valmælaborð** (ekki sjálfgefið í 1.0; bætt við úr miðstöð eða að beiðni).

Svarar: **Hvar verður framlegðin til, hvar lekur hún, hvernig standa verkin, og hvað gerist ef verð eða kostnaður breytist?**

Fylgdu `bifrost-maelabord` (útlit, gæði) og `bifrost-gogn` (gögn). Aðeins lesið úr BC.

Sameinar fyrri mælaborðin *Framlegð* og *Vörur og þjónusta*. **Óreikningsfært á verkum er ekki hér** heldur í `tekjuleki`; vísaðu þangað með tengli (`data-nav`) í Yfirsýn og Verk. Reikningsfært umfram framvindu er hins vegar áhætta og á heima hér.

## 1. Gögn og sýn eftir starfsemi

**Gögn: samtölur fyrst** (`bifrost-gogn`, kafli 0). Upphæðir á viðskiptavin, birgi, lykil, verk og vöru koma sem samtölur úr BC (`Data.Totals.Get`, `period_breakdown`, `aging`); færslur eru aðeins sóttar fyrir drill-down á stærstu liðina og athuganir sem þurfa færsluna sjálfa.

`dataset.json` úr `bifrost-gogn` (tekjur og vörunotkun á mánuði, `profile`). Veldu sýn:

| Starfsemi | Gögn |
|---|---|
| Verk (`jobs` > 0) | `Job`, `Job Task`, `Job Planning Line` sem færslur; **notkun og sala á verk sem samtölur**: `Data.Totals.Get` á `Job Ledger Entry` (`[9,13,15]`, `groupBy` `Job No.`, eitt kall með `Entry Type=CONST(Usage)` og eitt með `Sale`); tímar, kostnaður og verð á forða sem FlowFields á `Resource` (44–46 með `Date Filter`), sýnt með kóða en ekki nafni. Sala og birgðir á vöru sem FlowFields á `Item` (72, 78, 68). Framlegð á verk = reikningsfært/reikningshæft − kostnaður; framlegð við verklok = samningur − áætlaður heildarkostnaður |
| Vörur (`items` > 0) | `Item`; sala, kostnaður og magn á vöru sem samtölur úr `Value Entry` (`groupBy` `Item No.`, eitt kall á tímabil); birgðir á vöru úr `Item Ledger Entry` (`Remaining Quantity`, `groupBy` `Item No.`). Sjá *Vörusala* hér að neðan |
| Hvorugt | Tekjur eftir tekjulykli og viðskiptamanni (samtölur úr `Cust. Ledger Entry`); framlegð á tekjustoð |

**Vörusala (verslun, heildsala), samtölur fyrst.** Fylltu valfrjálsu lyklana í `schema.md` (*Valfrjálst*), öll köll fyrir fullbókuðu mánuðina (`Posting Date` jan..síðasti fullbókaði):
1. Heild: `Data.Totals.Get` á `Value Entry` (`Item Ledger Entry Type`=Sale), summa `Sales Amount (Actual)`, `Cost Amount (Actual)` og `Discount Amount`, án groupBy → `item_totals` og `disc`. Stemmdu við tekjur og vörunotkun í `months` (munur = sala utan birgðakerfis, t.d. þjónusta eða dagbókarfærslur; segðu frá honum í `js.quality`).
2. Á vöru: sama kall með `groupBy` `Item No.` → `items[].sales`/`cogs`. Taktu söluhæstu vörurnar (t.d. 50–200) í `items`; fjöldi hópa fer í `item_totals.n`.
3. Á vöruflokk: leggðu samtölur á vöru saman eftir `Item."Item Category Code"` (spjöld lesin með síu á þær vörur, ekki færslur) → `item_groups` (allar vörur, ekki aðeins þær söluhæstu).
4. Á staðsetningu: `groupBy` `Location Code`, eða `Global Dimension 1/2 Code` ef verslanir eru vídd → `stores`.
5. Birgðavirði: `Value Entry` til stöðudags, summa `Cost Amount (Actual)` + `Cost Amount (Expected)`, `groupBy` `Item No.` (og `Location Code` fyrir `stores[].stock_value`); `birgdir` = staða birgðalykla í fjárhag.
6. Hægfara vörur: aðeins fyrir vörur með birgðir, síðasti `Posting Date` sölu úr `Item Ledger Entry` (Sale, `groupBy` `Item No.`, hámark dagsetningar ef tólið styður það; annars ein færsla á vöru, nýjasta fyrst) → `items[].last_sale`.

Kassasala á einn staðgreiðsluviðskiptamann gerir ABC á viðskiptavin lítils virði; þá er ABC á vörur sjálfgefin vídd (gerist sjálfkrafa þegar `items[].sales` er til).

Félag með bæði verk og vörur fær báða flipana. Segðu í haus hvaða sýn er notuð. Ef sölu- og kostnaðarlínur vantar á einingastigi: segðu það og sýndu framlegð á heildarstigi.

## 2. Flipar (mest fjórir, eftir gögnum)

Yfirsýn · Verk (aðeins ef `jobs` er ekki tómt) · Vörur og ABC · Herming. Gæði gagna er spjald neðst á Yfirsýn. Án verka hverfa verkmælar, Staða verka, ABC-víddin Verk og atriði merkt `"job"` í áhættum og gæðum gagna.

**Yfirsýn**
- Hero í fullri breidd: framlegð og framlegðarhlutfall, rofi *með / án einskiptisliða*.
- Lykilmælar: framlegð, framlegðarhlutfall, framlag eftir laun, samningsvirði opinna verka (án verka: birgðir á kostnaðarverði og birgðadagar, eða aðeins þrír mælar ef engar birgðir eru).
- Staða verka sem staflasúla (á áætlun / athygli / á eftir), helstu áhættur, framlegðarhlutfall á mánuði á móti fyrra ári, brú.
- Lína: „Óreikningsfært á verkum: sjá Tekjuleka →“.

**Verk** (eða **Vörur** / **Þjónustulínur** eftir sýn)
- **Ein tafla á verk** með framvindu (kostnaður og tímar á móti áætlun, hlutfall liðins tíma sem súla með merki), samningi, framlegð við verklok í kr. og %, og athugasemd. Sama talan fyrir hvert verk alls staðar á síðunni.
- Tímalína (gantt) með merki við daginn í dag, framlegð á verk, „Þarf athygli“ (t.d. reikningsfært umfram framvindu, framlegð sem fellur), framlegð vinnu eftir deild eða forða (kóðar, ekki nöfn).

**Viðskiptavinir** eru í `tekjur`; hér er aðeins tengill „Viðskiptavinir: sjá Tekjur“.

**Vörur og ABC**
- ABC/Pareto (vörur, vöruflokkar, viðskiptavinir eða verk, eftir því hvaða gögn eru til) með mörkum við 80% og 95%.
- Vörutafla með álagningu, leit og röðun; vörur **undir kostnaðarverði** og framlegð sem fellur merktar.
- Með vörusölu: framlegð eftir vöruflokki, vörutafla með raunsölu, hægfara vörur (engin sala í 90/180 daga) og bundið fé, framlegð eftir staðsetningu ef `stores` er til. Án vörusölu: álagning í verðskrá.

**Herming**
- Stikur: verð (±%), afsláttur (pp), magn (±%), kostnaðarverð aðfanga (±%), yfirfærsla kostnaðarhækkunar í verð. Skýringartextar miðast við gögnin: „verðskrá vinnu og efnis“ og „verk“ aðeins ef verk eða forðar eru til, annars söluverð og selt magn; veittur afsláttur aðeins ef `disc` er gefið.
- Sviðsmyndir: *Grunnur · Kostnaður +5% · Verðhækkun +3% · Afsláttur 2 pp*. Niðurstöðusetning: „Til að halda X% framlegð þarf verð að hækka um Y%.“

**Gæði gagna** (spjald neðst á Yfirsýn)
- Sala bókuð á verk eða ekki, sala bókuð með dagbók í stað sölureikninga, tímar í safnfærslum, opin verk eftir lokadag, VÍV ekki reiknað, ófullbókaðir mánuðir.

## 3. Sannreyning

- Heildarframlegð stemmir við tekjur − vörunotkun í `dataset.json` (eða skýrðu muninn, t.d. birgðabreytingar).
- Samningsvirði og kostnaður verka stemma við verkfærslur; engin eining tvítalin milli flokka.
- Birgðir í kr. stemma við birgðalykla í efnahag.

## Samstæða

- Félagsval efst. Starfsemisgreining er gerð á hvert félag, svo flipar geta verið ólíkir eftir félagi. Í samstæðusýn eru aðeins sameiginlegir mælikvarðar (sala, framlegð, ABC) og dálkurinn *Félag*.
- Framlegð samstæðu reiknast eftir jöfnun innbyrðis sölu og innkaupa (`eliminations.json`, tegund `rekstur`).
- Hermirinn getur beinst að einu félagi eða öllum.
