"""
Genereert graph-model.json door de vault te inspecteren.
Leest kleuren uit .obsidian/graph.json en ontdekt node-types,
edge-types en attributen uit de frontmatter van vault-bestanden.

Gebruik:
    cd tools/
    .venv/bin/python generate_model.py [--vault-root ..] [--out graph-model.json]
"""

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import frontmatter

SKIP = {"template.md", "index.md"}
WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")
IGNORE_VELDEN = {"type", "tags", "aliases", "cssclasses"}


def hex_van_rgb_int(rgb_int: int) -> str:
    return f"#{rgb_int:06X}"


def lees_obsidian_kleuren(vault_root: Path) -> dict[str, dict]:
    """Leest tag → {kleur, rgb} uit .obsidian/graph.json."""
    graph_json = vault_root / ".obsidian" / "graph.json"
    if not graph_json.exists():
        return {}

    with graph_json.open() as f:
        data = json.load(f)

    kleur_map = {}
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


def bevat_wikilink(waarde) -> bool:
    if isinstance(waarde, str):
        return bool(WIKILINK.search(waarde))
    if isinstance(waarde, list):
        return any(isinstance(v, str) and WIKILINK.search(v) for v in waarde)
    return False


def wikilink_naar_pad(waarde) -> str | None:
    """Geeft het mappad terug uit de eerste wikilink, bijv. 'begrippen'."""
    targets = [waarde] if isinstance(waarde, str) else (waarde or [])
    for t in targets:
        if isinstance(t, str):
            m = WIKILINK.search(t)
            if m:
                pad = m.group(1)
                if "/" in pad:
                    return pad.split("/")[0]
    return None


def detecteer_label_veld(frontmatters: list[dict], type_naam: str) -> str:
    """Kiest het meest geschikte label-veld voor een node-type."""
    kandidaten = ["naam", "begripsnaam", "regel-id", "artikel", "titel", type_naam]
    tellingen = defaultdict(int)

    for fm in frontmatters:
        for veld, waarde in fm.items():
            if veld in IGNORE_VELDEN:
                continue
            if isinstance(waarde, str) and waarde.strip():
                tellingen[veld] += 1

    for kandidaat in kandidaten:
        if kandidaat in tellingen:
            return kandidaat

    velden_zonder_links = [
        (v, t) for v, t in tellingen.items()
        if not any(bevat_wikilink(fm.get(v)) for fm in frontmatters)
    ]
    if velden_zonder_links:
        return max(velden_zonder_links, key=lambda x: x[1])[0]

    return "type"


def detecteer_klasse_veld(frontmatters: list[dict]) -> str | None:
    """Zoekt een veld met 'klasse' in de naam."""
    for fm in frontmatters:
        for veld in fm:
            if "klasse" in veld.lower() and veld not in IGNORE_VELDEN:
                return veld
    return None


def detecteer_id_veld(frontmatters: list[dict], md_bestanden: list[Path]) -> str | None:
    """Detecteert een veld waarvan de waarde overeenkomt met de bestandsnaam-stem."""
    if not frontmatters:
        return None
    stems = [md.stem for md in md_bestanden]
    kandidaten: dict[str, int] = defaultdict(int)
    for fm, stem in zip(frontmatters, stems):
        for veld, waarde in fm.items():
            if veld in IGNORE_VELDEN or bevat_wikilink(waarde):
                continue
            if isinstance(waarde, str) and waarde == stem:
                kandidaten[veld] += 1
    if not kandidaten:
        return None
    beste = max(kandidaten, key=lambda v: kandidaten[v])
    if kandidaten[beste] == len(frontmatters):
        return beste
    return None


def detecteer_attributen(frontmatters: list[dict]) -> list[str]:
    """Verzamelt alle frontmatter-velden die geen wikilinks bevatten."""
    alle_velden: dict[str, int] = defaultdict(int)
    for fm in frontmatters:
        for veld, waarde in fm.items():
            if veld not in IGNORE_VELDEN and not bevat_wikilink(waarde):
                if not isinstance(waarde, list) or all(
                    not (isinstance(v, str) and WIKILINK.search(v)) for v in waarde
                ):
                    alle_velden[veld] += 1
    return sorted(alle_velden, key=lambda v: -alle_velden[v])


