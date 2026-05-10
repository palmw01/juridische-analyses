# Juridische wetsanalyse — kennisgraaf voor de invorderingspraktijk

![License](https://img.shields.io/github/license/palmw01/juridische-analyses)
![Status](https://img.shields.io/badge/status-in%20ontwikkeling-yellow)
![Methodiek](https://img.shields.io/badge/methodiek-JAS%20v1.0.10-blue)
![Domein](https://img.shields.io/badge/domein-invordering%20rijksbelastingen-darkgreen)

Gestructureerde wetsanalyse op **art. 9 Invorderingswet 1990** (betalingstermijnen).  
De output is een traceerbare kennisgraaf: van wetstekst → JAS-annotaties → begrippen → afleidingsregels → RDF/GraphML.

Aangedreven door Claude Code + MCP-koppeling met [wetten.overheid.nl](https://wetten.overheid.nl), gevalideerd met een Python-toolchain.

---

## Voor wie

| Rol | Wat biedt dit |
|-----|---------------|
| **Jurist (invordering)** | Uitgewerkte analyse van art. 9 IW / §9.1 Leidraad, traceerbaar naar de wettekst |
| **Wetsanalist / methodiekbureau** | Werkend voorbeeld van de BZK-Wetsanalyse-methodiek met JAS-classificatie |
| **Kennisengineer / IT-jurist** | Machineleesbare regelmodellen (RDF, SKOS) en afleidingsregels in RegelSpraak-formaat |
| **Geïnteresseerde** | Proof-of-concept van AI-ondersteunde wetsanalyse met volledige audittrail |

## In een notendop

```
wetstekst                     kennisgraaf
    │                             ▲
    ▼                             │
┌──────────┐   ┌──────────┐   ┌──────────┐
│ bronnen/ │ → │ annotaties│ → │ begrippen│ → RDF/GraphML
│ (JSON)   │   │ (JAS)    │   │ + regels │
└──────────┘   └──────────┘   └──────────┘
                    ↑                ↑
              Claude Code        Python tools
              (/annoteer)        (validatie, views)
```

---

## Status

| Onderdeel | Status |
|-----------|--------|
| Art. 9 lid 1 IW — annotatie | ✅ Gereed |
| Art. 9 lid 5 IW — annotatie | ✅ Gereed |
| §9.1 Leidraad Invordering — annotatie | ✅ Gereed |
| Begrippen (A3a) — 28 stuks | ✅ Gereed |
| Afleidingsregels (A3b) — 10 stuks | ✅ Gereed |
| RDF/SKOS-export | ✅ Gereed |
| Validatie (L1–L3) — 41 bestanden, 0 fouten | ✅ Gereed |
| Enrichment-detectie | ✅ Gereed |
| Graph-export (GEXF/GraphML/PDF) | ✅ Gereed |
| **Totaal: art. 9 IW volledig doorlopen** | **✅ Proof-of-concept compleet** |
| Uitbreiding naar andere artikelen | 🔜 Volgende fase |

📊 Grafische weergave van het kennismodel: [`kennisgraaf/juridisch_kennismodel.pdf`](./kennisgraaf/juridisch_kennismodel.pdf)

---

## Vault-structuur

```
annotaties/{bwb-id}/   A2 — JAS-annotaties (markering + classificatie + diagram)
  art{N}.json          structuuranker per artikel
  art{N}-lid{L}.json   annotatie per lid: 7 JAS-klassen, kruisreferenties, knopen/kanten
begrippen/             A3a — begrippen (YAML)
  {slug}.yaml          definitie, soort, markeringen met brontraceerbaarheid
regels/                A3b — afleidingsregels (YAML)
  AR-{bwb-id}-*.yaml   als-dan regels: beslissings-, reken-, specialisatie-, beperkingsregels
bronnen/{bwb-id}/      primaire wetstekst (genormaliseerde MCP-responses)
schemas/               JSON Schema draft-07 (validatie)
ontologie/             JAS-ontologie + SKOS-mapping + soort-systeem
views/                 gegenereerde Obsidian-views (niet handmatig bewerken)
kennisgraaf/           graph-export: GEXF / GraphML / RDF Turtle / PDF
tools/                 Python-toolchain (9 scripts)
.claude/skills/        Claude Code skills + JAS-kaders
```

---

## Workflow

```bash
# 1. Structuur ophalen en annoteren
/annoteer art. 9 IW 1990
/annoteer art. 9 lid 1 IW 1990
/annoteer art. 9 lid 5 IW 1990

# 2. Betekenis vastleggen
/begrip-alles art. 9 IW 1990

# 3. Valideren
tools/.venv/bin/python tools/validate_note.py --file annotaties/BWBR0004770/art9-lid1.json

# 4. Views genereren
tools/.venv/bin/python tools/generate_views.py

# 5. Enrichment-controleren (bij meerdere bronnen per begrip)
tools/.venv/bin/python tools/check_enrichment.py

# 6. Kennismodel exporteren
/graph                                   # GEXF + GraphML
tools/.venv/bin/python tools/export_rdf.py  # RDF Turtle
```

---

## Python-toolchain

```bash
cd tools && python -m venv .venv && .venv/bin/pip install pyyaml jsonschema networkx
```

| Script | Functie | Wanneer |
|--------|---------|---------|
| `validate_note.py` | 3-laags validatie (schema/integriteit/kwaliteit) | Na elke schrijfactie |
| `generate_views.py` | Genereert Obsidian-views uit YAML/JSON | Na `/annoteer` of `/begrip` |
| `check_enrichment.py` | Detecteert begrippen met meerdere bronnen | Na nieuwe markeringen |
| `export_rdf.py` | Exporteert begrippen naar RDF Turtle (SKOS) | Bij externe koppeling |
| `fetch_wettenbank.py` | Normaliseert MCP-responses naar `bronnen/` | Via `/wettenbank` skill |
| `extract_kruisrefs.py` | Extraheert JCI URI-verwijzingen | Via `/wettenbank` skill |
| `generate_pdf_graph.py` | Genereert PDF-visualisatie | Op aanvraag |
| `query_rdf.py` | SPARQL-query op RDF-model | Bij analyse |
| `migrate_vault.py` | Vault-herstructurering | Bij schema-wijziging |

---

## Validatielagen

| Laag | Wat | Waar |
|------|-----|------|
| L1 | Schema-conformiteit (JSON Schema) | `schemas/*.schema.json` |
| L2 | Integriteit (verwijzingen kloppen) | `validate_note.py` |
| L3 | Kwaliteit (ontbrekende relaties/grensgevallen) | `validate_note.py` |

Huidig rapport: 41 bestanden ✅, 0 fouten, 13 waarschuwingen (L3).  
Zie [`rapporten/validatie-rapport.md`](./rapporten/validatie-rapport.md).

---

## Techniek

| Laag | Technologie |
|------|-------------|
| AI-assistent | Claude Code (Anthropic) met MCP |
| Wettenbrondata | `wetten.overheid.nl` via MCP (`wettenbank`-skill) |
| Vault | Obsidian (Markdown + YAML frontmatter) |
| Dataformaten | JSON (annotaties), YAML (begrippen/regels), JSON Schema (validatie) |
| Python | 3.10+, PyYAML, jsonschema, networkx |
| Kennisgraaf | GEXF (Gephi), GraphML, RDF Turtle (SKOS), DOT (Graphviz) |
| Regelmodellering | RegelSpraak v2.3.0 (zie [`regelspraak/`](./regelspraak/)) |

---

## Verantwoording

Deze werkruimte implementeert de **Wetsanalyse-methodiek** (Ministerie van BZK, 2024), gebaseerd op het **Juridisch Analyseschema (JAS) v1.0.10**, geworteld in Wesley Newcomb Hohfeld (1913).  
Kaders: [JAS-taxonomie](./.claude/skills/annoteer/kaders.md) · [Begrippen](./.claude/skills/begrip/kaders.md) · [Regels](./.claude/skills/begrip/kaders-regels.md) · [BWB-mapping](./.claude/skills/wettenbank/bwb-mapping.md)

Alleen **A2 (structuur zichtbaar maken)** en **A3 (betekenis vaststellen)** worden door AI ondersteund. A4–A6 (valideren, signaleren, kennismodel) worden uitgevoerd in een multidisciplinair team.

---

## Aan de slag

```bash
git clone git@github.com:palmw01/juridische-analyses.git
cd juridische-analyses

# Python-toolchain
cd tools && python -m venv .venv && .venv/bin/pip install pyyaml jsonschema networkx && cd ..

# Controleer of alles klopt
tools/.venv/bin/python tools/validate_note.py --file annotaties/BWBR0004770/art9-lid1.json

# Open in Obsidian (vault = ./)
# Of start een analysesessie met Claude Code
```
