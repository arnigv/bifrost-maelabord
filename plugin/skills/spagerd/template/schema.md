# Spágerð og rekstrarhermir: gagnaskema (`spagerd`)

Gervigreindin skrifar **aðeins** JSON eftir þessu skema og keyrir:

```
python3 ${PLUGIN}/skills/bifrost-maelabord/scripts/render.py --dashboard spagerd --data spagerd.json --out build/spagerd.html [--subpage]
```

`example.json` er sýnidæmið (DT Vélsmiðjan, gullútgáfa). Afritaðu það og skiptu út gildunum; lyklar mega ekki vanta.

**Einingar:** allar fjárhæðir í **krónum** (ekki m.kr.), sem tölur. Tekjur og kostnaður eru **jákvæðar** tölur (kostnaður dreginn frá í EBITDA). Hlutföll sem tugabrot (0,059 = 5,9%). Mánuðir sem `"ÁÁÁÁ-MM"`.

## 1. Hvaðan gögnin koma

Spáin kemur úr `skills/spagerd/scripts/forecast.py` (sama líkan og hermirinn í síðunni keyrir í JS):

```
python3 forecast.py --data dataset.json --assumptions assumptions.json --out forecast.json
```

| DATA-lykill | Úr forecast.py / dataset.json |
|---|---|
| `company`, `as_of` | `forecast.company`, `forecast.as_of` (= `dataset.company`, `dataset.as_of`) |
| `months` | `dataset.months` (aðeins lyklarnir hér að neðan; `incomplete_reason` → `reason`) |
| `oneoffs` | `dataset.oneoffs` |
| `profile` (valfrjálst) | `dataset.profile` (`profile.json` úr `bifrost-gogn`, kafli 2) |
| `fit` | `forecast.fit()` innan skriftunnar; `mode` = `forecast.model.adferd`. Úttakið `forecast.model` hefur hluta: `grunnstig`→`base`, `leitni_man`→`g`, `sigma`, `efnishlutfall`→`mat`, `arstidir`→`season`. `fixed`, `last` og `n` fást aðeins með því að kalla `fit()` beint (sjá dæmi í lok skjalsins). |
| `A` | `forecast.assumptions` (óbreytt, með `_`-lyklum) |
| `fc` | `forecast.forecast` |
| `year` | `forecast.year` |
| `backtest` | `forecast.backtest` + `rows` (spá og raun á bakprófunarmánuði, sjá neðar) |
| `py` | Heildartölur fyrra árs eftir flokkum (sjá neðar) |

## 2. DATA-lyklar

Allir lyklar eru **skyldir** nema annað sé tekið fram.

### `company` (texti), `as_of` (texti `ÁÁÁÁ-MM-DD`)
Heiti félags og dagsetning gagna. Úr `dataset.json` (`Context_Companies_List`, dagsetning keyrslu).

### `months` (listi, einn hlutur á mánuð yfirstandandi árs, jan → síðasti bókaði mánuður)
| Lykill | Tegund | Merking |
|---|---|---|
| `ym` | texti | Mánuður `"2026-01"` |
| `tekjur`, `vorunotkun`, `laun`, `husnaedi`, `annar_rekstur`, `afskriftir`, `fjarmagn` | tala, kr., jákvæð | Hreyfing flokks í mánuðinum |
| `ebitda` | tala, kr. | tekjur − vörunotkun − laun − húsnæði − annar rekstur |
| `hagnadur_fs` | tala, kr. | ebitda − afskriftir − fjármagnsliðir (± óreglulegt) |
| `complete` | true/false | Fullbókaður mánuður (aðeins þeir fara í líkanið) |
| `reason` | texti | Af hverju ófullbókaður, t.d. „laun vantar, vörunotkun vantar“; `""` ef fullbókaður |

BC: `period_breakdown` á `G/L Account`, `balance_fields:[32]` (Hreyfing), `field_type:"net_change"`, 12 bil; flokkun og ófullbókun í `build_dataset.py` (`bifrost-gogn`, kaflar 4–5).

### `oneoffs` (listi, má vera tómur)
`{no, name, cat, ym, amount}`: lykill, heiti lykils, flokkur (`"tekjur"` o.s.frv.), mánuður, fjárhæð í kr. (jákvæð). Úr `dataset.oneoffs` (`build_dataset.py`: hreyfing í einum fullbókuðum mánuði ≥ 10% af tekjum hans). Einskiptistekjur eru teknar út úr spágrunni.

