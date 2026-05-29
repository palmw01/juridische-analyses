---
name: beoordeel
description: "Menselijke validatie — leidt de jurist door de te beoordelen analyseproducten, legt het oordeel vast en voert de dialogische herzielus uit. Gebruik: /beoordeel [pad] | art. [A] lid [L] [W] | --openstaand"
context: fork
agent: general-purpose
---

# /beoordeel — menselijke validatie

Leidt de jurist door de openstaande beoordelingspunten van een analyseproduct, registreert het menselijke oordeel in de audit-velden, en voert bij afkeuring de dialogische herzielus uit. De skill **neemt geen juridische beslissing** — ze faciliteert en legt vast wat de jurist beslist.

> Lees vóór elke run: `.claude/skills/kaders/samenwerking.md` en `.claude/skills/kaders/menselijke-validatie.md`.

## Trigger

| Trigger | Wanneer |
|---------|---------|
| `/beoordeel begrippen/[slug].yaml` (of `regels/…`, `validaties/…`) | Eén artefact beoordelen |
| `/beoordeel art. [A] lid [L] [W]` | Alle artefacten van één lid achtereenvolgens |
| `/beoordeel --openstaand` | Werk alle artefacten met `status: concept`/`ter-review` of openstaande punten af |

## Invoer

- Het te beoordelen artefact (begrip-, regel- of voorbeeldreeks-YAML) met door de A2/A3/A4b-skills gevulde velden.
- Voor `art. [A] lid [L] [W]`: alle begrippen/regels/voorbeeldreeksen die naar dat lid verwijzen (`grep -rl "art[A]/lid[L]" begrippen/ regels/ validaties/`).
- De disciplinetoewijzing uit `kaders/menselijke-validatie.md`.

## Werkwijze

Per artefact:

1. **Bepaal type + discipline.** Lees het artefact; bepaal het disciplineperspectief (jurist en/of regelanalist) uit `kaders/menselijke-validatie.md`.
2. **Verzamel openstaande punten:**
   - begrip: lege `definitie.kern`, onbevestigde `markeringen`, ontbrekende voorbeelden/grensgeval, `status`.
   - regel: ontbrekende invoer/uitvoer, taalpatroon, tussenresultaten.
   - voorbeeldreeks: kolommen met `is-voorspelling-juist: "?"`.
   - alle: aanwezige `signalering`-meldingen.
   Toon ook de relevante L3-waarschuwingen uit `tools/validate_note.py --file [pad]`.
3. **Leg de beslisvragen voor** (zie `kaders/samenwerking.md §Beslisvragen`), met de relevante artefactinhoud, en vraag de jurist per punt om een oordeel: **goedkeuren / afkeuren / voorbehoud** + onderbouwing. Bij een voorbeeldreeks: vraag het juridische oordeel `ja`/`nee`/`nvt` per `?`-kolom.
4. **Goedkeuren:**
   - Schrijf het `validatie`-blok via `stub_validatie(gevalideerd_door, "goedgekeurd", gevalideerd_op, discipline, notitie)` (uit `tools/jas_index_lib.py`).
   - begrip: zet de beoordeelde `markeringen` op `bevestigd: true` + `bevestigd-op` (peildatum/heden) + `bevestigd-door`; zet `status: gevalideerd` (mits `definitie.kern` gevuld).
   - voorbeeldreeks: vervang elke `?` door het opgegeven oordeel; zet `status: gevalideerd`.
5. **Afkeuren / voorbehoud (dialogische herzielus):**
   - Schrijf het `validatie`-blok met `oordeel: afgekeurd`/`voorbehoud` en de reden in `notitie`.
   - Herzie het artefact via de betreffende sub-skill (`begrip-definitie`, `annoteer-classificeer`, `valideer`, …) conform hun bronregels — niet uit eigen kennis.
   - Markeer de wijziging: verhoog waar van toepassing `definitie-versie` en vat de herziening samen in `validatie.notitie`. Zet `status: ter-review` en bied opnieuw ter beoordeling aan.
6. **Schrijf** met `schrijf_yaml` en **valideer**: `tools/.venv/bin/python tools/validate_note.py --file [pad]`. L1/L2-fouten herstellen vóór doorgaan; L3 rapporteren.

## Output

- Bijgewerkt artefact met ingevuld `validatie`-blok, bevestigde markeringen en/of ingevulde `is-voorspelling-juist`, en de juiste `status`. Schema's: `schemas/begrip.schema.json`, `schemas/regel.schema.json`, `schemas/voorbeeldreeks.schema.json`.

## Vervolg

- `make webapp` → `webapp/voortgang.html` toont de bijgewerkte validatiestatus.
- In een orchestrator-context volgt `/beoordeel` als afsluitende stap na A2–A4b.

## Kwaliteitseisen (proces)

- **De AI beslist niet.** `status: gevalideerd`, `markeringen[].bevestigd: true` en `is-voorspelling-juist` worden uitsluitend gezet op expliciete goedkeuring door de jurist.
- `gevalideerd-door` is altijd ingevuld bij goedkeuring; de AI vult dit nooit met een eigen naam.
- Vergt een punt aantoonbaar een andere discipline → `signalering`, niet zelf beslechten (`KADERS.md §Signaleringsdiscipline`).
- Herziening loopt via de sub-skills (bronregels blijven gelden), niet via vrije AI-bewerking.

## Bronnen

- Schemas: `schemas/begrip.schema.json`, `schemas/regel.schema.json`, `schemas/voorbeeldreeks.schema.json` (`validatie`-blok)
- Kaders: `kaders/samenwerking.md`, `kaders/menselijke-validatie.md`
- Helper: `tools/jas_index_lib.py` (`stub_validatie`)
- Canon: Handleiding §1 (mensenwerk, `handleiding.pages.md` r. 2771); Leidraad §2.4 (validatie, `leidraad.pages.md` r. 711-747)
