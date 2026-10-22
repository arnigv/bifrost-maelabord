# Mánaðarlok og afstemmingar: gagnalýsing (`DATA`)

Sniðmát: `template.html`. Smíða: `render.py --dashboard manadarlok --data manadarlok.json --out build/manadarlok.html`. Allir lyklar í `example.json` eru **skylda** (lyklar merktir *valfrjálst* hér að neðan mega vanta). Fjárhæðir í **krónum**. Formerki eins og í BC nema annað sé tekið fram. Allt sótt með lesköllum (`bifrost-gogn` kafli 0); ekkert bókað, afstemmt eða lokað í BC.

## Grunnur

| Lykill | Tegund | Merking | Úr BC |
|---|---|---|---|
| `today` | `ÁÁÁÁ-MM-DD` | Stöðudagur | Dagurinn sem gögn eru sótt |
| `company` | texti | Heiti félags (sama og `meta.company`) | `Company Information` |
| `default` | `ÁÁÁÁ-MM` | Mánuður sem er valinn við opnun (síðasti liðni mánuður); ef hann er ekki í `months` er síðasti mánuður valinn | reiknað |
| `jobs_n` | heiltala | Fjöldi opinna verka. **0 ef félagið notar ekki verkbókhald**: þá eru gátlistaatriði `verk` og línur með `"if": "jobs_n"` (t.d. áfangar, verk í vinnslu) faldar. Í stað `jobs_n` má senda listann `jobs` (lengdin gildir) | `Job` (Status = Open), `Data.Totals.Get` / talning |
| `inventory` | `{gl, subledger, date, ym}`, *valfrjálst* | Birgðir: `gl` = staða birgðalykla í fjárhag, `subledger` = virði birgða í birgðabók (summa `Cost Amount (Actual)` + `(Expected)` ef bókað er áætlað), bæði í kr. á `date`; `ym` = mánuðurinn sem samanburðurinn á við (sjálfgefið `default`). Vanti lykilinn eða báðar tölur eru 0 telst félagið ekki með birgðir og birgðaatriði eru falin | `Data.Totals.Get` á `Value Entry` (summa kostnaðar til `date`) á móti stöðu birgðalykla (`Inventory Posting Setup` → „Inventory Account“) |
| `birgdir` | tala, kr., *valfrjálst* | Birgðastaða án samanburðar. > 0 sýnir gátlistaatriði `birgd` sem koma úr gögnum, en sniðmátið reiknar ekki afstemmingu | Staða birgðalykla |

## `months[]`: gátlisti á mánuð (flipi Lokun mánaðar)

Einn hlutur á mánuð frá janúar til stöðumánaðar (síðustu 6 sýndir í mánaðavali). Verður að innihalda a.m.k. einn fullbókaðan mánuð.

| Reitur | Tegund | Merking |
|---|---|---|
| `ym` | `ÁÁÁÁ-MM` | Mánuður |
| `complete` | true/false | Fullbókaður (tekjur og helstu rekstrarliðir félagsins bókaðir, t.d. laun og vörunotkun ef þau eiga við) |
| `reason` | texti eða null | Ástæða ef ófullbókaður („laun vantar, vörunotkun vantar“) |
| `current` | true/false | Yfirstandandi mánuður |
| `items[]` | listi | Gátlistaatriði í þessari röð með `k`: `tekjur`, `laun`, `voru`, `birgd`, `verk`, `afskr`, `kortupp`, `vsk`, `fx`, `accr`, `lok`. Almenn atriði fyrir öll félög: `tekjur`, `afskr`, `vsk`, `fx`, `accr`, `lok`. Eftir rekstri: `laun` (sleppt ef engin laun), `voru` (sleppt ef engin vörunotkun; heiti „Birgðabreyting/vörunotkun bókuð“ hjá félagi með birgðir), `birgd` „Birgðir stemma við fjárhag (birgðabók á móti birgðalykli)“ (aðeins ef birgðir, sjá `inventory`), `verk` „Verk í vinnslu og áfangar bókuð“ (aðeins ef `jobs_n` > 0), `kortupp` „Kortauppgjör stemmir við uppgjör færsluhirðis“ (aðeins ef `banks` hefur reikning af tegundinni „Kortauppgjör“). Sniðmátið felur `birgd`, `verk` og `kortupp` þegar gögnin sýna ekki birgðir, verk eða kortauppgjör, og bætir `birgd` og `kortupp` sjálft við samanburðarmánuðinn (`inventory.ym` eða `default`) ef þau vantar |

