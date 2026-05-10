---
type: annotatie
annotatie-id: BWBR0004770/art9/lid5
artikel: "Art. 9 lid 5 IW 1990"
bwb-id: BWBR0004770
peildatum: 2026-01-01
tags:
  - annotatie
  - wet/iw1990
  - art/9
begrippen:
  - "[[views/begrippen/voorlopige-aanslag]]"
  - "[[views/begrippen/logische-of]]"
  - "[[views/begrippen/voorlopige-conserverende-aanslag-ib]]"
  - "[[views/begrippen/invorderbaarheid]]"
  - "[[views/begrippen/in-afwijking-van-eerste-lid]]"
  - "[[views/begrippen/dagtekening-in-vaststellingsjaar]]"
  - "[[views/begrippen/dagtekening-aanslagbiljet]]"
  - "[[views/begrippen/maand-dagtekening-aanslagbiljet]]"
  - "[[views/begrippen/termijnenberekening-resterende-maanden]]"
  - "[[views/begrippen/resterende-maanden-jaar]]"
  - "[[views/begrippen/invorderbaarheid-in-gelijke-termijnen]]"
  - "[[views/begrippen/vervaldag-eerste-termijn]]"
  - "[[views/begrippen/een-maand-na-dagtekening]]"
  - "[[views/begrippen/vervaldag-volgende-termijnen]]"
  - "[[views/begrippen/telkens-een-maand-later]]"
  - "[[views/begrippen/terugvalregel-lid-1]]"
  - "[[views/begrippen/termijnbedrag]]"
  - "[[views/begrippen/totaalbedrag-belastingaanslag]]"
---

## Wetstekst lid 5 (letterlijk)

> **5** In afwijking van het eerste lid is een voorlopige aanslag in de inkomstenbelasting of in de vennootschapsbelasting en een voorlopige conserverende aanslag in de inkomstenbelasting, waarvan het aanslagbiljet een dagtekening heeft die ligt in het jaar waarover deze is vastgesteld, invorderbaar in zoveel gelijke termijnen als er na de maand, die in de dagtekening van het aanslagbiljet is vermeld, nog maanden van het jaar overblijven. De eerste termijn vervalt één maand na de dagtekening van het aanslagbiljet en elk van de volgende termijnen telkens een maand later. Indien de toepassing van de eerste volzin niet leidt tot meer dan één termijn, vindt het eerste lid toepassing.

*Hoofdstuk II Invordering in eerste aanleg > Artikel 9 > Lid 5*

## Annotatietabel

