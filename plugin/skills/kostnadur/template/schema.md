# Kostnaður og innkaup: gagnalýsing (`DATA`)

Sniðmát: `template.html`. Gögn: einn JSON-hlutur með lyklunum hér að neðan. Smíða með
`render.py --dashboard kostnadur --data kostnadur.json --out build/kostnadur.html`. Lögun er borin saman við `example.json` (DT Vélsmiðjan); allir lyklar þar eru **skylda** nema annað sé tekið fram. Fjárhæðir í **krónum** (ekki m.kr.) nema annað sé tekið fram. Kostnaður er **jákvæður**. Allt sótt með lesköllum í BC um Bifröst (sjá `bifrost-gogn` kafla 0: samtölur fyrst).

## Grunnur

| Lykill | Tegund | Merking | Úr BC |
|---|---|---|---|
| `today` | texti `ÁÁÁÁ-MM-DD` | Stöðudagur (dagar í bið og gjaldfallið reiknast frá honum) | Dagurinn sem gögn eru sótt |
| `rev8` | tala, kr. | Tekjur fullbókuðu mánaðanna (jákvætt) | `dataset.json` → summa `months[].tekjur` fyrir fullbókaða mánuði |
| `revg` | tala, hlutfall (0,20 = 20%) | Vöxtur tekna fullbókuðu mánaðanna á móti sama hlutfalli fyrra árs (`rev8` / (tekjur fyrra árs × n/12) − 1) | `dataset.json` + Hreyfing (32) á `G/L Account` fyrra ár |
| `cats` | hlutur `{flokkur: heiti}` | Kostnaðarflokkar í birtingarröð: `vorunotkun`, `laun`, `husnaedi`, `annar_rekstur`, `afskriftir`, `fjarmagn`, `oreglulegt` | `dataset.json` → `categories` (flokkun bifrost-gogn) |
| `opex` | listi af flokkalyklum | Flokkar sem teljast rekstrarkostnaður (fyrstu fjórir); hinir eru sýndir daufir „utan rekstrarkostnaðar“. Hámark 4 (litir `--s1`–`--s4`) | Fast: `["vorunotkun","laun","husnaedi","annar_rekstur"]` |
| `incomplete` | hlutur `{"ÁÁÁÁ-MM": ástæða}` | Ófullbókaðir mánuðir og ástæða (sýndir daufir í mánaðargrafi) | `dataset.json` → `months[]` þar sem `complete=false`, `incomplete_reason` |

## `inv[]`: innkaupareikningar í samþykkt (flipi Samþykkt reikninga)

Allir óbókaðir innkaupareikningar sem bíða samþykkis. Úr `Purchase Header` (Document Type=Invoice, Status=Pending Approval) og `Approval Entry` (Status=Open) með `data_batch_records`; fjárhæð = Amount Including VAT (SGM).

| Reitur | Tegund | Merking |
|---|---|---|
| `doc` | texti | Númer skjals (Purchase Header No.) |
| `vno`, `vendor` | texti | Númer og heiti lánardrottins |
| `amt` | tala, kr. með VSK | Upphæð reiknings |
| `due` | `ÁÁÁÁ-MM-DD` | Gjalddagi |
| `sent` | `ÁÁÁÁ-MM-DD` | Sent í samþykkt (Approval Entry Date-Time Sent for Approval) |
| `days` | heiltala | Dagar í bið = `today` − `sent` |
| `overdue` | heiltala | `today` − `due` (jákvætt = kominn yfir gjalddaga, neikvætt = dagar þar til) |
| `approver` | texti | Samþykkjandi sem **hlutverk/númer**, aldrei nafn („Samþykkjandi 1“) |
| `ic` | true/false | Tengdur aðili (innan samstæðu) |
| `fx` | texti | Gjaldmiðill ef erlendur („EUR“), annars `""` |

## `sav[]`: sparnaðartækifæri (mat)

| Reitur | Tegund | Merking |
|---|---|---|
| `t` | texti | Heiti tækifæris |
| `d` | texti | Ein setning: forsenda og stærð („2% betri kjör á vöruinnkaupum … um 651 m.kr. á ári.“) |
| `amt` | tala, kr. á ári | Áætlaður árlegur sparnaður (jákvætt) |
| `eff` | texti | Fyrirhöfn: „Lítið“, „Miðl.“, „Mikið“ |
| `v` | texti | Vissa: „Líklegt“ eða „Mat“ |
| `next` | texti | Næsta skref |

Reiknað úr `accs` (t.d. 2% af vöruinnkaupum á ársgrundvelli). Ekki sótt beint úr BC.

## `accs[]`: kostnaðarlyklar (tré flokkur → lykill → færslur)

Einn hlutur á hvern bókunarlykil í kostnaðarflokkunum (`cats`) með hreyfingu á árinu, raðað eftir flokki og svo `v` lækkandi.

