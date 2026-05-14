#!/usr/bin/env python3
"""
query_rdf.py — Bevragen van het RDF-model met SPARQL.
Gebruikt rdflib om kennisgraaf/begrippen.ttl te laden en queries uit te voeren.

Gebruik:
    tools/.venv/bin/python tools/query_rdf.py
    tools/.venv/bin/python tools/query_rdf.py --query "SELECT * WHERE { ?s ?p ?o } LIMIT 10"
    tools/.venv/bin/python tools/query_rdf.py --query tools/queries/voorbeeld.rq
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BUILTIN_QUERIES: list[tuple[str, str]] = [
    ("Aantal begrippen per JAS-klasse", """
        PREFIX jas: <http://regels.overheid.nl/jas/ontology#>
        SELECT ?klasse (COUNT(?s) AS ?aantal)
        WHERE { ?s jas:jasKlasse ?klasse . }
        GROUP BY ?klasse
        ORDER BY DESC(?aantal)
    """),
    ("Hiërarchische relaties (SKOS Broader)", """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?smal ?label_smal ?breed ?label_breed
        WHERE {
            ?smal skos:broader ?breed .
            ?smal skos:prefLabel ?label_smal .
            ?breed skos:prefLabel ?label_breed .
        }
        ORDER BY ?label_breed
    """),
    ("Kwaliteitscheck: Begrippen zonder definitie", """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?begrip ?label
        WHERE {
            ?begrip a skos:Concept .
            ?begrip skos:prefLabel ?label .
            FILTER NOT EXISTS { ?begrip skos:definition ?def }
        }
    """),
    ("Begrippen met meerdere bronnen (Enrichment kandidaten)", """
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?label (COUNT(?bron) AS ?aantal_bronnen)
        WHERE {
            ?s skos:prefLabel ?label .
            ?s prov:wasDerivedFrom ?bron .
        }
        GROUP BY ?label
        HAVING (?aantal_bronnen > 1)
    """),
    ("Specifieke JAS-relaties (heeft/leidt-tot)", """
        PREFIX jas: <http://regels.overheid.nl/jas/ontology#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?van_label ?predikaat ?naar_label
        WHERE {
            VALUES ?predikaat { jas:heeft jas:leidtTot }
            ?van ?predikaat ?naar .
            ?van skos:prefLabel ?van_label .
            ?naar skos:prefLabel ?naar_label .
        }
    """),
    ("Projectvoortgang: Status van begrippen", """
        PREFIX jas: <http://regels.overheid.nl/jas/ontology#>
        SELECT ?status (COUNT(?s) AS ?aantal)
        WHERE { ?s jas:status ?status . }
        GROUP BY ?status
    """),
    ("Koppeling: Begrippen met een Afleidingsregel", """
        PREFIX jas: <http://regels.overheid.nl/jas/ontology#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?begrip_label ?regel_id
        WHERE {
            ?s jas:afleidingsregel ?regel_id .
            ?s skos:prefLabel ?begrip_label .
        }
    """),
    ("Kwaliteitscheck: Wees-begrippen (geen relaties)", """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX jas: <http://regels.overheid.nl/jas/ontology#>
        SELECT ?label
        WHERE {
            ?s a skos:Concept .
            ?s skos:prefLabel ?label .
            FILTER NOT EXISTS { ?s skos:broader ?o }
            FILTER NOT EXISTS { ?i skos:broader ?s }
            FILTER NOT EXISTS { ?s jas:heeft ?o2 }
            FILTER NOT EXISTS { ?i2 jas:heeft ?s }
            FILTER NOT EXISTS { ?s jas:leidtTot ?o3 }
            FILTER NOT EXISTS { ?i3 jas:leidtTot ?s }
        }
    """),
]

def run_query(g: Graph, label: str, sparql: str) -> None:
    print(f"\n=== {label} ===")
    try:
        results = g.query(sparql)
    except Exception as e:
        print(f"Fout: {e}")
        return
    if not results:
        print("Geen resultaten.")
        return

    vars = results.vars
    header = " | ".join(f"{str(v):<30}" for v in vars)
    print(header)
    print("-" * len(header))

    for row in results:
        print(" | ".join(f"{str(item):<30}" for item in row))

def laad_graph(rdf_path: Path) -> "Graph":
    from rdflib import Graph

    if not rdf_path.exists():
        print(f"Fout: {rdf_path} niet gevonden. Voer eerst make export-rdf uit.")
        sys.exit(1)

    print(f"Laden van {rdf_path}...", file=sys.stderr)
    g = Graph()
    g.parse(rdf_path, format="turtle")
    print(f"Graph geladen met {len(g)} triples.", file=sys.stderr)
    return g

def main() -> None:
    parser = argparse.ArgumentParser(description="Bevraag het RDF-model met SPARQL")
    parser.add_argument("--query", "-q", help="SPARQL query als tekst of .rq bestand")
    parser.add_argument("--list", "-l", action="store_true", help="Toon beschikbare ingebouwde queries")
    parser.add_argument("--rdf", default="kennisgraaf/begrippen.ttl", help="Pad naar RDF Turtle bestand")
    args = parser.parse_args()

    if args.list:
        print("Beschikbare ingebouwde queries:")
        for i, (label, _) in enumerate(BUILTIN_QUERIES, 1):
            print(f"  {i}. {label}")
        return

    if args.query:
        # Check of het een bestand is
        query_path = Path(args.query)
        if query_path.exists():
            sparql = query_path.read_text()
            label = f"Query uit: {query_path.name}"
        else:
            sparql = args.query
            label = "Eigen query"
        g = laad_graph(Path(args.rdf))
        run_query(g, label, sparql)
        return

    # Geen --query: draai alle ingebouwde queries
    g = laad_graph(Path(args.rdf))
    for label, sparql in BUILTIN_QUERIES:
        run_query(g, label, sparql)

if __name__ == "__main__":
    main()
