# Menselijke validatie en disciplines

> **Bron:** Handleiding Wetsanalyse §1 (multidisciplinair samenwerken, `handleiding.pages.md` r. 500-516; "mensenwerk" r. 2771) en Leidraad §2 (disciplinetabel + maatwerk team, `leidraad.pages.md` r. 117-140). Gebruikt door **alle** skills.

---

## Uitgangspunt — AI is een hulpmiddel

Wetsanalyse is en blijft **mensenwerk** (Handleiding r. 2771). De skills ondersteunen het *maken, controleren en verbeteren* van analyseproducten, maar vervangen **niet**:

1. de **menselijke juridische verantwoordelijkheid** voor het eindoordeel, en
2. de **multidisciplinaire validatie** door het team.

> "Een essentieel aspect van Wetsanalyse is multidisciplinair samenwerken … Wetsanalyse levert de beste resultaten op als ze wordt uitgevoerd in een team van juristen, uitvoeringsdeskundigen, kennismodelleurs en softwareontwikkelaars." (Handleiding r. 500-503)

Skill-output is daarom altijd een **concept ter validatie**, nooit een vastgesteld juridisch oordeel. Het veld `status` blijft `concept` en `markeringen[].bevestigd` blijft `false` totdat een mens het juridisch heeft gevalideerd.

## Welke discipline valideert welke output

De benodigde samenstelling van het team is maatwerk en hangt af van doel en context (Leidraad r. 117-140). Onderstaande tabel geeft de **minimale** menselijke reviewer per analyseproduct; bij twijfel of grotere impact schuift validatie naar het volledige team.

| Skill / product | Analyseresultaat | Minimale menselijke validatie |
|-----------------|------------------|-------------------------------|
| `annoteer-markeer` (A2a) | Markeringen + tekstdekking | Vaktechnisch jurist (juiste afbakening/uitleg) |
| `annoteer-classificeer` (A2b) | JAS-klasse + interpretatiemethode | Vaktechnisch jurist; bij meerduidigheid het team |
| `annoteer-diagram` (A2c) | Structuurdiagram centrale klasse | Vaktechnisch jurist + uitvoeringspraktijkjurist |
| `begrip-definitie` (A3a) | Begripsnaam + kern + contexten + voorbeelden | Vaktechnisch jurist (+ wetgevingsjurist bij open normen) |
| `begrip-regel` (A3b) | Afleidingsregel | Vaktechnisch jurist + regelanalist |
| `begrip-scenario` (A3c) | Scenario-koppeling | Uitvoeringspraktijkjurist |
| `begrip-bron` (A3d) | Secundaire bronnen | Vaktechnisch jurist |
| `valideer` (A4b) | Voorbeeldreeks | **Vaktechnisch jurist** — vult `is-voorspelling-juist` (juridisch oordeel, nooit door AI) |

## Operationele regel voor skills

- Elke skill noemt in haar `## Kwaliteitseisen (proces)` expliciet welke discipline de output moet valideren (verwijzend naar dit kader).
- De AI markeert nooit een output als juridisch vastgesteld; ze levert een concept en benoemt welke menselijke beoordeling nog nodig is.
- Interpretatieverschillen worden niet door de AI beslecht maar voorgelegd aan het team (zie `interpretatie.md` en de signaleringsregel in `KADERS.md`).
