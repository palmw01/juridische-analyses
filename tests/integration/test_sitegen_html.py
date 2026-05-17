"""Tests voor sitegen/html.py en sitegen/mermaid.py — pure functies."""
from pathlib import Path

import pytest

from sitegen.html import (
    gen_nav,
    pagina,
    schrijf_html,
    breadcrumb,
    jas_tag,
    status_badge,
    format_ann_title,
    format_structuurpositie,
)
from sitegen.mermaid import diagram_tekst_fallback, diagram_to_mermaid


# ===== gen_nav =====

def test_gen_nav_bevat_alle_links():
    html = gen_nav()
    for label in ("Dashboard", "Begrippen", "Annotaties", "Regels", "SPARQL", "Zoeken"):
        assert label in html


def test_gen_nav_active_class_gezet():
    html = gen_nav(active="begrippen")
    assert 'aria-current="page"' in html
    assert "Begrippen" in html


def test_gen_nav_pad_prefix():
    html = gen_nav(p="../")
    assert "../index.html" in html
    assert "../begrippen.html" in html


def test_gen_nav_geen_active_geen_aria_current():
    html = gen_nav(active="")
    assert 'aria-current="page"' not in html


# ===== pagina =====

def test_pagina_bevat_title():
    html = pagina("Mijn Titel", "<p>inhoud</p>")
    assert "Mijn Titel" in html


def test_pagina_escapet_title():
    html = pagina("<script>alert(1)</script>", "body")
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_pagina_bevat_body():
    html = pagina("Titel", "<p>Unieke inhoud xyz</p>")
    assert "<p>Unieke inhoud xyz</p>" in html


def test_pagina_bevat_nav():
    html = pagina("T", "b")
    assert "<nav" in html


def test_pagina_met_extra_scripts():
    html = pagina("T", "b", extra_scripts='<script src="custom.js"></script>')
    assert 'custom.js' in html


def test_pagina_met_pad_prefix():
    html = pagina("T", "b", p="../")
    assert "../css/style.css" in html


# ===== schrijf_html =====

def test_schrijf_html_maakt_bestand_aan(tmp_path):
    schrijf_html(tmp_path, "test/pagina.html", "Titel", "<p>inhoud</p>")
    bestand = tmp_path / "test" / "pagina.html"
    assert bestand.exists()
    assert "<p>inhoud</p>" in bestand.read_text()


def test_schrijf_html_maakt_parent_dirs(tmp_path):
    schrijf_html(tmp_path, "diep/pad/test.html", "T", "b")
    assert (tmp_path / "diep" / "pad" / "test.html").exists()


# ===== breadcrumb =====

def test_breadcrumb_bevat_crumbs():
    html = breadcrumb("../", "Actief", [("../index.html", "Home"), ("../begrippen.html", "Begrippen")])
    assert "Home" in html
    assert "Begrippen" in html
    assert "Actief" in html


def test_breadcrumb_escapet_actief():
    html = breadcrumb("../", "<XSS>", [])
    assert "<XSS>" not in html
    assert "&lt;XSS&gt;" in html


def test_breadcrumb_bevat_nav():
    html = breadcrumb("../", "item", [])
    assert "<nav" in html
    assert "<ol" in html


# ===== jas_tag =====

def test_jas_tag_bekende_klasse_heeft_kleur():
    html = jas_tag("rechtssubject")
    assert "rechtssubject" in html
    assert "background:" in html
    assert "<span" in html


def test_jas_tag_onbekende_klasse_heeft_fallback_kleur():
    html = jas_tag("niet-bestaande-klasse")
    assert "background:#888" in html


def test_jas_tag_escapet_klasse():
    html = jas_tag("<script>")
    assert "<script>" not in html


# ===== status_badge =====

def test_status_badge_concept():
    html = status_badge("concept")
    assert "concept" in html
    assert "badge" in html


def test_status_badge_definitief():
    html = status_badge("definitief")
    assert "badge-definitief" in html


def test_status_badge_leeg_geeft_onbekend():
    html = status_badge("")
    assert "onbekend" in html


def test_status_badge_none_geeft_concept_class():
    html = status_badge(None)
    assert "badge-concept" in html


# ===== format_ann_title =====

def test_format_ann_title_normale_wet():
    a = {"wet": "Invorderingswet 1990", "artikel": "9", "lid": "1"}
    result = format_ann_title(a)
    assert "art. 9" in result
    assert "lid 1" in result


def test_format_ann_title_zonder_lid():
    a = {"wet": "Invorderingswet 1990", "artikel": "9", "lid": ""}
    result = format_ann_title(a)
    assert "art. 9" in result
    assert "lid" not in result


def test_format_ann_title_leidraad_met_lid():
    a = {"wet": "LI Leidraad", "artikel": "12", "lid": "3"}
    result = format_ann_title(a)
    assert "§ 3" in result


def test_format_ann_title_leidraad_zonder_lid():
    a = {"wet": "LI Leidraad", "artikel": "12", "lid": ""}
    result = format_ann_title(a)
    assert "§ 12" in result


