---
type: annotatie
artikel: "Art. 9 lid 1 IW 1990"
bwb-id: BWBR0004770
peildatum: 2026-01-01
structuurpositie: "Hoofdstuk II Invordering in eerste aanleg > Artikel 9 > Lid 1"
tags:
  - annotatie
  - wet/iw1990
  - art/9
onderdeel-van: "[[annotaties/iw1990/art9]]"
wetstekst: "[[wetteksten/iw1990/art9]]"
begrippen:
  - "[[begrippen/belastingaanslag]]"
  - "[[begrippen/invorderbaarheid]]"
  - "[[begrippen/zes-weken-na-dagtekening-aanslagbiljet]]"
  - "[[begrippen/zes-weken]]"
  - "[[begrippen/dagtekening-aanslagbiljet]]"
  - "[[begrippen/invorderbaarheid-belastingaanslag]]"
---

## Wetstekst lid 1 (letterlijk)

> **1** Een belastingaanslag is invorderbaar zes weken na de dagtekening van het aanslagbiljet.

## Annotatietabel

| Nr | Markering (letterlijk incl. lidwoord en verwijzingen) | JAS-klasse | Interpretatiemethode | Begrip | Signalering |
|----|------------------------------------------------------|-----------|---------------------|--------|-------------|
| 1 | "Een belastingaanslag" | **rechtsobject** | grammaticaal | [[begrippen/belastingaanslag]] | — |
| 2 | "is invorderbaar" | **rechtsbetrekking** | grammaticaal | [[begrippen/invorderbaarheid]] | ⚠ rechtssubjecten (belastingschuldige, ontvanger) niet expliciet benoemd in lid 1; impliciet via art. 2 en 3 IW 1990 |
| 3 | "zes weken na de dagtekening van het aanslagbiljet" | **voorwaarde** | grammaticaal | [[begrippen/zes-weken-na-dagtekening-aanslagbiljet]] | — |
| 4 | "zes weken" | **tijdsaanduiding** | grammaticaal | [[begrippen/zes-weken]] | — |
| 5 | "de dagtekening van het aanslagbiljet" | **tijdsaanduiding** | systematisch | [[begrippen/dagtekening-aanslagbiljet]] | ⚠ dubbelclassificatie: ook rechtsfeit (nr. 6); dagtekening markeert zowel het aanvangstijdstip van de invorderingstermijn als het rechtsscheppende moment dat de termijn doet ingaan |
| 6 | "de dagtekening van het aanslagbiljet" | **rechtsfeit** | systematisch | [[begrippen/dagtekening-aanslagbiljet]] | ⚠ hergebruik begrip-noot (zie nr. 5); als rechtsfeit: de dagtekening is de handeling waaraan het rechtsgevolg (aanvang invorderingstermijn) is verbonden |
| 7 | "Een belastingaanslag is invorderbaar zes weken na de dagtekening van het aanslagbiljet." | **afleidingsregel** | systematisch | [[begrippen/invorderbaarheid-belastingaanslag]] | — |

## Diagram

### Diagram 1 — lid 1: invorderbaarheid van de belastingaanslag

```mermaid
graph LR
    RF["rechtsfeit<br/>'dagtekening van het aanslagbiljet'"]:::rf
    RB["rechtsbetrekking<br/>'invorderbaar'"]:::rb
    RO["rechtsobject<br/>'belastingaanslag'"]:::ro
    VW["voorwaarde<br/>'zes weken na de dagtekening…'"]:::vw
    TA["tijdsaanduiding<br/>'zes weken'"]:::ta
    AR["afleidingsregel<br/>'belastingaanslag invorderbaar zes…'"]:::ar

    RF -->|triggert| RB
    RB -->|voorwerp| RO
    RB -->|geldig indien| VW
    RB -->|nader uitgewerkt in| AR
    VW --- TA

    classDef rb fill:#FF0000,color:#fff
    classDef ro fill:#70AD47,color:#fff
    classDef rf fill:#FFC000
    classDef vw fill:#7030A0,color:#fff
    classDef ta fill:#F4B942
    classDef ar fill:#00B0F0
```
