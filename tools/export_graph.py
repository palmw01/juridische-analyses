"""
Exporteert vault naar graph.gexf en graph.graphml.
Leest begrippen/*.yaml, regels/*.yaml, annotaties/**/*.json.

Gebruik:
    tools/.venv/bin/python tools/export_graph.py [--vault-root .]
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml
import networkx as nx

from jas_index_lib import bouw_jas_index

FALLBACK_KLEUR = "#CCCCCC"


def is_verborgen_pad(fp: Path, root: Path) -> bool:
    """True als een van de path-componenten (relatief t.o.v. root) begint met '.'."""
    try:
        return any(part.startswith(".") for part in fp.relative_to(root).parts)
    except ValueError:
        return False


def check_staleness(vault_root: Path, output_dir: Path) -> None:
    """Waarschuw als vault-bestanden nieuwer zijn dan de laatste GEXF-export."""
    gexf = output_dir / "graph.gexf"
    if not gexf.exists():
        return

    export_mtime = gexf.stat().st_mtime
    nieuwere = []

    for patroon in ["begrippen/*.yaml", "regels/*.yaml", "annotaties/**/*.json"]:
        for f in vault_root.glob(patroon):
            if is_verborgen_pad(f, vault_root):
                continue
            if f.stat().st_mtime > export_mtime:
                nieuwere.append(f.relative_to(vault_root))

    if nieuwere:
        print(
            f"  waarschuwing: {len(nieuwere)} vault-bestand(en) zijn nieuwer dan de laatste export "
            f"({gexf.name}). Voer /graph opnieuw uit om de graaf bij te werken.",
            file=sys.stderr,
        )
        for f in sorted(nieuwere)[:5]:
            print(f"    {f}", file=sys.stderr)
        if len(nieuwere) > 5:
            print(f"    … en {len(nieuwere) - 5} andere(n)", file=sys.stderr)


def lees_kleuren(vault_root: Path) -> dict[str, str]:
    """Laadt kleur per JAS-klasse uit .obsidian/graph.json."""
    graph_json = vault_root / ".obsidian" / "graph.json"
    if not graph_json.exists():
        return {}
    with graph_json.open() as f:
        data = json.load(f)
    kleur_map: dict[str, str] = {}
    for groep in data.get("colorGroups", []):
        query = groep.get("query", "")
        rgb_int = groep.get("color", {}).get("rgb")
        if not rgb_int:
            continue
        m = re.search(r"tag:#(?:jas/)?(\S+)", query)
        if m:
            kleur_map[m.group(1)] = f"#{rgb_int:06X}"
    return kleur_map


def build_graph(vault_root: Path) -> nx.MultiDiGraph:
    kleur_map = lees_kleuren(vault_root)
    jas_index = bouw_jas_index(vault_root)
    G = nx.MultiDiGraph()

    # --- Begrip-nodes ---
    begrippen_dir = vault_root / "begrippen"
    if begrippen_dir.exists():
        for yaml_file in sorted(begrippen_dir.glob("*.yaml")):
            with yaml_file.open(encoding="utf-8") as f:
                fm = yaml.safe_load(f)
            if not fm or not isinstance(fm, dict):
                continue

            node_id = fm.get("begrip-id") or yaml_file.stem
            label = fm.get("begripsnaam") or node_id
            jas_klasse = jas_index.get(node_id, "") or str(fm.get("jas-klasse") or "")

            attrs: dict = {
                "label": str(label),
                "node_type": "begrip",
                "soort": str(fm.get("soort") or ""),
                "herkomst": str(fm.get("herkomst") or ""),
                "status": str(fm.get("status") or ""),
                "jas_klasse": jas_klasse,
                "color": kleur_map.get(jas_klasse, FALLBACK_KLEUR),
            }
            if fm.get("geldigheid-van"):
                attrs["start"] = str(fm["geldigheid-van"])
            if fm.get("geldigheid-tot"):
                attrs["end"] = str(fm["geldigheid-tot"])

            G.add_node(node_id, **attrs)

    # --- Regel-nodes ---
    regels_dir = vault_root / "regels"
    if regels_dir.exists():
        for yaml_file in sorted(regels_dir.glob("*.yaml")):
            with yaml_file.open(encoding="utf-8") as f:
                fm = yaml.safe_load(f)
            if not fm or not isinstance(fm, dict):
                continue

            node_id = fm.get("regel-id") or yaml_file.stem
            label = fm.get("naam") or node_id
            jas_klasse = "afleidingsregel"

            attrs = {
                "label": str(label),
                "node_type": "afleidingsregel",
                "jas_klasse": jas_klasse,
                "soort": str(fm.get("soort") or ""),
                "bwb_id": str(fm.get("bwb-id") or ""),
                "artikel": str(fm.get("artikel") or ""),
                "color": kleur_map.get(jas_klasse, FALLBACK_KLEUR),
            }
            if fm.get("peildatum"):
                attrs["start"] = str(fm["peildatum"])

            G.add_node(node_id, **attrs)

    # --- Annotatie-nodes ---
    annotaties_dir = vault_root / "annotaties"
    if annotaties_dir.exists():
        for json_file in sorted(annotaties_dir.glob("**/*.json")):
            if is_verborgen_pad(json_file, annotaties_dir):
                continue
            with json_file.open(encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    continue

            node_id = data.get("annotatie-id") or str(json_file.relative_to(vault_root).with_suffix(""))
            artikel = data.get("artikel", "?")
            lid = data.get("lid", "")
            wet = data.get("wet", "")
            label = f"Art. {artikel}{(' lid ' + lid) if lid else ''} {wet}".strip()

            attrs = {
                "label": label,
                "node_type": "annotatie",
                "jas_klasse": "annotatie",
                "bwb_id": str(data.get("bwb-id") or ""),
                "wet": str(wet),
                "artikel": str(artikel),
                "color": kleur_map.get("annotatie", FALLBACK_KLEUR),
            }
            if data.get("peildatum"):
                attrs["start"] = str(data["peildatum"])

            G.add_node(node_id, **attrs)

    # --- Typed edges: begrip-relaties ---
    if begrippen_dir.exists():
        for yaml_file in sorted(begrippen_dir.glob("*.yaml")):
            with yaml_file.open(encoding="utf-8") as f:
                fm = yaml.safe_load(f)
            if not fm or not isinstance(fm, dict):
                continue

            van_id = fm.get("begrip-id") or yaml_file.stem
            if van_id not in G:
                continue

            relaties = fm.get("relaties") or {}

            for doel in relaties.get("is-een") or []:
                if isinstance(doel, str) and doel in G:
                    G.add_edge(van_id, doel, label="is-een", edge_type="is-een")

            for item in relaties.get("heeft") or []:
                doel = item.get("begrip-id") if isinstance(item, dict) else item
                if doel and doel in G:
                    G.add_edge(van_id, doel, label="heeft", edge_type="heeft")

            for item in relaties.get("leidt-tot") or []:
                if isinstance(item, dict):
                    doel = item.get("begrip-id")
                    relatie_soort = item.get("relatie-soort") or "leidt-tot"
                else:
                    doel = item
                    relatie_soort = "leidt-tot"
                if doel and doel in G:
                    G.add_edge(van_id, doel, label=relatie_soort, edge_type="leidt-tot")

            ar_id = fm.get("afleidingsregel-id")
            if ar_id and ar_id in G:
                G.add_edge(van_id, ar_id, label="afgeleid-via", edge_type="afgeleid-via")

    # --- Typed edges: annotatie → begrip (via annotatierijen) ---
    if annotaties_dir.exists():
        for json_file in sorted(annotaties_dir.glob("**/*.json")):
            if is_verborgen_pad(json_file, annotaties_dir):
                continue
            with json_file.open(encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    continue

            annotatie_id = data.get("annotatie-id") or str(json_file.relative_to(vault_root).with_suffix(""))
            if annotatie_id not in G:
                continue

            for rij in data.get("annotatierijen") or []:
                begrip_id = rij.get("begrip-id")
                if begrip_id and begrip_id in G:
                    G.add_edge(annotatie_id, begrip_id, label="markeert", edge_type="markeert")

            diagram = data.get("diagram") or {}
            knoop_map = {k["id"]: k.get("begrip-id") for k in diagram.get("knopen") or []}
            for kant in diagram.get("kanten") or []:
                van_begrip = knoop_map.get(kant.get("van"))
                naar_begrip = knoop_map.get(kant.get("naar"))
                label = kant.get("label") or "relatie"
                if van_begrip and naar_begrip and van_begrip in G and naar_begrip in G:
                    G.add_edge(van_begrip, naar_begrip, label=label, edge_type="diagram")

    # --- Edges: regel → begrip (invoer/uitvoer) ---
    if regels_dir.exists():
        for yaml_file in sorted(regels_dir.glob("*.yaml")):
            with yaml_file.open(encoding="utf-8") as f:
                fm = yaml.safe_load(f)
            if not fm or not isinstance(fm, dict):
                continue

            van_id = fm.get("regel-id") or yaml_file.stem
            if van_id not in G:
                continue

            for begrip_id in fm.get("uitvoer") or []:
                if begrip_id in G:
                    G.add_edge(van_id, begrip_id, label="bepaalt", edge_type="bepaalt")

            for begrip_id in fm.get("invoer") or []:
                if begrip_id in G:
                    G.add_edge(begrip_id, van_id, label="invoer-voor", edge_type="invoer-voor")

    return G


def main():
    parser = argparse.ArgumentParser(description="Vault → GraphML/GEXF export")
    parser.add_argument("--vault-root", default=".", help="Pad naar vault-root (default: .)")
    args = parser.parse_args()

    vault_root = Path(args.vault_root).resolve()

    print(f"Vault: {vault_root}")

    output_dir = vault_root / "kennisgraaf"
    output_dir.mkdir(exist_ok=True)

    check_staleness(vault_root, output_dir)

    G = build_graph(vault_root)

    print(f"Graaf: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    out_gexf = output_dir / "graph.gexf"
    out_graphml = output_dir / "graph.graphml"

    nx.write_gexf(G, out_gexf)
    print(f"Geschreven: {out_gexf}")

    nx.write_graphml(G, out_graphml)
    print(f"Geschreven: {out_graphml}")


if __name__ == "__main__":
    main()
