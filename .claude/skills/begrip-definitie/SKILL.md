---
name: begrip-definitie
description: "A3a — vult begripsdefinitie (kern + contexten), soort, herkomst, relaties en voorbeelden in vanuit gevulde markeringen. Gebruik: /begrip [slug]"
context: fork
agent: general-purpose
---

# /begrip-definitie — A3a begripsdefinitie

Vult de inhoudelijke velden van een begrip-YAML in. Bronnen zijn uitsluitend `markeringen[].tekst` in het begrip-bestand zelf (vastgelegd door `annoteer-markeer`). De wettenbank wordt **niet** opnieuw aangeroepen.

> Lees vóór elke run: `.claude/skills/kaders/definitie.md`, `.claude/skills/kaders/begripsnaam.md`, `.claude/skills/kaders/relaties.md`.

## Trigger

| Trigger | Wanneer |
|---------|---------|
| `/begrip [slug]` | Eén begrip invullen |
| `/begrip-alles art. [A] [W]` | Alle begrip-YAML's van een artikel achtereenvolgens verwerken |

## Voorbereiding

1. **Idempotentie:** als `definitie.kern`, `soort`, `herkomst` allemaal gevuld zijn én `relaties` minstens één niet-lege lijst heeft: meld "begrip [slug] is al afgerond" en stop. Overschrijf nooit zonder bevestiging.
2. **Enrichment-queue:** lees `rapporten/enrichment-queue.json`. Als dit begrip een open beslissing heeft (`status: te-verrijken` zonder `beslissing`-veld): stop en meld; los eerst op.
3. **Annotaties terugvinden:** `grep -rl "[begrip-id]" annotaties/`. Lees elke gevonden annotatie-JSON. Uit de rij met dit `begrip-id`: vul `jas-klasse` en `toelichting-klasse` op het top-level van de YAML bij (uit annotatie naar begrip — niet uit eigen kennis).
   - **Brondefinitie-check (zie `kaders/jas-taxonomie.md §Brondefinitie`):** is de begripsnaam uitdrukkelijk omschreven in een ander artikel in de wetgeving? Zo ja: `jas-klasse: brondefinitie`; de markering uit het huidige artikel krijgt `bijdrage: aanvullend` en wordt als context/verfijning vastgelegd, niet als kern.
4. **Verwante begrippen verkennen:** `ls begrippen/` en lees specifiek de mogelijke generalisaties (`is-een`), composities (`heeft`) en gevolgen (`leidt-tot`).

Bij `/begrip-alles art. [A] [W]`: zoek alle begrip-YAML's met een markering die begint met `[B]/art[A]`:
```
grep -rl "bron-annotatie-id.*[B]/art[A]" begrippen/
```

## Definitie opstellen

Zie `kaders/definitie.md` voor de volledige normen. Kort:

- **Kern** gebaseerd op de primaire markeringen (`bijdrage: primair`). Geldig voor alle bronartikelen. Geen punt aan het einde. Substitutietest doorlopen.
- **Contexten** alleen toevoegen als de Verrijkingsprotocol-beslisboom een context-item rechtvaardigt (verfijning / uitbreiding / uitzondering).
- **`definitie-gebaseerd-op`** bevat uitsluitend de markering-id's die de **kern** staven.
- **`definitie-versie`** verhogen bij elke kernwijziging.

## Velden bijwerken

De canonieke veldenset, enums en conditionele regels staan in `schemas/begrip.schema.json` — zie ook `begrippen/belastingaanslag.yaml` als levend voorbeeld. De skill vult vanuit `markeringen[]`:

- `definitie.kern` (vereist; geen punt aan einde)
- `definitie.contexten[]` (optioneel — `bijdrage`-beslisboom in `kaders/definitie.md §Verrijkingsprotocol`)
- `definitie-versie` (verhogen bij kernwijziging)
- `definitie-gebaseerd-op` (uitsluitend kern-markeringen)
- `soort` + `soort-id` (gelijk aan `identificatiebegrip`)
- `herkomst` + (bij `afgeleid`) precies één van `afleidingsregel-id` of `uitvoer-van-regel-id`
- `aliases`, `tussenresultaat`, `kenmerken[]`
- `relaties.{is-een, heeft, leidt-tot}` — formaten in `schemas/begrip.schema.json` + `kaders/relaties.md`
- `voorbeelden[]` — minItems: 2 (schema), waarvan ≥ 1 grensgeval

Wijzig **niet**: `begrip-id`, `begripsnaam`, `markeringen`, `geldigheid-van`, `geldigheid-tot`, `status`, `vervangen-door`.

## Vervolg

Na afronden van `begrip-definitie`:

- Als `jas-klasse: afleidingsregel` → roep `begrip-regel` aan.
- Roep `begrip-scenario` aan voor scenario-koppeling (A3c).
- Roep `begrip-bron` aan voor secundaire bronnen (A3d).

In een orchestrator-context worden deze vervolg-skills automatisch sequentieel uitgevoerd.

## Valideren

```
tools/.venv/bin/python tools/validate_note.py --file begrippen/[slug].yaml
```

L1/L2-fouten herstellen vóór doorgaan; L3 rapporteren.

## Kwaliteitseisen (proces)

Procesregels die niet in `schemas/begrip.schema.json` of `kaders/definitie.md` zijn vastgelegd:

- Definitie uitsluitend gebaseerd op `markeringen[].tekst` — niet uit eigen kennis of wetstekst (projectconventie #1).
- Substitueerbaar in een zin (zie `kaders/definitie.md §Kern`).
- `status` blijft `concept` — statuswijziging is A4-taak.
- `markeringen[].bevestigd` blijft `false` tenzij door een domeinexpert juridisch gevalideerd.

Structurele vereisten (enums, minItems, if-then) worden door het schema afgedwongen — herhaal ze hier niet.