def detecteer_edge_types(
    frontmatters: list[dict],
    van_type: str,
    map_naar_type: dict[str, str],
) -> list[dict]:
    """Detecteert edge-types op basis van wikilink-velden in frontmatter."""
    veld_doelen: dict[str, set] = defaultdict(set)

    for fm in frontmatters:
        for veld, waarde in fm.items():
            if veld in IGNORE_VELDEN:
                continue
            if bevat_wikilink(waarde):
                pad = wikilink_naar_pad(waarde)
                if pad:
                    veld_doelen[veld].add(pad)

    edges = []
    for veld, paden in veld_doelen.items():
        for pad in paden:
            naar_type = map_naar_type.get(pad)
            if not naar_type:
                continue
            edges.append({
                "label": veld,
                "van": van_type,
                "naar": naar_type,
                "frontmatter_veld": veld,
                "richting": "forward",
                "kardinaliteit": "1:n",
            })
    return edges


def genereer_model(vault_root: Path) -> dict:
    kleur_map = lees_obsidian_kleuren(vault_root)

    node_types = []
    alle_frontmatters: dict[str, list[dict]] = {}
    map_naar_type: dict[str, str] = {}

    for submap in sorted(vault_root.iterdir()):
        if not submap.is_dir() or submap.name.startswith("."):
            continue
        md_bestanden = [f for f in sorted(submap.glob("**/*.md")) if f.name not in SKIP]
        if not md_bestanden:
            continue

        type_telling: dict[str, int] = defaultdict(int)
        fms = []
        for md in md_bestanden:
            post = frontmatter.load(md)
            fm = post.metadata
            fms.append(fm)
            type_naam = fm.get("type", "")
            if type_naam:
                type_telling[type_naam] += 1

        if not type_telling:
            continue

        dominant_type = max(type_telling, key=lambda t: type_telling[t])
        map_naam = submap.name
        map_naar_type[map_naam] = dominant_type
        alle_frontmatters[dominant_type] = fms

        label_veld = detecteer_label_veld(fms, dominant_type)
        klasse_veld = detecteer_klasse_veld(fms)
        id_veld = detecteer_id_veld(fms, md_bestanden)
        attributen = detecteer_attributen(fms)

        jas_override = None if klasse_veld else dominant_type

        node_def = {
            "type": dominant_type,
            "bron_map": f"{map_naam}/",
            "frontmatter_type": dominant_type,
            "label_veld": label_veld,
            "klasse_veld": klasse_veld,
            "id_veld": id_veld,
            "attributen": attributen,
        }
        if jas_override is not None:
            node_def["jas_klasse_override"] = jas_override

        node_types.append(node_def)

    alle_edges = []
    voor_dubbelen: set[tuple] = set()

    for node_def in node_types:
        van_type = node_def["type"]
        fms = alle_frontmatters.get(van_type, [])
        edges = detecteer_edge_types(fms, van_type, map_naar_type)
        for edge in edges:
            sleutel = (edge["van"], edge["naar"], edge["label"])
            if sleutel not in voor_dubbelen:
                voor_dubbelen.add(sleutel)
                alle_edges.append(edge)

    jas_klassen = list(kleur_map.values()) if kleur_map else []

    return {
        "versie": "1.0",
        "beschrijving": f"Gegenereerd model voor vault: {vault_root.name}",
        "node_types": node_types,
        "jas_klassen": jas_klassen,
        "edge_types": alle_edges,
        "export": {
            "formaten": ["gexf", "graphml"],
            "output_map": "tools/",
            "skip_bestanden": list(SKIP),
            "tijdsdimensie": {
                "actief": True,
                "start_veld": "geldigheid-van",
                "end_veld": "geldigheid-tot",
                "fallback_veld": "peildatum",
            },
            "wikilink_regex": "\\[\\[([^\\]]+)\\]\\]",
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
    parser.add_argument("--vault-root", default="..", help="Pad naar vault-root (default: ..)")
    parser.add_argument("--out", default="graph-model.json", help="Output-bestand (default: graph-model.json)")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    vault_root = (script_dir / args.vault_root).resolve()
    out_path = script_dir / args.out

    print(f"Vault: {vault_root}")

    model = genereer_model(vault_root)

    with out_path.open("w") as f:
        json.dump(model, f, indent=2, ensure_ascii=False)

    print(f"Node-types:  {len(model['node_types'])}")
    print(f"Edge-types:  {len(model['edge_types'])}")
    print(f"JAS-klassen: {len(model['jas_klassen'])}")
    print(f"Geschreven:  {out_path}")


if __name__ == "__main__":
    main()
