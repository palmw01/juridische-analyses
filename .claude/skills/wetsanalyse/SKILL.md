---
name: wetsanalyse
description: "Orchestrator — voert de volledige A2–A4b-keten voor één lid uit. Gebruik: /wetsanalyse art. [A] lid [L] [W] | --auto | --vanaf [stap]"
context: fork
agent: general-purpose
---

# /wetsanalyse — orchestrator A2 → A3 → A4b

Voert de gehele wetsanalyse-keten sequentieel uit voor één lid. Roept sub-skills aan, doet existing-checks, schrijft een run-rapport en updatet het webapp-dashboard.

> Lees vóór elke run: `.claude/skills/KADERS.md` (conflicthiërarchie en bronanker-eis gelden ook hier).

## Trigger

```
/wetsanalyse art. [A] lid [L] [W]               ← interactief (pauzes tussen activiteiten)
/wetsanalyse art. [A] lid [L] [W] --auto        ← geen pauzes
/wetsanalyse art. [A] lid [L] [W] --vanaf begrip  ← skip A2 (alleen als al aanwezig)
/wetsanalyse art. [A] lid [L] [W] --vanaf valideer  ← skip A2 en A3
```

Aliasen: `[W]` kan een vrije wetsafkorting zijn (`IW 1990`, `Awb`, …); de orchestrator vertaalt naar BWB-id via `.claude/skills/wettenbank/bwb-mapping.md`.

## Invoer

- Artikel + lid + wetsafkorting (slash-argument).
- Optioneel: `--auto` (geen pauzes) of `--vanaf [stap]` (skip A2 of A2+A3 als output al bestaat).
- Bestaande artefacten in `bronnen/`, `annotaties/`, `begrippen/`, `regels/`, `validaties/` — gebruikt voor existing-checks (idempotentie).

## TaskList

Bouw bij start een TaskList met alle voorziene stappen op basis van de input. De daadwerkelijke stappen 3-6 worden pas zichtbaar nadat `annoteer-markeer` is afgerond (omdat het aantal begrippen pas dan bekend is).

Beginnende TaskList:

```
[ ] wettenbank — art. [A] [W] ophalen          (skip als bronnen/[B]/art[A].json bestaat)
[ ] annoteer-markeer — Flow A index            (skip als annotaties/[B]/art[A].json bestaat)
[ ] annoteer-markeer — Flow B lid [L]          (skip als annotaties/[B]/art[A]-lid[L].json bestaat)
[ ] tekstdekkings-controle — lid [L]
[ ] annoteer-classificeer — lid [L]
[ ] annoteer-diagram — lid [L]
[ ] begrip-XXX  (één per stub; toegevoegd ná annoteer-markeer)
[ ] valideer-XXX  (één per regel-YAML; toegevoegd ná begrip-regel)
[ ] run-rapport schrijven
[ ] webapp-dashboard updaten
```

Gebruik `TaskCreate` aan het begin en `TaskUpdate` bij elke status-overgang. Status: `pending` → `in_progress` → `completed` of `blocked` (met reden).

## Sequentie

### 0. Argument-parsing en doel-/maatwerkcheck

- `bwb-id` afleiden uit `[W]`. Onbekend → meld en stop.
- Pad: `bronnen/[B]/`, `annotaties/[B]/`, etc.
- `--vanaf` bepaalt vanaf welke fase wordt gestart.
- **Doel-bewustzijn (maatwerk).** A2/A3/A4b is een gekozen subset; de gewenste diepgang volgt uit het doel van de analyse (IT, handmatig proces, uitvoeringstoets, casuïstiek — Leidraad r. 79-96). Ga niet uit van software als enig doel.
- **Start-informatie (A1) controleren, niet invullen.** Ontbreken `scenarios/` of een vastgelegd doel/projecttypologie, dan signaleer je dat in het run-rapport (welke startinformatie ontbreekt) en ga je door waar mogelijk — je verzint geen A1-keuzes (zie `KADERS.md §Scope`).

### 1. wettenbank (als `bronnen/[B]/art[A].json` ontbreekt)

Roep `/wettenbank art. [A] [W]` aan. Bij MCP-fout: stop, markeer task `blocked`, schrijf in het rapport welke fout en welk manueel alternatief mogelijk is.

### 2. annoteer-markeer (Flow A)

Als `annotaties/[B]/art[A].json` ontbreekt: roep de sub-skill aan om de index-JSON aan te maken.

### 3. annoteer-markeer (Flow B)

Als `annotaties/[B]/art[A]-lid[L].json` ontbreekt: roep de sub-skill aan om markeringen + begrip-stubs te maken. Verzamel de lijst van nieuwe begrip-stubs voor stappen 6.

### 3.5. tekstdekkings-controle (vóór classificeren)

Voer de tekstdekkings-volledigheidscheck uit op `annotaties/[B]/art[A]-lid[L].json`:

