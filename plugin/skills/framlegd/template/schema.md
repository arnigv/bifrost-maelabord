# Framlegð og verk: gagnalýsing (`DATA`)

Sniðmát: `template.html`. Smíða: `render.py --dashboard framlegd --data framlegd.json --out build/framlegd.html`. Allir lyklar í `example.json` eru **skylda**. Fjárhæðir í **krónum**, tekjur og kostnaður **jákvæð**. Lesköll eingöngu (`bifrost-gogn` kafli 0).

**Ekkert er harðkóðað:** verk, hópar smáverka, verk með föstu gjaldi, aðfangalyklar í brú og athugasemdalistar koma úr `js` (sjá neðst). Verk eða lykill í `js` sem er ekki til í gögnunum er sleppt, og tómir listar fela viðkomandi spjald í stað þess að síðan stöðvist.

## Fjárhagur (flipi Yfirsýn og Herming)

| Lykill | Tegund | Merking | Úr BC |
|---|---|---|---|
| `as_of` | `ÁÁÁÁ-MM-DD` | Stöðudagur | — |
| `months[]` | listi `{ym, rev, cogs, laun, complete, oneoff}` | Á mánuð frá janúar: tekjur, vörunotkun og aðföng, laun, fullbókaður, einskiptistekjur í mánuðinum. Aðeins `complete=true` mánuðir fara í tölur og gröf | `dataset.json` → `months[]` (`tekjur`, `vorunotkun`, `laun`, `complete`) og `oneoffs` |
| `py` | `{rev, cogs, laun}` | Fyrra ár, heilt ár | Hreyfing (32) á `G/L Account` fyrra ár, eftir flokkum |
| `ytd` | `{rev, cogs, laun}` | Ár til þessa (allir mánuðir) | `dataset.json` → `ytd` |
| `oneoffs[]` | listi `{no, name, cat, ym, amount}` | Einskiptisliðir (bifrost-gogn). Tekjuliðir eru dregnir frá í „Án einskiptissölu“ | `dataset.json` → `oneoffs` |
| `cogs_acc[]` | listi `{no, name, v, py}` | Vörunotkunarlyklar: hreyfing fullbókaðra mánaða og fyrra árs heilt (`py` null ef óþekkt) | Hreyfing (32) á `G/L Account`, flokkur `vorunotkun` |
| `gl_rev` | tala, kr. | Tekjur ársins í fjárhag (til samanburðar við sölu á viðskiptavin) | `dataset.json` → `ytd.tekjur` |
| `cle_total` | tala, kr. | Reikningsfærð sala ársins í viðskiptamannabók | `Data.Totals.Get` á `Cust. Ledger Entry` [18] Sales (LCY) |

## Verk (flipi Verk)

`jobs[]`: eitt á verk (opin verk ársins). Úr `Job` (spjald), `Job Planning Line` (áætlun og reikningshæft) og `Job Ledger Entry` (notkun), samtölur með `Data.Totals.Get` (groupBy `Job No.`), og `Cust. Ledger Entry` fyrir reikningsfært utan verkbókhalds.

| Reitur | Tegund | Merking |
|---|---|---|
| `no`, `desc` | texti | Verknúmer og lýsing |
| `cno`, `cust` | texti | Viðskiptamaður (númer, heiti) |
| `dept` | texti | Deild (Global Dimension 1), t.d. `THJONUSTA`, `VERKST`, `UPPSETN` |
| `typ` | texti | Tegund verks („Tilboðsverk“, „Þjónustusamningur“, „Tímaverk“ …) |
| `start`, `end` | `ÁÁÁÁ-MM-DD` | Upphaf og lok verks (tímalína) |
| `contract` | tala, kr. | Reikningshæft samkvæmt áætlun (Line Type Billable, Total Price) |
| `contract_m` | tala, kr. | Samningsvirði sem notað er (= `contract`, eða ársáætlun á verðskrá fyrir þjónustusamning) |
| `contract_year` | tala, valfrjálst | Ársáætlun á verðskrá (aðeins þjónustusamningar) |
| `budcost` | tala, kr. | Áætlaður heildarkostnaður (Budget-línur, Total Cost) |
| `cost` | tala, kr. | Kostnaður til þessa (Job Ledger Entry, Usage, Total Cost) |
| `hrs_b`, `hrs` | tala, klst. | Áætlaðir og bókaðir tímar forða |
| `invoiced` | tala, kr. | Reikningsfært á verkið (verkbókhald + sölureikningar tengdir eftir viðskiptamanni og fjárhæð) |
| `tfrac` | tala 0–1 | Hlutfall verktíma liðið á stöðudegi |
| `used_val` | tala, kr. | Bókaðir tímar á verðskrá |
| `tobill` | tala, kr. | Reikningshæft sem ekki er reikningsfært |
| `margin` | tala, kr., eða null | Áætluð framlegð við verklok = `contract_m` − `budcost` (null ef ekkert samningsvirði, t.d. lagersmíði) |

