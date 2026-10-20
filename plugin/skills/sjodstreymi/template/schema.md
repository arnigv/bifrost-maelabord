# Sjóðstreymi og bankar: gagnaskema (DATA)

Gervigreindin fyllir aðeins þetta JSON og keyrir
`render.py --dashboard sjodstreymi --data sjodstreymi.json --out sjodstreymi.html`. HTML er aldrei skrifað í höndunum.
`example.json` er gullútgáfan (DT Vélsmiðjan ehf.).

**Formerki og einingar.** Fjárhæðir í **kr.** Inn- og útgreiðslur sem **jákvæðar** tölur (spálíkanið ákveður stefnu). Bankainnstæður jákvæðar, kortaskuld neikvæð. Hlutföll sem tugabrot (0,51 = 51%). Dagsetningar `"ÁÁÁÁ-MM-DD"`.

## Lyklar

| Lykill | Tegund | Skylt | Merking | Hvaðan úr BC (Bifröst) |
|---|---|---|---|---|
| `today` | ÁÁÁÁ-MM-DD | já | Staða gagna (BC) | dagur sóknar |
| `start` | ÁÁÁÁ-MM-DD | já | Mánudagur fyrstu spáviku (13 vikur frá honum) | næsti mánudagur eftir `today` |
| `cash` | kr. | já | Bankainnstæður nú (upphafsstaða spár) | `period_breakdown` á `G/L Account` (bankalyklar, balance) eða summa `banks[].bal` utan korta |
| `cash_hist[]` | listi kr. | já | Bankainnstæður í lok hvers mánaðar (`months`); síðasta = staða `today` | `period_breakdown` balance, 1M bil |
| `months[]` | ÁÁÁÁ-MM | já | Mánuðir fyrir `cash_hist`/`krofur_hist` | |
| `krofur_hist[]` | listi kr. | já | Viðskiptakröfur í lok mánaðar | `period_breakdown` á kröfulykli |
| `laun_m` | kr. | já | Meðallaun á mánuði (fullbókaðir mánuðir) | `dataset.json → months[].laun` |
| `coll_base`, `coll_slow` | hlutfall | já | Hlutfall nýrrar sölu m. VSK sem innheimtist (meðaltal fullbókaðra mánaða / síðustu 2 mánaða) | innborganir á `Bank Account Ledger Entry` (samtölur, `Data.Totals.Get`) ÷ sala m. VSK |
| `share_net`, `share_wh` | hlutfall | já | Hlutfall launakostnaðar sem greitt er út (síðasta virka dag) og í staðgreiðslu/launatengd (15. næsta mánaðar) | bankafærslur launa/skatta ÷ `laun_m` |
| `sala_m`, `sala_vsk_m` | kr. | já | Meðalsala á mánuði án/með VSK | `dataset.json` tekjur; × 1,24 nema undanþegin sala |
| `vsk_m` | kr. | já | Meðal-VSK til greiðslu á mánuði (greitt 2 mánuði í senn) | staða VSK-lykla (`period_breakdown`) |
| `vsk_julagu`, `vsk_net` | kr. | já | VSK síðasta tímabils; nettó VSK-skuld nú | VSK-lyklar |
| `loan`, `fixed` | kr. | já | Mánaðarleg afborgun+vextir lána; fastar mánaðargreiðslur (leiga o.fl.) | bankafærslur / lánalykill |
| `ven` | kort `{"DD": kr}` | já | Regluleg greiðsla til lánardrottna eftir degi mánaðar (meðaltal á mánuð) | `Data.Totals.Get` á `Bank Account Ledger Entry` (útgreiðslur, flokkað eftir degi) |
| `innh` | kort `{ÁÁÁÁ-MM: kr}` | já | Innborganir á mánuð | sama, innborganir |
| `net_sal_share` | hlutfall | já | Útborguð laun ÷ launakostnaður | bankafærslur |
| `custs[]` | listi | já | `{no, name, b:[6 tölur kr.], delay}`; `b` = ekki gjaldfallið, 0–30, 31–60, 61–90, 91–120, > 120 d.; `delay` = meðaltöf greiddra reikninga í dögum (`null` = engin greiðsla) | `aging` (`entity:"customer"`); töf úr lokuðum `Cust. Ledger Entry` |
| `nyd[]` | listi `[no, gjalddagi, kr]` | já | Ógjaldfallnar opnar kröfur með gjalddaga | `Cust. Ledger Entry`, `Open=CONST(true)`, Due Date ≥ today |
| `ag_total` | kr. | já | Summa `custs[].b` | reiknað |
| `krofur_gl` | kr. | já | Viðskiptakröfur skv. fjárhag | `period_breakdown` balance |
| `vend_open[]` | listi | já | Opnar lánardrottnafærslur: `{no, name, amt, due}` | `Vendor Ledger Entry`, `Open=CONST(true)` |
| `ap_gl` | kr. | já | Lánardrottnar skv. fjárhag (jákvætt) | `period_breakdown` |
| `inv[]` | listi | já | Innkaupareikningar í samþykkt: `{doc, vno, vendor, amt, due, sent, ic, fx}`; `ic` = tengdur aðili, `fx` = mynt eða "" | `Purchase Header` (Document Type=Invoice, ósamþykkt) — sama og Kostnaður |
| `unbooked[]` | listi | já | Gjaldfallnar greiðslur sem vantar í bókhald: `{k, t, d, amt, note}`; `k` ∈ `laun, skattar, vsk, lan` | mat út frá ófullbókuðum mánuðum (`months[].complete=false`) og stöðu skuldalykla |
| `rec` | hlutur | já | Afstemmingargögn (notuð í Mánaðarlokum; haldið hér óbreyttum): `stmts[]{acc,name,stmt,ledger,outst}`, `gl6920_aug`, `gl6340_aug`, `gl6920`, `stemming[]{ym,mismunur}`, `loan[]` | `Bank Acc. Reconciliation`, `period_breakdown` |
| `banks[]` | listi | já | Bankareikningar og kort: `{no, name, teg, bal, stmt_date, stmt_no, stmt_bal, outst}`; `teg` = "Greiðslukort" fyrir kort | `Bank Account` (Staða á dagsetningu, FlowField) + síðasta `Bank Account Statement`. Kort sem númer, ekki nöfn korthafa |
| `banks_gl` | `{bankar, kort}` kr. | já | Bankar og kort skv. fjárhag | `period_breakdown` á bankalyklum |

