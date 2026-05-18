"""Tests voor sitegen/pages/graph.py en sitegen/assets.py."""
import json
from pathlib import Path

import pytest

from sitegen.pages.graph import gen_graph
from sitegen import assets


def b(**overrides) -> dict:
    base = {
        "id": "BWBR0004770/art9/lid1/belastingschuldige",
        "naam": "belastingschuldige",
        "slug": "belastingschuldige",
        "jas_klasse": "rechtssubject",
        "soort": "entiteit",
        "status": "concept",
        "relaties": {"is-een": [], "heeft": [], "leidt-tot": []},
    }
    base.update(overrides)
    return base


def r(**overrides) -> dict:
    base = {
        "id": "AR-BWBR0004770-art9-lid1-a",
        "naam": "Berekening betalingstermijn",
        "invoer": [],
        "uitvoer": ["BWBR0004770/art9/lid1/betalingstermijn"],
    }
    base.update(overrides)
    return base


# ===== gen_graph =====

def test_gen_graph_maakt_graph_html(tmp_path):
    gen_graph(tmp_path, [], [], [])
    assert (tmp_path / "graph.html").exists()


def test_gen_graph_maakt_graph_json(tmp_path):
    gen_graph(tmp_path, [], [], [])
    assert (tmp_path / "data" / "graph.json").exists()


def test_gen_graph_json_heeft_vereiste_velden(tmp_path):
    gen_graph(tmp_path, [b()], [], [])
    data = json.loads((tmp_path / "data" / "graph.json").read_text())
    assert "nodes" in data
    assert "links" in data
    assert "colorMap" in data


def test_gen_graph_begrip_node_aanwezig(tmp_path):
    gen_graph(tmp_path, [b()], [], [])
    data = json.loads((tmp_path / "data" / "graph.json").read_text())
    node_ids = [n["id"] for n in data["nodes"]]
    assert "BWBR0004770/art9/lid1/belastingschuldige" in node_ids


def test_gen_graph_begrip_node_heeft_page(tmp_path):
    gen_graph(tmp_path, [b()], [], [])
    data = json.loads((tmp_path / "data" / "graph.json").read_text())
    nodes = {n["id"]: n for n in data["nodes"]}
    assert "begrippen/belastingschuldige.html" in nodes["BWBR0004770/art9/lid1/belastingschuldige"]["page"]


def test_gen_graph_met_relatie_link(tmp_path):
    b1 = b()
    b2 = b(id="test/persoon", naam="persoon", slug="persoon", relaties={"is-een": [], "heeft": [], "leidt-tot": []})
    b1["relaties"]["is-een"] = ["test/persoon"]
    gen_graph(tmp_path, [b1, b2], [], [])
    data = json.loads((tmp_path / "data" / "graph.json").read_text())
    assert any(lnk["relatie"] == "is-een" for lnk in data["links"])


def test_gen_graph_onbekend_relatie_doel_wordt_node(tmp_path):
    begrip = b()
    begrip["relaties"]["heeft"] = ["test/onbekend-begrip"]
    gen_graph(tmp_path, [begrip], [], [])
    data = json.loads((tmp_path / "data" / "graph.json").read_text())
    node_ids = [n["id"] for n in data["nodes"]]
    assert "test/onbekend-begrip" in node_ids


def test_gen_graph_regel_node(tmp_path):
    gen_graph(tmp_path, [], [r()], [])
    data = json.loads((tmp_path / "data" / "graph.json").read_text())
    regel_nodes = [n for n in data["nodes"] if n["type"] == "regel"]
    assert len(regel_nodes) == 1
    assert regel_nodes[0]["id"] == "AR-BWBR0004770-art9-lid1-a"


def test_gen_graph_regel_met_invoer_link(tmp_path):
    begrip = b()
    reg = r(invoer=["BWBR0004770/art9/lid1/belastingschuldige"])
    gen_graph(tmp_path, [begrip], [reg], [])
    data = json.loads((tmp_path / "data" / "graph.json").read_text())
    invoer_links = [lnk for lnk in data["links"] if lnk["relatie"] == "invoer"]
    assert len(invoer_links) == 1


def test_gen_graph_regel_met_invoer_onbekend_begrip(tmp_path):
    reg = r(invoer=["test/onbekend-invoer"], uitvoer=[])
    gen_graph(tmp_path, [], [reg], [])
    data = json.loads((tmp_path / "data" / "graph.json").read_text())
    node_ids = [n["id"] for n in data["nodes"]]
    assert "test/onbekend-invoer" in node_ids


def test_gen_graph_regel_met_uitvoer_onbekend_begrip(tmp_path):
    reg = r(invoer=[], uitvoer=["test/onbekend-uitvoer"])
    gen_graph(tmp_path, [], [reg], [])
    data = json.loads((tmp_path / "data" / "graph.json").read_text())
    node_ids = [n["id"] for n in data["nodes"]]
    assert "test/onbekend-uitvoer" in node_ids


def test_gen_graph_html_bevat_graaf_content(tmp_path):
    gen_graph(tmp_path, [b()], [], [])
    content = (tmp_path / "graph.html").read_text()
    assert "Kennisgraaf" in content
    assert "graph.json" in content


# ===== gen_css_js =====

def test_gen_css_js_maakt_mappen(tmp_path):
    assets.gen_css_js(tmp_path)
    assert (tmp_path / "css").is_dir()
    assert (tmp_path / "js").is_dir()


def test_gen_css_js_kopieert_css_als_static_bestaat(tmp_path):
    assets.gen_css_js(tmp_path)
    # Geen fout; statische bestanden worden gekopieerd als ze bestaan
    assert (tmp_path / "css").is_dir()


