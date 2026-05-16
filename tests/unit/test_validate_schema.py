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


# ---------- Bron schema ----------

def maak_bron(**overrides):
    base = {
        "bwb-id": "BWBR0004770",
        "artikel": "9",
        "opgehaald-op": "2026-05-16",
        "versiedatum": "2026-01-01",
        "citeertitel": "Invorderingswet 1990",
        "bronreferentie": "jci1.3:c:BWBR0004770&artikel=9",
        "pad": "Hoofdstuk II > Artikel 9",
        "leden": [{"lid": "1", "tekst": "De belastingaanslag..."}],
    }
    for k, v in overrides.items():
        if v is None:
            base.pop(k, None)
        else:
            base[k] = v
    return base


@pytest.fixture(scope="module")
def bron_schema():
    return load_json_schema(SCHEMAS_DIR, "bron")


def test_bron_schema_geldig(bron_schema, tmp_path):
    errors = validate_schema(maak_bron(), bron_schema, tmp_path / "art9.json")
    assert errors == []


def test_bron_schema_met_optionele_velden(bron_schema, tmp_path):
    data = maak_bron(sectie="Artikel 9", formaat="markdown")
    errors = validate_schema(data, bron_schema, tmp_path / "art9.json")
    assert errors == []


def test_bron_schema_verbiedt_bwbid_camelcase(bron_schema, tmp_path):
    data = maak_bron()
    data["bwbId"] = data["bwb-id"]
    errors = validate_schema(data, bron_schema, tmp_path / "art9.json")
    assert errors, "Verwacht L1-fout voor extra veld bwbId"


def test_bron_schema_verbiedt_wet_veld(bron_schema, tmp_path):
    data = maak_bron(wet="Invorderingswet 1990")
    errors = validate_schema(data, bron_schema, tmp_path / "art9.json")
    assert errors, "Verwacht L1-fout voor extra veld wet"


def test_bron_schema_verbiedt_structuurpositie(bron_schema, tmp_path):
    data = maak_bron(structuurpositie="Hoofdstuk II > Artikel 9")
    errors = validate_schema(data, bron_schema, tmp_path / "art9.json")
    assert errors, "Verwacht L1-fout voor extra veld structuurpositie"


@pytest.mark.parametrize("veld,verwacht_fragment", [
    ("bwb-id", "bwb-id"),
    ("artikel", "artikel"),
    ("opgehaald-op", "opgehaald-op"),
    ("versiedatum", "versiedatum"),
    ("citeertitel", "citeertitel"),
    ("bronreferentie", "bronreferentie"),
    ("pad", "pad"),
    ("leden", "leden"),
])
def test_bron_schema_ontbrekend_verplicht_veld(bron_schema, tmp_path, veld, verwacht_fragment):
    data = maak_bron(**{veld: None})
    errors = validate_schema(data, bron_schema, tmp_path / "art9.json")
    assert errors, f"Verwacht L1-fout voor ontbrekend veld {veld}"
    assert any(verwacht_fragment in e for e in errors)
