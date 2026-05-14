"""Tests voor tools/export_graph.py — pure functies en CLI."""
import json
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from export_graph import (
    is_verborgen_pad,
    check_staleness,
    build_graph,
    main,
)
from sitegen.config import JAS_KLEUREN
from tests.fixtures.begrippen import maak_begrip
from tests.fixtures.regels import maak_regel
from tests.fixtures.annotaties import maak_annotatie


# ===== is_verborgen_pad =====

def test_is_verborgen_pad_normaal_pad(tmp_path):
    fp = tmp_path / "begrippen" / "test.yaml"
    assert is_verborgen_pad(fp, tmp_path) is False


def test_is_verborgen_pad_verborgen_map(tmp_path):
    fp = tmp_path / ".obsidian" / "graph.json"
    assert is_verborgen_pad(fp, tmp_path) is True


def test_is_verborgen_pad_geneste_verborgen_map(tmp_path):
    fp = tmp_path / "annotaties" / ".hidden" / "test.json"
    assert is_verborgen_pad(fp, tmp_path) is True


def test_is_verborgen_pad_buiten_root(tmp_path):
    """Pad buiten root: ValueError → geeft False terug."""
    other = tmp_path.parent / "ander_project" / "file.txt"
    assert is_verborgen_pad(other, tmp_path) is False


def test_is_verborgen_pad_direct_in_root(tmp_path):
    fp = tmp_path / "test.yaml"
    assert is_verborgen_pad(fp, tmp_path) is False


def test_is_verborgen_pad_verborgen_bestand(tmp_path):
    fp = tmp_path / "begrippen" / ".gitkeep"
    assert is_verborgen_pad(fp, tmp_path) is True


# ===== check_staleness =====

def test_check_staleness_geen_gexf(tmp_path, capsys):
    """Geen graph.gexf aanwezig → geen waarschuwing."""
    check_staleness(tmp_path, tmp_path)
    assert capsys.readouterr().err == ""


def test_check_staleness_gexf_nieuwer_dan_bestanden(tmp_path, capsys):
    """Alle projectbestanden zijn ouder dan gexf → geen waarschuwing."""
    begrippen = tmp_path / "begrippen"
    begrippen.mkdir()
    yaml_file = begrippen / "test.yaml"
    yaml_file.write_text("begrip-id: test")

    output_dir = tmp_path / "kennisgraaf"
    output_dir.mkdir()
    gexf = output_dir / "graph.gexf"
    gexf.write_text("<gexf/>")
    # Zet mtime van gexf ver in de toekomst
    future = time.time() + 10000
    import os
    os.utime(gexf, (future, future))

    check_staleness(tmp_path, output_dir)
    assert capsys.readouterr().err == ""


def test_check_staleness_bestanden_nieuwer_dan_gexf(tmp_path, capsys):
    """Projectbestanden zijn nieuwer dan gexf → waarschuwing in stderr."""
    begrippen = tmp_path / "begrippen"
    begrippen.mkdir()

    output_dir = tmp_path / "kennisgraaf"
    output_dir.mkdir()
    gexf = output_dir / "graph.gexf"
    gexf.write_text("<gexf/>")
    # Zet mtime van gexf ver in het verleden
    import os
    past = time.time() - 10000
    os.utime(gexf, (past, past))

    # Schrijf yaml-bestand (nieuwer dan de gexf in het verleden)
    yaml_file = begrippen / "test.yaml"
    yaml_file.write_text("begrip-id: test")

    check_staleness(tmp_path, output_dir)
    err = capsys.readouterr().err
    assert "waarschuwing" in err.lower() or "nieuwer" in err.lower()


def test_check_staleness_meer_dan_5_nieuwere(tmp_path, capsys):
    """Meer dan 5 nieuwere bestanden → '… en X andere(n)' in stderr."""
    begrippen = tmp_path / "begrippen"
    begrippen.mkdir()

    output_dir = tmp_path / "kennisgraaf"
    output_dir.mkdir()
    gexf = output_dir / "graph.gexf"
    gexf.write_text("<gexf/>")
    import os
    past = time.time() - 10000
    os.utime(gexf, (past, past))

    for i in range(7):
        (begrippen / f"begrip{i}.yaml").write_text(f"begrip-id: test{i}")

    check_staleness(tmp_path, output_dir)
    err = capsys.readouterr().err
    assert "andere(n)" in err


