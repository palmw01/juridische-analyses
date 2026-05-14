"""Integratie: volledige validate_file pipeline per schema-type."""
import json
from pathlib import Path

import yaml

from validate_note import validate_file, load_json_schema, build_begrip_index
from tests.fixtures.begrippen import maak_begrip
from tests.fixtures.regels import maak_regel

SCHEMAS_DIR = Path(__file__).resolve().parent.parent.parent / "schemas"


def schrijf_en_valideer(project_root, relatief_pad, data, schema_name, check_integrity=False):
    pad = project_root / relatief_pad
    pad.parent.mkdir(parents=True, exist_ok=True)
    if pad.suffix == ".json":
        pad.write_text(json.dumps(data, ensure_ascii=False))
    else:
        pad.write_text(yaml.dump(data, allow_unicode=True))
    schema = load_json_schema(SCHEMAS_DIR, schema_name)
    idx = build_begrip_index(project_root)
    return validate_file(pad, schema_name, schema, idx, project_root, check_integrity)


# ---------- Begrip ----------

def test_pipeline_geldig_begrip_geen_fouten(project_root):
    result = schrijf_en_valideer(
        project_root, "begrippen/test.yaml", maak_begrip(), "begrip", check_integrity=True
    )
    assert result.errors == []


def test_pipeline_begrip_schema_fout_geeft_l1_error(project_root):
    data = maak_begrip(**{"begrip-id": None})
    result = schrijf_en_valideer(project_root, "begrippen/test.yaml", data, "begrip")
    assert any("[L1]" in e for e in result.errors)


def test_pipeline_begrip_l3_onbevestigd_altijd_aanwezig(project_root):
    result = schrijf_en_valideer(
        project_root, "begrippen/test.yaml", maak_begrip(), "begrip"
    )
    assert any("onbevestigd" in w for w in result.warnings)


def test_pipeline_begrip_integrity_ontbrekende_markering_geeft_l2(project_root):
    data = maak_begrip(**{"definitie-gebaseerd-op": ["m-bestaat-niet"]})
    result = schrijf_en_valideer(
        project_root, "begrippen/test.yaml", data, "begrip", check_integrity=True
    )
    assert any("definitie-gebaseerd-op" in e for e in result.errors)


def test_pipeline_begrip_integrity_niet_primair_bijdrage_geeft_l2(project_root):
    data = maak_begrip(
        markeringen=[{
            "markering-id": "m-001", "bijdrage": "verfijning",
            "bron-annotatie-id": "BWBR0004770/art9/lid1",
            "tekst": "test", "interpretatiemethode": "grammaticaal", "bevestigd": False,
        }],
        **{"definitie-gebaseerd-op": ["m-001"]},
    )
    result = schrijf_en_valideer(
        project_root, "begrippen/test.yaml", data, "begrip", check_integrity=True
    )
    assert any("definitie-gebaseerd-op" in e and "verfijning" in e for e in result.errors)


# ---------- Regel ----------

def test_pipeline_geldig_regel_geen_fouten(project_root):
    # Schrijf het uitvoer-begrip zodat de integriteitscheck niet faalt
    import yaml as _yaml
    from tests.fixtures.begrippen import maak_begrip as _mb
    doel = _mb(**{
        "begrip-id": "BWBR0004770/art9/lid1/betalingstermijn",
        "begripsnaam": "betalingstermijn",
    })
    (project_root / "begrippen" / "betalingstermijn.yaml").write_text(
        _yaml.dump(doel, allow_unicode=True)
    )
    result = schrijf_en_valideer(
        project_root, "regels/test.yaml", maak_regel(), "regel", check_integrity=True
    )
    assert result.errors == []


def test_pipeline_regel_schema_fout_geeft_l1_error(project_root):
    data = maak_regel(**{"regel-id": None})
    result = schrijf_en_valideer(project_root, "regels/test.yaml", data, "regel")
    assert any("[L1]" in e for e in result.errors)


def test_pipeline_regel_vervangt_ontbreekt_geeft_l2(project_root):
    data = maak_regel(**{"vervangt-regel-id": "AR-ontbreekt"})
    result = schrijf_en_valideer(
        project_root, "regels/test.yaml", data, "regel", check_integrity=True
    )
    assert any("vervangt-regel-id" in e for e in result.errors)


def test_pipeline_regel_l3_grensgeval_warning(project_root):
    data = maak_regel(voorbeeldreeksen=[
        {"invoerwaarden": "x=1", "verwachte-uitkomst": "y=1", "juridisch-juist": True},
        {"invoerwaarden": "x=2", "verwachte-uitkomst": "y=2", "juridisch-juist": True},
    ])
    result = schrijf_en_valideer(project_root, "regels/test.yaml", data, "regel")
    assert any("grensgeval" in w for w in result.warnings)
