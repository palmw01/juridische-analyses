---
regel-id: AR-BWBR0004770-art9-lid1-a
naam: "bepalen invorderbaarheid belastingaanslag"
soort: Beslissingsregel
peildatum: 2026-01-01
tags:
  - afleidingsregel
  - wet/iw1990
  - art/9
annotatie-id: BWBR0004770/art9/lid1
uitvoer:
  - "[[views/begrippen/invorderbaarheid-belastingaanslag]]"
invoer:
  - "[[views/begrippen/belastingaanslag]]"
  - "[[views/begrippen/dagtekening-aanslagbiljet]]"
  - "[[views/begrippen/zes-weken-na-dagtekening-aanslagbiljet]]"
---

# bepalen invorderbaarheid belastingaanslag

*Beslissingsregel · art. 9 lid 1 · IW1990*

## Invoer en uitvoer

**Rechtsfeit:** [[views/begrippen/dagtekening-aanslagbiljet]]

**Invoer:**
- [[views/begrippen/belastingaanslag]]
- [[views/begrippen/dagtekening-aanslagbiljet]]
- [[views/begrippen/zes-weken-na-dagtekening-aanslagbiljet]]

**Uitvoer:**
- [[views/begrippen/invorderbaarheid-belastingaanslag]]

**Operators:** plus, groter-dan-of-gelijk-aan

## Formele regel

**Een belastingaanslag is invorderbaar**
indien aan alle volgende voorwaarden is voldaan:
- de belastingaanslag heeft een dagtekening van het aanslagbiljet
- het tijdstip van beoordeling is gelegen op of na het tijdstip van de dagtekening van het aanslagbiljet plus zes weken

## Toelichting

Herleidbaar tot art. 9 lid 1 IW 1990: *"Een belastingaanslag is invorderbaar zes weken na de dagtekening van het aanslagbiljet."*

De grammaticale interpretatie levert een beslissingsregel op: invorderbaarheid treedt in (ja/nee) zodra de termijn van zes weken na de dagtekening is verstreken. De datum van dagtekening is het rechtsfeit dat de termijn doet aanvangen; de termijn van zes weken (parameter) is de vaste drempel.

Precisering: art. 9 lid 10 IW 1990 sluit de Algemene termijnenwet uitdrukkelijk uit. Dit betekent dat de termijn van zes weken kalenderstrikt doorloopt, zonder verlenging bij weekenden of feestdagen.

Lid 1 is de hoofdregel. De leden 2, 4, 5, 6, 7, 8 en 9 bevatten specialisatieregels die lid 1 opzijzetten voor specifieke aanslagsoorten. Deze specialisaties vallen buiten de scope van AR-9-1.

## Voorbeeldreeksen

| Invoerwaarden | Verwachte uitkomst | Juist? | Toelichting |
|--------------|-------------------|--------|-------------|
| Belastingaanslag (aanslag IB); dagtekening aanslagbiljet: 1 januari 2026; beoordelingstijdstip: 12 februari 2026 (= 6 weken later) | invorderbaar: ja | ja |  |
| Belastingaanslag (aanslag IB); dagtekening aanslagbiljet: 1 januari 2026; beoordelingstijdstip: 11 februari 2026 (= 41 dagen, één dag te vroeg) | invorderbaar: nee | ja |  |
| Navorderingsaanslag; dagtekening aanslagbiljet: 1 januari 2026; beoordelingstijdstip: 12 februari 2026 | invorderbaar: nee (o.g.v. lid 1) | ja |  |
| Belastingaanslag (aanslag IB); dagtekening aanslagbiljet: 1 januari 2026; beoordelingstijdstip: 12 februari 2026 00:00 (= exact 6 weken) | invorderbaar: nee (na betekent na, niet op of na) | nee | Grensgeval: art. 9 lid 10 IW sluit Algemene termijnenwet uit; termijn is kalenderstrikt. "Na" betekent na verstrijken van de zesde week — niet op de laatste dag. Maar gangbare uitleg is dat de aanslag op dagtekening+6wk om 00:00 invorderbaar is (peildatum valt samen met einde termijn). |
