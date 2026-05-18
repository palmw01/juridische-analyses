"""Tests voor tools/export_rdf.py — pure functies en CLI."""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from export_rdf import (
    turtle_literal,
    slug_van_id,
    begrip_naar_turtle,
    regel_naar_turtle,
    exporteer_begrippen,
    exporteer_regels,
    schrijf_turtle,
    main,
    PREFIXES,
)
from tests.fixtures.begrippen import maak_begrip
from tests.fixtures.regels import maak_regel


# ===== turtle_literal =====

def test_turtle_literal_normale_string():
    result = turtle_literal("belastingschuldige")
    assert result == '"belastingschuldige"@nl'


def test_turtle_literal_andere_taal():
    result = turtle_literal("taxpayer", lang="en")
    assert result.endswith("@en")


def test_turtle_literal_escapet_aanhalingstekens():
    result = turtle_literal('hij zei "hallo"')
    assert '\\"hallo\\"' in result


def test_turtle_literal_escapet_backslash():
    result = turtle_literal("pad\\bestand")
    assert "\\\\" in result


def test_turtle_literal_escapet_newline():
    result = turtle_literal("regel1\nregel2")
    assert "\\n" in result


# ===== slug_van_id =====

def test_slug_van_id_slashes_naar_underscores():
    assert slug_van_id("BWBR0004770/art9/lid1") == "BWBR0004770_art9_lid1"


def test_slug_van_id_geen_slashes():
    assert slug_van_id("AR-BWBR0004770-art9-lid1-a") == "AR-BWBR0004770-art9-lid1-a"


def test_slug_van_id_leeg():
    assert slug_van_id("") == ""


# ===== begrip_naar_turtle =====

def test_begrip_naar_turtle_lege_id_geeft_leeg():
    assert begrip_naar_turtle({}, {}) == ""
    assert begrip_naar_turtle({"begrip-id": ""}, {}) == ""


def test_begrip_naar_turtle_basis_structuur():
    fm = maak_begrip()
    result = begrip_naar_turtle(fm, {})
    assert "a skos:Concept" in result
    assert "skos:prefLabel" in result
    assert "skos:definition" in result


def test_begrip_naar_turtle_bevat_uri():
    fm = maak_begrip()
    result = begrip_naar_turtle(fm, {})
    assert "begrip:BWBR0004770_art9_lid1_belastingschuldige" in result


def test_begrip_naar_turtle_eindig_met_punt():
    fm = maak_begrip()
    result = begrip_naar_turtle(fm, {})
    assert result.strip().endswith(".")


def test_begrip_naar_turtle_met_jas_index():
    fm = maak_begrip()
    jas_index = {"BWBR0004770/art9/lid1/belastingschuldige": "rechtssubject"}
    result = begrip_naar_turtle(fm, jas_index)
    assert 'jas:jasKlasse "rechtssubject"' in result


def test_begrip_naar_turtle_met_alias():
    fm = maak_begrip(aliases=["belastingplichtige"])
    result = begrip_naar_turtle(fm, {})
    assert "skos:altLabel" in result
    assert "belastingplichtige" in result


def test_begrip_naar_turtle_met_geldigheid():
    fm = maak_begrip(**{"geldigheid-van": "2024-01-01"})
    result = begrip_naar_turtle(fm, {})
    assert "2024-01-01" in result
    assert "dct:valid" in result


def test_begrip_naar_turtle_met_is_een_relatie():
    fm = maak_begrip(relaties={"is-een": ["BWBR/art1/lid1/persoon"], "heeft": [], "leidt-tot": []})
    result = begrip_naar_turtle(fm, {})
    assert "skos:broader" in result


def test_begrip_naar_turtle_met_heeft_dict():
    fm = maak_begrip(relaties={"is-een": [], "heeft": [{"begrip-id": "BWBR/art1/lid1/aanslag"}], "leidt-tot": []})
    result = begrip_naar_turtle(fm, {})
    assert "jas:heeft" in result


def test_begrip_naar_turtle_met_heeft_string():
    fm = maak_begrip(relaties={"is-een": [], "heeft": ["BWBR/art1/lid1/aanslag"], "leidt-tot": []})
    result = begrip_naar_turtle(fm, {})
    assert "jas:heeft" in result


def test_begrip_naar_turtle_met_leidt_tot():
    fm = maak_begrip(relaties={"is-een": [], "heeft": [], "leidt-tot": ["BWBR/art9/lid1/r001"]})
    result = begrip_naar_turtle(fm, {})
    assert "jas:leidtTot" in result


