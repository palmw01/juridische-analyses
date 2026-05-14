"""Tests voor helper-functies, detect_schema, format/collect-functies en validate_file-paden."""
import json
from pathlib import Path

import pytest
import yaml

from validate_note import (
    load_json_schema,
    load_md_frontmatter,
    load_json,
    load_file,
    build_begrip_index,
    begrip_id_to_slug,
    detect_schema,
    build_annotatie_index,
    validate_integrity_annotatie_lid,
    validate_quality_annotatie_lid,
    validate_quality_annotatie_index,
    validate_file,
    format_rapport_text,
    format_rapport_json,
    schrijf_md_rapport,
    collect_files_for_schema,
    collect_all_files,
    ValidationResult,
)
from tests.fixtures.annotaties import maak_annotatie
from tests.fixtures.begrippen import maak_begrip
from tests.fixtures.regels import maak_regel

SCHEMAS_DIR = Path(__file__).resolve().parent.parent.parent / "schemas"


# ===== load_json_schema =====

def test_load_json_schema_niet_gevonden_gooit_fout():
    with pytest.raises(FileNotFoundError):
        load_json_schema(Path("/tmp"), "schema-bestaat-niet-xyz")


def test_load_json_schema_laadt_begrip_schema():
    schema = load_json_schema(SCHEMAS_DIR, "begrip")
    assert isinstance(schema, dict)
    assert "properties" in schema


# ===== load_md_frontmatter =====

def test_load_md_frontmatter_laadt_yaml_header(tmp_path):
    md = tmp_path / "test.md"
    md.write_text("---\nbegrip-id: test/id\nbegripsnaam: testbegrip\n---\nInhoud hier.")
    data = load_md_frontmatter(md)
    assert data["begrip-id"] == "test/id"
    assert data["begripsnaam"] == "testbegrip"


# ===== load_json =====

def test_load_json_laadt_valide_json(tmp_path):
    f = tmp_path / "test.json"
    f.write_text('{"sleutel": "waarde", "getal": 42}')
    data = load_json(f)
    assert data["sleutel"] == "waarde"
    assert data["getal"] == 42


# ===== load_file =====

def test_load_file_md_extensie(tmp_path):
    f = tmp_path / "test.md"
    f.write_text("---\nbegrip-id: x\n---\n")
    data = load_file(f)
    assert "begrip-id" in data


def test_load_file_json_extensie(tmp_path):
    f = tmp_path / "test.json"
    f.write_text('{"a": 1}')
    data = load_file(f)
    assert data["a"] == 1


def test_load_file_onbekende_extensie_gooit_fout(tmp_path):
    f = tmp_path / "test.xml"
    f.write_text("<root/>")
    with pytest.raises(ValueError, match="Onbekende extensie"):
        load_file(f)


# ===== build_begrip_index =====

def test_build_begrip_index_md_bestanden_opgenomen(tmp_path):
    (tmp_path / "begrippen").mkdir()
    md = tmp_path / "begrippen" / "mijn-begrip.md"
    md.write_text("---\nbegrip-id: BWBR0004770/art9/lid1/mijn-begrip\nbegripsnaam: mijn-begrip\n---\n")
    idx = build_begrip_index(tmp_path)
    assert "mijn-begrip" in idx


def test_build_begrip_index_index_md_wordt_overgeslagen(tmp_path):
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "begrippen" / "index.md").write_text("---\nbegrip-id: skip/this\n---\n")
    idx = build_begrip_index(tmp_path)
    assert "index" not in idx


def test_build_begrip_index_yaml_parse_fout_overgeslagen(tmp_path):
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "begrippen" / "kapot.yaml").write_text("begrip-id: {{{ongeldige yaml")
    idx = build_begrip_index(tmp_path)
    assert "kapot" not in idx


def test_build_begrip_index_geen_begrippen_dir_geeft_leeg(tmp_path):
    idx = build_begrip_index(tmp_path)
    assert idx == {}