```
tools/.venv/bin/python tools/validate_note.py --file annotaties/[B]/art[A]-lid[L].json
```

Inspecteer de L3-meldingen **"niet-gemarkeerde wetstekst"** en **"markering niet teruggevonden in wetstekst"** (Handleiding §3.4.2a). Bij ongedekte betekenisvolle fragmenten: vul de ontbrekende markeringen aan (her-run de `annoteer-markeer`-logica voor het lid) vóór je classificeert. Niet-blokkerend (L3), maar log het resultaat — opgelost of bewust geaccepteerd — in het run-rapport.

### 4. annoteer-classificeer

Vul `jas-klasse`, `interpretatiemethode`, `toelichting-klasse`, `signalering`, `kruisreferenties`, `delegatiestructuur` in voor het lid.

### 5. annoteer-diagram

Bouw het `diagram`-object op basis van de geclassificeerde rijen.

### 6. begrip-* per stub

Voor elke begrip-stub uit stap 3 die nog niet "afgerond" is (`definitie.kern` leeg of relaties leeg):

1. **begrip-definitie** — vult kern, contexten, soort, herkomst, relaties, voorbeelden.
2. **begrip-regel** — alleen bij `jas-klasse: afleidingsregel`; maakt `regels/AR-….yaml`.
3. **begrip-scenario** — vult `scenario-refs[]` als `scenarios/` bestaat; anders skip met melding.
4. **begrip-bron** — vult `bronnen-secundair[]` als secundaire bronnen relevant zijn.

Bij idempotentie-check (begrip al afgerond): skip dat begrip, log in het rapport.

### 7. valideer per nieuwe regel

Voor elke `regels/AR-….yaml` die in stap 6 is aangemaakt: roep `/valideer AR-id` aan om `validaties/VR-….yaml` te maken.

### 8. Project-validatie

```
tools/.venv/bin/python tools/validate_note.py --full
```

Verzamel L1/L2/L3-meldingen voor het rapport.

### 9. Run-rapport schrijven

Roep `tools/genereer_run_rapport.py` aan met de verzamelde stap-status, gewijzigde bestanden, validatie-uitkomsten en openstaande `?`-velden. Output naar `rapporten/runs/run-YYYY-MM-DD-HHMM-art{A}-lid{L}.md`.

### 10. Webapp updaten

```
make webapp
```

Genereert onder andere `webapp/voortgang.html` met de cross-cutting status.

## Pauze-gedrag

In interactieve modus (zonder `--auto`):

- Pauzeer ná stap 2 (Flow A) — vraag bevestiging om door te gaan met annotatie van lid [L].
- Pauzeer ná stap 5 (A2 compleet) — toon de annotatie-uitkomst en vraag bevestiging om A3 te starten.
- Pauzeer ná stap 6 (alle begrippen) — toon definities en vraag bevestiging om A4b te starten.

Bij `--auto`: doorlopen zonder pauzes, run-rapport markeert pauzepunten als "automatisch gepasseerd".

## Foutafhandeling

- Bij L1/L2-fout in een sub-skill: stop, markeer task `blocked`, schrijf foutmelding naar rapport. Adviseer welke sub-skill handmatig her-run kan oplossen.
- Bij MCP-time-out: retry één keer; daarna `blocked`.
- Bij ontbrekende `scenarios/` voor een rechtsbetrekking/rechtsfeit-begrip: meld L3-waarschuwing maar blokkeer niet.

## Output

- TaskList volledig afgerond (status per stap) in de Claude Code UI.
- Run-rapport in `rapporten/runs/`.
- Dashboard in `webapp/voortgang.html` na `make webapp`.
- Eindbericht in de chat: "Wetsanalyse art. [A] lid [L] [W] voltooid — zie rapporten/runs/run-…md en webapp/voortgang.html. Openstaande punten: N grensgevallen op `?`."

## Kwaliteitseisen (proces)

- Geen sub-skill twee keer aanroepen voor hetzelfde bestand (idempotentie).
- Bij elke stap: TaskList bijwerken vóór en na uitvoering.
- Run-rapport bevat altijd een Mermaid-diagram van de keten.
- Alle uitvoer is traceerbaar — geen losse bestanden buiten de standaardmappen.
- **Concept ter validatie.** De keten levert concepten op; het run-rapport benoemt per product welke menselijke discipline nog moet valideren (`kaders/menselijke-validatie.md`) en welke `signalering`/`?`-velden openstaan voor het multidisciplinaire team.

## Bronnen

- Sub-skills + kaders: zie `.claude/skills/KADERS.md` (workflow + skills-index, incl. `menselijke-validatie.md` en `glossarium.md`).
- Tools: `tools/genereer_run_rapport.py`, `tools/validate_note.py --full`, `make webapp`.
- Canon: Handleiding §3.4–3.6 (A2–A4b-keten); Leidraad §2 (maatwerk; `leidraad.pages.md` r. 79-96).
