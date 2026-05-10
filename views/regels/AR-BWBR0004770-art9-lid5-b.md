---
regel-id: AR-BWBR0004770-art9-lid5-b
naam: "berekenen resterende maanden jaar"
soort: Rekenregel
peildatum: 2026-01-01
tags:
  - afleidingsregel
  - wet/iw1990
  - art/9
annotatie-id: [[annotaties/iw1990/art9-5]]
uitvoer:
  - "[[views/begrippen/resterende-maanden-jaar]]"
invoer:
  - "[[views/begrippen/maand-dagtekening-aanslagbiljet]]"
---

# berekenen resterende maanden jaar

*Rekenregel · art. 9 lid 5 · IW1990*

## Invoer en uitvoer

**Rechtsfeit:** [[views/begrippen/dagtekening-aanslagbiljet]]

**Invoer:**
- [[views/begrippen/maand-dagtekening-aanslagbiljet]]

**Uitvoer:**
- [[views/begrippen/resterende-maanden-jaar]]

**Operators:** min

## Formele regel

**resterende-maanden-jaar moet berekend worden als**
12 min maand-dagtekening-aanslagbiljet

*(waarbij de maand wordt uitgedrukt als ordegetal: januari = 1, februari = 2, …, december = 12)*

## Toelichting

Herleidbaar tot art. 9 lid 5 IW 1990, eerste volzin: *"in zoveel gelijke termijnen als er na de maand, die in de dagtekening van het aanslagbiljet is vermeld, nog maanden van het jaar overblijven."*

Grammaticale interpretatie: het aantal maanden dat na de dagtekening-maand nog in het jaar overblijft, is gelijk aan 12 minus het ordegetal van de dagtekening-maand. Bij dagtekening in januari (maand 1) zijn er 11 resterende maanden; bij december (maand 12) zijn er 0.

De rekenregel produceert een tussenresultaat (`resterende-maanden-jaar`) dat als invoer dient voor de beslissing of de specialisatieregel (AR-9-5a) of de terugvalregel (AR-9-5e) van toepassing is.

## Voorbeeldreeksen

| Invoerwaarden | Verwachte uitkomst | Juist? | Toelichting |
|--------------|-------------------|--------|-------------|
| maand-dagtekening: januari (1) | resterende-maanden-jaar: 11 | ja |  |
| maand-dagtekening: oktober (10) | resterende-maanden-jaar: 2 | ja |  |
| maand-dagtekening: november (11) | resterende-maanden-jaar: 1 | ja |  |
| maand-dagtekening: december (12) | resterende-maanden-jaar: 0 | ja |  |
