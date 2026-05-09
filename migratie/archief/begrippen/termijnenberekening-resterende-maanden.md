---
type: begrip
begripsnaam: termijnenberekening-resterende-maanden
jas-klasse: afleidingsregel
tags:
  - begrip
  - jas/afleidingsregel
  - wet/iw1990
  - art/9
markering: "in zoveel gelijke termijnen als er na de maand, die in de dagtekening van het aanslagbiljet is vermeld, nog maanden van het jaar overblijven"
bron: "Art. 9 lid 5 IW 1990"
bronnen:
  - "Art. 9 lid 5 IW 1990"
peildatum: 2026-01-01
interpretatiemethode: systematisch
toelichting-klasse: "Rekenregel die het aantal invorderingstermijnen bepaalt. Input: maand van de dagtekening (tijdsaanduiding) en het resterende aantal kalendermaanden (variabele). Output: het exacte aantal gelijke maandelijkse termijnen. Logica: bij dagtekening in januari zijn er 11 termijnen; bij oktober 2, bij november 1 (terugval naar lid 1 via derde volzin)."
definitie: "De rekenregel die het aantal gelijke invorderingstermijnen bepaalt door het aantal kalendermaanden te tellen dat in het belastingjaar resteert na de maand die in de dagtekening van het aanslagbiljet is vermeld"
soort: "getal"
herkomst: "afgeleid"
aliases: []
is-een: []
heeft:
  - "[[begrippen/maand-dagtekening-aanslagbiljet]]"
  - "[[begrippen/resterende-maanden-jaar]]"
leidt-tot:
  - "[[begrippen/invorderbaarheid-in-gelijke-termijnen]]"
afleidingsregels:
  - "[[regels/AR-9-5b]]"
geldigheid-van: 2026-01-01
geldigheid-tot: ""
status: concept
---

## Definitie

*"in zoveel gelijke termijnen als er na de maand, die in de dagtekening van het aanslagbiljet is vermeld, nog maanden van het jaar overblijven"* *(Art. 9 lid 5 IW 1990, peildatum 2026-01-01)*

De rekenregel die het aantal gelijke invorderingstermijnen bepaalt door het aantal kalendermaanden te tellen dat in het belastingjaar resteert na de maand die in de dagtekening van het aanslagbiljet is vermeld

## Voorbeelden

| Stelling | Waar? | Toelichting |
|----------|-------|-------------|
| Een aanslagbiljet gedagtekend in februari 2026 levert op grond van deze rekenregel 10 termijnen op. | ja | Na februari resteren in 2026 tien maanden (maart t/m december); de aanslag is invorderbaar in tien gelijke termijnen. |
| Een aanslagbiljet gedagtekend in oktober 2026 levert 2 termijnen op. | ja | Na oktober resteren in 2026 twee maanden (november en december); de aanslag is invorderbaar in twee gelijke termijnen. |
| Een aanslagbiljet gedagtekend in november 2026 levert op grond van lid 5 eerste volzin slechts 1 termijn op, zodat lid 1 herneemt. | ja | Grensgeval: na november resteert slechts één maand; de derde volzin bepaalt dat bij niet meer dan één termijn lid 1 van toepassing is. De rekenregel levert weliswaar 1 op, maar de terugvalregel activeert lid 1. |

## Kenmerken

- De rekenregel is een tussenberekening: de uitkomst (het termijnenaantal) is invoer voor de beslissing of lid 5 of lid 1 van toepassing is.
- De rekenregel berekent het termijnenaantal via de variabele `resterende-maanden-jaar`; het termijnenaantal is identiek aan de waarde van die variabele.
- Bij een uitkomst ≤ 1 activeert de terugvalregel (`terugvalregel-lid-1`) de hoofdregel van lid 1.

## Relaties

| Type | Kardinaliteit | Begrip |
|------|---------------|--------|
| heeft | 1:1 | [[begrippen/maand-dagtekening-aanslagbiljet]] |
| heeft | 1:1 | [[begrippen/resterende-maanden-jaar]] |
| leidt tot | — | [[begrippen/invorderbaarheid-in-gelijke-termijnen]] |