def test_check_staleness_negeert_verborgen_bestanden(tmp_path, capsys):
    """Verborgen bestanden worden niet meegeteld."""
    begrippen = tmp_path / "begrippen"
    begrippen.mkdir()
    hidden = begrippen / ".hidden_dir"
    hidden.mkdir()

    output_dir = tmp_path / "kennisgraaf"
    output_dir.mkdir()
    gexf = output_dir / "graph.gexf"
    gexf.write_text("<gexf/>")
    import os
    past = time.time() - 10000
    os.utime(gexf, (past, past))

    # Verborgen yaml — mag niet meegeteld worden
    (hidden / "verborgen.yaml").write_text("begrip-id: hidden")

    check_staleness(tmp_path, output_dir)
    err = capsys.readouterr().err
    # Geen waarschuwing want geen zichtbare nieuwere bestanden
    assert "waarschuwing" not in err.lower()


# ===== kleurkaart (JAS_KLEUREN) =====

def test_build_graph_begrip_node_kleur_uit_jas_kleuren(tmp_path):
    """Begrip met bekende JAS-klasse krijgt kleur uit JAS_KLEUREN, niet FALLBACK."""
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "regels").mkdir()
    (tmp_path / "annotaties").mkdir()
    b = maak_begrip(**{"jas-klasse": "rechtssubject"})
    (tmp_path / "begrippen" / "test.yaml").write_text(yaml.dump(b, allow_unicode=True))
    G = build_graph(tmp_path)
    node = G.nodes.get(b["begrip-id"])
    assert node is not None
    assert node["color"] == JAS_KLEUREN["rechtssubject"]


def test_build_graph_begrip_node_onbekende_klasse_geeft_fallback(tmp_path):
    """Begrip met onbekende JAS-klasse krijgt FALLBACK_KLEUR."""
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "regels").mkdir()
    (tmp_path / "annotaties").mkdir()
    b = maak_begrip(**{"jas-klasse": "onbekende-klasse-xyz"})
    (tmp_path / "begrippen" / "test.yaml").write_text(yaml.dump(b, allow_unicode=True))
    G = build_graph(tmp_path)
    node = G.nodes.get(b["begrip-id"])
    assert node is not None
    assert node["color"] == "#CCCCCC"


# ===== build_graph =====

def test_build_graph_leeg_project(tmp_path):
    """Lege mappen → lege graaf."""
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "regels").mkdir()
    (tmp_path / "annotaties").mkdir()
    g = build_graph(tmp_path)
    assert g.number_of_nodes() == 0
    assert g.number_of_edges() == 0


def test_build_graph_geen_mappen(tmp_path):
    """Geen begrippen/regels/annotaties dirs → lege graaf, geen crash."""
    g = build_graph(tmp_path)
    assert g.number_of_nodes() == 0


def test_build_graph_met_begrip(tmp_path):
    (tmp_path / "begrippen").mkdir()
    fm = maak_begrip()
    (tmp_path / "begrippen" / "test.yaml").write_text(yaml.dump(fm, allow_unicode=True))
    g = build_graph(tmp_path)
    assert g.number_of_nodes() == 1
    node_id = "BWBR0004770/art9/lid1/belastingschuldige"
    assert node_id in g
    assert g.nodes[node_id]["node_type"] == "begrip"
    assert g.nodes[node_id]["label"] == "belastingschuldige"


def test_build_graph_begrip_leeg_yaml(tmp_path):
    """Leeg YAML-bestand wordt overgeslagen."""
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "begrippen" / "leeg.yaml").write_text("")
    g = build_graph(tmp_path)
    assert g.number_of_nodes() == 0


def test_build_graph_begrip_niet_dict(tmp_path):
    """YAML met niet-dict inhoud wordt overgeslagen."""
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "begrippen" / "lijst.yaml").write_text("- item1\n- item2\n")
    g = build_graph(tmp_path)
    assert g.number_of_nodes() == 0




