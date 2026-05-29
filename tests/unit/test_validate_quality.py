"""L3 kwaliteitscontrole-tests — elke check heeft happy path én failure path."""
import json
from pathlib import Path

from validate_note import validate_quality_begrip, validate_quality_regel, resolve_markering_jas_klasse
from tests.fixtures.begrippen import maak_begrip
from tests.fixtures.regels import maak_regel

DUMMY = Path("/tmp/test.yaml")


# ===== validate_quality_begrip =====

def test_begrip_alle_bevestigd_geen_onbevestigd_warning():
    data = maak_begrip(
        markeringen=[{"markering-id": "m-001", "bijdrage": "primair",
                      "bron-annotatie-id": "x", "jas-klasse": "rechtssubject",
                      "bevestigd": True}],
    )
    warnings = validate_quality_begrip(data, DUMMY)
    assert not any("onbevestigd" in w for w in warnings)


def test_begrip_alle_onbevestigd_geeft_warning():
    data = maak_begrip()  # default: bevestigd=False
    warnings = validate_quality_begrip(data, DUMMY)
    assert any("onbevestigd" in w for w in warnings)


def test_begrip_geen_markeringen_geen_onbevestigd_warning():
    data = maak_begrip(markeringen=[])
    warnings = validate_quality_begrip(data, DUMMY)
    assert not any("onbevestigd" in w for w in warnings)


# ===== Menselijke validatie — validatie-blok + bevestigd-door (L3) =====

def test_begrip_gevalideerd_zonder_validatie_geeft_l3():
    data = maak_begrip(status="gevalideerd")
    warnings = validate_quality_begrip(data, DUMMY)
    assert any("geregistreerd menselijk oordeel" in w for w in warnings)


def test_begrip_gevalideerd_met_volledig_validatieblok_geen_l3():
    data = maak_begrip(status="gevalideerd", validatie={
        "gevalideerd-door": "JdG", "gevalideerd-op": "2026-05-29", "oordeel": "goedgekeurd",
    })
    warnings = validate_quality_begrip(data, DUMMY)
    assert not any("geregistreerd menselijk oordeel" in w for w in warnings)


def test_begrip_gevalideerd_met_afgekeurd_oordeel_geeft_l3():
    data = maak_begrip(status="gevalideerd", validatie={
        "gevalideerd-door": "JdG", "gevalideerd-op": "2026-05-29", "oordeel": "afgekeurd",
    })
    warnings = validate_quality_begrip(data, DUMMY)
    assert any("geregistreerd menselijk oordeel" in w for w in warnings)


def test_begrip_bevestigd_zonder_bevestigd_door_geeft_l3():
    data = maak_begrip(markeringen=[{
        "markering-id": "m-001", "bijdrage": "primair", "bron-annotatie-id": "x",
        "tekst": "t", "interpretatiemethode": "grammaticaal", "bevestigd": True,
    }])
    warnings = validate_quality_begrip(data, DUMMY)
    assert any("mist bevestigd-door" in w for w in warnings)


def test_begrip_bevestigd_met_bevestigd_door_geen_l3():
    data = maak_begrip(markeringen=[{
        "markering-id": "m-001", "bijdrage": "primair", "bron-annotatie-id": "x",
        "tekst": "t", "interpretatiemethode": "grammaticaal", "bevestigd": True,
        "bevestigd-door": "jurist",
    }])
    warnings = validate_quality_begrip(data, DUMMY)
    assert not any("mist bevestigd-door" in w for w in warnings)


# ===== Scenario-specifieke begripsnaam (valkuil V1) =====

def test_begripsnaam_met_maandnaam_geeft_l3():
    data = maak_begrip(begripsnaam="vervaldag-oktober")
    warnings = validate_quality_begrip(data, DUMMY)
    assert any("scenario-specifiek" in w and "maandnaam" in w for w in warnings)


def test_begripsnaam_met_jaartal_geeft_l3():
    data = maak_begrip(begripsnaam="belastingbedrag-2024-ib")
    warnings = validate_quality_begrip(data, DUMMY)
    assert any("scenario-specifiek" in w and "jaartal" in w for w in warnings)


