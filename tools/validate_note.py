#!/usr/bin/env python3
"""
validate_note.py — Vault-validatie voor juridisch kennissysteem
Laag 1: JSON Schema-validatie
Laag 2: Integriteitsvalidatie (--full of --integrity)
Laag 3: Kwaliteitswaarschuwingen
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import frontmatter
import jsonschema
import yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json_schema(schema_dir: Path, schema_name: str) -> dict:
    """Laad JSON Schema uit schemas/{schema_name}.schema.json."""
    path = schema_dir / f"{schema_name}.schema.json"
    if not path.exists():
        raise FileNotFoundError(f"Schema niet gevonden: {path}")
    with path.open() as f:
        return json.load(f)


def load_md_frontmatter(filepath: Path) -> dict:
    """Laad YAML-frontmatter uit een Markdown-bestand."""
    post = frontmatter.load(str(filepath))
    return dict(post)


def load_yaml(filepath: Path) -> dict:
    """Laad puur YAML-bestand."""
    with filepath.open() as f:
        return yaml.safe_load(f)


def load_json(filepath: Path) -> dict:
    """Laad JSON-bestand."""
    with filepath.open() as f:
        return json.load(f)


def load_file(filepath: Path) -> dict:
    """Laad bestand op basis van extensie."""
    ext = filepath.suffix.lower()
    if ext == ".md":
        return load_md_frontmatter(filepath)
    elif ext in (".yaml", ".yml"):
        return load_yaml(filepath)
    elif ext == ".json":
        return load_json(filepath)
    else:
        raise ValueError(f"Onbekende extensie: {ext}")


# ---------------------------------------------------------------------------
# Begrip-index
# ---------------------------------------------------------------------------

def build_begrip_index(vault_root: Path) -> dict[str, Path]:
    """
    Bouw een index van begrip-id → bestandspad.
    Begrip-bestanden staan in begrippen/ met extensie .md of .yaml.
    De begrip-id staat in de frontmatter; als fallback is de bestandsnaam het laatste segment.
    """
    index: dict[str, Path] = {}
    begrippen_dir = vault_root / "begrippen"
    if not begrippen_dir.exists():
        return index

    for fp in begrippen_dir.glob("*.md"):
        if fp.name == "index.md":
            continue
        try:
            data = load_md_frontmatter(fp)
            stem = fp.stem  # bijv. invorderbaarheid
            # Sla op onder de bestandsnaam (slug)
            index[stem] = fp
            # Sla ook op onder het volledige begrip-id als dat aanwezig is
            # Begrip-id's in relaties zijn strings als "BWBR0004770/art9/lid1/invorderbaarheid"
            # het laatste segment is de slug; sla ook volledig id op als aanwezig
        except Exception:
            index[fp.stem] = fp

    for fp in begrippen_dir.glob("*.yaml"):
        try:
            data = load_yaml(fp)
            stem = fp.stem
            index[stem] = fp
            bid = data.get("begrip-id")
            if bid:
                # laatste segment
                slug = bid.rstrip("/").split("/")[-1]
                index[slug] = fp
                index[bid] = fp
        except Exception:
            index[fp.stem] = fp

    return index


def begrip_id_to_slug(begrip_id: str) -> str:
    """Extraheer het laatste segment van een begrip-id als slug."""
    # begrip-id kan zijn: "BWBR0004770/art9/lid1/invorderbaarheid"
    # of een Obsidian-link: "[[begrippen/invorderbaarheid]]"
    # of gewoon een slug: "invorderbaarheid"
    bid = begrip_id.strip()
    # Obsidian wiki-link
    m = re.match(r'\[\[(?:begrippen/)?([^\]|]+?)(?:\|[^\]]+)?\]\]', bid)
    if m:
        return Path(m.group(1)).stem
    # Pad-stijl
    if "/" in bid:
        return bid.rstrip("/").split("/")[-1]
    return bid


def begrip_bestaat(begrip_id: str, index: dict[str, Path]) -> bool:
    """Controleer of een begrip-id verwijst naar een bestaand begrip."""
    slug = begrip_id_to_slug(begrip_id)
    return slug in index or begrip_id in index


# ---------------------------------------------------------------------------
# Schema-detectie bij --full
# ---------------------------------------------------------------------------

def detect_schema(filepath: Path, vault_root: Path) -> Optional[str]:
    """
    Bepaal het schema-type op basis van het pad en de bestandsnaam.
    Geeft None terug als het bestand niet gevalideerd hoeft te worden.
    """
    rel = filepath.relative_to(vault_root)
    parts = rel.parts

    if parts[0] == "begrippen":
        return "begrip"

    if parts[0] == "regels":
        return "regel"

    if parts[0] == "annotaties":
        name = filepath.stem  # bijv. art9-1, art9
        # Lid-annotatie: bevat "lid" of heeft patroon art{N}-{L}
        if re.search(r'art\d+-\d+', name):
            return "annotatie-lid"
        # Alternatieven: JSON-bestanden
        if filepath.suffix == ".json":
            name_no_ext = name
            if re.search(r'art\d+-lid\d+', name_no_ext):
                return "annotatie-lid"
            if re.search(r'art\d+$', name_no_ext):
                return "annotatie-index"
        # MD-bestanden: art9.md = index, art9-1.md = lid
        if filepath.suffix == ".md":
            if re.match(r'art\d+[a-z]?$', name):
                return "annotatie-index"
            if re.match(r'art\d+[a-z]?-\d+', name):
                return "annotatie-lid"

    return None


# ---------------------------------------------------------------------------
# Validatielagen
# ---------------------------------------------------------------------------

class ValidationResult:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.errors: list[str] = []      # blokkeerfouten
        self.warnings: list[str] = []    # waarschuwingen


def validate_schema(data: dict, schema: dict, filepath: Path) -> list[str]:
    """Laag 1: JSON Schema-validatie. Verzamel alle fouten."""
    errors = []
    validator = jsonschema.Draft7Validator(schema)
    for error in sorted(validator.iter_errors(data), key=str):
        # Maak een leesbare foutboodschap
        path_str = ".".join(str(p) for p in error.path) if error.path else "root"
        msg = f"[L1] {path_str}: {error.message}"
        errors.append(msg)
    return errors


def validate_integrity_begrip(data: dict, filepath: Path, begrip_index: dict, vault_root: Path) -> list[str]:
    """Laag 2: Integriteitsvalidatie voor begrip-bestanden."""
    errors = []
    relaties = data.get("relaties", {}) or {}

    # is-een
    for bid in (relaties.get("is-een") or []):
        if not begrip_bestaat(bid, begrip_index):
            slug = begrip_id_to_slug(bid)
            errors.append(f"[L2] relaties.is-een: begrip '{slug}' niet gevonden in begrippen/")

    # heeft
    for item in (relaties.get("heeft") or []):
        bid = item.get("begrip-id", "") if isinstance(item, dict) else str(item)
        if bid and not begrip_bestaat(bid, begrip_index):
            slug = begrip_id_to_slug(bid)
            errors.append(f"[L2] relaties.heeft[].begrip-id: begrip '{slug}' niet gevonden")

    # leidt-tot
    for item in (relaties.get("leidt-tot") or []):
        bid = item.get("begrip-id", "") if isinstance(item, dict) else str(item)
        if bid and not begrip_bestaat(bid, begrip_index):
            slug = begrip_id_to_slug(bid)
            errors.append(f"[L2] relaties.leidt-tot[].begrip-id: begrip '{slug}' niet gevonden")

    # herkomst == "afgeleid" → afleidingsregel-id niet null
    herkomst = data.get("herkomst")
    ar_id = data.get("afleidingsregel-id")
    if herkomst == "afgeleid" and not ar_id:
        errors.append("[L2] herkomst is 'afgeleid' maar afleidingsregel-id is leeg/null")

    # afleidingsregel-id → regels/{id}.yaml of regels/{id}.md bestaat
    if ar_id:
        ar_slug = begrip_id_to_slug(ar_id) if "/" in ar_id else ar_id
        regels_dir = vault_root / "regels"
        found = (
            (regels_dir / f"{ar_slug}.yaml").exists()
            or (regels_dir / f"{ar_slug}.md").exists()
            or (regels_dir / f"{ar_slug}.json").exists()
        )
        if not found:
            errors.append(f"[L2] afleidingsregel-id: regel '{ar_slug}' niet gevonden in regels/")

    # Obsidian-links in afleidingsregels (MD-frontmatter formaat)
    for link in (data.get("afleidingsregels") or []):
        m = re.match(r'\[\[regels/([^\]|]+?)(?:\|[^\]]+)?\]\]', str(link))
        if m:
            ar_name = m.group(1)
            regels_dir = vault_root / "regels"
            found = (
                (regels_dir / f"{ar_name}.yaml").exists()
                or (regels_dir / f"{ar_name}.md").exists()
            )
            if not found:
                errors.append(f"[L2] afleidingsregels: regel '{ar_name}' niet gevonden in regels/")

    return errors


def validate_integrity_regel(data: dict, filepath: Path, begrip_index: dict, vault_root: Path) -> list[str]:
    """Laag 2: Integriteitsvalidatie voor regel-bestanden."""
    errors = []

    def check_begrip(bid: str, veld: str):
        if not bid:
            return
        if not begrip_bestaat(bid, begrip_index):
            slug = begrip_id_to_slug(bid)
            errors.append(f"[L2] {veld}: begrip '{slug}' niet gevonden in begrippen/")

    # invoer en uitvoer — kunnen Obsidian-links zijn
    for bid in (data.get("invoer") or []):
        check_begrip(str(bid), "invoer")
    for bid in (data.get("uitvoer") or []):
        check_begrip(str(bid), "uitvoer")

    # rechtsfeit-id
    rf_id = data.get("rechtsfeit-id")
    if rf_id:
        check_begrip(rf_id, "rechtsfeit-id")

    return errors


def validate_integrity_annotatie_lid(data: dict, filepath: Path, begrip_index: dict) -> list[str]:
    """Laag 2: Integriteitsvalidatie voor annotatie-lid-bestanden."""
    errors = []
    for rij in (data.get("annotatierijen") or []):
        bid = rij.get("begrip-id", "") if isinstance(rij, dict) else ""
        if bid and not begrip_bestaat(bid, begrip_index):
            slug = begrip_id_to_slug(bid)
            errors.append(f"[L2] annotatierijen.begrip-id: begrip '{slug}' niet gevonden")
    return errors


def validate_quality_begrip(data: dict, filepath: Path) -> list[str]:
    """Laag 3: Kwaliteitscontrole voor begrip-bestanden."""
    warnings = []

    begripsnaam = data.get("begripsnaam", "")
    definitie = data.get("definitie", "")
    if begripsnaam and definitie and begripsnaam.lower() in definitie.lower():
        warnings.append(f"[L3] definitie bevat de begripsnaam zelf — mogelijk schending substitutiebaarheidsregel")

    status = data.get("status")
    if status == "te-verrijken":
        warnings.append("[L3] status: te-verrijken — actie vereist")

    # Lege relaties (MD-formaat of YAML-formaat)
    relaties = data.get("relaties") or {}
    is_een = relaties.get("is-een") or data.get("is-een") or []
    heeft = relaties.get("heeft") or data.get("heeft") or []
    leidt_tot = relaties.get("leidt-tot") or data.get("leidt-tot") or []
    if not is_een and not heeft and not leidt_tot:
        warnings.append("[L3] alle relaties leeg (is-een, heeft, leidt-tot)")

    return warnings


def validate_quality_regel(data: dict, filepath: Path) -> list[str]:
    """Laag 3: Kwaliteitscontrole voor regel-bestanden."""
    warnings = []
    voorbeeldreeksen = data.get("voorbeeldreeksen") or []
    heeft_grensgeval_false = any(
        isinstance(v, dict) and v.get("juridisch-juist") is False
        for v in voorbeeldreeksen
    )
    if voorbeeldreeksen and not heeft_grensgeval_false:
        warnings.append("[L3] voorbeeldreeksen: geen grensgeval (juridisch-juist: false) aanwezig")
    return warnings


# ---------------------------------------------------------------------------
# Hoofd-validatiefunctie per bestand
# ---------------------------------------------------------------------------

def validate_file(
    filepath: Path,
    schema_name: str,
    schema: dict,
    begrip_index: dict,
    vault_root: Path,
    check_integrity: bool = False,
) -> ValidationResult:
    """Valideer één bestand en geef een ValidationResult terug."""
    result = ValidationResult(filepath)

    # Laad data
    try:
        data = load_file(filepath)
    except Exception as e:
        result.errors.append(f"[L0] bestand kan niet geladen worden: {e}")
        return result

    if not isinstance(data, dict) or not data:
        result.errors.append("[L0] bestand is leeg of geen object")
        return result

    # Laag 1: Schema-validatie
    # Voor MD-bestanden met Obsidian-links proberen we schema-validatie te doen
    # maar slaan we fouten over die puur door het MD-formaat komen
    schema_errors = validate_schema(data, schema, filepath)
    result.errors.extend(schema_errors)

    # Laag 2: Integriteitsvalidatie
    if check_integrity:
        if schema_name == "begrip":
            result.errors.extend(
                validate_integrity_begrip(data, filepath, begrip_index, vault_root)
            )
        elif schema_name == "regel":
            result.errors.extend(
                validate_integrity_regel(data, filepath, begrip_index, vault_root)
            )
        elif schema_name == "annotatie-lid":
            result.errors.extend(
                validate_integrity_annotatie_lid(data, filepath, begrip_index)
            )

    # Laag 3: Kwaliteitscontrole
    if schema_name == "begrip":
        result.warnings.extend(validate_quality_begrip(data, filepath))
    elif schema_name == "regel":
        result.warnings.extend(validate_quality_regel(data, filepath))

    return result


# ---------------------------------------------------------------------------
# Bestandsverzameling
# ---------------------------------------------------------------------------

def collect_files_for_schema(vault_root: Path, schema_name: str) -> list[Path]:
    """Verzamel alle bestanden die bij een schema-type horen."""
    files = []
    if schema_name == "begrip":
        d = vault_root / "begrippen"
        for ext in ("*.md", "*.yaml", "*.yml"):
            files.extend(d.glob(ext))
        files = [f for f in files if f.name != "index.md"]
    elif schema_name == "regel":
        d = vault_root / "regels"
        for ext in ("*.md", "*.yaml", "*.yml"):
            files.extend(d.glob(ext))
        files = [f for f in files if f.name != "index.md"]
    elif schema_name in ("annotatie-lid", "annotatie-index"):
        d = vault_root / "annotaties"
        for fp in d.rglob("*.md"):
            detected = detect_schema(fp, vault_root)
            if detected == schema_name:
                files.append(fp)
        for fp in d.rglob("*.json"):
            detected = detect_schema(fp, vault_root)
            if detected == schema_name:
                files.append(fp)
    return sorted(files)


def collect_all_files(vault_root: Path) -> list[tuple[Path, str]]:
    """Verzamel alle te valideren bestanden met hun schema-naam."""
    result = []
    for schema_name in ("begrip", "regel"):
        for fp in collect_files_for_schema(vault_root, schema_name):
            result.append((fp, schema_name))
    # annotaties
    annotaties_dir = vault_root / "annotaties"
    if annotaties_dir.exists():
        for fp in sorted(annotaties_dir.rglob("*.md")):
            detected = detect_schema(fp, vault_root)
            if detected in ("annotatie-lid", "annotatie-index"):
                result.append((fp, detected))
        for fp in sorted(annotaties_dir.rglob("*.json")):
            detected = detect_schema(fp, vault_root)
            if detected in ("annotatie-lid", "annotatie-index"):
                result.append((fp, detected))
    return result


# ---------------------------------------------------------------------------
# Rapport-output
# ---------------------------------------------------------------------------

def format_rapport_text(
    results: list[ValidationResult],
    vault_root: Path,
    today: str,
) -> str:
    """Formateer tekstueel validatierapport."""
    errors_by_file = [(r, r.errors) for r in results if r.errors]
    warnings_by_file = [(r, r.warnings) for r in results if r.warnings]
    geslaagd = sum(1 for r in results if not r.errors)
    totaal_fouten = sum(len(r.errors) for r in results)
    totaal_waarschuwingen = sum(len(r.warnings) for r in results)

    lines = [
        f"Validatierapport — {today}",
        "══════════════════════════════",
        "",
    ]

    if errors_by_file:
        lines.append("BLOKKEERFOUTEN (moeten 0 zijn voor productie)")
        for r, errs in errors_by_file:
            try:
                rel = r.filepath.relative_to(vault_root)
            except ValueError:
                rel = r.filepath
            lines.append(f"  {rel}")
            for e in errs:
                lines.append(f"    {e}")
        lines.append("")
    else:
        lines.append("BLOKKEERFOUTEN")
        lines.append("  (geen)")
        lines.append("")

    if warnings_by_file:
        lines.append("WAARSCHUWINGEN")
        for r, warns in warnings_by_file:
            try:
                rel = r.filepath.relative_to(vault_root)
            except ValueError:
                rel = r.filepath
            lines.append(f"  {rel}")
            for w in warns:
                lines.append(f"    {w}")
        lines.append("")
    else:
        lines.append("WAARSCHUWINGEN")
        lines.append("  (geen)")
        lines.append("")

    lines.append(f"GESLAAGD: {geslaagd} bestanden")
    lines.append(f"BLOKKEERFOUTEN: {totaal_fouten}")
    lines.append(f"WAARSCHUWINGEN: {totaal_waarschuwingen}")
    return "\n".join(lines)


def format_rapport_json(results: list[ValidationResult], vault_root: Path) -> dict:
    """Formateer JSON-validatierapport."""
    fouten = []
    waarschuwingen = []
    geslaagd = 0

    for r in results:
        try:
            rel = str(r.filepath.relative_to(vault_root))
        except ValueError:
            rel = str(r.filepath)
        for e in r.errors:
            fouten.append({"bestand": rel, "boodschap": e})
        for w in r.warnings:
            waarschuwingen.append({"bestand": rel, "boodschap": w})
        if not r.errors:
            geslaagd += 1

    return {"fouten": fouten, "waarschuwingen": waarschuwingen, "geslaagd": geslaagd}


def schrijf_md_rapport(rapport_tekst: str, vault_root: Path):
    """Schrijf validatierapport naar rapporten/validatie-rapport.md."""
    rapporten_dir = vault_root / "rapporten"
    rapporten_dir.mkdir(exist_ok=True)
    rapport_path = rapporten_dir / "validatie-rapport.md"
    rapport_path.write_text(f"# Validatierapport\n\n```\n{rapport_tekst}\n```\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Valideer vault-bestanden tegen JSON Schemas"
    )
    parser.add_argument("--vault-root", default=".", help="Pad naar vault-root")
    parser.add_argument("--file", help="Valideer één bestand")
    parser.add_argument("--dir", help="Valideer alle bestanden in een directory")
    parser.add_argument("--schema", help="Schema-naam (begrip, annotatie-lid, annotatie-index, regel)")
    parser.add_argument("--full", action="store_true", help="Volledige vault-validatie")
    parser.add_argument("--integrity", action="store_true", help="Voeg integriteitsvalidatie toe")
    parser.add_argument("--json", action="store_true", dest="json_output", help="JSON-output")
    args = parser.parse_args()

    vault_root = Path(args.vault_root).resolve()
    schema_dir = vault_root / "schemas"
    today = date.today().isoformat()
    check_integrity = args.full or args.integrity

    # Bouw begrip-index
    begrip_index = build_begrip_index(vault_root)

    # Verzamel te valideren bestanden
    to_validate: list[tuple[Path, str]] = []

    if args.full:
        to_validate = collect_all_files(vault_root)
    elif args.file:
        fp = Path(args.file)
        if not fp.is_absolute():
            fp = vault_root / fp
        if not fp.exists():
            print(f"FOUT: bestand niet gevonden: {fp}", file=sys.stderr)
            sys.exit(1)
        schema_name = args.schema
        if not schema_name:
            schema_name = detect_schema(fp, vault_root)
        if not schema_name:
            print(f"FOUT: kan schema niet detecteren voor {fp}. Geef --schema op.", file=sys.stderr)
            sys.exit(1)
        to_validate = [(fp, schema_name)]
    elif args.dir:
        dp = Path(args.dir)
        if not dp.is_absolute():
            dp = vault_root / dp
        schema_name = args.schema
        if not schema_name:
            print("FOUT: --schema vereist bij --dir", file=sys.stderr)
            sys.exit(1)
        for fp in sorted(dp.rglob("*.md")) + sorted(dp.rglob("*.yaml")) + sorted(dp.rglob("*.json")):
            if fp.name == "index.md":
                continue
            to_validate.append((fp, schema_name))
    else:
        parser.print_help()
        sys.exit(0)

    if not to_validate:
        print("Geen bestanden gevonden om te valideren.")
        sys.exit(0)

    # Laad schema's (cache per naam)
    schema_cache: dict[str, dict] = {}

    results: list[ValidationResult] = []
    for filepath, schema_name in to_validate:
        if schema_name not in schema_cache:
            try:
                schema_cache[schema_name] = load_json_schema(schema_dir, schema_name)
            except FileNotFoundError as e:
                print(f"FOUT: {e}", file=sys.stderr)
                sys.exit(1)
        schema = schema_cache[schema_name]
        result = validate_file(
            filepath=filepath,
            schema_name=schema_name,
            schema=schema,
            begrip_index=begrip_index,
            vault_root=vault_root,
            check_integrity=check_integrity,
        )
        results.append(result)

    # Output
    if args.json_output:
        print(json.dumps(format_rapport_json(results, vault_root), ensure_ascii=False, indent=2))
    else:
        rapport_tekst = format_rapport_text(results, vault_root, today)
        print(rapport_tekst)
        if args.full:
            schrijf_md_rapport(rapport_tekst, vault_root)
            print(f"\nRapport geschreven naar: rapporten/validatie-rapport.md")

    # Exit code
    heeft_fouten = any(r.errors for r in results)
    sys.exit(1 if heeft_fouten else 0)


if __name__ == "__main__":
    main()