## meta / text / html (texti utan DATA)

Reglur: stutt og staðreyndamiðað, íslenskt talnasnið („31,6 m.kr.“, „20.09.“). 

**Hvar gildin lenda.** `meta.*` og `text.*` fara aðeins í HTML (HTML-sloppin). `html.*` fer óbreytt í HTML (aðeins `<b>` og `<a href="x.html">`). `js.*` fer inn í JavaScript sem JSON-bókstafur (`json.dumps`), svo þar má vera hvaða texti sem er, líka gæsalappir, `'`, `` ` `` og `\`; tölur, listar og hlutir eru settir inn sem slíkir (ekki sem texti). Textar í `js` eru birtir sem HTML (innerHTML) þar sem þeir lenda í töflum og spjöldum: aðeins `<b>` og `<a href="x.html">`. Lykill sem er bæði í `meta` og `js` (t.d. `year`, `py`) á að hafa sama gildi í báðum. Valfrjálsir listar mega vera tómir (`[]`): þá er hlutinn falinn eða sýnir „Á ekki við“/„engin“ í stað villu.

| Lykill | Dæmi (DT) | Regla |
|---|---|---|
| `meta.company` | DT Vélsmiðjan ehf. | nefnifall |
| `meta.initials` | DT | merki |
| `meta.as_of` | 16.10.2026 | `today` á DD.MM.ÁÁÁÁ |
| `meta.fetched` | 16.–17.10.2026 | dagar gagnasóknar |
| `meta.fc_from`, `meta.fc_to` | 19.10.2026, 17.01.2027 | fyrsti og síðasti dagur 13 vikna |
| `meta.nw_default` | 71 | `round(coll_base × 100)` |
| `js.fc_sales_due` | ["2026-11-20", …] | 3 gjalddagar nýrrar sölu (20. næsta mánaðar, færður á virkan dag) |
| `js.fc_salary_dates` | ["2026-10-30", …] | 3 útborgunardagar launa (síðasti virki dagur) |
| `js.fc_wh_dates` | ["2026-11-16", …] | 3 gjalddagar staðgreiðslu (15., virkur dagur) |
| `js.fc_vendor_dates` | [["2026-11-16","14"], …] | `[dagsetning, lykill í ven]`: reglulegar lánardrottnagreiðslur innan spár |
| `js.days_since_rec` | 47 | dagar frá síðustu bankaafstemmingu |
| `js.bank_gl_accounts` | 6920, 6340 | fjárhagslyklar banka og korta |
| `js.unrec_period` | sep–okt | óafstemmt tímabil |
| `js.cur_month` | október | heiti yfirstandandi mánaðar |
| `js.base_period`, `js.slow_period` | Jan–ágú, júl–ágú | tímabil `coll_base`/`coll_slow` |
| `js.first_incomplete` | 2026-09 | fyrsti ófullbókaði mánuður (ÁÁÁÁ-MM) |
| `text.hist_period` | janúar til október 2026 | tímabil `cash_hist` |
| `js.bank_txt` | Þrír bankareikningar og þrjú fyrirtækjakort. … | 2–3 setningar um bankastöðu og afstemmingu |
| `js.bank_note` | Óafstemmt 31.08. er … | skýring á óafstemmdu; korthafar ekki nafngreindir |
| `js.hist_inc` | Sep–okt eru ófullbókaðir. | |
| `js.act2_title`, `js.act2_text` | Staðfesta hvort laun … voru greidd | aðgerð 2 í „Fyrst að gera“ |
| `js.act3_text` | Stálvogur á 31,6 m.kr. gjaldfallið frá 20.09. … | stærsti gjaldfallni lánardrottinn |
| `js.beyond_sale` | desembersala á gjalddaga 20.01.2027 | hvað fellur utan 13 vikna |
| `js.ag_trend_pre` / `js.ag_trend_post` | „Kröfur hafa hækkað úr “ / „ m.kr. í júní, sem skýrir sjóðsfallið.“ | utan um töluna `krofur_hist[ag_ref_idx]` |
| `js.warn_pre` / `js.warn_post` | „<b>September og október eru ófullbókaðir.</b> … samtals um “ / „ m.kr. Hvort sem …“ | viðvörunarborði utan um summu `unbooked` |
| `html.ap_note` | Staðgreiðsluafslættir: engir … | athugasemd undir reikningum í samþykkt |
| `html.footer_assumptions` | laun jan–ágú að meðaltali (51% …) … | forsendur spár, á eftir „Spá, ekki loforð. Forsendur:“ |
| `js.fc_vsk` | [["2026-12-07", 2]] | VSK-gjalddagar innan 13 vikna: `[dagsetning ÁÁÁÁ-MM-DD, fjöldi mánaða í uppgjöri]` (2 = tveggja mánaða tímabil, 1 = mánaðarskil, `null` → 2); `[]` ef enginn |
| `js.ag_ref_ym` | 2026-06 | mánuður (ÁÁÁÁ-MM í `months`) sem kröfuþróun er borin saman við; mánuður utan `months` → setningin fellur út |

**Valfrjálst / tómt leyft:** `unbooked: []` felur viðvörunarborðann; `js.first_incomplete: ""` þegar allir mánuðir eru fullbókaðir; `js.unrec_period: ""` sýnir „Afstemmt“ í bankatöflu; `inv`, `vend_open`, `nyd` og `js.fc_*`-listar mega vera tómir. Lánardrottnadagur í `js.fc_vendor_dates` sem er ekki lykill í `ven` telst 0.
