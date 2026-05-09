---
type: afleidingsregel
regel-id: AR-9-5d
naam: "berekenen vervaldag volgende termijnen voorlopige aanslag"
soort: Rekenregel
tags:
  - afleidingsregel
  - wet/iw1990
  - art/9
afgeleid-van: "[[annotaties/iw1990/art9-5]]"
peildatum: 2026-01-01
bepaalt: "[[begrippen/vervaldag-volgende-termijnen]]"
rechtsfeit: "[[begrippen/dagtekening-aanslagbiljet]]"
invoer:
  - "[[begrippen/vervaldag-eerste-termijn]]"
  - "[[begrippen/telkens-een-maand-later]]"
uitvoer:
  - "[[begrippen/vervaldag-volgende-termijnen]]"
operators:
  - "plus"
---

## Formele regel

**vervaldag-volgende-termijnen moet berekend worden als**
vervaldag vorige termijn plus één kalendermaand

*(iteratief toe te passen voor elke termijn na de eerste, totdat alle termijnen zijn vastgesteld)*

## Toelichting

Herleidbaar tot art. 9 lid 5 IW 1990, tweede volzin: *"elk van de volgende termijnen telkens een maand later."*

Grammaticale interpretatie: de vervaldatum van elke termijn na de eerste wordt berekend door één kalendermaand op te tellen bij de vervaldatum van de vorige termijn. De berekening is iteratief en wordt herhaald voor elke volgende termijn. Invoer voor de eerste iteratie is de uitkomst van AR-9-5c (vervaldag eerste termijn). Art. 9 lid 10 IW 1990 sluit de Algemene termijnenwet uit.

## Voorbeeldreeksen

| Invoerwaarden | Verwachte uitkomst | Is voorspelling juridisch juist? |
|--------------|-------------------|---------------------------------|
| vervaldag eerste termijn: 15 april 2026 (dagtekening 15 maart); resterende-maanden-jaar: 9 | vervaldagen: 15 april, 15 mei, 15 juni, 15 juli, 15 aug, 15 sept, 15 okt, 15 nov, 15 dec 2026 | ja — negen termijnen; elke volgende termijn één maand later |
| vervaldag eerste termijn: 1 oktober 2026 (dagtekening 1 september); resterende-maanden-jaar: 3 | vervaldagen: 1 okt, 1 nov, 1 dec 2026 | ja — drie termijnen; iteratief één maand opgeteld |
| vervaldag eerste termijn: 15 november 2026 (dagtekening 15 oktober); resterende-maanden-jaar: 2 | vervaldagen: 15 nov, 15 dec 2026 | ja — grensgeval: twee termijnen; de laatste termijn vervalt op 15 december 2026, het einde van het belastingjaar |
