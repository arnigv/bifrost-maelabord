---
name: bifrost-gogn
description: Sækir og undirbýr gögn úr Business Central í gegnum Bifröst fyrir mælaborð — flokkar bókhaldslykla, greinir tímabil, ófullbókaða mánuði, einskiptisliði og hvaða starfsemi félagið notar (vörur, verk, þjónusta, bankar) og skilar dataset.json. Notaðu á undan hverju Bifröst-mælaborði, eða þegar beðið er um rekstrartölur, mánaðaryfirlit eða samanburð við fyrra ár úr BC.
---

# Bifröst gagnalag

Öll mælaborð byggja á sömu gögnum svo tölurnar stemmi á milli þeirra. Þetta skill sækir þau **einu sinni í lotu** og skilar `dataset.json`.

**Aðeins lesið.** Notaðu aðeins lesaðgerðir Bifrastar (`data_batch_records`, `period_breakdown`, `aging`, `data_record_count`, `find_records`). Aldrei `inbound_invoke`, `inbound_queue` eða `set_records`.

## 1. Velja félag

- `Context_Companies_List` (með `session_id` sem er stöðugt fyrir lotuna). Ef fleiri en eitt félag: spyrðu hvert, nema notandinn hafi nefnt það.
- Sendu `company_id` og `environment` **beint í hvert kall**. Treystu ekki á valið félag í lotunni.

## 1b. Eitt félag eða samstæða

Spyrðu einnar spurningar ef það er ekki ljóst: **„Eitt félag eða samstæða?“** og sýndu félögin sem notandinn hefur aðgang að.

- Ef samstæða: notandinn velur félögin (geta verið í mismunandi umhverfum). Bjóddu líkleg félög: þau sem birtast sem viðskiptamenn eða lánardrottnar hvert hjá öðru, eða bera sameiginlegt heiti. Spyrðu um **eignarhlut** í hverju dótturfélagi (sjálfgefið 100%).
- Keyrðu skref 2–5 **fyrir hvert félag** og vistaðu sem `dataset_<félag>.json`.
- Finndu **innbyrðis viðskipti** (sjá kafla 7) og sameinaðu með `build_consolidated.py`.

## 2. Starfsemisgreining (eitt kall)

`data_batch_records` með `take:1` og `field_numbers:[1]` á þessar töflur og lestu `noOfRecords`:

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
| Opnar kröfur á viðskiptamann | `data_batch_records` á `Cust. Ledger Entry`, `WHERE(Open=CONST(true))` |
| Verk og staða | `Job` (fields 1,3,5,13,14,19), `Job Ledger Entry` (2,3,4,5,7,8,9,13,15,1000), `Job Planning Line` (1,8,9,12,13,15,1001), `Job Task` (1,2,3,4) |
| Staða banka | `period_breakdown` á `Bank Account` með balance-svæði, eða `Bank Account Ledger Entry` |
| Vörur | `Item Ledger Entry` og `Value Entry` eftir vöru og mánuði |

Gefðu `field_numbers` alltaf þegar hægt er (svörin verða minni). Fáist villa um óþekkt svæðisnúmer, sæktu eina færslu án `field_numbers` til að sjá nöfnin og veldu svo.

## 6b. Fjárhagsáætlanir

- Áætlanir: `G/L Budget Name` (Name, Description, Blocked, budget-víddir). Færslur: `Finance.BudgetEntry.Get` (budgetName, dateFrom, dateTo, skip/take ≤ 1000) eða samanburður beint með `Finance.Budget.Compare` (budgetName, startDate, endDate, periodLength `<1M>`, accountFilter, víddasíur).
- Settu í `dataset.json` sem `budgets: [{name, desc, src: "bc", acc: {lykill: {"ÁÁÁÁ-MM": fjárhæð}}}]` með sama formerki og fjárhagur (tekjur í mínus).
- Ef `roster` vantar Finance.Budget-tegundirnar: keyrðu `refresh_roster` og reyndu aftur.
- Aldrei skrifa í áætlun nema notandi biðji um það og samþykki (`Finance.BudgetEntry.Set`).

## 7. Samstæða: innbyrðis viðskipti og samstæðugögn

Finndu og skráðu í `eliminations.json` (sjá snið í skriftunni):

| Tegund | Hvernig fundið | Jöfnun |
|---|---|---|
| `rekstur` | Viðskiptamenn í félagi A sem eru önnur félög í samstæðunni: sala á mánuði úr `Cust. Ledger Entry` (tegund reikningur). Staðfestu mótlið hjá kaupanda (oftast annar rekstur eða vörunotkun) með því að bera saman fjárhæðir á mánuði. | Lækkar tekjur seljanda og kostnað kaupanda jafnt. EBITDA samstæðu breytist ekki. |
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
