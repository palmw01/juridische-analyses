---
type: wetsartikel-hub
artikel: Art. 28 IW 1990
wet: Invorderingswet 1990 (BWBR0004770)
aliases:
  - "Art. 28 IW 1990"
tags:
  - wetsartikel
  - iw1990
  - art28
---

# Art. 28 — Invorderingswet 1990

**Onderwerp:** Invorderingsrente
**Hoofdstuk:** V — Invorderingsrente

---

## Alle annotaties

```dataview
TABLE datum AS "Analysedatum", peildatum AS "Peildatum", jas-versie AS "JAS"
FROM "analyses"
WHERE type = "jas-annotatie" AND contains(wet, "Invorderingswet") AND (artikel = "Art. 28 IW 1990" OR contains(artikel, "Art. 28 lid"))
SORT datum DESC
```

## Annotaties die naar dit artikel verwijzen

```dataview
TABLE artikel, datum AS "Analysedatum"
FROM "analyses"
WHERE type = "jas-annotatie" AND contains(kruisreferenties, "Art. 28 IW 1990")
SORT datum DESC
```

## Gerelateerde artikelen

- [[Art. 9 IW 1990]] — Betalingstermijnen (aanvang rentetijdvak)
- [[Art. 25 IW 1990]] — Uitstel van betaling (schort rente op)
- [[Art. 29 IW 1990]] — Invorderingsrentevoet
