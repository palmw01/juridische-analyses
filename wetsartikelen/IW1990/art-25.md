---
type: wetsartikel-hub
artikel: Art. 25 IW 1990
wet: Invorderingswet 1990 (BWBR0004770)
aliases:
  - "Art. 25 IW 1990"
tags:
  - wetsartikel
  - iw1990
  - art25
---

# Art. 25 — Invorderingswet 1990

## Alle annotaties

```dataview
TABLE datum AS "Analysedatum", peildatum AS "Peildatum", jas-versie AS "JAS"
FROM "analyses"
WHERE type = "jas-annotatie" AND contains(artikel, "Art. 25") AND contains(wet, "Invorderingswet")
SORT datum DESC
```

## Annotaties die naar dit artikel verwijzen

```dataview
TABLE artikel, datum AS "Analysedatum"
FROM "analyses"
WHERE type = "jas-annotatie" AND contains(kruisreferenties, "Art. 25 IW 1990")
SORT datum DESC
```
