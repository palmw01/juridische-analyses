# Juridische wetsanalyse — Obsidian knowledge graph

Werkruimte voor gestructureerde wetsanalyse op het domein **invordering van rijksbelastingen**, aangedreven door Claude Code en een MCP-koppeling met [wetten.overheid.nl](https://wetten.overheid.nl).

Het primaire artefact is een **Obsidian knowledge graph**: atomaire entiteitsbestanden per annotatie, begrip en afleidingsregel, verbonden via wiki-links en doorzoekbaar via Dataview en Obsidian Graph View.

---

## Vault-structuur

```
annotaties/       ← lichte annotatie-noot per artikel (wetstekst + annotatietabel)
begrippen/        ← atomaire begrip-noten (definitie, voorbeelden, kenmerken, relaties)
regels/           ← atomaire afleidingsregel-noten (als-dan, voorbeeldreeksen)
wetsartikelen/    ← hub-notes per artikel (puur Dataview)
.claude/skills/   ← skill-documentatie voor Claude Code
```

---

## Gebruik

### Workflow

```
/annoteer art. [A] [W]      →  A2: wetstekst ophalen, markeren, classificeren
/begrip-alles art. [A] [W]  →  A3: definities, voorbeelden, relaties, afleidingsregels
```

Voorbeeld:
```
/annoteer art. 25 IW 1990
/begrip-alles art. 25 IW 1990
```

### Installatie

1. Kloon de `wetten-overheid-tools` repository naast deze repo.
2. De MCP-server is geconfigureerd in `.claude/settings.json`.

---

## Juridisch Analyseschema (JAS) v1.0.10

Wetsartikelen worden geannoteerd conform het **Juridisch Analyseschema v1.0.10** (MinBZK, 2024), gebaseerd op Wesley Newcomb Hohfeld (1913).

Het JAS maakt interpretatie- en preciseringskeuzes traceerbaar en vormt de basis voor ICT-implementatie van regelgeving.

- **Annotatiekaders**: [`.claude/skills/annoteer/kaders.md`](./.claude/skills/annoteer/kaders.md) — alle 13 JAS-elementen
- **Skill /annoteer**: [`.claude/skills/annoteer/SKILL.md`](./.claude/skills/annoteer/SKILL.md) — markeringen + classificaties (A2)
- **Skill /begrip**: [`.claude/skills/begrip/SKILL.md`](./.claude/skills/begrip/SKILL.md) — begrippen + afleidingsregels (A3)
- **BWB-mapping**: [`.claude/skills/wettenbank/bwb-mapping.md`](./.claude/skills/wettenbank/bwb-mapping.md)

---

## Obsidian Graph View

Alle entiteiten zijn voorzien van geneste tags zodat de graph filterbaar en kleurbaar is:

| Tag | Inhoud |
|-----|--------|
| `#begrip` | Alle begrip-noten |
| `#afleidingsregel` | Alle regel-noten |
| `#annotatie` | Alle annotatie-noten |
| `#jas/rechtssubject` | Begrippen met klasse rechtssubject |
| `#jas/rechtsbetrekking` | Begrippen met klasse rechtsbetrekking |
| `#wet/iw1990` | Alles wat de IW 1990 betreft |
| `#art/25` | Alles dat art. 25 betreft |

Stel in Obsidian Graph View → Groups kleuren in per tag conform kaders.md §Kleurcodering.
