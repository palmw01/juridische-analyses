---
description: "A3c — koppelt een begrip aan juridische scenario's uit A1 via scenario-refs. Optioneel; alleen uitvoeren als scenarios/ bestaat."
context: fork
agent: general-purpose
---

# /begrip-scenario — A3c scenario-koppeling

Vult `scenario-refs[]` in op een begrip-YAML. Koppelt het begrip aan één of meer juridische scenario's uit Activiteit 1 (handmatig vastgelegd in `scenarios/{scenario-id}.yaml`).

> **Buiten scope:** scenario's zelf opstellen. Dat is A1, handmatig. Deze skill registreert alleen koppelingen tussen bestaande scenario's en begrippen.

## Invoer

- Begrip-YAML `begrippen/[slug].yaml` met gevulde definitie (uitvoer van `begrip-definitie`).
- Eén of meer scenario-bestanden in `scenarios/`.

## Stappen

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
4. Voeg per relevante scenario een entry toe aan `scenario-refs[]`:
   ```yaml
   scenario-refs:
   - scenario-id: scen-belastingschuldige-betaalt-tijdig
     rol: rechtsobject
     toelichting: "Belastingaanslag is voorwerp van de invorderingsrechtsbetrekking in stap 2"
   ```
5. Schrijf het begrip-YAML terug met `schrijf_yaml`.
6. Valideer.

## L3-aandacht

`validate_note.py` waarschuwt als een begrip met JAS-klasse `rechtsbetrekking` of `rechtsfeit` géén `scenario-refs[]` heeft. Bij die JAS-klassen is een scenario-koppeling vrijwel altijd verplicht (Handleiding §3.5.2c: scenario's voeden A3).

Bij ontbrekend scenario voor een dergelijk begrip: signaleer en stop met advies aan de domeinexpert om een scenario op te stellen.

## Kwaliteitseisen

- `scenario-refs[]` blijft leeg als er geen scenario's zijn — dit is geen blokkeerfout.
- Een `scenario-id` moet bestaan in `scenarios/{scenario-id}.yaml` (L2-controle).
- Gebruik niet meer dan één entry per (`scenario-id`, `rol`)-combinatie.
