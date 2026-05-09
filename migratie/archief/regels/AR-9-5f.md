---
type: afleidingsregel
regel-id: AR-9-5f
naam: "berekenen termijnbedrag voorlopige aanslag"
soort: Rekenregel
tags:
  - afleidingsregel
  - wet/iw1990
  - art/9
afgeleid-van: "[[annotaties/iw1990/art9-5]]"
peildatum: 2026-01-01
bepaalt: "[[begrippen/termijnbedrag]]"
rechtsfeit: "[[begrippen/dagtekening-aanslagbiljet]]"
invoer:
  - "[[begrippen/totaalbedrag-belastingaanslag]]"
  - "[[begrippen/resterende-maanden-jaar]]"
uitvoer:
  - "[[begrippen/termijnbedrag]]"
operators:
  - "gedeeld-door"
---

## Formele regel

**termijnbedrag moet berekend worden als**
totaalbedrag-belastingaanslag gedeeld door resterende-maanden-jaar

## Toelichting

Herleidbaar tot art. 9 lid 5 IW 1990, eerste volzin: *"in zoveel **gelijke** termijnen als er na de maand..."*

Systematische interpretatie: De wettelijke eis dat termijnen "gelijke" zijn, noodzaakt tot een rekenkundige operatie waarbij het totaalbedrag van de aanslag evenredig wordt verdeeld over het aantal beschikbare termijnen. 

**A5-signaal (ontbrekend uitvoeringsbeleid):** De wettekst zwijgt over de behandeling van afrondingsverschillen indien het totaalbedrag niet exact deelbaar is door het aantal termijnen. In de ICT-implementatie moet hier aanvullend beleid voor worden vastgesteld (bijv. het restant verrekenen in de eerste of laatste termijn) om te borgen dat het totaal van de termijnbedragen exact gelijk is aan het totaalbedrag-belastingaanslag.

## Voorbeeldreeksen

| Invoerwaarden | Verwachte uitkomst | Is voorspelling juridisch juist? |
|--------------|-------------------|---------------------------------|
| totaalbedrag: € 1.200; resterende maanden: 8 (dagtekening april) | termijnbedrag: € 150 | ja — 1200 / 8 = 150. Exacte verdeling mogelijk. |
| totaalbedrag: € 1.000; resterende maanden: 11 (dagtekening januari) | termijnbedrag: € 90,90 (met restant € 0,10) | ja — 1000 / 11 ≈ 90,909...; 'gelijke' termijnen vereisen een afrondingsregel in de uitvoering. |
| totaalbedrag: € 500; resterende maanden: 2 (dagtekening oktober) | termijnbedrag: € 250 | ja — 500 / 2 = 250. Twee gelijke termijnen in november en december. |
