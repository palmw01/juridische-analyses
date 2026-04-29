---
type: afleidingsregel
regel-id: AR-9-5c
naam: "berekenen vervaldag eerste termijn voorlopige aanslag"
soort: Rekenregel
tags:
  - afleidingsregel
  - wet/iw1990
  - art/9
afgeleid-van: "[[annotaties/iw1990/art9-5]]"
peildatum: 2026-01-01
bepaalt: "[[begrippen/vervaldag-eerste-termijn]]"
rechtsfeit: "[[begrippen/dagtekening-aanslagbiljet]]"
invoer:
  - "[[begrippen/dagtekening-aanslagbiljet]]"
  - "[[begrippen/een-maand-na-dagtekening]]"
uitvoer:
  - "[[begrippen/vervaldag-eerste-termijn]]"
operators:
  - "plus"
---

## Formele regel

**vervaldag-eerste-termijn moet berekend worden als**
dagtekening-aanslagbiljet plus één kalendermaand

## Toelichting

Herleidbaar tot art. 9 lid 5 IW 1990, tweede volzin: *"De eerste termijn vervalt één maand na de dagtekening van het aanslagbiljet."*

Grammaticale interpretatie: de vervaldatum van de eerste termijn is het resultaat van het optellen van één kalendermaand bij de dagtekening van het aanslagbiljet. De berekening is eenvoudig en enkelvoudig; er is geen tussenresultaat. Art. 9 lid 10 IW 1990 sluit de Algemene termijnenwet uit, zodat de termijn kalenderstrikt loopt.

## Voorbeeldreeksen

| Invoerwaarden | Verwachte uitkomst | Is voorspelling juridisch juist? |
|--------------|-------------------|---------------------------------|
| dagtekening: 15 maart 2026 | vervaldag eerste termijn: 15 april 2026 | ja — één maand na 15 maart is 15 april 2026 |
| dagtekening: 1 september 2026 | vervaldag eerste termijn: 1 oktober 2026 | ja — één maand na 1 september is 1 oktober 2026 |
| dagtekening: 31 januari 2026 | vervaldag eerste termijn: 28 februari 2026 (of 29 bij schrikkeljaar) | ja — grensgeval: de doelmaand (februari) telt minder dagen; de laatste dag van de doelmaand geldt als vervaldatum |
