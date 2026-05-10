---
type: annotatie
annotatie-id: BWBR0004770/art9/lid1
artikel: "Art. 9 lid 1 IW 1990"
bwb-id: BWBR0004770
peildatum: 2026-01-01
tags:
  - annotatie
  - wet/iw1990
  - art/9
begrippen:
  - "[[views/begrippen/belastingaanslag]]"
  - "[[views/begrippen/invorderbaarheid]]"
  - "[[views/begrippen/zes-weken-na-dagtekening-aanslagbiljet]]"
  - "[[views/begrippen/zes-weken]]"
  - "[[views/begrippen/dagtekening-aanslagbiljet]]"
  - "[[views/begrippen/invorderbaarheid-belastingaanslag]]"
---

## Wetstekst lid 1 (letterlijk)

> **1** Een belastingaanslag is invorderbaar zes weken na de dagtekening van het aanslagbiljet.

*Hoofdstuk II Invordering in eerste aanleg > Artikel 9 > Lid 1*

## Annotatietabel

| Nr | Markering | JAS-klasse | Methode | Begrip | Signalering |
|----|-----------|-----------|---------|--------|-------------|
| r-001 | Een belastingaanslag | **rechtsobject** | grammaticaal | [[views/begrippen/belastingaanslag]] | — |
| r-002 | is invorderbaar | **rechtsbetrekking** | grammaticaal | [[views/begrippen/invorderbaarheid]] | ⚠ rechtssubjecten (belastingschuldige, ontvanger) niet expliciet benoemd in lid 1; impliciet via art. 2 en 3 IW 1990 |
| r-003 | zes weken na de dagtekening van het aanslagbiljet | **voorwaarde** | grammaticaal | [[views/begrippen/zes-weken-na-dagtekening-aanslagbiljet]] | — |
| r-004 | zes weken | **tijdsaanduiding** | grammaticaal | [[views/begrippen/zes-weken]] | — |
| r-005 | de dagtekening van het aanslagbiljet | **tijdsaanduiding** | systematisch | [[views/begrippen/dagtekening-aanslagbiljet]] | ⚠ dubbelclassificatie: ook rechtsfeit (nr. 6); dagtekening markeert zowel het aanvangstijdstip van de invorderingstermijn als het rechtsscheppende moment dat de termijn doet ingaan |
| r-006 | de dagtekening van het aanslagbiljet | **rechtsfeit** | systematisch | [[views/begrippen/dagtekening-aanslagbiljet]] | ⚠ hergebruik begrip-noot (zie nr. 5); als rechtsfeit: de dagtekening is de handeling waaraan het rechtsgevolg (aanvang invorderingstermijn) is verbonden |
| r-007 | Een belastingaanslag is invorderbaar zes weken na de dagtekening van het aanslagbiljet. | **afleidingsregel** | systematisch | [[views/begrippen/invorderbaarheid-belastingaanslag]] | — |

## Diagram

```mermaid
graph LR
    RF["rechtsfeit 'dagtekening van het aanslagbiljet'"]:::rf
    RB["rechtsbetrekking 'invorderbaar'"]:::rb
    RO["rechtsobject 'belastingaanslag'"]:::ro
    VW["voorwaarde 'zes weken na de dagtekening…'"]:::vw
    TA["tijdsaanduiding 'zes weken'"]:::ta
    AR["afleidingsregel 'belastingaanslag invorderbaar zes…'"]:::ar
    RF -->|triggert| RB
    RB -->|voorwerp| RO
    RB -->|geldig indien| VW
    RB -->|nader uitgewerkt in| AR
    VW --- TA
    classDef ar fill:#00B0F0
    classDef rb fill:#FF0000,color:#fff
    classDef rf fill:#FFC000
    classDef ro fill:#70AD47,color:#fff
    classDef ta fill:#F4B942
    classDef vw fill:#7030A0,color:#fff
```

## Delegatiestructuur

Geen delegatiebevoegdheden.
