---
type: afleidingsregel
regel-id: AR-LI-9-1a
naam: "vaststellen vervaldag voorlopige aanslag einde kalenderjaar"
soort: Specialisatieregel
tags:
  - afleidingsregel
  - wet/li2008
  - art/9
afgeleid-van: "[[annotaties/li2008/art9-9-1]]"
peildatum: 2026-01-01
bepaalt: "[[begrippen/vervaldag-31-december]]"
invoer:
  - "[[begrippen/voorlopige-aanslag]]"
  - "[[begrippen/dagtekening-in-november-of-eerder]]"
  - "[[begrippen/termijn-eindigt-voor-31-december]]"
uitvoer:
  - "[[begrippen/vervaldag-31-december]]"
operators: [EN]
---

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

| Scenario | Deelgeval van toepassing? | Uitkomst deelgeval | Uitkomst hoofdregel |
|----------|--------------------------|-------------------|---------------------|
| Voorlopige aanslag gedagtekend in november, laatste termijn valt volgens wet op 15 december | ja | 31 december | 15 december |
| Voorlopige aanslag gedagtekend in december | nee | n.v.t. | datum volgens art. 9 lid 5 IW 1990 |
| Voorlopige aanslag gedagtekend in oktober, laatste termijn valt volgens wet op 31 december | nee | n.v.t. | 31 december (voldoet niet aan 'eindigt vóór') |
