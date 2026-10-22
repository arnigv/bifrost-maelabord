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
| `cust[]` | listi | já | Viðskiptavinir með reikning á árinu: `{no, name, ic, one, new, first, pos?}`; `ic` = tengdur aðili, `one` = einskiptissala, `new` = engin staða í lok fyrra árs, `first` = fyrsti reikningur | `Customer` (1, 2) + `Cust. Ledger Entry`. Aðeins fyrirtækjanöfn; einstaklingar sem númer |
| `cust[].pos` | true/false | nei | Staðgreiðslu- eða kassaviðskiptavinur (t.d. „Staðgreiðsla Kringlan“, einn á verslun). Birtist í listanum merktur *staðgreiðsla* en er **ekki** talinn með í fjölda viðskiptavina, stærsta viðskiptavini, þremur stærstu eða samþjöppun (nefnari = reikningssala utan staðgreiðslu) | `Customer`: viðskiptavinur sem kassakerfi bókar á (oft `Customer Posting Group` eða heiti „Staðgreiðsla …“); staðfestu með notanda |
| `stores[]` | listi | nei | Sala eftir verslun eða staðsetningu: `{code, name, m: {ÁÁÁÁ-MM: kr}}`. Ef til: spjaldið „Sala eftir verslun“ í Viðskiptavinum (fylgir völdu tímabili) | `Data.Totals.Get` á `G/L Entry` tekjulykla (`groupBy` `Global Dimension 1 Code` eða 2, eftir því hvor víddin er verslun) á mánuð; varaleið `Value Entry` (`groupBy` `Location Code`, `Sales Amount (Actual)`) |
| `other_cle[]` | `[dags, viðskiptavinur, skjal, lýsing, kr]` | já (má vera tómt) | Dagbókarfærslur á viðskiptamenn | `Cust. Ledger Entry` án Document Type |
| `jobs[]` | listi | já (má vera tómt) | Verk: `{no, desc, cust, typ, contract, inv}`; `contract` 0 = innra verk. **Tómt = félag án verka** (verslun, heildsala): þá falla út lykilmælirinn „Bókað á verk“, spjaldið Verk, sían „Verk og tímar“, dálkurinn Klst. og verkathuganir í Tekjuleka (A, C, G), og textar um verk í heimild og aðferð | `Job` + `Job Planning Line` (samningsverð) + `Data.Totals.Get` á `Job Ledger Entry` (Sale) |
| `prices[]` | listi kr. | já (má vera tómt) | Einingarverð forða (kr./klst.). Tómt og engin verk = lykilmælirinn „Verðskrá vinnu“ fellur út og eining í verðdæmum verður `stk.` (nema `unit` sé gefið) | `Resource` (Unit Price) |
| `items[]` | listi | nei | Vörur eða vöruflokkar: `{no, name, rev, cost, m?}`; `rev` sala og `cost` kostnaðarverð seldra vara ár til dags (kr., jákvætt); `m` = `{ÁÁÁÁ-MM: [sala, kostnaður]}` svo taflan fylgi völdu tímabili (vanti `m` hjá einni línu gildir ár til dags fyrir allar). Ef til: spjaldið „Vörur og vöruflokkar“ (sala, framlegð, framlegð %, hlutdeild) og, án verka, lykilmælarnir „Framlegð af vörusölu“ og „Stærsti vöruflokkur“. Hámark 15 línur birtast | **Samtölur:** `Data.Totals.Get` á `Value Entry` (`Item Ledger Entry Type`=Sale, `groupBy` `Item Category Code` eða `Item No.`; `Sales Amount (Actual)`, `Cost Amount (Actual)` formerki snúið), eitt kall á mánuð eða `period_breakdown` |
| `leak` | hlutur | já | Tekjuleki (skill `tekjuleki`) | |
| `leak.items[]` | | já | `{k, t, job, cust, amt, v, yr, d, next}`; `k` = athugun A–H, `v` ∈ `S` staðfest, `L` líklegt, `A` athuga; `amt` sækjanlegt kr., `yr` árleg endurtekning. Án verka er `job` vara, vöruflokkur, skjal eða viðskiptavinur | með verkum: `Job Ledger Entry`, `Job Planning Line`; án verka: `Sales Invoice Line`, `Value Entry` (sjá skill `tekjuleki`) |
| `leak.src[]` | | já | Upprunalínur: `{no, desc, cust, kind, g, h, amt, v}`; `g` ∈ `verk` (aðeins með verkum), `zero` (0 kr. notkun eða 0 kr. sölulínur), `price` (afsláttur umfram venju, verð undir kostnaði eða verðskrá), `rof` (rof í endurteknum reikningum); `h` klst. (0 án verka; dálkurinn falinn) | sama |
| `leak.actions[]` | | já | `{t, once, yr, eff, v, next}` | samantekt |
| `leak.method[]` | `[athugun, staða, niðurstaða]` | já | Staða ∈ `Gert`, `Ekki gert`, `Á ekki við`, `Utan mælaborðs`. Án verka eru athuganir með `Á ekki við` taldar upp berum orðum í hero tekjuleka, og þriðji lykilmælirinn verður „Athuganir gerðar“ (`Gert` af þeim sem eiga við) | |
| `leak.leakJobs`, `leak.openJobs` | heiltala eða `null` | já (`null` án verka) | Verk með leka / opin verk. Lykilmælirinn „Verk og samningar með leka“ birtist aðeins ef `jobs` er ekki tómt og `openJobs` er ekki `null` | `Job` |
| `leak.priceNote`, `leak.today` | texti | já | Athugasemd um verð og afslætti; dagsetning greiningar | |
| `oneoff` | hlutur eða `null` | nei (`null` ef enginn einskiptisliður) | Stærsti einskiptisliður `{no, name, cat, ym, amount}` (jákvætt). Lykillinn þarf enn að vera til (render.py ber saman við sýnidæmið); settu `null`. Einskiptismerki í mælaborðinu ráðast af `E`-færslum með stoð `einsk`: engar slíkar = „án einskiptissölu“ í hero og „Vöxtur án einskiptis“ víkja fyrir viðmiði fyrra árs og hlutfalli á viðskiptamannabók, og „Einskipti 1×“ hverfur úr skýringu grafs | `dataset.json → oneoffs[0]` |

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
| `js.dq_note`, `js.dq_tail` | <b>Gagnagæði:</b> megnið af tekjunum …; Frá september … | hve stór hluti er á viðskiptamannabók. `""` = öll sala á viðskiptavini: gagnagæðaborðinn er falinn |
| `js.unreg_desc`, `js.unreg_drawer` | söludagbók (FHFBOK) á 1110 og leiðréttingar … | uppruni tekna án viðskiptavinar |
| `js.reg_py`, `js.reg_lost` | Öll sala 2025 var bókuð með dagbók. | skráning fyrra árs; hvort tapaða viðskiptavini megi greina |
| `js.onjob_note` | aðeins S-2603 hefur sölulínur á verki | |
| `js.non_gl_note` | allar línur á fjárhagslykil, engin vörunúmer | |
| `js.py_share_src`, `js.py_share_tail` | „er úr söludagbók ársins (sömu fjórar stoðir,“ / „Einskiptissala og aðrar tekjur voru engar 2025.“ | uppruni hlutdeildar fyrra árs |
| `js.price_note` | Fast verð og tilboð eru bókuð sem ein lína … | |
| `js.leak_txt` | Vinna sem þegar er unnin en hefur ekki verið rukkuð … | hero-texti tekjuleka |
| `js.leak_k1`, `leak_k2`, `leak_k3` | Varahlutir afhentir án gjalds. … | skýringar þriggja lykilmæla tekjuleka |
| `js.src_note_zero` | Varahlutir (Athuga) eru ekki taldir með … | |
| `js.price_examples` | [{"kind": "rate", "label": "Reglubundið viðhald", "match": "Reglubundið viðhald"}, …, {"kind": "oneoff", "label": "Tankakerfi", "acc": "1130"}] | dæmi í „Verð og afslættir“. `kind`: `rate` (einingarverð: fyrsta reikningslína sem byrjar á `match`), `fixed` (fast gjald: allar línur sem byrja á `match`), `oneoff` (fyrsta lína á lykli `acc`). Valfrjálst `unit` (t.d. `"stk."`, `"kg"`, `"klst."`): eining verðs; sjálfgefið `klst.` ef verk eða verðskrá forða, annars `stk.` (í `i18n.en` t.d. `"pcs"`). Dæmi sem finnst ekki er sleppt; `[]` → engin dæmi |

**Reiknað úr gögnum:** ársfjórðungar Q1–Q4 eftir mánuðum í `M` og sjálfgefinn ársfjórðungur (síðasti fullbókaði); einskiptismerki (1×) á reikningum ræðst af `E`-færslum með stoð `einsk` (fylgiskjal), ekki föstum viðskiptavini. `leak.items`, `leak.src`, `leak.actions`, `leak.method`, `prices`, `jobs` og `other_cle` mega vera tómir; `items` og `stores` mega vanta.

**Rekstrarform ræðst af gögnunum, aldrei af nafni félags:** verk = `jobs.length > 0`; vinna á verðskrá = `jobs` eða `prices` ekki tómt; vörusala = `items` ekki tómt; dagbókarsala = einhver `E`-færsla með tegund `dagb` (annars segir textinn „Öll sala er reikningsfærð á viðskiptavini“ og bráðabirgðamánuðir eru „vanmetnir þar til þeir hafa verið fullbókaðir“ í stað söludagbókar); línutegund: `js.non_gl_lines` > 0 = línur á vöru eða forða (fótur reikningsspjalds segir ekki „fjárhagslykil“, og dálkurinn Verk fellur út án verka).

## Tungumál (`lang`, `i18n`)

| Lykill | Dæmi | Skýring |
|---|---|---|
| `lang` | `"is"` | tungumál grunngagna (úr `dataset.json`). Ræður hvaða mál opnast fyrst. Vanti það er það greint úr heitum í gögnunum. |
| `i18n.en` (eða `i18n.is`) | `{"meta": {...}, "text": {...}, "html": {...}, "js": {...}, "names": {...}}` | yfirlag fyrir hitt málið. Sömu lyklar og að ofan, aðeins þeir sem breytast. Dagsetningar á ensku `17 Oct 2026`, tölur `1,234.5`. |
| `i18n.<lang>.names` | `{"Áætlun 2026": "Budget 2026"}` | þýðir heila strengi hvar sem er í gögnunum (heiti lykla utan staðaltöflu, áætlana, flokka, stöðu). |

Sjá `example.json` (yfirlagið `i18n.en`) og `bifrost-maelabord/SKILL.md`, kaflann *Tungumál*.