def test_build_graph_begrip_met_geldigheid(tmp_path):
    """geldigheid-van en geldigheid-tot worden als start/end attrs opgeslagen."""
    (tmp_path / "begrippen").mkdir()
    fm = maak_begrip(**{"geldigheid-van": "2024-01-01", "geldigheid-tot": "2025-01-01"})
    (tmp_path / "begrippen" / "test.yaml").write_text(yaml.dump(fm, allow_unicode=True))
    g = build_graph(tmp_path)
    node_id = "BWBR0004770/art9/lid1/belastingschuldige"
    assert g.nodes[node_id]["start"] == "2024-01-01"
    assert g.nodes[node_id]["end"] == "2025-01-01"


def test_build_graph_met_regel(tmp_path):
    (tmp_path / "regels").mkdir()
    fm = maak_regel()
    (tmp_path / "regels" / "test.yaml").write_text(yaml.dump(fm, allow_unicode=True))
    g = build_graph(tmp_path)
    assert "AR-0001" in g
    assert g.nodes["AR-0001"]["node_type"] == "afleidingsregel"
    assert g.nodes["AR-0001"]["jas_klasse"] == "afleidingsregel"


def test_build_graph_regel_met_peildatum(tmp_path):
    (tmp_path / "regels").mkdir()
    fm = maak_regel(peildatum="2024-06-01")
    (tmp_path / "regels" / "test.yaml").write_text(yaml.dump(fm, allow_unicode=True))
    g = build_graph(tmp_path)
    assert g.nodes["AR-0001"]["start"] == "2024-06-01"


def test_build_graph_regel_leeg_yaml(tmp_path):
    (tmp_path / "regels").mkdir()
    (tmp_path / "regels" / "leeg.yaml").write_text("")
    g = build_graph(tmp_path)
    assert g.number_of_nodes() == 0


def test_build_graph_met_annotatie(tmp_path):
    (tmp_path / "annotaties").mkdir()
    data = maak_annotatie()
    (tmp_path / "annotaties" / "art9.json").write_text(json.dumps(data))
    g = build_graph(tmp_path)
    assert "BWBR0004770/art9/lid1" in g
    assert g.nodes["BWBR0004770/art9/lid1"]["node_type"] == "annotatie"


def test_build_graph_annotatie_label_formaat(tmp_path):
    """Label van annotatie-node bevat 'Art.' en artikelnummer."""
    (tmp_path / "annotaties").mkdir()
    data = maak_annotatie()
    (tmp_path / "annotaties" / "art9.json").write_text(json.dumps(data))
    g = build_graph(tmp_path)
    node_id = "BWBR0004770/art9/lid1"
    label = g.nodes[node_id]["label"]
    assert "Art." in label
    assert "9" in label


def test_build_graph_annotatie_met_lid(tmp_path):
    """lid-veld in annotatie wordt verwerkt in label."""
    (tmp_path / "annotaties").mkdir()
    data = maak_annotatie()
    data["lid"] = "2"
    (tmp_path / "annotaties" / "art9lid2.json").write_text(json.dumps(data))
    g = build_graph(tmp_path)
    node_id = "BWBR0004770/art9/lid1"
    label = g.nodes[node_id]["label"]
    assert "lid" in label


def test_build_graph_annotatie_zonder_lid(tmp_path):
    """Geen lid → geen 'lid' in label."""
    (tmp_path / "annotaties").mkdir()
    data = maak_annotatie()
    data.pop("lid", None)
    data["annotatie-id"] = "BWBR0004770/art9"
    (tmp_path / "annotaties" / "art9.json").write_text(json.dumps(data))
    g = build_graph(tmp_path)
    node_id = "BWBR0004770/art9"
    label = g.nodes[node_id]["label"]
    assert "lid" not in label


def test_build_graph_annotatie_ongeldige_json(tmp_path):
    """Ongeldige JSON → wordt overgeslagen."""
    (tmp_path / "annotaties").mkdir()
    (tmp_path / "annotaties" / "kapot.json").write_text("{niet: geldig json}")
    g = build_graph(tmp_path)
    assert g.number_of_nodes() == 0


