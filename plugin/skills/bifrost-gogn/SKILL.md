---
name: bifrost-gogn
description: "Gagnalag Bifröst-mælaborða: sækir og undirbýr gögn úr Business Central í gegnum Bifröst fyrir mælaborð pluginsins — samtölur fyrst (Data.Totals.Get, FlowFields, period_breakdown, aging), flokkun lykla, ófullbókaðir mánuðir, einskiptisliðir, samstæða og áætlanir; skilar dataset.json. Innra skill Bifröst-mælaborða: notað af hinum skillum pluginsins við smíði mælaborða. Ekki nota það eitt og sér og ekki fyrir önnur verkefni."
---

# Bifröst gagnalag

Öll mælaborð byggja á sömu gögnum svo tölurnar stemmi á milli þeirra. Þetta skill sækir þau **einu sinni í lotu** og skilar `dataset.json`.

**Aðeins lesið.** Notaðu aðeins lesaðgerðir Bifrastar (`outbound_invoke` með `Data.Totals.Get`, `period_breakdown`, `aging`, `data_record_count`, `data_batch_records`, `find_records`). Aldrei `inbound_invoke`, `inbound_queue` eða `set_records`.

**Samtölur fyrst, færslur aðeins þar sem þarf** (kafli 0). Það heldur keyrslunni hraðri og tölunum réttum upp á krónu, líka hjá félögum með hundruð þúsunda færslna á ári.

## 0. Samtölur fyrst (regla fyrir öll mælaborð)

BC leggur saman sjálft. Sæktu **aldrei færslur til að leggja þær saman** í skriftu eða í samhenginu.

| Spurning | Tól | Dæmi |
|---|---|---|
| Ein tala á hvert spjald (lykil, viðskiptavin, birgi, vöru, forða) fyrir tímabil eða á dagsetningu | **FlowField á spjaldinu** með FlowFilter í töflusýninni, t.d. Hreyfing á `G/L Account` eða Sala (SGM) á `Customer` (sjá *FlowFields fyrst* að neðan) | Rekstur á lykil, sala á viðskiptavin, innkaup á birgi, sala og birgðir á vöru, nýting forða |
| Hreyfing eða staða lykla á mánuði | `period_breakdown` á `G/L Account` (`net_change` eða `balance`, allt að 12 bil) | Rekstrarreikningur á mánuði, efnahagur í lok mánaðar |
| Summa eftir einum flokki á tímabili | `outbound_invoke` → `Data.Totals.Get` (`subject` = tafla, `data`: `fieldNumbers`, `groupBy`, `tableView`) | Tekjur á viðskiptavin, kostnaður á lykil eða birgi, kostnaður og verð á verk, tímar á forða |
| Kröfur og skuldir eftir aldri | `aging` | Aldursgreining, gjaldfallið |
| Fjöldi | `data_record_count` | Starfsemisgreining, fjöldi reikninga í samþykkt |
| Einstakar færslur | `data_batch_records` | Aðeins þar sem færslan sjálf skiptir máli (sjá neðst) |

**FlowFields fyrst þegar spurningin er „ein tala á hvert spjald“.** Aðaltöflur BC (lyklar, viðskiptamenn, lánardrottnar, vörur, forðar, bankareikningar) hafa reiknaða reiti (FlowFields) sem BC leggur saman eftir FlowFilters (`Date Filter`, víddir, birgðageymsla o.fl.). Notaðu þá **alltaf sem fyrsta val þegar það á við**:

- Svarið er ein tala á hverja færslu í aðaltöflu (lykil, viðskiptavin, birgi, vöru, forða) fyrir eitt tímabil eða á dagsetningu.
- Eitt kall (`data_batch_records`, `take` allt að 1000) skilar heiti og tölum allra spjaldanna, líka þeirra sem eru með 0.
- FlowFilters gefa sundurliðun sem `groupBy` á færslum getur ekki: deild, verk, rekstrareining, birgðageymsla.
- Mánaðarþróun sama reits: `period_breakdown` á sömu töflu (`balance_fields` = reitanúmerið, `field_type:"net_change"`), ekki bara á `G/L Account`.

Notaðu **`Data.Totals.Get`** í staðinn þegar flokkað er eftir einhverju sem er ekki spjald (dagsetning, fylgiskjal, tegund færslu, verk í verkbókarfærslum) eða þegar FlowField er lokaður (Field Access, sjá varaleið).