| Lykill | Tegund | Merking | Úr BC |
|---|---|---|---|
| `resources[]` | `{code, cost, price, hrs}` | Forðar með **kóða** (aldrei nafni): kostnaðarverð og verð á klst., bókaðir tímar | `Resource` (Unit Cost, Unit Price), Notkun (magn, 44) eða `Job Ledger Entry` groupBy `No.` |
| `dept[]` | `{code, val, cost, hrs}` | Á deild: bókaðir tímar á verðskrá, á kostnaðarverði, tímar | `Job Ledger Entry` (Type=Resource) eftir deild verks |

## Viðskiptavinir og vörur (flipi Vörur og ABC)

| Lykill | Tegund | Merking | Úr BC |
|---|---|---|---|
| `cust[]` | `{no, name, sales, jobs, job_contract, job_margin}` | Reikningsfærð sala ársins á viðskiptavin (lækkandi), verk hans, samningsvirði og framlegð þeirra | Sala (SGM, 62) á `Customer` með Date Filter, eða `Data.Totals.Get` á `Cust. Ledger Entry` |
| `items[]` | `{no, name, price, cost, inv}` | Vörur: einingarverð, kostnaðarverð, birgðir (magn) | `Item` (Unit Price, Unit Cost, Birgðir 68) |
## Reglur um `meta`, `text` og `js`