def test_begripsnaam_met_voorbeeld_suffix_geeft_l3():
    data = maak_begrip(begripsnaam="vervaldatum-een-maand-voorbeeld")
    warnings = validate_quality_begrip(data, DUMMY)
    assert any("scenario-specifiek" in w and "'-voorbeeld-'" in w for w in warnings)


def test_begripsnaam_zonder_scenario_signaal_geen_l3():
    data = maak_begrip(begripsnaam="vervaldag-kortemaand-een-maand")
    warnings = validate_quality_begrip(data, DUMMY)
    assert not any("scenario-specifiek" in w for w in warnings)


def test_begripsnaam_leeg_geen_l3_voor_scenario():
    data = maak_begrip(begripsnaam="")
    warnings = validate_quality_begrip(data, DUMMY)
    assert not any("scenario-specifiek" in w for w in warnings)


def test_begrip_kern_gevuld_geen_kern_leeg_warning():
    data = maak_begrip()
    warnings = validate_quality_begrip(data, DUMMY)
    assert not any("kern is leeg" in w for w in warnings)


def test_begrip_kern_leeg_geeft_warning():
    data = maak_begrip(definitie={"kern": "", "contexten": []})
    warnings = validate_quality_begrip(data, DUMMY)
    assert any("kern is leeg" in w for w in warnings)


def test_begrip_kern_eindigt_op_punt_geeft_warning():
    data = maak_begrip(definitie={"kern": "de persoon die belasting verschuldigd is.", "contexten": []})
    warnings = validate_quality_begrip(data, DUMMY)
    assert any("punt" in w for w in warnings)


def test_begrip_kern_zonder_punt_geen_punt_warning():
    data = maak_begrip()
    warnings = validate_quality_begrip(data, DUMMY)
    assert not any("punt" in w for w in warnings)


def test_begrip_kern_bevat_begripsnaam_geeft_warning():
    data = maak_begrip(
        begripsnaam="belastingschuldige",
        definitie={"kern": "een belastingschuldige is iemand die belasting verschuldigd is", "contexten": []},
    )
    warnings = validate_quality_begrip(data, DUMMY)
    assert any("substitutiebaarheidsregel" in w for w in warnings)


def test_begrip_kern_zonder_begripsnaam_geen_substitutie_warning():
    data = maak_begrip()  # kern bevat "de persoon die..." niet de begripsnaam zelf
    warnings = validate_quality_begrip(data, DUMMY)
    assert not any("substitutiebaarheidsregel" in w for w in warnings)


def test_begrip_lege_relaties_geeft_warning():
    data = maak_begrip(relaties={"is-een": [], "heeft": [], "leidt-tot": []})
    warnings = validate_quality_begrip(data, DUMMY)
    assert any("relaties leeg" in w for w in warnings)


def test_begrip_status_te_verrijken_geeft_warning():
    data = maak_begrip(status="te-verrijken")
    warnings = validate_quality_begrip(data, DUMMY)
    assert any("te-verrijken" in w for w in warnings)


def test_begrip_status_concept_geen_te_verrijken_warning():
    data = maak_begrip(status="concept")
    warnings = validate_quality_begrip(data, DUMMY)
    assert not any("te-verrijken" in w for w in warnings)


def test_begrip_aanvullend_zonder_context_geeft_warning():
    data = maak_begrip(
        markeringen=[
            {"markering-id": "m-001", "bijdrage": "primair", "bron-annotatie-id": "x",
             "jas-klasse": "rechtssubject", "bevestigd": False},
            {"markering-id": "m-002", "bijdrage": "aanvullend", "bron-annotatie-id": "y",
             "jas-klasse": "rechtssubject", "bevestigd": False},
        ],
        definitie={"kern": "de persoon die belasting verschuldigd is", "contexten": []},
    )
    warnings = validate_quality_begrip(data, DUMMY)
    assert any("aanvullend" in w and "context" in w for w in warnings)