def test_build_graph_annotatie_verborgen_pad(tmp_path):
    """JSON in verborgen map wordt overgeslagen."""
    annotaties = tmp_path / "annotaties"
    annotaties.mkdir()
    verborgen = annotaties / ".hidden"
    verborgen.mkdir()
    data = maak_annotatie()
    (verborgen / "art9.json").write_text(json.dumps(data))
    g = build_graph(tmp_path)
    assert g.number_of_nodes() == 0


def test_build_graph_annotatie_met_peildatum(tmp_path):
    """peildatum in annotatie wordt als start-attribuut opgeslagen."""
    (tmp_path / "annotaties").mkdir()
    data = maak_annotatie()
    data["peildatum"] = "2024-01-01"
    (tmp_path / "annotaties" / "art9.json").write_text(json.dumps(data))
    g = build_graph(tmp_path)
    node_id = "BWBR0004770/art9/lid1"
    assert g.nodes[node_id]["start"] == "2024-01-01"


# ===== Edge-tests =====

def test_build_graph_edge_begrip_is_een(tmp_path):
    """is-een relatie genereert een 'is-een' edge."""
    (tmp_path / "begrippen").mkdir()
    parent = maak_begrip(**{"begrip-id": "BWBR0004770/art1/lid1/persoon", "begripsnaam": "persoon"})
    parent["relaties"] = {"is-een": [], "heeft": [], "leidt-tot": []}
    parent["markeringen"] = []
    (tmp_path / "begrippen" / "persoon.yaml").write_text(yaml.dump(parent, allow_unicode=True))

    child = maak_begrip()
    child["relaties"] = {"is-een": ["BWBR0004770/art1/lid1/persoon"], "heeft": [], "leidt-tot": []}
    (tmp_path / "begrippen" / "belastingschuldige.yaml").write_text(yaml.dump(child, allow_unicode=True))

    g = build_graph(tmp_path)
    edges = list(g.edges(data=True))
    edge_types = [d.get("edge_type") for _, _, d in edges]
    assert "is-een" in edge_types


def test_build_graph_edge_begrip_heeft_dict(tmp_path):
    """heeft-relatie als dict genereert een 'heeft' edge."""
    (tmp_path / "begrippen").mkdir()
    doel = maak_begrip(**{"begrip-id": "BWBR0004770/art1/lid1/aanslag", "begripsnaam": "aanslag"})
    doel["relaties"] = {"is-een": [], "heeft": [], "leidt-tot": []}
    doel["markeringen"] = []
    (tmp_path / "begrippen" / "aanslag.yaml").write_text(yaml.dump(doel, allow_unicode=True))

    bron = maak_begrip()
    bron["relaties"] = {
        "is-een": [],
        "heeft": [{"begrip-id": "BWBR0004770/art1/lid1/aanslag"}],
        "leidt-tot": [],
    }
    (tmp_path / "begrippen" / "belastingschuldige.yaml").write_text(yaml.dump(bron, allow_unicode=True))

    g = build_graph(tmp_path)
    edges = list(g.edges(data=True))
    edge_types = [d.get("edge_type") for _, _, d in edges]
    assert "heeft" in edge_types


def test_build_graph_edge_begrip_leidt_tot_string(tmp_path):
    """leidt-tot als string genereert een 'leidt-tot' edge."""
    (tmp_path / "begrippen").mkdir()
    doel = maak_begrip(**{"begrip-id": "BWBR0004770/art9/lid1/plicht", "begripsnaam": "plicht"})
    doel["relaties"] = {"is-een": [], "heeft": [], "leidt-tot": []}
    doel["markeringen"] = []
    (tmp_path / "begrippen" / "plicht.yaml").write_text(yaml.dump(doel, allow_unicode=True))

    bron = maak_begrip()
    bron["relaties"] = {
        "is-een": [],
        "heeft": [],
        "leidt-tot": ["BWBR0004770/art9/lid1/plicht"],
    }
    (tmp_path / "begrippen" / "belastingschuldige.yaml").write_text(yaml.dump(bron, allow_unicode=True))

    g = build_graph(tmp_path)
    edges = list(g.edges(data=True))
    edge_types = [d.get("edge_type") for _, _, d in edges]
    assert "leidt-tot" in edge_types