def test_begrip_naar_turtle_met_markering_provenance():
    fm = maak_begrip()
    result = begrip_naar_turtle(fm, {})
    assert "prov:wasDerivedFrom" in result


def test_begrip_naar_turtle_met_afleidingsregel_id():
    fm = maak_begrip(**{"afleidingsregel-id": "AR-BWBR0004770-art9-lid1-a"})
    result = begrip_naar_turtle(fm, {})
    assert 'jas:afleidingsregel "AR-BWBR0004770-art9-lid1-a"' in result


def test_begrip_naar_turtle_met_uitvoer_van_regel():
    fm = maak_begrip(**{"uitvoer-van-regel-id": "AR-0002"})
    result = begrip_naar_turtle(fm, {})
    assert 'jas:uitvoerVanRegel "AR-0002"' in result


def test_begrip_naar_turtle_met_context_in_definitie():
    fm = maak_begrip(definitie={
        "kern": "de persoon die belasting verschuldigd is",
        "contexten": [{"bijdrage": "aanvullend", "tekst": "in het kader van art. 9", "markering-id": "m-001"}],
    })
    result = begrip_naar_turtle(fm, {})
    assert "jas:definitieContext" in result
    assert "in het kader van art. 9" in result


def test_begrip_naar_turtle_context_zonder_tekst_overgeslagen():
    fm = maak_begrip(definitie={
        "kern": "kern",
        "contexten": [{"bijdrage": "aanvullend", "tekst": "", "markering-id": "m-001"}],
    })
    result = begrip_naar_turtle(fm, {})
    assert "jas:definitieContext" not in result


# ===== regel_naar_turtle =====

def test_regel_naar_turtle_lege_id_geeft_leeg():
    assert regel_naar_turtle({}) == ""
    assert regel_naar_turtle({"regel-id": ""}) == ""


def test_regel_naar_turtle_basis_structuur():
    fm = maak_regel()
    result = regel_naar_turtle(fm)
    assert "a jas:Afleidingsregel" in result
    assert "skos:prefLabel" in result


def test_regel_naar_turtle_eindig_met_punt():
    fm = maak_regel()
    result = regel_naar_turtle(fm)
    assert result.strip().endswith(".")


def test_regel_naar_turtle_met_invoer():
    fm = maak_regel(invoer=["BWBR/art9/lid1/dagtekening"])
    result = regel_naar_turtle(fm)
    assert "jas:gebruikt" in result


def test_regel_naar_turtle_met_uitvoer():
    fm = maak_regel(uitvoer=["BWBR/art9/lid1/betalingstermijn"])
    result = regel_naar_turtle(fm)
    assert "jas:bepaalt" in result


def test_regel_naar_turtle_met_bwb_id():
    fm = maak_regel(**{"bwb-id": "BWBR0004770"})
    result = regel_naar_turtle(fm)
    assert 'dct:source "BWBR0004770"' in result


def test_regel_naar_turtle_met_toelichting():
    fm = maak_regel(toelichting="Standaard betalingstermijn")
    result = regel_naar_turtle(fm)
    assert "rdfs:comment" in result


# ===== exporteer_begrippen =====

def test_exporteer_begrippen_leeg(tmp_path):
    (tmp_path / "begrippen").mkdir()
    blokken = exporteer_begrippen(tmp_path, {})
    assert blokken == []


def test_exporteer_begrippen_een_bestand(tmp_path):
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "begrippen" / "test.yaml").write_text(
        yaml.dump(maak_begrip(), allow_unicode=True)
    )
    blokken = exporteer_begrippen(tmp_path, {})
    assert len(blokken) == 1
    assert "skos:Concept" in blokken[0]


def test_exporteer_begrippen_leeg_yaml_overgeslagen(tmp_path):
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "begrippen" / "leeg.yaml").write_text("")
    blokken = exporteer_begrippen(tmp_path, {})
    assert blokken == []


# ===== exporteer_regels =====

def test_exporteer_regels_geen_dir(tmp_path):
    blokken = exporteer_regels(tmp_path)
    assert blokken == []


def test_exporteer_regels_leeg(tmp_path):
    (tmp_path / "regels").mkdir()
    blokken = exporteer_regels(tmp_path)
    assert blokken == []


def test_exporteer_regels_een_bestand(tmp_path):
    (tmp_path / "regels").mkdir()
    (tmp_path / "regels" / "test.yaml").write_text(
        yaml.dump(maak_regel(), allow_unicode=True)
    )
    blokken = exporteer_regels(tmp_path)
    assert len(blokken) == 1
    assert "jas:Afleidingsregel" in blokken[0]


# ===== schrijf_turtle =====

