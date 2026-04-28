---
type: begrip
begripsnaam: vervaldag-eerste-termijn
jas-klasse: afleidingsregel
tags:
  - begrip
  - jas/afleidingsregel
  - wet/iw1990
  - art/9
markering: "De eerste termijn vervalt één maand na de dagtekening van het aanslagbiljet"
bron: "Art. 9 lid 5 IW 1990"
bronnen:
  - "Art. 9 lid 5 IW 1990"
peildatum: 2026-01-01
interpretatiemethode: grammaticaal
toelichting-klasse: "Rekenregel die de vervaldatum van de eerste maandelijkse termijn bepaalt. Input: dagtekening aanslagbiljet. Output: vervaldatum = dagtekening + één maand."
definitie: "De rekenregel die de vervaldatum van de eerste gelijke invorderingstermijn vaststelt als het tijdstip gelegen één kalendermaand na de dagtekening van het aanslagbiljet"
soort: "datum"
herkomst: "afgeleid"
aliases: []
is-een: []
heeft:
  - "[[begrippen/dagtekening-aanslagbiljet]]"
  - "[[begrippen/een-maand-na-dagtekening]]"
leidt-tot: []
afleidingsregels:
  - "[[regels/AR-9-5c]]"
geldigheid-van: 2026-01-01
geldigheid-tot: ""
status: concept
---

## Definitie

*"De eerste termijn vervalt één maand na de dagtekening van het aanslagbiljet"* *(Art. 9 lid 5 IW 1990, peildatum 2026-01-01)*

De rekenregel die de vervaldatum van de eerste gelijke invorderingstermijn vaststelt als het tijdstip gelegen één kalendermaand na de dagtekening van het aanslagbiljet

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