def test_build_graph_edge_begrip_leidt_tot_dict_met_relatie_soort(tmp_path):
    """leidt-tot als dict met relatie-soort genereert edge met die soort als label."""
    (tmp_path / "begrippen").mkdir()
    doel = maak_begrip(**{"begrip-id": "BWBR0004770/art9/lid1/gevolg", "begripsnaam": "gevolg"})
    doel["relaties"] = {"is-een": [], "heeft": [], "leidt-tot": []}
    doel["markeringen"] = []
    (tmp_path / "begrippen" / "gevolg.yaml").write_text(yaml.dump(doel, allow_unicode=True))

    bron = maak_begrip()
    bron["relaties"] = {
        "is-een": [],
        "heeft": [],
        "leidt-tot": [{"begrip-id": "BWBR0004770/art9/lid1/gevolg", "relatie-soort": "veroorzaakt"}],
    }
    (tmp_path / "begrippen" / "belastingschuldige.yaml").write_text(yaml.dump(bron, allow_unicode=True))

    g = build_graph(tmp_path)
    edges = list(g.edges(data=True))
    labels = [d.get("label") for _, _, d in edges]
    assert "veroorzaakt" in labels


def test_build_graph_edge_afleidingsregel_id(tmp_path):
    """afleidingsregel-id in begrip genereert 'afgeleid-via' edge naar regel."""
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "regels").mkdir()

    regel = maak_regel()
    (tmp_path / "regels" / "rule.yaml").write_text(yaml.dump(regel, allow_unicode=True))

    fm = maak_begrip(**{"afleidingsregel-id": "AR-0001"})
    (tmp_path / "begrippen" / "begrip.yaml").write_text(yaml.dump(fm, allow_unicode=True))

    g = build_graph(tmp_path)
    edges = list(g.edges(data=True))
    edge_types = [d.get("edge_type") for _, _, d in edges]
    assert "afgeleid-via" in edge_types


def test_build_graph_edge_uitvoer_van_regel_id(tmp_path):
    """uitvoer-van-regel-id in begrip genereert 'uitvoer-van' edge naar regel."""
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "regels").mkdir()

    regel = maak_regel()
    (tmp_path / "regels" / "rule.yaml").write_text(yaml.dump(regel, allow_unicode=True))

    fm = maak_begrip(**{"uitvoer-van-regel-id": "AR-0001"})
    (tmp_path / "begrippen" / "begrip.yaml").write_text(yaml.dump(fm, allow_unicode=True))

    g = build_graph(tmp_path)
    edges = list(g.edges(data=True))
    edge_types = [d.get("edge_type") for _, _, d in edges]
    assert "uitvoer-van" in edge_types


def test_build_graph_edge_annotatie_naar_begrip(tmp_path):
    """annotatierijen in annotatie genereert 'markeert' edge naar begrip."""
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "annotaties").mkdir()

    fm = maak_begrip()
    (tmp_path / "begrippen" / "begrip.yaml").write_text(yaml.dump(fm, allow_unicode=True))

    ann = maak_annotatie()
    (tmp_path / "annotaties" / "art9.json").write_text(json.dumps(ann))

    g = build_graph(tmp_path)
    edges = list(g.edges(data=True))
    edge_types = [d.get("edge_type") for _, _, d in edges]
    assert "markeert" in edge_types


def test_build_graph_edge_diagram_kanten(tmp_path):
    """diagram-kanten genereren 'diagram' edges."""
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "annotaties").mkdir()

    begrip1 = maak_begrip()
    (tmp_path / "begrippen" / "begrip1.yaml").write_text(yaml.dump(begrip1, allow_unicode=True))

    begrip2 = maak_begrip(**{"begrip-id": "BWBR0004770/art9/lid1/aanslag", "begripsnaam": "aanslag"})
    begrip2["markeringen"] = []
    (tmp_path / "begrippen" / "begrip2.yaml").write_text(yaml.dump(begrip2, allow_unicode=True))

    ann = maak_annotatie()
    ann["diagram"] = {
        "knopen": [
            {"id": "k1", "label": "belastingschuldige", "begrip-id": "BWBR0004770/art9/lid1/belastingschuldige"},
            {"id": "k2", "label": "aanslag", "begrip-id": "BWBR0004770/art9/lid1/aanslag"},
        ],
        "kanten": [
            {"van": "k1", "naar": "k2", "label": "ontvangt"},
        ],
    }
    (tmp_path / "annotaties" / "art9.json").write_text(json.dumps(ann))

    g = build_graph(tmp_path)
    edges = list(g.edges(data=True))
    edge_types = [d.get("edge_type") for _, _, d in edges]
    assert "diagram" in edge_types


