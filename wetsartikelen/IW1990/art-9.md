---
type: wetsartikel-hub
artikel: Art. 9 IW 1990
wet: Invorderingswet 1990 (BWBR0004770)
aliases:
  - "Art. 9 IW 1990"
tags:
  - wetsartikel
  - iw1990
  - art9
---

# Art. 9 — Invorderingswet 1990

**Onderwerp:** Betalingstermijnen (invorderbaar worden van belastingaanslagen)
**Hoofdstuk:** II — Invordering in eerste aanleg

---

## Alle annotaties

```dataview
TABLE datum AS "Analysedatum", peildatum AS "Peildatum", jas-versie AS "JAS"
FROM "analyses"
WHERE type = "jas-annotatie" AND contains(wet, "Invorderingswet") AND (contains(artikel, "Art. 9 ") OR contains(artikel, "Art. 9 lid") OR artikel = "Art. 9 IW 1990")
SORT datum DESC
```

## Annotaties die naar dit artikel verwijzen

```dataview
TABLE artikel, datum AS "Analysedatum"
FROM "analyses"
WHERE type = "jas-annotatie" AND contains(kruisreferenties, "Art. 9 IW 1990")
SORT datum DESC
```

## Gerelateerde artikelen

- [[Art. 7 IW 1990]] — Betalingsplicht
- [[Art. 2 IW 1990]] — Begripsbepalingen (belastingaanslag, navorderingsaanslag, naheffingsaanslag)
