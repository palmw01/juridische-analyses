# Handleiding

Deze gids laat zien hoe je de wetsanalyse-toolchain gebruikt — van wetstekst ophalen tot voorbeeldreeks afronden.

## Vereisten

- **Claude Code** — CLI of desktop-app ([claude.ai/code](https://claude.ai/code))
- **MCP-server wettenbank** — verbindt Claude Code met wetten.overheid.nl; configureer via de MCP-instellingen van Claude Code
- **Python 3.11+**
- **make**

## Opzet (eenmalig)

```bash
git clone git@github.com:palmw01/juridische-analyses.git
cd juridische-analyses
make setup
```

`make setup` maakt een virtuele Python-omgeving aan, installeert de dependencies en registreert de pre-commit en pre-push hooks. Na de setup blokkeert de pre-commit hook commits met L1/L2-fouten en controleert de pre-push hook of de testdekking op 100% staat.

## Werkwijze

De analyse volgt zes activiteiten (A1–A6), waarvan AI drie ondersteunt:

| Activiteit | Omschrijving | Wie |
|---|---|---|
| A1 — Werkgebied bepalen | Scope en bronnenselectie | Handmatig |
| **A2 — Markeren** | Wetstekst annoteren en JAS-classificeren | AI |
| **A3 — Betekenis vastleggen** | Begrippen, regels en relaties | AI |
| **A4b — Voorbeeldreeksen** | Testmatrix per afleidingsregel | AI |
| A4 — Valideren | Juridische beoordeling in teamverband | Handmatig |
| A5–A6 | Signaleren en kennismodel opstellen | Handmatig |

Het juridisch oordeel over voorbeeldreeksen (`is-voorspelling-juist`) vul je zelf in na de AI-stap. De skill `/beoordeel` ondersteunt deze menselijke validatie: ze leidt je per artefact langs de te beoordelen punten, legt je oordeel traceerbaar vast (wie/wanneer/onderbouwing) en herziet concepten op jouw aanwijzing — zonder het oordeel zelf te automatiseren.

## Typische workflow

### Optie 1 — Orchestrator (aanbevolen)

De orchestrator voert de volledige A2–A4b-keten uit voor één lid:

```
/wetsanalyse art. 9 lid 1 IW 1990
```

Tussendoor vraagt de orchestrator om bevestiging bij elke stap. Zonder pauzes:

```
/wetsanalyse art. 9 lid 1 IW 1990 --auto
```

Artikel al geannoteerd, alleen begrippen en regels updaten:

```
/wetsanalyse art. 9 lid 1 IW 1990 --vanaf begrip
```

### Optie 2 — Stapsgewijs

```
/wettenbank art. 9 IW 1990          wetstekst ophalen en opslaan in bronnen/
/annoteer art. 9 lid 1 IW 1990      A2: annoteren, classificeren en diagram
/begrip-alles art. 9 IW 1990        A3: begrippen en regels voor heel artikel
/valideer AR-BWBR0004770-art9-lid1-a   A4b: voorbeeldreeks voor één regel
```

## Belangrijkste commando's

| Commando | Functie |
|---|---|
| `/wettenbank art. [A] [W]` | Wetstekst ophalen |
| `/wetsanalyse art. [A] lid [L] [W]` | Volledige A2–A4b-keten (orchestrator) |
| `/annoteer art. [A] lid [L] [W]` | Stap A2: markeer → classificeer → diagram |
| `/begrip [slug]` | Stap A3: één begrip uitwerken |
| `/begrip-alles art. [A] [W]` | Stap A3: alle begrippen van een artikel |
| `/valideer AR-[id]` | Stap A4b: voorbeeldreeks opstellen |
| `/beoordeel [pad] \| art. [A] lid [L] [W] \| --openstaand` | Menselijke validatie: oordeel vastleggen + dialogische herzielus |

De sub-skills `/annoteer-markeer`, `/annoteer-classificeer`, `/annoteer-diagram` (binnen `/annoteer`) en `/begrip-scenario`, `/begrip-bron` (binnen `/begrip`) worden automatisch aangeroepen — je hoeft ze niet apart te starten.

De wetsnaam schrijf je als `IW 1990`, `AWR` of `Awb`. De BWB-mapping vertaalt dit automatisch naar het juiste BWB-id.

## Resultaten controleren

```bash
make validate       # L1-schema, L2-integriteit, L3-kwaliteitswaarschuwingen
make test           # volledige testsuite
make test-fast      # alleen unit-tests, stopt bij eerste fout
```

## Exports en webapp

```bash
make export-rdf     # begrippen → RDF Turtle / SKOS
make export-graph   # begrippen en relaties → GEXF / GraphML
make webapp         # statische site genereren in webapp/
make ci             # alles in één keer: tests + validatie + exports
```

Na `make webapp` open je `webapp/index.html` lokaal in een browser. De gepubliceerde versie staat op GitHub Pages.

## Veelvoorkomende situaties

**Wetstekst is al opgehaald, opnieuw ophalen overslaan**
Controleer of `bronnen/{bwb-id}/art{N}.json` bestaat. Als dat zo is, sla `/wettenbank` dan over — de skills lezen het bestaande bronbestand.

**Alleen één lid annoteren van een al gedeeltelijk uitgewerkt artikel**
Gebruik `/annoteer art. [A] lid [L] [W]` direct; dit overschrijft niet de andere leden.

**Voorbeeldreeks invullen na juridische beoordeling**
Draai `/beoordeel validaties/VR-*.yaml`: de skill loopt de `?`-kolommen met je door, vult `is-voorspelling-juist` (`ja`/`nee`/`nvt`) in en legt je oordeel vast in het `validatie`-blok. Handmatig kan ook: open het bestand en zet de waarden zelf.

**Commit mislukt**
De pre-commit hook blokkeert bij L1- of L2-fouten. Draai `make validate` om te zien welke bestanden fouten bevatten, herstel ze en commit opnieuw.
