# Begrip-noot template

Gebruik deze template bij het aanmaken of actualiseren van een begrip-noot in `begrippen/`.

```markdown
---
type: begrip
begripsnaam: [TERM]
jas-klasse: [Rechtssubject / Rechtsobject / Afleidingsregel / ...]
definitie: "[DEFINITIE — letterlijk geciteerd]"
annotaties:
  - "[[analyses/jas-annotatie-art[A]-[W]-[TIMESTAMP]]]"
vindplaatsen:
  - "[Art. [BD] lid Y [W]]"
datum-aangemaakt: [YYYY-MM-DD]
datum-bijgewerkt: [YYYY-MM-DD]
tags:
  - begrip
  - [wet-afkorting-lowercase]
aliases:
  - "[TERM]"
---

# [TERM]

## Definitie

"[DEFINITIE — letterlijk geciteerd]"

**Vindplaats:** [Art. [BD] lid Y [W]]

## Begripsvoorbeelden

| Stelling | Waar / Niet waar | Toelichting |
|----------|-----------------|-------------|
| [concrete stelling over toepassing van het begrip] | Waar | [waarom] |
| [concrete stelling over uitsluiting] | Niet waar | [waarom] |

## Kenmerken

- [kenmerk 1 — eigenschap van het begrip]
- [kenmerk 2]

## Relaties

| Relatie | Begrip | Toelichting |
|---------|--------|-------------|
| is een | [[begrippen/[bovenliggend-begrip]]] | [toelichting] |
| heeft | [[begrippen/[onderdeel]]] | [toelichting] |

## Annotatiebronnen

Annotaties die dit begrip voeden:

- [[analyses/jas-annotatie-art[A]-[W]-[TIMESTAMP]]]
```