def test_begrip_aanvullend_met_context_geen_warning():
    data = maak_begrip(
        markeringen=[
            {"markering-id": "m-001", "bijdrage": "primair", "bron-annotatie-id": "x",
             "jas-klasse": "rechtssubject", "bevestigd": False},
            {"markering-id": "m-002", "bijdrage": "aanvullend", "bron-annotatie-id": "y",
             "jas-klasse": "rechtssubject", "bevestigd": False},
        ],
        definitie={
            "kern": "de persoon die belasting verschuldigd is",
            "contexten": [{"markering-id": "m-002", "tekst": "aanvullende context"}],
        },
    )
    warnings = validate_quality_begrip(data, DUMMY)
    assert not any("aanvullend" in w and "context" in w for w in warnings)


# ===== validate_quality_regel =====

def test_regel_met_grensgeval_geen_grensgeval_warning():
    data = maak_regel()  # bevat al juridisch-juist: False
    warnings = validate_quality_regel(data, DUMMY)
    assert not any("grensgeval" in w for w in warnings)


def test_regel_zonder_grensgeval_geeft_warning():
    data = maak_regel(voorbeeldreeksen=[
        {"invoerwaarden": {}, "verwachte-uitkomst": {}, "juridisch-juist": True}
    ])
    warnings = validate_quality_regel(data, DUMMY)
    assert any("grensgeval" in w for w in warnings)


def test_regel_zonder_voorbeeldreeksen_geen_grensgeval_warning():
    data = maak_regel(voorbeeldreeksen=[])
    warnings = validate_quality_regel(data, DUMMY)
    assert not any("grensgeval" in w for w in warnings)


def test_regel_prioriteit_op_niet_specialisatie_geeft_warning():
    data = maak_regel(soort="Afleidingsregel", prioriteit=1)
    warnings = validate_quality_regel(data, DUMMY)
    assert any("prioriteit" in w and "Specialisatieregel" in w for w in warnings)


def test_regel_prioriteit_op_specialisatie_geen_warning():
    data = maak_regel(soort="Specialisatieregel", prioriteit=1)
    warnings = validate_quality_regel(data, DUMMY)
    assert not any("prioriteit" in w and "Specialisatieregel" in w for w in warnings)


def test_regel_prioriteit_none_geen_warning():
    data = maak_regel(soort="Afleidingsregel", prioriteit=None)
    warnings = validate_quality_regel(data, DUMMY)
    assert not any("prioriteit" in w for w in warnings)


def test_begrip_kern_gevuld_geen_voorbeelden_geeft_warning():
    data = maak_begrip(voorbeelden=[])
    warnings = validate_quality_begrip(data, DUMMY)
    assert any("voorbeelden ontbreken" in w for w in warnings)


# ===== resolve_markering_jas_klasse =====

def _schrijf_annotatie_lid(tmp_path: Path, ann_id: str, begrip_id: str, jas_klasse: str) -> None:
    """Hulpfunctie: schrijf minimale annotatie-lid JSON naar tmp_path/annotaties/."""
    annotaties_dir = tmp_path / "annotaties"
    annotaties_dir.mkdir(parents=True, exist_ok=True)
    fp = annotaties_dir / f"{ann_id.replace('/', '_')}.json"
    fp.write_text(json.dumps({
        "annotatie-id": ann_id,
        "annotatierijen": [
            {"rij-id": "r-001", "begrip-id": begrip_id, "jas-klasse": jas_klasse}
        ],
    }))


def test_resolve_markering_jas_klasse_gevonden(tmp_path):
    ann_id = "BWBR0004770/art2/lid2"
    begrip_id = "BWBR0004770/art9/lid1/belastingaanslag"
    _schrijf_annotatie_lid(tmp_path, ann_id, begrip_id, "brondefinitie")
    result = resolve_markering_jas_klasse(ann_id, begrip_id, tmp_path)
    assert result == "brondefinitie"


def test_resolve_markering_jas_klasse_annotatie_niet_gevonden(tmp_path):
    (tmp_path / "annotaties").mkdir()
    result = resolve_markering_jas_klasse("BWBR0004770/art99/lid9", "x/y/z", tmp_path)
    assert result is None


def test_resolve_markering_jas_klasse_begrip_id_niet_in_rijen(tmp_path):
    ann_id = "BWBR0004770/art2/lid2"
    _schrijf_annotatie_lid(tmp_path, ann_id, "BWBR0004770/art9/lid1/ander-begrip", "brondefinitie")
    result = resolve_markering_jas_klasse(ann_id, "BWBR0004770/art9/lid1/belastingaanslag", tmp_path)
    assert result is None


