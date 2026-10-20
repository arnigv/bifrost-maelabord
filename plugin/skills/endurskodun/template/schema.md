# Endurskoðun og ársreikningur: gagnaskema (`endurskodun`)

Gervigreindin skrifar **aðeins** JSON eftir þessu skema og keyrir:

```
python3 ${PLUGIN}/skills/bifrost-maelabord/scripts/render.py --dashboard endurskodun --data endurskodun.json --out build/endurskodun.html [--subpage]
```

`example.json` er sýnidæmið (DT Vélsmiðjan, gullútgáfa). Afritaðu það og skiptu út gildunum; lyklar mega ekki vanta.

**Einingar:** fjárhæðir í **krónum** (síðan sýnir m.kr.). Í rekstri eru tekjur og kostnaður **jákvæðar** tölur (síðan setur mínus á kostnað). Í efnahag eru eignir, eigið fé og skuldir **jákvæðar**. Í sjóðstreymi (`cf`) er innstreymi jákvætt og útstreymi neikvætt.

## 1. DATA-lyklar (allir skyldir)

### `py` (hlutur): rekstur fyrra árs í heild
`tekjur`, `vorunotkun`, `laun`, `husnaedi`, `annar_rekstur`, `afskriftir`, `fjarmagn`, `ebitda`, `hagnadur` (hagnaður fyrir skatta), kr.
BC: Hreyfing (reitur 32) á `G/L Account`, `Date Filter` = allt fyrra ár (`bifrost-gogn` kafli 0), flokkað eins og `dataset.months`; eða `dataset.py_full`. `ebitda` = tekjur − vörunotkun − laun − húsnæði − annar rekstur; `hagnadur` = ebitda − afskriftir − fjarmagn.

### `cy` (hlutur): rekstur yfirstandandi árs, fullbókaðir mánuðir
Sömu lyklar og `py`. Úr `dataset.ytd` (`hagnadur` = `ytd.hagnadur_fs`). Tímabilið er sýnt í `text.cy_label` og fjöldi daga í `meta.cy_days`.

### `bs_jan`, `bs_aug` (hlutir): efnahagur í upphafi og lok tímabils
Nöfnin eru föst (upphafs- og lokastaða), óháð mánuði. Lyklar: `fastafjarmunir`, `krofur` (viðskiptakröfur), `handbaert_fe`, `eignir` (samtals), `eigid_fe`, `langtimaskuldir`, `skammtimaskuldir`, kr.
BC: `period_breakdown` á `G/L Account` (`field_type:"balance"`) → `dataset.balance.categories[<flokkur>][<mánaðarvísir>]`. Upphafsstaða = lok síðasta lokaða tímabils (ef ársuppgjör fyrra árs er ólokað, fyrsti mánuður ársins: dagsetning í `meta.bs_start`). Lokastaða = síðasti fullbókaði mánuður (`meta.bs_end`). `eigid_fe` = eignir − skuldir.

### `cf` (listi af `[heiti, fjárhæð, flokkur]`): sjóðstreymi, óbein aðferð
Röðin skiptir máli: **[0] Hagnaður tímabils** og **[2] breyting viðskiptakrafna** eru lesin beint í texta. Flokkur er `rekstur`, `fjarfesting` eða `fjarmognun`. Dæmi:
`["Hagnaður tímabils", 247683487, "rekstur"], ["Afskriftir", …], ["Hækkun viðskiptakrafna", −(krofur_lok − krofur_upphaf)], ["Breyting skammtímaskulda", …], ["Fjárfesting", …, "fjarfesting"], ["Afborganir lána", Δlangtimaskuldir, "fjarmognun"], ["Greiddur arður", Δbókað eigið fé, "fjarmognun"]`.
Reiknað úr breytingum `bs_jan` → `bs_aug` (afkoma ársins, afskriftir úr hreyfingu afskriftalykla). Skilyrði: `cash[0] + Σcf = cash[1]` (±1.000 kr.). Liðir með |fjárhæð| ≤ 1 kr. eru faldir í grafi.

### `cash` (listi `[upphaf, lok]`)
Handbært fé í upphafi og lok sjóðstreymistímabils, kr. (= `bs_jan.handbaert_fe`, `bs_aug.handbaert_fe`).

### `size` (hlutur): úttak `classify_size.py` óbreytt
`flokkur`, `flokkur_heiti`, `fyrra_ar`, `stadfest_tvo_ar`, `fte_vantar`, `vidmid` (listi `{heiti, gildi, mork_litid, mork_medal}`; `gildi` má vera `null`), `endurskodun`, `endurskodun_stada`, `sjodstreymi_skylt`, `skilafrestur` (ISO), `sekt_kr`, `slitakrafa_fra` (ISO), `fyrirvari`, `heimild`.
Síðan les þetta ekki beint (geymt til rekjanleika); textarnir `text.size_class`, `text.audit`, `text.cashflow`, `meta.deadline`, `meta.dissolution` og `html.size_text` eru skrifaðir **úr því**.