def test_build_begrip_index_yaml_bevat_begrip_id_en_slug(tmp_path):
    (tmp_path / "begrippen").mkdir()
    data = maak_begrip()
    (tmp_path / "begrippen" / "belastingschuldige.yaml").write_text(yaml.dump(data))
    idx = build_begrip_index(tmp_path)
    assert "belastingschuldige" in idx
    assert "BWBR0004770/art9/lid1/belastingschuldige" in idx


# ===== begrip_id_to_slug =====

def test_begrip_id_to_slug_wikilink_geeft_leeg():
    assert begrip_id_to_slug("[[annotaties/art9]]") == ""


def test_begrip_id_to_slug_zonder_slash_geeft_heel_id():
    assert begrip_id_to_slug("belastingschuldige") == "belastingschuldige"


def test_begrip_id_to_slug_met_slash_geeft_laatste_segment():
    assert begrip_id_to_slug("BWBR0004770/art9/lid1/belastingschuldige") == "belastingschuldige"


def test_begrip_id_to_slug_trailing_slash_genegeerd():
    assert begrip_id_to_slug("BWBR0004770/art9/lid1/test/") == "test"


# ===== detect_schema =====

def test_detect_schema_begrip(tmp_path):
    (tmp_path / "begrippen").mkdir()
    f = tmp_path / "begrippen" / "test.yaml"
    f.touch()
    assert detect_schema(f, tmp_path) == "begrip"


def test_detect_schema_regel(tmp_path):
    (tmp_path / "regels").mkdir()
    f = tmp_path / "regels" / "test.yaml"
    f.touch()
    assert detect_schema(f, tmp_path) == "regel"


def test_detect_schema_annotatie_lid_md_via_art_streepje_cijfer(tmp_path):
    (tmp_path / "annotaties").mkdir()
    f = tmp_path / "annotaties" / "art9-1.md"
    f.touch()
    assert detect_schema(f, tmp_path) == "annotatie-lid"


def test_detect_schema_annotatie_index_md_via_art_cijfer(tmp_path):
    (tmp_path / "annotaties").mkdir()
    f = tmp_path / "annotaties" / "art9.md"
    f.touch()
    assert detect_schema(f, tmp_path) == "annotatie-index"


def test_detect_schema_annotatie_lid_json_lid_patroon(tmp_path):
    (tmp_path / "annotaties").mkdir()
    f = tmp_path / "annotaties" / "art9-lid1.json"
    f.touch()
    assert detect_schema(f, tmp_path) == "annotatie-lid"


def test_detect_schema_annotatie_index_json_art_patroon(tmp_path):
    (tmp_path / "annotaties").mkdir()
    f = tmp_path / "annotaties" / "art9.json"
    f.touch()
    assert detect_schema(f, tmp_path) == "annotatie-index"


def test_detect_schema_annotatie_lid_json_par_patroon(tmp_path):
    (tmp_path / "annotaties").mkdir()
    f = tmp_path / "annotaties" / "par1-1.json"
    f.touch()
    assert detect_schema(f, tmp_path) == "annotatie-lid"


def test_detect_schema_onbekende_map_geeft_none(tmp_path):
    (tmp_path / "overig").mkdir()
    f = tmp_path / "overig" / "test.yaml"
    f.touch()
    assert detect_schema(f, tmp_path) is None


def test_detect_schema_annotatie_md_geen_match_geeft_none(tmp_path):
    (tmp_path / "annotaties").mkdir()
    f = tmp_path / "annotaties" / "index.md"
    f.touch()
    assert detect_schema(f, tmp_path) is None


# ===== build_annotatie_index =====

def test_build_annotatie_index_leeg_als_dir_niet_bestaat(tmp_path):
    idx = build_annotatie_index(tmp_path)
    assert idx == set()


def test_build_annotatie_index_voegt_annotatie_id_toe(tmp_path):
    (tmp_path / "annotaties").mkdir()
    ann = maak_annotatie()
    (tmp_path / "annotaties" / "art9-1.json").write_text(json.dumps(ann))
    idx = build_annotatie_index(tmp_path)
    assert "BWBR0004770/art9/lid1" in idx


