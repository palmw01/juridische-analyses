import json
from pathlib import Path

from jas_index_lib import haal_kern, haal_contexten, bouw_jas_index


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
