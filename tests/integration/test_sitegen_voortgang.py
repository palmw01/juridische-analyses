"""Tests voor sitegen/pages/voortgang.py."""
from pathlib import Path

import pytest

from sitegen.pages.voortgang import (
    _heeft_kern,
    _heeft_relaties,
    _bouw_lid_index,
    _cel,
    _status_a2,
    _status_a3a,
    _status_a3b,
    _status_a3c,
    _status_a3d,
    _status_a4b,
    gen_voortgang,
    STATUS_LEEG,
    STATUS_STUB,
    STATUS_COMPLEET,
    STATUS_WAARSCHUWING,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _begrip(bid="BWBR0004770/art9/lid1/belastingschuldige", definitie="", relaties=None, **extra):
    return {
        "id": bid,
        "definitie": definitie,
        "relaties": relaties or {"is-een": [], "heeft": [], "leidt-tot": []},
        "jas_klasse": extra.get("jas_klasse", "rechtssubject"),
        "afleidingsregel-id": extra.get("afleidingsregel-id"),
        "scenario_refs": extra.get("scenario_refs", []),
        "bronnen_secundair": extra.get("bronnen_secundair", []),
        "markeringen": extra.get("markeringen", []),
    }


def _regel(rid="AR-BWBR0004770-art9-lid1-a", bwb="BWBR0004770", artikel="9", lid="1"):
    return {"id": rid, "bwb_id": bwb, "artikel": artikel, "lid": lid}


def _vr(vr_id="VR-BWBR0004770-art9-lid1-a", ar_id="AR-BWBR0004770-art9-lid1-a", kolommen=None):
    return {
        "id": vr_id,
        "afleidingsregel_id": ar_id,
        "kolommen": kolommen or [],
    }


_SENTINEL = object()

def _annotatie(bwb="BWBR0004770", artikel="9", lid="1", wet="IW 1990", rijen=_SENTINEL):
    return {
        "id": f"{bwb}/art{artikel}/lid{lid}",
        "bwb_id": bwb,
        "wet": wet,
        "artikel": artikel,
        "lid": lid,
        "rijen": [{"rij_id": "r1"}] if rijen is _SENTINEL else rijen,
    }


# ---------------------------------------------------------------------------
# _heeft_kern
# ---------------------------------------------------------------------------

def test_heeft_kern_met_tekst():
    assert _heeft_kern({"definitie": "de belastingplichtige"})


def test_heeft_kern_leeg():
    assert not _heeft_kern({"definitie": ""})


def test_heeft_kern_none():
    assert not _heeft_kern({"definitie": None})


def test_heeft_kern_ontbreekt():
    assert not _heeft_kern({})


# ---------------------------------------------------------------------------
# _heeft_relaties
# ---------------------------------------------------------------------------

def test_heeft_relaties_heeft_relatie():
    b = {"relaties": {"is-een": [], "heeft": ["BWBR/art9/lid1/x"], "leidt-tot": []}}
    assert _heeft_relaties(b)


def test_heeft_relaties_alle_leeg():
    b = {"relaties": {"is-een": [], "heeft": [], "leidt-tot": []}}
    assert not _heeft_relaties(b)


def test_heeft_relaties_ontbreekt():
    assert not _heeft_relaties({})


def test_heeft_relaties_is_een():
    b = {"relaties": {"is-een": ["x"], "heeft": [], "leidt-tot": []}}
    assert _heeft_relaties(b)


# ---------------------------------------------------------------------------
# _bouw_lid_index
# ---------------------------------------------------------------------------

def test_bouw_lid_index_begrip_art_lid():
    b = _begrip("BWBR0004770/art9/lid1/foo")
    per_lid = _bouw_lid_index([b], [], [])
    assert ("BWBR0004770", "9", "1") in per_lid


def test_bouw_lid_index_begrip_te_kort_overgeslagen():
    b = _begrip("BWBR0004770/art9")
    per_lid = _bouw_lid_index([b], [], [])
    assert len(per_lid) == 0


def test_bouw_lid_index_begrip_par():
    b = _begrip("BWBR0004770/par9-1/foo")
    per_lid = _bouw_lid_index([b], [], [])
    assert ("BWBR0004770", "par9-1", "") in per_lid


def test_bouw_lid_index_begrip_onbekend_patroon_overgeslagen():
    b = _begrip("BWBR0004770/onbekend/foo/bar")
    per_lid = _bouw_lid_index([b], [], [])
    assert len(per_lid) == 0


def test_bouw_lid_index_regel_toegevoegd():
    r = _regel()
    per_lid = _bouw_lid_index([], [r], [])
    assert ("BWBR0004770", "9", "1") in per_lid
    assert r in per_lid[("BWBR0004770", "9", "1")]["regels"]


def test_bouw_lid_index_voorbeeldreeks_gekoppeld_aan_regel():
    r = _regel()
    vr = _vr()
    per_lid = _bouw_lid_index([], [r], [vr])
    assert vr in per_lid[("BWBR0004770", "9", "1")]["voorbeeldreeksen"]


def test_bouw_lid_index_vr_zonder_regel_niet_opgenomen():
    vr = _vr(ar_id="AR-ONBEKEND")
    per_lid = _bouw_lid_index([], [], [vr])
    assert len(per_lid) == 0


# ---------------------------------------------------------------------------
# _cel
# ---------------------------------------------------------------------------

def test_cel_leeg():
    html = _cel(STATUS_LEEG)
    assert "cel-leeg" in html


def test_cel_compleet():
    html = _cel(STATUS_COMPLEET)
    assert "cel-compleet" in html


def test_cel_stub():
    html = _cel(STATUS_STUB)
    assert "cel-stub" in html


def test_cel_waarschuwing():
    html = _cel(STATUS_WAARSCHUWING)
    assert "cel-waarschuwing" in html


def test_cel_met_telling():
    html = _cel(STATUS_COMPLEET, 3)
    assert "3" in html


def test_cel_onbekende_status_valt_terug_op_leeg():
    html = _cel("onbekend")
    assert "cel-leeg" in html


# ---------------------------------------------------------------------------
# _status_a2
# ---------------------------------------------------------------------------

def test_status_a2_compleet_bij_rijen():
    a = _annotatie(rijen=[{"rij_id": "r1"}])
    assert _status_a2([a], "BWBR0004770", "9", "1") == STATUS_COMPLEET


def test_status_a2_stub_bij_geen_rijen():
    a = _annotatie(rijen=[])
    assert _status_a2([a], "BWBR0004770", "9", "1") == STATUS_STUB


def test_status_a2_leeg_bij_geen_annotatie():
    assert _status_a2([], "BWBR0004770", "9", "1") == STATUS_LEEG


def test_status_a2_ander_bwb_overgeslagen():
    a = _annotatie(bwb="ANDER", rijen=[{"rij_id": "r1"}])
    assert _status_a2([a], "BWBR0004770", "9", "1") == STATUS_LEEG


# ---------------------------------------------------------------------------
# _status_a3a
# ---------------------------------------------------------------------------

def test_status_a3a_leeg_zonder_begrippen():
    assert _status_a3a([]) == STATUS_LEEG


def test_status_a3a_stub_geen_kern_geen_relaties():
    b = _begrip(definitie="")
    assert _status_a3a([b]) == STATUS_STUB


def test_status_a3a_compleet_kern_en_relaties():
    b = _begrip(definitie="def", relaties={"is-een": [], "heeft": ["x"], "leidt-tot": []})
    assert _status_a3a([b]) == STATUS_COMPLEET


def test_status_a3a_waarschuwing_deels_afgerond():
    b1 = _begrip("BWBR0004770/art9/lid1/a", definitie="def",
                  relaties={"is-een": [], "heeft": ["x"], "leidt-tot": []})
    b2 = _begrip("BWBR0004770/art9/lid1/b", definitie="")
    assert _status_a3a([b1, b2]) == STATUS_WAARSCHUWING


# ---------------------------------------------------------------------------
# _status_a3b
# ---------------------------------------------------------------------------

def test_status_a3b_leeg_geen_afl_begrippen_geen_regels():
    b = _begrip(jas_klasse="rechtssubject")
    assert _status_a3b([b], []) == STATUS_LEEG


def test_status_a3b_compleet_afl_begrip_heeft_gekoppelde_regel():
    r = _regel()
    b = _begrip(jas_klasse="afleidingsregel", **{"afleidingsregel-id": "AR-BWBR0004770-art9-lid1-a"})
    assert _status_a3b([b], [r]) == STATUS_COMPLEET


def test_status_a3b_stub_afl_begrip_zonder_regel():
    b = _begrip(jas_klasse="afleidingsregel", **{"afleidingsregel-id": "AR-BWBR0004770-art9-lid1-a"})
    assert _status_a3b([b], []) == STATUS_STUB


def test_status_a3b_waarschuwing_deels_gekoppeld():
    r = _regel()
    b1 = _begrip("BWBR0004770/art9/lid1/a", jas_klasse="afleidingsregel",
                  **{"afleidingsregel-id": "AR-BWBR0004770-art9-lid1-a"})
    b2 = _begrip("BWBR0004770/art9/lid1/b", jas_klasse="afleidingsregel",
                  **{"afleidingsregel-id": "AR-ONTBREEKT"})
    assert _status_a3b([b1, b2], [r]) == STATUS_WAARSCHUWING


def test_status_a3b_compleet_bij_regels_maar_geen_afl_begrippen():
    r = _regel()
    assert _status_a3b([], [r]) == STATUS_COMPLEET


# ---------------------------------------------------------------------------
# _status_a3c
# ---------------------------------------------------------------------------

def test_status_a3c_leeg_geen_begrippen():
    assert _status_a3c([]) == STATUS_LEEG


def test_status_a3c_leeg_geen_kandidaten():
    b = _begrip(jas_klasse="variabele")
    assert _status_a3c([b]) == STATUS_LEEG


def test_status_a3c_stub_kandidaat_zonder_refs():
    b = _begrip(jas_klasse="rechtsbetrekking", scenario_refs=[])
    assert _status_a3c([b]) == STATUS_STUB


def test_status_a3c_compleet_alle_kandidaten_hebben_refs():
    b = _begrip(jas_klasse="rechtsfeit",
                scenario_refs=[{"scenario-id": "scen-001", "rol": "rechtssubject"}])
    assert _status_a3c([b]) == STATUS_COMPLEET


def test_status_a3c_waarschuwing_deels_gevuld():
    b1 = _begrip("BWBR0004770/art9/lid1/a", jas_klasse="rechtsbetrekking",
                  scenario_refs=[{"scenario-id": "scen-001", "rol": "rechtssubject"}])
    b2 = _begrip("BWBR0004770/art9/lid1/b", jas_klasse="rechtsfeit", scenario_refs=[])
    assert _status_a3c([b1, b2]) == STATUS_WAARSCHUWING


# ---------------------------------------------------------------------------
# _status_a3d
# ---------------------------------------------------------------------------

def test_status_a3d_leeg_geen_begrippen():
    assert _status_a3d([]) == STATUS_LEEG


def test_status_a3d_leeg_geen_secundaire_bronnen():
    b = _begrip(bronnen_secundair=[])
    assert _status_a3d([b]) == STATUS_LEEG


def test_status_a3d_compleet_alle_hebben_bronnen():
    b = _begrip(bronnen_secundair=[{"soort": "leidraad", "vindplaats": "§9.1"}])
    assert _status_a3d([b]) == STATUS_COMPLEET


def test_status_a3d_waarschuwing_deels_gevuld():
    b1 = _begrip("BWBR0004770/art9/lid1/a",
                  bronnen_secundair=[{"soort": "leidraad", "vindplaats": "§9.1"}])
    b2 = _begrip("BWBR0004770/art9/lid1/b", bronnen_secundair=[])
    assert _status_a3d([b1, b2]) == STATUS_WAARSCHUWING


# ---------------------------------------------------------------------------
# _status_a4b
# ---------------------------------------------------------------------------

def test_status_a4b_leeg_geen_regels():
    assert _status_a4b([], []) == STATUS_LEEG


def test_status_a4b_stub_geen_vr():
    r = _regel()
    assert _status_a4b([r], []) == STATUS_STUB


def test_status_a4b_compleet_geen_open_vragen():
    r = _regel()
    vr = _vr(kolommen=[{"is_voorspelling_juist": "ja"}])
    assert _status_a4b([r], [vr]) == STATUS_COMPLEET


def test_status_a4b_waarschuwing_open_vragen():
    r = _regel()
    vr = _vr(kolommen=[{"is_voorspelling_juist": "?"}])
    assert _status_a4b([r], [vr]) == STATUS_WAARSCHUWING


def test_status_a4b_waarschuwing_deels_gekoppeld():
    r1 = _regel("AR-BWBR0004770-art9-lid1-a")
    r2 = _regel("AR-BWBR0004770-art9-lid1-b")
    vr = _vr(ar_id="AR-BWBR0004770-art9-lid1-a", kolommen=[{"is_voorspelling_juist": "ja"}])
    assert _status_a4b([r1, r2], [vr]) == STATUS_WAARSCHUWING


# ---------------------------------------------------------------------------
# gen_voortgang (smoke test)
# ---------------------------------------------------------------------------

def test_gen_voortgang_maakt_html_bestand(tmp_path):
    annotaties = [_annotatie()]
    begrippen = [_begrip("BWBR0004770/art9/lid1/belastingschuldige")]
    regels = [_regel()]
    vrs = [_vr()]
    gen_voortgang(tmp_path, annotaties, begrippen, regels, vrs)
    assert (tmp_path / "voortgang.html").exists()


def test_gen_voortgang_bevat_tabelrijen(tmp_path):
    annotaties = [_annotatie()]
    begrippen = [_begrip("BWBR0004770/art9/lid1/belastingschuldige", definitie="def",
                          relaties={"is-een": [], "heeft": ["x"], "leidt-tot": []})]
    gen_voortgang(tmp_path, annotaties, begrippen, [], [])
    html = (tmp_path / "voortgang.html").read_text()
    assert "<tr>" in html
    assert "art. 9" in html


def test_gen_voortgang_lege_data(tmp_path):
    gen_voortgang(tmp_path, [], [], [], [])
    assert (tmp_path / "voortgang.html").exists()


def test_gen_voortgang_bevat_kpi_sectie(tmp_path):
    annotaties = [_annotatie()]
    gen_voortgang(tmp_path, annotaties, [], [], [])
    html = (tmp_path / "voortgang.html").read_text()
    assert "kpi" in html


def test_gen_voortgang_te_valideren_kpi(tmp_path):
    annotaties = [_annotatie()]
    begrippen = [_begrip("BWBR0004770/art9/lid1/belastingschuldige")]
    gen_voortgang(tmp_path, annotaties, begrippen, [], [])
    html = (tmp_path / "voortgang.html").read_text()
    assert "Te valideren" in html


def test_gen_voortgang_par_sectie_link(tmp_path):
    """Paragraaf-begrip geeft link naar sectie-annotatie."""
    b = _begrip("BWBR0024096/par9-1/belasting")
    gen_voortgang(tmp_path, [], [b], [], [])
    html = (tmp_path / "voortgang.html").read_text()
    assert "par9-1" in html


def test_gen_voortgang_annotatie_zonder_lid_geen_art_link(tmp_path):
    """Rij zonder artikel/lid toont bwb_id als label."""
    a = {
        "id": "BWBR0004770/par9-1",
        "bwb_id": "BWBR0004770",
        "wet": "IW 1990",
        "artikel": "",
        "lid": "",
        "rijen": [],
    }
    gen_voortgang(tmp_path, [a], [], [], [])
    html = (tmp_path / "voortgang.html").read_text()
    assert "BWBR0004770" in html
