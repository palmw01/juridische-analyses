---
description: "A3a — vult begripsdefinitie (kern + contexten), soort, herkomst, relaties en voorbeelden in vanuit gevulde markeringen. Gebruik: /begrip [slug]"
context: fork
agent: general-purpose
---

# /begrip-definitie — A3a begripsdefinitie

Vult de inhoudelijke velden van een begrip-YAML in. Bronnen zijn uitsluitend `markeringen[].tekst` in het begrip-bestand zelf (vastgelegd door `annoteer-markeer`). De wettenbank wordt **niet** opnieuw aangeroepen.

> Lees vóór elke run: `.claude/skills/kaders/definitie.md`, `.claude/skills/kaders/begripsnaam.md`, `.claude/skills/kaders/relaties.md`.

## Triggers

| Trigger | Wanneer |
|---------|---------|
| `/begrip [slug]` | Eén begrip invullen |
| `/begrip-alles art. [A] [W]` | Alle begrip-YAML's van een artikel achtereenvolgens verwerken |

## Voorbereiding

1. **Idempotentie:** als `definitie.kern`, `soort`, `herkomst` allemaal gevuld zijn én `relaties` minstens één niet-lege lijst heeft: meld "begrip [slug] is al afgerond" en stop. Overschrijf nooit zonder bevestiging.
2. **Enrichment-queue:** lees `rapporten/enrichment-queue.json`. Als dit begrip een open beslissing heeft (`status: te-verrijken` zonder `beslissing`-veld): stop en meld; los eerst op.
3. **Annotaties terugvinden:** `grep -rl "[begrip-id]" annotaties/`. Lees elke gevonden annotatie-JSON. Uit de rij met dit `begrip-id`: vul `jas-klasse` en `toelichting-klasse` op het top-level van de YAML bij (uit annotatie naar begrip — niet uit eigen kennis).
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

```yaml
soort: [monetair-bedrag | percentage | tijdsduur | datum | booleaans | tekst | enumeratie | entiteit]
soort-id: false           # true als identificatiebegrip (BSN, aanslagnummer)
herkomst: [direct | afgeleid]
definitie:
  kern: "[substitueerbare tekst zonder eindpunt]"
  contexten: []           # of array van {markering-id, bijdrage, tekst, toelichting?}
definitie-versie: 1       # verhogen bij kernwijziging
definitie-gebaseerd-op:
- m-001                   # uitsluitend kern-markeringen
aliases:
- "[juridisch synoniem]"  # of leeg
identificatiebegrip: false  # altijd gelijk aan soort-id
afleidingsregel-id: null        # alleen bij jas-klasse: afleidingsregel (zie begrip-regel)
uitvoer-van-regel-id: null      # bij herkomst: afgeleid + jas-klasse ≠ afleidingsregel
tussenresultaat: false
relaties:
  is-een: [...]
  heeft:
  - begrip-id: ...
    kardinaliteit: "1:1"
  leidt-tot:
  - begrip-id: ...
    relatie-soort: causaal
    kardinaliteit: null
voorbeelden:
  - stelling: "..."
    waar: true
    toelichting: "..."
kenmerken:
  - "..."
```

Voorbeelden: minimaal 2 stellingen waarvan ≥ 1 grensgeval. Zie `kaders/definitie.md §Concrete voorbeelden`.

Wijzig **niet**: `begrip-id`, `begripsnaam`, `markeringen`, `geldigheid-van`, `geldigheid-tot`, `status`, `vervangen-door`.

## Vervolgen

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

## Kwaliteitseisen

- Definitie uitsluitend gebaseerd op `markeringen[].tekst` — niet uit eigen kennis of wetstekst.
- Substitueerbaar in een zin.
- Geen punt aan het einde van de kern.
- Minimaal één grensgeval bij `voorbeelden`.
- Bij `herkomst: afgeleid` is minimaal één `leidt-tot`-relatie verplicht (of een `heeft`-relatie naar invoerbegrippen).
- `status` blijft `concept` — statuswijziging is A4-taak.
- `markeringen[].bevestigd` blijft `false` tenzij door een domeinexpert juridisch gevalideerd.
