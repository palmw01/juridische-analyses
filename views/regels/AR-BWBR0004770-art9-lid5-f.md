---
regel-id: AR-BWBR0004770-art9-lid5-f
naam: "berekenen termijnbedrag voorlopige aanslag"
soort: Rekenregel
peildatum: 2026-01-01
tags:
  - afleidingsregel
  - wet/iw1990
  - art/9
annotatie-id: BWBR0004770/art9/lid5
uitvoer:
  - "[[views/begrippen/termijnbedrag]]"
invoer:
  - "[[views/begrippen/totaalbedrag-belastingaanslag]]"
  - "[[views/begrippen/resterende-maanden-jaar]]"
---

# berekenen termijnbedrag voorlopige aanslag

*Rekenregel · art. 9 lid 5 · IW1990*

## Invoer en uitvoer

**Rechtsfeit:** [[views/begrippen/dagtekening-aanslagbiljet]]

**Invoer:**
- [[views/begrippen/totaalbedrag-belastingaanslag]]
- [[views/begrippen/resterende-maanden-jaar]]

**Uitvoer:**
- [[views/begrippen/termijnbedrag]]

**Operators:** gedeeld-door

## Formele regel

**termijnbedrag moet berekend worden als**
totaalbedrag-belastingaanslag gedeeld door resterende-maanden-jaar

## Toelichting

Herleidbaar tot art. 9 lid 5 IW 1990, eerste volzin: *"in zoveel **gelijke** termijnen als er na de maand..."*

Systematische interpretatie: De wettelijke eis dat termijnen "gelijke" zijn, noodzaakt tot een rekenkundige operatie waarbij het totaalbedrag van de aanslag evenredig wordt verdeeld over het aantal beschikbare termijnen. 

**A5-signaal (ontbrekend uitvoeringsbeleid):** De wettekst zwijgt over de behandeling van afrondingsverschillen indien het totaalbedrag niet exact deelbaar is door het aantal termijnen. In de ICT-implementatie moet hier aanvullend beleid voor worden vastgesteld (bijv. het restant verrekenen in de eerste of laatste termijn) om te borgen dat het totaal van de termijnbedragen exact gelijk is aan het totaalbedrag-belastingaanslag.

## Voorbeeldreeksen

| Invoerwaarden | Verwachte uitkomst | Juist? | Toelichting |
|--------------|-------------------|--------|-------------|
| totaalbedrag: € 1.200; resterende maanden: 8 (dagtekening april) | termijnbedrag: € 150 | ja |  |
| totaalbedrag: € 1.000; resterende maanden: 11 (dagtekening januari) | termijnbedrag: € 90,90 (met restant € 0,10) | ja |  |
| totaalbedrag: € 500; resterende maanden: 2 (dagtekening oktober) | termijnbedrag: € 250 | ja |  |
| totaalbedrag: € 100; resterende maanden: 3 (dagtekening september) | termijnbedrag: € 33,33 (zonder restant) | nee | Grensgeval: € 100 / 3 = € 33,333… Afronding noodzaakt restant-verrekening. De wettekst zwijgt over afronding (A5-signaal). Zonder restant-verrekening sommen de termijnen niet op tot € 100. |
