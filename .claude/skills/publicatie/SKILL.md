---
description: Sla een JAS-annotatierapport op, werk de index bij, maak of update de hub-note en commit naar git. Gebruik: /publiceer [bestandspad] [A] [W] [PD]
context: fork
agent: general-purpose
---

# /publiceer — Publicatie van een JAS-annotatie

**Argument:** `$ARGUMENTS` — verwacht: bestandspad rapport, artikelnummer `[A]`, wet `[W]`, peildatum `[PD]`

---

## Stap 1 — Frontmatter bepalen

Stel de frontmatter-velden vast op basis van de analyseresultaten:

**tags:**
- Altijd: `jas-annotatie`
- Wet-tag: lowercase afkorting — IW 1990 → `iw1990`; AWR → `awr`; Awb → `awb`; LI 2008 → `li2008`; UB IW 1990 → `ubiw1990`
- Artikel-tag: `art` + artikelnummer; `.` en `:` → `-`: art. 9 → `art9`; art. 4:86 → `art4-86`

**aliases:** `"Art. [A] [wet-afkorting] ([datum])"` — bijv. `"Art. 25 IW 1990 (2026-04-24)"`

**kruisreferenties:** gebruik `[kruisrefs]`-lijst uit de dataverwerving (lege array bij geen).

**Bestandsnaam-schema:**
```
analyses/jas-annotatie-art[A]-[afkorting wet]-[TIMESTAMP].md
```
Regels: geen spaties; "art. " → "art"; "lid " → "lid"; IW 1990 → "IW1990"; AWR → "AWR"; Awb → "Awb"; UB IW 1990 → "UBIW1990".

Voorbeelden:
- `analyses/jas-annotatie-art25-IW1990-2026-04-02_14-30-00.md`
- `analyses/jas-annotatie-art36lid4-IW1990-2026-04-02_14-30-00.md`

**Hub-pad:** `wetsartikelen/[wet-mapnaam]/art-[nummer].md`

`[wet-mapnaam]` — exacte mapnamen:

| Wet | Mapnaam |
|-----|---------|
| Invorderingswet 1990 | `IW1990` |
| Algemene wet bestuursrecht | `Awb` |
| Algemene wet inzake rijksbelastingen | `AWR` |
| Uitvoeringsbesluit IW 1990 | `UBIW1990` |

`[nummer]` = artikelnummer met `.` en `:` → `-`.

---

## Stap 2 — Timestamp en rapport opslaan

Haal timestamp op via `date +%Y-%m-%d_%H-%M-%S`. Voeg de volledige frontmatter toe aan het rapport en sla op als `analyses/jas-annotatie-art[A]-[afkorting wet]-[TIMESTAMP].md`.

---

## Stap 3 — Begrip-noten opslaan

Sla alle in de analysefase aangemaakte of bijgewerkte begrip-noten op (zie `begrip/begrippen-check.md`). Begrip-noten worden in dezelfde commit meegenomen.

---

## Stap 4 — INDEX.md bijwerken

Voeg het nieuwe rapport toe aan `analyses/INDEX.md` onder de juiste wet:
- Format: `- [Art. [A] (versie [PD])](./jas-annotatie-...) ([YYYY-MM-DD])`
- Nieuwe wet nog niet in index: voeg kop `## [Wet]` toe.
- Update `*Laatste update: YYYY-MM-DD*` onderaan.

---

## Stap 5 — Hub-note aanmaken of controleren ⚠️ VERPLICHT

Roep de Read-tool aan op `[hub-pad]`.

**Bestand bestaat niet:** maak aan met onderstaande structuur.

```markdown
---
type: wetsartikel-hub
artikel: Art. [A] [wet-afkorting]
wet: [volledige wetnaam (BWB-id)]
aliases:
  - "Art. [A] [wet-afkorting]"
tags:
  - wetsartikel
  - [wet-afkorting-lowercase]
  - art[nummer]
---

# Art. [A] — [volledige wetnaam]

## Alle annotaties

\`\`\`dataview
TABLE datum AS "Analysedatum", peildatum AS "Peildatum", jas-versie AS "JAS"
FROM "analyses"
WHERE type = "jas-annotatie" AND contains(artikel, "Art. [A]") AND contains(wet, "[deel van wetnaam]")
SORT datum DESC
\`\`\`

## Annotaties die naar dit artikel verwijzen

\`\`\`dataview
TABLE artikel, datum AS "Analysedatum"
FROM "analyses"
WHERE type = "jas-annotatie" AND contains(kruisreferenties, "Art. [A] [wet-afkorting]")
SORT datum DESC
\`\`\`
```

**Bestand bestaat al:** geen actie.

---

## Stap 6 — Git commit en push

```
git add analyses/jas-annotatie-art[A]-[afkorting wet]-[TIMESTAMP].md \
        analyses/INDEX.md \
        begrippen/ \
        [hub-pad indien nieuw]
git commit -m "jas: annotatie art. [A] [W] ([PD])"
git push
```

---

## Stap 7 — Retourneer bestandspad

Retourneer uitsluitend het opgeslagen bestandspad van het rapport.
