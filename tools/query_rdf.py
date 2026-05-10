#!/usr/bin/env python3
"""
query_rdf.py — Bevragen van de RDF-vault met SPARQL.
Gebruikt rdflib om graaf/begrippen.ttl te laden en queries uit te voeren.
"""

import sys
from pathlib import Path
from rdflib import Graph

def run_query(g, label, sparql):
    print(f"\n=== {label} ===")
    results = g.query(sparql)
    if not results:
        print("Geen resultaten.")
        return
    
    # Print headers based on variable names in the query
    vars = results.vars
    header = " | ".join(f"{str(v):<30}" for v in vars)
    print(header)
    print("-" * len(header))
    
    for row in results:
        print(" | ".join(f"{str(item):<30}" for item in row))

def main():
    rdf_path = Path("graaf/begrippen.ttl")
    if not rdf_path.exists():
        print(f"Fout: {rdf_path} niet gevonden. Voer eerst tools/export_rdf.py uit.")
        sys.exit(1)

    print(f"Laden van {rdf_path}...")
    g = Graph()
    g.parse(rdf_path, format="turtle")
    print(f"Graph geladen met {len(g)} triples.")

    # 1. Overzicht per JAS-klasse
    q1 = """
    PREFIX jas: <http://regels.overheid.nl/jas/ontology#>
    SELECT ?klasse (COUNT(?s) AS ?aantal)
    WHERE {
        ?s jas:jasKlasse ?klasse .
    }
    GROUP BY ?klasse
    ORDER BY DESC(?aantal)
    """
    run_query(g, "Aantal begrippen per JAS-klasse", q1)

    # 2. Hiërarchie (Broader relaties)
    q2 = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?smal ?label_smal ?breed ?label_breed
    WHERE {
        ?smal skos:broader ?breed .
        ?smal skos:prefLabel ?label_smal .
        ?breed skos:prefLabel ?label_breed .
    }
    ORDER BY ?label_breed
    """
    run_query(g, "Hiërarchische relaties (SKOS Broader)", q2)

    # 3. Kwaliteitscheck: Ontbrekende definities
    q3 = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?begrip ?label
    WHERE {
        ?begrip a skos:Concept .
        ?begrip skos:prefLabel ?label .
        FILTER NOT EXISTS { ?begrip skos:definition ?def }
    }
    """
    run_query(g, "Kwaliteitscheck: Begrippen zonder definitie", q3)

    # 4. Bron herleidbaarheid
    q4 = """
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?label (COUNT(?bron) AS ?aantal_bronnen)
    WHERE {
        ?s skos:prefLabel ?label .
        ?s prov:wasDerivedFrom ?bron .
    }
    GROUP BY ?label
    HAVING (?aantal_bronnen > 1)
    """
    run_query(g, "Begrippen met meerdere bronnen (Enrichment kandidaten)", q4)

    # 5. JAS Relaties (heeft / leidtTot)
    q5 = """
    PREFIX jas: <http://regels.overheid.nl/jas/ontology#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?van_label ?predikaat ?naar_label
    WHERE {
        VALUES ?predikaat { jas:heeft jas:leidtTot }
        ?van ?predikaat ?naar .
        ?van skos:prefLabel ?van_label .
        ?naar skos:prefLabel ?naar_label .
    }
    """
    run_query(g, "Specifieke JAS-relaties (heeft/leidt-tot)", q5)

    # 6. Status distributie
    q6 = """
    PREFIX jas: <http://regels.overheid.nl/jas/ontology#>
    SELECT ?status (COUNT(?s) AS ?aantal)
    WHERE {
        ?s jas:status ?status .
    }
    GROUP BY ?status
    """
    run_query(g, "Projectvoortgang: Status van begrippen", q6)

    # 7. Koppeling Begrip -> Afleidingsregel
    q7 = """
    PREFIX jas: <http://regels.overheid.nl/jas/ontology#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?begrip_label ?regel_id
    WHERE {
        ?s jas:afleidingsregel ?regel_id .
        ?s skos:prefLabel ?begrip_label .
    }
    """
    run_query(g, "Koppeling: Begrippen met een Afleidingsregel", q7)

    # 8. Wees-begrippen (geen inkomende of uitgaande relaties)
    q8 = """
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
    """
    run_query(g, "Kwaliteitscheck: Wees-begrippen (geen relaties)", q8)

if __name__ == "__main__":
    main()
