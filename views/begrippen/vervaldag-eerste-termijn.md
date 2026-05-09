---
type: begrip
begrip-id: vervaldag-eerste-termijn
begripsnaam: vervaldag-eerste-termijn
jas-klasse: afleidingsregel
soort: datum
herkomst: afgeleid
status: concept
geldigheid-van: 2026-01-01
tags:
  - begrip
  - jas/afleidingsregel
  - wet/iw1990
  - art/9
afleidingsregels:
  - "[[views/regels/AR-9-5c]]"
---

## Definitie

*"De eerste termijn vervalt één maand na de dagtekening van het aanslagbiljet"*
*(Art. 9 lid 5 IW 1990, peildatum 2026-01-01)*

De rekenregel die de vervaldatum van de eerste gelijke invorderingstermijn vaststelt als het tijdstip gelegen één kalendermaand na de dagtekening van het aanslagbiljet

## Markeringen

| ID | Bron | Tekst | Bijdrage | Bevestigd |
|----|------|-------|---------|-----------|
| m-001 | Art. 9 lid 5 IW 1990 | De eerste termijn vervalt één maand na de dagtekening van het aanslagbiljet | primair | — |

## Voorbeelden

| Stelling | Waar? | Toelichting |
|----------|-------|-------------|
| Een aanslagbiljet gedagtekend 15 maart 2026 heeft als eerste vervaldatum 15 april 2026. | ja | Één maand na 15 maart 2026 is 15 april 2026; de eerste termijn vervalt op dat tijdstip. |
| Een aanslagbiljet gedagtekend 15 maart 2026 heeft als eerste vervaldatum 15 mei 2026. | nee | De eerste termijn vervalt één maand na de dagtekening (15 april 2026), niet twee maanden later; 15 mei 2026 is de vervaldatum van de tweede termijn. |
| Een aanslagbiljet gedagtekend 1 september 2026 heeft als eerste vervaldatum 1 oktober 2026. | ja | Grensgeval: één maand na 1 september 2026 is 1 oktober 2026; de aanslag is (bij dagtekening in september) invorderbaar in drie gelijke termijnen, waarvan de eerste op 1 oktober 2026 vervalt. |

## Kenmerken

- De rekenregel berekent uitsluitend de vervaldatum van de eerste termijn; de vervaldatums van de volgende termijnen worden bepaald door `vervaldag-volgende-termijnen`.
- Art. 9 lid 10 IW 1990 sluit de Algemene termijnenwet uit; de maandtermijn loopt kalenderstrikt.
- Invoer is de dagtekening van het aanslagbiljet; uitvoer is een datum (de vervaldatum van de eerste termijn).

## Relaties

| Type | Kardinaliteit | Begrip |
|------|---------------|--------|
| heeft | 1:1 | [[begrippen/dagtekening-aanslagbiljet]] |
| heeft | 1:1 | [[begrippen/een-maand-na-dagtekening]] |
