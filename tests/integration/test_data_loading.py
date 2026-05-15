"""Integratie: sitegen/data.py laad-functies met tmp_path-isolatie."""
import json
import yaml

from sitegen.data import laad_begrippen, laad_regels, laad_annotaties, laad_artikel_indices, laad_waarschuwingen, waarschuwingen_voor, _bouw_annotatie_jas_index, _verrijk_markeringen
from tests.fixtures.annotaties import maak_annotatie
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


def test_bouw_annotatie_jas_index_geen_annotaties_map(tmp_path):
    """Geen annotaties/-map → lege index, geen fout."""
    (tmp_path / "begrippen").mkdir()
    index = _bouw_annotatie_jas_index(tmp_path)
    assert index == {}


def test_bouw_annotatie_jas_index_vult_index(project_root):
    """JSON-bestand in annotaties/ wordt correct geïndexeerd."""
    ann = {
        "annotatie-id": "BWBR0004770/art2/lid2",
        "annotatierijen": [
            {"rij-id": "r-001", "begrip-id": "BWBR0004770/art9/lid1/belastingaanslag",
             "jas-klasse": "brondefinitie"},
        ],
    }
    (project_root / "annotaties" / "art2-lid2.json").write_text(json.dumps(ann))
    index = _bouw_annotatie_jas_index(project_root)
    assert index["BWBR0004770/art2/lid2"]["BWBR0004770/art9/lid1/belastingaanslag"] == "brondefinitie"


def test_bouw_annotatie_jas_index_json_zonder_annotatie_id_overgeslagen(project_root):
    """JSON zonder annotatie-id-veld wordt stilzwijgend overgeslagen."""
    (project_root / "annotaties" / "geen-id.json").write_text(json.dumps({"annotatierijen": []}))
    index = _bouw_annotatie_jas_index(project_root)
    assert index == {}


def test_bouw_annotatie_jas_index_corrupt_json_overgeslagen(project_root):
    """Corrupt JSON-bestand in annotaties/ levert geen fout — wordt overgeslagen."""
    (project_root / "annotaties" / "corrupt.json").write_text("GEEN GELDIG JSON{{")
    index = _bouw_annotatie_jas_index(project_root)
    assert index == {}


def test_verrijk_markeringen_vult_jas_klasse(project_root):
    """Markering met bekende bron-annotatie-id krijgt jas-klasse uit index."""
    jas_index = {"BWBR0004770/art2/lid2": {"begrip-x": "brondefinitie"}}
    markeringen = [{"markering-id": "m-001", "bron-annotatie-id": "BWBR0004770/art2/lid2",
                    "bijdrage": "primair"}]
    result = _verrijk_markeringen(markeringen, "begrip-x", jas_index)
    assert result[0]["jas-klasse"] == "brondefinitie"


def test_verrijk_markeringen_onbekende_bron_geeft_lege_string(project_root):
    """Markering waarvan bron niet in index staat krijgt lege jas-klasse."""
    markeringen = [{"markering-id": "m-001", "bron-annotatie-id": "BWBR9999/art1/lid1",
                    "bijdrage": "primair"}]
    result = _verrijk_markeringen(markeringen, "begrip-x", {})
    assert result[0]["jas-klasse"] == ""


def test_laad_begrippen_verrijkt_markeringen_met_jas_klasse(project_root):
    """Markeringen in geladen begrip krijgen jas-klasse uit annotatie-index."""
    ann_id = "BWBR0004770/art2/lid2"
    begrip_id = "BWBR0004770/art9/lid1/belastingaanslag"
    ann = {
        "annotatie-id": ann_id,
        "annotatierijen": [
            {"rij-id": "r-001", "begrip-id": begrip_id, "jas-klasse": "brondefinitie"},
        ],
    }
    (project_root / "annotaties" / "art2-lid2.json").write_text(json.dumps(ann))
    begrip = maak_begrip(**{
        "begrip-id": begrip_id,
        "markeringen": [
            {"markering-id": "m-001", "bijdrage": "primair",
             "bron-annotatie-id": ann_id, "bevestigd": False},
        ],
    })
    (project_root / "begrippen" / "test.yaml").write_text(yaml.dump(begrip, allow_unicode=True))
    result = laad_begrippen(project_root)
    assert result[0]["markeringen"][0]["jas-klasse"] == "brondefinitie"


