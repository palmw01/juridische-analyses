import shutil
import sys
from pathlib import Path

import pytest
import yaml

# Projectroot = twee niveaus boven tests/conftest.py
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))   # validate_note, jas_index_lib, etc.
sys.path.insert(0, str(ROOT))             # sitegen.*

from tests.fixtures.begrippen import maak_begrip
from tests.fixtures.regels import maak_regel


@pytest.fixture
def project_root(tmp_path):
    """Minimaal geldig project-skelet in tmp_path voor integratie-tests."""
    for d in ("begrippen", "regels", "annotaties", "schemas"):
        (tmp_path / d).mkdir()
    schemas_src = ROOT / "schemas"
    for s in schemas_src.glob("*.schema.json"):
        shutil.copy(s, tmp_path / "schemas" / s.name)
    return tmp_path


@pytest.fixture
def begrip_yaml(project_root):
    """Valide begrip-YAML in project_root/begrippen/; geeft pad terug."""
    pad = project_root / "begrippen" / "test-begrip.yaml"
    pad.write_text(yaml.dump(maak_begrip(), allow_unicode=True))
    return pad


@pytest.fixture
def regel_yaml(project_root):
    """Valide regel-YAML in project_root/regels/; geeft pad terug."""
    pad = project_root / "regels" / "test-regel.yaml"
    pad.write_text(yaml.dump(maak_regel(), allow_unicode=True))
    return pad
