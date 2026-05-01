---
type: afleidingsregel
regel-id: AR-LI-9-1b
naam: "vaststellen vervaldag voorlopige aanslag afwijkend boekjaar"
soort: Specialisatieregel
tags:
  - afleidingsregel
  - wet/li2008
  - art/9
afgeleid-van: "[[annotaties/li2008/art9-9-1]]"
peildatum: 2026-01-01
bepaalt: "[[begrippen/vervaldag-laatste-dag-maand]]"
invoer:
  - "[[begrippen/voorlopige-aanslag]]"
  - "[[begrippen/afwijkend-boekjaar]]"
uitvoer:
  - "[[begrippen/vervaldag-laatste-dag-maand]]"
operators: [EN]
---

## Formele regel

In afwijking van vaststellen betalingstermijn belastingaanslag:
[[begrippen/vervaldag-laatste-dag-maand]] is laatste dag van de maand
indien aan alle volgende voorwaarden is voldaan:
- [[begrippen/voorlopige-aanslag]] is van toepassing
- [[begrippen/afwijkend-boekjaar]] is waar

## Toelichting

Voor belastingplichtigen met een afwijkend boekjaar wordt de laatste vervaldag van een voorlopige aanslag altijd gesteld op de laatste dag van de maand waarin deze valt.

## Voorbeeldreeksen

| Scenario | Deelgeval van toepassing? | Uitkomst deelgeval | Uitkomst hoofdregel |
|----------|--------------------------|-------------------|---------------------|
| BV met boekjaar van 1 april tot 31 maart, laatste termijn valt op 15 maart | ja | 31 maart | 15 maart |
| Natuurlijk persoon met regulier kalenderjaar | nee | n.v.t. | datum volgens art. 9 lid 5 IW 1990 |
| BV met boekjaar 1 april - 31 maart, laatste termijn valt op 28 februari | ja | 28 (of 29) februari | 28 februari |
