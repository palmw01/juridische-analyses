"""
Exporteert een Obsidian-vault naar graph.gexf en graph.graphml.
Volledig geconfigureerd via graph-model.json — geen hardcoded vault-specifieke waarden.

Gebruik:
    cd tools/
    .venv/bin/python export_graph.py [--vault-root ..] [--model graph-model.json]
"""

import argparse
import json
import re
import sys
from pathlib import Path

import frontmatter
import networkx as nx


def load_model(model_path: Path) -> dict:
    with model_path.open() as f:
        return json.load(f)


def extract_wikilinks(value, wikilink_re: re.Pattern) -> list[str]:
    if not value:
        return []
    targets = [value] if isinstance(value, str) else value
    result = []
    for t in targets:
        if isinstance(t, str):
            m = wikilink_re.search(t)
            if m:
                result.append(m.group(1))
    return result


def build_graph(vault_root: Path, model: dict) -> nx.DiGraph:
    export_cfg = model["export"]
    skip = set(export_cfg.get("skip_bestanden", []))
    wikilink_re = re.compile(export_cfg["wikilink_regex"])
    tijdsdim = export_cfg["tijdsdimensie"]

    kleur_map = {k["klasse"]: k["kleur"] for k in model["jas_klassen"]}
    G = nx.DiGraph()

    for node_def in model["node_types"]:
        bron_map = vault_root / node_def["bron_map"]
        if not bron_map.exists():
            continue

        for md_file in sorted(bron_map.glob("**/*.md")):
            if md_file.name in skip:
                continue

            post = frontmatter.load(md_file)
            fm = post.metadata
            node_id = str(md_file.relative_to(vault_root).with_suffix(""))

            jas_klasse = fm.get(node_def["klasse_veld"]) if node_def["klasse_veld"] else None
            jas_klasse = jas_klasse or node_def.get("jas_klasse_override") or ""
            label = fm.get(node_def["label_veld"]) or node_id

            attrs = {
                "label": str(label),
                "node_type": node_def["type"],
                "jas_klasse": jas_klasse,
                "color": kleur_map.get(jas_klasse, "#CCCCCC"),
            }

            for veld in node_def.get("attributen", []):
                waarde = fm.get(veld)
                if waarde is not None:
                    attrs[veld.replace("-", "_")] = str(waarde)

            if tijdsdim.get("actief"):
                start = fm.get(tijdsdim["start_veld"]) or fm.get(tijdsdim["fallback_veld"], "")
                end = fm.get(tijdsdim["end_veld"], "")
                if start:
                    attrs["start"] = str(start)
                if end:
                    attrs["end"] = str(end)

            G.add_node(node_id, **attrs)

    node_type_map = {nd["type"]: nd for nd in model["node_types"]}

    for edge_def in model["edge_types"]:
        veld = edge_def["frontmatter_veld"]
        label = edge_def["label"]
        van_type = edge_def["van"]

        node_def = node_type_map.get(van_type)
        if not node_def:
            continue

        bron_map = vault_root / node_def["bron_map"]
        if not bron_map.exists():
            continue

        for md_file in sorted(bron_map.glob("**/*.md")):
            if md_file.name in skip:
                continue

            post = frontmatter.load(md_file)
            fm = post.metadata
            van_id = str(md_file.relative_to(vault_root).with_suffix(""))

            if van_id not in G:
                continue

            doelen = extract_wikilinks(fm.get(veld), wikilink_re)
            for naar_id in doelen:
                if naar_id not in G:
                    print(f"  waarschuwing: onbekend doel '{naar_id}' in {md_file.name} ({veld})", file=sys.stderr)
                    continue
                G.add_edge(van_id, naar_id, label=label)

    return G


def main():
    parser = argparse.ArgumentParser(description="Vault → GraphML/GEXF export")
    parser.add_argument("--vault-root", default="..", help="Pad naar vault-root (default: ..)")
    parser.add_argument("--model", default="graph-model.json", help="Pad naar model-JSON (default: graph-model.json)")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    vault_root = (script_dir / args.vault_root).resolve()
    model_path = (script_dir / args.model).resolve()

    print(f"Vault: {vault_root}")
    print(f"Model: {model_path}")

    model = load_model(model_path)
    G = build_graph(vault_root, model)

    print(f"Graaf: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    output_dir = vault_root / "graaf"
    output_dir.mkdir(exist_ok=True)

    for formaat in model["export"].get("formaten", ["gexf"]):
        out = output_dir / f"graph.{formaat}"
        if formaat == "gexf":
            nx.write_gexf(G, out)
        elif formaat == "graphml":
            nx.write_graphml(G, out)
        else:
            print(f"  onbekend formaat '{formaat}', overgeslagen", file=sys.stderr)
            continue
        print(f"Geschreven: {out}")


if __name__ == "__main__":
    main()
