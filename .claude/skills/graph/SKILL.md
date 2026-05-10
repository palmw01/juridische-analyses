---
description: "Exporteer de vault naar graph-model.json + GEXF/GraphML. Gebruik: /graph of /graph model"
context: fork
agent: general-purpose
---

# /graph — Graph-export

## Triggervormen

| Trigger | Wanneer gebruiken |
|---------|-------------------|
| `/graph` | Exporteer de vault naar GEXF + GraphML (bestaand graph-model.json hergebruiken) |
| `/graph model` | Hergenereeer graph-model.json en exporteer daarna |

**Argument:** `$ARGUMENTS`

De scripts lezen `begrippen/*.yaml`, `regels/*.yaml` en `annotaties/**/*.json` — geen Markdown meer.
Output gaat naar `kennisgraaf/` in de vault-root.

---

## Stap 1 — Argument parsen

Controleer of `$ARGUMENTS` de waarde `model` bevat (hoofdletterongevoelig).

- **`model` aanwezig** → voer Stap 2 én Stap 3 uit.
- **`model` afwezig** → sla Stap 2 over; voer alleen Stap 3 uit.

---

## Stap 2 — Modelgeneratie (alleen bij `/graph model`)

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

```
cd "$CLAUDE_SKILL_DIR" && .venv/bin/python export_graph.py --vault-root "$CLAUDE_PROJECT_DIR"
```

Extraheer uit de stdout:
- Aantal nodes
- Aantal edges
- Geschreven bestanden (GEXF en/of GraphML)

**Staleness-waarschuwing (stderr):** Als vault-bestanden nieuwer zijn dan de bestaande GEXF, print het script een waarschuwing. Meld dit aan de gebruiker.

Meld eventuele andere fouten of waarschuwingen aan de gebruiker.

---

## Stap 4 — Rapportage

```
Graph-export voltooid.

Nodes:  [N]
Edges:  [E]
Output: kennisgraaf/graph.gexf, kennisgraaf/graph.graphml
```

Voeg bij `/graph model` ook toe:

```
Model bijgewerkt: [N] node-types, [E] edge-types, [K] JAS-klassen.
```
