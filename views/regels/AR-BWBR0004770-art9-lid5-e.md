---
regel-id: AR-BWBR0004770-art9-lid5-e
naam: "bepalen terugval naar lid 1 bij onvoldoende termijnen"
soort: Beslissingsregel
peildatum: 2026-01-01
tags:
  - afleidingsregel
  - wet/iw1990
  - art/9
annotatie-id: BWBR0004770/art9/lid5
uitvoer:
  - "[[views/begrippen/terugvalregel-lid-1]]"
  - "[[views/begrippen/invorderbaarheid-belastingaanslag]]"
invoer:
  - "[[views/begrippen/resterende-maanden-jaar]]"
  - "[[views/begrippen/termijnenberekening-resterende-maanden]]"
---

# bepalen terugval naar lid 1 bij onvoldoende termijnen

*Beslissingsregel · art. 9 lid 5 · IW1990*

## Invoer en uitvoer

**Rechtsfeit:** [[views/begrippen/dagtekening-aanslagbiljet]]

**Invoer:**
- [[views/begrippen/resterende-maanden-jaar]]
- [[views/begrippen/termijnenberekening-resterende-maanden]]

**Uitvoer:**
- [[views/begrippen/terugvalregel-lid-1]]
- [[views/begrippen/invorderbaarheid-belastingaanslag]]

**Operators:** ten-hoogste, NIET

## Formele regel

**lid 1 (bepalen invorderbaarheid belastingaanslag) is van toepassing**
indien aan alle volgende voorwaarden is voldaan:
- het aanslagtype voldoet aan de kwalificatievoorwaarden van lid 5 (voorlopige aanslag IB/VPB of voorlopige conserverende aanslag IB)
- de dagtekening-in-vaststellingsjaar is vervuld
- de resterende-maanden-jaar bedraagt ten hoogste 1

## Toelichting

Herleidbaar tot art. 9 lid 5 IW 1990, derde volzin: *"Indien de toepassing van de eerste volzin niet leidt tot meer dan één termijn, vindt het eerste lid toepassing."*

Systematische interpretatie: de terugvalregel is een beslissingsregel die bepaalt wanneer de specialisatieregel van lid 5 eerste volzin zijn werking verliest en de hoofdregel van lid 1 herneemt. De conditie 'niet leidt tot meer dan één termijn' is vervuld als `resterende-maanden-jaar` ≤ 1. Dit is het geval bij een dagtekening in november (1 resterende maand) of december (0 resterende maanden).

De terugvalregel veronderstelt dat aan de kwalificatievoorwaarden van de eerste en tweede conditie van AR-9-5a al is voldaan (juist aanslagtype én dagtekening in belastingjaar); alleen dan is de vraag naar de drempelwaarde relevant.

## Voorbeeldreeksen

| Invoerwaarden | Verwachte uitkomst | Juist? | Toelichting |
|--------------|-------------------|--------|-------------|
| aanslagtype: voorlopige IB; dagtekening: 15 november 2026; resterende-maanden-jaar: 1 | lid 1 van toepassing: ja; invorderbaarheid zes weken na dagtekening | ja |  |
| aanslagtype: voorlopige IB; dagtekening: 15 december 2026; resterende-maanden-jaar: 0 | lid 1 van toepassing: ja; invorderbaarheid zes weken na dagtekening | ja |  |
| aanslagtype: voorlopige IB; dagtekening: 15 oktober 2026; resterende-maanden-jaar: 2 | lid 1 van toepassing: nee; lid 5 specialisatieregel geldt | ja |  |
| aanslagtype: voorlopige IB; dagtekening: 15 november 2026; resterende-maanden-jaar: 1 | lid 5 van toepassing: 1 resterende maand = 1 termijn | nee | Grensgeval: "niet leidt tot meer dan één termijn" — 1 resterende maand leidt tot 1 termijn (de eerste), dus de terugval naar lid 1 is van toepassing, niet lid 5. |
