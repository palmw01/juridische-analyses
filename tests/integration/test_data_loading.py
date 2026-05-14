"""Integratie: sitegen/data.py laad-functies met tmp_path-isolatie."""
import yaml

from sitegen.data import laad_begrippen, laad_regels
from tests.fixtures.begrippen import maak_begrip
from tests.fixtures.regels import maak_regel


def test_laad_begrippen_leeg(project_root):
    assert laad_begrippen(project_root) == []


def test_laad_regels_leeg(project_root):
    assert laad_regels(project_root) == []


def test_laad_begrippen_een_bestand(project_root):
    data = maak_begrip()
    (project_root / "begrippen" / "test.yaml").write_text(
        yaml.dump(data, allow_unicode=True)
    )
    result = laad_begrippen(project_root)
    assert len(result) == 1
    b = result[0]
    assert b["id"] == "BWBR0004770/art9/lid1/belastingschuldige"
    assert b["naam"] == "belastingschuldige"
    assert b["slug"]
    assert b["soort"] == "entiteit"
    assert b["herkomst"] == "direct"


def test_laad_begrippen_gesorteerd(project_root):
    for naam in ("zzz.yaml", "aaa.yaml", "mmm.yaml"):
        d = maak_begrip(**{"begrip-id": f"test/{naam}", "begripsnaam": naam})
        (project_root / "begrippen" / naam).write_text(yaml.dump(d, allow_unicode=True))
    result = laad_begrippen(project_root)
    ids = [b["id"] for b in result]
    assert ids == sorted(ids)


def test_laad_begrippen_optioneel_veld_ontbreekt(project_root):
    """Ontbrekende optionele velden geven geen KeyError — default naar lege lijst/string."""
    data = {
        "begrip-id": "test/mini",
        "begripsnaam": "mini",
        "soort": "entiteit",
        "herkomst": "direct",
        "status": "concept",
        "definitie": {"kern": "test", "contexten": []},
        "definitie-versie": 1,
        "definitie-gebaseerd-op": [],
        "markeringen": [],
        "identificatiebegrip": False,
        "geldigheid-van": "2024-01-01",
        "relaties": {},
    }
    (project_root / "begrippen" / "mini.yaml").write_text(yaml.dump(data))
    result = laad_begrippen(project_root)
    assert len(result) == 1
    assert result[0]["voorbeelden"] == []
    assert result[0]["kenmerken"] == []
    assert result[0]["geldigheid_van"] == "2024-01-01"
    assert result[0]["geldigheid_tot"] == ""


def test_laad_regels_een_bestand(project_root):
    data = maak_regel()
    (project_root / "regels" / "test.yaml").write_text(
        yaml.dump(data, allow_unicode=True)
    )
    result = laad_regels(project_root)
    assert len(result) == 1
    r = result[0]
    assert r["id"] == "AR-0001"
    assert r["soort"] == "Rekenregel"
    assert r["tussenresultaat"] is False


def test_laad_regels_prioriteit_null_by_default(project_root):
    (project_root / "regels" / "test.yaml").write_text(
        yaml.dump(maak_regel(), allow_unicode=True)
    )
    result = laad_regels(project_root)
    assert result[0]["prioriteit"] is None


def test_laad_regels_prioriteit_ingevuld(project_root):
    (project_root / "regels" / "test.yaml").write_text(
        yaml.dump(maak_regel(prioriteit=2), allow_unicode=True)
    )
    result = laad_regels(project_root)
    assert result[0]["prioriteit"] == 2


def test_laad_regels_geldigheid_van_string(project_root):
    data = maak_regel(**{"geldigheid-van": "2024-01-01"})
    (project_root / "regels" / "test.yaml").write_text(yaml.dump(data, allow_unicode=True))
    result = laad_regels(project_root)
    assert result[0]["geldigheid_van"] == "2024-01-01"


def test_laad_regels_vervangt_regel_id(project_root):
    data = maak_regel(**{"vervangt-regel-id": "AR-0000"})
    (project_root / "regels" / "test.yaml").write_text(yaml.dump(data, allow_unicode=True))
    result = laad_regels(project_root)
    assert result[0]["vervangt_regel_id"] == "AR-0000"
