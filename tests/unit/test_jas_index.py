import json
from pathlib import Path

import pytest
import yaml

from jas_index_lib import (
    haal_kern,
    haal_contexten,
    bouw_jas_index,
    load_yaml,
    load_json,
    slug_from_begrip_id,
    stub_annotatie_index,
    stub_annotatie_lid,
    stub_annotatierij,
    stub_begrip,
    stub_regel,
    stub_voorbeeldreeks,
    schrijf_yaml,
    schrijf_json,
)


# ---------- haal_kern ----------

def test_haal_kern_dict_met_kern():
    assert haal_kern({"kern": "de belastingplichtige"}) == "de belastingplichtige"


def test_haal_kern_dict_zonder_kern():
    assert haal_kern({}) == ""


def test_haal_kern_dict_kern_none():
    assert haal_kern({"kern": None}) == ""


def test_haal_kern_legacy_string():
    assert haal_kern("legacy definitie") == "legacy definitie"


def test_haal_kern_none():
    assert haal_kern(None) == ""


def test_haal_kern_stript_whitespace():
    assert haal_kern({"kern": "  spaties  "}) == "spaties"


def test_haal_kern_lege_string():
    assert haal_kern("") == ""


# ---------- haal_contexten ----------

def test_haal_contexten_dict_met_contexten():
    ctx = [{"markering-id": "m-001", "tekst": "in het kader van art. 9"}]
    assert haal_contexten({"kern": "x", "contexten": ctx}) == ctx


def test_haal_contexten_dict_zonder_contexten():
    assert haal_contexten({"kern": "x"}) == []


def test_haal_contexten_contexten_none():
    assert haal_contexten({"kern": "x", "contexten": None}) == []


def test_haal_contexten_legacy_string():
    assert haal_contexten("legacy") == []


def test_haal_contexten_none():
    assert haal_contexten(None) == []


def test_haal_contexten_lege_lijst():
    assert haal_contexten({"contexten": []}) == []


def test_haal_contexten_geeft_kopie():
    ctx = [{"markering-id": "m-001"}]
    result = haal_contexten({"contexten": ctx})
    result.append({"markering-id": "m-002"})
    assert len(haal_contexten({"contexten": ctx})) == 1


# ---------- bouw_jas_index ----------

def test_bouw_jas_index_leeg_als_annotaties_dir_niet_bestaat(tmp_path):
    idx = bouw_jas_index(tmp_path)
    assert idx == {}


def test_bouw_jas_index_leeg_als_dir_leeg_is(tmp_path):
    (tmp_path / "annotaties").mkdir()
    idx = bouw_jas_index(tmp_path)
    assert idx == {}


def test_bouw_jas_index_bouwt_index_uit_annotatierijen(tmp_path):
    (tmp_path / "annotaties").mkdir()
    data = {
        "annotatierijen": [
            {"begrip-id": "BWBR0004770/art9/lid1/belastingschuldige", "jas-klasse": "rechtssubject"},
            {"begrip-id": "BWBR0004770/art9/lid1/betalingstermijn", "jas-klasse": "tijdsaanduiding"},
        ]
    }
    (tmp_path / "annotaties" / "art9-1.json").write_text(json.dumps(data))
    idx = bouw_jas_index(tmp_path)
    assert idx["BWBR0004770/art9/lid1/belastingschuldige"] == "rechtssubject"
    assert idx["BWBR0004770/art9/lid1/betalingstermijn"] == "tijdsaanduiding"


def test_bouw_jas_index_json_decode_fout_overgeslagen(tmp_path):
    (tmp_path / "annotaties").mkdir()
    (tmp_path / "annotaties" / "kapot.json").write_text("{{geen json")
    idx = bouw_jas_index(tmp_path)
    assert idx == {}


def test_bouw_jas_index_hidden_file_overgeslagen(tmp_path):
    (tmp_path / "annotaties").mkdir()
    verborgen_dir = tmp_path / "annotaties" / ".verborgen"
    verborgen_dir.mkdir()
    data = {"annotatierijen": [{"begrip-id": "x", "jas-klasse": "variabele"}]}
    (verborgen_dir / "test.json").write_text(json.dumps(data))
    idx = bouw_jas_index(tmp_path)
    assert "x" not in idx


def test_bouw_jas_index_eerste_jas_klasse_wint(tmp_path):
    (tmp_path / "annotaties").mkdir()
    data1 = {"annotatierijen": [{"begrip-id": "test/begrip", "jas-klasse": "rechtssubject"}]}
    data2 = {"annotatierijen": [{"begrip-id": "test/begrip", "jas-klasse": "variabele"}]}
    (tmp_path / "annotaties" / "art1.json").write_text(json.dumps(data1))
    (tmp_path / "annotaties" / "art2.json").write_text(json.dumps(data2))
    idx = bouw_jas_index(tmp_path)
    assert idx["test/begrip"] == "rechtssubject"


# ---------- load_yaml ----------

