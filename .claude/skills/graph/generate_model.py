"""
Genereert graph-model.json door de vault te inspecteren.
Leest begrippen/*.yaml, regels/*.yaml, annotaties/**/*.json.
Laadt kleuren uit .obsidian/graph.json en edge-types uit ontologie/jas-ontologie.yaml.

Gebruik:
    cd .claude/skills/graph/
    .venv/bin/python generate_model.py [--vault-root ../../..] [--out graph-model.json]
"""

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml

SKIP = {"index.md"}


def hex_van_rgb_int(rgb_int: int) -> str:
    return f"#{rgb_int:06X}"


def lees_obsidian_kleuren(vault_root: Path) -> dict[str, dict]:
    graph_json = vault_root / ".obsidian" / "graph.json"
    if not graph_json.exists():
        return {}
    with graph_json.open() as f:
        data = json.load(f)
    kleur_map: dict[str, dict] = {}
    for groep in data.get("colorGroups", []):
        query = groep.get("query", "")
        rgb_int = groep.get("color", {}).get("rgb")
        if not rgb_int:
            continue
        m = re.search(r"tag:#(?:jas/)?(\S+)", query)
        if m:
            klasse = m.group(1)
            kleur_map[klasse] = {
                "klasse": klasse,
                "kleur": hex_van_rgb_int(rgb_int),
                "rgb": rgb_int,
            }
    return kleur_map


def lees_jas_ontologie(vault_root: Path) -> list[dict]:
    """Laadt edge-types uit ontologie/jas-ontologie.yaml (relatiematrix)."""
    ontologie_path = vault_root / "ontologie" / "jas-ontologie.yaml"
    if not ontologie_path.exists():
        return []
    with ontologie_path.open(encoding="utf-8") as f:
        ontologie = yaml.safe_load(f)
    if not ontologie:
        return []
    relaties = ontologie.get("relatiematrix", [])
    if isinstance(relaties, dict):
        relaties = relaties.get("relaties", [])
    edge_types = []
    for rel in relaties:
        edge_types.append({
            "label": rel.get("predicaat") or rel.get("naam", ""),
            "van": rel.get("van", "begrip"),
            "naar": rel.get("naar", "begrip"),
            "frontmatter_veld": rel.get("yaml_veld", ""),
            "richting": "forward",
            "kardinaliteit": rel.get("kardinaliteit", "1:n"),
        })
    return edge_types


def detecteer_begrip_soorten(begrippen_dir: Path) -> dict[str, int]:
    """Verzamelt soort-verdeling voor rapportage."""
    soorten: dict[str, int] = defaultdict(int)
    for f in begrippen_dir.glob("*.yaml"):
        with f.open(encoding="utf-8") as fh:
            fm = yaml.safe_load(fh)
        if fm and isinstance(fm, dict):
            soorten[fm.get("soort", "onbekend")] += 1
    return dict(soorten)