def test_build_annotatie_index_sla_parse_fout_over(tmp_path):
    (tmp_path / "annotaties").mkdir()
    (tmp_path / "annotaties" / "kapot.json").write_text("{{geen json")
    idx = build_annotatie_index(tmp_path)
    assert len(idx) == 0


def test_build_annotatie_index_zonder_annotatie_id_niet_toegevoegd(tmp_path):
    (tmp_path / "annotaties").mkdir()
    (tmp_path / "annotaties" / "art9.json").write_text('{"bwb-id": "BWBR0004770"}')
    idx = build_annotatie_index(tmp_path)
    assert len(idx) == 0


# ===== validate_integrity_annotatie_lid =====

def test_integrity_annotatie_lid_begrip_ontbreekt_geeft_fout(tmp_path):
    (tmp_path / "begrippen").mkdir()
    idx = build_begrip_index(tmp_path)
    data = maak_annotatie()
    errors = validate_integrity_annotatie_lid(data, Path("/tmp/test.json"), idx)
    assert any("annotatierijen" in e for e in errors)


def test_integrity_annotatie_lid_begrip_gevonden_geen_fout(tmp_path):
    (tmp_path / "begrippen").mkdir()
    begrip = maak_begrip()
    (tmp_path / "begrippen" / "belastingschuldige.yaml").write_text(yaml.dump(begrip))
    idx = build_begrip_index(tmp_path)
    data = maak_annotatie()
    errors = validate_integrity_annotatie_lid(data, Path("/tmp/test.json"), idx)
    assert not any("annotatierijen" in e for e in errors)


def test_integrity_annotatie_lid_kant_onbestaande_knoop_geeft_fout():
    data = {
        "annotatierijen": [],
        "diagram": {
            "knopen": [{"id": "k1"}],
            "kanten": [{"van": "k1", "naar": "k-ontbreekt"}],
        },
    }
    errors = validate_integrity_annotatie_lid(data, Path("/tmp/test.json"), {})
    assert any("k-ontbreekt" in e for e in errors)


def test_integrity_annotatie_lid_geldige_kant_geen_fout():
    data = {
        "annotatierijen": [],
        "diagram": {
            "knopen": [{"id": "k1"}, {"id": "k2"}],
            "kanten": [{"van": "k1", "naar": "k2"}],
        },
    }
    errors = validate_integrity_annotatie_lid(data, Path("/tmp/test.json"), {})
    assert errors == []


def test_integrity_annotatie_lid_lege_annotatierijen_geen_fout():
    data = {"annotatierijen": [], "diagram": {"knopen": [], "kanten": []}}
    errors = validate_integrity_annotatie_lid(data, Path("/tmp/test.json"), {})
    assert errors == []


# ===== validate_quality_annotatie_lid =====

def test_quality_annotatie_lid_leeg_geeft_twee_warnings():
    data = {"annotatierijen": [], "diagram": {"knopen": [], "kanten": []}}
    warnings = validate_quality_annotatie_lid(data, Path("/tmp/test.json"))
    assert any("annotatierijen leeg" in w for w in warnings)
    assert any("diagram" in w for w in warnings)


def test_quality_annotatie_lid_knopen_zonder_kanten_geeft_warning():
    data = {
        "annotatierijen": [{"rij-id": "r1"}],
        "diagram": {"knopen": [{"id": "k1"}], "kanten": []},
    }
    warnings = validate_quality_annotatie_lid(data, Path("/tmp/test.json"))
    assert any("kanten" in w for w in warnings)


def test_quality_annotatie_lid_volledig_geen_struct_warnings():
    data = {
        "annotatierijen": [{"rij-id": "r1"}],
        "diagram": {
            "knopen": [{"id": "k1"}, {"id": "k2"}],
            "kanten": [{"van": "k1", "naar": "k2"}],
        },
    }
    warnings = validate_quality_annotatie_lid(data, Path("/tmp/test.json"))
    assert not any("annotatierijen leeg" in w for w in warnings)
    assert not any("knopen maar geen kanten" in w for w in warnings)


