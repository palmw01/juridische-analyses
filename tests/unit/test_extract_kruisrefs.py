"""Tests voor tools/extract_kruisrefs.py — URI-parser, lid-extractie, fase1/2, deduplicatie, CLI."""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from extract_kruisrefs import (
    parse_jci_uri,
    extract_lids_from_display,
    extract_artikelnrs_from_display,
    _zin_van,
    _zoek_wet_in_zin,
    _maak_record,
    fase1,
    fase2,
    dedupliceer,
    verwerk_lid,
    main,
    BWB_MAPPING,
    WET_NAAR_BWB,
    RE_JCI_LINK,
)


# ===== parse_jci_uri =====

def test_parse_jci_uri_met_artikel():
    result = parse_jci_uri("jci1.3:c:BWBR0004770&artikel=9")
    assert result["bwb_id"] == "BWBR0004770"
    assert result["artikel"] == "9"


def test_parse_jci_uri_zonder_artikel():
    result = parse_jci_uri("jci1.3:c:BWBR0004770")
    assert result["bwb_id"] == "BWBR0004770"
    assert result["artikel"] is None


def test_parse_jci_uri_met_meerdere_params():
    result = parse_jci_uri("jci1.3:c:BWBR0004770&hoofdstuk=2&artikel=15a")
    assert result["bwb_id"] == "BWBR0004770"
    assert result["artikel"] == "15a"


def test_parse_jci_uri_artikel_met_letter():
    result = parse_jci_uri("jci1.3:c:BWBR0002226&artikel=25a")
    assert result["bwb_id"] == "BWBR0002226"
    assert result["artikel"] == "25a"


def test_parse_jci_uri_negeert_hoofdstuk():
    result = parse_jci_uri("jci1.3:c:BWBR0004770&hoofdstuk=1")
    assert result["artikel"] is None


def test_parse_jci_uri_negeert_afdeling():
    result = parse_jci_uri("jci1.3:c:BWBR0004770&afdeling=2")
    assert result["artikel"] is None


def test_parse_jci_uri_uri_zonder_c_prefix():
    """Wanneer geen 'c:' in de URI, gebruikt alles als bwb_id."""
    result = parse_jci_uri("BWBR0004770&artikel=9")
    assert result["artikel"] == "9"


def test_parse_jci_uri_bwb_id_stripped():
    """Spaties rondom bwb_id worden gestript."""
    result = parse_jci_uri("jci1.3:c: BWBR0004770 &artikel=9")
    assert result["bwb_id"] == "BWBR0004770"


# ===== extract_lids_from_display =====

def test_extract_lids_geen_lid():
    assert extract_lids_from_display("artikel 9") == [None]


def test_extract_lids_lid_getal():
    result = extract_lids_from_display("lid 3")
    assert result == ["3"]


def test_extract_lids_rangnam_enkelvoud():
    result = extract_lids_from_display("derde lid")
    assert result == ["3"]


def test_extract_lids_rangnam_meerdere():
    result = extract_lids_from_display("derde lid en vijfde lid")
    assert result == ["3", "5"]


def test_extract_lids_reeks_en():
    result = extract_lids_from_display("leden 2 en 5")
    assert result == ["2", "3", "4", "5"]


def test_extract_lids_reeks_tot_en_met():
    result = extract_lids_from_display("leden 1 tot en met 3")
    assert result == ["1", "2", "3"]


def test_extract_lids_eerste_lid():
    result = extract_lids_from_display("eerste lid")
    assert result == ["1"]


def test_extract_lids_twintigste_lid():
    result = extract_lids_from_display("twintigste lid")
    assert result == ["20"]


def test_extract_lids_lid_getal_heeft_prioriteit_na_rangnam():
    """rangnam-patroon heeft prioriteit boven getal-patroon."""
    result = extract_lids_from_display("het vijfde lid, lid 3")
    # rangnam-match ['vijfde'] gevonden eerste
    assert "5" in result


# ===== extract_artikelnrs_from_display =====

def test_extract_artikelnrs_enkelvoud_default():
    result = extract_artikelnrs_from_display("artikel 9", "9")
    assert result == ["9"]


def test_extract_artikelnrs_meervoud():
    result = extract_artikelnrs_from_display("artikelen 9 en 10", None)
    assert "9" in result
    assert "10" in result


