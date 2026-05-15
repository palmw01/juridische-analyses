"""Smoke tests voor sitegen page generators — verifieert dat bestanden aangemaakt worden."""
import json
from pathlib import Path

import pytest

from sitegen.pages.index import gen_index, gen_404
from sitegen.pages.search import gen_search
from sitegen.pages.sparql import gen_sparql
from sitegen.pages.regels import gen_regels
from sitegen.pages.artikel_indices import gen_artikel_indices
from sitegen.pages.begrippen import gen_begrippen
from sitegen.pages.annotaties import gen_annotaties


# ---------------------------------------------------------------------------
# Minimale fixture-factories voor sitegen dataformaat (output van laad_*())
# ---------------------------------------------------------------------------

def begrip(
    begrip_id="BWBR0004770/art9/lid1/belastingschuldige",
    naam="belastingschuldige",
    slug="belastingschuldige",
    **overrides,
) -> dict:
    base = {
        "id": begrip_id,
        "naam": naam,
        "slug": slug,
        "definitie": "de persoon die de belasting verschuldigd is",
        "definitie_contexten": [],
        "definitie_versie": 1,
        "definitie_gebaseerd_op": ["m-001"],
        "soort": "entiteit",
        "soort_id": False,
        "herkomst": "direct",
        "status": "concept",
        "aliases": [],
        "relaties": {"is-een": [], "heeft": [], "leidt-tot": []},
        "afleidingsregel-id": None,
        "uitvoer-van-regel-id": None,
        "tussenresultaat": False,
        "identificatiebegrip": False,
        "jas_klasse": "rechtssubject",
        "toelichting_klasse": "",
        "markeringen": [],
        "geldigheid_van": "2024-01-01",
        "geldigheid_tot": "",
        "vervangen_door": "",
        "voorbeelden": [],
        "kenmerken": [],
    }
    base.update(overrides)
    return base


def annotatie(
    ann_id="BWBR0004770/art9/lid1",
    **overrides,
) -> dict:
    base = {
        "id": ann_id,
        "bwb_id": "BWBR0004770",
        "wet": "Invorderingswet 1990",
        "artikel": "9",
        "lid": "1",
        "peildatum": "2024-01-01",
        "structuurpositie": "Hoofdstuk 1 > Artikel 9",
        "wetstekst": "De belastingaanslag moet worden betaald binnen dertig dagen.",
        "rijen": [
            {
                "rij_id": "r1",
                "markering": "belastingschuldige",
                "jas_klasse": "rechtssubject",
                "interpretatiemethode": "grammaticaal",
                "begrip_id": "BWBR0004770/art9/lid1/belastingschuldige",
                "toelichting_klasse": "",
                "signalering": None,
            }
        ],
        "diagram": {
            "knopen": [{"id": "k1", "label": "belastingschuldige", "jas-klasse": "rechtssubject"}],
            "kanten": [],
        },
        "kruisreferenties": [],
        "delegatiestructuur": [],
    }
    base.update(overrides)
    return base


def regel(
    regel_id="AR-0001",
    naam="Berekening betalingstermijn",
    **overrides,
) -> dict:
    base = {
        "id": regel_id,
        "naam": naam,
        "soort": "Rekenregel",
        "formele_regel": "betalingstermijn = 30 dagen na dagtekening aanslag",
        "toelichting": "Standaard betalingstermijn conform art. 9 IW 1990.",
        "invoer": [],
        "uitvoer": ["BWBR0004770/art9/lid1/betalingstermijn"],
        "operators": [],
        "voorbeeldreeksen": [
            {"invoerwaarden": "dagtekening=2024-01-01", "verwachte-uitkomst": "betalingstermijn=2024-01-31", "juridisch-juist": True},
            {"invoerwaarden": "dagtekening=2024-01-01", "verwachte-uitkomst": "betalingstermijn=2024-01-15", "juridisch-juist": False, "toelichting": "Grensgeval"},
        ],
        "tussenresultaat": False,
        "bwb_id": "BWBR0004770",
        "artikel": "9",
        "lid": "1",
        "peildatum": "2024-01-01",
        "rechtsfeit_id": "",
        "vervangt_regel_id": "",
        "geldigheid_van": "2024-01-01",
        "geldigheid_tot": "",
        "prioriteit": None,
    }
    base.update(overrides)
    return base


