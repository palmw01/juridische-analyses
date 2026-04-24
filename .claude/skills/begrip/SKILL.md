---
description: Documenteer of actualiseer een juridisch begrip in begrippen/. Gebruik: /begrip ontvanger IW 1990 of /begrip belastingschuldige
context: fork
agent: general-purpose
---

# /begrip — Begrip documenteren

**Term:** `$ARGUMENTS`

Voer onderstaande stappen uit. Het doel is een actuele, correcte begrip-noot in `begrippen/` die als Obsidian-knooppunt functioneert.

---

## Stap 1 — Argument parsen

Parseer `$ARGUMENTS`:
- **`[TERM]`**: de juridische term (bijv. "ontvanger", "belastingschuldige")
- **`[W]`** en **`[B]`**: wet en BWB-id, gebruik dezelfde mapping als de JAS-skill

Bestandspad: `begrippen/[TERM-slug].md` waarbij `[TERM-slug]` = term in lowercase, spaties → `-`, speciale tekens verwijderd (bijv. "belastingschuldige" → `begrippen/belastingschuldige.md`).

---

## Stap 2 — Controleer bestaande begrip-noot

Roep de Read-tool aan op `begrippen/[TERM-slug].md`.

**Als het bestand bestaat:**
- Lees de huidige `definitie`, `vindplaats` en `jas-element`
- Vergelijk met de aangeleverde of nieuw op te zoeken definitie
- Als er niets veranderd is: retourneer het bestandspad zonder aanpassing
- Als actualisering nodig is (nieuwe vindplaats, betere definitie, extra JAS-element): ga naar Stap 4 (actualiseren)

**Als het bestand niet bestaat:** ga naar Stap 3.

---

## Stap 3 — Definitie ophalen

Roep aan: `wettenbank_artikel(bwbId=[B], artikel=<begripsbepalings-artikel>)`

Zoek in de `leden`-array naar de omschrijving van `[TERM]`. Citeer letterlijk. Als de term niet in het begripsbepalings-artikel staat: zoek in het volledige artikel dat de term introduceert via `wettenbank_zoekterm(bwbId=[B], zoekterm="[TERM]")`.

Noteer:
- `[DEFINITIE]`: letterlijk geciteerde definitie
- `[VINDPLAATS]`: artikelnummer + lid + wet (bijv. "Art. 3 lid 1 IW 1990")
- `[JAS-ELEMENT]`: het primaire JAS-element van deze term (Rechtssubject / Rechtsobject / Brondefinitie / etc.)

---

## Stap 4 — Begrip-noot aanmaken of actualiseren

Sla op als `begrippen/[TERM-slug].md`. Haal de timestamp op via `date +%Y-%m-%d`. Gebruik de template uit `.claude/skills/begrip/template.md`.

---

## Stap 5 — Commit

```
git add begrippen/[TERM-slug].md
git commit -m "begrip: [TERM] ([W])"
git push
```

---

## Stap 6 — Retourneer bestandspad

Retourneer uitsluitend `begrippen/[TERM-slug].md`.
