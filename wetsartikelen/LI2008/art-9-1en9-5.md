---
type: wetsartikel-hub
artikel: Art. 9.1 en 9.5 LI 2008
wet: Leidraad Invordering 2008 (BWBR0024096)
aliases:
  - "Art. 9.1 LI 2008"
  - "Art. 9.5 LI 2008"
  - "Art. 9.1 en 9.5 LI 2008"
tags:
  - wetsartikel
  - li2008
  - art9-1
  - art9-5
---

# Art. 9.1 en 9.5 — Leidraad Invordering 2008

**Onderwerp:** Beleidskader betalingstermijnen (Leidraad bij art. 9 IW 1990)

---

## Alle annotaties

```dataview
TABLE datum AS "Analysedatum", peildatum AS "Peildatum", jas-versie AS "JAS"
FROM "analyses"
WHERE type = "jas-annotatie" AND contains(wet, "Leidraad") AND (contains(artikel, "9.1") OR contains(artikel, "9.5"))
SORT datum DESC
```

## Annotaties die naar dit artikel verwijzen

```dataview
TABLE artikel, datum AS "Analysedatum"
FROM "analyses"
WHERE type = "jas-annotatie" AND (contains(kruisreferenties, "Art. 9.1 LI 2008") OR contains(kruisreferenties, "Art. 9.5 LI 2008"))
SORT datum DESC
```

## Gerelateerd

- [[Art. 9 IW 1990]] — Wettelijke betalingstermijnen (Leidraad vult dit aan)
