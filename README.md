# Juridische wetsanalyse — Obsidian knowledge graph

![License](https://img.shields.io/github/license/palmw01/juridische-analyses)

Werkruimte voor gestructureerde wetsanalyse op het domein **invordering van rijksbelastingen**. Doel is wetgeving zo te analyseren dat de resultaten bruikbaar zijn voor de uitvoeringspraktijk: rechtmatig, uitlegbaar en controleerbaar. Claude Code ondersteunt **Activiteit 2** (zichtbaar maken van de juridische structuur) en **Activiteit 3** (vaststellen van de betekenis), aangedreven door een MCP-koppeling met [wetten.overheid.nl](https://wetten.overheid.nl).

---

## Methodiek: Wetsanalyse

Wetsanalyse is een multidisciplinaire methode voor het expliciet maken, concretiseren en vastleggen van de betekenis van wet- en regelgeving, zodat de uitvoeringspraktijk rechtmatig, uitlegbaar en controleerbaar is. De activiteiten worden iteratief uitgevoerd — per artikel, per lid, steeds verder verfijnd — vanuit het perspectief van de uitvoeringspraktijk.

| # | Activiteit | Omschrijving | AI |
|---|-----------|-------------|-----|
| 1 | Bepalen van het werkgebied | Scope, juridische scenario's, bronnenselectie | — |
| **2** | **Zichtbaar maken van de juridische structuur** | Markeren, classificeren (JAS), structuurdiagram | **✓** |
| **3** | **Vaststellen van de betekenis** | Begrippen, afleidingsregels, traceerbaarheid | **✓** |
| 4 | Valideren van de analyseresultaten | Toetsing met juridische scenario's en voorbeeldreeksen | — |
| 5 | Signaleren van ontbrekende beleidsregels | Interpretaties en nadere invullingen ter oplevering | — |
| 6 | Opstellen van een kennismodel | Gegevensmodel, regelmodel, procesmodel | — |

De AI-output (annotatie-JSON's, begrip-YAML's, afleidingsregel-YAML's) is het analysemateriaal dat input vormt voor A4–A6. Die activiteiten vallen buiten de scope van deze werkruimte en worden uitgevoerd in een multidisciplinair team.

---

## Activiteit 2: Zichtbaar maken van de juridische structuur

Wetgeving bevat een impliciete juridische structuur — rechten, plichten, bevoegdheden, voorwaarden — die blootgelegd moet worden voordat de betekenis vastgesteld kan worden. Activiteit 2 bestaat uit drie samenhangende deelactiviteiten:

- **2a — Markeren:** afbakenen van wetsformuleringen die bij elkaar horen
- **2b — Classificeren:** elke markering voorzien van een klasse uit het Juridisch Analyseschema (JAS)
- **2c — Structuurdiagram:** grafische weergave van de juridische structuur voor een centrale klasse

### JAS als classificatie-instrument

Het **Juridisch Analyseschema v1.0.10** (MinBZK, 2024), gebaseerd op Wesley Newcomb Hohfeld (1913), is het instrument voor deelactiviteit 2b. Het schema kent 13 elementen waarmee de juridische grammatica van een wetsformulering zichtbaar wordt: rechtssubjecten, rechtsobjecten, rechtsfeiten, rechtsbetrekkingen (bevoegdheden, plichten, rechten, vrijstellingen) en de bijbehorende voorwaarden en afleidingsregels.

**Kaders en skill:** [kaders.md](./.claude/skills/annoteer/kaders.md) | [SKILL.md /annoteer](./.claude/skills/annoteer/SKILL.md)

### Vault-producten A2

Een `/annoteer`-run voor een artikel levert op:

- `annotaties/{bwb-id}/art{N}.json` — index-JSON: structuuranker voor het artikel
- `annotaties/{bwb-id}/art{N}-lid{L}.json` — lid-annotatie-JSON: annotatietabel + structuurdiagram (knopen/kanten)
- `begrippen/{slug}.yaml` — begrip-stubs met `markeringen[]`-lijst (lege definitie)

Na schrijven worden automatisch Markdown-views gegenereerd in `views/annotaties/` en `views/begrippen/`.

---

## Activiteit 3: Vaststellen van de betekenis

Op basis van de geclassificeerde wetsformuleringen uit Activiteit 2 wordt de inhoudelijke betekenis vastgelegd. Activiteit 3 omvat twee deelactiviteiten:

- **3a — Begrippen:** voor elke markering een begrip met begripsnaam, definitie, voorbeelden als stellingen (waar/niet waar), kenmerken en relaties met andere begrippen
- **3b — Afleidingsregels:** berekeningen, beslissingen, specialisaties en beperkingen die bepalen hoe rechtsgevolgen intreden op basis van feiten en omstandigheden

### Traceerbaarheid als rode draad

Rechtmatigheid vereist dat beslissingen in de uitvoeringspraktijk traceerbaar zijn op wet- en regelgeving. In de vault is dit geïmplementeerd via `markeringen[].bron-annotatie-id` in elke begrip-YAML en `annotatie-id` in elke regel-YAML. Elk analyseresultaat is direct herleidbaar naar de primaire juridische bron.

**Kaders en skills:** [begrippenkader](./.claude/skills/begrip/kaders.md) | [regelkader](./.claude/skills/begrip/kaders-regels.md) | [SKILL.md /begrip](./.claude/skills/begrip/SKILL.md)

### Vault-producten A3

- `begrippen/{slug}.yaml` — begrip: definitie, soort, herkomst, relaties, markeringen (A3a)
- `begrippen/{slug}.extra.json` — voorbeelden als stellingen + kenmerken (A3a)
- `regels/AR-{bwb-id}-art{N}-lid{L}-{nr}.yaml` — afleidingsregel: als-dan patroon, voorbeeldreeksen (A3b)

---

## Vault-structuur

```
annotaties/             ← A2-producten: markering + classificatie + structuurdiagram
  {bwb-id}/
    art{N}.json         ← index-JSON (structuuranker artikel)
    art{N}-lid{L}.json  ← lid-annotatie-JSON: annotatietabel + knopen/kanten
begrippen/              ← A3a-producten: begrip-YAML + extra-JSON
  {slug}.yaml           ← begrip: definitie, soort, relaties, markeringen
  {slug}.extra.json     ← voorbeelden + kenmerken
regels/                 ← A3b-producten: afleidingsregel-YAML
  AR-{bwb-id}-art{N}-lid{L}-{nr}.yaml
bronnen/                ← genormaliseerde MCP-responses (wetstekst per artikel)
  {bwb-id}/
    art{N}.json
schemas/                ← JSON Schema (draft-07) voor validatie
  annotatie-index.schema.json
  annotatie-lid.schema.json
  begrip.schema.json
  regel.schema.json
ontologie/              ← JAS-ontologie + SKOS-mapping + soort-systeem
  jas-ontologie.yaml
  skos-mapping.yaml
  soort-systeem.yaml
views/                  ← gegenereerde Obsidian-views (nooit handmatig editen)
  index.md              ← dashboard (Dataview)
  begrippen/            ← views per begrip
  annotaties/           ← views per annotatie
  regels/               ← views per afleidingsregel
kennisgraaf/                  ← graph-export
  graph.gexf            ← Gephi/Cytoscape-formaat
  graph.graphml         ← GraphML-formaat
  begrippen.ttl         ← RDF Turtle (SKOS-compatibel)
rapporten/              ← tools-output
  enrichment-queue.json ← begrippen die aanvullende analyse vereisen
  validatie-rapport.md
tools/                  ← Python-toolchain
.claude/skills/         ← skill-documentatie en kaders voor Claude Code
```

| Map | Wetsanalyse-product | Activiteit |
|-----|---------------------|-----------|
| `annotaties/` | Markering + classificatie + structuurdiagram | A2 (2a/2b/2c) |
| `begrippen/` | Begrippen + kenmerken + relaties | A3 (3a) |
| `regels/` | Afleidingsregels | A3 (3b) |
| `bronnen/` | Primaire juridische bronnen (genormaliseerd) | Input A2 |
| `views/` | Obsidian-weergave (gegenereerd) | Navigatie |
| `kennisgraaf/` | Graph-export | A6 (partieel) |

---

## AI-workflow

De workflow volgt de iteratieve structuur van Wetsanalyse: per artikel eerst A2, dan A3.

```
/annoteer art. [A] [W]         →  Flow A: index-JSON aanmaken (structuuranker)
/annoteer art. [A] lid [L] [W] →  Flow B: lid-annotatie-JSON + begrip-stubs (A2)
/begrip-alles art. [A] [W]     →  A3: definitie + extra-JSON + regel-YAML (A3a/3b)
```

Voor bronnen zonder leden (Leidraad Invordering, beleid):
```
/annoteer sectie [ref] [W]     →  Flow C: index-JSON + directe annotatie-JSON
```

Voorbeeld — artikel 9 IW 1990 volledig doorlopen:
```
/annoteer art. 9 IW 1990
/annoteer art. 9 lid 1 IW 1990
/annoteer art. 9 lid 5 IW 1990
/begrip-alles art. 9 IW 1990
```

### Enrichment-workflow

Begrippen die in meerdere annotaties voorkomen of conflicterende markeringen hebben, worden automatisch gedetecteerd:

```
tools/.venv/bin/python tools/check_enrichment.py
```

Zie `rapporten/enrichment-queue.json` voor de actuele lijst. Begrippen met een openstaande enrichment-beslissing worden geblokkeerd door `/begrip` totdat de beslissing is genomen.

### Graph-export (Gephi / Cytoscape)

```
/graph            →  exporteer naar kennisgraaf/graph.gexf + kennisgraaf/graph.graphml
/graph model      →  hergenereeer graph-model.json + exporteer
```

RDF Turtle (SKOS):
```
tools/.venv/bin/python tools/export_rdf.py
```

---

## Python-toolchain

| Tool | Commando | Wanneer uitvoeren |
|------|---------|------------------|
| `generate_views.py` | `tools/.venv/bin/python tools/generate_views.py` | Na elke `/annoteer` of `/begrip` run |
| `validate_note.py` | `tools/.venv/bin/python tools/validate_note.py --file [pad]` | Na elk schrijfcommando (automatisch door skills) |
| `check_enrichment.py` | `tools/.venv/bin/python tools/check_enrichment.py` | Na toevoegen van nieuwe markeringen |
| `export_rdf.py` | `tools/.venv/bin/python tools/export_rdf.py` | Bij RDF/SKOS-export voor externe systemen |

Installeer de venv eenmalig:
```
cd tools/ && python -m venv .venv && .venv/bin/pip install pyyaml jsonschema networkx
```

---

## Obsidian Graph View

Alle entiteiten zijn voorzien van geneste tags zodat de graph filterbaar en kleurbaar is:

| Tag | Inhoud |
|-----|--------|
| `#annotatie` | Alle annotatie-views |
| `#begrip` | Alle begrip-views |
| `#afleidingsregel` | Alle afleidingsregel-views |
| `#jas/rechtssubject` | Begrippen met klasse rechtssubject |
| `#jas/rechtsbetrekking` | Begrippen met klasse rechtsbetrekking |
| `#jas/afleidingsregel` | Begrippen met klasse afleidingsregel |
| `#wet/iw1990` | Alles wat de IW 1990 betreft |
| `#art/9` | Alles dat art. 9 betreft |
| `#tussenresultaat` | Alleen tussenresultaten |

Kleuren zijn geconfigureerd in `.obsidian/graph.json` conform de JAS-kleurcodering.

> **Let op:** Bewerk bestanden in `views/` nooit handmatig — ze worden overschreven door `generate_views.py`. Bronbestanden zijn de YAML's in `begrippen/` en `regels/` en de JSON's in `annotaties/`.

### Plugin-aanbevelingen

| Plugin | Functie | Status |
|--------|---------|--------|
| **Dataview** | Tabellen en lijsten op basis van frontmatter | Geïnstalleerd |
| **Templater** | Templates met dynamische velden | Geïnstalleerd |
| **Breadcrumbs** | Hiërarchische relaties via `is-een` en `leidt-tot` | Community Plugins |
| **Juggl** | Interactieve graph met meer filteropties | Community Plugins |

---

## Installatie

1. Kloon de `wetten-overheid-tools` repository naast deze repo.
2. De MCP-server is geconfigureerd in `.claude/settings.json`.
3. Installeer de Python-toolchain (zie boven).