| Tafla | Reitir (prófaðir á DT 19.10.2026) | FlowFilters í töflusýn |
|---|---|---|
| `G/L Account` | 31 Staða á dagsetningu, 32 Hreyfing, 36 Staða | `Date Filter`, `Global Dimension 1 Filter`, `Global Dimension 2 Filter`, `Business Unit Filter` |
| `Customer` | 58 Staða, 59 Staða (SGM), 60 Hreyfing, 61 Hreyfing (SGM), 62 Sala (SGM), 63 Framlegð (SGM), 66 Gjaldfallið, 67 Gjaldfallið (SGM), 69 Greiðslur | `Date Filter`, víddasíur |
| `Vendor` | 58 Staða, 59 Staða (SGM), 60 Hreyfing, 61 Hreyfing (SGM), 62 Innkaup (SGM, jákvætt formerki), 66 Gjaldfallið, 67 Gjaldfallið (SGM), 69 Greiðslur | `Date Filter`, víddasíur |
| `Item` | 68 Birgðir, 70 Hreyfing (magn), 71 Innkaup (magn), 72 Sala (magn), 77 Innkaup (SGM), 78 Sala (SGM) | `Date Filter`, `Location Filter`, `Variant Filter` |
| `Resource` | 41 Afkastageta, 44 Notkun (magn), 45 Notkun (kostnaður), 46 Notkun (verð), 47 Sala (magn) | `Date Filter` |
| `Bank Account` | Staða á dagsetningu og Hreyfing (SGM); reitanúmer eru breytileg, flettu upp | `Date Filter` |

Prófun á DT (jan–ágú 2026): Sala (SGM) á K10 = 169.375.000 og Innkaup (SGM) á L10 = 225.856.800, sama og `Data.Totals.Get` á viðskiptamanna- og lánardrottnabók; Notkun (magn) á forða = sömu tímar og í verkbókarfærslum. Sala og innkaup á spjaldi hafa sömu takmörkun og undirbókin: færslur úr almennri dagbók eru ekki með.

Ekki sækja persónugreinanleg heiti með (t.d. `Name` á `Resource` eða bankareikningum korta): sæktu númer og notaðu kóða í mælaborðinu.

**Rekstur á lykil fyrir eitt tímabil (aðalleið).** Eitt kall gefur hreyfingu og heiti allra bókunarlykla:

```
data_batch_records → table "G/L Account", field_numbers [1,2,32], take 1000,
table_view "WHERE(No.=FILTER(1000..4999),Account Type=CONST(Posting),Date Filter=FILTER(2026-01-01..2026-08-31))"
```

- Prófað á DT 19.10.2026: allir 48 lyklar með hreyfingu stemmdu upp á krónu við `Data.Totals.Get` á `G/L Entry`. Lyklar án hreyfingar koma líka (0), sem er gagnlegt í samanburði við fyrra ár.
- Hreyfing virðir allar FlowFilters lykilsins: bættu `Global Dimension 1 Filter=CONST(<deild>)`, `Global Dimension 2 Filter=…` eða `Business Unit Filter=…` við töflusýnina til að fá tölur á deild, verk eða rekstrareiningu (sem `groupBy` á færslum getur ekki).
- Fyrra ár: sama kall með dagsetningu ári fyrr. Staða í lok tímabils: reitur 31 (*Balance at Date*) með `Date Filter=FILTER(..<lokadagur>)`.
- Dagsetningar í töflusýn alltaf `ÁÁÁÁ-MM-DD`.
- **Varaleið (gildir um alla FlowFields hér að ofan):** Hreyfing er FlowField. Ef notandinn er með *Read*- eða *Both*-línu í Bifröst Field Access getur reiturinn verið lokaður. Þá: `Data.Totals.Get` á `G/L Entry` (`[17]` Amount, `groupBy` `G/L Account No.`, sama dagsetningarsía) og heiti lykla úr `accounts.json`.

**Uppskriftir fyrir `Data.Totals.Get`** (staðlaðir BC-reitir; prófað á DT 19.10.2026, stemmdi upp á krónu við færslusummur):

