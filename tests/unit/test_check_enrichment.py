"""Tests voor tools/check_enrichment.py — triggers, analyse, queue, CLI."""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from check_enrichment import (
    detecteer_triggers,
    genereer_delta_analyse,
    genereer_advies,
    laad_queue,
    sla_queue_op,
    is_in_queue,
    is_gesloten,
    scan_begrippen,
    druk_rapport,
    main,
    Trigger,
)
from tests.fixtures.begrippen import maak_begrip


# ===== detecteer_triggers =====

def test_triggers_geen_markeringen_geen_triggers():
    fm = maak_begrip(markeringen=[], **{"definitie-gebaseerd-op": []})
    assert detecteer_triggers(fm) == []


def test_triggers_een_markering_bevestigd_geen_triggers():
    fm = maak_begrip(markeringen=[{
        "markering-id": "m-001", "bijdrage": "primair",
        "bron-annotatie-id": "x", "jas-klasse": "rechtssubject", "bevestigd": True,
    }])
    assert Trigger.ONBEVESTIGD not in detecteer_triggers(fm)


def test_triggers_onbevestigde_markering():
    fm = maak_begrip()  # default bevestigd: False
    triggers = detecteer_triggers(fm)
    assert Trigger.ONBEVESTIGD in triggers


def test_triggers_status_te_verrijken():
    fm = maak_begrip(status="te-verrijken")
    triggers = detecteer_triggers(fm)
    assert Trigger.STATUS_TE_VERRIJKEN in triggers


def test_triggers_meerdere_markeringen_aanvullend_zonder_context():
    fm = maak_begrip(
        markeringen=[
            {"markering-id": "m-001", "bijdrage": "primair", "bron-annotatie-id": "x",
             "jas-klasse": "rechtssubject", "bevestigd": True},
            {"markering-id": "m-002", "bijdrage": "aanvullend", "bron-annotatie-id": "y",
             "jas-klasse": "rechtssubject", "bevestigd": True},
        ],
        definitie={"kern": "definitie", "contexten": []},
    )
    triggers = detecteer_triggers(fm)
    assert Trigger.MEERDERE_MARKERINGEN in triggers
    assert Trigger.CONTEXT_ONGEDOCUMENTEERD in triggers


def test_triggers_aanvullend_met_context_geen_meerdere():
    fm = maak_begrip(
        markeringen=[
            {"markering-id": "m-001", "bijdrage": "primair", "bron-annotatie-id": "x",
             "jas-klasse": "rechtssubject", "bevestigd": True},
            {"markering-id": "m-002", "bijdrage": "aanvullend", "bron-annotatie-id": "y",
             "jas-klasse": "rechtssubject", "bevestigd": True},
        ],
        definitie={"kern": "definitie", "contexten": [{"markering-id": "m-002", "tekst": "ctx"}]},
    )
    triggers = detecteer_triggers(fm)
    assert Trigger.MEERDERE_MARKERINGEN not in triggers
    assert Trigger.CONTEXT_ONGEDOCUMENTEERD not in triggers


def test_triggers_conflicterende_primaire_markeringen():
    fm = maak_begrip(
        markeringen=[
            {"markering-id": "m-001", "bijdrage": "primair", "bron-annotatie-id": "x",
             "tekst": "persoon A", "jas-klasse": "rechtssubject", "bevestigd": True},
            {"markering-id": "m-002", "bijdrage": "primair", "bron-annotatie-id": "y",
             "tekst": "persoon B", "jas-klasse": "rechtssubject", "bevestigd": True},
        ],
        definitie={"kern": "definitie", "contexten": []},
    )
    triggers = detecteer_triggers(fm)
    assert Trigger.CONFLICTERENDE_PRIMAIR in triggers


def test_triggers_definitie_basis_verlopen():
    fm = maak_begrip(**{"definitie-gebaseerd-op": ["m-999-bestaat-niet"]})
    triggers = detecteer_triggers(fm)
    assert Trigger.DEFINITIE_BASIS_VERLOPEN in triggers


def test_triggers_definitie_basis_geldig():
    fm = maak_begrip(**{"definitie-gebaseerd-op": ["m-001"]})
    triggers = detecteer_triggers(fm)
    assert Trigger.DEFINITIE_BASIS_VERLOPEN not in triggers


# ===== genereer_delta_analyse =====

def test_delta_analyse_onbevestigd():
    fm = maak_begrip()
    triggers = [Trigger.ONBEVESTIGD]
    result = genereer_delta_analyse(fm, triggers)
    assert "verificatie" in result.lower() or "bevestig" in result.lower()


