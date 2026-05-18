"""Tests voor sitegen/pages/regels.py."""
from html import escape
from pathlib import Path

from sitegen.pages.regels import gen_regels


def _regel(**overrides) -> dict:
    base = {
        "id": "AR-BWBR0004770-art9-lid1-a",
        "naam": "Berekening betalingstermijn",
        "soort": "Rekenregel",
        "formele_regel": "betalingstermijn = 30 dagen na dagtekening aanslag",
        "toelichting": "Standaard betalingstermijn.",
        "invoer": [],
        "uitvoer": ["BWBR0004770/art9/lid1/betalingstermijn"],
        "operators": [],
        "voorbeeldreeksen": [],
        "tussenresultaat": False,
        "bwb_id": "BWBR0004770",
        "artikel": "9",
        "lid": "1",
        "peildatum": "2026-01-01",
        "annotatie_id": "BWBR0004770/art9/lid1",
        "rechtsfeit_id": "",
        "vervangt_regel_id": "",
        "gespecialiseerd_regel_id": "",
        "geldigheid_van": "2026-01-01",
        "geldigheid_tot": "",
        "prioriteit": None,
    }
    base.update(overrides)
    return base


# ===== lijstpagina =====

def test_gen_regels_maakt_regels_html(tmp_path):
    gen_regels(tmp_path, [], [], [])
    assert (tmp_path / "regels.html").exists()


def test_gen_regels_lijst_toont_naam(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [])
    content = (tmp_path / "regels.html").read_text()
    assert "Berekening betalingstermijn" in content


def test_gen_regels_lijst_toont_geldigheid_van(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [])
    content = (tmp_path / "regels.html").read_text()
    assert "Geldig vanaf" in content
    assert "2026-01-01" in content


def test_gen_regels_lijst_toont_soort_badge(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [])
    content = (tmp_path / "regels.html").read_text()
    assert "Rekenregel" in content


# ===== detailpagina =====

