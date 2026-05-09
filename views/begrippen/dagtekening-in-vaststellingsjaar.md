---
type: begrip
begrip-id: dagtekening-in-vaststellingsjaar
begripsnaam: dagtekening-in-vaststellingsjaar
jas-klasse: voorwaarde
soort: waar-niet-waar
herkomst: afgeleid
status: concept
geldigheid-van: 2026-01-01
tags:
  - begrip
  - jas/voorwaarde
  - wet/iw1990
  - art/9
afleidingsregels:
  - "[[views/regels/AR-9-5a]]"
---

## Definitie

*"waarvan het aanslagbiljet een dagtekening heeft die ligt in het jaar waarover deze is vastgesteld"*
*(Art. 9 lid 5 IW 1990, peildatum 2026-01-01)*

De toepassingsvoorwaarde dat de dagtekening van het aanslagbiljet valt binnen het kalenderjaar waarover de voorlopige aanslag of de voorlopige conserverende aanslag is vastgesteld, als afbakeningscriterium voor de termijnenregeling van art. 9 lid 5 IW 1990

## Markeringen

| ID | Bron | Tekst | Bijdrage | Bevestigd |
|----|------|-------|---------|-----------|
| m-001 | Art. 9 lid 5 IW 1990 | waarvan het aanslagbiljet een dagtekening heeft die ligt in het jaar waarover deze is vastgesteld | primair | — |

## Voorbeelden

| Stelling | Waar? | Toelichting |
|----------|-------|-------------|
| Een voorlopige aanslag IB 2026 gedagtekend op 15 juni 2026. De voorwaarde 'dagtekening in vaststellingsjaar' is vervuld. | ja | De dagtekening (15 juni 2026) valt in het belastingjaar waarover de aanslag is vastgesteld (2026); lid 5 is van toepassing. |
| Een voorlopige aanslag IB 2026 gedagtekend op 1 februari 2027. De voorwaarde is vervuld. | nee | De dagtekening (1 februari 2027) valt buiten het belastingjaar 2026; de voorwaarde is niet vervuld en lid 5 is niet van toepassing. Lid 7 regelt aanslagen met een dagtekening vóór het belastingjaar; voor dagtekening ná het jaar is lid 1 van toepassing. |
| Een voorlopige aanslag IB 2026 gedagtekend op 31 december 2026 valt onder lid 5, ook al resteren er na december geen maanden meer. | ja (grensgeval) | De dagtekening valt in 2026; de voorwaarde is vervuld. De derde volzin van lid 5 regelt vervolgens dat lid 1 herneemt als het termijnenaantal ≤ 1 is. |

## Kenmerken

- De voorwaarde is temporeel van aard: zij toetst uitsluitend of het kalenderjaar van de dagtekening overeenkomt met het belastingjaar.
- Aanslagen met dagtekening vóór het belastingjaar worden door lid 7 geregeld; dagtekening ná het belastingjaar valt onder de hoofdregel van lid 1.
- De voorwaarde is een van de twee cumulatieve condities voor toepassing van lid 5 (de andere is het aanslagtype via `voorlopige-aanslag` of `voorlopige-conserverende-aanslag-ib`).

## Relaties

| Type | Kardinaliteit | Begrip |
|------|---------------|--------|
| heeft | 1:1 | [[begrippen/dagtekening-aanslagbiljet]] |
| leidt tot | — | [[begrippen/invorderbaarheid-in-gelijke-termijnen]] |
