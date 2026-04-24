# Begrip-noot template

Gebruik deze template bij het aanmaken of actualiseren van een begrip-noot in `begrippen/`.

```markdown
---
type: begrip
term: [TERM]
wet: [volledige wetnaam (BWB-id)]
vindplaats: [VINDPLAATS]
jas-element: [JAS-ELEMENT]
definitie: "[DEFINITIE]"
datum: [YYYY-MM-DD]
tags:
  - begrip
  - [wet-afkorting-lowercase]
aliases:
  - "[TERM]"
---

# Begrip: [TERM]

**Definitie (letterlijk):** "[DEFINITIE]"

**Vindplaats:** [[VINDPLAATS-WIKI]], lid [N]

**JAS-element:** [JAS-ELEMENT]

**Wet:** [volledige wetnaam]

## Annotaties met dit begrip

```dataview
TABLE artikel, datum AS "Analysedatum"
FROM "analyses"
WHERE type = "jas-annotatie" AND contains(file.content, "[TERM]")
SORT datum DESC
```

## Gerelateerde begrippen

*(Vul handmatig aan met wiki-links naar verwante begrippen)*
```
