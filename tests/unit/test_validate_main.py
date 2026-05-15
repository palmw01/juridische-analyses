"""Tests voor validate_note.main() CLI en resterende edge-cases."""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from validate_note import (
    main,
    validate_quality_begrip,
    validate_integrity_annotatie_lid,
    validate_integrity_regel,
    format_rapport_text,
    format_rapport_json,
    collect_files_for_schema,
    collect_all_files,
    detect_schema,
    ValidationResult,
    build_begrip_index,
)
from tests.fixtures.begrippen import maak_begrip
from tests.fixtures.regels import maak_regel
from tests.fixtures.annotaties import maak_annotatie

SCHEMAS_DIR = Path(__file__).resolve().parent.parent.parent / "schemas"


# ===== Edge cases kleine missing lines =====

def test_quality_begrip_kern_leeg_met_contexten_geeft_extra_warning():
    data = maak_begrip(
        definitie={"kern": "", "contexten": [{"markering-id": "m-001", "tekst": "context"}]},
    )
    warnings = validate_quality_begrip(data, Path("/tmp/test.yaml"))
    assert any("kern is leeg" in w for w in warnings)
    assert any("contexten" in w for w in warnings)


def test_integrity_annotatie_lid_non_dict_kant_overgeslagen():
    data = {
        "annotatierijen": [],
        "diagram": {
            "knopen": [{"id": "k1"}],
            "kanten": ["geen-dict"],
        },
    }
    errors = validate_integrity_annotatie_lid(data, Path("/tmp/test.json"), {})
    assert errors == []


def test_integrity_begrip_def_gebaseerd_op_lege_string_overgeslagen(tmp_path):
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "annotaties").mkdir()
    data = maak_begrip(**{"definitie-gebaseerd-op": ["", "m-001"]})
    idx = build_begrip_index(tmp_path)
    from validate_note import validate_integrity_begrip
    errors = validate_integrity_begrip(data, Path("/tmp/test.yaml"), idx, tmp_path)
    assert not any("definitie-gebaseerd-op" in e and "' '" in e for e in errors)


def test_integrity_regel_lege_bid_in_invoer_geen_fout(tmp_path):
    for d in ("begrippen", "regels", "annotaties"):
        (tmp_path / d).mkdir()
    data = maak_regel(invoer=[""])
    idx = build_begrip_index(tmp_path)
    errors = validate_integrity_regel(data, Path("/tmp/test.yaml"), idx, tmp_path)
    assert not any("invoer" in e for e in errors)


def test_detect_schema_annotatie_lid_md_met_letter(tmp_path):
    (tmp_path / "annotaties").mkdir()
    f = tmp_path / "annotaties" / "art9a-1.md"
    f.touch()
    assert detect_schema(f, tmp_path) == "annotatie-lid"


def test_collect_annotatie_lid_md_bestand(project_root):
    f = project_root / "annotaties" / "art9a-1.md"
    f.write_text("---\nannotatie-id: test\n---\n")
    files = collect_files_for_schema(project_root, "annotatie-lid")
    assert any("art9a-1" in fp.name for fp in files)


def test_collect_all_files_md_annotatie(project_root):
    f = project_root / "annotaties" / "art9a-1.md"
    f.write_text("---\nannotatie-id: test\n---\n")
    files = collect_all_files(project_root)
    schemas = [s for _, s in files]
    assert "annotatie-lid" in schemas


def test_format_rapport_text_filepath_buiten_project_met_fouten():
    r = ValidationResult(Path("/heel/ergens/anders/test.yaml"))
    r.errors.append("[L1] fout")
    tekst = format_rapport_text([r], Path("/tmp/project"), "2024-01-01")
    assert "fout" in tekst


def test_format_rapport_text_filepath_buiten_project_met_warnings():
    r = ValidationResult(Path("/heel/ergens/anders/test.yaml"))
    r.warnings.append("[L3] waarschuwing")
    tekst = format_rapport_text([r], Path("/tmp/project"), "2024-01-01")
    assert "waarschuwing" in tekst


def test_format_rapport_json_filepath_buiten_project():
    r = ValidationResult(Path("/heel/ergens/anders/test.yaml"))
    r.errors.append("[L1] fout")
    result = format_rapport_json([r], Path("/tmp/project"))
    assert len(result["fouten"]) == 1
    assert "/heel/" in result["fouten"][0]["bestand"]


# ===== main() CLI =====

