---
description: Voer een volledige JAS-annotatie (v1.0.10) uit op een wetsbepaling en sla het rapport op als MD-bestand. Gebruik: /jas art. 25 IW 1990 of /jas art. 36 lid 4 IW 1990
context: fork
agent: general-purpose
---

# /jas — JAS-annotatie Wetsbepaling

**Artikel:** `$ARGUMENTS`

---

## BWB-mapping

Raadpleeg `.claude/skills/shared/bwb-mapping.md` voor de BWB-tabel en fallback-instructie.

---

## Uitvoering

Lees **`$CLAUDE_SKILL_DIR/PROTOCOL.md`** volledig en voer de stappen 1–15 strikt in volgorde uit.

Het visuele workflowoverzicht (Mermaid-diagram, parallelle aanroepen, conditionele stappen) staat in **`$CLAUDE_SKILL_DIR/WORKFLOW.md`** — raadpleeg dit als oriëntatie, niet als uitvoeringsprotocol.

---

## Sub-bestanden (geladen vanuit PROTOCOL.md)

| Bestand | Doel | Geladen in stap |
|---------|------|----------------|
| `../shared/bwb-mapping.md` | Canonieke BWB-tabel + fallback-instructie | Stap 2 |
| `kaders.md` | JAS v1.0.10 taxonomie en annotatieregels | Stap 1 |
| `begrippen-protocol.md` | Begrippen-check (inline, geen commit) | Stap 4 |
| `../begrip/template.md` | Begrip-noot template | Via begrippen-protocol |
| `kruisverwijzingen.md` | Kruisreferentie-extractieprotocol | Stap 6 |
| `rapportformat.md` | Rapportstructuur en kwaliteitseisen | Stap 11 |
