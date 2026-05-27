---
name: begrip-scenario
description: "A3c — koppelt een begrip aan juridische scenario's uit A1 via scenario-refs. Optioneel; alleen uitvoeren als scenarios/ bestaat."
context: fork
agent: general-purpose
---

# /begrip-scenario — A3c scenario-koppeling

Vult `scenario-refs[]` in op een begrip-YAML. Koppelt het begrip aan één of meer juridische scenario's uit Activiteit 1 (handmatig vastgelegd in `scenarios/{scenario-id}.yaml`).

> **Buiten scope:** scenario's zelf opstellen. Dat is A1, handmatig. Deze skill registreert alleen koppelingen tussen bestaande scenario's en begrippen.

## Trigger

Aangeroepen door de orchestrator of `/begrip [slug]` na `begrip-definitie` (geen eigen `/`-commando).

## Invoer

- Begrip-YAML `begrippen/[slug].yaml` met gevulde definitie (uitvoer van `begrip-definitie`).
- Eén of meer scenario-bestanden in `scenarios/`.

## Werkwijze

1. Controleer of `scenarios/` bestaat met ≥ 1 scenario-bestand. Ontbreekt → meld:
   ```
   Geen scenario's gevonden in scenarios/. A1 is buiten AI-scope; vraag de domeinexpert
   om scenarios/{id}.yaml op te stellen voordat A3c wordt uitgevoerd. Skill stopt zonder
   wijziging.
   ```
2. Lees alle scenario-YAML's in `scenarios/` met `load_yaml`.
3. Voor elk scenario: bepaal of het huidige begrip een rol speelt in een van de stappen:
   - `rechtssubject` — het begrip is de hoofdrolspeler in het scenario.
   - `rechtsobject` — het begrip is het voorwerp (bijv. belastingaanslag).
   - `voorwaarde` — het begrip is een voorwaarde voor een rechtsfeit in het scenario.
   - `uitvoer` — het begrip is een rechtsgevolg of berekende waarde.
   - `context` — het begrip wordt slechts terloops genoemd.
4. Voeg per relevante scenario een entry toe aan `scenario-refs[]` met `scenario-id`, `rol`, optioneel `toelichting`. Voor het exacte formaat: zie `schemas/begrip.schema.json` (`scenario-refs[]`-veld) en bestaande voorbeelden in `begrippen/`.
5. Schrijf het begrip-YAML terug met `schrijf_yaml`.
6. Valideer.

## Output

- `begrippen/[slug].yaml` — `scenario-refs[]` aangevuld of leeg gelaten. Schema: `schemas/begrip.schema.json`.

## Vervolg

`begrip-bron` (A3d) voor secundaire bronnen, indien relevant.

## Kwaliteitseisen (proces)

- `scenario-refs[]` blijft leeg als er geen scenario's zijn — dit is geen blokkeerfout.
- Gebruik niet meer dan één entry per (`scenario-id`, `rol`)-combinatie.
- `validate_note.py` waarschuwt (L3) als een begrip met JAS-klasse `rechtsbetrekking` of `rechtsfeit` géén `scenario-refs[]` heeft (Handleiding §3.5.2c: scenario's voeden A3). Bij ontbrekend scenario: signaleer en stop met advies aan de domeinexpert.

Structurele vereisten (rol-enum, bestaande scenario-id via L2-check) worden door schema + `validate_note.py` afgedwongen.

## Bronnen

- Schema: `schemas/begrip.schema.json` (veld `scenario-refs[]`), `schemas/scenario.schema.json`
- Kaders: —
- Canon: handleiding §3.3 (scenario's), §3.5.2c; leidraad §2.4 (A1 → A3-keten)
- Projectconventies: `kaders/projectconventies.md` #21 (scenario-refs structuur)