def test_main_geen_args_exit_0(capsys):
    with patch.object(sys, "argv", ["validate_note.py"]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0


def test_main_full_valide_project(project_root):
    data = maak_begrip()
    (project_root / "begrippen" / "test.yaml").write_text(yaml.dump(data, allow_unicode=True))
    with patch.object(sys, "argv", ["validate_note.py", "--full", "--project-dir", str(project_root)]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0


def test_main_full_met_schema_fout_exit_1(project_root):
    kapot = {"begrip-id": None, "begripsnaam": "kapot"}
    (project_root / "begrippen" / "kapot.yaml").write_text(yaml.dump(kapot))
    with patch.object(sys, "argv", ["validate_note.py", "--full", "--project-dir", str(project_root)]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 1


def test_main_file_valide(project_root):
    data = maak_begrip()
    pad = project_root / "begrippen" / "test.yaml"
    pad.write_text(yaml.dump(data, allow_unicode=True))
    with patch.object(sys, "argv", ["validate_note.py", "--file", str(pad), "--project-dir", str(project_root)]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0


def test_main_file_bestaat_niet_exit_1(project_root, capsys):
    with patch.object(sys, "argv", ["validate_note.py", "--file", str(project_root / "bestaat-niet.yaml"), "--project-dir", str(project_root)]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 1


def test_main_file_zonder_schema_detectie_exit_1(project_root, capsys):
    (project_root / "overig").mkdir()
    f = project_root / "overig" / "test.yaml"
    f.write_text("key: value\n")
    with patch.object(sys, "argv", ["validate_note.py", "--file", str(f), "--project-dir", str(project_root)]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 1


def test_main_file_met_expliciet_schema(project_root):
    data = maak_begrip()
    pad = project_root / "begrippen" / "test.yaml"
    pad.write_text(yaml.dump(data, allow_unicode=True))
    with patch.object(sys, "argv", [
        "validate_note.py", "--file", str(pad),
        "--schema", "begrip", "--project-dir", str(project_root),
    ]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0


def test_main_file_json_output(project_root, capsys):
    data = maak_begrip()
    pad = project_root / "begrippen" / "test.yaml"
    pad.write_text(yaml.dump(data, allow_unicode=True))
    with patch.object(sys, "argv", [
        "validate_note.py", "--file", str(pad),
        "--project-dir", str(project_root), "--json",
    ]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0
    output = capsys.readouterr().out
    parsed = json.loads(output)
    assert "fouten" in parsed


def test_main_dir_valide(project_root):
    data = maak_begrip()
    (project_root / "begrippen" / "test.yaml").write_text(yaml.dump(data, allow_unicode=True))
    with patch.object(sys, "argv", [
        "validate_note.py", "--dir", str(project_root / "begrippen"),
        "--schema", "begrip", "--project-dir", str(project_root),
    ]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0


def test_main_dir_geen_bestanden(project_root):
    with patch.object(sys, "argv", [
        "validate_note.py", "--dir", str(project_root / "begrippen"),
        "--project-dir", str(project_root),
    ]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0


def test_main_full_schrijft_rapport(project_root):
    data = maak_begrip()
    (project_root / "begrippen" / "test.yaml").write_text(yaml.dump(data, allow_unicode=True))
    with patch.object(sys, "argv", ["validate_note.py", "--full", "--project-dir", str(project_root)]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0
    assert (project_root / "rapporten" / "validatie-rapport.md").exists()


def test_main_full_schrijft_json_rapport(project_root):
    data = maak_begrip()
    (project_root / "begrippen" / "test.yaml").write_text(yaml.dump(data, allow_unicode=True))
    with patch.object(sys, "argv", ["validate_note.py", "--full", "--project-dir", str(project_root)]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0
    json_pad = project_root / "rapporten" / "validatie-rapport.json"
    assert json_pad.exists()
    parsed = json.loads(json_pad.read_text())
    assert "waarschuwingen" in parsed
    assert "fouten" in parsed


def test_main_integrity_flag(project_root):
    data = maak_begrip()
    pad = project_root / "begrippen" / "test.yaml"
    pad.write_text(yaml.dump(data, allow_unicode=True))
    with patch.object(sys, "argv", [
        "validate_note.py", "--file", str(pad),
        "--project-dir", str(project_root), "--integrity",
    ]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0


def test_main_file_relatief_pad(project_root):
    data = maak_begrip()
    (project_root / "begrippen" / "test.yaml").write_text(yaml.dump(data, allow_unicode=True))
    with patch.object(sys, "argv", [
        "validate_note.py", "--file", "begrippen/test.yaml",
        "--project-dir", str(project_root),
    ]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0


def test_main_dir_relatief_pad(project_root):
    data = maak_begrip()
    (project_root / "begrippen" / "test.yaml").write_text(yaml.dump(data, allow_unicode=True))
    with patch.object(sys, "argv", [
        "validate_note.py", "--dir", "begrippen",
        "--schema", "begrip", "--project-dir", str(project_root),
    ]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0


def test_main_dir_slaat_index_md_over(project_root):
    (project_root / "begrippen" / "index.md").write_text("---\n---\n")
    with patch.object(sys, "argv", [
        "validate_note.py", "--dir", str(project_root / "begrippen"),
        "--project-dir", str(project_root),
    ]):
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 0


def test_main_schema_niet_gevonden_exit_1(project_root):
    data = maak_begrip()
    (project_root / "begrippen" / "test.yaml").write_text(yaml.dump(data, allow_unicode=True))
    with patch.object(sys, "argv", [
        "validate_note.py", "--full", "--project-dir", str(project_root),
    ]):
        (project_root / "schemas" / "begrip.schema.json").unlink()
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 1


def test_build_begrip_index_md_parse_fout_overgeslagen(tmp_path):
    from validate_note import build_begrip_index
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "begrippen" / "kapot.md").write_bytes(b"\xc3\x28 ongeldig utf-8 bytes \xc3\x28")
    idx = build_begrip_index(tmp_path)
    assert "kapot" not in idx
