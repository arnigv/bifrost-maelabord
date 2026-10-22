---
name: sjalfvirkni
description: "Mælaborðið „Sjálfvirknivæðing“ í Bifröst-mælaborðum: erindrekar og handverk bókara með áætlun, dagatali og sögu; keyrsla læst þar til virkjað með ráðgjafa. Notaðu AÐEINS innan Bifröst-mælaborða: þegar notandinn biður um Bifröst-mælaborð eða þetta mælaborð með nafni, eða breytir mælaborði sem pluginið bjó til. Ekki fyrir almennar spurningar um rekstur eða Business Central, aðrar skýrslur, skjöl eða artifacts."
---

# Sjálfvirknivæðing

Svarar: **Hvaða endurtekin verk í bókhaldinu má fela erindrekum, hvenær eiga þeir að keyra, og hvað fundu þeir síðast?**

Fylgdu `bifrost-maelabord` (útlit). Endurgerðu eða endurbirtu þessa síðu **aðeins** þegar beðið er um breytingu á henni; hún geymir stillingar notandans (lestu alltaf nýjustu útgáfu og haltu STATE). Aðeins lesið úr BC. Notaðu orðið **erindreki** (ft. erindrekar), aldrei „agent“.

## 1. Öryggisreglur (óbreytanlegar)

- Efst á síðunni: „**Áður en keyrsla er framkvæmd þarf að virkja aðgerðina og tala við ráðgjafa.**“ Ráðgjafi Origo fer yfir aðgang að BC, hvaða erindrekar henta, hver samþykkir niðurstöður og vinnslusamning um gögnin.
- **Allir keyrsluhnappar eru óvirkir** (🔒) þar til aðgerðin hefur verið virkjuð. Áætlanir má samt skipuleggja og vista.
- Hamir: *Tilkynning · Tillaga til samþykktar · Drög í BC*. Drög eru **aldrei bókuð**; bókari fer yfir og bókar. Enginn hamur bókar sjálfkrafa.
- Viðtakendur eru hlutverk (Fjármálastjóri, Bókari …), aldrei nöfn.

## 2. Gögn

- Keyrðu fyrst hin mælaborðin (eða notaðu niðurstöður þeirra) og skráðu **niðurstöðu síðustu greiningar** á hvern erindreka í `find` (alvarleiki `h`/`m`/`l` og ein setning með krónutölu), t.d. afstemmingar úr `sjodstreymi`, færsluvakt úr `endurskodun`, innheimta og sjóðstaða úr `sjodstreymi`, samþykkt reikninga úr `kostnadur`, reikningsfærsla úr `tekjuleki`.
- Erindreki sem hefur ekki gögn fær „Ekki keyrt“.
- Sjálfgefnar áætlanir eru í `scripts/build.py` (`DEFAULT`); aðlagaðu að félaginu (t.d. engin verk → engin reikningsfærsla verka).

## 3. Smíði og birting (síðan vistar sig sjálf)

Síðan er skráin: stillingar, biðröð og saga eru geymd í síðunni og vistuð með `artifact`-getunni.

1. Búðu til `config.json` (sjá haus `scripts/build.py`): félag, upphafsstafir, slóð miðstöðvar, dagsetning gagna, félög í vali, `find`, og `lang` (`is`/`en`, sama og miðstöðin). Á ensku er síðan þýdd með `assets/i18n/en.json`.
2. `python3 ${CLAUDE_SKILL_DIR}/scripts/build.py --config config.json --out sjalfvirkni.html`
3. Birtu með `capabilities: {"artifact": {}}`.
4. Lestu birtu síðuna aftur (`Artifact read`, `path: index.html`) og vistaðu allt fram að og með `<body>` auk `\n<meta charset="utf-8">\n` í `prefix.txt`.
5. Smíðaðu aftur með `--prefix prefix.txt` og birtu á sömu slóð. Nú vistast breytingar notenda.
6. Áður en þú birtir aftur síðar: lestu nýjustu útgáfu, því notendur kunna að hafa vistað stillingar. Byggðu á stöðu þeirra (`STATE` í síðunni), ekki á eldri skrá.

## 4. Flipar

**Yfirlit** — hero í fullri breidd (fjöldi á áætlun, næsta keyrsla), næstu keyrslur 7 daga, lykilmælar (opnar ábendingar, keyrslur næstu 7 daga, virkjað með ráðgjafa, síðast vistað), nýjustu ábendingar, sjálfvirkni eftir ferli.
**Erindrekar** — spjald á hvern: lýsing, síðasta niðurstaða, áætlun og næsta keyrsla, rofi „á áætlun“, 🔒 Keyra núna, Stilla tíma.
**Handverk** — tafla eftir ferli með síu: verk, hvað erindrekinn gerir, áætlun og hamur.
**Dagatal og saga** — næstu 14 dagar (vika byrjar á mánudegi), það sem keyrir við atburð í BC, biðröð, „Hvernig keyrsla virkar“ og keyrslusaga.

Stillingagluggi: tíðni (daglega virka daga, vikulega, dagur mánaðar, X. virki dagur, á tveggja mánaða fresti, ársfjórðungslega, árlega, við atburð, handvirkt), vikudagur/dagur/mánuður, klukka (24 klst.), hamur, félag (eða samstæða), viðtakandi. Sýnir næstu keyrslu.

## 5. Keyrsla eftir virkjun (síðar)

Þegar ráðgjafi hefur virkjað: áætlað verkefni les síðuna, keyrir erindreka sem eru komnir á tíma eða í biðröð með Bifröst (aðeins lestur), skráir niðurstöðu í söguna og tæmir biðröðina. Fyrr en þá er ekkert keyrt.

## Samstæða

Félagsval í stillingaglugga: hvert félag eða samstæða. Erindreki sem keyrir á samstæðu athugar líka innbyrðis stöðu milli félaga.