### `fit` (hlutur), líkanið metið á fullbókuðum mánuðum (einskiptistekjur frádregnar)
| Lykill | Tegund | Merking |
|---|---|---|
| `base` | kr./mán. | Grunnstig tekna (meðaltal síðustu 3 mánaða, árstíðaleiðrétt) |
| `g` | tugabrot/mán. | Leitni tekna á mánuði, takmörkuð við ±0,015 |
| `sigma` | tugabrot | Hlutfallslegt staðalfrávik leifa (≥ 0,03) |
| `mat` | tugabrot | Efnishlutfall (vörunotkun / tekjur, síðustu 6 mán.) |
| `fixed` | hlutur | `laun`, `husnaedi`, `annar_rekstur`, `afskriftir`, `fjarmagn`: meðaltal síðustu 3 mánaða, kr./mán. |
| `last` | `"ÁÁÁÁ-MM"` | Síðasti fullbókaði mánuður |
| `season` | true/false | Árstíðir notaðar (þarf ≥ 13 fullbókaða mánuði) |
| `n` | heiltala | Fjöldi fullbókaðra mánaða í líkaninu |
| `mode` | texti, valfrjálst | Spáaðferð = `forecast.model.adferd`: `"full"` (n ≥ 6, fullt líkan), `"runrate"` (3 ≤ n < 6: einföld spá, `g` = 0, víðara bil), `"none"` (n < 3: spá ekki gerð). Vanti lykilinn er hann leiddur af `n` (vanti líka `n`: `"full"`). |

**Stutt saga.** `runrate`: síðan merkir spána „Einföld spá“ í niðurstöðusetningu, forsendum, líkantöflu og óvissuþáttum, og `backtest` er `null` (bakprófun þarf ≥ 8 mánuði). `none`: `forecast.py` skrifar `forecast.json` með `stada: "engin_spa"`, `forecast: []` og `backtest: null`; settu `fc: []`, `backtest: null`, `fit` með `n`, `last`, `season: false`, `mode: "none"` og `null` í `base`, `g`, `sigma`, `mat`, `fixed`. Síðan sýnir þá „Spá ekki gerð: of fáir fullbókaðir mánuðir“ með raun ársins, felur flipann Rekstrarhermir og sýnir aðeins forsendutöfluna á Forsendum.

### `profile` (hlutur, valfrjálst)
`dataset.profile` óbreytt (`{"jobs": 15, "items": 16, "resources": 6, …}`, fjöldi færslna úr `bifrost-gogn` kafla 2). Síðan les aðeins `jobs`:
| Skilyrði | Orðalag |
|---|---|
| `jobs > 0` eða `profile` vantar | verk: „efnishlutfall“, „Verkefnastaða og sala“, „Þekktar pantanir og verk“ (BC: sölupantanir, verkáætlanir), „Efni og innkaup“ |
| `jobs` = 0 | vörur/þjónusta: „hlutfall vörunotkunar“, „Sala og eftirspurn“, „Þekktar pantanir“ (BC: sölupantanir), „Innkaupsverð“ |

### Reglur sem síðan reiknar úr `months` (ekki skrifaðar af gervigreindinni)
Reiknað úr fullbókuðum mánuðum með tekjur > 0:
| Regla | Viðmið | Áhrif |
|---|---|---|
| Sveiflukennd framlegð | EBITDA-hlutfall mánaða spannar **> 10 prósentustig** (hæsta − lægsta; `VOL_MARGIN`) | Óvissuþátturinn „Sveiflukennd framlegð“ sýndur og niðurstöðusetningin segir að framlegðin sé stærsti óvissuþátturinn; annars segir hún að framlegð hafi verið stöðug og tekjustigið sé stærsti óvissuþátturinn (áhrif 1% tekna á EBITDA). |
| Vörunotkun nefnd | vörunotkun **≥ 5% af tekjum** að meðaltali (`MAT_MIN`) | Annars eru aðeins laun nefnd (þjónusta, eignarhald). |
| Stærsti kostnaðardrifinn | spönn efnishlutfalls ≥ spönn launahlutfalls | „Hvert prósentustig í efnishlutfalli…“, annars „…í launahlutfalli…“. |
| Engar árstíðir | `fit.season` = false | Óvissuþátturinn „Engar árstíðir“ (texti `js.why4_text`). |
| Tekjuspáin traustari | `backtest.mape_tekjur` ≤ 25% og < `mape_ebitda` | Græni óvissuþátturinn sýndur. |
| Einskiptistekjur | `oneoffs` með `cat` = `"tekjur"` | Aðeins þær eru teknar úr grunni og sýndar sem einskipti; leiðrétt MAPE aðeins ef einskiptismánuður er í bakprófun („enn yfir 25%“ / „innan 25%“ reiknað). |

