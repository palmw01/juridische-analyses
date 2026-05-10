#!/usr/bin/env python3
"""
export_rdf.py — Exporteer begrippen-vault naar RDF Turtle (SKOS-compatibel).

Leest begrippen/*.yaml en genereert kennisgraaf/begrippen.ttl. Geen rdflib
nodig — Turtle wordt als tekst gegenereerd.

Gebruik:
    cd vault-root/
    tools/.venv/bin/python tools/export_rdf.py [--vault-root .] [--out kennisgraaf/begrippen.ttl]
"""

import argparse
import sys
from pathlib import Path

import yaml

from jas_index_lib import bouw_jas_index


# ---------------------------------------------------------------------------
# Turtle-hulpfuncties
# ---------------------------------------------------------------------------

def turtle_literal(waarde: str, lang: str = "nl") -> str:
    escaped = waarde.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"@{lang}'


def slug_van_id(begrip_id: str) -> str:
    return begrip_id.replace("/", "_")


# ---------------------------------------------------------------------------
# Prefixes en header
# ---------------------------------------------------------------------------

PREFIXES = """@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix jas:  <http://regels.overheid.nl/jas/ontology#> .
@prefix dct:  <http://purl.org/dc/terms/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix begrip: <urn:jas:begrip:> .
@prefix regel: <urn:jas:regel:> .
"""


# ---------------------------------------------------------------------------
# Begrip → Turtle-blok
# ---------------------------------------------------------------------------

def begrip_naar_turtle(fm: dict, jas_index: dict[str, str]) -> str:
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
    markeringen: list[dict] = fm.get("markeringen") or []

    if begripsnaam:
        lines.append(f"    skos:prefLabel {turtle_literal(begripsnaam)} ;")

    for alias in aliases:
        if alias:
            lines.append(f"    skos:altLabel {turtle_literal(str(alias))} ;")

    if definitie:
        lines.append(f"    skos:definition {turtle_literal(definitie)} ;")

    if geldigheid_van:
        lines.append(f'    dct:valid "{geldigheid_van}"^^xsd:date ;')

    # Alle markeringen als provenance-bron
    bronnen_gezien: set[str] = set()
    for m in markeringen:
        bron = m.get("bron-annotatie-id", "")
        if bron and bron not in bronnen_gezien:
            bronnen_gezien.add(bron)
            bron_escaped = bron.replace('"', '\\"')
            lines.append(f'    prov:wasDerivedFrom "{bron_escaped}" ;')

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
    jas_klasse = jas_index.get(begrip_id, "")
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

def exporteer_begrippen(vault_root: Path, jas_index: dict[str, str]) -> list[str]:
    begrippen_dir = vault_root / "begrippen"
    blokken: list[str] = []

    for yaml_file in sorted(begrippen_dir.glob("*.yaml")):
        with yaml_file.open(encoding="utf-8") as f:
            fm = yaml.safe_load(f)
        if not fm or not isinstance(fm, dict):
            continue
        blok = begrip_naar_turtle(fm, jas_index)
        if blok:
            blokken.append(blok)

    return blokken


# ---------------------------------------------------------------------------
# Regel → Turtle-blok
# ---------------------------------------------------------------------------

def regel_naar_turtle(fm: dict) -> str:
    regel_id = fm.get("regel-id", "")
    if not regel_id:
        return ""
    slug = regel_id.replace("/", "_").replace("-", "_")
    lines: list[str] = [f"regel:{slug}"]
    lines.append("    a jas:Afleidingsregel ;")
    naam = fm.get("naam") or ""
    soort = fm.get("soort") or ""
    bwb_id = fm.get("bwb-id") or ""
    if naam:
        lines.append(f"    skos:prefLabel {turtle_literal(naam)} ;")
    if soort:
        lines.append(f'    jas:regeltype "{soort}" ;')
    if bwb_id:
        lines.append(f'    dct:source "{bwb_id}" ;')
    for invoer_id in (fm.get("invoer") or []):
        if invoer_id:
            lines.append(f"    jas:gebruikt begrip:{slug_van_id(invoer_id)} ;")
    for uitvoer_id in (fm.get("uitvoer") or []):
        if uitvoer_id:
            lines.append(f"    jas:bepaalt begrip:{slug_van_id(uitvoer_id)} ;")
    toelichting = fm.get("toelichting") or ""
    if toelichting:
        lines.append(f"    rdfs:comment {turtle_literal(toelichting[:200])} ;")
    if lines[-1].endswith(" ;"):
        lines[-1] = lines[-1][:-2] + " ."
    else:
        lines.append("    .")
    return "\n".join(lines)


def exporteer_regels(vault_root: Path) -> list[str]:
    regels_dir = vault_root / "regels"
    blokken: list[str] = []
    if not regels_dir.exists():
        return blokken
    for yaml_file in sorted(regels_dir.glob("*.yaml")):
        with yaml_file.open(encoding="utf-8") as f:
            fm = yaml.safe_load(f)
        if not fm or not isinstance(fm, dict):
            continue
        blok = regel_naar_turtle(fm)
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
        description="Exporteer begrippen + regels naar RDF Turtle (SKOS)."
    )
    parser.add_argument(
        "--vault-root", default=".", help="Pad naar de vault-root (default: .)"
    )
    parser.add_argument(
        "--out",
        default="kennisgraaf/begrippen.ttl",
        help="Uitvoerbestand (default: kennisgraaf/begrippen.ttl)",
    )
    args = parser.parse_args()

    vault_root = Path(args.vault_root).resolve()
    output_pad = vault_root / args.out

    begrippen_dir = vault_root / "begrippen"
    if not begrippen_dir.exists():
        print(f"Fout: begrippen-map niet gevonden: {begrippen_dir}", file=sys.stderr)
        return 1

    jas_index = bouw_jas_index(vault_root)
    blokken = exporteer_begrippen(vault_root, jas_index)
    blokken.extend(exporteer_regels(vault_root))
    schrijf_turtle(output_pad, blokken)

    print(f"RDF Turtle gegenereerd: {output_pad}")
    print(f"  Begrippen: {len([b for b in blokken if 'a skos:Concept' in b])}")
    print(f"  Regels: {len([b for b in blokken if 'a jas:Afleidingsregel' in b])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