def test_delta_analyse_status_te_verrijken():
    fm = maak_begrip(status="te-verrijken")
    result = genereer_delta_analyse(fm, [Trigger.STATUS_TE_VERRIJKEN])
    assert "te-verrijken" in result


def test_delta_analyse_geen_triggers_geeft_fallback():
    fm = maak_begrip()
    result = genereer_delta_analyse(fm, [])
    assert result == "Automatisch gedetecteerd als enrichment-kandidaat."


def test_delta_analyse_conflicterend():
    fm = maak_begrip(
        markeringen=[
            {"markering-id": "m-001", "bijdrage": "primair", "bron-annotatie-id": "x",
             "tekst": "tekst A", "jas-klasse": "rechtssubject", "bevestigd": True},
            {"markering-id": "m-002", "bijdrage": "primair", "bron-annotatie-id": "y",
             "tekst": "tekst B", "jas-klasse": "rechtssubject", "bevestigd": True},
        ],
        definitie={"kern": "definitie", "contexten": []},
    )
    result = genereer_delta_analyse(fm, [Trigger.MEERDERE_MARKERINGEN, Trigger.CONFLICTERENDE_PRIMAIR])
    assert "Conflicterende" in result


def test_delta_analyse_context_ongedocumenteerd():
    fm = maak_begrip(
        markeringen=[
            {"markering-id": "m-001", "bijdrage": "primair", "bron-annotatie-id": "x",
             "jas-klasse": "rechtssubject", "bevestigd": True},
            {"markering-id": "m-002", "bijdrage": "aanvullend", "bron-annotatie-id": "y",
             "jas-klasse": "rechtssubject", "bevestigd": True},
        ],
        definitie={"kern": "definitie", "contexten": []},
    )
    result = genereer_delta_analyse(fm, [Trigger.MEERDERE_MARKERINGEN, Trigger.CONTEXT_ONGEDOCUMENTEERD])
    assert "aanvullend" in result.lower() or "context" in result.lower()


def test_delta_analyse_definitie_basis_verlopen():
    fm = maak_begrip(**{"definitie-gebaseerd-op": ["m-999"]})
    result = genereer_delta_analyse(fm, [Trigger.DEFINITIE_BASIS_VERLOPEN])
    assert "verlopen" in result.lower() or "definitie-gebaseerd-op" in result


# ===== genereer_advies =====

def test_advies_conflicterend():
    fm = maak_begrip()
    result = genereer_advies(fm, [Trigger.CONFLICTERENDE_PRIMAIR])
    assert "conflicterend" in result or "afsplitsen" in result


def test_advies_te_verrijken():
    fm = maak_begrip(status="te-verrijken")
    result = genereer_advies(fm, [Trigger.STATUS_TE_VERRIJKEN])
    assert "herziening" in result or "te-verrijken" in result.lower()


def test_advies_definitie_basis_verlopen():
    fm = maak_begrip()
    result = genereer_advies(fm, [Trigger.DEFINITIE_BASIS_VERLOPEN])
    assert "definitie-gebaseerd-op" in result or "bijwerken" in result


def test_advies_onbevestigd():
    fm = maak_begrip()
    result = genereer_advies(fm, [Trigger.ONBEVESTIGD])
    assert "bevestiging" in result or "geverifieerd" in result


def test_advies_context_ongedocumenteerd():
    fm = maak_begrip()
    result = genereer_advies(fm, [Trigger.CONTEXT_ONGEDOCUMENTEERD])
    assert "context" in result.lower()


def test_advies_identieke_markeringen():
    fm = maak_begrip(
        markeringen=[
            {"markering-id": "m-001", "bijdrage": "primair", "tekst": "zelfde tekst",
             "bron-annotatie-id": "x", "jas-klasse": "rechtssubject", "bevestigd": True},
            {"markering-id": "m-002", "bijdrage": "primair", "tekst": "zelfde tekst",
             "bron-annotatie-id": "y", "jas-klasse": "rechtssubject", "bevestigd": True},
        ],
        definitie={"kern": "definitie", "contexten": []},
    )
    result = genereer_advies(fm, [Trigger.MEERDERE_MARKERINGEN])
    assert "identieke" in result or "ongewijzigd" in result


def test_advies_met_contexten():
    fm = maak_begrip(
        markeringen=[
            {"markering-id": "m-001", "bijdrage": "primair", "tekst": "tekst A",
             "bron-annotatie-id": "x", "jas-klasse": "rechtssubject", "bevestigd": True},
        ],
        definitie={"kern": "definitie", "contexten": [{"markering-id": "m-001", "tekst": "ctx"}]},
    )
    result = genereer_advies(fm, [Trigger.MEERDERE_MARKERINGEN])
    assert "context" in result.lower() or "kern" in result.lower()