| Þörf | `subject` | `fieldNumbers` | `groupBy` | `tableView` (dæmi) |
|---|---|---|---|---|
| Hreyfing á fjárhagslykil á tímabili (varaleið) | `G/L Entry` | `[17]` Amount | `G/L Account No.` | `WHERE(Posting Date=FILTER(2026-01-01..2026-08-31),G/L Account No.=FILTER(1000..4999))` |
| Sala á viðskiptavin | `Cust. Ledger Entry` | `[18]` Sales (LCY) | `Customer No.` | `WHERE(Posting Date=FILTER(…))` |
| Innkaup á lánardrottin | `Vendor Ledger Entry` | `[18]` Purchase (LCY), formerki í mínus | `Vendor No.` | `WHERE(Posting Date=FILTER(…))` |
| Kostnaður, verð og tímar á verk | `Job Ledger Entry` | `[9,13,15]` Quantity, Total Cost (LCY), Total Price (LCY) | `Job No.` | `WHERE(Entry Type=CONST(Usage))` (eða `Sale` fyrir reikningsfært) |
| Tímar og kostnaður á forða | `Job Ledger Entry` eða `Res. Ledger Entry` | magn og kostnaður | `No.` / `Resource No.` | `WHERE(Type=CONST(Resource))` |
| Sala á vöru | `Value Entry` | Sales Amount (Actual), Cost Amount (Actual) | `Item No.` | `WHERE(Item Ledger Entry Type=CONST(Sale),Posting Date=FILTER(…))` |
| Tekjur á vöru, þjónustu eða verk á reikningum | `Sales Invoice Line` | Amount, Quantity | `No.` eða `Job No.` | `WHERE(Posting Date=FILTER(…))` |
| Bankahreyfingar á reikning | `Bank Account Ledger Entry` | Amount (LCY) | `Bank Account No.` | `WHERE(Posting Date=FILTER(…))` |

Fáist villan „ekki af gerðinni tugabrot“ eða óþekktur reitur: flettu reitanúmerum upp með `describe_message_type` (`include_fields`) eða `Help.Fields.Get` og reyndu aftur. Reitanúmer geta verið önnur í sérsniðnum töflum.

**Takmarkanir og hvernig er farið í kringum þær**

- **Ein flokkun í kalli.** „Lykill × mánuður“: notaðu `period_breakdown`, eða Hreyfingu á `G/L Account` með einu kalli á mánuð. `groupBy` á `Posting Date` gefur dagsummur sem má leggja saman í mánuði ef þarf.
- **FlowFields** (t.d. *Amount (LCY)* og *Remaining Amount* í viðskiptamanna- og lánardrottnabók, *Balance* á lyklum) er hvorki hægt að leggja saman né flokka eftir. Notaðu geymda reiti (*Sales (LCY)*, *Purchase (LCY)*), `aging` fyrir opnar stöður og `period_breakdown` fyrir stöður lykla.
- **Field Access:** hjá notanda með einhverja *Read*- eða *Both*-línu teljast allar FlowFields lokaðar, líka í síum og röðun. Byggðu síur á geymdum reitum svo skillin virki með ráðlagðri öryggisuppsetningu.
- **Geymdir upphæðarreitir í undirbókum** ná aðeins yfir það sem var bókað sem skjal. *Sales (LCY)* og *Purchase (LCY)* eru 0 fyrir færslur úr almennri dagbók (t.d. tekjur bókaðar með dagbók eða kostnaður í erlendri mynt). Berðu því summu undirbókar saman við fjárhagslykilinn og segðu hve stór hluti er á undirbókinni (t.d. „um 30% tekna eru á viðskiptamannabók“).
- **Hvert kall telst skilaboð** í kvóta Bifrastar, en eitt samtölukall kemur í stað margra síðna af færslum.

**Færslur eru sóttar aðeins þegar færslan sjálf skiptir máli:**