def test_extract_artikelnrs_meervoud_komma():
    result = extract_artikelnrs_from_display("artikelen 1, 2 en 3", None)
    assert "1" in result
    assert "2" in result
    assert "3" in result


def test_extract_artikelnrs_geen_default_geen_match():
    result = extract_artikelnrs_from_display("artikel 9", None)
    assert result == []


def test_extract_artikelnrs_met_letter():
    result = extract_artikelnrs_from_display("artikelen 9a en 10b", None)
    assert "9a" in result
    assert "10b" in result


def test_extract_artikelnrs_default_artikel_gebruikt():
    result = extract_artikelnrs_from_display("het eerste lid", "25")
    assert result == ["25"]


# ===== _zin_van =====

def test_zin_van_enkelvoudige_zin():
    tekst = "Artikel 9 is van toepassing."
    zin = _zin_van(tekst, 0, len(tekst) - 1)
    assert "Artikel 9" in zin


def test_zin_van_midden_van_tekst():
    tekst = "Eerste zin. Artikel 9 geldt hier. Derde zin."
    start = tekst.index("Artikel 9")
    einde = start + len("Artikel 9")
    zin = _zin_van(tekst, start, einde)
    assert "Artikel 9" in zin
    assert "Eerste zin" not in zin
    assert "Derde zin" not in zin


def test_zin_van_begin_van_tekst():
    tekst = "Artikel 9 is het begin. Rest."
    zin = _zin_van(tekst, 0, 8)
    assert "Artikel" in zin


def test_zin_van_einde_van_tekst():
    tekst = "Begin. Artikel 9"
    start = tekst.index("Artikel")
    zin = _zin_van(tekst, start, len(tekst))
    assert "Artikel 9" in zin


def test_zin_van_newline_begrenzing():
    tekst = "Eerste zin\nArtikel 9 hier\nDerde zin"
    start = tekst.index("Artikel 9")
    einde = start + len("Artikel 9")
    zin = _zin_van(tekst, start, einde)
    assert "Eerste" not in zin
    assert "Derde" not in zin


# ===== _zoek_wet_in_zin =====

def test_zoek_wet_in_zin_awb():
    zin = "Dit volgt uit artikel 3 van de Awb."
    result = _zoek_wet_in_zin(zin)
    assert result == "BWBR0005537"


def test_zoek_wet_in_zin_iw_1990():
    zin = "Van de IW 1990 is artikel 9 van toepassing."
    result = _zoek_wet_in_zin(zin)
    assert result == "BWBR0004770"


def test_zoek_wet_in_zin_geen_wetnaam():
    zin = "Artikel 9 is van toepassing."
    result = _zoek_wet_in_zin(zin)
    assert result is None


def test_zoek_wet_in_zin_awr():
    zin = "Conform artikel 25 van de AWR wordt bezwaar gemaakt."
    result = _zoek_wet_in_zin(zin)
    assert result == "BWBR0002226"


def test_zoek_wet_in_zin_gedeeltelijke_match():
    """Gedeeltelijke naam-match retourneert BWB-id."""
    zin = "Artikel 9 van de IW 1990 bepaalt dit."
    result = _zoek_wet_in_zin(zin)
    assert result == "BWBR0004770"


# ===== _maak_record =====

def test_maak_record_forward_richting():
    r = _maak_record(
        bron_bwb_id="BWBR0004770",
        bron_artikel="9",
        bron_lid="1",
        doel_bwb_id="BWBR0002226",
        doel_wet="AWR",
        doel_artikel="25",
        doel_lid="3",
        ruwe_tekst="artikel 25 AWR",
        confidence=0.9,
    )
    assert r["richting"] == "forward"
    assert r["doel-wet"] == "AWR"
    assert r["confidence"] == 0.9


def test_maak_record_intern_richting():
    r = _maak_record(
        bron_bwb_id="BWBR0004770",
        bron_artikel="9",
        bron_lid="1",
        doel_bwb_id="BWBR0004770",
        doel_wet="IW 1990",
        doel_artikel="10",
        doel_lid=None,
        ruwe_tekst="artikel 10",
        confidence=0.7,
    )
    assert r["richting"] == "intern"


