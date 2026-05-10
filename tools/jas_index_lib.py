"""Gedeelde functie: bouw jas-index uit annotatie-JSONs (A2 → begrip-id → JAS-klasse)."""

import json
from pathlib import Path


def bouw_jas_index(vault_root: Path) -> dict[str, str]:
    """Bouw een map begrip-id → jas-klasse door alle annotatie-JSONs te scannen."""
    index: dict[str, str] = {}
    annotaties_dir = vault_root / "annotaties"
    if not annotaties_dir.exists():
        return index
    for json_file in sorted(annotaties_dir.glob("**/*.json")):
        rel_parts = json_file.relative_to(annotaties_dir).parts
        if any(part.startswith(".") for part in rel_parts):
            continue
        with json_file.open(encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue
        for rij in data.get("annotatierijen") or []:
            bid = rij.get("begrip-id")
            jas = rij.get("jas-klasse")
            if bid and jas and bid not in index:
                index[bid] = jas
    return index
