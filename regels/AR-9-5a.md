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

| Scenario | Deelgeval van toepassing? | Uitkomst deelgeval | Uitkomst hoofdregel (art. 9 lid 1) |
|----------|--------------------------|-------------------|-------------------------------------|
| Voorlopige aanslag IB 2026; dagtekening 15 april 2026; 8 resterende maanden | ja — aanslagtype correct, dagtekening in belastingjaar, termijnen > 1 | invorderbaar in 8 gelijke maandelijkse termijnen | n.v.t. |
| Voorlopige aanslag VPB 2026; dagtekening 1 februari 2026; 10 resterende maanden | ja — VPB valt ook onder de specialisatieregel; aan alle voorwaarden voldaan | invorderbaar in 10 gelijke maandelijkse termijnen | n.v.t. |
| Voorlopige aanslag IB 2026; dagtekening 15 december 2026; 0 resterende maanden *(grensgeval)* | nee — terugvalregel art. 9 lid 5 derde volzin: termijnenberekening leidt tot ≤ 1 termijn | n.v.t. | invorderbaar zes weken na dagtekening aanslagbiljet |
| Definitieve aanslag IB 2026; dagtekening 15 april 2026 *(randgeval)* | nee — aanslagtype voldoet niet; definitieve aanslag valt niet onder lid 5 | n.v.t. | invorderbaar zes weken na dagtekening aanslagbiljet |
