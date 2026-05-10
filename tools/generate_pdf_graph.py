#!/usr/bin/env python3
"""
generate_pdf_graph.py — Genereer een visuele PDF-graaf van de begrippen-vault.
Gebruikt rdflib voor data en Graphviz (dot) voor de PDF-generatie.
"""

import sys
import subprocess
from pathlib import Path
from rdflib import Graph, Namespace

# JAS Kleuren (overeenkomstig met de ontologie)
JAS_KLEUREN = {
    "rechtsbetrekking": "#FF0000",
    "rechtssubject": "#4472C4",
    "rechtsobject": "#70AD47",
    "rechtsfeit": "#FFC000",
    "voorwaarde": "#7030A0",
    "afleidingsregel": "#00B0F0",
    "variabele": "#92D050",
    "parameter": "#FFD966",
    "tijdsaanduiding": "#F4B942",
    "plaatsaanduiding": "#9DC3E6",
}

def main():
    rdf_path = Path("kennisgraaf/begrippen.ttl")
    dot_path = Path("kennisgraaf/model_graph.dot")
    pdf_path = Path("kennisgraaf/juridisch_kennismodel.pdf")

    if not rdf_path.exists():
        print(f"Fout: {rdf_path} niet gevonden.")
        sys.exit(1)

    print(f"Laden van {rdf_path}...")
    g = Graph()
    g.parse(rdf_path, format="turtle")

    JAS = Namespace("http://regels.overheid.nl/jas/ontology#")
    SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

    dot_content = [
        'digraph G {',
        '  rankdir=LR;',
        '  node [fontname="Arial", shape=box, style="filled,rounded", color="#333333", fontcolor=white];',
        '  edge [fontname="Arial", fontsize=10, color="#666666"];',
        '  label="Juridisch Kennismodel — Inning & Invordering\\nGegenereerd door Gemini CLI";',
        '  labelloc="t";',
        '  fontsize=20;',
        ''
    ]

    # Knopen toevoegen
    for s in g.subjects(SKOS.prefLabel, None):
        label = str(g.value(s, SKOS.prefLabel))
        jas_klasse = str(g.value(s, JAS.jasKlasse))
        
        color = JAS_KLEUREN.get(jas_klasse, "#808080")
        fontcolor = "white" if jas_klasse in ["rechtsbetrekking", "rechtssubject", "voorwaarde"] else "black"
        
        node_id = f'"{s}"'
        dot_content.append(f'  {node_id} [label="{label}", fillcolor="{color}", fontcolor="{fontcolor}"];')

    dot_content.append('')

    # Relaties toevoegen
    # 1. Broader (Hiërarchie)
    for s, o in g.subject_objects(SKOS.broader):
        dot_content.append(f'  "{s}" -> "{o}" [label="is-een", style=dashed, arrowhead=empty];')

    # 2. Heeft
    for s, o in g.subject_objects(JAS.heeft):
        dot_content.append(f'  "{s}" -> "{o}" [label="heeft"];')

    # 3. LeidtTot (met regel-labels)
    for s, o in g.subject_objects(JAS.leidtTot):
        # Check of het doel-begrip (o) een afleidingsregel heeft
        regel_id = g.value(o, JAS.afleidingsregel)
        label = "leidt-tot"
        if regel_id:
            # Maak het regel-id iets korter voor de visuele weergave (bijv. alleen het einde)
            short_id = str(regel_id).split("-")[-1]
            label = f"leidt-tot\\n({str(regel_id)})"
        
        dot_content.append(f'  "{s}" -> "{o}" [label="{label}", color="#FF0000", penwidth=2, fontcolor="#CC0000", fontsize=9];')

    dot_content.append('}')

    # Schrijf DOT file
    dot_path.parent.mkdir(parents=True, exist_ok=True)
    dot_path.write_text("\n".join(dot_content))
    print(f"DOT bestand gegenereerd: {dot_path}")

    # Converteer naar PDF
    try:
        subprocess.run(["dot", "-Tpdf", str(dot_path), "-o", str(pdf_path)], check=True)
        print(f"PDF succesvol gegenereerd: {pdf_path}")
    except Exception as e:
        print(f"Fout bij PDF generatie: {e}")

if __name__ == "__main__":
    main()
