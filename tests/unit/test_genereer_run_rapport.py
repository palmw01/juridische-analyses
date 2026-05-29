"""Tests voor tools/genereer_run_rapport.py."""
import json
from pathlib import Path

import pytest

from genereer_run_rapport import (
    lees_stap_status,
    bouw_mermaid,
    lees_validatie_rapport,
    tel_open_velden,
    schrijf_rapport,
    main,
)


# ---------------------------------------------------------------------------
# lees_stap_status
# ---------------------------------------------------------------------------

def test_lees_stap_status_geldige_lijst(tmp_path):
    f = tmp_path / "stappen.json"
    stappen = [{"name": "A2", "status": "completed"}]
    f.write_text(json.dumps(stappen))
    assert lees_stap_status(f) == stappen


def test_lees_stap_status_geen_lijst_geeft_valueerror(tmp_path):
    f = tmp_path / "stappen.json"
    f.write_text(json.dumps({"name": "x"}))
    with pytest.raises(ValueError, match="verwacht een JSON-lijst"):
        lees_stap_status(f)


def test_lees_stap_status_ontbrekend_bestand_geeft_fout(tmp_path):
    with pytest.raises(Exception):
        lees_stap_status(tmp_path / "weg.json")


# ---------------------------------------------------------------------------
# bouw_mermaid
# ---------------------------------------------------------------------------

def test_bouw_mermaid_bevat_mermaid_header():
    stappen = [{"name": "A2", "status": "completed"}]
    result = bouw_mermaid(stappen)
    assert "```mermaid" in result
    assert "graph LR" in result


def test_bouw_mermaid_knopen_per_stap():
    stappen = [
        {"name": "stap-een", "status": "completed"},
        {"name": "stap-twee", "status": "pending"},
    ]
    result = bouw_mermaid(stappen)
    assert "stap-een" in result
    assert "stap-twee" in result
    assert "S0 --> S1" in result


def test_bouw_mermaid_lege_stappen():
    result = bouw_mermaid([])
    assert "```mermaid" in result
    assert "S0" not in result


def test_bouw_mermaid_classdef_per_status():
    stappen = [{"name": "x", "status": "blocked"}]
    result = bouw_mermaid(stappen)
    assert "classDef blocked" in result


def test_bouw_mermaid_onbekende_status_valt_terug_op_pending():
    stappen = [{"name": "x", "status": "onbekend"}]
    result = bouw_mermaid(stappen)
    assert "class S0 onbekend" in result


def test_bouw_mermaid_naam_met_aanhalingstekens():
    stappen = [{"name": 'naam "met" quotes', "status": "completed"}]
    result = bouw_mermaid(stappen)
    # Aanhalingstekens in naam worden vervangen door enkele quotes
    assert '"met"' not in result
    assert "'met'" in result


def test_bouw_mermaid_geen_pijl_bij_eerste_stap():
    stappen = [{"name": "eerste", "status": "completed"}]
    result = bouw_mermaid(stappen)
    assert "-->" not in result


# ---------------------------------------------------------------------------
# lees_validatie_rapport
# ---------------------------------------------------------------------------

def test_lees_validatie_rapport_ontbreekt_geeft_defaults(tmp_path):
    result = lees_validatie_rapport(tmp_path)
    assert result == {"l1": 0, "l2": 0, "l3": 0, "bestanden": 0, "details": []}


def test_lees_validatie_rapport_telt_fouten(tmp_path):
    rapport_dir = tmp_path / "rapporten"
    rapport_dir.mkdir()
    data = {
        "geslaagd": 5,
        "blokkeerfouten": [
            {"laag": "L1", "bestand": "a.yaml", "boodschap": "fout"},
            {"laag": "L2", "bestand": "b.yaml", "boodschap": "fout"},
        ],
        "waarschuwingen": [
            {"bestand": "c.yaml", "boodschap": "waarschuwing"},
        ],
    }
    (rapport_dir / "validatie-rapport.json").write_text(json.dumps(data))
    result = lees_validatie_rapport(tmp_path)
    assert result["l1"] == 1
    assert result["l2"] == 1
    assert result["l3"] == 1
    assert result["bestanden"] == 5
    assert len(result["details"]) == 1