def artikel_index(**overrides) -> dict:
    base = {
        "id": "BWBR0004770/art9",
        "bwb_id": "BWBR0004770",
        "wet": "Invorderingswet 1990",
        "artikel": "9",
        "peildatum": "2024-01-01",
        "structuurpositie": "Hoofdstuk 1 > Artikel 9",
        "leden_annotaties": ["BWBR0004770/art9/lid1"],
        "kruisreferenties": [],
        "delegatiestructuur": [],
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# gen_index
# ---------------------------------------------------------------------------

def test_gen_index_maakt_bestand_aan(tmp_path):
    gen_index(tmp_path, [begrip()], [annotatie()], [regel()])
    assert (tmp_path / "index.html").exists()


def test_gen_index_bevat_tellingen(tmp_path):
    begrippen = [begrip(), begrip(begrip_id="test/b2", naam="b2", slug="b2")]
    gen_index(tmp_path, begrippen, [], [])
    content = (tmp_path / "index.html").read_text()
    assert "2" in content


def test_gen_index_leeg_project(tmp_path):
    gen_index(tmp_path, [], [], [])
    assert (tmp_path / "index.html").exists()


def test_gen_404_maakt_bestand_aan(tmp_path):
    gen_404(tmp_path)
    assert (tmp_path / "404.html").exists()


def test_gen_404_bevat_404_tekst(tmp_path):
    gen_404(tmp_path)
    assert "404" in (tmp_path / "404.html").read_text()


# ---------------------------------------------------------------------------
# gen_search
# ---------------------------------------------------------------------------

def test_gen_search_maakt_bestand_aan(tmp_path):
    gen_search(tmp_path, [begrip()], [annotatie()], [regel()])
    assert (tmp_path / "search.html").exists()


def test_gen_search_bevat_minisearch(tmp_path):
    gen_search(tmp_path, [], [], [])
    content = (tmp_path / "search.html").read_text()
    assert "MiniSearch" in content or "minisearch" in content.lower()


# ---------------------------------------------------------------------------
# gen_sparql
# ---------------------------------------------------------------------------

def test_gen_sparql_maakt_bestand_aan(tmp_path):
    gen_sparql(tmp_path)
    assert (tmp_path / "sparql.html").exists()


def test_gen_sparql_bevat_sparql_content(tmp_path):
    gen_sparql(tmp_path)
    content = (tmp_path / "sparql.html").read_text()
    assert "SPARQL" in content
    assert "SELECT" in content


# ---------------------------------------------------------------------------
# gen_regels
# ---------------------------------------------------------------------------

def test_gen_regels_maakt_lijstpagina_aan(tmp_path):
    gen_regels(tmp_path, [regel()], [begrip()], [annotatie()])
    assert (tmp_path / "regels.html").exists()


def test_gen_regels_maakt_detailpagina_aan(tmp_path):
    gen_regels(tmp_path, [regel()], [], [])
    assert (tmp_path / "regels" / "AR-0001.html").exists()


def test_gen_regels_leeg_geen_fout(tmp_path):
    gen_regels(tmp_path, [], [], [])
    assert (tmp_path / "regels.html").exists()


def test_gen_regels_detailpagina_bevat_naam(tmp_path):
    gen_regels(tmp_path, [regel()], [], [])
    content = (tmp_path / "regels" / "AR-0001.html").read_text()
    assert "Berekening betalingstermijn" in content


def test_gen_regels_met_annotatie_link(tmp_path):
    gen_regels(tmp_path, [regel()], [begrip()], [annotatie()])
    content = (tmp_path / "regels" / "AR-0001.html").read_text()
    assert "Annotatie" in content or "annotatie" in content.lower()


def test_gen_regels_met_prioriteit(tmp_path):
    gen_regels(tmp_path, [regel(prioriteit=1, soort="Specialisatieregel")], [], [])
    content = (tmp_path / "regels" / "AR-0001.html").read_text()
    assert "Prioriteit" in content or "prioriteit" in content.lower()


def test_gen_regels_met_geldigheid_tot(tmp_path):
    gen_regels(tmp_path, [regel(**{"geldigheid_tot": "2025-12-31"})], [], [])
    content = (tmp_path / "regels" / "AR-0001.html").read_text()
    assert "2025-12-31" in content


def test_gen_regels_met_vervangt(tmp_path):
    gen_regels(tmp_path, [regel(**{"vervangt_regel_id": "AR-0000"})], [], [])
    content = (tmp_path / "regels" / "AR-0001.html").read_text()
    assert "AR-0000" in content


def test_gen_regels_voorbeeld_ongeldig_heeft_label(tmp_path):
    gen_regels(tmp_path, [regel()], [], [])
    content = (tmp_path / "regels" / "AR-0001.html").read_text()
    assert "[-]" in content


# ---------------------------------------------------------------------------
# gen_artikel_indices
# ---------------------------------------------------------------------------

def test_gen_artikel_indices_maakt_pagina_aan(tmp_path):
    gen_artikel_indices(tmp_path, [artikel_index()], [annotatie()])
    pad = tmp_path / "annotaties" / "BWBR0004770-art9.html"
    assert pad.exists()


def test_gen_artikel_indices_leeg_geen_fout(tmp_path):
    gen_artikel_indices(tmp_path, [], [])


def test_gen_artikel_indices_lid_niet_gevonden(tmp_path):
    idx = artikel_index(leden_annotaties=["bestaat/niet"])
    gen_artikel_indices(tmp_path, [idx], [])
    pad = tmp_path / "annotaties" / "BWBR0004770-art9.html"
    assert pad.exists()


def test_gen_artikel_indices_met_kruisrefs(tmp_path):
    idx = artikel_index(kruisreferenties=["BWBR0002656/art1"])
    gen_artikel_indices(tmp_path, [idx], [])
    content = (tmp_path / "annotaties" / "BWBR0004770-art9.html").read_text()
    assert "Kruisreferenties" in content


def test_gen_artikel_indices_met_delegatie(tmp_path):
    idx = artikel_index(delegatiestructuur=[{
        "omschrijving": "Nadere regels",
        "vindplaats": "art. 10",
        "type": "AMvB",
        "invulling": "Uitvoeringsbesluit",
        "vindplaats-invulling": "art. 5",
    }])
    gen_artikel_indices(tmp_path, [idx], [])
    content = (tmp_path / "annotaties" / "BWBR0004770-art9.html").read_text()
    assert "Delegatiestructuur" in content


# ---------------------------------------------------------------------------
# gen_begrippen
# ---------------------------------------------------------------------------

def test_gen_begrippen_maakt_lijstpagina_aan(tmp_path):
    gen_begrippen(tmp_path, [begrip()], [annotatie()])
    assert (tmp_path / "begrippen.html").exists()


def test_gen_begrippen_maakt_detailpagina_aan(tmp_path):
    gen_begrippen(tmp_path, [begrip()], [])
    assert (tmp_path / "begrippen" / "belastingschuldige.html").exists()


def test_gen_begrippen_leeg_geen_fout(tmp_path):
    gen_begrippen(tmp_path, [], [])
    assert (tmp_path / "begrippen.html").exists()


def test_gen_begrippen_detailpagina_bevat_naam(tmp_path):
    gen_begrippen(tmp_path, [begrip()], [])
    content = (tmp_path / "begrippen" / "belastingschuldige.html").read_text()
    assert "belastingschuldige" in content


def test_gen_begrippen_met_relaties(tmp_path):
    b1 = begrip()
    b2 = begrip(begrip_id="test/persoon", naam="persoon", slug="persoon")
    b1["relaties"]["is-een"] = ["test/persoon"]
    gen_begrippen(tmp_path, [b1, b2], [])
    content = (tmp_path / "begrippen" / "belastingschuldige.html").read_text()
    assert "Is een" in content or "is-een" in content.lower()


def test_gen_begrippen_met_markeringen(tmp_path):
    b = begrip(markeringen=[{
        "markering-id": "m-001",
        "bijdrage": "primair",
        "bron-annotatie-id": "BWBR0004770/art9/lid1",
        "tekst": "de persoon die de belasting verschuldigd is",
        "interpretatiemethode": "grammaticaal",
        "bevestigd": True,
        "bevestigd-op": "2024-01-01",
    }])
    gen_begrippen(tmp_path, [b], [annotatie()])
    content = (tmp_path / "begrippen" / "belastingschuldige.html").read_text()
    assert "m-001" in content


def test_gen_begrippen_met_voorbeelden(tmp_path):
    b = begrip(voorbeelden=[{"stelling": "Testcase", "waar": True, "toelichting": ""}])
    gen_begrippen(tmp_path, [b], [])
    content = (tmp_path / "begrippen" / "belastingschuldige.html").read_text()
    assert "Voorbeelden" in content


def test_gen_begrippen_met_kenmerken(tmp_path):
    b = begrip(kenmerken=["Kenmerk A", "Kenmerk B"])
    gen_begrippen(tmp_path, [b], [])
    content = (tmp_path / "begrippen" / "belastingschuldige.html").read_text()
    assert "Kenmerken" in content


def test_gen_begrippen_met_definitie_contexten(tmp_path):
    b = begrip(definitie_contexten=[{
        "markering-id": "m-001",
        "bijdrage": "aanvullend",
        "tekst": "context tekst",
        "toelichting": "extra toelichting",
    }])
    gen_begrippen(tmp_path, [b], [])
    content = (tmp_path / "begrippen" / "belastingschuldige.html").read_text()
    assert "context tekst" in content


def test_gen_begrippen_met_annotatie_koppeling(tmp_path):
    b = begrip()
    a = annotatie()
    gen_begrippen(tmp_path, [b], [a])
    content = (tmp_path / "begrippen" / "belastingschuldige.html").read_text()
    assert "Annotaties" in content or "annotatie" in content.lower()


# ---------------------------------------------------------------------------
# gen_annotaties
# ---------------------------------------------------------------------------

def test_gen_annotaties_maakt_lijstpagina_aan(tmp_path):
    gen_annotaties(tmp_path, [annotatie()], [regel()], [begrip()])
    assert (tmp_path / "annotaties.html").exists()


def test_gen_annotaties_maakt_detailpagina_aan(tmp_path):
    gen_annotaties(tmp_path, [annotatie()], [], [])
    assert (tmp_path / "annotaties" / "BWBR0004770-art9-lid1.html").exists()


def test_gen_annotaties_leeg_geen_fout(tmp_path):
    gen_annotaties(tmp_path, [], [], [])
    assert (tmp_path / "annotaties.html").exists()


def test_gen_annotaties_detailpagina_bevat_wetstekst(tmp_path):
    gen_annotaties(tmp_path, [annotatie()], [], [])
    content = (tmp_path / "annotaties" / "BWBR0004770-art9-lid1.html").read_text()
    assert "belastingaanslag" in content


def test_gen_annotaties_met_diagram(tmp_path):
    gen_annotaties(tmp_path, [annotatie()], [], [])
    content = (tmp_path / "annotaties" / "BWBR0004770-art9-lid1.html").read_text()
    assert "mermaid" in content.lower() or "Diagram" in content


def test_gen_annotaties_met_kruisrefs(tmp_path):
    a = annotatie(kruisreferenties=[{
        "doel_bwb_id": "BWBR0002656",
        "doel_artikel": "1",
        "doel_lid": "",
        "richting": "forward",
        "confidence": 0.9,
        "ruwe_tekst": "artikel 1 AWR",
    }])
    gen_annotaties(tmp_path, [a], [], [])
    content = (tmp_path / "annotaties" / "BWBR0004770-art9-lid1.html").read_text()
    assert "Kruisreferenties" in content or "BWBR0002656" in content


def test_gen_annotaties_met_delegatiestructuur(tmp_path):
    a = annotatie(delegatiestructuur=[{
        "omschrijving": "Nadere regels",
        "vindplaats": "art. 10",
        "type": "AMvB",
        "invulling": None,
        "vindplaats-invulling": None,
    }])
    gen_annotaties(tmp_path, [a], [], [])
    content = (tmp_path / "annotaties" / "BWBR0004770-art9-lid1.html").read_text()
    assert "Delegatiestructuur" in content


def test_gen_annotaties_leidraad_format(tmp_path):
    a = annotatie(ann_id="LI/sectie1", wet="LI Leidraad", artikel="1", lid="")
    gen_annotaties(tmp_path, [a], [], [])
    assert (tmp_path / "annotaties" / "LI-sectie1.html").exists()


def test_gen_begrippen_ongeldige_markering_geen_crash(tmp_path):
    b = begrip(markeringen=[{
        "markering-id": "m-001",
        "bijdrage": "primair",
        "bron-annotatie-id": "",
        "tekst": "de persoon",
        "interpretatiemethode": "grammaticaal",
        "bevestigd": False,
    }])
    gen_begrippen(tmp_path, [b], [])
    assert (tmp_path / "begrippen" / "belastingschuldige.html").exists()


def test_gen_begrippen_voorbeeld_met_toelichting(tmp_path):
    b = begrip(voorbeelden=[{"stelling": "Test", "waar": True, "toelichting": "Extra uitleg hier"}])
    gen_begrippen(tmp_path, [b], [])
    content = (tmp_path / "begrippen" / "belastingschuldige.html").read_text()
    assert "Extra uitleg hier" in content


def test_gen_begrippen_met_afleidingsregel_id(tmp_path):
    b = begrip(**{"afleidingsregel-id": "AR-0001"})
    gen_begrippen(tmp_path, [b], [])
    content = (tmp_path / "begrippen" / "belastingschuldige.html").read_text()
    assert "AR-0001" in content


def test_gen_begrippen_met_uitvoer_van_regel_id(tmp_path):
    b = begrip(**{"uitvoer-van-regel-id": "AR-0002"})
    gen_begrippen(tmp_path, [b], [])
    content = (tmp_path / "begrippen" / "belastingschuldige.html").read_text()
    assert "AR-0002" in content


def test_gen_begrippen_waarschuwingen_kaart_zichtbaar(tmp_path):
    b = begrip()
    ws = {"begrippen/belastingschuldige.yaml": ["[L3] Relaties leeg — overweeg is-een"]}
    gen_begrippen(tmp_path, [b], [], waarschuwingen=ws)
    content = (tmp_path / "begrippen" / "belastingschuldige.html").read_text()
    assert "Kwaliteitspunten" in content
    assert "Relaties leeg" in content


def test_gen_begrippen_geen_waarschuwingen_geen_kaart(tmp_path):
    b = begrip()
    gen_begrippen(tmp_path, [b], [], waarschuwingen={})
    content = (tmp_path / "begrippen" / "belastingschuldige.html").read_text()
    assert "Kwaliteitspunten" not in content


def test_gen_begrippen_definitie_context_met_bron_annotatie(tmp_path):
    b = begrip(
        markeringen=[{
            "markering-id": "m-001",
            "bijdrage": "aanvullend",
            "bron-annotatie-id": "BWBR0004770/art9/lid1",
            "tekst": "de persoon",
            "interpretatiemethode": "grammaticaal",
            "bevestigd": False,
        }],
        definitie_contexten=[{
            "markering-id": "m-001",
            "bijdrage": "aanvullend",
            "tekst": "context tekst hier",
            "toelichting": "",
        }],
    )
    gen_begrippen(tmp_path, [b], [annotatie()])
    content = (tmp_path / "begrippen" / "belastingschuldige.html").read_text()
    assert "context tekst hier" in content


# ---------------------------------------------------------------------------
# gen_artikel_indices — missing line 23
# ---------------------------------------------------------------------------

def test_gen_artikel_indices_lege_leden_annotaties(tmp_path):
    idx = artikel_index(leden_annotaties=[])
    gen_artikel_indices(tmp_path, [idx], [])
    content = (tmp_path / "annotaties" / "BWBR0004770-art9.html").read_text()
    assert "Geen lid-annotaties gevonden" in content


# ---------------------------------------------------------------------------
# gen_annotaties — missing lines 22, 63-64, 81-92, 111-113, 115, 124, 140-142
# ---------------------------------------------------------------------------

def test_gen_annotaties_rij_met_signalering(tmp_path):
    a = annotatie(rijen=[{
        "rij_id": "r1",
        "markering": "belastingschuldige",
        "jas_klasse": "rechtssubject",
        "interpretatiemethode": "grammaticaal",
        "begrip_id": "BWBR0004770/art9/lid1/belastingschuldige",
        "toelichting_klasse": "",
        "signalering": "Let op: bijzonder geval",
    }])
    gen_annotaties(tmp_path, [a], [], [])
    content = (tmp_path / "annotaties" / "BWBR0004770-art9-lid1.html").read_text()
    assert "has-sign" in content


def test_gen_annotaties_rij_met_toelichting_klasse(tmp_path):
    a = annotatie(rijen=[{
        "rij_id": "r1",
        "markering": "belastingschuldige",
        "jas_klasse": "rechtssubject",
        "interpretatiemethode": "grammaticaal",
        "begrip_id": None,
        "toelichting_klasse": "Toelichting op klasse",
        "signalering": None,
    }])
    gen_annotaties(tmp_path, [a], [], [])
    content = (tmp_path / "annotaties" / "BWBR0004770-art9-lid1.html").read_text()
    assert "sign-detail" in content


def test_gen_annotaties_met_regel_via_invoer(tmp_path):
    bid = "BWBR0004770/art9/lid1/belastingschuldige"
    r = regel(invoer=[bid])
    a = annotatie()  # rij heeft begrip_id = bid
    b = begrip()
    gen_annotaties(tmp_path, [a], [r], [b])
    content = (tmp_path / "annotaties" / "BWBR0004770-art9-lid1.html").read_text()
    assert "Afleidingsregels" in content


def test_gen_annotaties_kruisref_met_doel_lid(tmp_path):
    a = annotatie(kruisreferenties=[{
        "doel_bwb_id": "BWBR0002656",
        "doel_artikel": "1",
        "doel_lid": "2",
        "richting": "forward",
        "confidence": 0.9,
        "ruwe_tekst": "artikel 1 lid 2 AWR",
    }])
    gen_annotaties(tmp_path, [a], [], [])
    content = (tmp_path / "annotaties" / "BWBR0004770-art9-lid1.html").read_text()
    assert "lid 2" in content


def test_gen_annotaties_met_parent_link(tmp_path):
    a = annotatie()
    idx = artikel_index(leden_annotaties=["BWBR0004770/art9/lid1"])
    gen_annotaties(tmp_path, [a], [], [], indices=[idx])
    content = (tmp_path / "annotaties" / "BWBR0004770-art9-lid1.html").read_text()
    assert "Deel van artikel" in content


def test_gen_annotaties_indices_op_lijstpagina(tmp_path):
    idx = artikel_index()
    gen_annotaties(tmp_path, [], [], [], indices=[idx])
    content = (tmp_path / "annotaties.html").read_text()
    assert "artikeloverzicht" in content