Hvert atriði í `items[]`:

| Reitur | Tegund | Merking |
|---|---|---|
| `k` | texti | Lykill atriðis (sjá að ofan) |
| `t` | texti | Heiti („Laun bókuð“, „VSK-uppgjörsfærsla“, „Tímabil lokað í BC“ …) |
| `s` | texti | Staða: `lokid`, `vantar` eða `na` (á ekki við) |
| `amt` | tala, kr., eða null | Fjárhæð bókuð í mánuðinum, eða áætluð ef `est` |
| `est` | true/false | Fjárhæð er áætluð (sýnd með ≈) |
| `flag` | true/false, valfrjálst | Sýnir „Athuga“ |
| `role` | texti | Ábyrgð sem hlutverk: „Bókari“ eða „Fjármálastjóri“ (síurnar í Opnum atriðum nota þessi tvö gildi) |
| `note` | texti | Ein til tvær setningar um stöðuna |

Heimildir: Hreyfing á mánuð úr `dataset.json` (`months[]`: `tekjur`, `laun`, `vorunotkun`, `afskriftir`, `husnaedi`) og `period_breakdown` á `G/L Account` (afskriftalyklar, vaxtagjöld 4220, VSK-lyklar 9510–9540). Lyklanúmerin eru dæmi úr DT; notaðu lykla félagsins. Ófullbókuðum atriðum er gefin áætluð fjárhæð úr síðasta fullbókaða mánuði. VSK: tveggja mánaða tímabil, uppgjör í lok sléttu mánaðanna; fjárhæð = breyting útskatts og innskatts yfir tímabilið. Gengismunur: opnar færslur í erlendri mynt (`Cust./Vendor Ledger Entry`, Currency Code≠'') á móti `Currency Exchange Rate` og `Exch. Rate Adjmt. Reg.`. Tímabil lokað: `General Ledger Setup` (Allow Posting From/To), `User Setup`, `Accounting Period` (Closed).

## Afstemmingar (flipi Afstemmingar)