### `A` (hlutur), forsendur = `assumptions.json`
Byrjaðu á `skills/spagerd/assets/assumptions.default.json` og uppfærðu (Hagstofa, Seðlabanki, kjarasamningar). Síðan les:
`verdbolga` (tugabrot, 12 mán. VNV), `styrivextir`, `styrivextir_grunnur` (tugabrot), `kjarasamningar` (listi `{fra:"ÁÁÁÁ-MM-DD", haekkun}`; **a.m.k. ein færsla**, hermirinn notar þá fyrstu), `yfirfaersla_efnis` (0–1), `demping_leitni` (0–1), `eldsneyti_hlutur` (hlutfall annars rekstrar), `eldsneyti_breyting` (tugabrot). Aðrir lyklar (`verdskra`, `adfangaverd`, `thekktar_pantanir`, `stodugildi_breyting`, `magnbreyting_arleg`, `_…heimild`) fylgja óbreyttir.

### `fc` (listi, 12 hlutir, næstu 12 mánuðir eftir `fit.last`)
`forecast.forecast` óbreytt (tómur listi `[]` ef `fit.mode` = `"none"`): `ym`, sömu fjárhæðarlyklar og `months` (kr.), auk `tekjur_p10`, `tekjur_p90`, `ebitda_p10`, `ebitda_p90` (kr.). Ófullbókaðir mánuðir ársins eru spáðir (ekki raun).

### `year` (hlutur), yfirstandandi ár = raun (fullbókað) + spá
`forecast.year`: `raun_tekjur`, `raun_ebitda` (fullbókaðir mánuðir, kr.), `spa_tekjur`, `spa_ebitda` (spá út árið), `p10_ebitda`, `p90_ebitda` (summa P10/P90 spámánaða ársins), `ar_tekjur`, `ar_ebitda` (raun + spá).

### `backtest` (hlutur)
Má vera `null` (færri en 8 fullbókaðir mánuðir): þá segir síðan „Bakprófun ekki gerð“. Annars `forecast.backtest` (`manudir`, `mape_tekjur`, `mape_ebitda`, tugabrot) **auk** `rows`: listi `{ym, raun_tekjur, spa_tekjur, raun_ebitda, spa_ebitda}` (kr.) fyrir 3 síðustu fullbókuðu mánuðina. `rows` fæst með `fit(rows[:-3])` og `project(..., verdskra=[], adfangaverd=[], kjarasamningar=[], thekktar_pantanir=[])` eins og í `forecast.py`.

### `py` (hlutur), fyrra ár í heild
`tekjur`, `vorunotkun`, `laun`, `husnaedi`, `annar_rekstur`, `afskriftir`, `fjarmagn`, `ebitda`, `hagnadur_fs`, kr., jákvæð. Úr `dataset.py_full` ef til; annars Hreyfing (reitur 32) á `G/L Account` með `Date Filter` = allt fyrra ár (eitt `data_batch_records`-kall, `bifrost-gogn` kafli 0) flokkuð eins og `months`. Mánaðarskipting fyrra árs er ekki notuð (sýnd sem meðaltal á mánuði).

## 3. `meta`, `text`, `js` (textar síðunnar)

