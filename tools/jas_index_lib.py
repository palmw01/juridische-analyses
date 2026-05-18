"""Gedeelde functies voor de juridische kennisgraaf-tools."""

import json
import sys
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# I/O-helpers — uniform laden van YAML en JSON met UTF-8 + foutafhandeling
# ---------------------------------------------------------------------------

def load_yaml(path: Path, *, silent: bool = True) -> dict | None:
    """Laad een YAML-bestand. Bij OSError/YAMLError: None (silent=True) of raise."""
    try:
        with path.open(encoding="utf-8") as f:
            return yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as e:
        if silent:
            print(f"[load_yaml] {path}: {e}", file=sys.stderr)
            return None
        raise


def load_json(path: Path, *, silent: bool = True) -> dict | None:
    """Laad een JSON-bestand. Bij OSError/JSONDecodeError: None (silent=True) of raise."""
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        if silent:
            print(f"[load_json] {path}: {e}", file=sys.stderr)
            return None
        raise


def slug_from_begrip_id(bid: str) -> str:
    """Haal de slug (laatste pad-segment) uit een begrip-id zoals 'BWBR0004770/art9/lid1/foo'."""
    return bid.rstrip("/").rsplit("/", 1)[-1] if bid else ""


# ---------------------------------------------------------------------------
# Definitie-helpers — gelaagde definitie (kern + contexten)
# ---------------------------------------------------------------------------

def haal_kern(definitie_obj) -> str:
    """Extraheer de kerntekst uit een definitie-object of legacy-string."""
    if isinstance(definitie_obj, dict):
        return str(definitie_obj.get("kern") or "").strip()
    return str(definitie_obj or "").strip()


def haal_contexten(definitie_obj) -> list[dict]:
    """Retourneer de contextarray uit een definitie-object (lege lijst bij legacy-string)."""
    if isinstance(definitie_obj, dict):
        return list(definitie_obj.get("contexten") or [])
    return []


# ---------------------------------------------------------------------------
# JAS-index
# ---------------------------------------------------------------------------

def bouw_jas_index(project_root: Path) -> dict[str, str]:
    """Bouw een map begrip-id → jas-klasse door alle annotatie-JSONs te scannen."""
    index: dict[str, str] = {}
    annotaties_dir = project_root / "annotaties"
    if not annotaties_dir.exists():
        return index
    for json_file in sorted(annotaties_dir.glob("**/*.json")):
        rel_parts = json_file.relative_to(annotaties_dir).parts
        if any(part.startswith(".") for part in rel_parts):
            continue
        data = load_json(json_file)
        if data is None:
            continue
        for rij in data.get("annotatierijen") or []:
            bid = rij.get("begrip-id")
            jas = rij.get("jas-klasse")
            if bid and jas and bid not in index:
                index[bid] = jas
    return index
