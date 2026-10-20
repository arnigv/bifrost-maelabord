# Stjórn: gagnaskema (DATA)

Gervigreindin fyllir aðeins þetta JSON og keyrir
`render.py --dashboard stjorn --data stjorn.json --out stjorn.html`. HTML er aldrei skrifað í höndunum.
`example.json` er gullútgáfan (DT Vélsmiðjan ehf.) og sýnir nákvæma lögun.

**Formerki og einingar.** Allar fjárhæðir í **kr.** (ekki m.kr.; síðan deilir sjálf). Mánuðir sem `"ÁÁÁÁ-MM"`, dagsetningar sem `"ÁÁÁÁ-MM-DD"`.
- `months[*]`: tekjur og kostnaðarliðir **jákvæðir** (kostnaður sem jákvæð tala).
- `accounts[*].months` og `budgets[*].acc`: **GL-formerki** (tekjur neikvæðar, gjöld jákvæð). Síðan snýr þeim.
- `balance`: eignir jákvæðar; `eigid_fe`, `langtimaskuldir`, `skammtimaskuldir` jákvæð í `categories` en með GL-formerki (neikvæð) í `balance.accounts[*].levels`.

Skylt = verður að vera til (render.py stöðvar annars). Valfrjálst = má vera tómur listi/`null` (`fc: null` felur spáspjaldið, `budgets: []` og `spa: []` fela þá samanburði).

## Lyklar

