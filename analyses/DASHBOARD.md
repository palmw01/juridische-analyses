---
type: dashboard
aliases:
  - "Dashboard"
  - "Overzicht annotaties"
tags:
  - dashboard
---

# JAS-annotaties — Dashboard

## Alle annotaties

```dataview
TABLE artikel, wet, peildatum AS "Peildatum", datum AS "Analysedatum"
FROM "analyses"
WHERE type = "jas-annotatie"
SORT wet ASC, artikel ASC, datum DESC
```

## Recente annotaties (laatste 10)

```dataview
TABLE artikel, wet, datum AS "Analysedatum"
FROM "analyses"
WHERE type = "jas-annotatie"
SORT datum DESC
LIMIT 10
```

## Artikelen met meeste versies

```dataview
TABLE length(rows) AS "Versies", min(rows.datum) AS "Eerste", max(rows.datum) AS "Laatste"
FROM "analyses"
WHERE type = "jas-annotatie"
GROUP BY artikel
SORT length(rows) DESC
```

## Per wet

```dataview
TABLE rows.artikel, rows.datum AS "Data"
FROM "analyses"
WHERE type = "jas-annotatie"
GROUP BY wet
```

## Alle hub-notes (wetsartikelen)

```dataview
TABLE wet, artikel
FROM "wetsartikelen"
WHERE type = "wetsartikel-hub"
SORT wet ASC, artikel ASC
```