def test_resolve_markering_jas_klasse_geen_annotaties_map(tmp_path):
    result = resolve_markering_jas_klasse("BWBR0004770/art2/lid2", "x/y/z", tmp_path)
    assert result is None


# ===== L3 prioriteitsconflict markeringen =====

def _maak_begrip_met_conflict(tmp_path: Path) -> dict:
    """Begrip waarbij primaire markering rechtsobject is en niet-primaire brondefinitie."""
    ann_primair = "BWBR0004770/art9/lid1"
    ann_niet_primair = "BWBR0004770/art2/lid2"
    begrip_id = "BWBR0004770/art9/lid1/belastingaanslag"
    _schrijf_annotatie_lid(tmp_path, ann_primair, begrip_id, "rechtsobject")
    _schrijf_annotatie_lid(tmp_path, ann_niet_primair, begrip_id, "brondefinitie")
    return maak_begrip(
        **{
            "begrip-id": begrip_id,
            "markeringen": [
                {"markering-id": "m-001", "bijdrage": "primair",
                 "bron-annotatie-id": ann_primair, "bevestigd": False},
                {"markering-id": "m-002", "bijdrage": "aanvullend",
                 "bron-annotatie-id": ann_niet_primair, "bevestigd": False},
            ],
        }
    )


def test_begrip_prioriteitsconflict_geeft_warning(tmp_path):
    data = _maak_begrip_met_conflict(tmp_path)
    warnings = validate_quality_begrip(data, DUMMY, project_root=tmp_path)
    assert any("prioriteitsconflict" in w for w in warnings)


def test_begrip_primaire_is_brondefinitie_geen_prioriteitsconflict(tmp_path):
    ann_primair = "BWBR0004770/art2/lid2"
    ann_aanvullend = "BWBR0004770/art9/lid1"
    begrip_id = "BWBR0004770/art9/lid1/belastingaanslag"
    _schrijf_annotatie_lid(tmp_path, ann_primair, begrip_id, "brondefinitie")
    _schrijf_annotatie_lid(tmp_path, ann_aanvullend, begrip_id, "rechtsobject")
    data = maak_begrip(
        **{
            "begrip-id": begrip_id,
            "markeringen": [
                {"markering-id": "m-001", "bijdrage": "primair",
                 "bron-annotatie-id": ann_primair, "bevestigd": False},
                {"markering-id": "m-002", "bijdrage": "aanvullend",
                 "bron-annotatie-id": ann_aanvullend, "bevestigd": False},
            ],
        }
    )
    warnings = validate_quality_begrip(data, DUMMY, project_root=tmp_path)
    assert not any("prioriteitsconflict" in w for w in warnings)


def test_begrip_enkelvoudige_markering_geen_prioriteitsconflict(tmp_path):
    data = maak_begrip()  # slechts 1 markering
    warnings = validate_quality_begrip(data, DUMMY, project_root=tmp_path)
    assert not any("prioriteitsconflict" in w for w in warnings)


def test_begrip_geen_project_root_geen_prioriteitscheck():
    data = maak_begrip(
        **{
            "begrip-id": "x/y/z",
            "markeringen": [
                {"markering-id": "m-001", "bijdrage": "primair",
                 "bron-annotatie-id": "a/b/c", "bevestigd": False},
                {"markering-id": "m-002", "bijdrage": "aanvullend",
                 "bron-annotatie-id": "d/e/f", "bevestigd": False},
            ],
        }
    )
    warnings = validate_quality_begrip(data, DUMMY, project_root=None)
    assert not any("prioriteitsconflict" in w for w in warnings)


def test_resolve_markering_jas_klasse_corrupt_json_geeft_none(tmp_path):
    annotaties_dir = tmp_path / "annotaties"
    annotaties_dir.mkdir()
    (annotaties_dir / "corrupt.json").write_text("GEEN GELDIGE JSON{{")
    result = resolve_markering_jas_klasse("BWBR0004770/art2/lid2", "x/y/z", tmp_path)
    assert result is None


