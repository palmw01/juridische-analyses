# Skill-kaders en workflow — Wetsanalyse A2 / A3 / A4b

Dit bestand geeft het overkoepelende kader voor alle skills in `.claude/skills/`. **Lees dit bestand vóór elke skill-run.**

## Scope

De skills ondersteunen drie deelactiviteiten uit de Wetsanalyse-methodiek:

- **A2 — Markeren en classificeren** (Handleiding §3.4)
- **A3 — Vaststellen van de betekenis** (Handleiding §3.5)
- **A4b — Voorbeeldreeksen opstellen** (Handleiding §3.6.2b)

Activiteiten A1, A4a, A5 en A6 zijn nadrukkelijk **buiten AI-scope**. De skills mogen daarvoor input opmerken (bijv. ontbrekende scenario's, signaleringen, gegevensmodel-vragen) maar nooit zelf invullen.

## Conflicthiërarchie

Bij tegenspraak tussen documenten geldt de volgende volgorde:

1. **PDF-bronnen** — *Handleiding Wetsanalyse* en *Leidraad voor Wetsanalyse op maat* (zie `docs/wetsanalyse-methodiek/`).
2. **`kaders/`-bestanden** — projectsamenvattingen van de PDF-normen, mét expliciete bronverwijzing per regel.
3. **`SKILL.md`-bestanden** — procesinstructies per skill.
4. **Claude-aannames** — alleen wanneer 1–3 zwijgen of meerduidig zijn.

Als een PDF-norm en projectconventie verschillen: schrijf het verschil expliciet uit, met motivatie. Een projectconventie staat in een kader-bestand altijd vermeld als "projectconventie".

## Bronanker-eis

**Skill-output mag nooit een juridische conclusie bevatten zonder bronanker.** Elke uitspraak in annotatie, begripsdefinitie, regel of voorbeeldreeks verwijst via een id-veld terug naar de primaire wettekst:

- `annotatie-id` / `bron-annotatie-id` voor wetsformuleringen
- `begrip-id` voor begrippen
- `regel-id` voor afleidingsregels
- `voorbeeldreeks-id` voor testmatrices
- `bronnen-secundair[].vindplaats` voor secundaire bronnen (Leidraad, beleidsregels, jurisprudentie)

## Workflow

```
A1 (handmatig — buiten AI-scope)
    └─ doel + projecttypologie + scenario's in scenarios/{scenario-id}.yaml

A2  /annoteer art. [A] [W]
    └─ annoteer-markeer (Flow A: index aanmaken)

    /annoteer art. [A] lid [L] [W]
    ├─ 1. annoteer-markeer       (A2a — markeert wetsformuleringen)
    ├─ 2. annoteer-classificeer  (A2b — wijst jas-klasse + interpretatiemethode toe)
    └─ 3. annoteer-diagram       (A2c — bouwt diagram met centrale klasse)
       → output: annotatie-lid.json + begrip-stubs in begrippen/

A3  /begrip [slug]
    ├─ 1. begrip-definitie       (A3a — kern + contexten + soort + herkomst + voorbeelden)
    ├─ 2. begrip-regel           (A3b — alleen bij JAS-klasse afleidingsregel; maakt regels/AR-*.yaml)
    ├─ 3. begrip-scenario        (A3c — koppelt begrip aan scenario-id's uit A1)
    └─ 4. begrip-bron            (A3d — registreert secundaire bronnen)

A4b /valideer AR-[id]
    └─ valideer                  → validaties/VR-*.yaml met ≥ 3 kolommen

Orchestrator
    /wetsanalyse art. [A] lid [L] [W]
    ├─ Voert bovenstaande keten sequentieel uit voor één lid
    ├─ TaskList live in Claude Code
    ├─ Run-rapport in rapporten/runs/run-YYYY-MM-DD-HHMM-{slug}.md
    └─ Dashboard webapp/voortgang.html via make webapp
```

## Skills-index

### Activiteit 2

| Skill | Doel | Triggert door |
|-------|------|---------------|
| `annoteer-markeer` | A2a — markeringen + annotatierij-skelet | `/annoteer art. [A] [W]` of `/annoteer art. [A] lid [L] [W]` |
| `annoteer-classificeer` | A2b — jas-klasse + interpretatiemethode + toelichting | volgt op `annoteer-markeer` |
| `annoteer-diagram` | A2c — Mermaid-diagram met centrale klasse | volgt op `annoteer-classificeer` |

### Activiteit 3

| Skill | Doel | Triggert door |
|-------|------|---------------|
| `begrip-definitie` | A3a — kern + contexten + soort/herkomst + voorbeelden + relaties | `/begrip [slug]` |
| `begrip-regel` | A3b — regel-YAML voor afleidingsregel-begrippen | volgt op `begrip-definitie` bij `jas-klasse: afleidingsregel` |
| `begrip-scenario` | A3c — `scenario-refs[]` invullen | volgt op `begrip-definitie` |
| `begrip-bron` | A3d — `bronnen-secundair[]` invullen | volgt op `begrip-definitie` |

### Activiteit 4b

| Skill | Doel | Triggert door |
|-------|------|---------------|
| `valideer` | A4b — voorbeeldreeks-YAML | `/valideer AR-[id]` |

### Orchestratie

| Skill | Doel | Triggert door |
|-------|------|---------------|
| `wetsanalyse` | Volledige A2–A4b-keten voor één lid | `/wetsanalyse art. [A] lid [L] [W]` |
| `wettenbank` | Wetstekst ophalen via MCP + kruisrefs | `/wettenbank art. [A] [W]` |

## Cross-references (kader → skills)

Welke kader-bestanden welke skills voeden:

| Kader-bestand | Gebruikt door |
|---------------|---------------|
| `kaders/jas-taxonomie.md` | annoteer-classificeer, annoteer-diagram, begrip-definitie |
| `kaders/markeerregels.md` | annoteer-markeer |
| `kaders/diagramregels.md` | annoteer-diagram |
| `kaders/begripsnaam.md` | annoteer-markeer (stub-naam), begrip-definitie |
| `kaders/definitie.md` | begrip-definitie |
| `kaders/relaties.md` | begrip-definitie |
| `kaders/regeltypen.md` | begrip-regel, valideer |
| `kaders/voorbeeldreeks.md` | valideer |
| `kaders/interpretatie.md` | annoteer-classificeer, begrip-definitie |

## Code-laag

Skills delegeren naar code waar mogelijk:

| Wat | Waar | Functie |
|-----|------|---------|
| Stub-skeletten (annotatie, begrip, regel, VR) | `tools/jas_index_lib.py` | `stub_annotatie_index`, `stub_annotatie_lid`, `stub_annotatierij`, `stub_begrip`, `stub_regel`, `stub_voorbeeldreeks` |
| YAML/JSON schrijven met projectconventies | `tools/jas_index_lib.py` | `schrijf_yaml`, `schrijf_json` |
| Definitie-helpers (kern/contexten) | `tools/jas_index_lib.py` | `haal_kern`, `haal_contexten` |
| Slug-derivatie | `tools/jas_index_lib.py` | `slug_from_begrip_id` |
| JAS-index (begrip-id → jas-klasse) | `tools/jas_index_lib.py` | `bouw_jas_index` |
| Validatie L1/L2/L3 | `tools/validate_note.py` | `--file`, `--full`, `--integrity` |
| Schemas (canonieke L1) | `schemas/*.schema.json` | id-patronen, enums, minItems |

Wat de validator al afdwingt, herhaalt de skill niet meer.

## Kwaliteitseisen (gedeeld)

Voor elke skill geldt:

1. **Traceerbaarheid.** Elke output verwijst naar bron via id-veld.
2. **Idempotentie.** Bestaand bestand niet overschrijven zonder bevestiging.
3. **Validatie.** Run `tools/validate_note.py --file [pad]` na elk schrijfcommando; L1/L2-fouten herstellen vóór doorgaan; L3 rapporteren.
4. **Geen MCP-aanroep als bron al lokaal bestaat.** Eerst `find bronnen/[B]/ …`.
5. **Peildatum uit bronbestand**, niet uit lopende sessie.
6. **Letterlijk citeren** van wetstekst — nooit parafraseren.

## Skill-sjabloon (projectconventie)

> **Spec-anker.** De [Agent Skills-spec](https://agentskills.io/specification) vereist alleen een `name`-veld in de frontmatter en een markdown-body — géén vaste sectie-structuur. De [Claude Code skill-docs](https://code.claude.com/docs/en/skills.md) voegen optionele velden toe (`context`, `agent`, `when_to_use`, `allowed-tools`, …) maar schrijven ook geen body-secties voor. Het sjabloon hieronder is **projectconventie** voor onderlinge consistentie en orchestrator-leesbaarheid; zie `kaders/projectconventies.md` #24.

### Frontmatter

**Verplicht** (Anthropic-spec):
- `name` — kebab-case, identiek aan mapnaam.
- `description` — 1-1024 karakters; bevat trigger-zin.

**Optioneel** (Claude Code-extensies):
- `context: fork` — geïsoleerde subagent (langlopende A2/A3/A4b-taken).
- `agent: general-purpose` — subagent-type.
- `when_to_use` — extra context als description te beknopt is.

### Body — sub-skill (standaard)

```markdown
# /<naam> — <korte titel>

<1-2 zinnen samenvatting; eindigt met "Lees vóór elke run: kaders/<x>.md.">

## Trigger
<commandvormen>

## Invoer
<verwachte bestanden + parameters>

## Werkwijze
1. ...

## Output
<bestand(en) + verwijzing naar schemas/<x>.schema.json + bestaand voorbeeld>

## Vervolg
<volgende skill in keten>

## Kwaliteitseisen (proces)
<alleen regels die niet in schema of kader staan>

## Bronnen
- Schema: `schemas/<x>.schema.json`
- Kaders: `kaders/<a>.md`, `kaders/<b>.md`
- Canon: handleiding §X.Y[, leidraad §A.B]
- Projectconventies: `kaders/projectconventies.md` #N (indien van toepassing)
```

### Body — orchestrator (alleen `wetsanalyse`)

Basis + extra secties **na Werkwijze**: `## TaskList`, `## Pauze-gedrag`, `## Foutafhandeling`. `## Werkwijze` heet hier `## Sequentie` (10 stappen). `## Bronnen` blijft verplicht.

### Body — utility (alleen `wettenbank`)

Basis met afwijking: `## Werkwijze` mag opgesplitst zijn in `### Stap 1`, `### Stap 2`, …; `## Vervolg` vervalt (geen vaste opvolger). `## Kwaliteitseisen (proces)` en `## Bronnen` blijven verplicht.

### Lengte- en disclosure-richtlijn

Elke SKILL.md blijft onder de Anthropic-richtlijn van 500 regels. Uitgebreide referenties (JAS-taxonomie, markeerregels, regeltypen, voorbeeldreeks-patronen) staan in `kaders/`; uitvoerbare helpers in `tools/jas_index_lib.py`. Skills bevatten *proces* — niet *inhoud*.
