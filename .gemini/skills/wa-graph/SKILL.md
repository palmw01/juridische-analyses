---
name: wa-graph
description: "Exporteer de vault naar graph-model.json + GEXF/GraphML voor visualisatie. Gebruik 'Exporteer de graaf' of 'Update het graafmodel'."
---

# wa-graph — Graph-export

Exporteert de vault naar GEXF en GraphML formaten in de map `graaf/`.

## Scripts

De skill bevat Python scripts in de `scripts/` map om de export uit te voeren.

### 1. Modelgeneratie (`generate_model.py`)
Genereert `graph-model.json` op basis van de huidige vault structuur.
Gebruik wanneer er nieuwe JAS-klassen of node-types zijn toegevoegd.

### 2. Graph-export (`export_graph.py`)
Exporteert de nodes en edges naar `graaf/graph.gexf` en `graaf/graph.graphml`.

## Gebruik

Voer de scripts uit met de lokale Python omgeving.
Zorg dat de vault-root correct wordt meegegeven als argument `--vault-root`.

```bash
python3 scripts/generate_model.py --vault-root .
python3 scripts/export_graph.py --vault-root .
```

*Noot: De scripts verwachten mogelijk bepaalde dependencies. Indien deze ontbreken, installeer ze via pip (networkx, rdflib, etc.).*
