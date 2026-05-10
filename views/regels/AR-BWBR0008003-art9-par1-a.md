---
regel-id: AR-BWBR0008003-art9-par1-a
naam: "vaststellen vervaldag voorlopige aanslag einde kalenderjaar"
soort: Specialisatieregel
peildatum: 2026-01-01
tags:
  - afleidingsregel
  - wet/iw1990
  - art/9
annotatie-id: [[annotaties/li2008/art9-9-1]]
uitvoer:
  - "[[views/begrippen/vervaldag-31-december]]"
invoer:
  - "[[views/begrippen/voorlopige-aanslag]]"
  - "[[views/begrippen/dagtekening-in-november-of-eerder]]"
  - "[[views/begrippen/termijn-eindigt-voor-31-december]]"
---

# vaststellen vervaldag voorlopige aanslag einde kalenderjaar

*Specialisatieregel · art. 9 lid par1 · IW1990*

## Invoer en uitvoer

**Rechtsfeit:** [[views/begrippen/dagtekening-aanslagbiljet]]

**Invoer:**
- [[views/begrippen/voorlopige-aanslag]]
- [[views/begrippen/dagtekening-in-november-of-eerder]]
- [[views/begrippen/termijn-eindigt-voor-31-december]]

**Uitvoer:**
- [[views/begrippen/vervaldag-31-december]]

**Operators:** EN

## Formele regel

In afwijking van vaststellen betalingstermijn belastingaanslag:
[[begrippen/vervaldag-31-december]] is [[begrippen/31-december]]
indien aan alle volgende voorwaarden is voldaan:
- [[begrippen/voorlopige-aanslag]] is van toepassing
- [[begrippen/dagtekening-in-november-of-eerder]] is waar
- [[begrippen/termijn-eindigt-voor-31-december]] is waar

## Toelichting

Deze regel specificeert dat voor voorlopige aanslagen die gedagtekend zijn in november of eerder, de vervaldag van de laatste termijn naar 31 december wordt verschoven als deze anders eerder zou vallen. Dit is een begunstigende afwijking van de wettelijke termijnregels in art. 9 lid 5 IW 1990.

## Voorbeeldreeksen

| Invoerwaarden | Verwachte uitkomst | Juist? | Toelichting |
|--------------|-------------------|--------|-------------|
| Voorlopige aanslag gedagtekend in november, laatste termijn valt volgens wet op 15 december | ja | nee | 15 december |
| Voorlopige aanslag gedagtekend in december | nee | nee | datum volgens art. 9 lid 5 IW 1990 |
| Voorlopige aanslag gedagtekend in oktober, laatste termijn valt volgens wet op 31 december | nee | nee | 31 december (voldoet niet aan 'eindigt vóór') |
