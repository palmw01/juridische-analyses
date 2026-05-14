"""Tests voor sitegen/pages/regels.py."""
from html import escape
from pathlib import Path

from sitegen.pages.regels import gen_regels


def _regel(**overrides) -> dict:
    base = {
        "id": "AR-0001",
        "naam": "Berekening betalingstermijn",
        "soort": "Rekenregel",
        "formele_regel": "betalingstermijn = 30 dagen na dagtekening aanslag",
        "toelichting": "Standaard betalingstermijn.",
        "invoer": [],
        "uitvoer": ["BWBR0004770/art9/lid1/betalingstermijn"],
        "operators": [],
        "voorbeeldreeksen": [],
        "tussenresultaat": False,
        "bwb_id": "BWBR0004770",
        "artikel": "9",
        "lid": "1",
        "peildatum": "2026-01-01",
        "annotatie_id": "BWBR0004770/art9/lid1",
        "rechtsfeit_id": "",
        "vervangt_regel_id": "",
        "geldigheid_van": "2026-01-01",
        "geldigheid_tot": "",
        "prioriteit": None,
    }
    base.update(overrides)
    return base


# ===== lijstpagina =====

def test_gen_regels_maakt_regels_html(tmp_path):
    gen_regels(tmp_path, [], [], [])
    assert (tmp_path / "regels.html").exists()


def test_gen_regels_lijst_toont_naam(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [])
    content = (tmp_path / "regels.html").read_text()
    assert "Berekening betalingstermijn" in content


def test_gen_regels_lijst_toont_geldigheid_van(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [])
    content = (tmp_path / "regels.html").read_text()
    assert "Geldig vanaf" in content
    assert "2026-01-01" in content


def test_gen_regels_lijst_toont_soort_badge(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [])
    content = (tmp_path / "regels.html").read_text()
    assert "Rekenregel" in content


# ===== detailpagina =====

def test_gen_regels_detail_maakt_bestand(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [])
    assert (tmp_path / "regels" / "AR-0001.html").exists()


def test_gen_regels_detail_toont_formele_regel(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [])
    content = (tmp_path / "regels" / "AR-0001.html").read_text()
    assert "betalingstermijn = 30 dagen" in content


def test_gen_regels_detail_toont_annotatie_id(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [])
    content = (tmp_path / "regels" / "AR-0001.html").read_text()
    assert "Annotatie-id" in content
    assert "BWBR0004770/art9/lid1" in content


def test_gen_regels_detail_geen_annotatie_id_geen_rij(tmp_path):
    gen_regels(tmp_path, [_regel(annotatie_id="")], [], [])
    content = (tmp_path / "regels" / "AR-0001.html").read_text()
    assert "Annotatie-id" not in content


def test_gen_regels_detail_toont_geldig_vanaf(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [])
    content = (tmp_path / "regels" / "AR-0001.html").read_text()
    assert "Geldig vanaf" in content
    assert "2026-01-01" in content


def test_gen_regels_detail_tussenresultaat_ja(tmp_path):
    gen_regels(tmp_path, [_regel(tussenresultaat=True)], [], [])
    content = (tmp_path / "regels" / "AR-0001.html").read_text()
    assert "Ja" in content


def test_gen_regels_detail_tussenresultaat_nee(tmp_path):
    gen_regels(tmp_path, [_regel(tussenresultaat=False)], [], [])
    content = (tmp_path / "regels" / "AR-0001.html").read_text()
    assert "Nee" in content