**Hvar gildin lenda.** `meta.*` og `text.*` fara aðeins í HTML (HTML-sloppin). `html.*` fer óbreytt í HTML (aðeins `<b>` og `<a href="x.html">`). `js.*` fer inn í JavaScript sem JSON-bókstafur (`json.dumps`), svo þar má vera hvaða texti sem er, líka gæsalappir, `'`, `` ` `` og `\`; tölur, listar og hlutir eru settir inn sem slíkir (ekki sem texti). Textar í `js` eru birtir sem HTML (innerHTML) þar sem þeir lenda í töflum og spjöldum: aðeins `<b>` og `<a href="x.html">`. Lykill sem er bæði í `meta` og `js` (t.d. `year`, `py`) á að hafa sama gildi í báðum. Valfrjálsir listar mega vera tómir (`[]`): þá er hlutinn falinn eða sýnir „Á ekki við“/„engin“ í stað villu.

### `meta` (HTML)

| Lykill | Dæmi (DT) | Regla |
|---|---|---|
| `meta.company` | DT Vélsmiðjan ehf. | Fullt heiti (nefnifall) |
| `meta.short` | DT | Stutt heiti í `<title>` |
| `meta.logo` | DT | 1–3 stafir í merki |
| `meta.year`, `meta.py` | 2026, 2025 | Yfirstandandi ár og fyrra ár (tala) |
| `meta.as_of` | 16.10.2026 | Dagsetning gagna |
| `meta.fetched` | 16.–17.10.2026 | Hvenær forsendur voru sóttar |

### `text` (HTML, sloppið)

| Lykill | Dæmi (DT) | Regla |
|---|---|---|
| `text.warn` | Raun nær til 31.8.2026. September og október eru ófullbókaðir (laun og vörunotkun vantar) og eru því spáðir. Einskiptissala 31,0 m.kr. í ágúst er tekin út úr grunni spárinnar. EBITDA-spáin er óviss (bakprófun 48% frávik) — *án lokapunkts; síðan bætir við „, sjá Forsendur.“* |  |
| `text.spa_note` | Mánaðarskipting 2025 er ekki í gögnunum, aðeins heildartölur ársins. … |  |
| `text.footer_src` | fjárhagur 1.1.–16.10.2026; raun til 31.8.2026. 2025: heildartölur … Spálíkan: spagerd/forecast.py. |  |
| `text.bt_months` | jún–ágú (bakprófunarmánuðir) |  |
| `text.why_h`, `text.why_sub` | Af hverju er EBITDA-spáin óviss?, MAPE yfir 25% |  |

### `js` (JavaScript-bókstafir)

| Lykill | Dæmi (DT) | Regla |
|---|---|---|
| `js.decide_ym`, `js.decide_date` | "2026-11", 1.11.2026 | Fyrsti heili mánuður eftir keyrslu: ákvarðanir í hermi taka gildi |
| `js.oneoff_ym` | "2026-08" | Mánuður einskiptistekna (`""` ef engar) |
| `js.bt_rev_sign`, `js.bt_eb_sign` | 1, −1 | Tala: 1 ef MAPE ≤ 25% (grænt), −1 ef yfir (rautt) |
| `js.act_short`, `js.fc_short` | jan–ágú, sep–des (raun- og spámánuðir ársins) |  |
| `js.act_long`, `js.fc_long` | janúar–ágúst, september–desember |  |
| `js.base3`, `js.hist_period` | jún–ágú 2026 (grunnlaun), jan–ágú 2026 (saga leitni) |  |
| `js.oneoff_month`, `js.oneoff_month_cap`, `js.oneoff_acc`, `js.oneoff_period`, `js.oneoff_note` | ágúst, Ágúst, 1130, 08.2026, Sala undanþegin VSK, tekin úr tekjugrunni spár. |  |
| `js.inc_tip` | Ófullbókaður mánuður: laun og vörunotkun vantar. |  |
| `js.as_cpi_date`, `js.as_cpi_st` | sept. 2026, staðfest |  |
| `js.as_rate_date`, `js.as_rate_st`, `js.as_rate_note` | 7.10.2026, staðfest, Næsta ákvörðun 18.11.2026. Fjármagnsliðir fylgja hlutfallslega. |  |
| `js.as_kj_date`, `js.as_kj_st`, `js.as_kj_note` | 1.1.2027, óstaðfest, Samningar á almennum markaði 2024–2028: 3,5% … Staðfesta. |  |
| `js.as_fx_val`, `js.as_fx_src`, `js.as_fx_st`, `js.as_fx_note` | ekki notað, Bifröst, gengistafla, vantar, Ekki sótt; … |  |
| `js.as_ord_val`, `js.as_ord_st`, `js.as_ord_note` | engar í spá, vantar, Opnar pantanir … ekki sótt. |  |
| `js.bt_rev_chip`, `js.bt_eb_chip` | innan 25%, yfir 25%: óviss |  |
| `js.why1_tail` (aðeins sýnt ef framlegð er sveiflukennd, sjá *Reglur*; má vera `""`) | Líkanið notar meðaltöl, en framlegð batnaði mikið jún–ágú og bakprófunin vanmat því EBITDA. |  |
| `js.why2_mid` | laun og vörunotkun ekki bókuð. Síðasti fullbókaði mánuður er ágúst |  |
| `js.why4_text` | Mánaðarskipting 2025 er ekki í gögnunum (aðeins ársheild), svo jól og sumarleyfi koma ekki fram í spánni. |  |
| `js.rate_base` | 8,0% (= `A.styrivextir_grunnur`) |  |
| `js.kj_desc`, `js.cpi_desc`, `js.rate_desc`, `js.fuel_desc`, `js.pass_def` | SA/ASÍ: 3,5% (óstaðfest).; Hagstofa: 5,9% (sept. 2026).; Seðlabanki: 8,0% (7.10.2026).; 5% af öðrum rekstri.; 50% |  |
| `js.need_fail` | Verðhækkun á tveimur mánuðum dugar ekki. (fjöldi mánaða frá `decide_date` til áramóta) |  |
| `js.year` | 2026 | tala, sama og `meta.year` |
| `js.py` | 2025 | tala, sama og `meta.py` |
| `js.as_of` | 16.10.2026 | sama og `meta.as_of` |

Reglur: stutt og staðreyndabundið, íslenskt talnasnið (`1.234,5 m`, `5,9%`), dagsetningar `D.M.ÁÁÁÁ`. Stöðugildi (`as_*_st`) eru eitt af: `staðfest`, `óstaðfest`, `notandi`, `forsenda`, `saga`, `vantar`. **Reiknað úr gögnum:** næsta ár (`year` + 1), síðasti ófullbókaði mánuður (úr `months`). `A.kjarasamningar` má vera tómur (engin launahækkun í spá; forsendulínan sýnir „engir í spá“); `oneoffs`, `backtest.rows` mega vera tóm.


## 4. Dæmi: smíða DATA úr forecast.py

```python
import json, sys; sys.path.insert(0, f'{PLUGIN}/skills/spagerd/scripts'); import forecast as FC
D = json.load(open('dataset.json')); A = json.load(open('assumptions.json')); R = json.load(open('forecast.json'))
one = {}
for o in D['oneoffs']:
    if o['cat'] == 'tekjur': one[o['ym']] = one.get(o['ym'], 0) + o['amount']
