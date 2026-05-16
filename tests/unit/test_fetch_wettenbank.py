"""Tests voor tools/fetch_wettenbank.py — pure functies en CLI."""
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from fetch_wettenbank import (
    load_input,
    validate_response,
    normalize_artikel,
    normalize,
    write_output,
    main,
)


VALIDE_DATA = {
    "bwbId": "BWBR0004770",
    "citeertitel": "Invorderingswet 1990",
    "artikel": "9",
    "versiedatum": "2024-01-01",
    "pad": "Hoofdstuk II > Afdeling 1 > Artikel 9",
    "leden": [{"lid": "1", "tekst": "De belastingaanslag..."}],
    "bronreferentie": "https://wetten.overheid.nl/BWBR0004770/art9",
}


# ===== load_input =====

def test_load_input_van_bestand(tmp_path):
    pad = tmp_path / "input.json"
    pad.write_text(json.dumps(VALIDE_DATA))
    result = load_input(str(pad))
    assert result["bwbId"] == "BWBR0004770"


def test_load_input_van_stdin(tmp_path, monkeypatch):
    import io
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(
        io.BytesIO(json.dumps(VALIDE_DATA).encode())))
    result = load_input(None)
    assert result["artikel"] == "9"


def test_load_input_ongeldige_json_bestand(tmp_path):
    pad = tmp_path / "bad.json"
    pad.write_text("dit is geen json{{{")
    with pytest.raises(SystemExit) as exc:
        load_input(str(pad))
    assert exc.value.code == 1


def test_load_input_bestand_niet_gevonden():
    with pytest.raises(SystemExit) as exc:
        load_input("/tmp/bestaat_niet_xyz_abc.json")
    assert exc.value.code == 1


def test_load_input_stdin_ongeldige_json(monkeypatch):
    import io
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(
        io.BytesIO(b"geen json")))
    with pytest.raises(SystemExit) as exc:
        load_input(None)
    assert exc.value.code == 1


# ===== validate_response =====

def test_validate_response_valide():
    validate_response(VALIDE_DATA)  # geen exception


def test_validate_response_ontbrekend_bwb_id():
    data = {k: v for k, v in VALIDE_DATA.items() if k != "bwbId"}
    with pytest.raises(SystemExit) as exc:
        validate_response(data)
    assert exc.value.code == 1


def test_validate_response_ontbrekend_artikel():
    data = {k: v for k, v in VALIDE_DATA.items() if k != "artikel"}
    with pytest.raises(SystemExit) as exc:
        validate_response(data)
    assert exc.value.code == 1


def test_validate_response_ontbrekende_leden():
    data = {k: v for k, v in VALIDE_DATA.items() if k != "leden"}
    with pytest.raises(SystemExit) as exc:
        validate_response(data)
    assert exc.value.code == 1


# ===== normalize_artikel =====

def test_normalize_artikel_trim():
    assert normalize_artikel("  9  ") == "9"


def test_normalize_artikel_lowercase_bewaard():
    assert normalize_artikel("9a") == "9a"


def test_normalize_artikel_geen_wijziging():
    assert normalize_artikel("9") == "9"


# ===== normalize =====

def test_normalize_vult_velden():
    record = normalize(VALIDE_DATA)
    assert record["bwb-id"] == "BWBR0004770"
    assert "wet" not in record
    assert record["artikel"] == "9"
    assert record["citeertitel"] == "Invorderingswet 1990"
    assert record["versiedatum"] == "2024-01-01"
    assert record["pad"] == "Hoofdstuk II > Afdeling 1 > Artikel 9"
    assert "structuurpositie" not in record
    assert record["leden"] == VALIDE_DATA["leden"]
    assert record["bronreferentie"] == VALIDE_DATA["bronreferentie"]
    assert "opgehaald-op" in record


def test_normalize_ontbrekende_optionele_velden():
    data = {"bwbId": "BWBR0004770", "artikel": "9", "leden": []}
    record = normalize(data)
    assert record["citeertitel"] == ""
    assert record["versiedatum"] == ""
    assert record["pad"] == ""
    assert record["bronreferentie"] == ""


def test_normalize_geeft_sectie_en_formaat_door():
    data = {**VALIDE_DATA, "sectie": "Artikel 9", "formaat": "markdown"}
    record = normalize(data)
    assert record["sectie"] == "Artikel 9"
    assert record["formaat"] == "markdown"


def test_normalize_zonder_sectie_en_formaat():
    record = normalize(VALIDE_DATA)
    assert "sectie" not in record
    assert "formaat" not in record


# ===== write_output =====

def test_write_output_maakt_bestand(tmp_path):
    record = normalize(VALIDE_DATA)
    pad = write_output(record, tmp_path, force=False)
    assert pad.exists()
    with pad.open() as f:
        data = json.load(f)
    assert data["bwb-id"] == "BWBR0004770"
    assert pad == tmp_path / "bronnen" / "BWBR0004770" / "art9.json"


def test_write_output_al_aanwezig_geen_force(tmp_path):
    record = normalize(VALIDE_DATA)
    write_output(record, tmp_path, force=False)
    with pytest.raises(SystemExit) as exc:
        write_output(record, tmp_path, force=False)
    assert exc.value.code == 0


def test_write_output_force_overschrijft(tmp_path):
    record = normalize(VALIDE_DATA)
    write_output(record, tmp_path, force=False)
    # Tweede keer met force mag niet falen
    pad2 = write_output(record, tmp_path, force=True)
    assert pad2.exists()


# ===== main =====

def test_main_succes(tmp_path):
    pad = tmp_path / "input.json"
    pad.write_text(json.dumps(VALIDE_DATA))
    with patch("sys.argv", ["fetch_wettenbank.py", "--input", str(pad), "--project-dir", str(tmp_path)]):
        main()
    output = tmp_path / "bronnen" / "BWBR0004770" / "art9.json"
    assert output.exists()


def test_main_project_root_niet_gevonden(tmp_path):
    pad = tmp_path / "input.json"
    pad.write_text(json.dumps(VALIDE_DATA))
    with patch("sys.argv", ["fetch_wettenbank.py", "--input", str(pad), "--project-dir", "/bestaat_niet_xyz"]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 1


def test_main_met_kruisrefs_succes(tmp_path):
    pad = tmp_path / "input.json"
    pad.write_text(json.dumps(VALIDE_DATA))
    mock_result = MagicMock()
    mock_result.returncode = 0
    with patch("sys.argv", ["fetch_wettenbank.py", "--input", str(pad),
                             "--project-dir", str(tmp_path), "--kruisrefs"]):
        with patch("subprocess.run", return_value=mock_result):
            main()
    output = tmp_path / "bronnen" / "BWBR0004770" / "art9.json"
    assert output.exists()


def test_main_met_kruisrefs_fout(tmp_path):
    pad = tmp_path / "input.json"
    pad.write_text(json.dumps(VALIDE_DATA))
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "extract_kruisrefs fout"
    with patch("sys.argv", ["fetch_wettenbank.py", "--input", str(pad),
                             "--project-dir", str(tmp_path), "--kruisrefs"]):
        with patch("subprocess.run", return_value=mock_result):
            main()
    output = tmp_path / "bronnen" / "BWBR0004770" / "art9.json"
    assert output.exists()
