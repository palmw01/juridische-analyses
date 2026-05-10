---
type: dashboard
tags:
  - dashboard
  - index
---

# Kennismodel — overzicht

## Begrippen

```dataview
TABLE
  begripsnaam AS "Begrip",
  jas-klasse AS "JAS-klasse",
  soort AS "Soort",
  herkomst AS "Herkomst",
  status AS "Status"
FROM "begrippen"
WHERE type = "begrip"
SORT begripsnaam ASC
```

## Afleidingsregels

```dataview
TABLE
  naam AS "Naam",
  soort AS "Regeltype",
  file.link AS "Bestand"
FROM "regels"
WHERE type = "afleidingsregel"
SORT naam ASC
```

## Annotaties

```dataview
TABLE
  artikel AS "Artikel",
  bwb-id AS "BWB-id",
  peildatum AS "Peildatum"
FROM "views/annotaties"
WHERE type = "annotatie"
SORT artikel ASC
```

## Begrippen zonder definitie

```dataview
TABLE
  begripsnaam AS "Begrip",
  status AS "Status"
FROM "begrippen"
WHERE type = "begrip" AND definitie = ""
SORT begripsnaam ASC
```

## Enrichment-kandidaten

Zie `rapporten/enrichment-queue.json` voor de actuele lijst van begrippen die aanvullende analyse vereisen.

```dataview
TABLE
  begripsnaam AS "Begrip",
  status AS "Status"
FROM "begrippen"
WHERE type = "begrip" AND status = "te-verrijken"
SORT begripsnaam ASC
```

---

## Toolchain

| Tool | Commando | Functie |
|------|---------|---------|
| `generate_views.py` | `tools/.venv/bin/python tools/generate_views.py` | Markdown-views genereren vanuit YAML/JSON |
| `check_enrichment.py` | `tools/.venv/bin/python tools/check_enrichment.py` | Enrichment-kandidaten detecteren |
| `validate_note.py` | `tools/.venv/bin/python tools/validate_note.py --file [pad]` | Schema-validatie uitvoeren |
| `export_rdf.py` | `tools/.venv/bin/python tools/export_rdf.py` | RDF Turtle exporteren |
| `/graph` | Claude Code skill | GEXF/GraphML-export voor Gephi |
