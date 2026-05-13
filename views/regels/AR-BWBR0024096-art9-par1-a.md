---
regel-id: AR-BWBR0024096-art9-par1-a
naam: "bepalen of betalingstermijn eindigt voor 31 december"
soort: Beslissingsregel
peildatum: 2026-01-01
tags:
  - afleidingsregel
  - wet/li2008
  - art/9
  - tussenresultaat
annotatie-id: BWBR0024096/par9-1
uitvoer:
  - "[[views/begrippen/termijn-eindigt-voor-31-december]]"
invoer:
  - "[[views/begrippen/vervaldag-volgende-termijnen]]"
  - "[[views/begrippen/resterende-maanden-jaar]]"
---

# bepalen of betalingstermijn eindigt voor 31 december

*Beslissingsregel · art. 9 lid par1 · LI2008*

## Invoer en uitvoer

**Rechtsfeit:** [[views/begrippen/dagtekening-aanslagbiljet]]

**Invoer:**
- [[views/begrippen/vervaldag-volgende-termijnen]]
- [[views/begrippen/resterende-maanden-jaar]]

**Uitvoer:**
- [[views/begrippen/termijn-eindigt-voor-31-december]]

**Operators:** kleiner-dan

## Formele regel

**termijn-eindigt-voor-31-december is waar**
indien aan alle volgende voorwaarden is voldaan:
- het aantal resterende-maanden-jaar bedraagt ten minste 2 (lid 5 is van toepassing)
- de vervaldag van de laatste betalingstermijn, berekend conform AR-9-5c, valt vóór 31 december van het belastingjaar

## Toelichting

Herleidbaar tot LI 2008 §9.1 (uitvoeringsbeleid bij art. 9 lid 5 IW 1990).

De Leidraad Invordering 2008 geeft uitvoering aan de wettelijke termijnenregeling van art. 9 lid 5 door een aanvullende grensregel te stellen: indien de berekende vervaldagen leiden tot een laatste termijn die eindigt vóór 31 december, wordt de vervaldatum van die termijn verschoven naar 31 december. Dit voorkomt dat de belastingschuldige bij een late dagtekening in het belastingjaar effectief minder betalingstijd krijgt dan de wettelijke regeling beoogt.

Dit begrip is een tussenresultaat: het wordt uitsluitend berekend als invoer voor de beperkingsregel AR-9-5e (vervaldag-31-december). De regel is gebaseerd op uitvoeringsbeleid, niet op een expliciete wetsbepaling; volledige juridische onderbouwing vereist annotatie van LI 2008 §9 in zijn geheel.

**A5-signaal:** de wettekst van art. 9 lid 5 IW 1990 zwijgt over de 31 december-cap; deze volgt uitsluitend uit de Leidraad. Bij conflict tussen wet en Leidraad prevaleert de wet.

## Voorbeeldreeksen

| Invoerwaarden | Verwachte uitkomst | Juist? | Toelichting |
|--------------|-------------------|--------|-------------|
| dagtekening: 1 april 2026; resterende maanden: 8; laatste vervaldag berekend: 1 december 2026 | termijn-eindigt-voor-31-december: ja | ja | 1 december valt vóór 31 december — cap is van toepassing |
| dagtekening: 1 februari 2026; resterende maanden: 10; laatste vervaldag berekend: 1 december 2026 | termijn-eindigt-voor-31-december: ja | ja | grensgeval — ook hier eindigt de reeks voor 31 december |
| dagtekening: 1 januari 2026; resterende maanden: 11; laatste vervaldag berekend: 1 december 2026 | termijn-eindigt-voor-31-december: ja | ja |  |
| dagtekening: 1 maart 2026; resterende maanden: 9; laatste vervaldag berekend: 1 december 2026 | termijn-eindigt-voor-31-december: nee (dec = 31 dec) | nee | Grensgeval: "eindigt voor 31 december" — 1 december eindigt vóór 31 december, dus de cap is van toepassing. Alleen als de laatste vervaldag exact 31 december is, eindigt deze niet "voor" 31 december en treedt de cap niet in werking. |