### `size_vals` (hlutur): viðmið stærðarflokkunar, kr.
`eignir` (heildareignir á lokadegi), `velta` (hrein velta, 12 mán. eða áætlun ársins), `velta_py`, `eignir_py` (fyrra ár). Sömu tölur og fóru í `classify_size.py` (`--assets`, `--revenue`, `--prev-…`). Ársverk eru ekki í BC og síðan sýnir „vantar í BC“.

### `mat` (hlutur): mikilvægi (ISA 320), kr.
`rev` = [0,5%, 1%] af tekjum fyrra árs, `pbt` = [5%, 10%] af hagnaði fyrir skatta fyrra árs, `assets` = [1%, 2%] af heildareignum, `valið` = valin heildartala (tillaga). Hlutföll úr `thresholds.json → mikilvaegi`. Framkvæmdamikilvægi (75%) og smávægilegt (5%) reiknar síðan.

### `vsk` (hlutur): VSK-yfirlit ársins, kr.
`utskattur`, `innskattur`, `uppgjor` (staða uppgjörsreiknings). Hreyfing á VSK-lyklum (`G/L Account`, reitur 32) og staða uppgjörslykils. Ekki sýnt í síðunni enn; notað til að skrifa PBC-atriðið „VSK-uppgjör“.

### `closed_gap` (tala, kr.)
Hagnaður fyrri ára sem hefur ekki verið færður á eigið fé: `eigid_fe − eigid_fe_bokad − afkoma_arsins` í upphafsstöðu (`dataset.balance.categories`). 0 ef ársuppgjör er lokað.

## 2. `meta`, `text`, `html`, `js`