def test_begrip_prioriteitscheck_slaat_markering_met_lege_id_over(tmp_path):
    """Markering zonder markering-id of bron-annotatie-id wordt stilzwijgend overgeslagen."""
    data = maak_begrip(
        **{
            "begrip-id": "BWBR0004770/art9/lid1/belastingaanslag",
            "markeringen": [
                {"markering-id": "m-001", "bijdrage": "primair",
                 "bron-annotatie-id": "BWBR0004770/art9/lid1", "bevestigd": False},
                {"markering-id": "", "bijdrage": "aanvullend",
                 "bron-annotatie-id": "", "bevestigd": False},
            ],
        }
    )
    warnings = validate_quality_begrip(data, DUMMY, project_root=tmp_path)
    assert not any("prioriteitsconflict" in w for w in warnings)


def test_begrip_prioriteitscheck_slaat_markering_zonder_jas_over(tmp_path):
    """Markering waarvoor geen jas-klasse gevonden wordt (jas is None) wordt overgeslagen."""
    ann_primair = "BWBR0004770/art9/lid1"
    begrip_id = "BWBR0004770/art9/lid1/belastingaanslag"
    _schrijf_annotatie_lid(tmp_path, ann_primair, begrip_id, "rechtsobject")
    data = maak_begrip(
        **{
            "begrip-id": begrip_id,
            "markeringen": [
                {"markering-id": "m-001", "bijdrage": "primair",
                 "bron-annotatie-id": ann_primair, "bevestigd": False},
                {"markering-id": "m-002", "bijdrage": "aanvullend",
                 "bron-annotatie-id": "BWBR0004770/art99/lid9", "bevestigd": False},
            ],
        }
    )
    warnings = validate_quality_begrip(data, DUMMY, project_root=tmp_path)
    assert not any("prioriteitsconflict" in w for w in warnings)


def test_begrip_kern_gevuld_met_voorbeelden_geen_warning():
    data = maak_begrip(voorbeelden=[
        {"stelling": "test", "waar": True},
        {"stelling": "grens", "waar": False},
    ])
    warnings = validate_quality_begrip(data, DUMMY)
    assert not any("voorbeelden ontbreken" in w for w in warnings)


def test_begrip_kern_leeg_geen_voorbeelden_warning():
    data = maak_begrip(definitie={"kern": "", "contexten": []}, voorbeelden=[])
    warnings = validate_quality_begrip(data, DUMMY)
    assert not any("voorbeelden ontbreken" in w for w in warnings)


def test_regel_specialisatie_zonder_prioriteit_geeft_warning():
    data = maak_regel(soort="Specialisatieregel", prioriteit=None)
    warnings = validate_quality_regel(data, DUMMY)
    assert any("Specialisatieregel" in w and "prioriteit" in w for w in warnings)


def test_regel_specialisatie_geen_l3_warning_voor_gespecialiseerd_id():
    """gespecialiseerd-regel-id wordt vanaf nu in L2 gecontroleerd, niet in L3."""
    data = maak_regel(soort="Specialisatieregel", prioriteit=1)
    warnings = validate_quality_regel(data, DUMMY)
    assert not any("gespecialiseerd-regel-id" in w for w in warnings)


# ===== validate_quality_voorbeeldreeks =====

from validate_note import validate_quality_voorbeeldreeks


def _maak_vr_data(n_kolommen=3, status="gereviseerd", open_beoordelingen=0) -> dict:
    kolommen = []
    for i in range(n_kolommen):
        is_vpj = "?" if i < open_beoordelingen else "ja"
        kolommen.append({
            "label": f"Kolom {i}",
            "invoer": {},
            "is-invoer-juist": "ja",
            "verwachte-uitvoer": {},
            "is-voorspelling-juist": is_vpj,
        })
    return {
        "voorbeeldreeks-id": "VR-BWBR0004770-art9-lid1-a",
        "afleidingsregel-id": "AR-BWBR0004770-art9-lid1-a",
        "naam": "Test",
        "status": status,
        "peildatum": "2026-01-01",
        "aangemaakt-op": "2026-01-01",
        "kolommen": kolommen,
    }


