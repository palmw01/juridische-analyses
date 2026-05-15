"""Tests voor sitegen/data.py — laad_waarschuwingen_meta en zoek_meta."""
import json
from pathlib import Path

import yaml
import pytest

from sitegen.data import laad_waarschuwingen_meta, zoek_meta


def _schrijf_meta(tmp_path: Path, entries: list) -> Path:
    tools = tmp_path / "tools"
    tools.mkdir(exist_ok=True)
    (tools / "waarschuwingen-meta.yaml").write_text(
        yaml.dump(entries, allow_unicode=True)
    )
    return tmp_path


# ── laad_waarschuwingen_meta ──────────────────────────────────────────────────

def test_laad_meta_ontbreekt_geeft_lege_lijst(tmp_path):
    assert laad_waarschuwingen_meta(tmp_path) == []


def test_laad_meta_leest_entries(tmp_path):
    entries = [{"sleutel": "definitie.kern is leeg", "titel": "Test", "uitleg": "U.", "stappen": ["S1"]}]
    _schrijf_meta(tmp_path, entries)
    result = laad_waarschuwingen_meta(tmp_path)
    assert len(result) == 1
    assert result[0]["titel"] == "Test"


def test_laad_meta_sorteert_langste_eerst(tmp_path):
    entries = [
        {"sleutel": "kort", "titel": "Kort"},
        {"sleutel": "heel lang prefix hier", "titel": "Lang"},
        {"sleutel": "middel prefix", "titel": "Middel"},
    ]
    _schrijf_meta(tmp_path, entries)
    result = laad_waarschuwingen_meta(tmp_path)
    sleutels = [e["sleutel"] for e in result]
    assert sleutels == sorted(sleutels, key=lambda s: -len(s))


def test_laad_meta_lege_yaml_geeft_lege_lijst(tmp_path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "waarschuwingen-meta.yaml").write_text("")
    assert laad_waarschuwingen_meta(tmp_path) == []


# ── zoek_meta ─────────────────────────────────────────────────────────────────

def test_zoek_meta_exacte_match(tmp_path):
    meta = [{"sleutel": "definitie.kern is leeg", "titel": "Kern ontbreekt", "uitleg": "", "stappen": []}]
    result = zoek_meta("[L3] definitie.kern is leeg — gebruik /begrip", meta)
    assert result is not None
    assert result["titel"] == "Kern ontbreekt"


def test_zoek_meta_strip_l2_prefix():
    meta = [{"sleutel": "annotatierijen leeg", "titel": "Geen rijen", "uitleg": "", "stappen": []}]
    assert zoek_meta("[L2] annotatierijen leeg — actie vereist", meta) is not None


def test_zoek_meta_strip_l1_prefix():
    meta = [{"sleutel": "annotatierijen leeg", "titel": "Test", "uitleg": "", "stappen": []}]
    assert zoek_meta("[L1] annotatierijen leeg", meta) is not None


def test_zoek_meta_dynamisch_suffix_matcht(tmp_path):
    meta = [{"sleutel": "prioriteit is ingevuld (", "titel": "Verkeerde prioriteit", "uitleg": "", "stappen": []}]
    result = zoek_meta("[L3] prioriteit is ingevuld (2) maar soort is 'Rekenregel'", meta)
    assert result is not None
    assert result["titel"] == "Verkeerde prioriteit"


def test_zoek_meta_geen_match_geeft_none():
    meta = [{"sleutel": "bekende sleutel", "titel": "Test", "uitleg": "", "stappen": []}]
    assert zoek_meta("[L3] onbekende waarschuwing", meta) is None


def test_zoek_meta_lege_lijst_geeft_none():
    assert zoek_meta("[L3] definitie.kern is leeg", []) is None


def test_zoek_meta_langste_eerst_wint():
    """Specifiekere (langere) sleutel wint van kortere bij overlappende prefixen als meta gesorteerd is."""
    meta_gesorteerd = [
        {"sleutel": "definitie.kern is leeg maar definitie.contexten[] bevat items", "titel": "Specifiek", "uitleg": "", "stappen": []},
        {"sleutel": "definitie.kern is leeg", "titel": "Generiek", "uitleg": "", "stappen": []},
    ]
    result = zoek_meta("[L3] definitie.kern is leeg maar definitie.contexten[] bevat items — ...", meta_gesorteerd)
    assert result["titel"] == "Specifiek"


def test_zoek_meta_kortere_sleutel_matcht_als_geen_langere_past():
    meta = [
        {"sleutel": "definitie.kern is leeg maar definitie.contexten[] bevat items", "titel": "Specifiek", "uitleg": "", "stappen": []},
        {"sleutel": "definitie.kern is leeg", "titel": "Generiek", "uitleg": "", "stappen": []},
    ]
    result = zoek_meta("[L3] definitie.kern is leeg — gebruik /begrip", meta)
    assert result["titel"] == "Generiek"