def test_load_yaml_geldig_bestand(tmp_path):
    f = tmp_path / "x.yaml"
    f.write_text("naam: Aanslag\nartikel: '9'\n", encoding="utf-8")
    assert load_yaml(f) == {"naam": "Aanslag", "artikel": "9"}


def test_load_yaml_ontbrekend_bestand_geeft_none(tmp_path):
    assert load_yaml(tmp_path / "weg.yaml") is None


def test_load_yaml_kapot_bestand_geeft_none(tmp_path, capsys):
    f = tmp_path / "kapot.yaml"
    f.write_text("a: [unterminated\n", encoding="utf-8")
    assert load_yaml(f) is None
    assert "load_yaml" in capsys.readouterr().err


def test_load_yaml_silent_false_raised(tmp_path):
    f = tmp_path / "kapot.yaml"
    f.write_text("a: [unterminated\n", encoding="utf-8")
    with pytest.raises(Exception):
        load_yaml(f, silent=False)


# ---------- load_json ----------

def test_load_json_geldig_bestand(tmp_path):
    f = tmp_path / "x.json"
    f.write_text(json.dumps({"bwb-id": "BWBR0004770"}), encoding="utf-8")
    assert load_json(f) == {"bwb-id": "BWBR0004770"}


def test_load_json_ontbrekend_bestand_geeft_none(tmp_path):
    assert load_json(tmp_path / "weg.json") is None


def test_load_json_kapot_bestand_geeft_none(tmp_path, capsys):
    f = tmp_path / "kapot.json"
    f.write_text("{niet json", encoding="utf-8")
    assert load_json(f) is None
    assert "load_json" in capsys.readouterr().err