| Reitur | Tegund | Merking | Úr BC |
|---|---|---|---|
| `no`, `name` | texti | Lykill og heiti (án „24% VSK“ o.þ.h.) | `G/L Account` (1, 2) |
| `cat` | texti | Flokkur, lykill í `cats` | flokkun bifrost-gogn |
| `v` | tala, kr. | Hreyfing ársins til þessa (allir mánuðir í `m`) | Hreyfing (32) á `G/L Account`, Date Filter jan–stöðudag |
| `v8` | tala, kr. | Hreyfing fullbókuðu mánaðanna | sama, Date Filter jan–síðasti fullbókaði mánuður |
| `py8` | tala, kr. | Fyrra ár × n/12 (samanburður við `v8`); 0 ef lykill var ekki til | Hreyfing (32) fyrra ár |
| `n` | heiltala | Fjöldi færslna á lyklinum | `data_record_count` á `G/L Entry` |
| `m` | listi af tölum, kr. | Hreyfing á mánuði, einn liður á hvern mánuð í `js.months` (sama röð) | `period_breakdown` (net_change) á `G/L Account` |
| `e` | listi `[dags, fylgiskjal, lýsing, birgir/uppruni, fjárhæð]` | Stærstu færslur (allt að 50, eftir algildi). Uppruni tómur = dagbók. Kort sem „Greiðslukort 1“, aldrei upphafsstafir | `data_batch_records` á `G/L Entry` (aðeins þær sem birtast) |
| `rest` | `[fjöldi, fjárhæð]` | Færslur umfram þær sem eru í `e` | `n` − len(`e`), `v` − summa `e` |

Samtala `v` á lykil á að stemma við fjárhag upp á krónu (stendur í neðanmálsgrein trésins).

## `vend[]`: birgjar (lánardrottnar og greiðslukort)

Raðað eftir `tot + samt` lækkandi. Fyrstu 8 sýnd, leit og „Sýna alla“.

| Reitur | Tegund | Merking | Úr BC |
|---|---|---|---|
| `no`, `name` | texti | Númer og heiti. Greiðslukort: `no` byrjar á `KORT` („KORT-1“, „Greiðslukort 1“) | `Vendor` |
| `ic` | true/false | Tengdur aðili | Vendor Posting Group / samstæðulisti |
| `tot` | tala, kr. með VSK | Reikningar ársins (bókaðir), kreditreikningar draga frá | Innkaup (SGM, 62) á `Vendor` með Date Filter, eða `Data.Totals.Get` á `Vendor Ledger Entry` |
| `open` | tala, kr. | Opið (eftirstöðvar) | `aging` lánardrottna |
| `od` | tala, kr. | Gjaldfallið opið | Gjaldfallið (SGM, 67) eða `aging` |
| `samt` | tala, kr. | Reikningar í samþykkt (sama og `inv` fyrir birgi) | úr `inv` |
| `gl` | listi `[lykill, heiti, fjárhæð]` | Allt að 4 lyklar sem birgir er mest bókaður á | `Data.Totals.Get` á `G/L Entry` (groupBy `G/L Account No.`, Source No.=birgir) |
| `inv` | listi `[dags, skjal, lýsing, gjalddagi, fjárhæð, eftirstöðvar, tegund]` | Reikningar, nýjastir fyrst. `tegund` = `"bok"` (bókaður, úr `Vendor Ledger Entry`) eða `"samt"` (í samþykkt). Kreditreikningar með mínus | `data_batch_records` á `Vendor Ledger Entry` (aðeins birgjar sem birtast) |
## Reglur um `meta`, `text` og `html`