def test_maak_record_zelfverwijzing():
    r = _maak_record(
        bron_bwb_id="BWBR0004770",
        bron_artikel="9",
        bron_lid="1",
        doel_bwb_id="BWBR0004770",
        doel_wet="IW 1990",
        doel_artikel="9",
        doel_lid="1",
        ruwe_tekst="artikel 9",
        confidence=0.7,
    )
    assert r["ruwe-tekst"] == "zelfverwijzing"


def test_maak_record_bevat_alle_velden():
    r = _maak_record(
        bron_bwb_id="A",
        bron_artikel="1",
        bron_lid="2",
        doel_bwb_id="B",
        doel_wet="Wet B",
        doel_artikel="3",
        doel_lid="4",
        ruwe_tekst="tekst",
        confidence=1.0,
    )
    for veld in ["bron-bwb-id", "bron-artikel", "bron-lid", "doel-bwb-id", "doel-wet",
                 "doel-artikel", "doel-lid", "ruwe-tekst", "richting", "confidence"]:
        assert veld in r


# ===== fase1 =====

def test_fase1_jci_link_met_artikel():
    tekst = "[artikel 9 IW 1990](jci1.3:c:BWBR0004770&artikel=9)"
    records = fase1(tekst, "BWBR0004770", "10", "1")
    assert len(records) >= 1
    assert records[0]["doel-bwb-id"] == "BWBR0004770"
    assert records[0]["doel-artikel"] == "9"


def test_fase1_jci_link_confidence_1_met_artikel():
    tekst = "[artikel 9](jci1.3:c:BWBR0004770&artikel=9)"
    records = fase1(tekst, "BWBR0004770", "10", "")
    assert records[0]["confidence"] == 1.0


def test_fase1_jci_link_confidence_0_8_zonder_artikel():
    tekst = "[IW 1990](jci1.3:c:BWBR0004770)"
    records = fase1(tekst, "BWBR0002226", "25", "")
    assert len(records) >= 1
    assert records[0]["confidence"] == 0.8


def test_fase1_geen_jci_links():
    tekst = "Artikel 9 is van toepassing."
    records = fase1(tekst, "BWBR0004770", "9", "1")
    assert records == []


def test_fase1_wetnaam_uit_mapping():
    tekst = "[artikel 9](jci1.3:c:BWBR0004770&artikel=9)"
    records = fase1(tekst, "BWBR0002226", "25", "")
    assert records[0]["doel-wet"] == "IW 1990"


def test_fase1_met_lid_in_display():
    tekst = "[derde lid van artikel 9](jci1.3:c:BWBR0004770&artikel=9)"
    records = fase1(tekst, "BWBR0002226", "25", "")
    lids = [r["doel-lid"] for r in records]
    assert "3" in lids


def test_fase1_meerdere_links():
    tekst = (
        "[artikel 9](jci1.3:c:BWBR0004770&artikel=9) en "
        "[artikel 25](jci1.3:c:BWBR0002226&artikel=25)"
    )
    records = fase1(tekst, "BWBR0004770", "10", "")
    assert len(records) >= 2


def test_fase1_display_met_artikelen_meervoud():
    tekst = "[artikelen 9 en 10](jci1.3:c:BWBR0004770)"
    records = fase1(tekst, "BWBR0002226", "25", "")
    artikels = [r["doel-artikel"] for r in records]
    assert "9" in artikels
    assert "10" in artikels


# ===== fase2 =====

def test_fase2_plain_tekst_artikel():
    tekst = "Dit volgt uit artikel 9."
    records = fase2(tekst, [], "BWBR0004770", "10", "1")
    assert any(r["doel-artikel"] == "9" for r in records)


def test_fase2_met_wetnaam_confidence_0_9():
    tekst = "Zie artikel 25 van de Awb."
    records = fase2(tekst, [], "BWBR0004770", "9", "1")
    awb_records = [r for r in records if r["doel-bwb-id"] == "BWBR0005537"]
    assert len(awb_records) >= 1
    assert awb_records[0]["confidence"] == 0.9


def test_fase2_zonder_wetnaam_confidence_0_7():
    tekst = "Zoals in artikel 10 beschreven."
    records = fase2(tekst, [], "BWBR0004770", "9", "1")
    assert len(records) >= 1
    assert records[0]["confidence"] == 0.7