| Lykill | Tegund | Merking | Úr BC |
|---|---|---|---|
| `banks[]` | listi | Bankareikningar og greiðslukort (má vera tómt; kort valfrjáls). Síðasta afstemming = nýjasta `stmt_date`. `outst` má vera 0 á öllum | `Bank Account` (Staða á dagsetningu), `Bank Account Statement` (síðasta yfirlit) |
| `banks[].no`, `.name` | texti | Númer og heiti („LB-ISK“, „Landsbankinn, veltureikningur“). Kort: „KORT-1“, „Fyrirtækjakort 1“ | |
| `banks[].teg` | texti | „Veltureikningur“, „Launareikningur“ …, **„Greiðslukort“** (fyrirtækjakort, skuld, kreditstaða) eða **„Kortauppgjör“** (EN „Card settlement“: krafa á færsluhirði vegna kortasölu, debetstaða, gerð upp innan fárra daga). Tegundin skiptir töflunni í bankareikninga, kortauppgjör og greiðslukort; kortauppgjör teljast hvorki með bönkum né kortum í samtölum | |
| `banks[].lag_days` | heiltala, *valfrjálst* | Aðeins kortauppgjör: umsaminn uppgjörstími færsluhirðis í dögum (t.d. 1–3) | samningur / reynsla úr bankabók |
| `banks[].open_days` | heiltala, *valfrjálst* | Aðeins kortauppgjör: aldur elstu óuppgerðu færslu í dögum á stöðudegi. Ef `open_days` > `lag_days` er reikningurinn merktur rauður | `Bank Account Ledger Entry` (Open = true), elsta `Posting Date` |
| `banks[].bal` | tala, kr. | Staða í BC í dag (kort neikvæð) | Balance at Date |
| `banks[].stmt_date`, `.stmt_no`, `.stmt_bal` | texti/texti/tala | Síðasta bankayfirlit: dagsetning, númer, lokastaða | `Bank Account Statement` |
| `banks[].outst` | tala, kr. | Óafstemmt (útistandandi) við síðasta yfirlit, 0 ef stemmir | yfirlit − bankabók á yfirlitsdegi |
| `banks_gl` | `{bankar, kort, kortauppgjor}` kr. | Staða bankalykla, kortalykla og (*valfrjálst*) lykla kortauppgjörs í fjárhag í dag. `kort` 0 ef engin fyrirtækjakort. Vanti `kortauppgjor` er línan „Kortauppgjör á móti fjárhag“ ekki sýnd | Staða (31) á `G/L Account` (t.d. 6920, 6340; lyklar úr `Bank Account Posting Group`) |
| `rec.stmts[]` | listi `{acc, name, stmt, ledger, outst}` | Á yfirlitsdegi: yfirlit, bankabók og mismunur á hvern reikning (`acc` = `banks[].no`; einn á hvern reikning í `banks`) | `Bank Account Ledger Entry` summa til yfirlitsdags |
| `unbooked[]` | listi `{k, t, d, amt, note}` | Greiðslur sem vantar í bankabók (VSK, staðgreiðsla, laun, lán …). `amt` jákvætt | Áætlað út frá skuldalyklum (9710–9740, VSK) og síðustu mánuðum |
| `unb_total` | tala, kr. | Summa `unbooked[].amt` | reiknað |
| `ag_total` | tala, kr. | Aldursgreining viðskiptamanna, samtals | `aging` (viðskiptamenn) |
| `krofur_gl` | tala, kr. | Staða kröfulykla í fjárhag | Staða á `G/L Account` (kröfulyklar, t.d. 6310–6330) |
| `ven_total` | tala, kr. | Opnar færslur lánardrottna, samtals (jákvætt) | `aging` (lánardrottnar) |
| `ap_gl` | tala, kr. | Staða skuldalykla lánardrottna (jákvætt) | Staða á `G/L Account` (t.d. 9410–9440) × −1 |
| `vsk_net` | tala, kr. | Nettó VSK-skuld í dag (jákvætt = skuld) | VSK-lyklar (Staða) − uppgjörsreikningur |
| `vsk_julagu` | tala, kr. | VSK síðasta lokna tímabils (sem er á gjalddaga) | breyting VSK-lykla yfir tímabilið |
| `vsk9570` | tala, kr. | Staða VSK-uppgjörsreiknings (debet jákvætt) | Staða á `G/L Account` (uppgjörsreikningur) |
| `stemming` | `{"ÁÁÁÁ-MM": mismunur}` | Debet − kredit innan mánaðar á hvern mánuð (0 = stemmir; allir mega vera 0) | `period_breakdown` net_change á öllum lyklum, summa á mánuð |
| `kort_m` | tala, kr. | Meðalhækkun kortaskuldar á mánuði (fullbókaðir mánuðir); 0 ef engin fyrirtækjakort | Staða kortalykils, fyrsti − síðasti / fjöldi |

## Opin atriði (flipi Opin atriði)

| Lykill | Tegund | Merking | Úr BC |
|---|---|---|---|
| `inv_n`, `inv_sum` | heiltala, kr. | Fjöldi og summa innkaupareikninga í samþykkt | `Purchase Header` / `Approval Entry` (sama og `kostnadur.inv`) |
| `inv_od_n`, `inv_od_sum` | heiltala, kr. | Þar af komnir yfir gjalddaga | sama |

Afstemmingarlínur og opin atriði eru **listar í gögnunum** (`js.rec_rows`, `js.open_items`, sjá neðar): jafnmargar línur og eiga við félagið, í þeirri röð sem á að birta (opin atriði eru röðuð eftir alvarleika og fjárhæð). Félagssértækar fjárhæðir (t.d. tvíreikningur, innbyrðis krafa, gengismunur, óráðstafaður hagnaður fyrra árs) eru skrifaðar beint í `amt` línunnar.
## Reglur um `meta`, `text` og `js`

