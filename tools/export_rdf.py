#!/usr/bin/env python3
"""
export_rdf.py — Exporteer begrippen-vault naar RDF Turtle (SKOS-compatibel).

Leest begrippen/*.yaml en genereert graaf/begrippen.ttl op basis van de
SKOS-mapping in ontologie/skos-mapping.yaml. Geen rdflib nodig — Turtle
wordt als tekst gegenereerd.

Gebruik:
    cd vault-root/
    tools/.venv/bin/python tools/export_rdf.py [--vault-root .] [--out graaf/begrippen.ttl]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Turtle-hulpfuncties
# ---------------------------------------------------------------------------

def turtle_literal(waarde: str, lang: str = "nl") -> str:
    escaped = waarde.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"@{lang}'


def turtle_uri(uri: str, base: str = "") -> str:
    if uri.startswith("http://") or uri.startswith("https://"):
        return f"<{uri}>"
    # Behandel als lokale naam (begrip-id als URI-fragment)
    return f"<{base}{uri}>"


def slug_van_id(begrip_id: str) -> str:
    return begrip_id.replace("/", "_").replace("-", "_")


# ---------------------------------------------------------------------------
# Prefixes en header
# ---------------------------------------------------------------------------

PREFIXES = """@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix jas:  <http://regels.overheid.nl/jas/ontology#> .
@prefix dct:  <http://purl.org/dc/terms/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix begrip: <urn:jas:begrip:> .
"""

BEGRIP_BASE = "urn:jas:begrip:"


# ---------------------------------------------------------------------------
# Begrip → Turtle-blok
# ---------------------------------------------------------------------------

def begrip_naar_turtle(fm: dict, mapping: dict) -> str:
    begrip_id = fm.get("begrip-id", "")
    if not begrip_id:
        return ""

    uri_ref = f"begrip:{slug_van_id(begrip_id)}"
    lines: list[str] = [f"{uri_ref}"]
    lines.append("    a skos:Concept ;")

    # Velden op basis van mapping
    begripsnaam = fm.get("begripsnaam") or ""
    definitie = fm.get("definitie") or ""
    geldigheid_van = str(fm.get("geldigheid-van") or "")
    herkomst = fm.get("herkomst") or ""
    aliases: list[str] = fm.get("aliases") or []
    relaties: dict = fm.get("relaties") or {}

    if begripsnaam:
        lines.append(f"    skos:prefLabel {turtle_literal(begripsnaam)} ;")

    for alias in aliases:
        if alias:
            lines.append(f"    skos:altLabel {turtle_literal(str(alias))} ;")

    if definitie:
        lines.append(f"    skos:definition {turtle_literal(definitie)} ;")

    if geldigheid_van:
        lines.append(f'    dct:valid "{geldigheid_van}"^^xsd:date ;')

    if herkomst == "direct":
        # Markeringen als herkomst-bron
        for m in (fm.get("markeringen") or []):
            bron = m.get("bron-annotatie-id", "")
            if bron:
                bron_escaped = bron.replace('"', '\\"')
                lines.append(f'    prov:wasDerivedFrom "{bron_escaped}" ;')
                break  # één provenance-triple volstaat

    # Relaties
    is_een: list = relaties.get("is-een") or []
    heeft: list = relaties.get("heeft") or []
    leidt_tot: list = relaties.get("leidt-tot") or []

    for bid in is_een:
        if bid:
            lines.append(f"    skos:broader begrip:{slug_van_id(str(bid))} ;")

    for item in heeft:
        bid = item.get("begrip-id") if isinstance(item, dict) else str(item)
        if bid:
            lines.append(f"    jas:heeft begrip:{slug_van_id(str(bid))} ;")

    for item in leidt_tot:
        bid = item.get("begrip-id") if isinstance(item, dict) else str(item)
        if bid:
            lines.append(f"    jas:leidtTot begrip:{slug_van_id(str(bid))} ;")

    # Notities
    jas_klasse = fm.get("jas-klasse") or ""
    status = fm.get("status") or ""
    if jas_klasse:
        lines.append(f'    jas:jasKlasse "{jas_klasse}" ;')
    if status:
        lines.append(f'    jas:status "{status}" ;')

    # Afleidingsregel-koppeling
    ar_id = fm.get("afleidingsregel-id")
    if ar_id:
        lines.append(f'    jas:afleidingsregel "{ar_id}" ;')

    # Afsluiten: vervang laatste ';' door '.'
    if lines[-1].endswith(" ;"):
        lines[-1] = lines[-1][:-2] + " ."
    else:
        lines.append("    .")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Hoofd-export
# ---------------------------------------------------------------------------

def exporteer_begrippen(vault_root: Path, mapping: dict) -> list[str]:
    begrippen_dir = vault_root / "begrippen"
    blokken: list[str] = []

    for yaml_file in sorted(begrippen_dir.glob("*.yaml")):
        with yaml_file.open(encoding="utf-8") as f:
            fm = yaml.safe_load(f)
        if not fm or not isinstance(fm, dict):
            continue
        blok = begrip_naar_turtle(fm, mapping)
        if blok:
            blokken.append(blok)

    return blokken


def schrijf_turtle(output_pad: Path, blokken: list[str]) -> None:
    output_pad.parent.mkdir(parents=True, exist_ok=True)
    with output_pad.open("w", encoding="utf-8") as f:
        f.write("# Gegenereerd door tools/export_rdf.py\n")
        f.write("# SKOS-compatibele export van begrippen-vault\n\n")
        f.write(PREFIXES)
        f.write("\n")
        for blok in blokken:
            f.write(blok)
            f.write("\n\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exporteer begrippen-vault naar RDF Turtle (SKOS)."
    )
    parser.add_argument(
        "--vault-root", default=".", help="Pad naar de vault-root (default: .)"
    )
    parser.add_argument(
        "--out",
        default="graaf/begrippen.ttl",
        help="Uitvoerbestand (default: graaf/begrippen.ttl)",
    )
    args = parser.parse_args()

    vault_root = Path(args.vault_root).resolve()
    output_pad = vault_root / args.out

    mapping_pad = vault_root / "ontologie" / "skos-mapping.yaml"
    mapping: dict = {}
    if mapping_pad.exists():
        with mapping_pad.open(encoding="utf-8") as f:
            mapping = yaml.safe_load(f) or {}

    begrippen_dir = vault_root / "begrippen"
    if not begrippen_dir.exists():
        print(f"Fout: begrippen-map niet gevonden: {begrippen_dir}", file=sys.stderr)
        return 1

    blokken = exporteer_begrippen(vault_root, mapping)
    schrijf_turtle(output_pad, blokken)

    print(f"RDF Turtle gegenereerd: {output_pad}")
    print(f"  Begrippen: {len(blokken)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