def test_fase2_negeert_jci_passages():
    """Tekst die al door fase1 is gevonden (jci_matches) wordt niet opnieuw verwerkt."""
    tekst = "[artikel 9](jci1.3:c:BWBR0004770&artikel=9)"
    jci_matches = list(RE_JCI_LINK.finditer(tekst))
    records = fase2(tekst, jci_matches, "BWBR0004770", "10", "")
    # Geen artikelreferenties buiten de JCI-match
    assert len(records) == 0


def test_fase2_meerdere_artikelen():
    tekst = "Artikel 9 en artikel 10 zijn van toepassing."
    records = fase2(tekst, [], "BWBR0004770", "11", "")
    artikels = [r["doel-artikel"] for r in records]
    assert "9" in artikels
    assert "10" in artikels


def test_fase2_lid_in_zin():
    tekst = "Artikel 9, tweede lid, is van toepassing."
    records = fase2(tekst, [], "BWBR0004770", "10", "")
    lid_records = [r for r in records if r["doel-artikel"] == "9"]
    lids = [r["doel-lid"] for r in lid_records]
    assert "2" in lids


def test_fase2_lege_tekst():
    records = fase2("", [], "BWBR0004770", "9", "")
    assert records == []


# ===== dedupliceer =====

def test_dedupliceer_unieke_records():
    records = [
        _maak_record(bron_bwb_id="A", bron_artikel="1", bron_lid="1",
                     doel_bwb_id="B", doel_wet="W", doel_artikel="2", doel_lid="1",
                     ruwe_tekst="t", confidence=1.0),
        _maak_record(bron_bwb_id="A", bron_artikel="1", bron_lid="1",
                     doel_bwb_id="C", doel_wet="W", doel_artikel="3", doel_lid="1",
                     ruwe_tekst="t", confidence=1.0),
    ]
    result = dedupliceer(records)
    assert len(result) == 2


def test_dedupliceer_duplicaten_verwijderd():
    r = _maak_record(bron_bwb_id="A", bron_artikel="1", bron_lid="1",
                     doel_bwb_id="B", doel_wet="W", doel_artikel="2", doel_lid="1",
                     ruwe_tekst="t", confidence=1.0)
    result = dedupliceer([r, r, r])
    assert len(result) == 1


def test_dedupliceer_lege_lijst():
    assert dedupliceer([]) == []


def test_dedupliceer_behoudt_volgorde():
    r1 = _maak_record(bron_bwb_id="A", bron_artikel="1", bron_lid="1",
                      doel_bwb_id="B", doel_wet="W", doel_artikel="2", doel_lid="1",
                      ruwe_tekst="eerste", confidence=1.0)
    r2 = _maak_record(bron_bwb_id="A", bron_artikel="1", bron_lid="1",
                      doel_bwb_id="C", doel_wet="W", doel_artikel="3", doel_lid=None,
                      ruwe_tekst="tweede", confidence=0.9)
    result = dedupliceer([r1, r2])
    assert result[0]["ruwe-tekst"] == "eerste"
    assert result[1]["ruwe-tekst"] == "tweede"


# ===== verwerk_lid =====

def test_verwerk_lid_combineert_fase1_en_fase2():
    lid_obj = {
        "lid": "1",
        "tekst": (
            "[artikel 9](jci1.3:c:BWBR0004770&artikel=9) "
            "en ook artikel 10 van de Awb."
        ),
    }
    records = verwerk_lid(lid_obj, "BWBR0004770", "11")
    doel_artikels = {r["doel-artikel"] for r in records}
    assert "9" in doel_artikels
    assert "10" in doel_artikels


def test_verwerk_lid_lege_tekst():
    lid_obj = {"lid": "1", "tekst": ""}
    records = verwerk_lid(lid_obj, "BWBR0004770", "9")
    assert records == []


def test_verwerk_lid_bron_lid_str():
    """bron_lid wordt als str(lid_obj["lid"]) verwerkt."""
    lid_obj = {"lid": 2, "tekst": "artikel 9"}
    records = verwerk_lid(lid_obj, "BWBR0004770", "10")
    if records:
        assert records[0]["bron-lid"] == "2"


