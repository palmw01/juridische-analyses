---
regel-id: AR-BWBR0008003-art9-par1-b
naam: "vaststellen vervaldag voorlopige aanslag afwijkend boekjaar"
soort: Specialisatieregel
peildatum: 2026-01-01
tags:
  - afleidingsregel
  - wet/iw1990
  - art/9
annotatie-id: [[annotaties/li2008/art9-9-1]]
uitvoer:
  - "[[views/begrippen/vervaldag-laatste-dag-maand]]"
invoer:
  - "[[views/begrippen/voorlopige-aanslag]]"
  - "[[views/begrippen/afwijkend-boekjaar]]"
---

# vaststellen vervaldag voorlopige aanslag afwijkend boekjaar

*Specialisatieregel · art. 9 lid par1 · IW1990*

## Invoer en uitvoer

**Rechtsfeit:** [[views/begrippen/dagtekening-aanslagbiljet]]

**Invoer:**
- [[views/begrippen/voorlopige-aanslag]]
- [[views/begrippen/afwijkend-boekjaar]]

**Uitvoer:**
- [[views/begrippen/vervaldag-laatste-dag-maand]]

**Operators:** EN

## Formele regel

In afwijking van vaststellen betalingstermijn belastingaanslag:
[[begrippen/vervaldag-laatste-dag-maand]] is laatste dag van de maand
indien aan alle volgende voorwaarden is voldaan:
- [[begrippen/voorlopige-aanslag]] is van toepassing
- [[begrippen/afwijkend-boekjaar]] is waar

## Toelichting

Voor belastingplichtigen met een afwijkend boekjaar wordt de laatste vervaldag van een voorlopige aanslag altijd gesteld op de laatste dag van de maand waarin deze valt.

## Voorbeeldreeksen

| Invoerwaarden | Verwachte uitkomst | Juist? | Toelichting |
|--------------|-------------------|--------|-------------|
| BV met boekjaar van 1 april tot 31 maart, laatste termijn valt op 15 maart | ja | nee | 15 maart |
| Natuurlijk persoon met regulier kalenderjaar | nee | nee | datum volgens art. 9 lid 5 IW 1990 |
| BV met boekjaar 1 april - 31 maart, laatste termijn valt op 28 februari | ja | nee | 28 februari |