| Lykill | Tegund | Skylt | Merking | Hvaðan úr BC (Bifröst) |
|---|---|---|---|---|
| `as_of` | texti ÁÁÁÁ-MM-DD | já | Dagsetning stöðu (sjóður, kröfur) | dagur gagnasóknar, `dataset.json → as_of` |
| `company` | texti | já | Heiti félags | `Context_Companies_List` / `dataset.json → company` |
| `months[]` | listi | já | Einn hlutur á mánuð yfirstandandi árs, jan → síðasta mánaðar með hreyfingu | `dataset.json → months` (bifrost-gogn kafli 4–5: `period_breakdown` á `G/L Account`, reitur 32 net_change, 1M bil) |
| `months[].ym` | ÁÁÁÁ-MM | já | Mánuður | |
| `months[].complete` | bool | já | `false` = ófullbókaður (laun/vörunotkun vantar eða yfirstandandi mánuður) | `build_dataset.py` merkir |
| `months[].tekjur, vorunotkun, laun, husnaedi, annar_rekstur, afskriftir, fjarmagn, oreglulegt` | tala kr., + | já | Summa lykla í flokki á mánuði | flokkun `build_dataset.py` (kafli 5) |
| `months[].ebitda` | tala kr. | já | tekjur − vörunotkun − laun − húsnæði − annar rekstur | reiknað |
| `months[].hagnadur_fs` | tala kr. | já | EBITDA − afskriftir − fjármagnsliðir − óreglulegt | reiknað |
| `oneoffs[]` | listi | já (má vera tómur) | Einskiptisliðir: `{no, name, cat, ym, amount}`; `amount` jákvætt kr. | `dataset.json → oneoffs` (lykill með hreyfingu í einum fullbókuðum mánuði ≥ 10% tekna) |
| `accounts[]` | listi | já | Allir rekstrarlyklar: `{no, name, cat, months}` | `G/L Account` (reitir 1, 2) + `period_breakdown` |
| `accounts[].cat` | texti | já | Einn af `tekjur, vorunotkun, laun, husnaedi, annar_rekstur, afskriftir, fjarmagn, oreglulegt` | flokkun `build_dataset.py` |
| `accounts[].months` | kort `{"ÁÁÁÁ-MM": kr, "<fyrra ár>": kr}` | já | Hreyfing á mánuð (GL-formerki) **og** lykillinn `"<meta.py>"` (t.d. `"2025"`) = hreyfing alls fyrra árs | mánuðir: `period_breakdown`; fyrra ár: Hreyfing (reitur 32) á `G/L Account` með `Date Filter` fyrra árs (kafli 0) |
| `balance.months` | listi ÁÁÁÁ-MM | já | Mánaðarlok sem efnahagur er sýndur fyrir; síðasti má vera yfirstandandi mánuður (staða `as_of`) | |
| `balance.categories.{fastafjarmunir, krofur, handbaert_fe, eignir, eigid_fe, eigid_fe_bokad, afkoma_arsins, langtimaskuldir, skammtimaskuldir}` | listi kr. (jafnlangur `balance.months`) | já | Staða flokka í lok hvers mánaðar. `eigid_fe_bokad` = bókað eigið fé án afkomu ársins; `afkoma_arsins` = uppsafnaður hagnaður ársins | `period_breakdown` á `G/L Account` (efnahagslyklar, `field_type:"balance"`, reitur 31) |
| `balance.accounts[]` | listi | já | `{no, name, cat, levels[]}` efnahagslyklar; `levels` = staða í lok hvers mánaðar, GL-formerki | sama kall |
| `aging.rows[]` | listi | já | Viðskiptavinir raðaðir eftir `total` (stærst fyrst): `{no, name, total, overdue}` kr. | `aging` (`entity:"customer"`, `period_length:"1M"`) |
| `aging.total`, `aging.not_yet_due`, `aging.b61` | tala kr. | já | Opið alls, ekki gjaldfallið, eldra en 60 daga | `aging` |
| `aging.buckets` | listi `[heiti, kr]` (6) | já | Ekki gjaldfallið, 0–30, 31–60, 61–90, 91–120, yfir 120 dagar | `aging` |
| `spa[]` | listi | valfrjálst | Spá gerð mánuði fyrir fram: `{ym, tekjur, vorunotkun, laun, husnaedi, annar_rekstur}` kr. + | Spágerð (skill `spagerd`, rúllandi spá) |
| `budgets[]` | listi | valfrjálst | `{name, desc, src:"bc"\|"draft", acc:{lykill:{ÁÁÁÁ-MM: kr}}}`, GL-formerki | `G/L Budget Name` + `Finance.BudgetEntry.Get` (kafli 6b); drög merkt `src` ≠ `"bc"` |
| `fc` | hlutur eða `null` | valfrjálst | Spá Bifrastar út árið | skill `spagerd` |
| `fc.rolling[]` | listi | | `{ym, spa_tekjur, spa_ebitda, raun_tekjur, raun_ebitda, einskipti, p10, p90, t10, t90, lidir:{vorunotkun\|laun\|husnaedi\|annar_rekstur:{spa, raun}}}` kr. | spagerd (bakprófun mánaðar fyrir mánuð) |
| `fc.forecast[]` | listi | | Spámánuðir yfirstandandi árs: `{ym, tekjur, ebitda, tekjur_p10, tekjur_p90, ebitda_p10, ebitda_p90}` | spagerd |
| `fc.year` | hlutur | | `raun_tekjur, raun_ebitda, spa_tekjur, spa_ebitda, p10_ebitda, p90_ebitda, ar_tekjur, ar_ebitda` kr.; `raun_*` = fullbókaðir mánuðir, `spa_*` = spámánuðir (P50), `p10_ebitda`/`p90_ebitda` = P10/P90 EBITDA spámánaðanna samanlagt (síðan leggur `raun_ebitda` við), `ar_*` = raun + spá | spagerd |
| `fc.backtest` | hlutur | | `{manudir:[ÁÁÁÁ-MM], mape_tekjur, mape_ebitda}` (hlutföll, 0,105 = 10,5%) | spagerd |

## meta / text / html (texti utan DATA)

Reglur: stutt og staðreyndamiðað, tölur á íslensku sniði („1.234,5 m“, „31.08.2026“). `meta`/`text` eru HTML-sloppin. 