rows = [dict(r) for r in D['months'] if r['complete']]
for r in rows: r['tekjur'] -= one.get(r['ym'], 0)
M = R['model']; mode = M.get('adferd', 'full')
if mode == 'none':   # < 3 fullbókaðir mánuðir: spá ekki gerð
    fit = dict(base=None, g=None, sigma=None, mat=None, fixed=None, last=M.get('sidasti'), season=False, n=len(rows), mode='none')
else:
    F = FC.fit(rows, A)   # g og sigma úr forecast.json (run-rate breytir þeim)
    fit = dict(base=F['base'], g=M['leitni_man'], sigma=M['sigma'], mat=F['mat'], fixed=F['fixed'], last=F['last'], season=F['season'], n=len(rows), mode=mode)
bt = None
if R['backtest']:     # aðeins ef ≥ 8 fullbókaðir mánuðir
    Fb = FC.fit(rows[:-3], A)
    pb = FC.project(Fb, dict(A, verdskra=[], adfangaverd=[], kjarasamningar=[], thekktar_pantanir=[]), [r['ym'] for r in rows[-3:]])
    bt = dict(R['backtest'], rows=[dict(ym=r['ym'], raun_tekjur=r['tekjur'], spa_tekjur=p['tekjur'], raun_ebitda=r['ebitda'], spa_ebitda=p['ebitda']) for p, r in zip(pb, rows[-3:])])
K = ['tekjur','vorunotkun','laun','husnaedi','annar_rekstur','afskriftir','fjarmagn','ebitda','hagnadur_fs']
DATA = dict(company=D['company'], as_of=D['as_of'], profile=D.get('profile'),
  months=[dict({k: m[k] for k in K}, ym=m['ym'], complete=m['complete'], reason=m.get('incomplete_reason', '')) for m in D['months']],
  oneoffs=D['oneoffs'], fit=fit, A=A, fc=R['forecast'], year=R['year'], backtest=bt,
  py=PY_FULL)  # sjá „py“
DATA.update(meta={...}, text={...}, html={})
```

Athugið: `forecast.py` dregur einskiptistekjur líka frá `ebitda` í bakprófun, en gullútgáfan (DT) dró þær aðeins frá tekjum. Hermirinn í síðunni notar ekki árstíðastuðla; ef `fit.season` er `true` víkur grunnur hermis lítillega frá `fc`.

## Tungumál (`lang`, `i18n`)

| Lykill | Dæmi | Skýring |
|---|---|---|
| `lang` | `"is"` | tungumál grunngagna (úr `dataset.json`). Ræður hvaða mál opnast fyrst. Vanti það er það greint úr heitum í gögnunum. |
| `i18n.en` (eða `i18n.is`) | `{"meta": {...}, "text": {...}, "html": {...}, "js": {...}, "names": {...}}` | yfirlag fyrir hitt málið. Sömu lyklar og að ofan, aðeins þeir sem breytast. Dagsetningar á ensku `17 Oct 2026`, tölur `1,234.5`. |
| `i18n.<lang>.names` | `{"Áætlun 2026": "Budget 2026"}` | þýðir heila strengi hvar sem er í gögnunum (heiti lykla utan staðaltöflu, áætlana, flokka, stöðu). |

Sjá `example.json` (yfirlagið `i18n.en`) og `bifrost-maelabord/SKILL.md`, kaflann *Tungumál*.