def test_load_json_silent_false_raised(tmp_path):
    f = tmp_path / "kapot.json"
    f.write_text("{niet json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_json(f, silent=False)


# ---------- slug_from_begrip_id ----------

def test_slug_from_begrip_id_pad():
    assert slug_from_begrip_id("BWBR0004770/art9/lid1/foo") == "foo"


def test_slug_from_begrip_id_par():
    assert slug_from_begrip_id("BWBR0024096/par9-5/bar") == "bar"


def test_slug_from_begrip_id_trailing_slash():
    assert slug_from_begrip_id("BWBR0004770/art9/lid1/foo/") == "foo"


def test_slug_from_begrip_id_zonder_pad():
    assert slug_from_begrip_id("losse-slug") == "losse-slug"


def test_slug_from_begrip_id_leeg():
    assert slug_from_begrip_id("") == ""


# ---------- stub_annotatie_index ----------

def test_stub_annotatie_index_basisvelden():
    result = stub_annotatie_index("BWBR0004770", "IW 1990", "9", "2026-01-01", "H1 > Art 9")
    assert result["artikel-id"] == "BWBR0004770/art9"
    assert result["bwb-id"] == "BWBR0004770"
    assert result["leden-annotaties"] == []
    assert result["kruisreferenties"] == []


def test_stub_annotatie_index_met_kruisreferenties():
    refs = ["BWBR0002657/art1"]
    result = stub_annotatie_index("BWBR0004770", "IW 1990", "9", "2026-01-01", "H1", refs)
    assert result["kruisreferenties"] == refs


def test_stub_annotatie_index_kruisreferenties_none():
    result = stub_annotatie_index("BWBR0004770", "IW 1990", "9", "2026-01-01", "H1", None)
    assert result["kruisreferenties"] == []


# ---------- stub_annotatie_lid ----------

def test_stub_annotatie_lid_basisvelden():
    result = stub_annotatie_lid("BWBR0004770", "IW 1990", "9", "1", "2026-01-01", "H1 > Art 9", "De tekst.")
    assert result["annotatie-id"] == "BWBR0004770/art9/lid1"
    assert result["wetstekst"] == "De tekst."
    assert result["annotatierijen"] == []
    assert result["kruisreferenties"] == []


def test_stub_annotatie_lid_artikel_en_lid():
    result = stub_annotatie_lid("BWBR0004770", "IW", "2", "2", "2026-01-01", "H1", "tekst")
    assert result["artikel"] == "2"
    assert result["lid"] == "2"


# ---------- stub_annotatierij ----------

def test_stub_annotatierij_basisvelden():
    result = stub_annotatierij("r-001", "de belastingplichtige", "rechtssubject",
                                "grammaticaal", "BWBR/art9/lid1/bp", "rechtssubject-toelichting")
    assert result["rij-id"] == "r-001"
    assert result["jas-klasse"] == "rechtssubject"
    assert result["signalering"] is None


def test_stub_annotatierij_met_signalering():
    result = stub_annotatierij("r-001", "tekst", "variabele", "grammaticaal",
                                "BWBR/art9/lid1/x", "variabele-toelichting", "A5")
    assert result["signalering"] == "A5"


def test_stub_annotatierij_none_waarden_doorgestuurd():
    result = stub_annotatierij("r-001", "tekst", None, None, "BWBR/art9/lid1/x", "")
    assert result["jas-klasse"] is None
    assert result["interpretatiemethode"] is None


# ---------- stub_begrip ----------

def test_stub_begrip_basisstructuur():
    result = stub_begrip("BWBR0004770", "9", "1", "belastingschuldige",
                          "rechtssubject", "de belastingschuldige", "grammaticaal", "2026-01-01")
    assert result["begrip-id"] == "BWBR0004770/art9/lid1/belastingschuldige"
    assert result["herkomst"] == "direct"
    assert result["status"] == "concept"
    assert result["definitie"] == {"kern": "", "contexten": []}
    assert len(result["markeringen"]) == 1


def test_stub_begrip_afleidingsregel_herkomst_afgeleid():
    result = stub_begrip("BWBR0004770", "9", "1", "invorderbaarheid",
                          "afleidingsregel", "is invorderbaar", "grammaticaal", "2026-01-01")
    assert result["herkomst"] == "afgeleid"


def test_stub_begrip_toelichting_klasse_placeholder():
    result = stub_begrip("BWBR0004770", "9", "1", "slug", "variabele", "tekst", "grammaticaal", "2026-01-01")
    assert "stub" in result["toelichting-klasse"]


def test_stub_begrip_toelichting_klasse_opgegeven():
    result = stub_begrip("BWBR0004770", "9", "1", "slug", "variabele", "tekst",
                          "grammaticaal", "2026-01-01", toelichting_klasse="mijn toelichting")
    assert result["toelichting-klasse"] == "mijn toelichting"


# ---------- stub_regel ----------

def test_stub_regel_basisvelden():
    result = stub_regel("BWBR0004770", "9", "1", "a", "bepalen invorderbaarheid", "Beslissingsregel", "2026-01-01")
    assert result["regel-id"] == "AR-BWBR0004770-art9-lid1-a"
    assert result["soort"] == "Beslissingsregel"
    assert result["invoer"] == []
    assert result["uitvoer"] == []
    assert result["tussenresultaat"] is False


def test_stub_regel_met_rechtsfeit_id():
    result = stub_regel("BWBR0004770", "9", "1", "a", "naam", "Beslissingsregel", "2026-01-01", "rf-001")
    assert result["rechtsfeit-id"] == "rf-001"


def test_stub_regel_annotatie_id():
    result = stub_regel("BWBR0004770", "9", "1", "a", "naam", "Beslissingsregel", "2026-01-01")
    assert result["annotatie-id"] == "BWBR0004770/art9/lid1"


# ---------- stub_voorbeeldreeks ----------

def test_stub_voorbeeldreeks_basisvelden():
    result = stub_voorbeeldreeks("AR-BWBR0004770-art9-lid1-a", "naam", "2026-01-01", "2026-05-01")
    assert result["voorbeeldreeks-id"] == "VR-BWBR0004770-art9-lid1-a"
    assert result["afleidingsregel-id"] == "AR-BWBR0004770-art9-lid1-a"
    assert result["status"] == "concept"
    assert result["kolommen"] == []


def test_stub_voorbeeldreeks_geen_ar_prefix_geeft_valueerror():
    with pytest.raises(ValueError, match="AR-"):
        stub_voorbeeldreeks("VR-fout", "naam", "2026-01-01", "2026-05-01")


def test_stub_voorbeeldreeks_naam_en_datums():
    result = stub_voorbeeldreeks("AR-BWBR-art1-lid1-a", "mijn naam", "2026-01-01", "2026-03-15")
    assert result["naam"] == "mijn naam"
    assert result["peildatum"] == "2026-01-01"
    assert result["aangemaakt-op"] == "2026-03-15"


# ---------- schrijf_yaml ----------

def test_schrijf_yaml_maakt_bestand(tmp_path):
    pad = tmp_path / "test.yaml"
    schrijf_yaml(pad, {"naam": "belastingplichtige", "soort": "entiteit"})
    assert pad.exists()
    geladen = yaml.safe_load(pad.read_text())
    assert geladen["naam"] == "belastingplichtige"


def test_schrijf_yaml_maakt_parent_aan(tmp_path):
    pad = tmp_path / "sub" / "test.yaml"
    schrijf_yaml(pad, {"x": 1})
    assert pad.exists()


def test_schrijf_yaml_unicode_bewaard(tmp_path):
    pad = tmp_path / "test.yaml"
    schrijf_yaml(pad, {"naam": "naïviteit"})
    tekst = pad.read_text(encoding="utf-8")
    assert "naïviteit" in tekst


# ---------- schrijf_json ----------

def test_schrijf_json_maakt_bestand(tmp_path):
    pad = tmp_path / "test.json"
    schrijf_json(pad, {"bwb-id": "BWBR0004770"})
    assert pad.exists()
    import json as _json
    geladen = _json.loads(pad.read_text())
    assert geladen["bwb-id"] == "BWBR0004770"


def test_schrijf_json_maakt_parent_aan(tmp_path):
    pad = tmp_path / "sub" / "test.json"
    schrijf_json(pad, {"x": 1})
    assert pad.exists()


def test_schrijf_json_eindigt_met_newline(tmp_path):
    pad = tmp_path / "test.json"
    schrijf_json(pad, {"x": 1})
    assert pad.read_text().endswith("\n")
