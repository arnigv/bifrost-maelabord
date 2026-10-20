# Miðstöð (index.html): hub.json

Skilaðu `hub.json` og keyrðu `render_hub.py`. Skrifaðu aldrei HTML miðstöðvarinnar sjálf(ur). Sýnidæmi: `example.json` (DT Vélsmiðjan).

| Lykill | Tegund | Skýring |
|---|---|---|
| `meta.company` | texti | Heiti félags í nefnifalli („DT Vélsmiðjan ehf.“) eða samstæðu („Vélsmiðjusamstæðan“) |
| `meta.company_acc` | texti | Í þolfalli, fer í skipanir: „fyrir **DT Vélsmiðjuna ehf.**“ |
| `meta.initials` | texti | 2–3 stafir í merki og titli („DT“) |
| `meta.as_of` | texti | Staða gagna, DD.MM.ÁÁÁÁ |
| `meta.source_dates` | texti | Hvenær gögn voru sótt, í fæti („16.–17.10.2026“) |
| `hero.title` / `hero.sub` | texti | Heildarmynd í tveimur hlutum: „Góð afkoma,“ + „en sjóðurinn er í hættu“ |
| `hero.text` | texti | Ein til tvær setningar með aðalniðurstöðu í krónum, úr mælaborðunum |
| `hero.figures` | 4 × [gildi, skýring] | T.d. ["441,5 m", "EBITDA 2026, spá"]; gildi úr mælaborðunum, engin tala tvisvar |
| `top[]` | 3–5 atriði | `sev` h/m/l, `title`, `text` (ein setning með fjárhæð), `src` (mælaborð sem það kemur úr). Raðað eftir áhrifum |
| `cards[]` | 9 + valin sérmælaborð | Röð: Stjórn, Sjóðstreymi og bankar, Tekjur, Kostnaður, Mánaðarlok, Framlegð og verk, Spágerð, Endurskoðun, [sérmælaborð], **Sjálfvirknivæðing síðust**. Reitir: `title`, `tabs` (flipar með „ · “), `label`, `value`, `note`, `href` (`stjorn.html` …, `ser-<id>.html`; Sjálfvirknivæðing = slóð artifacts), `color` (`--s1`…`--s7`, sjá sýnidæmi), `status` up/warn/dn/info, valfrjálst `pill` (eigin texti á merki) |
| `recommended[]` | 0–3 | `{id, reasons[]}` úr `sermaelabord/scripts/flokka.py` (`id` úr pakkar.json, `reasons` = `astaedur`) |

Tölur: íslenskt snið („1.295,6 m“, „−18,1 m“). Sömu lykiltölur og í mælaborðunum sjálfum.
