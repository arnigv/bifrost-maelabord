# Bifröst mælaborð 1.0.0

Plugin frá Origo sem býr til gagnvirk mælaborð úr Business Central í gegnum Bifröst: miðstöð og níu sjálfgefin mælaborð í einu artifacti (Stjórn, Sjóðstreymi og bankar, Kostnaður, Mánaðarlok og afstemmingar, Tekjur, Framlegð og verk, Spágerð, Endurskoðun og ársreikningur, Sjálfvirknivæðing), auk sérmælaborða eftir atvinnugrein (ÍSAT). Mælaborðin eru smíðuð úr föstum sniðmátum, svo útlit og uppbygging eru alltaf eins, og aðeins er lesið úr Business Central.

**Byrjaðu á:** `/maelabord` eða „Settu upp Bifröst-mælaborðin“. Skillin eru aðeins notuð fyrir mælaborðin, ekki önnur verkefni notandans.

**Leiðbeiningar:** https://arnigv.github.io/bifrost-maelabord/ (öll skills: [skills.html](https://arnigv.github.io/bifrost-maelabord/skills.html))

## Innihald

- `plugin/`: frumkóði pluginsins (`.claude-plugin/`, `commands/` með `/maelabord`, `skills/` með föstum sniðmátum í `template/`-möppum, `docs/`, `README.md`, `mcp.example.json`)
- `bifrost-maelabord-1.0.0.zip`: pluginið tilbúið til uppsetningar (líka sem viðhengi við útgáfuna v1.0.0)
- `index.html`, `skills.html`: leiðbeiningasíðurnar sem GitHub Pages birtir

## Uppsetning

1. Sæktu `bifrost-maelabord-1.0.0.zip`.
2. Stjórnandi í Claude (Team eða Enterprise) fer í *Organization settings › Plugins & skills* og velur *Add › Upload a plugin*.
3. Hleður upp zip-skránni og stillir á *Installed by default* ef allir eiga að fá pluginið.

Bifröst-tengingin þarf að vera tengd í Claude og notandi þarf lesaðgang að félaginu í Business Central. Nánar í [plugin/README.md](plugin/README.md).

## Fyrirvari

Þetta er ekki opinber vara eða þjónusta Origo. Efnið er birt til stuðnings og eru mælaborðin, gögnin og leiðbeiningarnar dæmi. Sýnidæmin byggja á tilbúnum prófunargögnum.

Origo ehf. · Unnið með aðstoð gervigreindar.
