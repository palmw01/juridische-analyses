---
type: begrip
begripsnaam: invorderbaarheid-in-gelijke-termijnen
jas-klasse: afleidingsregel
tags:
  - begrip
  - jas/afleidingsregel
  - wet/iw1990
  - art/9
markering: "In afwijking van het eerste lid is een voorlopige aanslag in de inkomstenbelasting of in de vennootschapsbelasting en een voorlopige conserverende aanslag in de inkomstenbelasting, waarvan het aanslagbiljet een dagtekening heeft die ligt in het jaar waarover deze is vastgesteld, invorderbaar in zoveel gelijke termijnen als er na de maand, die in de dagtekening van het aanslagbiljet is vermeld, nog maanden van het jaar overblijven."
bron: "Art. 9 lid 5 IW 1990"
bronnen:
  - "Art. 9 lid 5 IW 1990"
peildatum: 2026-01-01
interpretatiemethode: systematisch
toelichting-klasse: "Specialisatieregel t.o.v. art. 9 lid 1. Als-dan: als de voorlopige aanslag (IB/VPB) of voorlopige conserverende aanslag (IB) is gedagtekend in het belastingjaar, dan is hij invorderbaar in gelijke maandelijkse termijnen. Bevat twee cumulatieve kwalificatievoorwaarden en de rekenregel voor het termijnenaantal."
definitie: "De specialisatieregel die bepaalt dat een voorlopige aanslag IB of VPB, dan wel een voorlopige conserverende aanslag IB, waarvan het aanslagbiljet is gedagtekend in het belastingjaar, invorderbaar is in een aantal gelijke maandelijkse termijnen dat gelijk is aan het aantal kalendermaanden dat na de dagtekening maand nog in dat jaar resteert"
soort: "getal"
herkomst: "afgeleid"
aliases: []
is-een:
  - "[[begrippen/invorderbaarheid]]"
heeft:
  - "[[begrippen/voorlopige-aanslag]]"
  - "[[begrippen/voorlopige-conserverende-aanslag-ib]]"
  - "[[begrippen/dagtekening-in-vaststellingsjaar]]"
  - "[[begrippen/termijnenberekening-resterende-maanden]]"
leidt-tot:
  - "[[begrippen/vervaldag-eerste-termijn]]"
  - "[[begrippen/vervaldag-volgende-termijnen]]"
afleidingsregels:
  - "[[regels/AR-9-5a]]"
geldigheid-van: 2026-01-01
geldigheid-tot: ""
status: concept
---

## Definitie

*"In afwijking van het eerste lid is een voorlopige aanslag in de inkomstenbelasting of in de vennootschapsbelasting en een voorlopige conserverende aanslag in de inkomstenbelasting, waarvan het aanslagbiljet een dagtekening heeft die ligt in het jaar waarover deze is vastgesteld, invorderbaar in zoveel gelijke termijnen als er na de maand, die in de dagtekening van het aanslagbiljet is vermeld, nog maanden van het jaar overblijven."* *(Art. 9 lid 5 IW 1990, peildatum 2026-01-01)*

De specialisatieregel die bepaalt dat een voorlopige aanslag IB of VPB, dan wel een voorlopige conserverende aanslag IB, waarvan het aanslagbiljet is gedagtekend in het belastingjaar, invorderbaar is in een aantal gelijke maandelijkse termijnen dat gelijk is aan het aantal kalendermaanden dat na de dagtekening maand nog in dat jaar resteert

## Voorbeelden

| Stelling | Waar? | Toelichting |
|----------|-------|-------------|
| Een voorlopige aanslag IB 2026 gedagtekend 15 april 2026 is invorderbaar in 8 gelijke termijnen op grond van lid 5. | ja | Na april resteren in 2026 acht maanden (mei t/m december); de specialisatieregel van lid 5 is van toepassing; het termijnenaantal is acht. |
| Een voorlopige aanslag IB 2026 gedagtekend 15 december 2026 is invorderbaar in 1 termijn op grond van lid 5. | nee | Grensgeval: na december resteren nul maanden; de derde volzin van lid 5 activeert lid 1 (terugvalregel); de aanslag is dan invorderbaar zes weken na dagtekening op grond van lid 1. |
| Een voorlopige aanslag VPB 2025 gedagtekend 15 februari 2025 is invorderbaar in 10 gelijke termijnen. | ja | Na februari resteren tien maanden; de aanslag voldoet aan de kwalificatievoorwaarden (VPB, dagtekening in belastingjaar); 10 termijnen. |

## Kenmerken

- De specialisatieregel verdringt de hoofdregel van art. 9 lid 1 voor de specifieke aanslagtypen (lex specialis); bij ≤ 1 termijn herneemt lid 1 via de terugvalregel.
- Twee cumulatieve kwalificatievoorwaarden: (1) het juiste aanslagtype (voorlopige aanslag IB/VPB of voorlopige conserverende aanslag IB); (2) dagtekening in het belastingjaar.
- Het termijnenaantal is een berekende waarde; de vervaldatums worden bepaald door `vervaldag-eerste-termijn` en `vervaldag-volgende-termijnen`.

## Relaties

| Type | Kardinaliteit | Begrip |
|------|---------------|--------|
| is een | — | [[begrippen/invorderbaarheid]] |
| heeft | 1:n | [[begrippen/voorlopige-aanslag]] |
| heeft | 1:n | [[begrippen/voorlopige-conserverende-aanslag-ib]] |
| heeft | 1:1 | [[begrippen/dagtekening-in-vaststellingsjaar]] |
| heeft | 1:1 | [[begrippen/termijnenberekening-resterende-maanden]] |
| leidt tot | — | [[begrippen/vervaldag-eerste-termijn]] |
| leidt tot | — | [[begrippen/vervaldag-volgende-termijnen]] |