| Nr | Markering | JAS-klasse | Methode | Begrip | Signalering |
|----|-----------|-----------|---------|--------|-------------|
| r-001 | een voorlopige aanslag in de inkomstenbelasting of in de vennootschapsbelasting | **rechtsobject** | grammaticaal | [[views/begrippen/voorlopige-aanslag]] | — |
| r-002 | of | **operator** | grammaticaal | [[views/begrippen/logische-of]] | ⚠ logische OR; verbindt IB en VPB als alternatieve belastingsoorten voor het toepassingsbereik van lid 5 |
| r-003 | een voorlopige conserverende aanslag in de inkomstenbelasting | **rechtsobject** | grammaticaal | [[views/begrippen/voorlopige-conserverende-aanslag-ib]] | — |
| r-004 | is ... invorderbaar | **rechtsbetrekking** | grammaticaal | [[views/begrippen/invorderbaarheid]] | ⚠ hergebruik begrip-noot; rechtssubjecten niet expliciet in lid 5; impliciet via art. 3 IW 1990. Soort-consistentiecheck: `invorderbaarheid` heeft `soort: waar-niet-waar` (binair); in lid-5-context is invorderbaarheid per termijn — soort incompatibel. A5-signaal: de wet bepaalt wanneer termijnen vervallen maar articuleert niet hoe de status per termijn op een peildatum wordt vastgesteld; dit vereist uitvoeringsbeleid of een implementatielaag. |
| r-005 | In afwijking van het eerste lid | **voorwaarde** | systematisch | [[views/begrippen/in-afwijking-van-eerste-lid]] | ⚠ specialisatiebepaling; markeert lid 5 als lex specialis t.o.v. art. 9 lid 1 voor de genoemde voorlopige aanslagen |
| r-006 | waarvan het aanslagbiljet een dagtekening heeft die ligt in het jaar waarover deze is vastgesteld | **voorwaarde** | grammaticaal | [[views/begrippen/dagtekening-in-vaststellingsjaar]] | ⚠ kwalificatieconditie: beperkt lid 5 tot aanslagen met een dagtekening in het belastingjaar; aanslagen vóór het jaar vallen onder lid 7 |
| r-007 | de dagtekening van het aanslagbiljet | **rechtsfeit** | systematisch | [[views/begrippen/dagtekening-aanslagbiljet]] | ⚠ hergebruik begrip-noot; hier als ankerpunt voor de termijnenberekening in lid 5 |
| r-008 | de maand, die in de dagtekening van het aanslagbiljet is vermeld | **tijdsaanduiding** | grammaticaal | [[views/begrippen/maand-dagtekening-aanslagbiljet]] | — |
| r-009 | in zoveel gelijke termijnen als er na de maand, die in de dagtekening van het aanslagbiljet is vermeld, nog maanden van het jaar overblijven | **afleidingsregel** | systematisch | [[views/begrippen/termijnenberekening-resterende-maanden]] | — |
| r-010 | nog maanden van het jaar overblijven | **variabele** | grammaticaal | [[views/begrippen/resterende-maanden-jaar]] | — |
| r-011 | In afwijking van het eerste lid is een voorlopige aanslag in de inkomstenbelasting of in de vennootschapsbelasting en een voorlopige conserverende aanslag in de inkomstenbelasting, waarvan het aanslagbiljet een dagtekening heeft die ligt in het jaar waarover deze is vastgesteld, invorderbaar in zoveel gelijke termijnen als er na de maand, die in de dagtekening van het aanslagbiljet is vermeld, nog maanden van het jaar overblijven. | **afleidingsregel** | systematisch | [[views/begrippen/invorderbaarheid-in-gelijke-termijnen]] | ⚠ specialisatieregel t.o.v. art. 9 lid 1; als-dan: als aan beide kwalificatievoorwaarden is voldaan (aanslagtype én dagtekening in jaar), dan invorderbaar in gelijke maandelijkse termijnen |
| r-012 | De eerste termijn vervalt één maand na de dagtekening van het aanslagbiljet | **afleidingsregel** | grammaticaal | [[views/begrippen/vervaldag-eerste-termijn]] | ⚠ reeks-statustoets: deze rekenregel produceert één vervaldatum; samen met markering 14 vormt het een reeks van N datums. De status van elke datum t.o.v. een peildatum is niet in de wettekst gearticuleerd — A5-signaal: ontbrekend uitvoeringsbeleid. |
| r-013 | één maand na de dagtekening van het aanslagbiljet | **tijdsaanduiding** | grammaticaal | [[views/begrippen/een-maand-na-dagtekening]] | — |
| r-014 | elk van de volgende termijnen telkens een maand later | **afleidingsregel** | grammaticaal | [[views/begrippen/vervaldag-volgende-termijnen]] | ⚠ reeks-statustoets: deze rekenregel produceert een reeks van N−1 vervaldatums (iteratief). Zie ook markering 12. |
| r-015 | telkens een maand later | **tijdsaanduiding** | grammaticaal | [[views/begrippen/telkens-een-maand-later]] | — |
| r-016 | Indien de toepassing van de eerste volzin niet leidt tot meer dan één termijn, vindt het eerste lid toepassing. | **afleidingsregel** | systematisch | [[views/begrippen/terugvalregel-lid-1]] | ⚠ beslissingsregel (terugvalregel); art. 9 lid 1 herneemt toepassing als het termijnenantal ≤ 1 is (bij dagtekening in december) |
| r-017 | gelijke | **afleidingsregel** | systematisch | [[views/begrippen/termijnbedrag]] | ⚠ rekenregel voor termijnbedrag; de eis dat termijnen 'gelijk' zijn, dwingt tot de berekening: totaalbedrag / aantal termijnen |
| r-018 | gelijke termijnen | **variabele** | systematisch | [[views/begrippen/termijnbedrag]] | ⚠ de variabele die de uitkomst van AR-9-5f representeert |
| r-019 | een belastingaanslag | **variabele** | systematisch | [[views/begrippen/totaalbedrag-belastingaanslag]] | ⚠ hergebruik markering uit lid 1; het totaalbedrag is noodzakelijk voor de berekening van het termijnbedrag (invoer voor AR-9-5f) |

## Diagram

```mermaid
graph LR
    RF["rechtsfeit 'dagtekening van het aanslagbiljet'"]:::rf
    RB["rechtsbetrekking 'invorderbaar'"]:::rb
    RO1["rechtsobject 'voorlopige aanslag (IB/VPB)'"]:::ro
    RO2["rechtsobject 'voorlopige conserverende…'"]:::ro
    VW1["voorwaarde 'In afwijking van het eerste lid'"]:::vw
    VW2["voorwaarde 'dagtekening in vaststellingsjaar'"]:::vw
    AR1["afleidingsregel 'in zoveel gelijke termijnen…'"]:::ar
    AR1f["afleidingsregel 'berekenen termijnbedrag'"]:::ar
    AR2["afleidingsregel 'eerste termijn vervalt één maand…'"]:::ar
    AR3["afleidingsregel 'volgende termijnen een maand later'"]:::ar
    AR4["afleidingsregel 'terugval lid 1 bij ≤ 1 termijn'"]:::ar
    VA["variabele 'maanden van het jaar overblijven'"]:::va
    VA2["variabele 'totaalbedrag belastingaanslag'"]:::va
    VA3["variabele 'termijnbedrag'"]:::va
    TA["tijdsaanduiding 'maand dagtekening aanslagbiljet'"]:::ta
    RF -->|triggert| RB
    RB -->|voorwerp| RO1
    RB -->|voorwerp| RO2
    RB -->|geldig indien| VW1
    RB -->|geldig indien| VW2
    RB -->|nader uitgewerkt in| AR1
    RB -->|nader uitgewerkt in| AR1f
    RB -->|nader uitgewerkt in| AR2
    RB -->|nader uitgewerkt in| AR3
    RB -->|nader uitgewerkt in| AR4
    AR1 -->|gebruikt| VA
    AR1 -->|gebruikt| TA
    AR1f -->|gebruikt| VA2
    AR1f -->|gebruikt| VA
    AR1f -->|gebruikt| VA3
    classDef ar fill:#00B0F0
    classDef rb fill:#FF0000,color:#fff
    classDef rf fill:#FFC000
    classDef ro fill:#70AD47,color:#fff
    classDef ta fill:#F4B942
    classDef va fill:#92D050
    classDef vw fill:#7030A0,color:#fff
```

## Delegatiestructuur

Geen delegatiebevoegdheden.