# ===== laad_queue / sla_queue_op =====

def test_laad_queue_niet_bestaand(tmp_path):
    assert laad_queue(tmp_path / "niet-bestaand.json") == []


def test_laad_queue_leeg_bestand(tmp_path):
    pad = tmp_path / "queue.json"
    pad.write_text("[]")
    assert laad_queue(pad) == []


def test_laad_queue_met_items(tmp_path):
    pad = tmp_path / "queue.json"
    data = [{"begrip-id": "test/begrip", "beslissing": None}]
    pad.write_text(json.dumps(data))
    result = laad_queue(pad)
    assert len(result) == 1
    assert result[0]["begrip-id"] == "test/begrip"


def test_sla_queue_op_maakt_bestand(tmp_path):
    pad = tmp_path / "rapporten" / "queue.json"
    sla_queue_op(pad, [{"begrip-id": "test"}])
    assert pad.exists()


def test_sla_queue_op_schrijft_inhoud(tmp_path):
    pad = tmp_path / "queue.json"
    data = [{"begrip-id": "test/begrip", "aangemeld-op": "2024-01-01"}]
    sla_queue_op(pad, data)
    result = json.loads(pad.read_text())
    assert result[0]["begrip-id"] == "test/begrip"


# ===== is_in_queue / is_gesloten =====

def test_is_in_queue_aanwezig():
    queue = [{"begrip-id": "test/begrip", "beslissing": None}]
    assert is_in_queue("test/begrip", queue) is True


def test_is_in_queue_niet_aanwezig():
    queue = [{"begrip-id": "ander/begrip"}]
    assert is_in_queue("test/begrip", queue) is False


def test_is_in_queue_lege_queue():
    assert is_in_queue("test/begrip", []) is False


def test_is_gesloten_met_beslissing():
    queue = [{"begrip-id": "test/begrip", "beslissing": "accepteren"}]
    assert is_gesloten("test/begrip", queue) is True


def test_is_gesloten_zonder_beslissing():
    queue = [{"begrip-id": "test/begrip", "beslissing": None}]
    assert is_gesloten("test/begrip", queue) is False


def test_is_gesloten_niet_in_queue():
    assert is_gesloten("test/begrip", []) is False


# ===== scan_begrippen =====

def test_scan_begrippen_lege_map(tmp_path):
    (tmp_path / "begrippen").mkdir()
    nieuwe, overgeslagen, gesloten = scan_begrippen(tmp_path, [], None, False)
    assert nieuwe == []


def test_scan_begrippen_geen_begrippen_dir(tmp_path, capsys):
    nieuwe, overgeslagen, gesloten = scan_begrippen(tmp_path, [], None, False)
    assert nieuwe == []


def test_scan_begrippen_kandidaat_gevonden(tmp_path):
    (tmp_path / "begrippen").mkdir()
    fm = maak_begrip()  # default: bevestigd: False → ONBEVESTIGD trigger
    (tmp_path / "begrippen" / "test.yaml").write_text(yaml.dump(fm, allow_unicode=True))
    nieuwe, _, _ = scan_begrippen(tmp_path, [], None, False)
    assert len(nieuwe) == 1
    assert nieuwe[0]["begrip-id"] == "BWBR0004770/art9/lid1/belastingschuldige"


def test_scan_begrippen_al_in_queue_overgeslagen(tmp_path):
    (tmp_path / "begrippen").mkdir()
    fm = maak_begrip()
    (tmp_path / "begrippen" / "test.yaml").write_text(yaml.dump(fm, allow_unicode=True))
    queue = [{"begrip-id": "BWBR0004770/art9/lid1/belastingschuldige", "beslissing": None}]
    _, overgeslagen, _ = scan_begrippen(tmp_path, queue, None, False)
    assert "BWBR0004770/art9/lid1/belastingschuldige" in overgeslagen


def test_scan_begrippen_gesloten_overgeslagen(tmp_path):
    (tmp_path / "begrippen").mkdir()
    fm = maak_begrip()
    (tmp_path / "begrippen" / "test.yaml").write_text(yaml.dump(fm, allow_unicode=True))
    queue = [{"begrip-id": "BWBR0004770/art9/lid1/belastingschuldige", "beslissing": "accepteren"}]
    _, _, gesloten = scan_begrippen(tmp_path, queue, None, False)
    assert "BWBR0004770/art9/lid1/belastingschuldige" in gesloten


