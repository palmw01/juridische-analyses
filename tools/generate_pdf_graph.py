#!/usr/bin/env python3
"""
generate_pdf_graph.py — Genereer een visuele PDF-graaf van de begrippen-vault.
Gebruikt rdflib voor data en Graphviz (dot) voor de PDF-generatie.
Kleuren worden geladen uit ontologie/jas-ontologie.yaml.
"""

import sys
import subprocess
from pathlib import Path
from rdflib import Graph, Namespace

import yaml

JAS_CODE_NAAR_NAAM = {
    "rb": "rechtsbetrekking",
    "rs": "rechtssubject",
    "ro": "rechtsobject",
    "rf": "rechtsfeit",
    "vw": "voorwaarde",
    "ar": "afleidingsregel",
    "va": "variabele",
    "pa": "parameter",
    "ta": "tijdsaanduiding",
    "pl": "plaatsaanduiding",
    "db": "delegatiebevoegdheid",
    "bd": "brondefinitie",
    "op": "operator",
}


def laad_jas_kleuren(ontologie_pad: Path) -> dict[str, str]:
    """Laad JAS-kleuren uit ontologie/jas-ontologie.yaml, geeft full-name → hex dict terug."""
    if not ontologie_pad.exists():
        return {}
    with ontologie_pad.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        return {}
    code_kleuren = data.get("classDef-kleuren") or {}
    result: dict[str, str] = {}
    for code, css in code_kleuren.items():
        full_name = JAS_CODE_NAAR_NAAM.get(code)
        if not full_name:
            continue
        hex_match = __import__("re").search(r"#([0-9A-Fa-f]{6})", css)
        if hex_match:
            result[full_name] = f"#{hex_match.group(1)}"
    return result

def main():
    script_dir = Path(__file__).resolve().parent
    vault_root = script_dir.parent
    ontologie_pad = vault_root / "ontologie" / "jas-ontologie.yaml"
    jas_kleuren = laad_jas_kleuren(ontologie_pad)

    rdf_path = Path("kennisgraaf/begrippen.ttl")
    dot_path = Path("kennisgraaf/model_graph.dot")
    pdf_path = Path("kennisgraaf/juridisch_kennismodel.pdf")

    if not rdf_path.exists():
        print(f"Fout: {rdf_path} niet gevonden.")
        print("  Run eerst 'make export-rdf' of 'make pdf-graph' (doet dit automatisch).")
        sys.exit(1)

    print(f"Laden van {rdf_path}...")
    g = Graph()
    g.parse(rdf_path, format="turtle")

    JAS = Namespace("http://regels.overheid.nl/jas/ontology#")
    SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

    # Regel prefix voor regel-nodes
    REGEL_NS = "urn:jas:regel:"

    dot_content = [
        'digraph G {',
        '  rankdir=LR;',
        '  node [fontname="Arial", shape=box, style="filled,rounded", color="#333333", fontcolor=white];',
        '  edge [fontname="Arial", fontsize=10, color="#666666"];',
        '  label="Juridisch Kennismodel — Inning & Invordering\\nGegenereerd door PDF graph";',
        '  labelloc="t";',
        '  fontsize=20;',
        ''
    ]

    # 1. Begrip-knopen (skos:Concept)
    for s in g.subjects(SKOS.prefLabel, None):
        if (s, None, RDF.type) not in g:
            continue
        types = list(g.objects(s, RDF.type))
        type_strs = [str(t) for t in types]
        if "http://www.w3.org/2004/02/skos/core#Concept" not in type_strs:
            if "http://www.w3.org/ns/prov#Entity" in type_strs:
                pass  # fall through — prov entities might be concepts too
        label = str(g.value(s, SKOS.prefLabel))
        jas_klasse = str(g.value(s, JAS.jasKlasse))
        
        color = jas_kleuren.get(jas_klasse, "#808080")
        fontcolor = "white" if jas_klasse in ["rechtsbetrekking", "rechtssubject", "voorwaarde"] else "black"
        
        node_id = f'"{s}"'
        dot_content.append(f'  {node_id} [label="{label}", fillcolor="{color}", fontcolor="{fontcolor}"];')

    # 2. Regel-knopen (jas:Afleidingsregel)
    for s in g.subjects(RDF.type, JAS.Afleidingsregel):
        label = str(g.value(s, SKOS.prefLabel) or str(s).split(":")[-1].replace("_", "-"))
        color = jas_kleuren.get("afleidingsregel", "#00B0F0")
        node_id = f'"{s}"'
        dot_content.append(f'  {node_id} [label="{label}", shape=hexagon, fillcolor="{color}", fontcolor="black"];')

    dot_content.append('')

    # Relaties toevoegen
    # 3. Broader (Hierarchie)
    for s, o in g.subject_objects(SKOS.broader):
        dot_content.append(f'  "{s}" -> "{o}" [label="is-een", style=dashed, arrowhead=empty];')

    # 4. Heeft
    for s, o in g.subject_objects(JAS.heeft):
        dot_content.append(f'  "{s}" -> "{o}" [label="heeft"];')

    # 5. LeidtTot (met regel-labels)
    for s, o in g.subject_objects(JAS.leidtTot):
        regel_id = g.value(o, JAS.afleidingsregel)
        label = "leidt-tot"
        if regel_id:
            label = f"leidt-tot\\n({str(regel_id)})"
        dot_content.append(f'  "{s}" -> "{o}" [label="{label}", color="#FF0000", penwidth=2, fontcolor="#CC0000", fontsize=9];')

    # 6. Regel-relaties: bepaalt (regel -> uitvoer)
    for s in g.subjects(RDF.type, JAS.Afleidingsregel):
        for o in g.objects(s, JAS.bepaalt):
            dot_content.append(f'  "{s}" -> "{o}" [label="bepaalt", style=dotted, color="#00B0F0", penwidth=1.5];')
        for o in g.objects(s, JAS.gebruikt):
            dot_content.append(f'  "{o}" -> "{s}" [label="invoer", style=dotted, color="#00B0F0", penwidth=1.5];')

    dot_content.append('}')

    # Schrijf DOT file
    dot_path.parent.mkdir(parents=True, exist_ok=True)
    dot_path.write_text("\n".join(dot_content))
    print(f"DOT bestand gegenereerd: {dot_path}")

    # Converteer naar PDF
    try:
        subprocess.run(["dot", "-Tpdf", str(dot_path), "-o", str(pdf_path)], check=True)
        print(f"PDF succesvol gegenereerd: {pdf_path}")
    except FileNotFoundError:
        print("Fout: Graphviz (dot) niet gevonden. Installeer met: sudo apt install graphviz")
    except Exception as e:
        print(f"Fout bij PDF generatie: {e}")

if __name__ == "__main__":
    main()
