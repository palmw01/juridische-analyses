#!/usr/bin/env python3
"""
fetch_wettenbank.py — Normaliseer een MCP-response van de wettenbank API naar bronnen/-formaat.

Gebruik:
    python tools/fetch_wettenbank.py --input /tmp/mcp-response.json --vault-root .
    echo '{...}' | python tools/fetch_wettenbank.py --vault-root .
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normaliseer een MCP-response van de wettenbank naar bronnen/-formaat."
    )
    parser.add_argument(
        "--input", "-i",
        metavar="FILE",
        help="Pad naar het JSON-invoerbestand (default: stdin)",
    )
    parser.add_argument(
        "--vault-root",
        required=True,
        metavar="DIR",
        help="Pad naar de vault root (bevat bronnen/)",
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overschrijf het uitvoerbestand als het al bestaat",
    )
    return parser.parse_args()


def load_input(input_path: str | None) -> dict:
    """Laad JSON van bestand of stdin."""
    try:
        if input_path:
            with open(input_path, encoding="utf-8") as fh:
                return json.load(fh)
        else:
            return json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"Fout: ongeldige JSON — {exc}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Fout: kan bestand niet lezen — {exc}", file=sys.stderr)
        sys.exit(1)


def validate_response(data: dict) -> None:
    """Controleer verplichte velden in de MCP-response."""
    required = {"bwbId", "artikel", "leden"}
    missing = required - data.keys()
    if missing:
        print(f"Fout: ontbrekende velden in MCP-response: {', '.join(sorted(missing))}", file=sys.stderr)
        sys.exit(1)


def normalize_artikel(artikel: str) -> str:
    """Verwijder leading/trailing whitespace; bewaar lowercase letters (bijv. '9a' → '9a')."""
    return artikel.strip()


def normalize(data: dict) -> dict:
    """Bouw het genormaliseerde bronnen-record op."""
    artikel = normalize_artikel(str(data["artikel"]))
    return {
        "bwb-id": data["bwbId"],
        "wet": data.get("citeertitel", ""),
        "artikel": artikel,
        "citeertitel": data.get("citeertitel", ""),
        "versiedatum": data.get("versiedatum", ""),
        "structuurpositie": data.get("pad", ""),
        "leden": data.get("leden", []),
        "bronreferentie": data.get("bronreferentie", ""),
        "opgehaald-op": date.today().isoformat(),
    }


def write_output(record: dict, vault_root: Path, force: bool) -> Path:
    """Schrijf het record naar bronnen/{bwb-id}/art{artikel}.json."""
    bwb_id = record["bwb-id"]
    artikel = record["artikel"]

    output_dir = vault_root / "bronnen" / bwb_id
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"art{artikel}.json"

    if output_path.exists() and not force:
        print(f"al aanwezig: {output_path}", file=sys.stderr)
        sys.exit(0)

    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    return output_path


def main() -> None:
    args = parse_args()
    vault_root = Path(args.vault_root).resolve()

    if not vault_root.is_dir():
        print(f"Fout: vault-root bestaat niet of is geen directory: {vault_root}", file=sys.stderr)
        sys.exit(1)

    data = load_input(args.input)
    validate_response(data)
    record = normalize(data)
    output_path = write_output(record, vault_root, args.force)
    print(str(output_path))


if __name__ == "__main__":
    main()
