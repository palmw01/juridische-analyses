"""Tests voor tools/query_rdf.py — SPARQL-query uitvoering, graph laden, CLI."""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SKOS

from query_rdf import (
    run_query,
    laad_graph,
    main,
    BUILTIN_QUERIES,
)

SKOS_NS = Namespace("http://www.w3.org/2004/02/skos/core#")
JAS_NS = Namespace("http://regels.overheid.nl/jas/ontology#")


# ===== Hulpfunctie: maak minimale turtle =====

def maak_turtle(tmp_path: Path, content: str = "") -> Path:
    """Schrijft een Turtle-bestand en geeft het pad terug."""
    default_ttl = """
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix jas:  <http://regels.overheid.nl/jas/ontology#> .
@prefix begrip: <urn:jas:begrip:> .

begrip:test_begrip
    a skos:Concept ;
    skos:prefLabel "testbegrip"@nl ;
    skos:definition "een testdefinitie"@nl ;
    jas:jasKlasse "rechtssubject" .
"""
    ttl = tmp_path / "begrippen.ttl"
    ttl.write_text(content if content else default_ttl)
    return ttl


# ===== run_query =====

def test_run_query_retourneert_resultaten(capsys):
    g = Graph()
    begrip = URIRef("urn:jas:begrip:test")
    g.add((begrip, RDF.type, SKOS.Concept))
    g.add((begrip, SKOS.prefLabel, Literal("testbegrip", lang="nl")))

    sparql = "SELECT ?s WHERE { ?s a <http://www.w3.org/2004/02/skos/core#Concept> . }"
    run_query(g, "Testquery", sparql)
    out = capsys.readouterr().out
    assert "Testquery" in out


def test_run_query_print_header_en_scheidingsteken(capsys):
    g = Graph()
    begrip = URIRef("urn:jas:begrip:test")
    g.add((begrip, RDF.type, SKOS.Concept))
    g.add((begrip, SKOS.prefLabel, Literal("testbegrip", lang="nl")))

    sparql = "SELECT ?label WHERE { ?s skos:prefLabel ?label . }"
    run_query(g, "LabelQuery", sparql)
    out = capsys.readouterr().out
    assert "===" in out


def test_run_query_geen_resultaten(capsys):
    g = Graph()  # Lege graph
    sparql = "SELECT ?s WHERE { ?s a <http://www.w3.org/2004/02/skos/core#Concept> . }"
    run_query(g, "Leeg", sparql)
    out = capsys.readouterr().out
    assert "Geen resultaten" in out


def test_run_query_ongeldige_sparql(capsys):
    g = Graph()
    run_query(g, "Kapot", "GEEN GELDIGE SPARQL !!!")
    out = capsys.readouterr().out
    assert "Fout" in out


def test_run_query_count_aggregatie(capsys):
    g = Graph()
    for i in range(3):
        begrip = URIRef(f"urn:jas:begrip:test{i}")
        g.add((begrip, RDF.type, SKOS.Concept))
        g.add((begrip, URIRef("http://regels.overheid.nl/jas/ontology#jasKlasse"), Literal(f"klasse{i}")))

    sparql = """
        PREFIX jas: <http://regels.overheid.nl/jas/ontology#>
        SELECT ?klasse (COUNT(?s) AS ?aantal)
        WHERE { ?s jas:jasKlasse ?klasse . }
        GROUP BY ?klasse
        ORDER BY DESC(?aantal)
    """
    run_query(g, "Klassen", sparql)
    out = capsys.readouterr().out
    assert "Klassen" in out