- **Hvar gildin lenda.** `meta.*` og `text.*` fara aðeins í HTML (HTML-sloppin). `html.*` fer óbreytt í HTML (aðeins `<b>` og `<a href="x.html">`). `js.*` fer inn í JavaScript sem JSON-bókstafur (`json.dumps`), svo þar má vera hvaða texti sem er, líka gæsalappir, `'`, `` ` `` og `\`; tölur, listar og hlutir eru settir inn sem slíkir (ekki sem texti). Textar í `js` eru birtir sem HTML (innerHTML) þar sem þeir lenda í töflum og spjöldum: aðeins `<b>` og `<a href="x.html">`. Lykill sem er bæði í `meta` og `js` (t.d. `year`, `py`) á að hafa sama gildi í báðum. Valfrjálsir listar mega vera tómir (`[]`): þá er hlutinn falinn eða sýnir „Á ekki við“/„engin“ í stað villu.
- Skrifaðu stutt og staðreyndamiðað, án gildishlaðinna orða. Tölur á íslensku sniði: `1.234,5 m`, `41,8 m.kr.`, dagsetningar `31.08.2026`, tímabil `jan–ágú`.

### `meta` (dæmi úr DT)

| Lykill | Dæmi (DT) |
|---|---|
| `meta.company` | DT Vélsmiðjan ehf. |
| `meta.short`, `meta.logo` | DT |
| `meta.as_of` | 17.10.2026 |
| `meta.year`, `meta.py` | 2026, 2025 (haus; ár í gátlista er tekið úr völdum mánuði) |

### `text`

| Lykill | Dæmi (DT) |
|---|---|
| `text.source` | Heimild: Business Central (Bifröst), DT Vélsmiðjan ehf., … sótt 16.–18.10.2026. Staða 17.10.2026. |

### `js`

| Lykill | Dæmi (DT) | Regla |
|---|---|---|
| `js.unrec` | sep–okt | mánuðir sem vantar bankaafstemmingu; `""` ef allt er afstemmt (þá falla „… vantar“-merki út) |
| `js.rec_bnk_pill` | Stemmir 31.08. | merki á reikningi sem stemmdi við síðasta yfirlit |
| `js.bank_note` | Allir sex reikningar voru afstemmdir við bankayfirlit 31.08.2026 ({days:n} dagar). … um {unb} m.kr. … | athugasemd undir bankatöflu; má nota gildi (sjá neðar) |
| `js.rec_rows` | sjá `example.json` (11 línur) | afstemmingarlínur: `{s, t, d, amt, ref, est, if}` |
| `js.open_items` | sjá `example.json` (16 atriði) | opin atriði: `{s, t, d, nx, role, amt, ref, est, txt, if}` |

**Línur (`rec_rows`, `open_items`).** `s`: `l` (grænt), `m` (gult), `h` (rautt) eða `auto` (grænt ef |fjárhæð| < 1 kr., annars rautt; aðeins `rec_rows`). `t` titill, `d` lýsing, `nx` næsta skref, `role` ábyrgð („Bókari“, „Fjármálastjóri“). `amt`: fjárhæð í kr. eða `null` (birtist „óstaðfest“/„–“); **eða** `ref`: heiti reiknaðs gildis hér að neðan (þá `amt: null`). `est: true` setur „≈“ framan við. `txt`: texti í stað fjárhæðar (t.d. „87 f.“). `if`: heiti gildis; línan birtist aðeins ef það er ekki 0/tómt (t.d. `"if": "stm_n"` fyrir ójöfnuð innan mánaðar, `"if": "lb_outst"` fyrir útistandandi bankafærslu, `"if": "unb_n"`). Engin lína er föst í sniðmátinu; tómur listi sýnir „Engar afstemmingarlínur.“

**Reiknuð gildi** sem textar mega vísa í með `{heiti}` (m.kr., 1 aukastafur), `{heiti:2}` (2 aukastafir), `{heiti:kr}` (krónur) eða `{heiti:n}` (heiltala), og `ref`/`if` mega nota:
`bank_isk`, `bank_gl`, `bank_diff` (bankar í bankabók, bankalykill, mismunur); `card_sum`, `card_gl`, `card_diff`; `lb_name`, `lb_stmt`, `lb_ledger`, `lb_outst`, `lb_outst_abs` (fyrsti reikningur með útistandandi færslu, annars tómt/0); `unb`, `unb_neg`, `unb_n`, `unb_list` (óbókaðar greiðslur); `kort_m`, `kort_2`, `kort_neg2`; `ag_total`, `krofur_gl`, `ARd` (fjárhagur − aldursgreining); `ven_total`, `ap_gl`, `APd` (undirbók − fjárhagur); `vsk_net`, `vsk9570`, `vsk_julagu`; `stm_n`, `stm_list`, `stm_first`, `stm_first_abs` (ójöfnuður innan mánaðar); `inv_n`, `inv_sum`, `inv_od_n`, `inv_od_sum`; `cs_n`, `cs_sum`, `cs_gl`, `cs_diff`, `cs_outst`, `cs_late_n`, `cs_lag` (kortauppgjör færsluhirða: fjöldi, staða í BC, fjárhagslykill, mismunur, óafstemmt við síðasta uppgjör, reikningar óuppgerðir lengur en `lag_days`, lengsti uppgjörstími); `stock_gl`, `stock_sub`, `stock_diff`, `has_stock` (birgðalykill, birgðabók, mismunur, 1 ef birgðir); `jobs_n` (opin verk); `inc_est` (vantandi rekstrarkostnaður ófullbókaðra liðinna mánaða úr `months[].items`); `days` (dagar frá síðustu afstemmingu).

**Línur sem sniðmátið bætir við** (aðeins þegar gögnin sýna viðkomandi rekstur og engin lína í gögnunum vísar þegar í gildið með `ref`): í Afstemmingum „Kortauppgjör stemmir við uppgjör færsluhirðis“ (`cs_outst`), „Kortauppgjör á móti fjárhag“ (`cs_diff`, ef `banks_gl.kortauppgjor`) og „Birgðir á móti fjárhag“ (`stock_diff`), settar á eftir banka- og kortalínum; í Opnum atriðum „Kortauppgjör stemmir ekki við uppgjör færsluhirðis“ og „Birgðir stemma ekki við fjárhag“ ef mismunur er ≥ 1 kr. Línur sem eiga aðeins við verk (áfangar, verk í vinnslu, verksamningar) eiga að hafa `"if": "jobs_n"`.

**Reiknað úr gögnum:** fyrirsögn og texti yfirstandandi mánaðar („Október er ekki liðinn. Lokun hans hefst í byrjun nóvember.“), ár í fyrirsögnum gátlista (úr völdum mánuði), litir á lykilmælum Afstemminga (rautt/gult/grænt eftir stöðu).

## Tungumál (`lang`, `i18n`)

| Lykill | Dæmi | Skýring |
|---|---|---|
| `lang` | `"is"` | tungumál grunngagna (úr `dataset.json`). Ræður hvaða mál opnast fyrst. Vanti það er það greint úr heitum í gögnunum. |
| `i18n.en` (eða `i18n.is`) | `{"meta": {...}, "text": {...}, "html": {...}, "js": {...}, "names": {...}}` | yfirlag fyrir hitt málið. Sömu lyklar og að ofan, aðeins þeir sem breytast. Dagsetningar á ensku `17 Oct 2026`, tölur `1,234.5`. |
| `i18n.<lang>.names` | `{"Áætlun 2026": "Budget 2026"}` | þýðir heila strengi hvar sem er í gögnunum (heiti lykla utan staðaltöflu, áætlana, flokka, stöðu). |

Sjá `example.json` (yfirlagið `i18n.en`) og `bifrost-maelabord/SKILL.md`, kaflann *Tungumál*.
