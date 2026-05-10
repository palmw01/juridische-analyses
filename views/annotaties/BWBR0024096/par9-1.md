---
type: annotatie
annotatie-id: BWBR0008003/par9-1
artikel: "Art. 9 lid 9.1 LI 2008"
bwb-id: BWBR0024096
peildatum: 2026-01-01
tags:
  - annotatie
  - wet/li2008
begrippen:
  - "[[views/begrippen/voorlopige-aanslag]]"
  - "[[views/begrippen/dagtekening-in-november-of-eerder]]"
  - "[[views/begrippen/termijn-eindigt-voor-31-december]]"
  - "[[views/begrippen/vervaldag-31-december]]"
  - "[[views/begrippen/31-december]]"
  - "[[views/begrippen/afwijkend-boekjaar]]"
  - "[[views/begrippen/vervaldag-laatste-dag-maand]]"
---

## Wetstekst lid 9.1 (letterlijk)

> **9.1** **[9.1]** In de gevallen waarin voor voorlopige aanslagen (bedoeld in [artikel 9, vijfde lid, van de wet](jci1.3:c:BWBR0004770&artikel=9)) die zijn gedagtekend in november of eerder, toepassing van de [wet](jci1.3:c:BWBR0004770) er toe zou leiden dat de enige of laatste betalingstermijn eindigt voor 31 december, dan wordt de vervaldag van deze termijn op 31 december gesteld. Bij afwijkende boekjaren wordt de laatste vervaldag steeds op de laatste dag van de maand gesteld.

*Artikel 1 Inleiding en toepassingsgebied > Artikel 9 Betalingstermijnen > Lid 9.1*

## Annotatietabel

| Nr | Markering | JAS-klasse | Methode | Begrip | Signalering |
|----|-----------|-----------|---------|--------|-------------|
| r-001 | voor voorlopige aanslagen (bedoeld in artikel 9, vijfde lid, van de wet) | **rechtsobject** | systematisch | [[views/begrippen/voorlopige-aanslag]] | — |
| r-002 | die zijn gedagtekend in november of eerder | **voorwaarde** | grammaticaal | [[views/begrippen/dagtekening-in-november-of-eerder]] | — |
| r-003 | toepassing van de wet er toe zou leiden dat de enige of laatste betalingstermijn eindigt voor 31 december | **voorwaarde** | systematisch | [[views/begrippen/termijn-eindigt-voor-31-december]] | — |
| r-004 | dan wordt de vervaldag van deze termijn op 31 december gesteld | **afleidingsregel** | grammaticaal | [[views/begrippen/vervaldag-31-december]] | **type**: Specialisatieregel (in afwijking van de hoofdregel in art. 9 lid 5 IW 1990) |
| r-005 | 31 december | **tijdsaanduiding** | grammaticaal | [[views/begrippen/31-december]] | — |
| r-006 | Bij afwijkende boekjaren | **voorwaarde** | grammaticaal | [[views/begrippen/afwijkend-boekjaar]] | — |
| r-007 | wordt de laatste vervaldag steeds op de laatste dag van de maand gesteld | **afleidingsregel** | grammaticaal | [[views/begrippen/vervaldag-laatste-dag-maand]] | **type**: Specialisatieregel |

## Diagram

```mermaid
graph LR
    AR1["afleidingsregel 'vervaldag op 31 december gesteld'"]:::ar
    VW1["voorwaarde 'gedagtekend in november of eerder'"]:::vw
    VW2["voorwaarde 'termijn eindigt voor 31 december'"]:::vw
    RO["rechtsobject 'voorlopige aanslagen'"]:::ro
    TA["tijdsaanduiding '31 december'"]:::ta
    VW1 --- RO
    VW2 --- RO
    AR1 -->|geldig indien| VW1
    AR1 -->|geldig indien| VW2
    AR1 -->|gebruikt| TA
    classDef ar fill:#00B0F0
    classDef ro fill:#70AD47,color:#fff
    classDef ta fill:#F4B942
    classDef vw fill:#7030A0,color:#fff
```

## Kruisreferenties

- 9 (forward)

## Delegatiestructuur

Geen delegatiebevoegdheden.
