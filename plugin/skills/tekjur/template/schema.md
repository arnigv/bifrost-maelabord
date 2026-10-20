# Tekjur: gagnaskema (DATA)

Gervigreindin fyllir aðeins þetta JSON og keyrir
`render.py --dashboard tekjur --data tekjur.json --out tekjur.html`. HTML er aldrei skrifað í höndunum.
`example.json` er gullútgáfan (DT Vélsmiðjan ehf.). `"_maps": ["py_stream"]` segir render.py að lyklar `py_stream` séu gögn.

**Formerki og einingar.** Fjárhæðir í **kr.** án VSK. Tekjur **jákvæðar**, afsláttur og bakfærslur neikvæð (öfugt við GL). Mánuðir `"ÁÁÁÁ-MM"`, dagsetningar `"ÁÁÁÁ-MM-DD"`.

## Lyklar

| Lykill | Tegund | Skylt | Merking | Hvaðan úr BC (Bifröst) |
|---|---|---|---|---|
| `today` | ÁÁÁÁ-MM-DD | já | Dagur gagnasóknar | |
| `asof` | ÁÁÁÁ-MM-DD | já | Staða tekjulekagreiningar | |
| `M[]` | listi ÁÁÁÁ-MM | já | Mánuðir yfirstandandi árs með gögnum | `dataset.json → months` |
| `inc` | kort `{ÁÁÁÁ-MM: skýring}` | já | Ófullbókaðir mánuðir og ástæða | `months[].complete=false` |
| `py` | kr. | já | Tekjur fyrra árs alls | Hreyfing (reitur 32) á tekjulyklum `G/L Account`, `Date Filter` fyrra árs (formerki snúið) |
| `py_stream` | kort `{stoð: kr}` | já | Tekjur fyrra árs á tekjustoð (lyklar úr `streams`) | flokkun færslna fyrra árs (sama regla og `E`) |
| `bud` | kort `{ÁÁÁÁ-MM: kr}` | já | Tekjuáætlun á mánuð (jákvæð) | `Finance.BudgetEntry.Get` á tekjulyklum (kafli 6b), formerki snúið |
| `bud_name`, `bud_desc` | texti | já | Heiti og lýsing áætlunar | `G/L Budget Name` |
| `streams[]` | listi `[lykill, heiti]` | já | Tekjustoðir í röð, t.d. `["tilbod","Tilboðsverk og verkefni"]`; sérlyklar `einsk` (einskipti), `adrar`, `afsl` (afsláttur) | flokkun eftir lýsingu færslu/reikningslínu |
| `E[]` | listi `[dags, lykill, fylgiskjal, lýsing, kr, tegund, viðskiptavinur, stoð]` | já | Allar tekjufærslur ársins. `tegund` ∈ `reikn` (sölureikningur), `dagb` (dagbók), `bakf` (bakfærsla); viðskiptavinur "" ef ekki reikn | `G/L Entry` á tekjulyklum (reitir 1, 3, 4, 6, 7, 17, 28, 58). Teldu fyrst með `data_record_count`; > 5.000 → regla bifrost-gogn kafli 0 lið 3 |
| `inv[]` | listi | já | Bókaðir sölureikningar ársins: `{doc, c, d, desc, net, gross, open, fx, lines}`; `net` án VSK, `gross` með VSK, `open` = ógreitt, `fx` = mynt eða "" | `Cust. Ledger Entry` (Invoice; Sales (LCY), Amount (LCY), Open) |
| `inv[].lines[]` | `[línunr, lykill, lýsing, magn, einingarverð, afsl %, kr, verk]` | já | Reikningslínur; `kr` í ISK | `Sales Invoice Line` (reitir 2, 3, 4, 6, 11, 15, 22, 27, 29, 45) |
| `cust[]` | listi | já | Viðskiptavinir með reikning á árinu: `{no, name, ic, one, new, first}`; `ic` = tengdur aðili, `one` = einskiptissala, `new` = engin staða í lok fyrra árs, `first` = fyrsti reikningur | `Customer` (1, 2) + `Cust. Ledger Entry`. Aðeins fyrirtækjanöfn; einstaklingar sem númer |
| `other_cle[]` | `[dags, viðskiptavinur, skjal, lýsing, kr]` | já (má vera tómt) | Dagbókarfærslur á viðskiptamenn | `Cust. Ledger Entry` án Document Type |
| `jobs[]` | listi | já | Verk: `{no, desc, cust, typ, contract, inv}`; `contract` 0 = innra verk | `Job` + `Job Planning Line` (samningsverð) + `Data.Totals.Get` á `Job Ledger Entry` (Sale) |
| `prices[]` | listi kr. | já | Einingarverð forða (kr./klst.) | `Resource` (Unit Price) |
| `leak` | hlutur | já | Tekjuleki (skill `tekjuleki`) | |
| `leak.items[]` | | já | `{k, t, job, cust, amt, v, yr, d, next}`; `k` = athugun A–H, `v` ∈ `S` staðfest, `L` líklegt, `A` athuga; `amt` sækjanlegt kr., `yr` árleg endurtekning | `Job Ledger Entry`, `Job Planning Line` |
| `leak.src[]` | | já | Upprunalínur: `{no, desc, cust, kind, g, h, amt, v}`; `g` ∈ `verk, zero, price`; `h` klst. | sama |
| `leak.actions[]` | | já | `{t, once, yr, eff, v, next}` | samantekt |
| `leak.method[]` | `[athugun, staða, niðurstaða]` | já | Staða ∈ `Gert`, `Ekki gert`, `Á ekki við`, `Utan mælaborðs` | |
| `leak.leakJobs`, `leak.openJobs` | heiltala | já | Verk með leka / opin verk | `Job` |
| `leak.priceNote`, `leak.today` | texti | já | Athugasemd um verð og afslætti; dagsetning greiningar | |
| `oneoff` | hlutur | já | Stærsti einskiptisliður `{no, name, cat, ym, amount}` (jákvætt) | `dataset.json → oneoffs[0]` |

