---
type: afleidingsregel
regel-id: AR-9-5a
naam: "bepalen invorderbaarheid voorlopige aanslag in gelijke termijnen"
soort: Specialisatieregel
tags:
  - afleidingsregel
  - wet/iw1990
  - art/9
afgeleid-van: "[[annotaties/iw1990/art9-5]]"
peildatum: 2026-01-01
bepaalt: "[[begrippen/invorderbaarheid-in-gelijke-termijnen]]"
rechtsfeit: "[[begrippen/dagtekening-aanslagbiljet]]"
invoer:
  - "[[begrippen/voorlopige-aanslag]]"
  - "[[begrippen/voorlopige-conserverende-aanslag-ib]]"
  - "[[begrippen/dagtekening-in-vaststellingsjaar]]"
  - "[[begrippen/termijnenberekening-resterende-maanden]]"
uitvoer:
  - "[[begrippen/invorderbaarheid-in-gelijke-termijnen]]"
operators:
  - "EN"
  - "OF"
  - "groter-dan"
---

## Formele regel

**In afwijking van bepalen invorderbaarheid belastingaanslag:**
invorderbaarheid-in-gelijke-termijnen is van toepassing
indien aan alle volgende voorwaarden is voldaan:
- het aanslagtype is een voorlopige aanslag IB of VPB, of een voorlopige conserverende aanslag IB
- het aanslagbiljet heeft een dagtekening in het jaar waarover de aanslag is vastgesteld
- de termijnenberekening-resterende-maanden leidt tot meer dan één termijn

## Toelichting

Herleidbaar tot art. 9 lid 5 IW 1990, eerste volzin: *"In afwijking van het eerste lid is een voorlopige aanslag in de inkomstenbelasting of in de vennootschapsbelasting en een voorlopige conserverende aanslag in de inkomstenbelasting, waarvan het aanslagbiljet een dagtekening heeft die ligt in het jaar waarover deze is vastgesteld, invorderbaar in zoveel gelijke termijnen als er na de maand, die in de dagtekening van het aanslagbiljet is vermeld, nog maanden van het jaar overblijven."*

Systematische interpretatie: lid 5 is lex specialis ten opzichte van de hoofdregel van lid 1 (AR-9-1). De specialisatieregel is van toepassing als aan twee cumulatieve kwalificatievoorwaarden is voldaan: (1) het juiste aanslagtype; (2) dagtekening in het belastingjaar. Het uitvoerbegrip is het aantal gelijke termijnen, berekend door AR-9-5b.

De derde volzin van lid 5 bevat een terugvalregel (AR-9-5e): als de berekening niet leidt tot meer dan één termijn, herneemt lid 1. Deze terugvalregel is een derde conditie die impliciet onderdeel uitmaakt van de specialisatieregel: de specialisatie geldt alleen bij meer dan één termijn.

## Voorbeeldreeksen

| Invoerwaarden | Verwachte uitkomst | Is voorspelling juridisch juist? |
|--------------|-------------------|---------------------------------|
| Aanslagtype: voorlopige aanslag IB 2026; dagtekening: 15 april 2026 (in belastingjaar); termijnen: 8 (> 1) | invorderbaarheid-in-gelijke-termijnen: 8 termijnen | ja — aan alle kwalificatievoorwaarden is voldaan; specialisatieregel is van toepassing |
| Aanslagtype: voorlopige aanslag VPB 2026; dagtekening: 1 februari 2026; termijnen: 10 (> 1) | invorderbaarheid-in-gelijke-termijnen: 10 termijnen | ja — voorlopige VPB-aanslag in het belastingjaar; 10 resterende maanden |
| Aanslagtype: voorlopige aanslag IB 2026; dagtekening: 15 december 2026; termijnen: 0 (≤ 1) | invorderbaarheid-in-gelijke-termijnen: n.v.t.; lid 1 herneemt | ja — grensgeval: de terugvalregel activeert lid 1; invorderbaarheid zes weken na dagtekening |
| Aanslagtype: definitieve aanslag IB 2026; dagtekening: 15 april 2026 | invorderbaarheid-in-gelijke-termijnen: n.v.t. | ja — randgeval: een definitieve aanslag voldoet niet aan het aanslagtype-criterium; lid 1 is van toepassing |