def test_scan_begrippen_verbose_output(tmp_path, capsys):
    (tmp_path / "begrippen").mkdir()
    fm = maak_begrip()
    (tmp_path / "begrippen" / "test.yaml").write_text(yaml.dump(fm, allow_unicode=True))
    queue = [{"begrip-id": "BWBR0004770/art9/lid1/belastingschuldige", "beslissing": None}]
    scan_begrippen(tmp_path, queue, None, verbose=True)
    out = capsys.readouterr().out
    assert "queue" in out.lower() or "belastingschuldige" in out


def test_scan_begrippen_geen_triggers_overgeslagen(tmp_path):
    (tmp_path / "begrippen").mkdir()
    fm = maak_begrip(
        markeringen=[{
            "markering-id": "m-001", "bijdrage": "primair", "bron-annotatie-id": "x",
            "jas-klasse": "rechtssubject", "bevestigd": True,
        }],
        status="definitief",
        **{"definitie-gebaseerd-op": ["m-001"]},
    )
    (tmp_path / "begrippen" / "test.yaml").write_text(yaml.dump(fm, allow_unicode=True))
    nieuwe, _, _ = scan_begrippen(tmp_path, [], None, False)
    assert nieuwe == []


# ===== druk_rapport =====

def test_druk_rapport_geen_kandidaten(tmp_path, capsys):
    druk_rapport([], [], [], False, tmp_path / "queue.json")
    out = capsys.readouterr().out
    assert "Geen nieuwe" in out


def test_druk_rapport_met_kandidaten(tmp_path, capsys):
    kandidaat = {
        "begrip-id": "test/begrip",
        "triggers": [Trigger.ONBEVESTIGD],
        "advies": "bevestiging vereist",
    }
    druk_rapport([kandidaat], [], [], False, tmp_path / "queue.json")
    out = capsys.readouterr().out
    assert "test/begrip" in out
    assert "Queue bijgewerkt" in out


def test_druk_rapport_dry_run(tmp_path, capsys):
    kandidaat = {"begrip-id": "test/begrip", "triggers": [], "advies": ""}
    druk_rapport([kandidaat], [], [], True, tmp_path / "queue.json")
    out = capsys.readouterr().out
    assert "Dry-run" in out


def test_druk_rapport_met_overgeslagen(tmp_path, capsys):
    druk_rapport([], ["test/overgeslagen"], [], False, tmp_path / "queue.json")
    out = capsys.readouterr().out
    assert "open in queue" in out or "overgeslagen" in out.lower()


def test_druk_rapport_met_gesloten(tmp_path, capsys):
    druk_rapport([], [], ["test/gesloten"], False, tmp_path / "queue.json")
    out = capsys.readouterr().out
    assert "gesloten" in out.lower()


# ===== main() =====

def test_main_succes_leeg_project(tmp_path):
    (tmp_path / "begrippen").mkdir()
    (tmp_path / "rapporten").mkdir()
    with patch.object(sys, "argv", ["check_enrichment.py", "--project-dir", str(tmp_path)]):
        result = main()
    assert result == 0


def test_main_met_kandidaten_exit_2(tmp_path):
    (tmp_path / "begrippen").mkdir()
    fm = maak_begrip()  # onbevestigd → kandidaat
    (tmp_path / "begrippen" / "test.yaml").write_text(yaml.dump(fm, allow_unicode=True))
    with patch.object(sys, "argv", ["check_enrichment.py", "--project-dir", str(tmp_path)]):
        result = main()
    assert result == 2


def test_main_dry_run_schrijft_niet(tmp_path):
    (tmp_path / "begrippen").mkdir()
    fm = maak_begrip()
    (tmp_path / "begrippen" / "test.yaml").write_text(yaml.dump(fm, allow_unicode=True))
    queue_pad = tmp_path / "rapporten" / "enrichment-queue.json"
    with patch.object(sys, "argv", ["check_enrichment.py", "--project-dir", str(tmp_path), "--dry-run"]):
        result = main()
    assert result == 2
    assert not queue_pad.exists()


def test_main_schrijft_queue_bij_kandidaten(tmp_path):
    (tmp_path / "begrippen").mkdir()
    fm = maak_begrip()
    (tmp_path / "begrippen" / "test.yaml").write_text(yaml.dump(fm, allow_unicode=True))
    queue_pad = tmp_path / "rapporten" / "enrichment-queue.json"
    with patch.object(sys, "argv", ["check_enrichment.py", "--project-dir", str(tmp_path)]):
        main()
    assert queue_pad.exists()


def test_main_ongeldige_datum_exit_1(tmp_path, capsys):
    (tmp_path / "begrippen").mkdir()
    with patch.object(sys, "argv", ["check_enrichment.py", "--project-dir", str(tmp_path), "--since", "niet-een-datum"]):
        result = main()
    assert result == 1
