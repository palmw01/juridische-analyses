---
name: wa-annoteer
description: "Voert Activiteit 2 uit van de Wetsanalyse-methode: markeren (A2a), classificeren (A2b) en structuurdiagram (A2c). Gebruik voor het annoteren van artikelen of secties uit wetteksten."
---

# wa-annoteer — Activiteit 2: markeren en classificeren

Voert Activiteit 2 uit van de Wetsanalyse-methode: markeren (A2a) en classificeren (A2b). De output bestaat uit annotatie-noten in `annotaties/` en begrip-noten met uitsluitend gevulde frontmatter in `begrippen/`.

**Lees vóór elke annotatie-run eerst [kaders.md](references/kaders.md) volledig in.** De taxonomie (13 JAS-elementen), annotatieregels en kleurcodering zijn bindend.

## Triggervormen

1. **Artikel-index (Flow A)**: Voor de eerste aanraking van een artikel. Maakt een wetstekst-noot en een index-noot aan.
2. **Lid-annotatie (Flow B)**: Voor het inhoudelijk annoteren van één lid.
3. **Sectie-annotatie (Flow C)**: Voor bronnen zonder leden (bijv. beleidsregels).

## Markeren en Classificeren

Volg de regels in [kaders.md](references/kaders.md) voor:
- Welke tekstfragmenten te markeren (inclusief lidwoorden en verwijzingen).
- Welke van de 13 JAS-klassen toe te kennen.
- Hoe diagrammen op te stellen (A2c) met Mermaid.

## Outputstructuur

- **Wetteksten**: `wetteksten/[wet]/art[A].md`
- **Annotaties**: 
  - Index: `annotaties/[wet]/art[A].md` (uistluitend structuurdrager, GEEN annotatietabellen)
  - Lid: `annotaties/[wet]/art[A]-[L].md` (bevat annotatietabel en diagram)
- **Begrippen**: `begrippen/[slug].md` (alleen frontmatter, body leeg)

## Kwaliteitseisen

- Citeer wetstekst ALTIJD volledig en letterlijk.
- Gebruik de peildatum uit de MCP `versiedatum`.
- Zorg dat de index-noot "schoon" blijft (read-only principe).
- Volg de verplichte checklist-output na elke run (zie Claude SKILL.md bron voor details indien nodig).