def test_vr_drie_kolommen_gereviseerd_geen_warnings():
    data = _maak_vr_data(n_kolommen=3, status="gereviseerd")
    warnings = validate_quality_voorbeeldreeks(data, DUMMY)
    assert warnings == []


def test_vr_minder_dan_drie_kolommen_geeft_warning():
    data = _maak_vr_data(n_kolommen=2)
    warnings = validate_quality_voorbeeldreeks(data, DUMMY)
    assert any("minder dan 3 kolommen" in w for w in warnings)


def test_vr_open_beoordelingen_geeft_warning():
    data = _maak_vr_data(n_kolommen=3, open_beoordelingen=2)
    warnings = validate_quality_voorbeeldreeks(data, DUMMY)
    assert any("is-voorspelling-juist=?" in w for w in warnings)
    assert any("2 kolom" in w for w in warnings)


def test_vr_geen_open_beoordelingen_geen_warning():
    data = _maak_vr_data(n_kolommen=3, open_beoordelingen=0)
    warnings = validate_quality_voorbeeldreeks(data, DUMMY)
    assert not any("is-voorspelling-juist=?" in w for w in warnings)


def test_vr_status_concept_geeft_warning():
    data = _maak_vr_data(status="concept")
    warnings = validate_quality_voorbeeldreeks(data, DUMMY)
    assert any("concept" in w for w in warnings)


def test_vr_status_gevalideerd_geen_concept_warning():
    data = _maak_vr_data(status="gevalideerd")
    warnings = validate_quality_voorbeeldreeks(data, DUMMY)
    assert not any("concept" in w for w in warnings)


def test_vr_is_invoer_nee_telt_niet_mee_als_open_beoordeling():
    data = _maak_vr_data(n_kolommen=3, status="gereviseerd")
    data["kolommen"][0]["is-invoer-juist"] = "nee"
    data["kolommen"][0]["is-voorspelling-juist"] = "?"
    warnings = validate_quality_voorbeeldreeks(data, DUMMY)
    assert not any("is-voorspelling-juist=?" in w for w in warnings)


def test_vr_gevalideerd_zonder_validatie_geeft_l3():
    data = _maak_vr_data(status="gevalideerd")
    warnings = validate_quality_voorbeeldreeks(data, DUMMY)
    assert any("geregistreerd menselijk oordeel" in w for w in warnings)


def test_vr_gevalideerd_met_validatieblok_geen_l3():
    data = _maak_vr_data(status="gevalideerd")
    data["validatie"] = {
        "gevalideerd-door": "JdG", "gevalideerd-op": "2026-05-29", "oordeel": "goedgekeurd",
    }
    warnings = validate_quality_voorbeeldreeks(data, DUMMY)
    assert not any("geregistreerd menselijk oordeel" in w for w in warnings)


# ===== A3c — scenario-refs L3-waarschuwing =====

def test_begrip_rechtsbetrekking_zonder_scenario_refs_geeft_l3_warning():
    data = maak_begrip(**{"jas-klasse": "rechtsbetrekking", "scenario-refs": []})
    warnings = validate_quality_begrip(data, DUMMY)
    assert any("scenario-refs" in w for w in warnings)


def test_begrip_rechtsfeit_zonder_scenario_refs_geeft_l3_warning():
    data = maak_begrip(**{"jas-klasse": "rechtsfeit", "scenario-refs": []})
    warnings = validate_quality_begrip(data, DUMMY)
    assert any("scenario-refs" in w for w in warnings)


def test_begrip_rechtsbetrekking_met_scenario_refs_geen_warning():
    data = maak_begrip(**{
        "jas-klasse": "rechtsbetrekking",
        "scenario-refs": [{"scenario-id": "scen-001", "rol": "rechtssubject"}],
    })
    warnings = validate_quality_begrip(data, DUMMY)
    assert not any("scenario-refs" in w for w in warnings)


def test_begrip_andere_klasse_zonder_scenario_refs_geen_warning():
    data = maak_begrip(**{"jas-klasse": "variabele", "scenario-refs": []})
    warnings = validate_quality_begrip(data, DUMMY)
    assert not any("scenario-refs" in w for w in warnings)