# ===== format_structuurpositie =====

def test_format_structuurpositie_normaal():
    a = {"wet": "Invorderingswet 1990", "structuurpositie": "Hoofdstuk 1 > Artikel 9"}
    result = format_structuurpositie(a)
    assert "Hoofdstuk 1" in result


def test_format_structuurpositie_leidraad_vervangt_lid():
    a = {"wet": "LI Leidraad", "structuurpositie": "Lid 12.3"}
    result = format_structuurpositie(a)
    assert "§ 12.3" in result


def test_format_structuurpositie_leeg():
    a = {"wet": "Invorderingswet 1990", "structuurpositie": ""}
    assert format_structuurpositie(a) == ""


# ===== diagram_to_mermaid =====

def test_diagram_to_mermaid_leeg_geeft_leeg():
    assert diagram_to_mermaid({}) == ""
    assert diagram_to_mermaid(None) == ""


def test_diagram_to_mermaid_geen_knopen_geeft_leeg():
    assert diagram_to_mermaid({"knopen": [], "kanten": []}) == ""


def test_diagram_to_mermaid_eenvoudig_diagram():
    diagram = {
        "knopen": [{"id": "k1", "jas-klasse": "rechtssubject", "label": "belastingschuldige"}],
        "kanten": [],
    }
    result = diagram_to_mermaid(diagram)
    assert "graph LR" in result
    assert "k1" in result
    assert "belastingschuldige" in result


def test_diagram_to_mermaid_kant_met_label():
    diagram = {
        "knopen": [
            {"id": "k1", "jas-klasse": "rechtssubject", "label": "persoon"},
            {"id": "k2", "jas-klasse": "variabele", "label": "bedrag"},
        ],
        "kanten": [{"van": "k1", "naar": "k2", "label": "heeft"}],
    }
    result = diagram_to_mermaid(diagram)
    assert "-->|heeft|" in result


def test_diagram_to_mermaid_kant_zonder_label():
    diagram = {
        "knopen": [
            {"id": "k1", "jas-klasse": "rechtssubject", "label": "A"},
            {"id": "k2", "jas-klasse": "variabele", "label": "B"},
        ],
        "kanten": [{"van": "k1", "naar": "k2"}],
    }
    result = diagram_to_mermaid(diagram)
    assert " --- " in result


def test_diagram_to_mermaid_label_met_spatie_geeft_br():
    diagram = {
        "knopen": [{"id": "k1", "jas-klasse": "rechtssubject", "label": "eerste woord"}],
        "kanten": [],
    }
    result = diagram_to_mermaid(diagram)
    assert "<br/>" in result


def test_diagram_to_mermaid_classdefs_aangemaakt():
    diagram = {
        "knopen": [{"id": "k1", "jas-klasse": "rechtssubject", "label": "test"}],
        "kanten": [],
    }
    result = diagram_to_mermaid(diagram)
    assert "classDef" in result


# ===== diagram_tekst_fallback =====

def test_diagram_tekst_fallback_leeg_geeft_leeg():
    assert diagram_tekst_fallback({}) == ""
    assert diagram_tekst_fallback(None) == ""
    assert diagram_tekst_fallback({"knopen": []}) == ""


def test_diagram_tekst_fallback_noemt_knopen():
    diagram = {
        "knopen": [
            {"id": "k1", "jas-klasse": "rechtssubject", "label": "belastingschuldige"},
            {"id": "k2", "jas-klasse": "rechtsobject", "label": "aanslag"},
        ],
        "kanten": [],
    }
    result = diagram_tekst_fallback(diagram)
    assert "<details" in result
    assert "belastingschuldige" in result
    assert "aanslag" in result
    assert "2 knopen" in result
    assert "Geen relaties" in result


def test_diagram_tekst_fallback_beschrijft_relaties_met_en_zonder_label():
    diagram = {
        "knopen": [
            {"id": "k1", "jas-klasse": "rechtssubject", "label": "persoon"},
            {"id": "k2", "jas-klasse": "variabele", "label": "bedrag"},
            {"id": "k3", "jas-klasse": "rechtsobject", "label": "ding"},
        ],
        "kanten": [
            {"van": "k1", "naar": "k2", "label": "heeft"},
            {"van": "k2", "naar": "k3"},
        ],
    }
    result = diagram_tekst_fallback(diagram)
    assert "persoon → heeft → bedrag" in result
    assert "bedrag — ding" in result


def test_diagram_tekst_fallback_escapet_html():
    diagram = {
        "knopen": [{"id": "k1", "jas-klasse": "rechtssubject", "label": "<script>"}],
        "kanten": [],
    }
    result = diagram_tekst_fallback(diagram)
    assert "<script>" not in result
    assert "&lt;script&gt;" in result


def test_diagram_tekst_fallback_knoop_zonder_label_valt_terug_op_klasse():
    diagram = {
        "knopen": [{"id": "k1", "jas-klasse": "rechtsfeit"}],
        "kanten": [],
    }
    result = diagram_tekst_fallback(diagram)
    assert "rechtsfeit" in result