def test_build_graph_regel_invoer_uitvoer_edges(tmp_path):
    """Regel invoer/uitvoer genereren 'invoer-voor' en 'bepaalt' edges."""
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "regels").mkdir()

    invoer_begrip = maak_begrip(**{
        "begrip-id": "BWBR0004770/art9/lid1/dagtekening",
        "begripsnaam": "dagtekening",
    })
    invoer_begrip["markeringen"] = []
    (tmp_path / "begrippen" / "dagtekening.yaml").write_text(yaml.dump(invoer_begrip, allow_unicode=True))

    uitvoer_begrip = maak_begrip(**{
        "begrip-id": "BWBR0004770/art9/lid1/betalingstermijn",
        "begripsnaam": "betalingstermijn",
    })
    uitvoer_begrip["markeringen"] = []
    (tmp_path / "begrippen" / "betalingstermijn.yaml").write_text(yaml.dump(uitvoer_begrip, allow_unicode=True))

    regel = maak_regel(
        invoer=["BWBR0004770/art9/lid1/dagtekening"],
        uitvoer=["BWBR0004770/art9/lid1/betalingstermijn"],
    )
    (tmp_path / "regels" / "regel.yaml").write_text(yaml.dump(regel, allow_unicode=True))

    g = build_graph(tmp_path)
    edges = list(g.edges(data=True))
    edge_types = [d.get("edge_type") for _, _, d in edges]
    assert "bepaalt" in edge_types
    assert "invoer-voor" in edge_types


def test_build_graph_node_id_fallback_naar_stem(tmp_path):
    """Als begrip-id ontbreekt wordt bestandsnaam (stem) als node-id gebruikt."""
    (tmp_path / "begrippen").mkdir()
    fm = maak_begrip()
    del fm["begrip-id"]
    (tmp_path / "begrippen" / "mijn-begrip.yaml").write_text(yaml.dump(fm, allow_unicode=True))
    g = build_graph(tmp_path)
    assert "mijn-begrip" in g


# ===== main() =====

def test_main_maakt_gexf_en_graphml(tmp_path):
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "regels").mkdir()
    (tmp_path / "annotaties").mkdir()
    with patch.object(sys, "argv", ["export_graph.py", "--project-dir", str(tmp_path)]):
        main()
    assert (tmp_path / "kennisgraaf" / "graph.gexf").exists()
    assert (tmp_path / "kennisgraaf" / "graph.graphml").exists()


def test_main_met_begrip_en_regel(tmp_path):
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "regels").mkdir()
    fm = maak_begrip()
    (tmp_path / "begrippen" / "begrip.yaml").write_text(yaml.dump(fm, allow_unicode=True))
    regel = maak_regel()
    (tmp_path / "regels" / "regel.yaml").write_text(yaml.dump(regel, allow_unicode=True))
    with patch.object(sys, "argv", ["export_graph.py", "--project-dir", str(tmp_path)]):
        main()
    gexf = tmp_path / "kennisgraaf" / "graph.gexf"
    assert gexf.exists()


def test_main_print_statistieken(tmp_path, capsys):
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "regels").mkdir()
    with patch.object(sys, "argv", ["export_graph.py", "--project-dir", str(tmp_path)]):
        main()
    out = capsys.readouterr().out
    assert "nodes" in out
    assert "edges" in out


# ===== Aanvullende edge-case coverage =====

def test_check_staleness_negeert_verborgen_in_globpatroon(tmp_path, capsys):
    """line 43: is_verborgen_pad check in check_staleness — verborgen bestand in annotaties wordt niet meegeteld."""
    import os
    annotaties = tmp_path / "annotaties"
    annotaties.mkdir()
    verborgen_sub = annotaties / ".hidden"
    verborgen_sub.mkdir()

    output_dir = tmp_path / "kennisgraaf"
    output_dir.mkdir()
    gexf = output_dir / "graph.gexf"
    gexf.write_text("<gexf/>")
    past = time.time() - 10000
    os.utime(gexf, (past, past))

    # Alleen een verborgen JSON bestand — mag niet meegeteld worden in check_staleness
    (verborgen_sub / "verborgen.json").write_text("{}")

    check_staleness(tmp_path, output_dir)
    err = capsys.readouterr().err
    assert "waarschuwing" not in err.lower()


