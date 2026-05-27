# Validatie

De validatielaag bewaakt dat de analysebestanden structureel kloppen, onderling naar bestaande objecten verwijzen en voldoende kwaliteitssignalen bevatten voor review.

Het actuele rapport staat in [`rapporten/validatie-rapport.md`](../rapporten/validatie-rapport.md).

## Overzicht

| Laag | Controle | Blokkerend |
|---|---|---|
| L1 | Schema-conformiteit | Ja |
| L2 | Integriteitscontrole | Ja |
| L3 | Kwaliteitswaarschuwingen | Nee |

## L1 - Schema-conformiteit

L1 valideert JSON- en YAML-bestanden tegen JSON Schema draft-07.

| Schema | Valideert |
|---|---|
| `schemas/bron.schema.json` | Wetsteksten in `bronnen/` |
| `schemas/annotatie-index.schema.json` | Artikelindices in `annotaties/` |
| `schemas/annotatie-lid.schema.json` | Lidannotaties in `annotaties/` |
| `schemas/begrip.schema.json` | Begrippen in `begrippen/` |
| `schemas/regel.schema.json` | Regels in `regels/` |
| `schemas/voorbeeldreeks.schema.json` | Voorbeeldreeksen in `validaties/` |
| `schemas/scenario.schema.json` | Juridische scenario's |

L1-fouten zijn blokkerend. Voorbeelden zijn ontbrekende verplichte velden, foutieve datatypes of waarden buiten een toegestane enumeratie.

## L2 - Integriteitscontrole

L2 controleert of bestanden samen een consistent model vormen. Deze fouten zijn ook blokkerend.

Belangrijke controles:

| Controle | Voorbeeld |
|---|---|
| Referentiële integriteit | `begrip-id`, `markering-id` of `afleidingsregel-id` verwijst naar bestaand object |
| Statusconsistentie | `status: gevalideerd` vereist een ingevulde definitie |
| Diagramintegriteit | Diagramkanten verwijzen naar bestaande diagramknopen |
| Voorbeeldreeksintegriteit | Invoer- en uitvoerbegrippen bestaan in `begrippen/` |
| Specialisatieregels | `gespecialiseerd-regel-id` is verplicht en bestaand |
| Vervangingsrelaties | `vervangt-regel-id` of `vervangen-door` verwijst correct |

## L3 - Kwaliteitswaarschuwingen

L3-signalen zijn niet blokkerend. Ze maken zichtbaar waar juridische review, modellering of opschoning nog aandacht kan vragen.

Typische waarschuwingen:

| Waarschuwing | Betekenis |
|---|---|
| `alle relaties leeg` | Mogelijk geïsoleerd begrip of ontbrekende modellering |
| `geen grensgevallen` | Afleidingsregel mist negatieve of grensgevallen |
| `definitie.kern leeg` | Begrip is nog een stub |
| `alle markeringen onbevestigd` | Domeinexpertvalidatie is nog niet verwerkt |
| `aanvullende markering zonder context` | Contextuele bijdrage mist toelichting in `definitie.contexten` |
| `is-voorspelling-juist=?` | Voorbeeldreeks wacht op juridisch oordeel |
| `scenario-specifieke begripsnaam` | Naam lijkt gebaseerd op concreet voorbeeld in plaats van juridische rol |

De huidige PoC heeft geen L1- of L2-fouten. De resterende L3-waarschuwingen zijn review-signalen en deels bewust geaccepteerde modellering.

## Pipeline

```text
git commit
  -> pre-commit hook
    -> validate_note.py
      -> L1/L2 blokkeert commit
      -> L3 toont waarschuwingen

git push
  -> GitHub Actions
    -> make ci
      -> tests
      -> validatie
      -> RDF-export
      -> graph-export
      -> enrichment-check
```

Lokale commando's:

```bash
make validate
make test
make test-cov
make ci
```