def genereer_model(vault_root: Path) -> dict:
    kleur_map = lees_obsidian_kleuren(vault_root)
    ontologie_edges = lees_jas_ontologie(vault_root)

    # Node-types — hardcoded voor de drie bekende brontypen
    node_types = []

    begrippen_dir = vault_root / "begrippen"
    if begrippen_dir.exists() and any(begrippen_dir.glob("*.yaml")):
        node_types.append({
            "type": "begrip",
            "bron_map": "begrippen/",
            "bestand_extensie": ".yaml",
            "id_veld": "begrip-id",
            "label_veld": "begripsnaam",
            "klasse_veld": None,
            "jas_klasse_override": None,
            "attributen": ["soort", "herkomst", "status", "geldigheid-van", "geldigheid-tot"],
        })

    regels_dir = vault_root / "regels"
    if regels_dir.exists() and any(regels_dir.glob("*.yaml")):
        node_types.append({
            "type": "afleidingsregel",
            "bron_map": "regels/",
            "bestand_extensie": ".yaml",
            "id_veld": "regel-id",
            "label_veld": "naam",
            "klasse_veld": None,
            "jas_klasse_override": "afleidingsregel",
            "attributen": ["soort", "bwb-id", "artikel", "peildatum"],
        })

    annotaties_dir = vault_root / "annotaties"
    if annotaties_dir.exists() and any(annotaties_dir.glob("**/*.json")):
        node_types.append({
            "type": "annotatie",
            "bron_map": "annotaties/",
            "bestand_extensie": ".json",
            "id_veld": "annotatie-id",
            "label_veld": "artikel",
            "klasse_veld": None,
            "jas_klasse_override": "annotatie",
            "attributen": ["bwb-id", "wet", "artikel", "lid", "peildatum"],
        })

    # Edge-types: voorkeur uit JAS-ontologie; aangevuld met bekende vault-relaties
    bekende_edges = [
        {"label": "is-een", "van": "begrip", "naar": "begrip",
         "frontmatter_veld": "relaties.is-een", "richting": "forward", "kardinaliteit": "n:m"},
        {"label": "heeft", "van": "begrip", "naar": "begrip",
         "frontmatter_veld": "relaties.heeft", "richting": "forward", "kardinaliteit": "1:n"},
        {"label": "leidt-tot", "van": "begrip", "naar": "begrip",
         "frontmatter_veld": "relaties.leidt-tot", "richting": "forward", "kardinaliteit": "1:n"},
        {"label": "afgeleid-via", "van": "begrip", "naar": "afleidingsregel",
         "frontmatter_veld": "afleidingsregel-id", "richting": "forward", "kardinaliteit": "1:1"},
        {"label": "bepaalt", "van": "afleidingsregel", "naar": "begrip",
         "frontmatter_veld": "uitvoer", "richting": "forward", "kardinaliteit": "1:n"},
        {"label": "invoer-voor", "van": "begrip", "naar": "afleidingsregel",
         "frontmatter_veld": "invoer", "richting": "backward", "kardinaliteit": "1:n"},
        {"label": "markeert", "van": "annotatie", "naar": "begrip",
         "frontmatter_veld": "annotatierijen[].begrip-id", "richting": "forward", "kardinaliteit": "1:n"},
    ]
    alle_edges = ontologie_edges if ontologie_edges else bekende_edges

    jas_klassen = list(kleur_map.values()) if kleur_map else []

    # Rapportage-statistieken
    stats: dict = {}
    if begrippen_dir.exists():
        stats["begrip_soorten"] = detecteer_begrip_soorten(begrippen_dir)

    return {
        "versie": "2.0",
        "beschrijving": f"Gegenereerd model voor vault: {vault_root.name}",
        "node_types": node_types,
        "jas_klassen": jas_klassen,
        "edge_types": alle_edges,
        "statistieken": stats,
        "export": {
            "formaten": ["gexf", "graphml"],
            "output_map": "graaf/",
            "skip_bestanden": list(SKIP),
            "tijdsdimensie": {
                "actief": True,
                "start_veld": "geldigheid-van",
                "end_veld": "geldigheid-tot",
                "fallback_veld": "peildatum",
            },
        },
        "gephi": {
            "layout": "ForceAtlas2",
            "node_grootte_op": "degree",
            "edge_kleur_op": "label",
            "timeline_veld": "geldigheid-van",
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Vault → graph-model.json generator")
    parser.add_argument("--vault-root", default="../../..", help="Pad naar vault-root (default: ../../..)")
    parser.add_argument("--out", default="graph-model.json", help="Output-bestand (default: graph-model.json)")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    vault_root = (script_dir / args.vault_root).resolve()
    out_path = script_dir / args.out

    print(f"Vault: {vault_root}")

    model = genereer_model(vault_root)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(model, f, indent=2, ensure_ascii=False)

    print(f"Node-types:  {len(model['node_types'])}")
    print(f"Edge-types:  {len(model['edge_types'])}")
    print(f"JAS-klassen: {len(model['jas_klassen'])}")
    print(f"Geschreven:  {out_path}")


if __name__ == "__main__":
    main()