def test_lees_validatie_rapport_leeg_json_geeft_defaults(tmp_path):
    rapport_dir = tmp_path / "rapporten"
    rapport_dir.mkdir()
    (rapport_dir / "validatie-rapport.json").write_text("{}")
    result = lees_validatie_rapport(tmp_path)
    assert result["l1"] == 0
    assert result["l3"] == 0


# ---------------------------------------------------------------------------
# tel_open_velden
# ---------------------------------------------------------------------------

def test_tel_open_velden_lege_mappen(tmp_path):
    (tmp_path / "validaties").mkdir()
    (tmp_path / "begrippen").mkdir()
    result = tel_open_velden(tmp_path)
    assert result == {"open_voorspellingen": 0, "onbevestigde_markeringen": 0, "te_valideren": 0}


def test_tel_open_velden_geen_mappen_geeft_nullen(tmp_path):
    result = tel_open_velden(tmp_path)
    assert result["open_voorspellingen"] == 0


def test_tel_open_velden_telt_vraagtekens(tmp_path):
    val_dir = tmp_path / "validaties"
    val_dir.mkdir()
    vr = {
        "kolommen": [
            {"is-voorspelling-juist": "?"},
            {"is-voorspelling-juist": "ja"},
            {"is-voorspelling-juist": "?"},
        ]
    }
    (val_dir / "VR-test.yaml").write_text(
        "kolommen:\n"
        "  - is-voorspelling-juist: \"?\"\n"
        "  - is-voorspelling-juist: ja\n"
        "  - is-voorspelling-juist: \"?\"\n"
    )
    result = tel_open_velden(tmp_path)
    assert result["open_voorspellingen"] == 2


def test_tel_open_velden_telt_onbevestigde_markeringen(tmp_path):
    begrippen_dir = tmp_path / "begrippen"
    begrippen_dir.mkdir()
    (begrippen_dir / "test.yaml").write_text(
        "markeringen:\n"
        "  - markering-id: m-001\n"
        "    bevestigd: false\n"
        "  - markering-id: m-002\n"
        "    bevestigd: true\n"
    )
    result = tel_open_velden(tmp_path)
    assert result["onbevestigde_markeringen"] == 1
    # begrip zonder validatie-blok telt als nog te valideren
    assert result["te_valideren"] == 1


def test_tel_open_velden_validatie_blok_telt_niet_als_te_valideren(tmp_path):
    begrippen_dir = tmp_path / "begrippen"
    begrippen_dir.mkdir()
    (begrippen_dir / "gevalideerd.yaml").write_text(
        "markeringen:\n"
        "  - markering-id: m-001\n"
        "    bevestigd: true\n"
        "validatie:\n"
        "  gevalideerd-door: JdG\n"
        "  gevalideerd-op: 2026-05-29\n"
        "  oordeel: goedgekeurd\n"
    )
    result = tel_open_velden(tmp_path)
    assert result["te_valideren"] == 0


# ---------------------------------------------------------------------------
# schrijf_rapport
# ---------------------------------------------------------------------------

def test_schrijf_rapport_maakt_bestand(tmp_path):
    output = tmp_path / "rapport.md"
    schrijf_rapport(
        output_pad=output,
        artikel="9",
        lid="1",
        wet="IW 1990",
        bwb_id="BWBR0004770",
        peildatum="2026-01-01",
        gestart_op="2026-01-01 10:00",
        klaar_op="2026-01-01 10:30",
        stappen=[{"name": "A2", "status": "completed", "summary": "klaar"}],
        gewijzigde_bestanden=["annotaties/BWBR0004770/art9-lid1.json"],
        validatie={"l1": 0, "l2": 0, "l3": 1, "bestanden": 3,
                   "details": [{"bestand": "x.yaml", "boodschap": "w1"}]},
        open_velden={"open_voorspellingen": 2, "onbevestigde_markeringen": 1, "te_valideren": 1},
    )
    assert output.exists()
    tekst = output.read_text()
    assert "art. 9 lid 1 IW 1990" in tekst
    assert "mermaid" in tekst
    assert "annotaties/BWBR0004770/art9-lid1.json" in tekst