def test_gen_regels_detail_maakt_bestand(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [])
    assert (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").exists()


def test_gen_regels_detail_toont_formele_regel(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "betalingstermijn = 30 dagen" in content


def test_gen_regels_detail_toont_annotatie_id(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "Annotatie-id" in content
    assert "BWBR0004770/art9/lid1" in content


def test_gen_regels_detail_geen_annotatie_id_geen_rij(tmp_path):
    gen_regels(tmp_path, [_regel(annotatie_id="")], [], [])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "Annotatie-id" not in content


def test_gen_regels_detail_toont_geldig_vanaf(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "Geldig vanaf" in content
    assert "2026-01-01" in content


def test_gen_regels_detail_tussenresultaat_ja(tmp_path):
    gen_regels(tmp_path, [_regel(tussenresultaat=True)], [], [])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "Ja" in content


def test_gen_regels_detail_tussenresultaat_nee(tmp_path):
    gen_regels(tmp_path, [_regel(tussenresultaat=False)], [], [])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "Nee" in content


def test_gen_regels_detail_gespecialiseerd_regel_id_toont_link(tmp_path):
    gen_regels(tmp_path, [_regel(gespecialiseerd_regel_id="AR-HOOFD-001")], [], [])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "AR-HOOFD-001" in content


def test_gen_regels_detail_waarschuwingen_kaart_zichtbaar(tmp_path):
    ws = {"regels/AR-BWBR0004770-art9-lid1-a.yaml": ["[L3] soort is 'Specialisatieregel' maar gespecialiseerd-regel-id ontbreekt"]}
    gen_regels(tmp_path, [_regel()], [], [], waarschuwingen=ws)
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "Kwaliteitspunten" in content
    assert "gespecialiseerd-regel-id" in content


def test_gen_regels_detail_geen_waarschuwingen_geen_kaart(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [], waarschuwingen={})
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "Kwaliteitspunten" not in content


def test_gen_regels_detail_waarschuwingen_toont_oplossing_als_meta(tmp_path):
    ws = {"regels/AR-BWBR0004770-art9-lid1-a.yaml": ["[L3] soort is 'Specialisatieregel' maar prioriteit is niet ingevuld — stel prioriteit in"]}
    meta = [{"sleutel": "soort is 'Specialisatieregel' maar prioriteit is niet ingevuld", "titel": "Prioriteit ontbreekt", "uitleg": "U.", "stappen": ["Stap R"]}]
    gen_regels(tmp_path, [_regel()], [], [], waarschuwingen=ws, meta=meta)
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "oplossing-blok" in content
    assert "Prioriteit ontbreekt" in content
    assert "Stap R" in content


# ===== VR-matrix rendering =====

def _vr(ar_id="AR-BWBR0004770-art9-lid1-a", **overrides) -> dict:
    base = {
        "id": f"VR-{ar_id[3:]}",
        "naam": "Test voorbeeldreeks",
        "afleidingsregel_id": ar_id,
        "status": "concept",
        "peildatum": "2026-01-01",
        "aangemaakt_op": "2026-01-01",
        "kolommen": [
            {
                "label": "Happy path",
                "invoer": {"b/invoer": "ja"},
                "is_invoer_juist": "ja",
                "verwachte_uitvoer": {"b/uitvoer": "ja"},
                "is_voorspelling_juist": "?",
                "toelichting": "",
            },
            {
                "label": "Negatief geval",
                "invoer": {"b/invoer": "nee"},
                "is_invoer_juist": "ja",
                "verwachte_uitvoer": {"b/uitvoer": "nee"},
                "is_voorspelling_juist": "ja",
                "toelichting": "Grensgeval toelichting",
            },
        ],
    }
    base.update(overrides)
    return base


def test_gen_regels_toont_vr_matrix(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [], voorbeeldreeksen=[_vr()])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "vr-matrix" in content
    assert "Happy path" in content


def test_gen_regels_vr_matrix_toont_invoer_sectie(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [], voorbeeldreeksen=[_vr()])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "Invoer" in content
    assert "invoer" in content


def test_gen_regels_vr_matrix_toont_uitvoer_sectie(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [], voorbeeldreeksen=[_vr()])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "Uitvoer" in content


def test_gen_regels_vr_matrix_toont_meta_rijen(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [], voorbeeldreeksen=[_vr()])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "Invoer juist?" in content
    assert "Voorspelling juist?" in content


def test_gen_regels_vr_matrix_toont_vraag_klasse(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [], voorbeeldreeksen=[_vr()])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "vr-vraag" in content


def test_gen_regels_vr_matrix_toont_ja_klasse(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [], voorbeeldreeksen=[_vr()])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "vr-ja" in content


def test_gen_regels_vr_matrix_toont_toelichting(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [], voorbeeldreeksen=[_vr()])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "Grensgeval toelichting" in content


def test_gen_regels_vr_matrix_toont_status_badge(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [], voorbeeldreeksen=[_vr()])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "concept" in content


def test_gen_regels_vr_matrix_gevalideerd_badge(tmp_path):
    gen_regels(tmp_path, [_regel()], [], [], voorbeeldreeksen=[_vr(status="gevalideerd")])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "badge-definitief" in content


def test_gen_regels_vr_matrix_link_naar_begrip(tmp_path):
    begrippen = [{"id": "b/invoer", "slug": "invoer-slug"}]
    gen_regels(tmp_path, [_regel()], begrippen, [], voorbeeldreeksen=[_vr()])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "invoer-slug.html" in content


def test_gen_regels_vr_matrix_null_waarde_toont_null_cel(tmp_path):
    vr = _vr()
    vr["kolommen"][0]["invoer"]["b/invoer"] = None
    gen_regels(tmp_path, [_regel()], [], [], voorbeeldreeksen=[vr])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "vr-nvt" in content


def test_gen_regels_vr_matrix_lege_kolommen_geeft_leeg(tmp_path):
    vr = _vr(kolommen=[])
    gen_regels(tmp_path, [_regel()], [], [], voorbeeldreeksen=[vr])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "vr-matrix" not in content


def test_gen_regels_vr_andere_regel_niet_in_html(tmp_path):
    vr = _vr(ar_id="AR-9999")
    gen_regels(tmp_path, [_regel()], [], [], voorbeeldreeksen=[vr])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "vr-matrix" not in content


def test_gen_regels_inline_voorbeelden_als_fallback(tmp_path):
    r = _regel(voorbeeldreeksen=[{
        "invoerwaarden": "x=1",
        "verwachte-uitkomst": "y=2",
        "juridisch-juist": True,
    }])
    gen_regels(tmp_path, [r], [], [], voorbeeldreeksen=[])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "voorbeeld" in content
    assert "x=1" in content


def test_gen_regels_vr_vervangt_inline_als_aanwezig(tmp_path):
    r = _regel(voorbeeldreeksen=[{
        "invoerwaarden": "x=1",
        "verwachte-uitkomst": "y=2",
        "juridisch-juist": False,
    }])
    gen_regels(tmp_path, [r], [], [], voorbeeldreeksen=[_vr()])
    content = (tmp_path / "regels" / "AR-BWBR0004770-art9-lid1-a.html").read_text()
    assert "vr-matrix" in content
    assert "x=1" not in content