def test_laad_begrippen_twee_markeringen_verschillende_jas_klassen(project_root):
    """Begrip met twee markeringen krijgt per markering de juiste jas-klasse."""
    begrip_id = "BWBR0004770/art9/lid1/belastingaanslag"
    for ann_id, jas in [("BWBR0004770/art9/lid1", "rechtsobject"),
                        ("BWBR0004770/art2/lid2", "brondefinitie")]:
        ann = {"annotatie-id": ann_id,
               "annotatierijen": [{"rij-id": "r-001", "begrip-id": begrip_id, "jas-klasse": jas}]}
        (project_root / "annotaties" / f"{ann_id.replace('/', '_')}.json").write_text(json.dumps(ann))
    begrip = maak_begrip(**{
        "begrip-id": begrip_id,
        "markeringen": [
            {"markering-id": "m-001", "bijdrage": "aanvullend",
             "bron-annotatie-id": "BWBR0004770/art9/lid1", "bevestigd": True},
            {"markering-id": "m-002", "bijdrage": "primair",
             "bron-annotatie-id": "BWBR0004770/art2/lid2", "bevestigd": False},
        ],
    })
    (project_root / "begrippen" / "test.yaml").write_text(yaml.dump(begrip, allow_unicode=True))
    result = laad_begrippen(project_root)
    markeringen = {m["markering-id"]: m["jas-klasse"] for m in result[0]["markeringen"]}
    assert markeringen["m-001"] == "rechtsobject"
    assert markeringen["m-002"] == "brondefinitie"


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
    assert r["annotatie_id"] == "BWBR0004770/art9/lid1"


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


# ===== laad_begrippen — jas-klasse fallback =====

def test_laad_begrippen_klasse_uit_primair_markering(project_root):
    data = maak_begrip()
    del data["jas-klasse"]
    data["markeringen"][0]["jas-klasse"] = "rechtsobject"
    (project_root / "begrippen" / "test.yaml").write_text(yaml.dump(data, allow_unicode=True))
    result = laad_begrippen(project_root)
    assert result[0]["jas_klasse"] == "rechtsobject"


def test_laad_begrippen_klasse_onbekend_via_soort_datum(project_root):
    data = maak_begrip(soort="datum", markeringen=[])
    del data["jas-klasse"]
    (project_root / "begrippen" / "test.yaml").write_text(yaml.dump(data, allow_unicode=True))
    result = laad_begrippen(project_root)
    assert result[0]["jas_klasse"] == "tijdsaanduiding"


def test_laad_begrippen_klasse_onbekend_via_soort_monetair(project_root):
    data = maak_begrip(soort="monetair-bedrag", markeringen=[])
    del data["jas-klasse"]
    (project_root / "begrippen" / "test.yaml").write_text(yaml.dump(data, allow_unicode=True))
    result = laad_begrippen(project_root)
    assert result[0]["jas_klasse"] == "variabele"


def test_laad_begrippen_klasse_onbekend_via_soort_enumeratie(project_root):
    data = maak_begrip(soort="enumeratie", markeringen=[])
    del data["jas-klasse"]
    (project_root / "begrippen" / "test.yaml").write_text(yaml.dump(data, allow_unicode=True))
    result = laad_begrippen(project_root)
    assert result[0]["jas_klasse"] == "rechtsobject"


# ===== laad_annotaties =====

def test_laad_annotaties_leeg(project_root):
    assert laad_annotaties(project_root) == []


def test_laad_annotaties_een_bestand(project_root):
    ann = maak_annotatie()
    (project_root / "annotaties" / "art9-1.json").write_text(
        json.dumps(ann, ensure_ascii=False)
    )
    result = laad_annotaties(project_root)
    assert len(result) == 1
    a = result[0]
    assert a["id"] == "BWBR0004770/art9/lid1"
    assert a["wet"] == "Invorderingswet 1990"
    assert a["artikel"] == "9"
    assert len(a["rijen"]) == 1