# ===== validate_quality_annotatie_index =====

def test_quality_annotatie_index_lege_leden_geeft_warning():
    data = {"leden-annotaties": []}
    warnings = validate_quality_annotatie_index(data, Path("/tmp/test.json"))
    assert any("leden-annotaties leeg" in w for w in warnings)


def test_quality_annotatie_index_gevuld_geen_warning():
    data = {"leden-annotaties": ["BWBR0004770/art9/lid1"]}
    warnings = validate_quality_annotatie_index(data, Path("/tmp/test.json"))
    assert warnings == []


# ===== validate_file — foutpaden =====

def test_validate_file_laad_fout_geeft_l0_fout(tmp_path):
    schema = load_json_schema(SCHEMAS_DIR, "begrip")
    f = tmp_path / "kapot.onbekend"
    f.write_text("inhoud")
    result = validate_file(f, "begrip", schema, {}, tmp_path)
    assert any("[L0]" in e for e in result.errors)


def test_validate_file_leeg_yaml_geeft_l0_fout(tmp_path):
    schema = load_json_schema(SCHEMAS_DIR, "begrip")
    f = tmp_path / "leeg.yaml"
    f.write_text("")
    result = validate_file(f, "begrip", schema, {}, tmp_path)
    assert any("[L0]" in e for e in result.errors)


def test_validate_file_annotatie_lid_quality_check_draait(project_root):
    schema = load_json_schema(SCHEMAS_DIR, "annotatie-lid")
    ann = maak_annotatie(annotatierijen=[], diagram={"knopen": [], "kanten": []})
    f = project_root / "annotaties" / "art9-1.json"
    f.write_text(json.dumps(ann, ensure_ascii=False))
    result = validate_file(f, "annotatie-lid", schema, {}, project_root, check_integrity=True)
    assert any("annotatierijen leeg" in w for w in result.warnings)


def test_validate_file_annotatie_index_quality_check_draait(project_root):
    schema = load_json_schema(SCHEMAS_DIR, "annotatie-index")
    data = {"artikel-id": "BWBR0004770/art9", "leden-annotaties": []}
    f = project_root / "annotaties" / "art9.json"
    f.write_text(json.dumps(data, ensure_ascii=False))
    result = validate_file(f, "annotatie-index", schema, {}, project_root)
    assert any("leden-annotaties leeg" in w for w in result.warnings)


# ===== collect_files_for_schema =====

def test_collect_begrip_vindt_yaml_bestanden(project_root):
    (project_root / "begrippen" / "test.yaml").write_text(yaml.dump(maak_begrip()))
    files = collect_files_for_schema(project_root, "begrip")
    assert any(f.name == "test.yaml" for f in files)


def test_collect_begrip_slaat_index_md_over(project_root):
    (project_root / "begrippen" / "index.md").write_text("---\n---\n")
    files = collect_files_for_schema(project_root, "begrip")
    assert not any(f.name == "index.md" for f in files)


def test_collect_regel_vindt_yaml_bestanden(project_root):
    (project_root / "regels" / "r.yaml").write_text(yaml.dump(maak_regel()))
    files = collect_files_for_schema(project_root, "regel")
    assert any(f.name == "r.yaml" for f in files)


def test_collect_annotatie_lid_vindt_json(project_root):
    ann = maak_annotatie()
    (project_root / "annotaties" / "art9-1.json").write_text(json.dumps(ann))
    files = collect_files_for_schema(project_root, "annotatie-lid")
    assert any("art9-1" in f.name for f in files)


def test_collect_annotatie_index_vindt_json(project_root):
    (project_root / "annotaties" / "art9.json").write_text(json.dumps({"artikel-id": "art9"}))
    files = collect_files_for_schema(project_root, "annotatie-index")
    assert any("art9" in f.name for f in files)


# ===== collect_all_files =====