**Hvar gildin lenda.** `meta.*` og `text.*` fara aðeins í HTML (HTML-sloppin). `html.*` fer óbreytt í HTML (aðeins `<b>` og `<a href="x.html">`). `js.*` fer inn í JavaScript sem JSON-bókstafur (`json.dumps`), svo þar má vera hvaða texti sem er, líka gæsalappir, `'`, `` ` `` og `\`; tölur, listar og hlutir eru settir inn sem slíkir (ekki sem texti). Textar í `js` eru birtir sem HTML (innerHTML) þar sem þeir lenda í töflum og spjöldum: aðeins `<b>` og `<a href="x.html">`. Lykill sem er bæði í `meta` og `js` (t.d. `year`, `py`) á að hafa sama gildi í báðum. Valfrjálsir listar mega vera tómir (`[]`): þá er hlutinn falinn eða sýnir „Á ekki við“/„engin“ í stað villu.

| Lykill | Dæmi (DT) | Regla |
|---|---|---|
| `meta.company` | DT Vélsmiðjan ehf. | nefnifall, fullt heiti |
| `meta.company_short` | DT Vélsmiðjan | án „ehf.“ (síðutitill) |
| `meta.company_gen` | DT Vélsmiðjunnar ehf. | eignarfall |
| `meta.initials` | DT | 1–3 stafir í merki |
| `meta.as_of` | 16.10.2026 | `as_of` á DD.MM.ÁÁÁÁ |
| `meta.last_closed` | 31.08.2026 | síðasti dagur síðasta fullbókaða mánaðar |
| `meta.ytd_label` | janúar–ágúst 2026 | fullbókaðir mánuðir ársins |
| `meta.year`, `meta.py` (og `js.year`, `js.py`) | 2026, 2025 | yfirstandandi ár og fyrra ár (texti). `py` verður líka að vera lykill í `accounts[].months` |
| `js.bil_from` | 2026-04 | sjálfgefið upphaf „Valið bil“ (ÁÁÁÁ-MM, t.d. 4 mánuðum fyrir síðasta fullbókaða) |
| `text.fc_actual_range` | janúar til ágúst | raunmánuðir í spágrafi |
| `text.fc_forecast_range` | september til desember | spámánuðir |
| `text.prelim_months` | september og október eru bráðabirgðatölur | ófullbókaðir mánuðir |
| `js.h_cash_lead` | Hagnaðurinn hefur hins vegar ekki skilað sér í sjóð: handbært fé hefur lækkað um | á undan „X m.kr. frá lokum <mánaðar>“; skrifa eftir því hvort sjóður hækkaði eða lækkaði |
| `js.ins1_title` … `js.ins4_title` | Reksturinn skilar meiru á hverja krónu | fyrirsagnir innsýnar (afkoma, sjóður, viðskiptavinir, áhætta) á stjórnarmáli |
| `js.ins1_lead` | Tekjuvöxtur hefur ekki dregið kostnað með sér: laun eru | á undan „X% af tekjum á móti Y% í fyrra“ |
| `js.ins1_one` | Ein stór sala til erlends viðskiptavinar í ágúst | lýsing einskiptisliðar á undan „(X m.kr.) er einskiptis“ |
| `js.ins2_tail`, `ins3_tail`, `ins4_tail` | Lagt til að stjórn óski eftir innheimtuáætlun … | lokasetning hverrar innsýnar: tillaga/ályktun |
| `js.one_desc` | stök sala til erlends viðskiptavinar | stutt lýsing einskiptisliðar (lágstafir) |
| `js.one_sale` | Sala til erlends viðskiptavinar | sama, hástafur í upphafi (áhættuskrá) |
| `js.dep_accounts` | ["5160"] | listi efnahagslykla uppsafnaðra afskrifta (óbeint sjóðstreymi); tómur listi → afskriftir 0 |

**Reiknað úr gögnum (ekki í meta):** fyrsta mánaðarlok og upphaf sjóðstreymis (úr `balance.months`), sjálfgefinn ársfjórðungur í Rekstri (síðasti fullbókaði ársfjórðungur, annars sá síðasti með fullbókuðum mánuði; Q1–Q4 eftir því hvaða mánuðir eru í `months`), hlutar sjóðstreymis (lok hvers ársfjórðungs á undan síðasta fullbókaða mánuði, sá mánuður og nýjasta staða). `oneoffs`, `budgets`, `spa`, `fc.rolling`, `fc.forecast` og `aging.rows` mega vera tómir.