## meta / text / html (texti utan DATA)

Reglur: stutt og staðreyndamiðað, íslenskt talnasnið. 

**Hvar gildin lenda.** `meta.*` og `text.*` fara aðeins í HTML (HTML-sloppin). `html.*` fer óbreytt í HTML (aðeins `<b>` og `<a href="x.html">`). `js.*` fer inn í JavaScript sem JSON-bókstafur (`json.dumps`), svo þar má vera hvaða texti sem er, líka gæsalappir, `'`, `` ` `` og `\`; tölur, listar og hlutir eru settir inn sem slíkir (ekki sem texti). Textar í `js` eru birtir sem HTML (innerHTML) þar sem þeir lenda í töflum og spjöldum: aðeins `<b>` og `<a href="x.html">`. Lykill sem er bæði í `meta` og `js` (t.d. `year`, `py`) á að hafa sama gildi í báðum. Valfrjálsir listar mega vera tómir (`[]`): þá er hlutinn falinn eða sýnir „Á ekki við“/„engin“ í stað villu.

| Lykill | Dæmi (DT) | Regla |
|---|---|---|
| `meta.company`, `meta.company_short`, `meta.company_gen`, `meta.initials` | DT Vélsmiðjan ehf. / DT Vélsmiðjan / DT Vélsmiðjunnar ehf. / DT | nefnifall, stutt, eignarfall, merki |
| `meta.year`, `meta.py` (og `js.year`, `js.py`) | 2026, 2025 | ár og fyrra ár |
| `meta.as_of` | 18.10.2026 | `today` DD.MM.ÁÁÁÁ |
| `meta.leak_as_of`, `meta.leak_fetched` | 16.10.2026, 16.–17.10.2026 | dagsetningar tekjulekagreiningar |
| `meta.fetched` | 16.–18.10.2026 | dagar gagnasóknar |
| `meta.rev_accounts` | 1000–1999 | bil tekjulykla |
| `meta.bc_env` | Bifrost | BC-umhverfi |
| `js.ytd_short` | jan–okt | `M` stytt |
| `js.disc_account` | 1140 | afsláttarlykill |
| `js.non_gl_lines` | 0 | fjöldi reikningslína á vöru/forða (tala sem texti) |
| `js.open_stream` | tilbod | stoð sem er opin í trénu í upphafi (lykill úr `streams`) |
| `js.acc_names` | {"1110": "Sala 24% VSK", "1130": …} | JSON-hlutur `{lykill: heiti}` tekjulykla (heiti mega innihalda hvaða staf sem er) |
| `html.footer_notes` | September og október eru ófullbókaðir … | athugasemdir í fæti |
| `js.one_incl` | að meðtalinni einskiptissölu til erlends viðskiptavinar í ágúst (1×) | |
| `js.streams_note` | Stoðir eru flokkaðar eftir lýsingu: … | hvernig stoðir eru flokkaðar |
| `js.inc_note` | Sep og okt eru ófullbókaðir og sýndir daufir. | |
| `js.dq_note`, `js.dq_tail` | <b>Gagnagæði:</b> megnið af tekjunum …; Frá september … | hve stór hluti er á viðskiptamannabók |
| `js.unreg_desc`, `js.unreg_drawer` | söludagbók (FHFBOK) á 1110 og leiðréttingar … | uppruni tekna án viðskiptavinar |
| `js.reg_py`, `js.reg_lost` | Öll sala 2025 var bókuð með dagbók. | skráning fyrra árs; hvort tapaða viðskiptavini megi greina |
| `js.onjob_note` | aðeins S-2603 hefur sölulínur á verki | |
| `js.non_gl_note` | allar línur á fjárhagslykil, engin vörunúmer | |
| `js.py_share_src`, `js.py_share_tail` | „er úr söludagbók ársins (sömu fjórar stoðir,“ / „Einskiptissala og aðrar tekjur voru engar 2025.“ | uppruni hlutdeildar fyrra árs |
| `js.price_note` | Fast verð og tilboð eru bókuð sem ein lína … | |
| `js.leak_txt` | Vinna sem þegar er unnin en hefur ekki verið rukkuð … | hero-texti tekjuleka |
| `js.leak_k1`, `leak_k2`, `leak_k3` | Varahlutir afhentir án gjalds. … | skýringar þriggja lykilmæla tekjuleka |
| `js.src_note_zero` | Varahlutir (Athuga) eru ekki taldir með … | |
| `js.price_examples` | [{"kind": "rate", "label": "Reglubundið viðhald", "match": "Reglubundið viðhald"}, …, {"kind": "oneoff", "label": "Tankakerfi", "acc": "1130"}] | dæmi í „Verð og afslættir“. `kind`: `rate` (tímaverð: fyrsta reikningslína sem byrjar á `match`), `fixed` (fast gjald: allar línur sem byrja á `match`), `oneoff` (fyrsta lína á lykli `acc`). Dæmi sem finnst ekki er sleppt; `[]` → engin dæmi |

**Reiknað úr gögnum:** ársfjórðungar Q1–Q4 eftir mánuðum í `M` og sjálfgefinn ársfjórðungur (síðasti fullbókaði); einskiptismerki (1×) á reikningum ræðst af `E`-færslum með stoð `einsk` (fylgiskjal), ekki föstum viðskiptavini. `leak.items`, `leak.src`, `leak.actions`, `leak.method`, `prices`, `jobs` og `other_cle` mega vera tómir.