def test_schrijf_turtle_maakt_bestand(tmp_path):
    schrijf_turtle(tmp_path / "out.ttl", ["begrip:test\n    a skos:Concept ."])
    assert (tmp_path / "out.ttl").exists()


def test_schrijf_turtle_bevat_prefixes(tmp_path):
    schrijf_turtle(tmp_path / "out.ttl", [])
    content = (tmp_path / "out.ttl").read_text()
    assert "@prefix skos:" in content


def test_schrijf_turtle_bevat_blokken(tmp_path):
    schrijf_turtle(tmp_path / "out.ttl", ["BLOK_A", "BLOK_B"])
    content = (tmp_path / "out.ttl").read_text()
    assert "BLOK_A" in content
    assert "BLOK_B" in content


def test_schrijf_turtle_maakt_parent_dir(tmp_path):
    schrijf_turtle(tmp_path / "diep" / "pad" / "out.ttl", [])
    assert (tmp_path / "diep" / "pad" / "out.ttl").exists()


# ===== main() =====

def test_main_geen_begrippen_dir_exit_1(tmp_path):
    with patch.object(sys, "argv", ["export_rdf.py", "--project-dir", str(tmp_path)]):
        result = main()
    assert result == 1


def test_main_succes(tmp_path):
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "begrippen" / "test.yaml").write_text(
        yaml.dump(maak_begrip(), allow_unicode=True)
    )
    out = tmp_path / "kennisgraaf" / "begrippen.ttl"
    with patch.object(sys, "argv", ["export_rdf.py", "--project-dir", str(tmp_path), "--out", str(out)]):
        result = main()
    assert result == 0
    assert out.exists()


def test_main_genereert_turtle_met_begrip_en_regel(tmp_path):
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "regels").mkdir()
    (tmp_path / "begrippen" / "test.yaml").write_text(yaml.dump(maak_begrip(), allow_unicode=True))
    (tmp_path / "regels" / "test.yaml").write_text(yaml.dump(maak_regel(), allow_unicode=True))
    out = tmp_path / "out.ttl"
    with patch.object(sys, "argv", ["export_rdf.py", "--project-dir", str(tmp_path), "--out", str(out)]):
        result = main()
    assert result == 0
    content = out.read_text()
    assert "skos:Concept" in content
    assert "jas:Afleidingsregel" in content


# ===== Aanvullende coverage voor regel-branch (line 233) en else-branches =====

def test_exporteer_regels_niet_dict_yaml_overgeslagen(tmp_path):
    """YAML met lijst-inhoud (niet dict) in regels-map wordt overgeslagen (line 233)."""
    (tmp_path / "regels").mkdir()
    (tmp_path / "regels" / "lijst.yaml").write_text("- item1\n- item2\n")
    blokken = exporteer_regels(tmp_path)
    assert blokken == []


def test_exporteer_regels_leeg_yaml_overgeslagen(tmp_path):
    """Leeg YAML-bestand in regels-map wordt overgeslagen."""
    (tmp_path / "regels").mkdir()
    (tmp_path / "regels" / "leeg.yaml").write_text("")
    blokken = exporteer_regels(tmp_path)
    assert blokken == []


def test_begrip_naar_turtle_else_branch_punt(tmp_path):
    """begrip_naar_turtle: als laatste regel niet op ' ;' eindigt → '    .' appended (line 163).

    Dit gebeurt als de begrip alleen 'a skos:Concept ;' heeft en de 'if lines[-1].endswith(" ;")'
    check faalt doordat de laatste regel al een '.' heeft. In de praktijk triggert dit
    wanneer de laatste toegevoegde regel niet met ' ;' eindigt.
    We testen dit door een begrip te maken zonder enig optioneel veld (alleen de URI + type).
    """
    # Minimaal begrip met alleen begrip-id, geen andere velden
    fm = {
        "begrip-id": "test/begrip",
        "begripsnaam": "",     # leeg → geen prefLabel
        "definitie": {},       # geen kern, geen contexten
        "geldigheid-van": "",  # leeg
        "herkomst": "",
        "aliases": [],
        "relaties": {},
        "markeringen": [],
        "status": "",
        "soort": "",
    }
    result = begrip_naar_turtle(fm, {})
    assert result.strip().endswith(".")


def test_regel_naar_turtle_else_branch_punt():
    """regel_naar_turtle: minimale regel zonder naam/soort/bwb → '    .' appended (line 220)."""
    fm = {"regel-id": "test-regel"}  # alleen regel-id, geen andere velden
    result = regel_naar_turtle(fm)
    assert result.strip().endswith(".")
