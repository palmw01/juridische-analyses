---
name: annoteer-markeer
description: "A2a — markeert wetsformuleringen in één lid. Eerste van drie A2-sub-skills (markeer → classificeer → diagram). Gebruik: /annoteer art. [A] lid [L] [W]"
context: fork
agent: general-purpose
---

# /annoteer-markeer — A2a markeren

Markeert wetsformuleringen in één lid en initialiseert het annotatie-lid-bestand. Wordt opgevolgd door `annoteer-classificeer` (A2b) en `annoteer-diagram` (A2c).

> Lees vóór elke run: `.claude/skills/KADERS.md` en `.claude/skills/kaders/markeerregels.md`.

## Trigger

| Trigger | Flow |
|---------|------|
| `/annoteer art. [A] [W]` | **Flow A** — alleen index-JSON aanmaken |
| `/annoteer art. [A] lid [L] [W]` | **Flow B** — lid-annotatie aanmaken + begrip-stubs |
| `/annoteer sectie [ref] [W]` | **Flow C** — sectie-annotatie (bronnen zonder leden) |

## Invoer

- Wetbestand `bronnen/[B]/art[A].json` (anders eerst `/wettenbank art. [A] [W]`).
- Optioneel: `bronnen/[B]/art[A].kruisrefs.json` voor Flow A.
- Voor Flow B: lidnummer `[L]`.

## Werkwijze

De skill kent drie flows; kies de juiste op basis van de trigger. Slug-conventies staan onderaan.

### Flow A — artikel-index

1. Controleer bronbestand: `find bronnen/[B]/ -name "art[A].json"`. Ontbreekt → `/wettenbank art. [A] [W]`.
2. Controleer of `annotaties/[B]/art[A].json` al bestaat. Zo ja → meld "index-annotatie bestaat al" en stop.
3. Roep `stub_annotatie_index(bwb_id, wet, artikel, peildatum, structuurpositie, kruisreferenties)` uit `tools/jas_index_lib.py`. Peildatum uit het `versiedatum`-veld van het bronbestand; structuurpositie uit `pad`; kruisreferenties uit `bronnen/[B]/art[A].kruisrefs.json` indien aanwezig.
4. Schrijf met `schrijf_json(Path("annotaties/[B]/art[A].json"), data)`.
5. Valideer: `tools/.venv/bin/python tools/validate_note.py --file annotaties/[B]/art[A].json`.

### Flow B — lid-annotatie (markeerfase)

1. Controleer of `annotaties/[B]/art[A].json` bestaat. Nee → voer Flow A eerst uit.
2. Controleer of `annotaties/[B]/art[A]-lid[L].json` al bestaat. Zo ja → meld en stop.
3. Lees de wetstekst voor lid [L] uit `bronnen/[B]/art[A].json` (`leden[].tekst` waar `lid == "[L]"`).
4. Roep `stub_annotatie_lid(...)` aan met peildatum + structuurpositie overgenomen uit de index-JSON.
5. **Markeer** wetsformuleringen volgens `kaders/markeerregels.md`:
   - lidwoord meenemen, verwijzing meenemen
   - juiste markeer-omvang per klasse (variabele: smal; voorwaarde: zin/zinsdeel; afleidingsregel: hele als-dan)
   - markeringen mogen overlappen — één rij per klasse
   - **Actieve check:** is het lid als geheel een als-dan-constructie (rechtsgevolg dat intreedt zodra een voorwaarde is vervuld)? Zo ja → voeg altijd een afleidingsregel-rij toe voor de volledige zin incl. punt (conform `kaders/markeerregels.md` tabel rij Afleidingsregel).
6. Voor elke markering: roep `stub_annotatierij(rij_id, markering, jas_klasse=None, interpretatiemethode=None, begrip_id, toelichting_klasse="", signalering=None)` aan. `jas-klasse` en `interpretatiemethode` worden door `annoteer-classificeer` ingevuld; vul hier alleen een placeholder. `begrip-id` deterministisch: `[B]/art[A]/lid[L]/[slug]`.
7. Voeg de rijen toe aan `annotatierijen[]` en schrijf met `schrijf_json`. **Niet valideren** — de annotatie-lid-JSON is na deze stap schema-invalid (jas-klasse = null); L1-validatie pas na `annoteer-diagram` (stap A2c).
8. Voor elke unieke `begrip-id`: roep `stub_begrip(...)` aan en schrijf met `schrijf_yaml(Path("begrippen/[slug].yaml"), data)`. Als de YAML al bestaat: laat het bestaande bestand met rust en voeg een tweede markering toe (`m-002`, `bijdrage: context`) — meld dit in de hergebruiksrapportage.
9. Werk `leden-annotaties[]` bij in de index-JSON: voeg `"[B]/art[A]/lid[L]"` toe, gesorteerd.
10. Valideer de begrip-stubs: `tools/.venv/bin/python tools/validate_note.py --file begrippen/[slug].yaml` (één aanroep per nieuw aangemaakt stub).

### Flow C — sectie-annotatie

Identiek aan Flow B met:
- `annotatie-id`: `[B]/[slug]` (slug uit `pad`-veld; geen lid)
- `lid: ""` (leeg)
- Geen index-JSON; bestand opslaan als `annotaties/[B]/[slug].json`

### Slug-conventies

Stub-bestanden voor begrippen krijgen een slug afgeleid van de begripsnaam:
- lowercase, spaties → koppelteken, bijzondere tekens weglaten
- bestandsnaam = slug (geen wet-suffix); bv. `belastingaanslag.yaml`

Eenheid-slug uit het `pad`-veld:
| MCP-pad-segment | Slug |
|-----------------|------|
| `Artikel 9` | `art9` |
| `Artikel 2a` | `art2a` |
| `§ 1.1 De ontvanger` | `par1-1` |
| `Paragraaf 3` | `par3` |

## Output

- **Flow A**: `annotaties/[B]/art[A].json` — conform `schemas/annotatie-index.schema.json`.
- **Flow B**: `annotaties/[B]/art[A]-lid[L].json` (schema-invalid totdat A2c klaar is) + begrip-stubs in `begrippen/[slug].yaml` per uniek `begrip-id`. Update van `leden-annotaties[]` in de index-JSON.
- **Flow C**: `annotaties/[B]/[slug].json` + begrip-stubs.

## Vervolg

Roep daarna `annoteer-classificeer` aan om `jas-klasse`, `interpretatiemethode` en `toelichting-klasse` per rij in te vullen.

## Kwaliteitseisen (proces)

- Wetstekst altijd letterlijk geciteerd (geen parafrase).
- `markering.tekst` bevat lidwoord en verwijzingen.
- Peildatum uit `versiedatum` in bronbestand.
- Stub-begrippen worden door `annoteer-markeer` aangemaakt maar pas door `/begrip` ingevuld.

## Bronnen

- Schemas: `schemas/annotatie-index.schema.json`, `schemas/annotatie-lid.schema.json`, `schemas/begrip.schema.json`
- Kaders: `kaders/markeerregels.md`, `kaders/begripsnaam.md`
- Canon: Handleiding §3.4.2a
- Projectconventies: `kaders/projectconventies.md` #1, #9