def test_collect_all_files_bevat_begrip_en_regel(project_root):
    (project_root / "begrippen" / "b.yaml").write_text(yaml.dump(maak_begrip()))
    (project_root / "regels" / "r.yaml").write_text(yaml.dump(maak_regel()))
    files = collect_all_files(project_root)
    schemas = [s for _, s in files]
    assert "begrip" in schemas
    assert "regel" in schemas


def test_collect_all_files_bevat_annotaties(project_root):
    ann = maak_annotatie()
    (project_root / "annotaties" / "art9-1.json").write_text(json.dumps(ann))
    files = collect_all_files(project_root)
    schemas = [s for _, s in files]
    assert "annotatie-lid" in schemas


def test_collect_all_files_leeg_project_geeft_lege_lijst(project_root):
    files = collect_all_files(project_root)
    assert files == []


# ===== format_rapport_text =====

def test_format_rapport_text_zonder_fouten_bevat_geen_blokkeer():
    r = ValidationResult(Path("/tmp/test.yaml"))
    r.warnings.append("[L3] test waarschuwing")
    tekst = format_rapport_text([r], Path("/tmp"), "2024-01-01")
    assert "BLOKKEERFOUTEN" in tekst
    assert "(geen)" in tekst
    assert "test waarschuwing" in tekst


def test_format_rapport_text_met_fouten():
    r = ValidationResult(Path("/tmp/test.yaml"))
    r.errors.append("[L1] schema fout")
    tekst = format_rapport_text([r], Path("/tmp"), "2024-01-01")
    assert "schema fout" in tekst
    assert "BLOKKEERFOUTEN (moeten 0 zijn" in tekst


def test_format_rapport_text_bevat_datum():
    r = ValidationResult(Path("/tmp/test.yaml"))
    tekst = format_rapport_text([r], Path("/tmp"), "2026-05-14")
    assert "2026-05-14" in tekst


def test_format_rapport_text_geen_warnings_bevat_geen():
    r = ValidationResult(Path("/tmp/test.yaml"))
    tekst = format_rapport_text([r], Path("/tmp"), "2024-01-01")
    assert "WAARSCHUWINGEN" in tekst


def test_format_rapport_text_bestand_buiten_project_root():
    r = ValidationResult(Path("/helemaal/anders/test.yaml"))
    tekst = format_rapport_text([r], Path("/tmp"), "2024-01-01")
    assert tekst  # geen crash bij filepath buiten project_root


# ===== format_rapport_json =====

def test_format_rapport_json_leeg_geen_fouten():
    r = ValidationResult(Path("/tmp/test.yaml"))
    result = format_rapport_json([r], Path("/tmp"))
    assert result["fouten"] == []
    assert result["waarschuwingen"] == []
    assert result["geslaagd"] == 1


def test_format_rapport_json_met_fouten():
    r = ValidationResult(Path("/tmp/test.yaml"))
    r.errors.append("[L1] fout")
    result = format_rapport_json([r], Path("/tmp"))
    assert len(result["fouten"]) == 1
    assert result["geslaagd"] == 0


def test_format_rapport_json_met_waarschuwing():
    r = ValidationResult(Path("/tmp/test.yaml"))
    r.warnings.append("[L3] waarschuwing")
    result = format_rapport_json([r], Path("/tmp"))
    assert len(result["waarschuwingen"]) == 1
    assert result["geslaagd"] == 1


# ===== schrijf_md_rapport =====

def test_schrijf_md_rapport_maakt_bestand_aan(tmp_path):
    schrijf_md_rapport("Testrapport inhoud hier", tmp_path)
    rapport = tmp_path / "rapporten" / "validatie-rapport.md"
    assert rapport.exists()
    assert "Testrapport inhoud hier" in rapport.read_text()


def test_schrijf_md_rapport_maakt_dir_aan_als_niet_bestaat(tmp_path):
    schrijf_md_rapport("inhoud", tmp_path)
    assert (tmp_path / "rapporten").is_dir()
