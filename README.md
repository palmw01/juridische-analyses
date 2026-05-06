# Juridische wetsanalyse — Obsidian knowledge graph

[![Live Documentation](https://img.shields.io/badge/Live-Documentation-green)](https://palmw01.github.io/juridische-analyses/)
![Deployment Status](https://github.com/palmw01/juridische-analyses/actions/workflows/deploy-quartz.yml/badge.svg)
![License](https://img.shields.io/github/license/palmw01/juridische-analyses)

🌐 **Bekijk de live knowledge graph en documentatie:**  
https://palmw01.github.io/juridische-analyses/

> Dit project levert een machine-leesbare representatie van wetgeving op basis van het JAS, geschikt voor analyse en automatisering.

---

Werkruimte voor gestructureerde wetsanalyse op het domein **invordering van rijksbelastingen**, aangedreven door Claude Code en een MCP-koppeling met [wetten.overheid.nl](https://wetten.overheid.nl).

Het primaire artefact is een **Obsidian knowledge graph**: atomaire entiteitsbestanden per annotatie, begrip en afleidingsregel, verbonden via wiki-links en doorzoekbaar via Dataview en Obsidian Graph View.

---

## Vault-structuur

```
wetteksten/       ← letterlijke wetstekst per bron (objectief, MCP-afkomstig)
annotaties/       ← interpretatief werk per artikel/lid (A2-tussenproduct)
  iw1990/         ← per wet een submap; art[N].md = index-noot, art[N]-[L].md = lid-annotatie
begrippen/        ← atomaire begrip-noten (definitie, voorbeelden, kenmerken, relaties)
regels/           ← atomaire afleidingsregel-noten (als-dan, voorbeeldreeksen)
graaf/            ← graph-export output: graph.gexf + graph.graphml (gegenereerd via /graph)
.claude/skills/   ← skill-documentatie en graph-exportscripts voor Claude Code
```

---

## Gebruik

### Workflow

```
/annoteer art. [A] [W]         →  Flow A: wetstekst-noot + index-noot (structuurankers)
/annoteer art. [A] lid [L] [W] →  Flow B: lid-annotatie-noot + lege begrip-noten (A2)
/begrip-alles art. [A] [W]     →  A3: definities, voorbeelden, relaties, afleidingsregels
```

Voor bronnen zonder leden (Leidraad, beleid):
```
/annoteer sectie [ref] [W]     →  Flow C: wetstekst-noot + directe annotatie-noot
```

Voorbeeld:
```
/annoteer art. 9 IW 1990
/annoteer art. 9 lid 1 IW 1990
/begrip-alles art. 9 IW 1990
```

### Graph-export (Gephi / Cytoscape)

De vault is exporteerbaar als GraphML en GEXF voor analyse in Gephi of Cytoscape:

```
/graph            →  exporteer naar graaf/graph.gexf + graaf/graph.graphml
/graph model      →  hergenereeer graph-model.json + exporteer
```

Het `graph-model.json` beschrijft node-types, edge-types, JAS-kleurcodering en exportinstellingen. Gebruik `/graph model` nadat nieuwe frontmatter-velden aan de templates zijn toegevoegd.

### Installatie

1. Kloon de `wetten-overheid-tools` repository naast deze repo.
2. De MCP-server is geconfigureerd in `.claude/settings.json`.

---

## Juridisch Analyseschema (JAS) v1.0.10

Wetsartikelen worden geannoteerd conform het **Juridisch Analyseschema v1.0.10** (MinBZK, 2024), gebaseerd op Wesley Newcomb Hohfeld (1913).

Het JAS maakt interpretatie- en preciseringskeuzes traceerbaar en vormt de basis voor ICT-implementatie van regelgeving.

- **Annotatiekaders**: [`.claude/skills/annoteer/kaders.md`](./.claude/skills/annoteer/kaders.md) — alle 13 JAS-elementen; 4 interpretatiemethoden (grammaticaal, systematisch, teleologisch, wetshistorisch); 4 typen afleidingsregels; diagram-centrum-prioritering; knooplabel-truncatieregels; delegatietype-beslisregel (verplicht/facultatief); Mermaid-diagramregels en kleurcodering
- **Begrippenkader**: [`.claude/skills/begrip/kaders.md`](./.claude/skills/begrip/kaders.md) — naamgeving, definitie, soort, herkomst, kardinaliteit, identificatie (A3a + A6d)
- **Regelkader**: [`.claude/skills/begrip/kaders-regels.md`](./.claude/skills/begrip/kaders-regels.md) — beslisboom regeltype-classificatie; taalpatronen incl. Beperkingsregel variant A/B; tussenresultaten; RegelSpraaak-correspondentietabel incl. vergelijkingsoperatoren; Specialisatieregel-voorbeeldformat (A3b + A6e)
- **Skill /annoteer**: [`.claude/skills/annoteer/SKILL.md`](./.claude/skills/annoteer/SKILL.md) — markeringen + classificaties + Mermaid-diagram (A2)
- **Skill /begrip**: [`.claude/skills/begrip/SKILL.md`](./.claude/skills/begrip/SKILL.md) — begrippen + afleidingsregels (A3)
- **Skill /graph**: [`.claude/skills/graph/SKILL.md`](./.claude/skills/graph/SKILL.md) — vault → GEXF/GraphML; `/graph model` hergenereert ook graph-model.json
- **BWB-mapping**: [`.claude/skills/wettenbank/bwb-mapping.md`](./.claude/skills/wettenbank/bwb-mapping.md)
- **Kruisreferentieprotocol**: [`.claude/skills/wettenbank/verwijzingen.md`](./.claude/skills/wettenbank/verwijzingen.md) — JCI URI-extractie, forward/backward kruisreferenties

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
| `#art/25` | Alles dat art. 25 betreft |

Kleuren zijn direct geconfigureerd in `.obsidian/graph.json` conform de JAS-kleurcodering — geen handmatige instelling nodig.

### Local Graph

Elke noot heeft een eigen lokale graph die alleen de directe verbindingen toont:

- **Openen:** Command Palette (`Ctrl+P`) → "Open local graph"  
- **Vastzetten:** Sleep het venster naar de rechterzijbalk voor permanent zicht naast de noot
- **Aanbevolen depth:** `2` voor een begrip-netwerk (begrip → gerelateerde begrippen), `3` voor een artikel-overzicht (artikel → begrippen → afleidingsregels)
- **Incoming/Outgoing:** Schakel af afzonderlijk om alleen verwijzingen vanúit of náár de noot te tonen
- **Relatierichting:** Wiki-links in begrip-noten zijn altijd *uitgaand* (forward-only): een begrip beschrijft uitsluitend relaties die vanuit zichzelf lopen. Backward links worden niet opgenomen — Obsidian genereert die automatisch als backlinks. Dit voorkomt dubbele of verkeerd gerichte kanten in de graph.

### Filterpatronen (Global Graph)

| Filter | Resultaat |
|--------|-----------|
| `tag:#jas/rechtsbetrekking` | Alleen rechtsbetrekkingen |
| `tag:#jas/afleidingsregel` | Alleen afleidingsregels |
| `tag:#tussenresultaat` | Alleen tussenresultaten in algoritmen |
| `tag:#wet/iw1990` | Alles m.b.t. IW 1990 |
| `path:begrippen/` | Alleen begrip-noten |

### Plugin-aanbevelingen

| Plugin | Functie | Installatie |
|--------|---------|------------|
| **Dataview** | Tabellen en lijsten op basis van frontmatter | Reeds geïnstalleerd |
| **Templater** | Templates met dynamische velden | Reeds geïnstalleerd |
| **Breadcrumbs** | Hiërarchische relaties zichtbaar in een eigen view; gebruik `is-een` als parent-relatie en `leidt-tot` als child-relatie | Community Plugins |
| **Juggl** | Interactieve graph met meer filteropties | Community Plugins |
