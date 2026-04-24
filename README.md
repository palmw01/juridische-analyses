# Wetten Overheid — Juridische wetsanalyse met AI

Werkruimte voor gestructureerde wetsanalyse op het domein **invordering van rijksbelastingen**, aangedreven door Claude Code en een MCP-koppeling met [wetten.overheid.nl](https://wetten.overheid.nl).

---

## Inhoud
- `analyses/`: De verzameling van alle voltooide JAS-annotaties ([INDEX](./analyses/INDEX.md) · [Dashboard](./analyses/DASHBOARD.md)).
- `begrippen/`: Juridische begrippen met definities, voorbeelden, kenmerken, relaties en annotatiebronnen ([INDEX](./begrippen/INDEX.md)).
- `wetsartikelen/`: Hub-notes per wetsartikel met links naar alle annotaties.
- `.claude/skills/jas/`: Analyse-skill (Hoofdactiviteiten 2 + 3), rapportformat en structuurdiagram.
- `.claude/skills/wettenbank/`: Dataverwerving-skill — BWB-mapping, MCP-aanroepen, kruisreferentie-extractie.
- `.claude/skills/begrip/`: Begrip-skill — documenteren en verrijken van juridische begrippen.
- `.claude/skills/publicatie/`: Publicatie-skill — opslaan, index, hub-note, git.

## Installatie & Gebruik
Om deze omgeving te gebruiken met Claude Code of Gemini CLI, moet de `wettenbank-mcp` server lokaal beschikbaar zijn.

1. Kloon de `wetten-overheid-tools` repository naast deze repo.
2. Voeg de MCP-server toe aan je configuratie:
   ```json
   "mcpServers": {
     "wettenbank": {
       "command": "node",
       "args": ["/home/willardp/Documenten/Projecten/wetten-overheid-tools/wettenbank-mcp/dist/index.js"]
     }
   }
   ```
3. Gebruik het commando `/jas [artikel]` (bijv. `/jas art. 25 IW 1990`) om een nieuwe analyse te starten.
4. Gebruik `/begrip [term] [wet]` (bijv. `/begrip ontvanger IW 1990`) om een begrip te documenteren of bij te werken.

---

## Juridisch Analyseschema (JAS)

Wetsartikelen kunnen worden geannoteerd volgens het **Juridisch Analyseschema v1.0.10** (MinBZK, 2024), gebaseerd op de theorie van Wesley Newcomb Hohfeld.

Het JAS maakt interpretatie- en preciseringskeuzes traceerbaar en vormt de basis voor ICT-implementatie van regelgeving.

- **Annotatiekaders**: [`.claude/skills/jas/kaders.md`](./.claude/skills/jas/kaders.md) — alle 13 JAS-elementen met definities en herkenningsvragen
- **Workflow**: [`.claude/skills/jas/SKILL.md`](./.claude/skills/jas/SKILL.md) — Hoofdactiviteiten 2 (annotatetabel) en 3 (begrippen, afleidingsregels, bronnen)
- **Rapportformat + checklist**: [`.claude/skills/jas/rapport.md`](./.claude/skills/jas/rapport.md)
- **BWB-mapping**: [`.claude/skills/wettenbank/bwb-mapping.md`](./.claude/skills/wettenbank/bwb-mapping.md)
- **Voorbeeldannotaties**: zie [`analyses/`](./analyses/)