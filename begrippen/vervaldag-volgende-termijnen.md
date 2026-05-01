---
type: begrip
begripsnaam: vervaldag-volgende-termijnen
jas-klasse: afleidingsregel
tags:
  - begrip
  - jas/afleidingsregel
  - wet/iw1990
  - art/9
markering: "elk van de volgende termijnen telkens een maand later"
bron: "Art. 9 lid 5 IW 1990"
bronnen:
  - "Art. 9 lid 5 IW 1990"
peildatum: 2026-01-01
interpretatiemethode: grammaticaal
toelichting-klasse: "Rekenregel die de vervaldatums van alle opvolgende termijnen bepaalt. Input: vervaldatum vorige termijn. Output: vervaldatum volgende termijn = vorige vervaldatum + één maand. De regel wordt iteratief toegepast voor elke volgende termijn."
definitie: "De rekenregel die voor elke invorderingstermijn na de eerste de vervaldatum vaststelt door bij de vervaldatum van de vorige termijn steeds één kalendermaand op te tellen"
soort: "datum (reeks)"
herkomst: "afgeleid"
aliases: []
is-een: []
heeft:
  - "[[begrippen/vervaldag-eerste-termijn]]"
  - "[[begrippen/telkens-een-maand-later]]"
leidt-tot: []
afleidingsregels:
  - "[[regels/AR-9-5d]]"
geldigheid-van: 2026-01-01
geldigheid-tot: ""
status: concept
---

## Definitie

*"elk van de volgende termijnen telkens een maand later"* *(Art. 9 lid 5 IW 1990, peildatum 2026-01-01)*

De rekenregel die voor elke invorderingstermijn na de eerste de vervaldatum vaststelt door bij de vervaldatum van de vorige termijn steeds één kalendermaand op te tellen

## Voorbeelden

| Stelling | Waar? | Toelichting |
|----------|-------|-------------|
| Een aanslagbiljet gedagtekend 15 maart 2026 heeft als tweede vervaldatum 15 mei 2026 en als derde vervaldatum 15 juni 2026. | ja | Eerste termijn: 15 april 2026; tweede termijn: 15 mei 2026 (= eerste + één maand); derde termijn: 15 juni 2026 (= tweede + één maand); enzovoorts. |
| Een aanslagbiljet gedagtekend 15 september 2026 heeft drie termijnen; de derde vervaldatum is 15 december 2026. | ja | Grensgeval: eerste termijn 15 oktober 2026; tweede termijn 15 november 2026; derde termijn 15 december 2026 — precies het einde van het belastingjaar. |
| De rekenregel wordt slechts eenmaal toegepast voor alle volgende termijnen. | nee | De regel wordt iteratief toegepast: voor elke volgende termijn afzonderlijk wordt één maand opgeteld bij de vorige vervaldatum. |

## Kenmerken

- De regel wordt iteratief toegepast voor elke termijn na de eerste, totdat alle termijnen zijn vastgesteld.
- De invoer voor elke stap is de vervaldatum van de vorige termijn (te beginnen bij de uitkomst van `vervaldag-eerste-termijn`).
- Art. 9 lid 10 IW 1990 sluit de Algemene termijnenwet uit; de maandtermijnen lopen kalenderstrikt.

## Relaties

| Type | Kardinaliteit | Begrip |
|------|---------------|--------|
| heeft | 1:1 | [[begrippen/vervaldag-eerste-termijn]] |
| heeft | 1:1 | [[begrippen/telkens-een-maand-later]] |
