# Wetten Overheid — Juridische wetsanalyse met AI

Werkruimte voor gestructureerde wetsanalyse op het domein **invordering van rijksbelastingen**, aangedreven door Claude Code en een MCP-koppeling met [wetten.overheid.nl](https://wetten.overheid.nl).

---

## Inhoud
- `analyses/`: De verzameling van alle voltooide JAS-annotaties.
- `.claude/skills/jas/`: De volledige intelligentie en kaders van de JAS-skill.

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

---

## Juridisch Analyseschema (JAS)

Wetsartikelen kunnen worden geannoteerd volgens het **Juridisch Analyseschema v1.0.10** (MinBZK, 2024), gebaseerd op de theorie van Wesley Newcomb Hohfeld.

Het JAS maakt interpretatie- en preciseringskeuzes traceerbaar en vormt de basis voor ICT-implementatie van regelgeving.

- **Annotatiekaders**: [`.claude/skills/jas/kaders.md`](./.claude/skills/jas/kaders.md) — alle 13 JAS-elementen met definities en herkenningsvragen
- **Workflow**: [`.claude/skills/jas/SKILL.md`](./.claude/skills/jas/SKILL.md)
- **Rapportformat + checklist**: [`.claude/skills/jas/rapportformat.md`](./.claude/skills/jas/rapportformat.md)
- **Voorbeeldannotaties**: zie [`analyses/`](./analyses/)