def test_schrijf_rapport_meer_dan_20_l3_meldingen(tmp_path):
    output = tmp_path / "rapport.md"
    details = [{"bestand": f"f{i}.yaml", "boodschap": f"w{i}"} for i in range(25)]
    schrijf_rapport(
        output_pad=output,
        artikel="9", lid="1", wet="IW 1990", bwb_id="BWBR0004770",
        peildatum="2026-01-01", gestart_op="2026-01-01 10:00", klaar_op="2026-01-01 10:30",
        stappen=[],
        gewijzigde_bestanden=[],
        validatie={"l1": 0, "l2": 0, "l3": 25, "bestanden": 0, "details": details},
        open_velden={"open_voorspellingen": 0, "onbevestigde_markeringen": 0, "te_valideren": 0},
    )
    tekst = output.read_text()
    assert "+5 verdere L3-meldingen" in tekst


def test_schrijf_rapport_geen_bestanden(tmp_path):
    output = tmp_path / "rapport.md"
    schrijf_rapport(
        output_pad=output,
        artikel="2", lid="2", wet="IW 1990", bwb_id="BWBR0004770",
        peildatum="2026-01-01", gestart_op="2026-01-01 10:00", klaar_op="2026-01-01 10:30",
        stappen=[],
        gewijzigde_bestanden=[],
        validatie={"l1": 0, "l2": 0, "l3": 0, "bestanden": 0, "details": []},
        open_velden={"open_voorspellingen": 0, "onbevestigde_markeringen": 0, "te_valideren": 0},
    )
    tekst = output.read_text()
    assert "_(geen)_" in tekst
    assert "_(geen L3-waarschuwingen)_" in tekst


def test_schrijf_rapport_maakt_parent_aan(tmp_path):
    output = tmp_path / "rapporten" / "runs" / "rapport.md"
    schrijf_rapport(
        output_pad=output,
        artikel="9", lid="1", wet="IW 1990", bwb_id="BWBR0004770",
        peildatum="2026-01-01", gestart_op="2026-01-01 10:00", klaar_op="2026-01-01 10:30",
        stappen=[], gewijzigde_bestanden=[],
        validatie={"l1": 0, "l2": 0, "l3": 0, "bestanden": 0, "details": []},
        open_velden={"open_voorspellingen": 0, "onbevestigde_markeringen": 0, "te_valideren": 0},
    )
    assert output.exists()


# ---------------------------------------------------------------------------
# main (CLI)
# ---------------------------------------------------------------------------

def test_main_schrijft_rapport(tmp_path):
    steps_file = tmp_path / "stappen.json"
    steps_file.write_text(json.dumps([{"name": "A2", "status": "completed"}]))
    output = tmp_path / "rapport.md"
    ret = main([
        "--project-dir", str(tmp_path),
        "--artikel", "9",
        "--lid", "1",
        "--wet", "IW 1990",
        "--bwb-id", "BWBR0004770",
        "--peildatum", "2026-01-01",
        "--steps-json", str(steps_file),
        "--output", str(output),
    ])
    assert ret == 0
    assert output.exists()


def test_main_default_output_pad(tmp_path):
    steps_file = tmp_path / "stappen.json"
    steps_file.write_text(json.dumps([{"name": "A2", "status": "completed"}]))
    ret = main([
        "--project-dir", str(tmp_path),
        "--artikel", "9",
        "--lid", "1",
        "--wet", "IW 1990",
        "--bwb-id", "BWBR0004770",
        "--peildatum", "2026-01-01",
        "--steps-json", str(steps_file),
    ])
    assert ret == 0
    runs_dir = tmp_path / "rapporten" / "runs"
    assert any(runs_dir.glob("run-*.md"))


def test_main_met_gewijzigde_bestanden(tmp_path):
    steps_file = tmp_path / "stappen.json"
    steps_file.write_text(json.dumps([{"name": "A2", "status": "completed"}]))
    output = tmp_path / "rapport.md"
    ret = main([
        "--project-dir", str(tmp_path),
        "--artikel", "9",
        "--lid", "1",
        "--wet", "IW 1990",
        "--bwb-id", "BWBR0004770",
        "--peildatum", "2026-01-01",
        "--steps-json", str(steps_file),
        "--output", str(output),
        "--gewijzigde-bestanden", "annotaties/a.json, begrippen/b.yaml",
        "--gestart-op", "2026-01-01 09:00",
    ])
    assert ret == 0
    tekst = output.read_text()
    assert "annotaties/a.json" in tekst
    assert "begrippen/b.yaml" in tekst