**Hvar gildin lenda.** `meta.*` og `text.*` fara aðeins í HTML (HTML-sloppin). `html.*` fer óbreytt í HTML (aðeins `<b>` og `<a href="x.html">`). `js.*` fer inn í JavaScript sem JSON-bókstafur (`json.dumps`), svo þar má vera hvaða texti sem er, líka gæsalappir, `'`, `` ` `` og `\`; tölur, listar og hlutir eru settir inn sem slíkir (ekki sem texti). Textar í `js` eru birtir sem HTML (innerHTML) þar sem þeir lenda í töflum og spjöldum: aðeins `<b>` og `<a href="x.html">`. Lykill sem er bæði í `meta` og `js` (t.d. `year`, `py`) á að hafa sama gildi í báðum. Valfrjálsir listar mega vera tómir (`[]`): þá er hlutinn falinn eða sýnir „Á ekki við“/„engin“ í stað villu.

### `meta` (HTML)

| Lykill | Dæmi (DT) | Regla |
|---|---|---|
| `meta.company`, `meta.short`, `meta.logo` | DT Vélsmiðjan ehf., DT, DT | Fullt heiti, stutt heiti í `<title>` og skýringum grafs, 1–3 stafir í merki |
| `meta.year`, `meta.py` | 2026, 2025 | Reikningsár og fyrra ár |
| `meta.as_of`, `meta.fetched` | 17.10.2026, 16.–17.10.2026 | Staða og hvenær sótt |
| `meta.cf_start` | 1.2., 31.8. | Upphaf og lok sjóðstreymistímabils, án árs |
| `meta.bs_end` | 31.1.2026, 31.8.2026 | Dagsetningar `bs_jan` og `bs_aug` |

### `text` (HTML, sloppið)

| Lykill | Dæmi (DT) | Regla |
|---|---|---|
| `text.law_note` | Á 158. löggjafarþingi liggja fyrir frumvörp … Mörkin hér miðast við gildandi lög 17.10.2026. (úr `size.fyrirvari`) |  |
| `text.size_class`, `text.size_class_lc` | Meðalstórt, meðalstórt félag (úr `size.flokkur_heiti`) |  |
| `text.ars_note` | Drög, óendurskoðað. 2026 sýnir 1.1.–31.8. … |  |
| `text.filing_note` | Skil eru eingöngu rafræn til ársreikningaskrár Skattsins. … |  |
| `text.footer_note` | Mörk 98. gr. (200 m eignir, 400 m velta, 50 ársverk) þarf að staðfesta. Ársverk vantar í BC. |  |

### `html` (HTML óbreytt)

| Lykill | Dæmi (DT) | Regla |
|---|---|---|
| `html.size_text` | Ein til tvær setningar, má nota `<b>`. Dæmi: `Fer yfir mörk lítils félags í heildareignum og veltu, bæði 2025 og 2026. Því er <b>endurskoðun skyld</b> og <b>sjóðstreymisyfirlit skylt</b> (28. gr.).` |  |

### `js` (JavaScript-bókstafir)

| Lykill | Dæmi (DT) | Regla |
|---|---|---|
| `js.cf_start` | 1.2., 31.8. | Upphaf og lok sjóðstreymistímabils, án árs |
| `js.bs_end` | 31.1.2026, 31.8.2026 | Dagsetningar `bs_jan` og `bs_aug` |
| `js.deadline` | 31.08.2027 | `size.skilafrestur` á sniðinu DD.MM.ÁÁÁÁ |
| `js.days_to_deadline` | 318 | Dagar frá `as_of` til `deadline` (heiltala) |
| `js.fy_end` | 31.12.2026 | Lok reikningsárs |
| `js.agm` | maí 2027 | Áætlaður aðalfundur (dæmi) |
| `js.dissolution` | 28.02.2028 | `size.slitakrafa_fra` á sniðinu DD.MM.ÁÁÁÁ |
| `js.cf_end` | 1.2., 31.8. | Upphaf og lok sjóðstreymistímabils, án árs |
| `js.bs_start` | 31.1.2026, 31.8.2026 | Dagsetningar `bs_jan` og `bs_aug` |
| `js.cy_days` | 243 | Fjöldi daga í `cy`-tímabilinu (tala; notað í innheimtutíma) |
| `js.audit`, `js.cashflow` | Skyld / Undanþegin; Skylt / Ekki skylt |  |
| `js.cy_label` | 2026 jan–ágú (dálkhaus `cy`) |  |
| `js.ring_note` | Öll atriði sem vantar eru leysanleg í BC fyrir áramót. |  |
| `js.kpi1_d` | framkvæmda 9,0 m · smávægilegt 0,6 m |  |
| `js.kpi2_l`, `js.kpi2_d` | Ólokað ársuppgjör 2025, hagnaður 2025 ekki færður á eigið fé (gildið er `closed_gap`) |  |
| `js.kpi3_l`, `js.kpi3_v`, `js.kpi3_d` | Handfærðar tekjufærslur, 87, dagbók í stað sölureikninga |  |
| `js.kpi4_l`, `js.kpi4_d` | Óbókaðar greiðslur, sep–okt, sjóður ofmetinn |  |
| `js.first_je_amt` | 87 f. (fjöldi í fyrsta færsluprófi, sýnt í „Fyrst að laga“) |  |
| `js.cf_note_tail` | Fjárfesting engin. |  |
| `js.pbc_js` | [["vantar", "Ógreiddar greiðslur sep–okt ekki bókaðar", "…", "123,5 m"], …] | JSON-fylki af `[staða, heiti, lýsing, fjárhæð]`; staða `vantar`/`vinnslu`/`lokid`. Fyrstu 4 `vantar`-atriðin birtast í „Fyrst að laga“. `[]` leyft |
| `js.je_js` | [["h", "Handfærðar tekjur", 87, "…", "…"], …] | JSON-fylki af `[alvarleiki h/m/l, próf, fjöldi (tala), lýsing, næsta skref]` úr `je_tests.py`; fyrsta prófið birtist líka í „Fyrst að laga“. `[]` leyft |
| `js.notes_js` | [["Reikningsskilaaðferðir", "já", "…"], …] | JSON-fylki af `[skýring, í BC (já/að hluta/nei), athugasemd]` |
| `js.kpi4_v` | 123,5<small>m</small> | gildi með einingu (HTML leyft) |
| `js.year` | 2026 | tala, sama og `meta.year` |
| `js.py` | 2025 | tala, sama og `meta.py` |

`cf` er listi `[heiti, fjárhæð, flokkur]`; hagnaðarlína (heiti byrjar á „Hagnaður“) og kröfulína (heiti inniheldur „krafn“/„kröfu“) eru fundnar eftir heiti, ekki sæti.


## 5. Fastar reglur í sniðmátinu (ekki gögn)

Stærðarmörk í grafi (600 m / 3.000 m eignir, 1.200 m / 6.000 m velta, 50 / 250 ársverk), 8 mánaða skilafrestur, sekt 600.000 kr. og VSK-stuðull 1,24 í innheimtutíma eru úr lögum nr. 3/2006 og `thresholds.json`. Breytist lögin þarf að uppfæra sniðmátið.
