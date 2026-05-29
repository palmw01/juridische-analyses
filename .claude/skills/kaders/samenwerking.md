# Jurist-AI-samenwerking (menselijke validatie)

> **Bron:** Handleiding Wetsanalyse §1 (multidisciplinair samenwerken, `handleiding.pages.md` r. 500-516; "mensenwerk" r. 2771); Leidraad §2.4 (validatie + signalering naar beleidsverantwoordelijken, `leidraad.pages.md` r. 711-747). Bouwt voort op `menselijke-validatie.md` (wie valideert wat) — dupliceer die tabel hier niet. Gebruikt door `/beoordeel` en de orchestrator.

---

## Uitgangspunt

De AI levert **concepten**; de jurist draagt de juridische verantwoordelijkheid en valideert. Wetsanalyse is mensenwerk en multidisciplinair (zie `menselijke-validatie.md`). In deze workflow werkt één senior jurist (domein Inning) samen met de AI en vertegenwoordigt daarbij de relevante disciplines. De twee operationele rollen die een oordeel vastleggen zijn:

- **jurist** — juridische juistheid (afbakening, classificatie, begripsbetekenis, regelinhoud, voorbeeldreeks-oordeel).
- **regelanalist** — formaliseerbaarheid van afleidingsregels (taalpatroon, invoer/uitvoer, tussenresultaten).

Vergt een kwestie aantoonbaar een andere discipline (bv. wetgevingsjurist bij een open norm, uitvoeringspraktijkjurist bij procesimpact), dan **signaleert** de jurist dat (zie `KADERS.md §Signaleringsdiscipline`) in plaats van het oordeel zelf te forceren.

## Werkritme — de validatiecyclus

```
AI (skill)            jurist (/beoordeel)
   levert concept  ─────────────►  beoordeelt per beslisvraag
   (status: concept)                    │
                                        ├─ goedkeuren ─► validatie-blok ingevuld,
                                        │                markeringen bevestigd,
                                        │                status → gevalideerd
                                        │
                                        └─ afkeuren/voorbehoud ─► reden vastleggen
   herziet concept  ◄───────────────────┘                       (dialogische herzielus)
   markeert wijziging
   (status → ter-review)  ─────────────►  herbeoordeling
```

De cyclus herhaalt tot de jurist goedkeurt. De AI zet **nooit** autonoom `status: gevalideerd` of `markeringen[].bevestigd: true`; dat gebeurt uitsluitend op expliciete goedkeuring binnen `/beoordeel`.

## Beslisvragen per artefacttype

Beoordeel vanuit het genoemde disciplineperspectief; de inhoudelijke norm staat in het gelinkte kader.

| Artefact | Discipline | Kernvragen (zie kader) |
|----------|-----------|------------------------|
| Markering (A2a) | jurist | Maximaal-betekenisvolle afbakening? Lidwoord/verwijzing mee? Tekstdekking volledig? (`markeerregels.md`) |
| Classificatie (A2b) | jurist | Meest specifieke JAS-klasse? Interpretatiemethode + onderbouwing? Meerduidigheid gesignaleerd? (`jas-taxonomie.md`, `interpretatie.md`) |
| Diagram (A2c) | jurist | Centrale klasse correct? Geen losse knopen zonder relatie? (`diagramregels.md`) |
| Begrip (A3a) | jurist | Naam volgt de regels? Kern substitueerbaar, geen punt? Voorbeelden incl. grensgeval? Homoniem/synoniem juist? (`begripsnaam.md`, `definitie.md`) |
| Afleidingsregel (A3b) | jurist + regelanalist | Juridisch volledig? Taalpatroon? Invoer/uitvoer en tussenresultaten expliciet? (`regeltypen.md`) |
| Voorbeeldreeks (A4b) | jurist | `is-voorspelling-juist` per kolom — het juridische oordeel; happy/grens/negatief gedekt? (`voorbeeldreeks.md`) |

## De dialogische herzielus

Bij **afkeuren** of **voorbehoud**:

1. De jurist geeft de reden in natuurlijke taal (wat klopt niet, wat moet anders).
2. De AI legt die reden vast in `validatie.notitie` met `oordeel: afgekeurd`/`voorbehoud`.
3. De AI herziet het artefact via de betreffende sub-skill (`begrip-definitie`, `annoteer-classificeer`, `valideer`, …) — niet rechtstreeks uit eigen kennis, maar conform de normale skill-bronregels.
4. De AI **markeert wat wijzigde**: verhoog waar van toepassing `definitie-versie`, en vat de wijziging samen in `validatie.notitie`.
5. Status gaat naar `ter-review`; de jurist beoordeelt opnieuw. Pas bij `oordeel: goedgekeurd` wordt `status: gevalideerd`.

## Vastlegging (traceerbaarheid)

- **Per artefact** (begrip, regel, voorbeeldreeks): het optionele `validatie`-blok — `gevalideerd-door`, `gevalideerd-op`, `oordeel`, optioneel `discipline` (`jurist`/`regelanalist`) en `notitie`. Helper: `stub_validatie` in `tools/jas_index_lib.py`.
- **Per markering**: `bevestigd` + `bevestigd-op` + `bevestigd-door`.
- **Status**: `concept` → `ter-review` → `gevalideerd` (begrip); `concept` → `gereviseerd` → `gevalideerd` (voorbeeldreeks).
- `validate_note.py` geeft **L3-waarschuwingen** (adviserend, niet-blokkerend) bij `status: gevalideerd` zonder ingevuld `validatie`-blok en bij `bevestigd: true` zonder `bevestigd-door`. De jurist stuurt het proces; niets blokkeert de commit.

## Verwijzingen

- `menselijke-validatie.md` — welke discipline valideert welk product.
- `KADERS.md §Signaleringsdiscipline` — open normen/meerduidigheid signaleren.
- `/beoordeel` (`.claude/skills/beoordeel/SKILL.md`) — de uitvoerende review-skill.