def test_laad_annotaties_zonder_wetstekst_overgeslagen(project_root):
    ann = maak_annotatie(wetstekst="")
    (project_root / "annotaties" / "leeg.json").write_text(json.dumps(ann))
    result = laad_annotaties(project_root)
    assert result == []


def test_laad_annotaties_zonder_annotatie_id_overgeslagen(project_root):
    ann = maak_annotatie(**{"annotatie-id": ""})
    (project_root / "annotaties" / "leeg.json").write_text(json.dumps(ann))
    result = laad_annotaties(project_root)
    assert result == []


def test_laad_annotaties_met_kruisrefs(project_root):
    ann = maak_annotatie()
    ann["kruisreferenties"] = [
        {"doel-bwb-id": "BWBR0002656", "doel-artikel": "1", "richting": "forward", "confidence": 0.9}
    ]
    (project_root / "annotaties" / "art9-1.json").write_text(json.dumps(ann))
    result = laad_annotaties(project_root)
    assert len(result[0]["kruisreferenties"]) == 1
    assert result[0]["kruisreferenties"][0]["doel_bwb_id"] == "BWBR0002656"


# ===== laad_artikel_indices =====

def test_laad_artikel_indices_leeg(project_root):
    assert laad_artikel_indices(project_root) == []


def test_laad_artikel_indices_lid_annotatie_overgeslagen(project_root):
    ann = maak_annotatie()
    (project_root / "annotaties" / "art9-1.json").write_text(json.dumps(ann))
    result = laad_artikel_indices(project_root)
    assert result == []


def test_laad_artikel_indices_een_bestand(project_root):
    data = {
        "artikel-id": "BWBR0004770/art9",
        "bwb-id": "BWBR0004770",
        "wet": "Invorderingswet 1990",
        "artikel": "9",
        "peildatum": "2024-01-01",
        "leden-annotaties": ["BWBR0004770/art9/lid1"],
    }
    (project_root / "annotaties" / "art9.json").write_text(json.dumps(data))
    result = laad_artikel_indices(project_root)
    assert len(result) == 1
    idx = result[0]
    assert idx["id"] == "BWBR0004770/art9"
    assert idx["artikel"] == "9"
    assert idx["leden_annotaties"] == ["BWBR0004770/art9/lid1"]


def test_laad_waarschuwingen_ontbreekt_geeft_leeg(tmp_path):
    assert laad_waarschuwingen(tmp_path) == {}


def test_laad_waarschuwingen_leest_json(tmp_path):
    (tmp_path / "rapporten").mkdir()
    data = {
        "waarschuwingen": [
            {"bestand": "begrippen/test.yaml", "boodschap": "[L3] Relaties leeg"},
        ],
        "fouten": [],
        "geslaagd": 1,
    }
    (tmp_path / "rapporten" / "validatie-rapport.json").write_text(json.dumps(data))
    result = laad_waarschuwingen(tmp_path)
    assert result == {"begrippen/test.yaml": ["[L3] Relaties leeg"]}


def test_waarschuwingen_voor_gevonden(tmp_path):
    index = {"begrippen/belastingschuldige.yaml": ["[L3] test"]}
    assert waarschuwingen_voor("belastingschuldige", index) == ["[L3] test"]


def test_waarschuwingen_voor_niet_gevonden(tmp_path):
    index = {"begrippen/belastingschuldige.yaml": ["[L3] test"]}
    assert waarschuwingen_voor("onbekend", index) == []


def test_waarschuwingen_voor_geen_substring_match(tmp_path):
    """Slug 'aanslag' mag geen warnings ophalen van 'belastingaanslag.yaml'."""
    index = {"begrippen/belastingaanslag.yaml": ["[L3] test"]}
    assert waarschuwingen_voor("aanslag", index) == []