- **Hvar gildin lenda.** `meta.*` og `text.*` fara aðeins í HTML (HTML-sloppin). `html.*` fer óbreytt í HTML (aðeins `<b>` og `<a href="x.html">`). `js.*` fer inn í JavaScript sem JSON-bókstafur (`json.dumps`), svo þar má vera hvaða texti sem er, líka gæsalappir, `'`, `` ` `` og `\`; tölur, listar og hlutir eru settir inn sem slíkir (ekki sem texti). Textar í `js` eru birtir sem HTML (innerHTML) þar sem þeir lenda í töflum og spjöldum: aðeins `<b>` og `<a href="x.html">`. Lykill sem er bæði í `meta` og `js` (t.d. `year`, `py`) á að hafa sama gildi í báðum. Valfrjálsir listar mega vera tómir (`[]`): þá er hlutinn falinn eða sýnir „Á ekki við“/„engin“ í stað villu.
- Skrifaðu stutt og staðreyndamiðað, eina til tvær setningar, án gildishlaðinna orða. Tölur á íslensku sniði: `1.234,5 m`, `41,8 m.kr.`, `12,4%`, dagsetningar `31.08.2026`, tímabil `jan–ágú`.
- Félagssértæk atriði (áhættur, athugasemdir, gæði gagna, athugasemd á verklínu) eru **listar í `js`** með fullskrifuðum texta og tölum (gervigreindin reiknar tölurnar úr DATA og skrifar þær á íslensku sniði). Engin verk, vörur eða lyklar eru harðkóðuð í sniðmátinu.

### `meta` (dæmi úr DT)

| Lykill | Dæmi (DT) | Regla |
|---|---|---|
| `meta.company`, `meta.company_short`, `meta.logo` | DT Vélsmiðjan ehf. / DT Vélsmiðjan / DT | nefnifall, án „ehf.“ (titill), merki |
| `meta.as_of`, `meta.as_of_dm` | 17.10.2026, 17.10. | stöðudagur |
| `meta.year`, `meta.py` (og `js.year`, `js.py`) | 2026, 2025 | ár og fyrra ár (texti) |
| `meta.n_full` | 8 | fjöldi fullbókaðra mánaða (í texta hermis) |
| `meta.job_fee` | S-2603 | verk í fyrirsögn grafs um fast gjald (sama og `js.fee_jobs[0].no`; `""` ef ekkert, þá er spjaldið falið) |

### `text` (dæmi úr DT; birt í HTML)

`text.period` (fullbókaðir mánuðir, „jan–ágú“), `text.line_note`, `text.cogs_note`, `text.verk_note`, `text.gantt_note`, `text.items_note`, `text.cost_examples`, `text.source`, `text.caveats`: sjá `example.json`.

### `js`

| Lykill | Dæmi (DT) | Regla |
|---|---|---|
| `js.period` | jan–ágú | sama og `text.period` |
| `js.job_rows` | `{"no": "V-2601", "s": "bad", "lbl": "Á eftir", "prog": "cost", "basis": "kostn.", "prev": 0.232, "note": "…"}` | línur verkatöflu í birtingarröð. `no`: verknúmer í `jobs` eða `no` hóps úr `job_groups`. `s`: `ok`/`warn`/`bad`. `prog`: `cost` (kostnaður/áætlaður kostnaður), `hrs` (tímar/áætlaðir tímar) eða `value` (þá `pv` = hlutfall, t.d. tímar á móti föstu gjaldi). `prev`: fyrri framlegð verks (hlutfall) eða `null`. Línur með verki sem er ekki til er sleppt. **Tómur listi** → öll verk sýnd (hópar samanlagðir) með sjálfvirkri stöðu eftir framlegð (undir 0 = á eftir, undir 25% = athygli) |
| `js.job_groups` | `[{"prefix": "D-", "no": "D-01–D-10", "desc": "Tíu tímaverk, ágúst", "cust": "5 viðskiptavinir", "start": "2026-08-01", "end": "2026-08-31", "label": "D-verk"}]` | hópar smáverka sem teljast sem eitt verk (summa yfir verk sem byrja á `prefix`); `[]` ef engir |
| `js.fee_jobs` | `[{"no": "S-2603", "fee_month": 1200000, "fee_rate": 18900, "months": ["2026-01", …], "hours": [62, …]}]` | verk með föstu mánaðargjaldi: gjald á mánuði (kr.), verð á klst., mánuðir og bókaðir tímar á mánuði. `[]` → grafið falið |
| `js.cogs_bridge` | `[{"no": "2010", "label": "Vöruinnk."}, …]` | aðfangalyklar (úr `cogs_acc`) í framlegðarbrú með stuttu heiti; afgangur sýndur sem „Annað“. `[]` → allir lyklar með hreyfingu |
| `js.overruns` | `{"S-2602": "2026-10-06"}` | verk → síðasti dagur vinnu eftir samningslok (rönd í tímalínu); `{}` ef ekkert |
| `js.dept_names` | `{"THJONUSTA": "Þjónusta", …}` | heiti deildakóða (`dept[].code`); kóði sýndur ef heiti vantar |
| `js.risks` | `[["h", "!", "titill", "lýsing", "41,0 m"], …]` | Helstu áhættur (Yfirsýn): `[alvarleiki h/m/l, tákn, titill, lýsing, fjárhæð eða ""]`; `[]` → spjaldið falið |
| `js.job_flags` | sama snið | Þarf athygli (Verk) |
| `js.item_flags` | sama snið | Þarf athygli (Vörur) |
| `js.quality` | sama snið | Gæði gagna; `[]` → „Engar athugasemdir um gæði gagna.“ |
| `js.ins_tail` | Aðföng sem hlutfall af tekjum eru 5,1 pp lægri … | lokasetning innsýnar á Yfirsýn |
| `js.abc_cust_mid` | Svarfaðarver eitt er | á undan hlutdeild stærsta viðskiptavinar (%) |
| `js.abc_job_tail` | V-2601 og S-2601 bera reksturinn; tíu D-verk eru samtals | á eftir ABC verka; hlutdeild fyrsta hóps (`job_groups`) er skeytt aftan við ef hópur er til |
| `js.v1_note`, `js.dept_note`, `js.res_note_tail` | S-2601 sem ársáætlun … | skýringar á lykilmæli verka, deildum og forðum |

**Reiknað úr gögnum:** fjöldi mánaða og ársuppfærsla í hermi (úr fullbókuðum mánuðum), tímalína (ár úr `js.year`, dagurinn í dag úr `as_of`), lágmark á ás framlegðarhlutfalls (úr gögnum, ekki fast 40%), „talin saman“-texti hópa.
