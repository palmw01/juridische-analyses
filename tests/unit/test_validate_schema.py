"""L1 schema-validatietests — happy path + failure per gevalideerd veld."""
from pathlib import Path

import pytest

from validate_note import load_json_schema, validate_schema
from tests.fixtures.begrippen import maak_begrip
from tests.fixtures.regels import maak_regel

SCHEMAS_DIR = Path(__file__).resolve().parent.parent.parent / "schemas"


@pytest.fixture(scope="module")
def begrip_schema():
    return load_json_schema(SCHEMAS_DIR, "begrip")


@pytest.fixture(scope="module")
def regel_schema():
    return load_json_schema(SCHEMAS_DIR, "regel")


# ---------- Begrip L1 happy path ----------

def test_begrip_schema_geldig(begrip_schema, tmp_path):
    errors = validate_schema(maak_begrip(), begrip_schema, tmp_path / "test.yaml")
    assert errors == []


# ---------- Begrip L1 failure paths ----------

@pytest.mark.parametrize("veld,waarde,verwacht_fragment", [
    ("begrip-id", None, "begrip-id"),
    ("begripsnaam", None, "begripsnaam"),
    ("soort", "onbekend-type-xyz", "soort"),
    ("status", "onbekende-status", "status"),
    ("herkomst", "onbekende-herkomst", "herkomst"),
])
def test_begrip_schema_ongeldig_veld(begrip_schema, tmp_path, veld, waarde, verwacht_fragment):
    data = maak_begrip(**{veld: waarde})
    errors = validate_schema(data, begrip_schema, tmp_path / "test.yaml")
    assert errors, f"Verwacht L1-fout voor {veld}={waarde!r}"
    assert any(verwacht_fragment in e for e in errors)


# ---------- Regel L1 happy path ----------

def test_regel_schema_geldig(regel_schema, tmp_path):
    errors = validate_schema(maak_regel(), regel_schema, tmp_path / "test.yaml")
    assert errors == []


# ---------- Regel L1 failure paths ----------

@pytest.mark.parametrize("veld,waarde,verwacht_fragment", [
    ("regel-id", None, "regel-id"),
    ("naam", None, "naam"),
    ("soort", "OnbekendType", "soort"),
    ("tussenresultaat", "ja", "tussenresultaat"),
    ("annotatie-id",    None, "annotatie-id"),
    ("toelichting",     None, "toelichting"),
])
def test_regel_schema_ongeldig_veld(regel_schema, tmp_path, veld, waarde, verwacht_fragment):
    data = maak_regel(**{veld: waarde})
    errors = validate_schema(data, regel_schema, tmp_path / "test.yaml")
    assert errors, f"Verwacht L1-fout voor {veld}={waarde!r}"
    assert any(verwacht_fragment in e for e in errors)
