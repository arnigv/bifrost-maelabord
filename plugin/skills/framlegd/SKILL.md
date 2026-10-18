---
name: framlegd
description: Mælaborðið „Framlegð og verk“ úr Business Central — hvar framlegðin verður til og hvar hún lekur, eftir verki, vöru, þjónustu og viðskiptavini, ásamt stöðu og framvindu verka, tímalínu, ABC/Pareto-greiningu, birgðum og hægfara vörum, gæðum verkbókhalds og hermi fyrir verð, afslátt, magn og kostnaðarverð. Lagar sig að starfseminni (verk, vörur eða þjónusta). Notaðu þegar beðið er um framlegð, arðsemi viðskiptavina, vara eða verka, „hvað skilar okkur mestu“, verðlagningu, verkayfirlit, framvindu verka, vörugreiningu, ABC, birgðir eða hægfara vörur.
---

# Framlegð og verk

**Valmælaborð** (ekki sjálfgefið í 1.0; bætt við úr miðstöð eða að beiðni).

Svarar: **Hvar verður framlegðin til, hvar lekur hún, hvernig standa verkin, og hvað gerist ef verð eða kostnaður breytist?**

Fylgdu `bifrost-maelabord` (útlit, gæði) og `bifrost-gogn` (gögn). Aðeins lesið úr BC.

Sameinar fyrri mælaborðin *Framlegð* og *Vörur og þjónusta*. **Óreikningsfært á verkum er ekki hér** heldur í `tekjuleki`; vísaðu þangað með tengli (`data-nav`) í Yfirsýn og Verk. Reikningsfært umfram framvindu er hins vegar áhætta og á heima hér.

## 1. Gögn og sýn eftir starfsemi

`dataset.json` úr `bifrost-gogn` (tekjur og vörunotkun á mánuði, `profile`). Veldu sýn:

| Starfsemi | Gögn |
|---|---|
| Verk (`jobs` > 0) | `Job`, `Job Task`, `Job Planning Line`, `Job Ledger Entry` (notkun og sala). Framlegð á verk = reikningsfært/reikningshæft − kostnaður; framlegð við verklok = samningur − áætlaður heildarkostnaður |
| Vörur (`items` > 0) | `Item`, `Item Ledger Entry`, `Value Entry` síðustu 12–24 mánuði: sala, kostnaður, magn, afsláttur, birgðir |
| Hvorugt | Tekjur eftir tekjulykli, víddum og viðskiptamanni (`Cust. Ledger Entry`); framlegð á tekjustoð |

Félag með bæði verk og vörur fær báða flipana. Segðu í haus hvaða sýn er notuð. Ef sölu- og kostnaðarlínur vantar á einingastigi: segðu það og sýndu framlegð á heildarstigi.

## 2. Flipar (fimm)

**Yfirsýn**
- Hero í fullri breidd: framlegð og framlegðarhlutfall, rofi *með / án einskiptisliða*.
- Lykilmælar: framlegð, framlegðarhlutfall, framlag eftir laun, samningsvirði opinna verka (eða birgðir í kr. í vörusýn).
- Staða verka sem staflasúla (á áætlun / athygli / á eftir), helstu áhættur, framlegðarhlutfall á mánuði á móti fyrra ári, brú.
- Lína: „Óreikningsfært á verkum: sjá Tekjuleka →“.

**Verk** (eða **Vörur** / **Þjónustulínur** eftir sýn)
- **Ein tafla á verk** með framvindu (kostnaður og tímar á móti áætlun, hlutfall liðins tíma sem súla með merki), samningi, framlegð við verklok í kr. og %, og athugasemd. Sama talan fyrir hvert verk alls staðar á síðunni.
- Tímalína (gantt) með merki við daginn í dag, framlegð á verk, „Þarf athygli“ (t.d. reikningsfært umfram framvindu, framlegð sem fellur), framlegð vinnu eftir deild eða forða (kóðar, ekki nöfn).

**Viðskiptavinir** eru í `tekjur`; hér er aðeins tengill „Viðskiptavinir: sjá Tekjur“.

**Vörur og ABC**
- ABC/Pareto (vörur, verk eða viðskiptavinir) með mörkum við 80% og 95%.
- Vörutafla með álagningu, leit og röðun; vörur **undir kostnaðarverði** og framlegð sem fellur merktar.
- Birgðir: hægfara vörur (engin sala í 90/180 daga) og bundið fé, birgðadagar.

**Herming**
- Stikur: verð (±%), afsláttur (pp), magn (±%), kostnaðarverð aðfanga (±%), yfirfærsla kostnaðarhækkunar í verð.
- Sviðsmyndir: *Grunnur · Kostnaður +5% · Verðhækkun +3% · Afsláttur 2 pp*. Niðurstöðusetning: „Til að halda X% framlegð þarf verð að hækka um Y%.“

**Gæði gagna**
- Sala bókuð á verk eða ekki, sala bókuð með dagbók í stað sölureikninga, tímar í safnfærslum, opin verk eftir lokadag, VÍV ekki reiknað, ófullbókaðir mánuðir.

## 3. Sannreyning

- Heildarframlegð stemmir við tekjur − vörunotkun í `dataset.json` (eða skýrðu muninn, t.d. birgðabreytingar).
- Samningsvirði og kostnaður verka stemma við verkfærslur; engin eining tvítalin milli flokka.
- Birgðir í kr. stemma við birgðalykla í efnahag.

## Samstæða

- Félagsval efst. Starfsemisgreining er gerð á hvert félag, svo flipar geta verið ólíkir eftir félagi. Í samstæðusýn eru aðeins sameiginlegir mælikvarðar (sala, framlegð, ABC) og dálkurinn *Félag*.
- Framlegð samstæðu reiknast eftir jöfnun innbyrðis sölu og innkaupa (`eliminations.json`, tegund `rekstur`).
- Hermirinn getur beinst að einu félagi eða öllum.
