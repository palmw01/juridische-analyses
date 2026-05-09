---
type: begrip
begripsnaam: resterende-maanden-jaar
jas-klasse: variabele
tags:
  - begrip
  - jas/variabele
  - wet/iw1990
  - art/9
  - tussenresultaat
markering: "nog maanden van het jaar overblijven"
bron: "Art. 9 lid 5 IW 1990"
bronnen:
  - "Art. 9 lid 5 IW 1990"
peildatum: 2026-01-01
interpretatiemethode: grammaticaal
toelichting-klasse: "Variabele die het aantal resterende kalendermaanden in het belastingjaar weergeeft, te tellen na de maand die in de dagtekening van het aanslagbiljet is vermeld. De waarde varieert naar gelang de dagtekening (max. 11 bij januari, min. 0 bij december)."
definitie: "Het aantal kalendermaanden dat in het belastingjaar resteert na de maand die in de dagtekening van het aanslagbiljet is vermeld, en dat gelijk is aan het aantal gelijke termijnen waarin de voorlopige aanslag invorderbaar is op grond van art. 9 lid 5 IW 1990"
soort: "getal"
herkomst: "afgeleid"
aliases: []
is-een: []
heeft:
  - "[[begrippen/maand-dagtekening-aanslagbiljet]]"
leidt-tot:
  - "[[begrippen/termijnenberekening-resterende-maanden]]"
afleidingsregels:
  - "[[regels/AR-9-5b]]"
geldigheid-van: 2026-01-01
geldigheid-tot: ""
status: concept
---

## Definitie

*"nog maanden van het jaar overblijven"* *(Art. 9 lid 5 IW 1990, peildatum 2026-01-01)*

Het aantal kalendermaanden dat in het belastingjaar resteert na de maand die in de dagtekening van het aanslagbiljet is vermeld, en dat gelijk is aan het aantal gelijke termijnen waarin de voorlopige aanslag invorderbaar is op grond van art. 9 lid 5 IW 1990

## Voorbeelden

| Stelling | Waar? | Toelichting |
|----------|-------|-------------|
| Een aanslagbiljet gedagtekend in maart 2026 levert een resterende-maanden-jaar van 9. | ja | Na maart resteren in 2026 negen maanden (april t/m december); de voorlopige aanslag is invorderbaar in negen gelijke termijnen. |
| Een aanslagbiljet gedagtekend in november 2026 levert een resterende-maanden-jaar van 1. | ja | Grensgeval: na november resteert slechts één maand (december). De derde volzin van lid 5 bepaalt dat bij niet méér dan één termijn lid 1 herneemt; lid 5 leidt dan niet tot termijneninvordering. |
| Een aanslagbiljet gedagtekend in januari 2026 levert een resterende-maanden-jaar van 11. | ja | Na januari resteren elf maanden (februari t/m december); de aanslag is invorderbaar in elf gelijke termijnen. |

## Kenmerken

- De variabele is een tussenresultaat: zij wordt berekend als invoer voor de hoofdregel van lid 5 (het aantal termijnen).
- Bereik: 0 (december) t/m 11 (januari); bij 0 of 1 treedt de terugvalregel van de derde volzin in werking.
- De waarde is afhankelijk van de maand van dagtekening en wordt bepaald door de rekenregel `AR-9-5b`.

## Relaties

| Type | Kardinaliteit | Begrip |
|------|---------------|--------|
| heeft | 1:1 | [[begrippen/maand-dagtekening-aanslagbiljet]] |
| leidt tot | — | [[begrippen/termijnenberekening-resterende-maanden]] |
