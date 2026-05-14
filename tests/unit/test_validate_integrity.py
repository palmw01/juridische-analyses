"""L2 integriteitsvalidatie-tests — elke check heeft happy path én failure path."""
from pathlib import Path

import pytest
import yaml

from validate_note import (
    validate_integrity_begrip,
    validate_integrity_regel,
    build_begrip_index,
)
from tests.fixtures.begrippen import maak_begrip
from tests.fixtures.regels import maak_regel

DUMMY = Path("/tmp/test.yaml")


def leeg_project(tmp_path, mappen=("begrippen", "annotaties")):
    for d in mappen:
        (tmp_path / d).mkdir(exist_ok=True)
    return tmp_path


# ===== validate_integrity_begrip =====

def test_begrip_zonder_markeringen_geen_fouten(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(markeringen=[], **{"definitie-gebaseerd-op": []})
    idx = build_begrip_index(project)
    assert validate_integrity_begrip(data, DUMMY, idx, project) == []


def test_begrip_def_gebaseerd_op_ontbrekende_markering_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(**{"definitie-gebaseerd-op": ["m-bestaat-nooit"]})
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("definitie-gebaseerd-op" in e and "m-bestaat-nooit" in e for e in errors)


def test_begrip_def_gebaseerd_op_bestaande_primaire_markering_geen_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip()  # m-001 bestaat en heeft bijdrage primair
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert not any("definitie-gebaseerd-op" in e for e in errors)


def test_begrip_def_gebaseerd_op_niet_primair_bijdrage_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(
        markeringen=[{"markering-id": "m-001", "bijdrage": "verfijning",
                      "bron-annotatie-id": "x", "jas-klasse": "rechtssubject", "bevestigd": False}],
        **{"definitie-gebaseerd-op": ["m-001"]},
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("definitie-gebaseerd-op" in e and "verfijning" in e for e in errors)


def test_begrip_wikilink_in_bron_annotatie_id_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(
        markeringen=[{"markering-id": "m-001", "bijdrage": "primair",
                      "bron-annotatie-id": "[[annotaties/art9]]",
                      "jas-klasse": "rechtssubject", "bevestigd": False}],
        **{"definitie-gebaseerd-op": []},
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("wikilink" in e.lower() for e in errors)


def test_begrip_is_een_ontbreekt_in_index_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(
        relaties={"is-een": ["BWBR0004770/art9/lid1/ontbreekt"], "heeft": [], "leidt-tot": []},
        markeringen=[], **{"definitie-gebaseerd-op": []},
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("is-een" in e for e in errors)


def test_begrip_is_een_aanwezig_in_index_geen_fout(tmp_path):
    project = leeg_project(tmp_path)
    # Schrijf het doelbegrip naar de index
    doel = maak_begrip(**{"begrip-id": "BWBR0004770/art9/lid1/persoon", "begripsnaam": "persoon"})
    (project / "begrippen" / "persoon.yaml").write_text(yaml.dump(doel, allow_unicode=True))
    data = maak_begrip(
        relaties={"is-een": ["BWBR0004770/art9/lid1/persoon"], "heeft": [], "leidt-tot": []},
        markeringen=[], **{"definitie-gebaseerd-op": []},
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert not any("is-een" in e for e in errors)


# ===== validate_integrity_regel =====

def test_regel_leeg_project_geen_fouten(tmp_path):
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    data = maak_regel(invoer=[], uitvoer=[])  # geen cross-references → geen fouten
    idx = build_begrip_index(project)
    assert validate_integrity_regel(data, DUMMY, idx, project) == []


def test_regel_invoer_ontbreekt_geeft_fout(tmp_path):
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    data = maak_regel(invoer=["BWBR0004770/art9/lid1/ontbrekend-begrip"])
    idx = build_begrip_index(project)
    errors = validate_integrity_regel(data, DUMMY, idx, project)
    assert any("invoer" in e for e in errors)


def test_regel_uitvoer_ontbreekt_geeft_fout(tmp_path):
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    data = maak_regel(uitvoer=["BWBR0004770/art9/lid1/ontbrekend"])
    idx = build_begrip_index(project)
    errors = validate_integrity_regel(data, DUMMY, idx, project)
    assert any("uitvoer" in e for e in errors)


def test_regel_vervangt_niet_gevonden_geeft_fout(tmp_path):
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    data = maak_regel(**{"vervangt-regel-id": "r-bestaat-niet"})
    idx = build_begrip_index(project)
    errors = validate_integrity_regel(data, DUMMY, idx, project)
    assert any("vervangt-regel-id" in e for e in errors)


def test_regel_vervangt_gevonden_geen_fout(tmp_path):
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    (project / "regels" / "r-oud.yaml").write_text("regel-id: r-oud\n")
    data = maak_regel(**{"vervangt-regel-id": "r-oud"})
    idx = build_begrip_index(project)
    errors = validate_integrity_regel(data, DUMMY, idx, project)
    assert not any("vervangt-regel-id" in e for e in errors)