1. **Opnar kröfur og skuldir með gjalddaga** fyrir sjóðspá (`Cust./Vendor Ledger Entry`, `Open=CONST(true)`, takmarkaðir reitir).
2. **Færsluprófanir og færsluvakt** (tvíreikningsfærsla, sléttar fjárhæðir, helgarfærslur, handfærðar tekjur): sæktu aðeins færslur sem uppfylla síu, t.d. `Source Code=FILTER(<>SALA)` á tekjulyklum, ekki alla töfluna.
3. **Drill-down í mælaborði: sama virkni og áður.** Samtölurnar breyta ekki því sem notandinn getur smellt á: allir liðir opnast niður í lykla, birgja, viðskiptavini eða verk (úr samtölum, alltaf heilt), og þaðan niður í færslur. Hvernig færslurnar fylgja með ræðst af fjölda, sem þú telur fyrst með `data_record_count` á sömu síu:
   - **≤ 5.000 færslur** á tímabili og svæði mælaborðsins (algengt hjá litlum og meðalstórum félögum): sæktu þær allar, eins og áður. Hver liður opnast niður í allar sínar færslur.
   - **Fleiri:** sæktu allar færslur fyrir stærstu liðina sem saman ná 80% af upphæðinni (mest 50 liðir), með síu á hvern lið. Aðrir liðir opnast niður á samtölustig (t.d. mánuð eða fylgiskjal) og sýna línuna „Spurðu gervigreindina: *sýndu færslurnar á bak við X*“. Segðu í fæti hve stór hluti upphæðarinnar er rekjanlegur niður í færslur í síðunni.
4. **Sýnishorn** fyrir lýsingar og dæmi (t.d. síðasti reikningur birgis): `take:1`–`5`.

Skráðu í `dataset.json` → `sources` hvaða tól skilaði hverri tölu (`totals`, `period_breakdown`, `aging`, `records`), svo hægt sé að rekja hana.

## 1. Velja félag

- `Context_Companies_List` (með `session_id` sem er stöðugt fyrir lotuna). Ef fleiri en eitt félag: spyrðu hvert, nema notandinn hafi nefnt það.
- Sendu `company_id` og `environment` **beint í hvert kall**. Treystu ekki á valið félag í lotunni.

## 1b. Eitt félag eða samstæða

Spyrðu einnar spurningar ef það er ekki ljóst: **„Eitt félag eða samstæða?“** og sýndu félögin sem notandinn hefur aðgang að.

- Ef samstæða: notandinn velur félögin (geta verið í mismunandi umhverfum). Bjóddu líkleg félög: þau sem birtast sem viðskiptamenn eða lánardrottnar hvert hjá öðru, eða bera sameiginlegt heiti. Spyrðu um **eignarhlut** í hverju dótturfélagi (sjálfgefið 100%).
- Keyrðu skref 2–5 **fyrir hvert félag** og vistaðu sem `dataset_<félag>.json`.
- Finndu **innbyrðis viðskipti** (sjá kafla 7) og sameinaðu með `build_consolidated.py`.

## 2. Starfsemisgreining (eitt kall á töflu)

`data_record_count` á þessar töflur (eða `data_batch_records` með `take:1` og `field_numbers:[1]` og lestu `noOfRecords`):

| Tafla | Merking ef > 0 |
|---|---|
| `Job`, `Job Ledger Entry` | Verkbókhald í notkun |
| `Item Ledger Entry` | Vörur og birgðir í notkun |
| `Resource` | Forðar (tímaskráning) |
| `Cust. Ledger Entry`, `Vendor Ledger Entry` | Viðskiptamenn / lánardrottnar |
| `Bank Account` (take 20, fields [1,2]) og `Bank Account Ledger Entry` | Bankareikningar í BC |
| `Bank Acc. Reconciliation` | Afstemmingar hafnar |

Vistaðu sem `profile.json`, t.d. `{"jobs":15,"items":16,"resources":6,"bank_accounts":6,"bank_entries":556,"reconciliations":0}`.

Mælaborðin nota þetta til að velja **vöru-, verk- eða þjónustusýn** og til að sleppa hlutum sem eiga ekki við (t.d. engin bankaafstemming ef engir bankareikningar eru í BC). Segðu það berum orðum í mælaborðinu frekar en að sýna tómt graf.

## 3. Bókhaldslyklar

`data_batch_records` á `G/L Account`, `field_numbers:[1,2,4,9,81]`, `table_view:"WHERE(Income/Balance=CONST(Income Statement),Account Type=CONST(Posting))"`, `take:500`. Vistaðu svarið óbreytt sem `accounts.json`. (Fyrir efnahag: sama með `Balance Sheet`.)

## 4. Hreyfingar á mánuði

`period_breakdown` á `G/L Account`, `balance_fields:[32]`, `field_type:"net_change"`, `identifier_fields:[1,2]`, sama `record_filter` og að ofan.