def test_gen_css_js_comunica_niet_aanwezig_geen_fout(tmp_path):
    assets.gen_css_js(tmp_path, project_root=tmp_path)
    assert (tmp_path / "js").is_dir()


def test_gen_css_js_comunica_aanwezig_wordt_gekopieerd(tmp_path):
    build_dir = tmp_path / ".build"
    build_dir.mkdir()
    (build_dir / "comunica.min.js").write_bytes(b"x" * 200)
    assets.gen_css_js(tmp_path, project_root=tmp_path)
    assert (tmp_path / "js" / "comunica.min.js").exists()


# ===== gen_icons =====

def test_gen_icons_maakt_manifest_json(tmp_path):
    assets.gen_icons(tmp_path, tmp_path)
    assert (tmp_path / "manifest.json").exists()


def test_gen_icons_manifest_bevat_naam(tmp_path):
    assets.gen_icons(tmp_path, tmp_path)
    data = json.loads((tmp_path / "manifest.json").read_text())
    assert "name" in data


def test_gen_icons_manifest_al_aanwezig_niet_overschreven(tmp_path):
    (tmp_path / "icons").mkdir()
    (tmp_path / "manifest.json").write_text('{"custom": true}')
    assets.gen_icons(tmp_path, tmp_path)
    assert json.loads((tmp_path / "manifest.json").read_text()).get("custom") is True


def test_gen_icons_kopieert_bestanden_uit_project_icons(tmp_path):
    proj = tmp_path / "project"
    proj.mkdir()
    (proj / "icons").mkdir()
    (proj / "icons" / "favicon.png").write_bytes(b"\x89PNG")
    out = tmp_path / "out"
    out.mkdir()
    assets.gen_icons(proj, out)
    assert (out / "icons" / "favicon.png").exists()


def test_gen_icons_geen_icons_dir_geen_fout(tmp_path):
    proj = tmp_path / "project"
    proj.mkdir()
    out = tmp_path / "out"
    out.mkdir()
    assets.gen_icons(proj, out)
    assert (out / "icons").is_dir()


# ===== gen_data_files =====

def _begrip():
    return {
        "id": "BWBR0004770/art9/lid1/belastingschuldige",
        "naam": "belastingschuldige",
        "slug": "belastingschuldige",
        "definitie": "de persoon die belasting verschuldigd is",
        "aliases": [],
        "jas_klasse": "rechtssubject",
        "soort": "entiteit",
        "status": "concept",
    }


def _annotatie():
    return {
        "id": "BWBR0004770/art9/lid1",
        "bwb_id": "BWBR0004770",
        "wet": "Invorderingswet 1990",
        "artikel": "9",
        "lid": "1",
        "wetstekst": "De belastingaanslag...",
        "rijen": [],
        "kruisreferenties": [],
    }


def _regel():
    return {
        "id": "AR-BWBR0004770-art9-lid1-a",
        "naam": "Berekening betalingstermijn",
        "formele_regel": "betalingstermijn = 30 dagen",
        "toelichting": "Standaard termijn.",
        "soort": "Rekenregel",
    }


def _artikel_index():
    return {
        "id": "BWBR0004770/art9",
        "bwb_id": "BWBR0004770",
        "wet": "Invorderingswet 1990",
        "artikel": "9",
        "structuurpositie": "Hoofdstuk 1 > Artikel 9",
        "leden_annotaties": [],
    }


def test_gen_data_files_maakt_json_bestanden(tmp_path):
    assets.gen_data_files(tmp_path, [_begrip()], [_annotatie()], [_regel()], [])
    assert (tmp_path / "data" / "begrippen.json").exists()
    assert (tmp_path / "data" / "annotaties.json").exists()
    assert (tmp_path / "data" / "regels.json").exists()


def test_gen_data_files_begrip_in_json(tmp_path):
    assets.gen_data_files(tmp_path, [_begrip()], [], [], [])
    data = json.loads((tmp_path / "data" / "begrippen.json").read_text())
    assert len(data) == 1
    assert data[0]["titel"] == "belastingschuldige"


def test_gen_data_files_annotatie_in_json(tmp_path):
    assets.gen_data_files(tmp_path, [], [_annotatie()], [], [])
    data = json.loads((tmp_path / "data" / "annotaties.json").read_text())
    assert len(data) == 1
    assert data[0]["bwb_id"] == "BWBR0004770"


def test_gen_data_files_artikel_index_in_annotaties_json(tmp_path):
    assets.gen_data_files(tmp_path, [], [], [], [_artikel_index()])
    data = json.loads((tmp_path / "data" / "annotaties.json").read_text())
    assert len(data) == 1
    assert "artikeloverzicht" in data[0]["titel"]


def test_gen_data_files_regel_in_json(tmp_path):
    assets.gen_data_files(tmp_path, [], [], [_regel()], [])
    data = json.loads((tmp_path / "data" / "regels.json").read_text())
    assert len(data) == 1
    assert data[0]["titel"] == "Berekening betalingstermijn"


def test_gen_data_files_ttl_gekopieerd_als_aanwezig(tmp_path):
    proj = tmp_path / "project"
    (proj / "kennisgraaf").mkdir(parents=True)
    (proj / "kennisgraaf" / "begrippen.ttl").write_text("@prefix : <test:> .")
    out = tmp_path / "out"
    assets.gen_data_files(out, [], [], [], [], project_root=proj)
    assert (out / "data" / "begrippen.ttl").exists()
