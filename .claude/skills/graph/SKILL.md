---
description: Exporteer de vault naar graph-model.json + GEXF/GraphML. Gebruik: /graph of /graph model
context: fork
agent: general-purpose
---

# /graph — Graph-export

**Argument:** `$ARGUMENTS`

Voer onderstaande stappen uit. De scripts staan in `$CLAUDE_SKILL_DIR`; output gaat naar `graaf/` in de vault-root.

---

## Stap 1 — Argument parsen

Controleer of `$ARGUMENTS` de waarde `model` bevat (hoofdletterongevoelig).

- **`model` aanwezig** → voer Stap 2 én Stap 3 uit.
- **`model` afwezig** → sla Stap 2 over; voer alleen Stap 3 uit.

---

## Stap 2 — Modelgeneratie (alleen bij `/graph model`)

Voer uit:

```
cd "$CLAUDE_SKILL_DIR" && .venv/bin/python generate_model.py --vault-root "$CLAUDE_PROJECT_DIR"
```

Extraheer uit de stdout:
- Aantal node-types
- Aantal edge-types
- Aantal JAS-klassen
- Pad van het geschreven modelbestand

Meld eventuele fouten aan de gebruiker en stop.

---

## Stap 3 — Graph-export

Voer uit:

```
cd "$CLAUDE_SKILL_DIR" && .venv/bin/python export_graph.py --vault-root "$CLAUDE_PROJECT_DIR"
```

Extraheer uit de stdout:
- Aantal nodes
- Aantal edges
- Geschreven bestanden (GEXF en/of GraphML)

Meld eventuele fouten of waarschuwingen aan de gebruiker.

---

## Stap 4 — Rapportage

Geef een korte samenvatting in deze vorm:

```
Graph-export voltooid.

Nodes:  [N]
Edges:  [E]
Output: graaf/graph.gexf, graaf/graph.graphml
```

Voeg bij `/graph model` ook toe:

```
Model bijgewerkt: [N] node-types, [E] edge-types, [K] JAS-klassen.
```
