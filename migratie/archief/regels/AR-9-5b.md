---
type: afleidingsregel
regel-id: AR-9-5b
naam: "berekenen resterende maanden jaar"
soort: Rekenregel
tags:
  - afleidingsregel
  - wet/iw1990
  - art/9
afgeleid-van: "[[annotaties/iw1990/art9-5]]"
peildatum: 2026-01-01
bepaalt: "[[begrippen/resterende-maanden-jaar]]"
rechtsfeit: "[[begrippen/dagtekening-aanslagbiljet]]"
invoer:
  - "[[begrippen/maand-dagtekening-aanslagbiljet]]"
uitvoer:
  - "[[begrippen/resterende-maanden-jaar]]"
operators:
  - "min"
---

## Formele regel

**resterende-maanden-jaar moet berekend worden als**
12 min maand-dagtekening-aanslagbiljet

*(waarbij de maand wordt uitgedrukt als ordegetal: januari = 1, februari = 2, …, december = 12)*

## Toelichting

Herleidbaar tot art. 9 lid 5 IW 1990, eerste volzin: *"in zoveel gelijke termijnen als er na de maand, die in de dagtekening van het aanslagbiljet is vermeld, nog maanden van het jaar overblijven."*

Grammaticale interpretatie: het aantal maanden dat na de dagtekening-maand nog in het jaar overblijft, is gelijk aan 12 minus het ordegetal van de dagtekening-maand. Bij dagtekening in januari (maand 1) zijn er 11 resterende maanden; bij december (maand 12) zijn er 0.

De rekenregel produceert een tussenresultaat (`resterende-maanden-jaar`) dat als invoer dient voor de beslissing of de specialisatieregel (AR-9-5a) of de terugvalregel (AR-9-5e) van toepassing is.

## Voorbeeldreeksen

| Invoerwaarden | Verwachte uitkomst | Is voorspelling juridisch juist? |
|--------------|-------------------|---------------------------------|
| maand-dagtekening: januari (1) | resterende-maanden-jaar: 11 | ja — 12 − 1 = 11; na januari resteren februari t/m december |
| maand-dagtekening: oktober (10) | resterende-maanden-jaar: 2 | ja — 12 − 10 = 2; na oktober resteren november en december |
| maand-dagtekening: november (11) | resterende-maanden-jaar: 1 | ja — grensgeval: 12 − 11 = 1; één resterende maand; de terugvalregel AR-9-5e activeert lid 1 |
| maand-dagtekening: december (12) | resterende-maanden-jaar: 0 | ja — grensgeval: 12 − 12 = 0; geen resterende maanden; de terugvalregel AR-9-5e activeert lid 1 |