- `meta` eru stuttar breytur (nafn, dagsetningar, ár, númer verka/lykla, tölur sem fara beint inn í kóða). `text` eru setningar og setningahlutar sem gervigreindin skrifar fyrir félagið. `html` er ekki notað í þessu sniðmáti. `js` eru gildi sem fara inn í JavaScript (sjá töflu `js`).
- **Hvar gildin lenda.** `meta.*` og `text.*` fara aðeins í HTML (HTML-sloppin). `html.*` fer óbreytt í HTML (aðeins `<b>` og `<a href="x.html">`). `js.*` fer inn í JavaScript sem JSON-bókstafur (`json.dumps`), svo þar má vera hvaða texti sem er, líka gæsalappir, `'`, `` ` `` og `\`; tölur, listar og hlutir eru settir inn sem slíkir (ekki sem texti). Textar í `js` eru birtir sem HTML (innerHTML) þar sem þeir lenda í töflum og spjöldum: aðeins `<b>` og `<a href="x.html">`. Lykill sem er bæði í `meta` og `js` (t.d. `year`, `py`) á að hafa sama gildi í báðum. Valfrjálsir listar mega vera tómir (`[]`): þá er hlutinn falinn eða sýnir „Á ekki við“/„engin“ í stað villu.
- Skrifaðu stutt og staðreyndamiðað, eina til tvær setningar, án gildishlaðinna orða. Tölur á íslensku sniði: `1.234,5 m`, `41,8 m.kr.`, `12,4%`, dagsetningar `31.08.` eða `31.08.2026`, tímabil `jan–ágú` (stutt strik –).
- Setningahlutar (`..._d1`, `..._d2`, …) eru skeyttir saman við reiknaðar tölur í kóðanum: haltu sama orðalagi í lok og byrjun svo setningin gangi upp (sjá dæmi DT í töflunni).
- Ef atriði á ekki við félagið (t.d. engin innbyrðis viðskipti): skrifaðu hlutlausan texta sem segir það („Engin innbyrðis viðskipti skráð.“), ekki skilja eftir tóman streng nema það sé setningahluti.
- `meta.company` er nefnifall („DT Vélsmiðjan ehf.“), `meta.company_gen` eignarfall („DT Vélsmiðjunnar ehf.“). `meta.logo`/`meta.short` er 2–3 stafa skammstöfun.
- `meta.year` = yfirstandandi uppgjörsár (texti, „2026“), `meta.py` = fyrra ár („2025“).

### `meta` (öll skylda; dæmi úr DT)

| Lykill | Dæmi (DT) |
|---|---|
| `meta.company` | DT Vélsmiðjan ehf. |
| `meta.company_gen` | DT Vélsmiðjunnar ehf. |
| `meta.logo` | DT |
| `meta.as_of` | 16.10.2026 |
| `meta.year` | 2026 |
| `meta.py` | 2025 |

### `js` (öll skylda; dæmi úr DT)

| Lykill | Dæmi (DT) |
|---|---|
| `js.year`, `js.py` | 2026, 2025 (sama og `meta.year`, `meta.py`) |
| `js.period` | jan–okt (sama og `text.period`) |
| `js.months` | ["2026-01", …, "2026-10"]: mánuðir (ÁÁÁÁ-MM) sem `accs[].m` vísar í, í sömu röð; mánaðargrafið sýnir þá |

### `text` (öll skylda; dæmi úr DT)

| Lykill | Dæmi (DT) |
|---|---|
| `text.period` | jan–okt |
| `text.period_long` | janúar til október |
| `js.full_period` | jan–ágú |
| `js.kpi_opex_note` | sep–okt ófullbókaðir |
| `js.incomplete_lead` | Sep og okt eru ófullbókaðir |
| `text.acc_range` | 2000–4999 |
| `text.fetched` | 16.–18.10.2026 |
| `text.incomplete_sentence` | September og október eru ófullbókaðir. |

### Hvað hver lykill er notaður í

- `meta.company`, `meta.logo`, `meta.as_of` (stöðudagur `DD.MM.ÁÁÁÁ`, sami dagur og `today`): haus.
- `meta.company_gen`: neðanmálsgrein („… samþykktarfærslur DT Vélsmiðjunnar ehf. í Business Central“).
- `js.months`: mánuðir í `accs[].m` og mánaðargrafi (ÁÁÁÁ-MM, í röð; þarf ekki að byrja í janúar). Ófullbókaðir mánuðir eru þeir sem eru lyklar í `incomplete`.
- `text.period` / `text.period_long`: tímabil gagna stutt og langt („jan–okt“, „janúar til október“).
- `js.full_period`: fullbókaðir mánuðir (grunnur `v8`, `py8`, `rev8`), t.d. „jan–ágú“.
- `js.kpi_opex_note`: undirtexti spjalds Rekstrarkostnaður („sep–okt ófullbókaðir“; ef allt fullbókað: „allir mánuðir fullbókaðir“).
- `js.incomplete_lead`: upphaf athugasemdar undir mánaðargrafi, á eftir kemur „(ástæða) og sýndir daufir.“ („Sep og okt eru ófullbókaðir“).
- `text.incomplete_sentence`: heil setning í neðanmálsgrein („September og október eru ófullbókaðir.“).
- `text.acc_range`: lyklabil kostnaðar („2000–4999“). `text.fetched`: hvenær sótt („16.–18.10.2026“).

**Tómt leyft:** `inv: []` (enginn reikningur í samþykkt) sýnir „Engir innkaupareikningar bíða samþykkis.“; `incomplete: {}` þegar allt er fullbókað; `sav: []`.

## Tungumál (`lang`, `i18n`)

| Lykill | Dæmi | Skýring |
|---|---|---|
| `lang` | `"is"` | tungumál grunngagna (úr `dataset.json`). Ræður hvaða mál opnast fyrst. Vanti það er það greint úr heitum í gögnunum. |
| `i18n.en` (eða `i18n.is`) | `{"meta": {...}, "text": {...}, "html": {...}, "js": {...}, "names": {...}}` | yfirlag fyrir hitt málið. Sömu lyklar og að ofan, aðeins þeir sem breytast. Dagsetningar á ensku `17 Oct 2026`, tölur `1,234.5`. |
| `i18n.<lang>.names` | `{"Áætlun 2026": "Budget 2026"}` | þýðir heila strengi hvar sem er í gögnunum (heiti lykla utan staðaltöflu, áætlana, flokka, stöðu). |

Sjá `example.json` (yfirlagið `i18n.en`) og `bifrost-maelabord/SKILL.md`, kaflann *Tungumál*.
