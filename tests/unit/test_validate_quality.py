"""L3 kwaliteitscontrole-tests — elke check heeft happy path én failure path."""
from pathlib import Path

from validate_note import validate_quality_begrip, validate_quality_regel
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