def test_run_query_meerdere_kolommen(capsys):
    g = Graph()
    begrip = URIRef("urn:jas:begrip:test")
    g.add((begrip, RDF.type, SKOS.Concept))
    g.add((begrip, SKOS.prefLabel, Literal("label", lang="nl")))
    g.add((begrip, SKOS.definition, Literal("def", lang="nl")))

    sparql = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?label ?def
        WHERE { ?s skos:prefLabel ?label ; skos:definition ?def . }
    """
    run_query(g, "Meerdere kolommen", sparql)
    out = capsys.readouterr().out
    assert "|" in out


# ===== laad_graph =====

def test_laad_graph_bestand_bestaat(tmp_path):
    ttl = maak_turtle(tmp_path)
    g = laad_graph(ttl)
    assert isinstance(g, Graph)
    assert len(g) > 0


def test_laad_graph_bevat_verwachte_triples(tmp_path):
    ttl = maak_turtle(tmp_path)
    g = laad_graph(ttl)
    concepts = list(g.subjects(RDF.type, SKOS.Concept))
    assert len(concepts) >= 1


def test_laad_graph_bestand_bestaat_niet(tmp_path):
    ontbrekend = tmp_path / "bestaat_niet.ttl"
    with pytest.raises(SystemExit) as exc_info:
        laad_graph(ontbrekend)
    assert exc_info.value.code == 1


def test_laad_graph_print_pad_naar_stderr(tmp_path, capsys):
    ttl = maak_turtle(tmp_path)
    laad_graph(ttl)
    err = capsys.readouterr().err
    assert str(ttl) in err or "Laden" in err


def test_laad_graph_minimale_ttl(tmp_path):
    minimal = tmp_path / "minimal.ttl"
    minimal.write_text("@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n")
    g = laad_graph(minimal)
    assert isinstance(g, Graph)


def test_laad_graph_grootte_in_stderr(tmp_path, capsys):
    ttl = maak_turtle(tmp_path)
    laad_graph(ttl)
    err = capsys.readouterr().err
    assert "triples" in err.lower() or "Graph" in err


# ===== BUILTIN_QUERIES =====

def test_builtin_queries_is_lijst():
    assert isinstance(BUILTIN_QUERIES, list)
    assert len(BUILTIN_QUERIES) > 0


def test_builtin_queries_elke_entry_heeft_label_en_sparql():
    for label, sparql in BUILTIN_QUERIES:
        assert isinstance(label, str) and len(label) > 0
        assert isinstance(sparql, str) and "SELECT" in sparql.upper()


def test_builtin_queries_eerste_over_jas_klasse():
    label, sparql = BUILTIN_QUERIES[0]
    assert "klasse" in label.lower() or "jasKlasse" in sparql


# ===== main() =====

def test_main_list_flag(capsys):
    with patch.object(sys, "argv", ["query_rdf.py", "--list"]):
        main()
    out = capsys.readouterr().out
    assert "queries" in out.lower() or "1." in out


def test_main_list_toont_alle_queries(capsys):
    with patch.object(sys, "argv", ["query_rdf.py", "--list"]):
        main()
    out = capsys.readouterr().out
    for i, (label, _) in enumerate(BUILTIN_QUERIES, 1):
        assert str(i) in out


def test_main_query_inline(tmp_path, capsys):
    ttl = maak_turtle(tmp_path)
    sparql = "SELECT ?s WHERE { ?s a <http://www.w3.org/2004/02/skos/core#Concept> . }"
    with patch.object(sys, "argv", ["query_rdf.py", "--query", sparql, "--rdf", str(ttl)]):
        main()
    out = capsys.readouterr().out
    assert "Eigen query" in out or "query" in out.lower()


def test_main_query_uit_bestand(tmp_path, capsys):
    ttl = maak_turtle(tmp_path)
    rq = tmp_path / "test.rq"
    rq.write_text("SELECT ?s WHERE { ?s a <http://www.w3.org/2004/02/skos/core#Concept> . }")
    with patch.object(sys, "argv", ["query_rdf.py", "--query", str(rq), "--rdf", str(ttl)]):
        main()
    out = capsys.readouterr().out
    assert "test.rq" in out or "Query" in out


def test_main_alle_builtin_queries(tmp_path, capsys):
    ttl = maak_turtle(tmp_path)
    with patch.object(sys, "argv", ["query_rdf.py", "--rdf", str(ttl)]):
        main()
    out = capsys.readouterr().out
    # Alle queries zijn uitgevoerd → labels aanwezig in output
    for label, _ in BUILTIN_QUERIES:
        assert label in out


def test_main_rdf_ontbreekt_exit_1(tmp_path):
    ontbrekend = tmp_path / "bestaat_niet.ttl"
    with patch.object(sys, "argv", ["query_rdf.py", "--rdf", str(ontbrekend)]):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1


def test_main_query_bestand_zonder_sparql_extensie(tmp_path, capsys):
    """Niet-bestaand bestandspad als --query → behandeld als inline SPARQL string."""
    ttl = maak_turtle(tmp_path)
    niet_bestaand_pad = str(tmp_path / "niet_bestaand.rq")
    with patch.object(sys, "argv", ["query_rdf.py", "--query", niet_bestaand_pad, "--rdf", str(ttl)]):
        main()
    out = capsys.readouterr().out
    # Geen crash — wordt als inline query behandeld (fout of geen resultaten)
    assert "Eigen query" in out or "Fout" in out or "Geen resultaten" in out