- Hámark er 12 bil í kalli. Kallaðu **tvisvar**: `as_of_date` = síðasti dagur yfirstandandi árs með `buckets:["1M","2M",…,"12M"]`, og sama fyrir fyrra ár.
- Vistaðu hvort svar óbreytt (`pl_ar.json`, `pl_fyrra.json`). Lestu alltaf `status` og `summary.complete`.

## 5. Smíða dataset.json

```
python3 ${CLAUDE_SKILL_DIR}/scripts/build_dataset.py --pl pl_ar.json --pl pl_fyrra.json \
  --accounts accounts.json --profile profile.json \
  --company "<nafn>" --env "<umhverfi>" --asof <YYYY-MM-DD> --out dataset.json
```

Skriftan:
- flokkar lykla í `tekjur, vorunotkun, laun, husnaedi, annar_rekstur, afskriftir, fjarmagn, oreglulegt, skattar` eftir nafni og undirflokki (ekki lyklanúmerum),
- reiknar mánaðarlega EBITDA og hagnað fyrir skatta (tekjur jákvæðar, kostnaður jákvæður),
- merkir **ófullbókaða mánuði** (sala en laun eða vörunotkun undir 20% af miðgildi, eða yfirstandandi mánuður),
- finnur **einskiptisliði** (lykill með hreyfingu í einum fullbókuðum mánuði og ≥ 10% af tekjum hans),
- skilar `ytd` (aðeins fullbókaðir mánuðir), `py_same_period` og `py_full`.

Skriftan prentar samantekt. **Berðu tekjur og EBITDA saman við** samtölu period_breakdown áður en haldið er áfram. Ef lyklar lenda í röngum flokki: leiðréttu `cat` í `dataset.json` og segðu notandanum frá því.

## 6. Viðbótargögn eftir mælaborði

| Þörf | Kall |
|---|---|
| Kröfur / skuldir eftir aldri | `aging` með `entity:"customer"` / `"vendor"`, `period_length:"1M"`, `number_of_periods:4` |
| Sala á viðskiptavin / innkaup á birgi | `Data.Totals.Get` (kafli 0) |
| Opnar kröfur með gjalddaga (sjóðspá) | `data_batch_records` á `Cust. Ledger Entry`, `WHERE(Open=CONST(true))`, aðeins reitir sem þarf |
| Verk og staða | `Job` (fields 1,3,5,13,14,19) og `Job Planning Line` (1,8,9,12,13,15,1001) sem færslur; **notkun og sala á verk sem samtölur** (`Data.Totals.Get` á `Job Ledger Entry`, `groupBy` `Job No.`, eitt kall fyrir `Usage` og eitt fyrir `Sale`) |
| Staða banka | `period_breakdown` á `Bank Account` með balance-svæði; hreyfingar sem samtölur á `Bank Account Ledger Entry` |
| Vörur | `Data.Totals.Get` á `Value Entry` eftir vöru; mánaðarþróun með einu kalli á mánuð eða `period_breakdown` á `Item` |

Gefðu `field_numbers` alltaf þegar færslur eru sóttar (svörin verða minni). Fáist villa um óþekkt svæðisnúmer, sæktu eina færslu án `field_numbers` til að sjá nöfnin og veldu svo.

## 6b. Fjárhagsáætlanir

- Áætlanir: `G/L Budget Name` (Name, Description, Blocked, budget-víddir). Færslur: `Finance.BudgetEntry.Get` (budgetName, dateFrom, dateTo, skip/take ≤ 1000) eða samanburður beint með `Finance.Budget.Compare` (budgetName, startDate, endDate, periodLength `<1M>`, accountFilter, víddasíur).
- Settu í `dataset.json` sem `budgets: [{name, desc, src: "bc", acc: {lykill: {"ÁÁÁÁ-MM": fjárhæð}}}]` með sama formerki og fjárhagur (tekjur í mínus).
- Ef `roster` vantar Finance.Budget-tegundirnar: keyrðu `refresh_roster` og reyndu aftur.
- Aldrei skrifa í áætlun nema notandi biðji um það og samþykki (`Finance.BudgetEntry.Set`).

## 7. Samstæða: innbyrðis viðskipti og samstæðugögn

Finndu og skráðu í `eliminations.json` (sjá snið í skriftunni):

