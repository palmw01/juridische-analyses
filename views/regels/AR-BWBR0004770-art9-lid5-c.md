---
regel-id: AR-BWBR0004770-art9-lid5-c
naam: "berekenen vervaldag eerste termijn voorlopige aanslag"
soort: Rekenregel
peildatum: 2026-01-01
tags:
  - afleidingsregel
  - wet/iw1990
  - art/9
annotatie-id: BWBR0004770/art9/lid5
uitvoer:
  - "[[views/begrippen/vervaldag-eerste-termijn]]"
invoer:
  - "[[views/begrippen/dagtekening-aanslagbiljet]]"
  - "[[views/begrippen/een-maand-na-dagtekening]]"
---

# berekenen vervaldag eerste termijn voorlopige aanslag

*Rekenregel · art. 9 lid 5 · IW1990*

## Invoer en uitvoer

**Rechtsfeit:** [[views/begrippen/dagtekening-aanslagbiljet]]

**Invoer:**
- [[views/begrippen/dagtekening-aanslagbiljet]]
- [[views/begrippen/een-maand-na-dagtekening]]

**Uitvoer:**
- [[views/begrippen/vervaldag-eerste-termijn]]

**Operators:** plus

## Formele regel

**vervaldag-eerste-termijn moet berekend worden als**
dagtekening-aanslagbiljet plus één kalendermaand

## Toelichting

Herleidbaar tot art. 9 lid 5 IW 1990, tweede volzin: *"De eerste termijn vervalt één maand na de dagtekening van het aanslagbiljet."*

Grammaticale interpretatie: de vervaldatum van de eerste termijn is het resultaat van het optellen van één kalendermaand bij de dagtekening van het aanslagbiljet. De berekening is eenvoudig en enkelvoudig; er is geen tussenresultaat. Art. 9 lid 10 IW 1990 sluit de Algemene termijnenwet uit, zodat de termijn kalenderstrikt loopt.

## Voorbeeldreeksen

| Invoerwaarden | Verwachte uitkomst | Juist? | Toelichting |
|--------------|-------------------|--------|-------------|
| dagtekening: 15 maart 2026 | vervaldag eerste termijn: 15 april 2026 | ja |  |
| dagtekening: 1 september 2026 | vervaldag eerste termijn: 1 oktober 2026 | ja |  |
| dagtekening: 31 januari 2026 | vervaldag eerste termijn: 28 februari 2026 (of 29 bij schrikkeljaar) | ja |  |
| dagtekening: 31 januari 2026 | vervaldag eerste termijn: 31 februari 2026 | nee | Grensgeval: 31 februari bestaat niet; vervaldag wordt laatste dag van de maand (28/29 feb). Art. 9 lid 10 IW sluit Algemene termijnenwet uit — kalenderstrikt. |
