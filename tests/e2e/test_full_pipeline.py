"""E2E-tests: volledige validator-pijplijn via subprocess."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent.parent

from tests.fixtures.begrippen import maak_begrip
from tests.fixtures.regels import maak_regel

pytestmark = pytest.mark.e2e

VALIDATE_CMD = [sys.executable, str(ROOT / "tools" / "validate_note.py"), "--full"]


def schrijf_valide_project(basis: Path):
    for d in ("begrippen", "regels", "annotaties", "schemas"):
        (basis / d).mkdir(exist_ok=True)
    for s in (ROOT / "schemas").glob("*.schema.json"):
        shutil.copy(s, basis / "schemas" / s.name)
    # Begrip voor het invoer-begrip van de annotatie
    (basis / "begrippen" / "test.yaml").write_text(
        yaml.dump(maak_begrip(), allow_unicode=True)
    )
    # Uitvoer-begrip dat de regel aanwijst
    uitvoer_begrip = maak_begrip(**{
        "begrip-id": "BWBR0004770/art9/lid1/betalingstermijn",
        "begripsnaam": "betalingstermijn",
    })
    (basis / "begrippen" / "betalingstermijn.yaml").write_text(
        yaml.dump(uitvoer_begrip, allow_unicode=True)
    )
    (basis / "regels" / "test.yaml").write_text(
        yaml.dump(maak_regel(), allow_unicode=True)
    )


def test_validate_slaagt_op_valide_project(tmp_path):
    schrijf_valide_project(tmp_path)
    result = subprocess.run(VALIDATE_CMD, capture_output=True, text=True, cwd=str(tmp_path))
    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"


def test_validate_detecteert_l1_schema_fout(tmp_path):
    schrijf_valide_project(tmp_path)
    kapot = {"begrip-id": None, "begripsnaam": "test", "soort": "entiteit",
             "herkomst": "direct", "status": "concept"}
    (tmp_path / "begrippen" / "kapot.yaml").write_text(yaml.dump(kapot))
    result = subprocess.run(VALIDATE_CMD, capture_output=True, text=True, cwd=str(tmp_path))
    assert result.returncode != 0
    assert "[L1]" in result.stdout


def test_validate_detecteert_l2_integriteits_fout(tmp_path):
    schrijf_valide_project(tmp_path)
    data = maak_begrip(**{"definitie-gebaseerd-op": ["m-bestaat-nooit"]})
    (tmp_path / "begrippen" / "fout.yaml").write_text(yaml.dump(data, allow_unicode=True))
    result = subprocess.run(VALIDATE_CMD, capture_output=True, text=True, cwd=str(tmp_path))
    assert result.returncode != 0
    assert "definitie-gebaseerd-op" in result.stdout