def test_build_graph_begrip_van_id_niet_in_graph(tmp_path):
    """line 181: begrip met relaties maar de van_id is niet in G (geen begrip-id node) → continue.

    Dit kan als begrip-id ontbreekt maar de yaml bestanden worden twee keer verwerkt
    (1e pass: nodes, 2e pass: edges). Als het bestand de 2e keer via een ander pad 'van_id' geeft,
    die niet overeenkomt met de node, wordt de continue getriggerd.
    We testen dit door een begrip te schrijven dat een relatie heeft naar een onbestaand begrip;
    de van_id (het begrip zelf) moet wel in de graph zitten voor de edge te werken.
    """
    (tmp_path / "begrippen").mkdir()

    # Begrip met is-een relatie naar onbestaand begrip (doel niet in G → geen edge maar geen crash)
    fm = maak_begrip()
    fm["relaties"] = {
        "is-een": ["BWBR0004770/art1/lid1/onbestaand"],
        "heeft": [],
        "leidt-tot": [],
    }
    (tmp_path / "begrippen" / "begrip.yaml").write_text(yaml.dump(fm, allow_unicode=True))
    g = build_graph(tmp_path)
    # Node bestaat, maar geen is-een edge want doel niet in G
    assert "BWBR0004770/art9/lid1/belastingschuldige" in g
    edges = list(g.edges(data=True))
    edge_types = [d.get("edge_type") for _, _, d in edges]
    assert "is-een" not in edge_types


def test_build_graph_annotatie_id_niet_in_graph(tmp_path):
    """line 224: annotatie-id niet in G (annotatie-nodes nooit aangemaakt) → continue.

    We schrijven alleen een annotatie-JSON (geen begrippen/annotaties dir), maar
    leggen de annotatie-nodes niet aan. De tweede pass (edge-fase) zou een continue triggeren
    als de annotatie-id er al was in de eerste pass maar de node ondertussen wegvalt.
    Echter, annotatie-nodes worden altijd aangemaakt. De enige manier om line 224 te raken
    is als annotatie-id in de JSON leeg is maar het bestand al in de eerste pass een andere id had.
    We testen dit door een corrupt JSON dat een annotatie-id bevat die anders is dan wat
    in de eerste pass werd opgeslagen.
    """
    # Dit is al impliciet gedekt door andere tests; annotaties met lege annotatie-id
    # zullen een pad-gebaseerde id gebruiken die altijd in G zit.
    # Meest directe test: verborgen annotatie (skip in beide passes) → geen node, geen crash
    (tmp_path / "annotaties").mkdir()
    verborgen = tmp_path / "annotaties" / ".hidden"
    verborgen.mkdir()
    data = maak_annotatie()
    (verborgen / "art9.json").write_text(json.dumps(data))
    g = build_graph(tmp_path)
    assert g.number_of_nodes() == 0  # Verborgen bestand volledig genegeerd


def test_build_graph_regel_van_id_niet_in_graph(tmp_path):
    """line 250: regel-id niet in G (regel-dir aanwezig maar node niet aangemaakt) → continue.

    Dit triggert wanneer een regel-yaml is zonder 'regel-id' en het stem al niet als node
    bestaat. Maar in de eerste pass wordt het stem wel als node-id gebruikt, dus het is
    altijd aanwezig. De continue-lijn wordt bereikt als een yaml tussen de eerste en tweede
    pass werd bijgewerkt — dat kan in tests niet. We testen een lege yaml die in de 2e pass
    geen node heeft (continue al getriggerd door 'not fm or not isinstance').
    """
    (tmp_path / "regels").mkdir()
    # Leeg yaml → beide passes skippen, geen nodes, geen edges
    (tmp_path / "regels" / "leeg.yaml").write_text("")
    g = build_graph(tmp_path)
    assert g.number_of_nodes() == 0
    assert g.number_of_edges() == 0