| Tegund | Hvernig fundið | Jöfnun |
|---|---|---|
| `rekstur` | Viðskiptamenn í félagi A sem eru önnur félög í samstæðunni: sala á mánuði sem samtala (`Data.Totals.Get` á `Cust. Ledger Entry`, `Customer No.` síað á samstæðufélögin, `groupBy` `Posting Date` eða eitt kall á mánuð). Staðfestu mótlið hjá kaupanda (oftast annar rekstur eða vörunotkun) með því að bera saman fjárhæðir á mánuði. | Lækkar tekjur seljanda og kostnað kaupanda jafnt. EBITDA samstæðu breytist ekki. |
| `ardur` | Lyklar með „arð“ hjá móðurfélagi, og lækkun á óráðstöfuðu eigin fé hjá dótturfélagi sama mánuð. | Fellur út úr fjármunatekjum. Hagnaður samstæðu lækkar. |
| `fjarmagn` | Vaxtatekjur „frá tengdum aðilum“ á móti vaxtagjöldum hjá öðru félagi í samstæðunni. | Fellur út báðum megin. |
| `stada` | Opnar kröfur og skuldir milli samstæðufélaga (`aging` með `entity_filter` á viðkomandi viðskiptamann/lánardrottinn). | Lækkar kröfur og skammtímaskuldir samstæðu. |

Ef mótliður finnst ekki hjá hinu félaginu (t.d. það er ekki í úrtakinu): skráðu það sem **óstaðfest** og segðu frá því.

```
python3 ${CLAUDE_SKILL_DIR}/scripts/build_consolidated.py \
  --entity "Móðurfélag=dataset_mod.json" --entity "Dóttir=dataset_dottir.json@0.8" \
  --elim eliminations.json --name "<Heiti samstæðu>" --out dataset.json
```

Úttakið hefur sama snið og `dataset.json` fyrir eitt félag, auk `entities` (tölur hvers félags) og `eliminations`. Mælaborðin virka því óbreytt, og sýna að auki skiptingu eftir félögum (sjá `bifrost-maelabord`). Fullbókaðir mánuðir samstæðu eru aðeins þeir sem eru fullbókaðir hjá **öllum** félögum.

## Gildrur sem prófanir leiddu í ljós

- **Efnahagur er staða á dagsetningu, rekstur er tímabil.** Sýndu handbært fé og kröfur á nýjustu stöðu (t.d. í dag), en rekstrarsamtölur aðeins fyrir fullbókaða mánuði. Berðu aldrei aldursgreiningu í dag saman við fjárhagsstöðu eldri mánaðar.
- **Fjárhagur á móti undirbók.** Berðu kröfur í fjárhag saman við `aging`-samtölu sama dags. Munur er afstemmingaratriði og fer í *Gæði gagna*.
- **Stemming innan mánaðar.** `balance.stemming` sýnir mánuði þar sem hreyfingar efnahags og rekstrar standast ekki á (færslur með mismunandi dagsetningu á línum). Sýndu það sem gæðaatriði.
- **Eigið fé** er reiknað sem eignir að frádregnum skuldum, því rekstur fyrri ára er oft ekki lokaður inn á eigið fé.
- **Innbyrðis gjöld í samstæðu.** Í prófun var umsýslugjald móðurfélags (2,4 m.kr. á mánuði, undanþegið VSK) bókað sem „annar rekstrarkostnaður“ hjá dótturfélagi og hefði litið út sem nýr kostnaðarliður. Í samstæðu fellur það út.
- **Eignarhaldsfélög.** Arður og vaxtatekjur frá dótturfélögum eru fjármagnsliðir, ekki rekstrartekjur. Rekstrartekjur geta verið litlar (umsýslugjöld) og hagnaðurinn komið úr fjármagnsliðum.
- **Reikningsdagur á eftir notkun.** Hjá veitum og áskriftum er reikningur oft dagsettur fyrsta dag næsta mánaðar. Fyrsti mánuður ársins getur þá verið tómur. Segðu það frekar en að kalla hann ófullbókaðan.
- **Félag án bankareikninga í BC** (greiðslur bókaðar beint á fjárhagslykil): engin bankaafstemming möguleg. Segðu það berum orðum.

## Persónuupplýsingar

Bankareikningar, forðar og kort geta borið nöfn einstaklinga. Haltu þeim í gögnunum ef þarf til útreikninga, en mælaborð sýna kóða (t.d. `KORT-01`) nema notandinn biðji annað.
