# Juridische wetsanalyse — Obsidian knowledge graph

[![Live Documentation](https://img.shields.io/badge/Live-Documentation-green)](https://palmw01.github.io/juridische-analyses/)
![Deployment Status](https://github.com/palmw01/juridische-analyses/actions/workflows/deploy-quartz.yml/badge.svg)
![License](https://img.shields.io/github/license/palmw01/juridische-analyses)

🌐 **Bekijk de live knowledge graph en documentatie:**  
https://palmw01.github.io/juridische-analyses/

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

De AI-output (annotatie-noten, begrip-noten, afleidingsregel-noten) is het analysemateriaal dat input vormt voor A4–A6. Die activiteiten vallen buiten de scope van deze werkruimte en worden uitgevoerd in een multidisciplinair team.

---

## Activiteit 2: Zichtbaar maken van de juridische structuur

Wetgeving bevat een impliciete juridische structuur — rechten, plichten, bevoegdheden, voorwaarden — die blootgelegd moet worden voordat de betekenis vastgesteld kan worden. Activiteit 2 bestaat uit drie samenhangende deelactiviteiten:

- **2a — Markeren:** afbakenen van wetsformuleringen die bij elkaar horen
- **2b — Classificeren:** elke markering voorzien van een klasse uit het Juridisch Analyseschema (JAS)
- **2c — Structuurdiagram:** grafische weergave van de juridische structuur voor een centrale klasse

### JAS als classificatie-instrument

Het **Juridisch Analyseschema v1.0.10** (MinBZK, 2024), gebaseerd op Wesley Newcomb Hohfeld (1913), is het instrument voor deelactiviteit 2b. Het schema kent 13 elementen waarmee de juridische grammatica van een wetsformulering zichtbaar wordt: rechtssubjecten, rechtsobjecten, rechtsfeiten, rechtsbetrekkingen (bevoegdheden, plichten, rechten, vrijstellingen) en de bijbehorende voorwaarden en afleidingsregels.

Door klassen toe te kennen worden de relaties tussen wetsformuleringen zichtbaar en ontstaat de basis voor de begrippen en afleidingsregels in Activiteit 3.

**Kaders en skill:** [kaders.md](./.claude/skills/annoteer/kaders.md) — 13 JAS-elementen, 4 interpretatiemethoden, diagramregels, kleurcodering | [SKILL.md /annoteer](./.claude/skills/annoteer/SKILL.md)

### Vault-product

Een `/annoteer`-run voor een artikel levert twee noten op:

- `annotaties/[wet]/art[N].md` — index-noot: structuuranker voor het artikel
- `annotaties/[wet]/art[N]-[L].md` — lid-annotatie: annotatietabel + Mermaid-structuurdiagram (2c)

---

## Activiteit 3: Vaststellen van de betekenis

Op basis van de geclassificeerde wetsformuleringen uit Activiteit 2 wordt de inhoudelijke betekenis vastgelegd. Activiteit 3 omvat drie deelactiviteiten:

- **3a — Begrippen:** voor elke markering een begrip met begripsnaam, definitie, voorbeelden als stellingen (waar/niet waar), kenmerken en relaties met andere begrippen
- **3b — Afleidingsregels:** berekeningen, beslissingen, specialisaties en beperkingen die bepalen hoe rechtsgevolgen intreden op basis van feiten en omstandigheden
- **3d — Traceerbaarheid:** elk begrip en elke afleidingsregel is direct herleidbaar naar de primaire juridische bron

### Traceerbaarheid als rode draad

Rechtmatigheid vereist dat beslissingen in de uitvoeringspraktijk traceerbaar zijn op wet- en regelgeving. In de vault is dit geïmplementeerd via de wikilink-keten:

```
begrip-noot  →  annotatie-noot  →  wetstekst-noot
```

Een begrip verwijst altijd naar de annotatie waaruit het is afgeleid. De annotatie verwijst naar de wetstekst-noot met de letterlijke wettekst. Zo is elk analyseresultaat direct herleidbaar naar de primaire juridische bron.

**Kaders en skills:** [begrippenkader](./.claude/skills/begrip/kaders.md) | [regelkader](./.claude/skills/begrip/kaders-regels.md) | [SKILL.md /begrip](./.claude/skills/begrip/SKILL.md)

### Vault-producten

- `begrippen/[slug].md` — begrip-noot: definitie, voorbeelden, kenmerken, relaties (A3a)
- `regels/[slug].md` — afleidingsregel-noot: als-dan patroon, voorbeeldreeksen (A3b)

---

## Vault-structuur

```
wetteksten/       ← letterlijke wetstekst per bron (objectief, MCP-afkomstig)
  iw1990/         ← per wet een submap
annotaties/       ← A2-producten: markering + klasse + structuurdiagram
  iw1990/         ← per wet een submap
    art9.md       ← index-noot (structuuranker artikel)
    art9-1.md     ← lid-annotatie: annotatietabel + Mermaid-diagram
begrippen/        ← A3a-producten: begrippen met definitie, kenmerken, relaties
regels/           ← A3b-producten: afleidingsregel-noten
graaf/            ← graph-export: graph.gexf + graph.graphml (partieel kennismodel A6)
.claude/skills/   ← skill-documentatie en kaders voor Claude Code
```

| Map | Wetsanalyse-product | Activiteit |
|-----|---------------------|-----------|
| `wetteksten/` | Primaire juridische bronnen | Input A2 |
| `annotaties/` | Markering + klasse + structuurdiagram | A2 (2a/2b/2c) |
| `begrippen/` | Begrippen + kenmerken + relaties | A3 (3a) |
| `regels/` | Afleidingsregels | A3 (3b) |
| `graaf/` | Graph-export | A6 (partieel) |

---

## AI-workflow

De workflow volgt de iteratieve structuur van Wetsanalyse: per artikel eerst A2, dan A3.

```
/annoteer art. [A] [W]         →  Flow A: wetstekst-noot + index-noot (2a)
/annoteer art. [A] lid [L] [W] →  Flow B: lid-annotatie + diagram (2b/2c)
/begrip-alles art. [A] [W]     →  A3: begrippen + afleidingsregels per lid
```

Voor bronnen zonder leden (Leidraad Invordering, beleid):
```
/annoteer sectie [ref] [W]     →  Flow C: wetstekst-noot + directe annotatie-noot
```

Voorbeeld — artikel 9 IW 1990 volledig doorlopen:
```
/annoteer art. 9 IW 1990
/annoteer art. 9 lid 1 IW 1990
/annoteer art. 9 lid 5 IW 1990
/begrip-alles art. 9 IW 1990
```

### Graph-export (Gephi / Cytoscape)

```
/graph            →  exporteer naar graaf/graph.gexf + graaf/graph.graphml
/graph model      →  hergenereeer graph-model.json + exporteer
```

### Installatie

1. Kloon de `wetten-overheid-tools` repository naast deze repo.
2. De MCP-server is geconfigureerd in `.claude/settings.json`.

---

## Obsidian Graph View

Alle entiteiten zijn voorzien van geneste tags zodat de graph filterbaar en kleurbaar is:

| Tag | Inhoud |
|-----|--------|
| `#wetstekst` | Alle wetstekst-noten |
| `#annotatie` | Alle annotatie-noten (index + lid) |
| `#begrip` | Alle begrip-noten |
| `#afleidingsregel` | Alle regel-noten |
| `#jas/rechtssubject` | Begrippen met klasse rechtssubject |
| `#jas/rechtsbetrekking` | Begrippen met klasse rechtsbetrekking |
| `#wet/iw1990` | Alles wat de IW 1990 betreft |
| `#art/9` | Alles dat art. 9 betreft |

Kleuren zijn geconfigureerd in `.obsidian/graph.json` conform de JAS-kleurcodering — geen handmatige instelling nodig.

### Local Graph

- **Openen:** Command Palette (`Ctrl+P`) → "Open local graph"
- **Aanbevolen depth:** `2` voor begrip-netwerk, `3` voor artikel-overzicht
- **Relatierichting:** Wiki-links in begrip-noten zijn altijd uitgaand (forward-only); Obsidian genereert backlinks automatisch

### Filterpatronen (Global Graph)

| Filter | Resultaat |
|--------|-----------|
| `tag:#jas/rechtsbetrekking` | Alleen rechtsbetrekkingen |
| `tag:#jas/afleidingsregel` | Alleen afleidingsregels |
| `tag:#tussenresultaat` | Alleen tussenresultaten |
| `tag:#wet/iw1990` | Alles m.b.t. IW 1990 |
| `path:begrippen/` | Alleen begrip-noten |

### Plugin-aanbevelingen

| Plugin | Functie | Status |
|--------|---------|--------|
| **Dataview** | Tabellen en lijsten op basis van frontmatter | Geïnstalleerd |
| **Templater** | Templates met dynamische velden | Geïnstalleerd |
| **Breadcrumbs** | Hiërarchische relaties via `is-een` en `leidt-tot` | Community Plugins |
| **Juggl** | Interactieve graph met meer filteropties | Community Plugins |
