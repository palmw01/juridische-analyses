# Glossarium — project- en canon-termen

> **Doel:** ondubbelzinnig vastleggen wat veelgebruikte termen en velden betekenen, zodat skills en kaders dezelfde taal spreken. Aanvulling op het termen-glossarium in `canon-ankers.md` (canon ↔ project).

---

## Activiteitscodes

| Code | Betekenis | Canon |
|------|-----------|-------|
| A1 | Bepalen werkgebied (doel, scenario's, bronnen) — **buiten AI-scope** | Leidraad §2; HW §3.3 |
| A2 (a/b/c) | Markeren / classificeren / diagram — **AI-scope** | HW §3.4 |
| A3 (a/b/c/d) | Begrippen / afleidingsregels / scenario-koppeling / bronrelaties — **AI-scope** | HW §3.5 |
| A4a / A4b | Valideren via scenario's / via voorbeeldreeksen (alleen A4b in AI-scope) | HW §3.6 |
| A5 | Signaleren ontbrekend/onbekend uitvoeringsbeleid — **buiten AI-scope** | Leidraad §2.4; HW §3.7 |
| A6 | Kennismodel opstellen — **buiten AI-scope** | Leidraad §4 |

## Velden en begrippen

| Term | Betekenis | Waar |
|------|-----------|------|
| `toelichting-klasse` | Vrij-tekstveld bij een annotatierij/markering waarin de classificatie- en interpretatiekeuze wordt gemotiveerd (welke methode, waarom, met bronanker). | `schemas/annotatie-lid.schema.json`; gebruikt in `interpretatie.md`, `begripsnaam.md` |
| `invoerbegrippen` | De begrippen die als input dienen voor een afleidingsregel (waaruit het afgeleide begrip wordt bepaald). | `regeltypen.md`, `relaties.md` |
| `afgeleid begrip` | Het uitvoer-begrip van een afleidingsregel (`herkomst: afgeleid`). | `definitie.md`, `regeltypen.md` |
| `tussenresultaat` | Een begrip/regel dat een tussenstap in een impliciet algoritme expliciet maakt; gemarkeerd met de `tussenresultaat`-vlag. | HW r. 301-303 (impliciete algoritmen); `regeltypen.md` |
| `signalering` | Veld waarin open normen, meerduidigheid, interpretatie-divergentie of vermoeden van onbekend beleid worden vastgelegd als input voor A5/mensen — **nooit door de AI opgelost**. | `schemas/annotatie-lid.schema.json`; `KADERS.md §Signaleringsdiscipline` |
| `primaire juridische bron` | Bron die rechtstreeks als rechtmatige grondslag dient: wet- en regelgeving en gepubliceerd uitvoeringsbeleid. Parlementaire geschiedenis en jurisprudentie zijn **geen** primaire bron, maar interpretatiebron. | Leidraad r. 572-580; `interpretatie.md`, `begrip-bron` |
| `interpretatiebron` | Bron die de uitleg ondersteunt maar geen zelfstandige rechtmatige grondslag is (MvT, kamerstukken, jurisprudentie, doctrine). Vastleggen in `bronnen-secundair`. | HW §3.5.4; `begrip-bron` |

## Status-enums (let op: verschillen per bestandstype)

De status-waarden verschillen bewust per artefact; harmoniseer ze **niet**.

| Bestandstype | Toegestane status | Bron |
|--------------|-------------------|------|
| `begrip` | `concept`, `ter-review`, `gevalideerd`, `vervallen`, `te-verrijken` | `schemas/begrip.schema.json` |
| `voorbeeldreeks` (kolom) | `concept`, `gereviseerd`, `gevalideerd` | `schemas/voorbeeldreeks.schema.json`; `voorbeeldreeks.md §Statusovergangen` |

Een begrip kent een levensloop (incl. verrijking/vervallen); een voorbeeldreeks-kolom kent alleen de validatie-toestand van dat testgeval. Statuswijziging naar `gevalideerd` is in beide gevallen een **menselijke A4-handeling**, geen AI-stap.