def test_verwerk_lid_deduplicatie():
    """Dubbele references worden door dedupliceer gededupliceerd (main roept dat aan)."""
    tekst = (
        "[artikel 9](jci1.3:c:BWBR0004770&artikel=9) "
        "[artikel 9](jci1.3:c:BWBR0004770&artikel=9)"
    )
    lid_obj = {"lid": "1", "tekst": tekst}
    records = verwerk_lid(lid_obj, "BWBR0004770", "10")
    deduped = dedupliceer(records)
    count_9 = sum(1 for r in deduped if r["doel-artikel"] == "9" and r["doel-bwb-id"] == "BWBR0004770")
    assert count_9 == 1


# ===== main() =====

def test_main_bestand_niet_gevonden(tmp_path, capsys):
    with patch.object(sys, "argv", ["extract_kruisrefs.py", "--input", str(tmp_path / "niet.json")]):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1


def test_main_ongeldige_json(tmp_path, capsys):
    kapot = tmp_path / "kapot.json"
    kapot.write_text("{niet geldig}")
    with patch.object(sys, "argv", ["extract_kruisrefs.py", "--input", str(kapot)]):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1


def test_main_lege_leden(tmp_path, capsys):
    data = {"bwb-id": "BWBR0004770", "artikel": "9", "leden": []}
    pad = tmp_path / "art9.json"
    pad.write_text(json.dumps(data))
    with patch.object(sys, "argv", ["extract_kruisrefs.py", "--input", str(pad)]):
        main()
    out = capsys.readouterr().out
    assert out.strip() == "[]"


def test_main_met_jci_links(tmp_path, capsys):
    data = {
        "bwb-id": "BWBR0004770",
        "artikel": "10",
        "leden": [
            {"lid": "1", "tekst": "[artikel 9](jci1.3:c:BWBR0004770&artikel=9)"}
        ],
    }
    pad = tmp_path / "art10.json"
    pad.write_text(json.dumps(data))
    with patch.object(sys, "argv", ["extract_kruisrefs.py", "--input", str(pad)]):
        main()
    out = capsys.readouterr().out
    result = json.loads(out)
    assert len(result) >= 1
    assert result[0]["doel-artikel"] == "9"


def test_main_met_output_bestand(tmp_path):
    data = {
        "bwb-id": "BWBR0004770",
        "artikel": "10",
        "leden": [
            {"lid": "1", "tekst": "[artikel 9](jci1.3:c:BWBR0004770&artikel=9)"}
        ],
    }
    pad = tmp_path / "art10.json"
    pad.write_text(json.dumps(data))
    out_pad = tmp_path / "out" / "result.json"
    with patch.object(sys, "argv", ["extract_kruisrefs.py", "--input", str(pad), "--output", str(out_pad)]):
        main()
    assert out_pad.exists()
    result = json.loads(out_pad.read_text())
    assert isinstance(result, list)


def test_main_bron_lid_filter(tmp_path, capsys):
    data = {
        "bwb-id": "BWBR0004770",
        "artikel": "9",
        "leden": [
            {"lid": "1", "tekst": "[artikel 10](jci1.3:c:BWBR0004770&artikel=10)"},
            {"lid": "2", "tekst": "[artikel 11](jci1.3:c:BWBR0004770&artikel=11)"},
        ],
    }
    pad = tmp_path / "art9.json"
    pad.write_text(json.dumps(data))
    with patch.object(sys, "argv", ["extract_kruisrefs.py", "--input", str(pad), "--bron-lid", "1"]):
        main()
    out = capsys.readouterr().out
    result = json.loads(out)
    assert all(r["bron-lid"] == "1" for r in result)


def test_main_bron_lid_niet_gevonden(tmp_path, capsys):
    data = {
        "bwb-id": "BWBR0004770",
        "artikel": "9",
        "leden": [{"lid": "1", "tekst": "artikel 10"}],
    }
    pad = tmp_path / "art9.json"
    pad.write_text(json.dumps(data))
    with patch.object(sys, "argv", ["extract_kruisrefs.py", "--input", str(pad), "--bron-lid", "99"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 1


def test_main_output_is_json_array(tmp_path, capsys):
    data = {
        "bwb-id": "BWBR0004770",
        "artikel": "9",
        "leden": [{"lid": "1", "tekst": "Artikel 10 is van toepassing."}],
    }
    pad = tmp_path / "art9.json"
    pad.write_text(json.dumps(data))
    with patch.object(sys, "argv", ["extract_kruisrefs.py", "--input", str(pad)]):
        main()
    out = capsys.readouterr().out
    result = json.loads(out)
    assert isinstance(result, list)
