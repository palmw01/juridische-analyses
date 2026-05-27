"""L2 integriteitsvalidatie-tests — elke check heeft happy path én failure path."""
from pathlib import Path

import pytest
import yaml

from validate_note import (
    validate_integrity_begrip,
    validate_integrity_regel,
    validate_integrity_voorbeeldreeks,
    build_begrip_index,
    build_annotatie_index,
)
from tests.fixtures.begrippen import maak_begrip
from tests.fixtures.regels import maak_regel

DUMMY = Path("/tmp/test.yaml")


def leeg_project(tmp_path, mappen=("begrippen", "annotaties")):
    for d in mappen:
        (tmp_path / d).mkdir(exist_ok=True)
    return tmp_path


# ===== validate_integrity_begrip =====

def test_begrip_zonder_markeringen_geen_fouten(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(markeringen=[], **{"definitie-gebaseerd-op": []})
    idx = build_begrip_index(project)
    assert validate_integrity_begrip(data, DUMMY, idx, project) == []


def test_begrip_def_gebaseerd_op_ontbrekende_markering_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(**{"definitie-gebaseerd-op": ["m-bestaat-nooit"]})
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("definitie-gebaseerd-op" in e and "m-bestaat-nooit" in e for e in errors)


def test_begrip_def_gebaseerd_op_bestaande_primaire_markering_geen_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip()  # m-001 bestaat en heeft bijdrage primair
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert not any("definitie-gebaseerd-op" in e for e in errors)


def test_begrip_def_gebaseerd_op_niet_primair_bijdrage_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(
        markeringen=[{"markering-id": "m-001", "bijdrage": "verfijning",
                      "bron-annotatie-id": "x", "jas-klasse": "rechtssubject", "bevestigd": False}],
        **{"definitie-gebaseerd-op": ["m-001"]},
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("definitie-gebaseerd-op" in e and "verfijning" in e for e in errors)


def test_begrip_wikilink_in_bron_annotatie_id_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(
        markeringen=[{"markering-id": "m-001", "bijdrage": "primair",
                      "bron-annotatie-id": "[[annotaties/art9]]",
                      "jas-klasse": "rechtssubject", "bevestigd": False}],
        **{"definitie-gebaseerd-op": []},
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("wikilink" in e.lower() for e in errors)


def test_begrip_is_een_ontbreekt_in_index_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(
        relaties={"is-een": ["BWBR0004770/art9/lid1/ontbreekt"], "heeft": [], "leidt-tot": []},
        markeringen=[], **{"definitie-gebaseerd-op": []},
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("is-een" in e for e in errors)


def test_begrip_is_een_aanwezig_in_index_geen_fout(tmp_path):
    project = leeg_project(tmp_path)
    # Schrijf het doelbegrip naar de index
    doel = maak_begrip(**{"begrip-id": "BWBR0004770/art9/lid1/persoon", "begripsnaam": "persoon"})
    (project / "begrippen" / "persoon.yaml").write_text(yaml.dump(doel, allow_unicode=True))
    data = maak_begrip(
        relaties={"is-een": ["BWBR0004770/art9/lid1/persoon"], "heeft": [], "leidt-tot": []},
        markeringen=[], **{"definitie-gebaseerd-op": []},
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert not any("is-een" in e for e in errors)


# ===== validate_integrity_regel =====

def test_regel_leeg_project_geen_fouten(tmp_path):
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    data = maak_regel(invoer=[], uitvoer=[])  # geen cross-references → geen fouten
    idx = build_begrip_index(project)
    assert validate_integrity_regel(data, DUMMY, idx, project) == []


def test_regel_invoer_ontbreekt_geeft_fout(tmp_path):
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    data = maak_regel(invoer=["BWBR0004770/art9/lid1/ontbrekend-begrip"])
    idx = build_begrip_index(project)
    errors = validate_integrity_regel(data, DUMMY, idx, project)
    assert any("invoer" in e for e in errors)


def test_regel_uitvoer_ontbreekt_geeft_fout(tmp_path):
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    data = maak_regel(uitvoer=["BWBR0004770/art9/lid1/ontbrekend"])
    idx = build_begrip_index(project)
    errors = validate_integrity_regel(data, DUMMY, idx, project)
    assert any("uitvoer" in e for e in errors)


def test_regel_vervangt_niet_gevonden_geeft_fout(tmp_path):
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    data = maak_regel(**{"vervangt-regel-id": "r-bestaat-niet"})
    idx = build_begrip_index(project)
    errors = validate_integrity_regel(data, DUMMY, idx, project)
    assert any("vervangt-regel-id" in e for e in errors)


def test_regel_vervangt_gevonden_geen_fout(tmp_path):
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    (project / "regels" / "r-oud.yaml").write_text("regel-id: r-oud\n")
    data = maak_regel(**{"vervangt-regel-id": "r-oud"})
    idx = build_begrip_index(project)
    errors = validate_integrity_regel(data, DUMMY, idx, project)
    assert not any("vervangt-regel-id" in e for e in errors)


def test_regel_specialisatie_zonder_gespecialiseerd_id_geeft_l2(tmp_path):
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    data = maak_regel(soort="Specialisatieregel", prioriteit=1)
    idx = build_begrip_index(project)
    errors = validate_integrity_regel(data, DUMMY, idx, project)
    assert any("[L2]" in e and "gespecialiseerd-regel-id" in e for e in errors)


def test_regel_specialisatie_met_onbekende_gespecialiseerd_id_geeft_l2(tmp_path):
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    data = maak_regel(soort="Specialisatieregel", prioriteit=1)
    data["gespecialiseerd-regel-id"] = "AR-BWBR0004770-art9-lid1-bestaat-niet"
    idx = build_begrip_index(project)
    errors = validate_integrity_regel(data, DUMMY, idx, project)
    assert any("[L2]" in e and "gespecialiseerd-regel-id" in e and "niet gevonden" in e for e in errors)


def test_regel_specialisatie_met_bestaande_gespecialiseerd_id_geen_l2(tmp_path):
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    (project / "regels" / "AR-BWBR0024096-par9-5-e.yaml").write_text("regel-id: AR-BWBR0024096-par9-5-e\n")
    data = maak_regel(soort="Specialisatieregel", prioriteit=1)
    data["gespecialiseerd-regel-id"] = "AR-BWBR0024096-par9-5-e"
    idx = build_begrip_index(project)
    errors = validate_integrity_regel(data, DUMMY, idx, project)
    assert not any("gespecialiseerd-regel-id" in e for e in errors)


def test_regel_wikilink_in_invoer_geeft_fout(tmp_path):
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    data = maak_regel(invoer=["[[begrippen/belastingschuldige]]"])
    idx = build_begrip_index(project)
    errors = validate_integrity_regel(data, DUMMY, idx, project)
    assert any("wikilink" in e.lower() for e in errors)


def test_regel_rechtsfeit_id_ontbreekt_geeft_fout(tmp_path):
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    data = maak_regel(**{"rechtsfeit-id": "BWBR0004770/art9/lid1/ontbrekend-rf"})
    idx = build_begrip_index(project)
    errors = validate_integrity_regel(data, DUMMY, idx, project)
    assert any("rechtsfeit-id" in e for e in errors)


def test_regel_annotatie_id_wikilink_geeft_fout(tmp_path):
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    data = maak_regel(**{"annotatie-id": "[[annotaties/art9-1]]"})
    idx = build_begrip_index(project)
    errors = validate_integrity_regel(data, DUMMY, idx, project)
    assert any("annotatie-id" in e for e in errors)


def test_regel_annotatie_id_niet_gevonden_geeft_fout(tmp_path):
    import json
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    from tests.fixtures.annotaties import maak_annotatie
    (project / "annotaties" / "art9-1.json").write_text(
        json.dumps(maak_annotatie(**{"annotatie-id": "BWBR0004770/art9/lid1"}))
    )
    data = maak_regel(**{"annotatie-id": "BWBR0004770/art9/lid2"})
    idx = build_begrip_index(project)
    errors = validate_integrity_regel(data, DUMMY, idx, project)
    assert any("annotatie-id" in e for e in errors)


def test_regel_annotatie_id_gevonden_geen_fout(tmp_path):
    import json
    project = leeg_project(tmp_path, mappen=("begrippen", "regels", "annotaties"))
    from tests.fixtures.annotaties import maak_annotatie
    (project / "annotaties" / "art9-1.json").write_text(
        json.dumps(maak_annotatie(**{"annotatie-id": "BWBR0004770/art9/lid1"}))
    )
    data = maak_regel(**{"annotatie-id": "BWBR0004770/art9/lid1"})
    idx = build_begrip_index(project)
    errors = validate_integrity_regel(data, DUMMY, idx, project)
    assert not any("annotatie-id" in e for e in errors)


# ===== validate_integrity_begrip — uitgebreide paden =====

def test_begrip_homoniem_conflict_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(
        markeringen=[
            {"markering-id": "m-001", "bijdrage": "primair", "bron-annotatie-id": "x",
             "jas-klasse": "rechtsfeit", "bevestigd": False},
            {"markering-id": "m-002", "bijdrage": "aanvullend", "bron-annotatie-id": "y",
             "jas-klasse": "tijdsaanduiding", "bevestigd": False},
        ],
        **{"definitie-gebaseerd-op": []},
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("homoniem" in e.lower() for e in errors)


def test_begrip_bron_annotatie_id_niet_in_index_geeft_fout(tmp_path):
    import json
    project = leeg_project(tmp_path)
    from tests.fixtures.annotaties import maak_annotatie
    (project / "annotaties" / "art9-1.json").write_text(
        json.dumps(maak_annotatie(**{"annotatie-id": "BWBR0004770/art9/lid1"}))
    )
    data = maak_begrip(
        markeringen=[{"markering-id": "m-001", "bijdrage": "primair",
                      "bron-annotatie-id": "BWBR0004770/art9/lid2",
                      "tekst": "x", "interpretatiemethode": "grammaticaal", "bevestigd": False}],
        **{"definitie-gebaseerd-op": ["m-001"]},
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("bron-annotatie-id" in e for e in errors)


def test_begrip_definitie_context_markering_id_ontbreekt_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(
        definitie={
            "kern": "de belastingplichtige",
            "contexten": [{"markering-id": "m-ontbreekt", "tekst": "extra context"}],
        },
        **{"definitie-gebaseerd-op": []},
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("contexten" in e and "m-ontbreekt" in e for e in errors)


def test_begrip_heeft_relatie_ontbreekt_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(
        relaties={"is-een": [], "heeft": [{"begrip-id": "BWBR0004770/art9/lid1/ontbrekend"}], "leidt-tot": []},
        markeringen=[], **{"definitie-gebaseerd-op": []},
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("heeft" in e for e in errors)


def test_begrip_leidt_tot_ontbreekt_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(
        relaties={"is-een": [], "heeft": [], "leidt-tot": [{"begrip-id": "BWBR0004770/art9/lid1/ontbrekend"}]},
        markeringen=[], **{"definitie-gebaseerd-op": []},
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("leidt-tot" in e for e in errors)


def test_begrip_status_gevalideerd_lege_kern_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(
        status="gevalideerd",
        definitie={"kern": "", "contexten": []},
        markeringen=[], **{"definitie-gebaseerd-op": []},
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("gevalideerd" in e and "kern" in e for e in errors)


def test_begrip_status_vervallen_zonder_vervangen_door_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(
        status="vervallen",
        markeringen=[], **{"definitie-gebaseerd-op": [], "vervangen-door": None},
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("vervallen" in e and "vervangen-door" in e for e in errors)


def test_begrip_herkomst_afgeleid_afleidingsregel_zonder_id_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(
        herkomst="afgeleid",
        **{"jas-klasse": "afleidingsregel", "definitie-gebaseerd-op": []},
        markeringen=[],
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("afleidingsregel-id" in e for e in errors)


def test_begrip_herkomst_afgeleid_zonder_uitvoer_id_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(
        herkomst="afgeleid",
        **{"jas-klasse": "variabele", "definitie-gebaseerd-op": []},
        markeringen=[],
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("uitvoer-van-regel-id" in e for e in errors)


def test_begrip_afleidingsregel_id_op_verkeerde_klasse_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(
        **{"jas-klasse": "variabele", "afleidingsregel-id": "AR-BWBR0004770-art9-lid1-a", "definitie-gebaseerd-op": []},
        markeringen=[],
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("afleidingsregel-id" in e and "variabele" in e for e in errors)


def test_begrip_afleidingsregel_id_niet_gevonden_in_regels_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    (project / "regels").mkdir()
    data = maak_begrip(
        **{"jas-klasse": "afleidingsregel", "afleidingsregel-id": "AR-bestaat-niet",
           "definitie-gebaseerd-op": []},
        markeringen=[],
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("afleidingsregel-id" in e and "AR-bestaat-niet" in e for e in errors)


def test_begrip_uitvoer_van_regel_id_niet_gevonden_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    (project / "regels").mkdir()
    data = maak_begrip(
        herkomst="afgeleid",
        **{"jas-klasse": "variabele", "uitvoer-van-regel-id": "AR-bestaat-niet",
           "definitie-gebaseerd-op": []},
        markeringen=[],
    )
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("uitvoer-van-regel-id" in e for e in errors)


# ===== validate_integrity_voorbeeldreeks =====

def _maak_vr(**overrides) -> dict:
    base = {
        "voorbeeldreeks-id": "VR-BWBR0004770-art9-lid1-a",
        "afleidingsregel-id": "AR-BWBR0004770-art9-lid1-a",
        "naam": "Test voorbeeldreeks",
        "status": "concept",
        "peildatum": "2026-01-01",
        "aangemaakt-op": "2026-01-01",
        "kolommen": [
            {
                "label": "Happy path",
                "invoer": {},
                "is-invoer-juist": "ja",
                "verwachte-uitvoer": {},
                "is-voorspelling-juist": "?",
            }
        ],
    }
    base.update(overrides)
    return base


def test_vr_geen_fouten_bij_valide_data(tmp_path):
    project = leeg_project(tmp_path, ("begrippen", "regels"))
    (project / "regels" / "AR-BWBR0004770-art9-lid1-a.yaml").write_text("regel-id: AR-BWBR0004770-art9-lid1-a\n")
    data = _maak_vr()
    idx = build_begrip_index(project)
    assert validate_integrity_voorbeeldreeks(data, DUMMY, idx, project) == []


def test_vr_ontbrekende_regel_geeft_fout(tmp_path):
    project = leeg_project(tmp_path, ("begrippen", "regels"))
    data = _maak_vr(**{"afleidingsregel-id": "AR-BESTAAT-NIET"})
    idx = build_begrip_index(project)
    errors = validate_integrity_voorbeeldreeks(data, DUMMY, idx, project)
    assert any("AR-BESTAAT-NIET" in e for e in errors)


def test_vr_bestaande_regel_md_geen_fout(tmp_path):
    project = leeg_project(tmp_path, ("begrippen", "regels"))
    (project / "regels" / "AR-BWBR0004770-art9-lid1-a.md").write_text("---\nregel-id: AR-BWBR0004770-art9-lid1-a\n---\n")
    data = _maak_vr()
    idx = build_begrip_index(project)
    assert validate_integrity_voorbeeldreeks(data, DUMMY, idx, project) == []


def test_vr_onbekend_invoer_begrip_geeft_fout(tmp_path):
    project = leeg_project(tmp_path, ("begrippen", "regels"))
    (project / "regels" / "AR-BWBR0004770-art9-lid1-a.yaml").write_text("regel-id: AR-BWBR0004770-art9-lid1-a\n")
    data = _maak_vr(kolommen=[{
        "label": "test",
        "invoer": {"bestaat/niet": "waarde"},
        "is-invoer-juist": "ja",
        "verwachte-uitvoer": {},
        "is-voorspelling-juist": "?",
    }])
    idx = build_begrip_index(project)
    errors = validate_integrity_voorbeeldreeks(data, DUMMY, idx, project)
    assert any("invoer" in e and "niet" in e for e in errors)


def test_vr_onbekend_uitvoer_begrip_geeft_fout(tmp_path):
    project = leeg_project(tmp_path, ("begrippen", "regels"))
    (project / "regels" / "AR-BWBR0004770-art9-lid1-a.yaml").write_text("regel-id: AR-BWBR0004770-art9-lid1-a\n")
    data = _maak_vr(kolommen=[{
        "label": "test",
        "invoer": {},
        "is-invoer-juist": "ja",
        "verwachte-uitvoer": {"bestaat/niet": "waarde"},
        "is-voorspelling-juist": "?",
    }])
    idx = build_begrip_index(project)
    errors = validate_integrity_voorbeeldreeks(data, DUMMY, idx, project)
    assert any("verwachte-uitvoer" in e for e in errors)


def test_vr_invoer_onjuist_maar_nvt_geen_fout(tmp_path):
    project = leeg_project(tmp_path, ("begrippen", "regels"))
    (project / "regels" / "AR-BWBR0004770-art9-lid1-a.yaml").write_text("regel-id: AR-BWBR0004770-art9-lid1-a\n")
    data = _maak_vr(kolommen=[{
        "label": "Ongeldig geval",
        "invoer": {},
        "is-invoer-juist": "nee",
        "verwachte-uitvoer": {},
        "is-voorspelling-juist": "nvt",
    }])
    idx = build_begrip_index(project)
    assert validate_integrity_voorbeeldreeks(data, DUMMY, idx, project) == []


def test_vr_invoer_onjuist_maar_voorspelling_ja_geeft_fout(tmp_path):
    project = leeg_project(tmp_path, ("begrippen", "regels"))
    (project / "regels" / "AR-BWBR0004770-art9-lid1-a.yaml").write_text("regel-id: AR-BWBR0004770-art9-lid1-a\n")
    data = _maak_vr(kolommen=[{
        "label": "Onjuist geval",
        "invoer": {},
        "is-invoer-juist": "nee",
        "verwachte-uitvoer": {},
        "is-voorspelling-juist": "ja",
    }])
    idx = build_begrip_index(project)
    errors = validate_integrity_voorbeeldreeks(data, DUMMY, idx, project)
    assert any("is-invoer-juist=nee" in e for e in errors)


def test_vr_leeg_afleidingsregel_id_geen_fout(tmp_path):
    project = leeg_project(tmp_path, ("begrippen", "regels"))
    data = _maak_vr(**{"afleidingsregel-id": ""})
    idx = build_begrip_index(project)
    assert validate_integrity_voorbeeldreeks(data, DUMMY, idx, project) == []


# ===== scenario-refs integriteit (A3c) =====

def test_begrip_scenario_refs_bestaand_scenario_geen_fout(tmp_path):
    project = leeg_project(tmp_path)
    scenarios_dir = tmp_path / "scenarios"
    scenarios_dir.mkdir()
    (scenarios_dir / "scen-001.yaml").write_text("scenario-id: scen-001\n")
    data = maak_begrip(**{"scenario-refs": [{"scenario-id": "scen-001", "rol": "rechtssubject"}]})
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert not any("scenario" in e for e in errors)


def test_begrip_scenario_refs_ontbrekend_scenario_geeft_fout(tmp_path):
    project = leeg_project(tmp_path)
    (tmp_path / "scenarios").mkdir()
    data = maak_begrip(**{"scenario-refs": [{"scenario-id": "scen-ontbreekt", "rol": "rechtssubject"}]})
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert any("scen-ontbreekt" in e for e in errors)


def test_begrip_scenario_refs_leeg_scenario_id_overgeslagen(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip(**{"scenario-refs": [{"scenario-id": "", "rol": "rechtssubject"}]})
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert not any("scenario" in e for e in errors)


def test_begrip_geen_scenario_refs_geen_fout(tmp_path):
    project = leeg_project(tmp_path)
    data = maak_begrip()
    idx = build_begrip_index(project)
    errors = validate_integrity_begrip(data, DUMMY, idx, project)
    assert not any("scenario" in e for e in errors)
