#!/usr/bin/env python3
"""
validate_note.py — Projectvalidatie voor juridisch kennissysteem
Laag 1: JSON Schema-validatie
Laag 2: Integriteitsvalidatie (--full of --integrity)
Laag 3: Kwaliteitswaarschuwingen
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import frontmatter
import jsonschema
import yaml

sys.path.insert(0, str(Path(__file__).parent))
from jas_index_lib import haal_kern, haal_contexten


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

def build_begrip_index(project_root: Path) -> dict[str, Path]:
    """
    Bouw een index van begrip-id → bestandspad.
    Begrip-bestanden staan in begrippen/ met extensie .md of .yaml.
    De begrip-id staat in de frontmatter; als fallback is de bestandsnaam het laatste segment.
    """
    index: dict[str, Path] = {}
    begrippen_dir = project_root / "begrippen"
    if not begrippen_dir.exists():
        return index

    for fp in begrippen_dir.glob("*.md"):
        if fp.name == "index.md":
            continue
        try:
            data = load_md_frontmatter(fp)
            index[fp.stem] = fp
        except Exception as e:
            print(f"[W] begrip overgeslagen (parse-fout): {fp.name}: {e}", file=sys.stderr)

    for fp in begrippen_dir.glob("*.yaml"):
        try:
            data = load_yaml(fp)
            stem = fp.stem
            index[stem] = fp
            bid = data.get("begrip-id")
            if bid:
                slug = bid.rstrip("/").split("/")[-1]
                index[slug] = fp
                index[bid] = fp
        except Exception as e:
            print(f"[W] begrip overgeslagen (parse-fout): {fp.name}: {e}", file=sys.stderr)

    return index


def begrip_id_to_slug(begrip_id: str) -> str:
    """Extraheer het laatste segment van een begrip-id als slug. Wikilinks zijn niet toegestaan."""
    bid = begrip_id.strip()
    if bid.startswith("[["):
        return ""
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

def detect_schema(filepath: Path, project_root: Path) -> Optional[str]:
    """
    Bepaal het schema-type op basis van het pad en de bestandsnaam.
    Geeft None terug als het bestand niet gevalideerd hoeft te worden.
    """
    rel = filepath.relative_to(project_root)
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
            if re.search(r'par\d+-\d+', name_no_ext):
                return "annotatie-lid"
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


ONVERENIGBARE_JAS_PAREN: set[frozenset] = {
    frozenset({"rechtsfeit", "tijdsaanduiding"}),
    frozenset({"rechtsfeit", "parameter"}),
    frozenset({"rechtsbetrekking", "variabele"}),
    frozenset({"afleidingsregel", "brondefinitie"}),
    frozenset({"delegatiebevoegdheid", "variabele"}),
}


def validate_integrity_begrip(data: dict, filepath: Path, begrip_index: dict, project_root: Path) -> list[str]:
    """Laag 2: Integriteitsvalidatie voor begrip-bestanden."""
    errors = []

    # Wikilink-detectie: markeringen mogen geen wikilink-formaat gebruiken
    markeringen: list[dict] = data.get("markeringen") or []
    for m in markeringen:
        ann_id = str(m.get("bron-annotatie-id") or "")
        if ann_id.startswith("[["):
            errors.append(
                f"[L2] markeringen[].bron-annotatie-id: gebruik geen wikilink-formaat — "
                f"verwacht pad-notatie bijv. 'BWBR0004770/art9/lid1'"
            )

    # Homoniem-detectie: onverenigbare JAS-klassen in dezelfde begrip-definitie
    jas_klassen = {m.get("jas-klasse") for m in markeringen if m.get("jas-klasse")}
    for paar in ONVERENIGBARE_JAS_PAREN:
        if paar.issubset(jas_klassen):
            errors.append(
                f"[L2] homoniem-conflict: markeringen bevatten onverenigbare JAS-klassen "
                f"{sorted(paar)} — mogelijk zijn dit twee verschillende begrippen"
            )

    # bron-annotatie-id → annotaties/ integriteitscheck via annotatie-id veld
    annotatie_ids = build_annotatie_index(project_root)
    for m in markeringen:
        ann_id = str(m.get("bron-annotatie-id") or "")
        if not ann_id or ann_id.startswith("[["):
            continue
        if annotatie_ids and ann_id not in annotatie_ids:
            errors.append(
                f"[L2] markeringen[].bron-annotatie-id: '{ann_id}' niet gevonden "
                f"als annotatie-id in annotaties/"
            )

    # Definitie-contexten: markering-id's moeten bestaan in markeringen[]
    markering_ids = {m.get("markering-id") for m in markeringen if m.get("markering-id")}
    definitie_obj = data.get("definitie") or {}
    contexten = haal_contexten(definitie_obj)
    for i, ctx in enumerate(contexten):
        ctx_mid = ctx.get("markering-id", "")
        if ctx_mid and ctx_mid not in markering_ids:
            errors.append(
                f"[L2] definitie.contexten[{i}].markering-id '{ctx_mid}' "
                f"verwijst naar een niet-bestaande markering in markeringen[]"
            )

    # definitie-gebaseerd-op: markering-id's moeten bestaan én bijdrage 'primair' hebben
    mark_bijdrage = {m.get("markering-id"): m.get("bijdrage") for m in (data.get("markeringen") or [])}
    def_gebaseerd_op: list[str] = data.get("definitie-gebaseerd-op") or []
    for mid in def_gebaseerd_op:
        if not mid:
            continue
        if mid not in markering_ids:
            errors.append(
                f"[L2] definitie-gebaseerd-op: markering-id '{mid}' "
                f"niet gevonden in markeringen[]"
            )
        elif mark_bijdrage.get(mid) not in ("primair", None):
            bijdrage_val = mark_bijdrage.get(mid)
            errors.append(
                f"[L2] definitie-gebaseerd-op: markering '{mid}' heeft bijdrage '{bijdrage_val}' "
                f"— alleen bijdrage 'primair' is toegestaan in definitie-gebaseerd-op"
            )

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

    # status == "gevalideerd" → definitie.kern niet leeg
    status = data.get("status")
    definitie_kern = haal_kern(definitie_obj)
    if status == "gevalideerd" and not definitie_kern:
        errors.append(
            "[L2] status is 'gevalideerd' maar definitie.kern is leeg — vul kern in vóór validatie"
        )

    # status == "vervallen" → vervangen-door niet null
    if status == "vervallen" and data.get("vervangen-door") is None:
        errors.append(
            "[L2] status is 'vervallen' maar vervangen-door is null — vermeld het opvolger-begrip-id"
        )

    # herkomst + jas-klasse → juist id-veld verplicht
    herkomst = data.get("herkomst")
    jas_klasse = data.get("jas-klasse")
    ar_id = data.get("afleidingsregel-id")
    uitvoer_id = data.get("uitvoer-van-regel-id")

    if herkomst == "afgeleid":
        if jas_klasse == "afleidingsregel":
            if not ar_id:
                errors.append(
                    "[L2] herkomst=afgeleid + jas-klasse=afleidingsregel vereist afleidingsregel-id"
                )
        else:
            if not uitvoer_id:
                errors.append(
                    "[L2] herkomst=afgeleid vereist uitvoer-van-regel-id "
                    "(afleidingsregel-id is voorbehouden aan jas-klasse: afleidingsregel)"
                )

    # afleidingsregel-id mag alleen op jas-klasse: afleidingsregel
    if ar_id and jas_klasse != "afleidingsregel":
        errors.append(
            f"[L2] afleidingsregel-id mag alleen bij jas-klasse: afleidingsregel; "
            f"gebruik uitvoer-van-regel-id voor jas-klasse: {jas_klasse}"
        )

    # integriteitscheck afleidingsregel-id
    if ar_id:
        ar_slug = begrip_id_to_slug(ar_id) if "/" in ar_id else ar_id
        regels_dir = project_root / "regels"
        found = (
            (regels_dir / f"{ar_slug}.yaml").exists()
            or (regels_dir / f"{ar_slug}.md").exists()
            or (regels_dir / f"{ar_slug}.json").exists()
        )
        if not found:
            errors.append(f"[L2] afleidingsregel-id: regel '{ar_slug}' niet gevonden in regels/")

    # integriteitscheck uitvoer-van-regel-id
    if uitvoer_id:
        uitvoer_slug = begrip_id_to_slug(uitvoer_id) if "/" in uitvoer_id else uitvoer_id
        regels_dir = project_root / "regels"
        found = (
            (regels_dir / f"{uitvoer_slug}.yaml").exists()
            or (regels_dir / f"{uitvoer_slug}.md").exists()
            or (regels_dir / f"{uitvoer_slug}.json").exists()
        )
        if not found:
            errors.append(
                f"[L2] uitvoer-van-regel-id: regel '{uitvoer_slug}' niet gevonden in regels/"
            )

    return errors


def build_annotatie_index(project_root: Path) -> set[str]:
    """Bouw een set van bekende annotatie-id's uit de annotaties/-map."""
    ids: set[str] = set()
    annotaties_dir = project_root / "annotaties"
    if not annotaties_dir.exists():
        return ids
    for fp in annotaties_dir.rglob("*.json"):
        try:
            data = load_json(fp)
            aid = data.get("annotatie-id")
            if aid:
                ids.add(str(aid))
        except Exception:
            pass
    return ids


def validate_integrity_regel(data: dict, filepath: Path, begrip_index: dict, project_root: Path) -> list[str]:
    """Laag 2: Integriteitsvalidatie voor regel-bestanden."""
    errors = []

    def check_begrip(bid: str, veld: str):
        if not bid:
            return
        if bid.startswith("[["):
            errors.append(
                f"[L2] {veld}: gebruik geen wikilink-formaat — "
                f"verwacht pad-notatie bijv. 'BWBR0004770/art9/lid1/begrip'"
            )
            return
        if not begrip_bestaat(bid, begrip_index):
            slug = begrip_id_to_slug(bid)
            errors.append(f"[L2] {veld}: begrip '{slug}' niet gevonden in begrippen/")

    for bid in (data.get("invoer") or []):
        check_begrip(str(bid), "invoer")
    for bid in (data.get("uitvoer") or []):
        check_begrip(str(bid), "uitvoer")

    # rechtsfeit-id
    rf_id = data.get("rechtsfeit-id")
    if rf_id:
        check_begrip(rf_id, "rechtsfeit-id")

    # vervangt-regel-id: moet verwijzen naar bestaand regel-bestand
    vervangt = data.get("vervangt-regel-id")
    if vervangt:
        regels_dir = project_root / "regels"
        if not (regels_dir / f"{vervangt}.yaml").exists():
            errors.append(f"[L2] vervangt-regel-id: regel '{vervangt}' niet gevonden in regels/")

    # annotatie-id: mag geen Obsidian-link zijn en moet verwijzen naar bestaande annotatie
    ann_id = data.get("annotatie-id")
    if ann_id:
        ann_id_str = str(ann_id)
        if ann_id_str.startswith("[["):
            errors.append(
                f"[L2] annotatie-id: gebruik geen Obsidian-link-format — "
                f"verwacht bijv. 'BWBR0004770/art9/lid1', niet '[[annotaties/...]]'"
            )
        else:
            annotatie_index = build_annotatie_index(project_root)
            if annotatie_index and ann_id_str not in annotatie_index:
                errors.append(
                    f"[L2] annotatie-id: '{ann_id_str}' niet gevonden in annotaties/"
                )

    return errors


def validate_integrity_annotatie_lid(data: dict, filepath: Path, begrip_index: dict) -> list[str]:
    """Laag 2: Integriteitsvalidatie voor annotatie-lid-bestanden."""
    errors = []
    for rij in (data.get("annotatierijen") or []):
        bid = rij.get("begrip-id", "") if isinstance(rij, dict) else ""
        if bid and not begrip_bestaat(bid, begrip_index):
            slug = begrip_id_to_slug(bid)
            errors.append(f"[L2] annotatierijen.begrip-id: begrip '{slug}' niet gevonden")

    # Diagram: kanten.van/naar moeten verwijzen naar bestaande knoop-id's
    diagram = data.get("diagram") or {}
    knopen = diagram.get("knopen") or []
    kanten = diagram.get("kanten") or []
    knoop_ids = {k.get("id") for k in knopen if isinstance(k, dict) and k.get("id")}
    for i, kant in enumerate(kanten):
        if not isinstance(kant, dict):
            continue
        for richting in ("van", "naar"):
            ref = kant.get(richting)
            if ref and ref not in knoop_ids:
                errors.append(
                    f"[L2] diagram.kanten[{i}].{richting}: knoop-id '{ref}' niet gevonden in diagram.knopen"
                )

    return errors


def validate_quality_begrip(data: dict, filepath: Path) -> list[str]:
    """Laag 3: Kwaliteitscontrole voor begrip-bestanden."""
    warnings = []

    begripsnaam = data.get("begripsnaam", "")
    definitie_obj = data.get("definitie") or {}
    kern = haal_kern(definitie_obj)
    contexten = haal_contexten(definitie_obj)

    # Kern bevat de begripsnaam zelf (substitutietest)
    if begripsnaam and kern and begripsnaam.lower() in kern.lower():
        warnings.append("[L3] definitie.kern bevat de begripsnaam zelf — mogelijk schending substitutiebaarheidsregel")

    # Kern eindigt op een punt (conventies-check)
    if kern and kern.rstrip().endswith("."):
        warnings.append("[L3] definitie.kern eindigt op een punt — conventie: geen punt aan het einde")

    # Kern leeg (stub — nog niet door /begrip ingevuld)
    if not kern:
        warnings.append("[L3] definitie.kern is leeg — gebruik /begrip om de kern in te vullen")

    # Kern ontbreekt maar contexten zijn aanwezig
    if not kern and contexten:
        warnings.append("[L3] definitie.kern is leeg maar definitie.contexten[] bevat items — kern invullen vóór contexten")

    # Aanvullende markeringen zonder context-documentatie
    markeringen: list[dict] = data.get("markeringen") or []
    context_mids = {ctx.get("markering-id") for ctx in contexten}
    aanvullende_mids = {
        m.get("markering-id") for m in markeringen
        if m.get("bijdrage") == "aanvullend" and m.get("markering-id")
    }
    ongedocumenteerd = aanvullende_mids - context_mids
    if ongedocumenteerd:
        warnings.append(
            f"[L3] markering(en) met bijdrage 'aanvullend' hebben geen context-entry in definitie.contexten: "
            f"{', '.join(sorted(ongedocumenteerd))} — overweeg een uitbreiding- of verfijning-context toe te voegen"
        )

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

    # Onbevestigde markeringen
    markeringen = data.get("markeringen") or []
    if markeringen and all(not m.get("bevestigd", False) for m in markeringen):
        warnings.append("[L3] alle markeringen onbevestigd — A4-validatie nog niet uitgevoerd")

    # Kern ingevuld maar voorbeelden ontbreken
    if kern and not (data.get("voorbeelden") or []):
        warnings.append(
            "[L3] definitie.kern is ingevuld maar voorbeelden ontbreken — "
            "voeg minimaal 2 stellingen toe (waarvan 1 grensgeval)"
        )

    return warnings


def validate_quality_annotatie_lid(data: dict, filepath: Path) -> list[str]:
    """Laag 3: Kwaliteitscontrole voor annotatie-lid bestanden."""
    warnings = []
    rijen = data.get("annotatierijen") or []
    if not rijen:
        warnings.append("[L3] annotatierijen leeg — geen markeringen vastgelegd")
    diagram = data.get("diagram") or {}
    knopen = diagram.get("knopen") or []
    kanten = diagram.get("kanten") or []
    if not knopen and not kanten:
        warnings.append("[L3] diagram ontbreekt of is leeg (geen knopen/kanten)")
    elif knopen and not kanten:
        warnings.append("[L3] diagram heeft knopen maar geen kanten (geen relaties)")

    # Par-based annotatie zonder sectie
    annotatie_id = data.get("annotatie-id", "")
    if "/par" in annotatie_id and not (data.get("sectie") or "").strip():
        warnings.append(
            "[L3] annotatie-id is een paragraaf-bron maar sectie-veld is leeg — "
            "vul sectie in (bijv. '9.1')"
        )

    return warnings


def validate_quality_annotatie_index(data: dict, filepath: Path) -> list[str]:
    """Laag 3: Kwaliteitscontrole voor annotatie-index bestanden."""
    warnings = []
    leden = data.get("leden-annotaties") or []
    if not leden:
        warnings.append("[L3] leden-annotaties leeg — geen lid-annotaties geregistreerd")
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

    # prioriteit mag alleen bij Specialisatieregel
    prioriteit = data.get("prioriteit")
    soort = data.get("soort", "")
    if prioriteit is not None and soort != "Specialisatieregel":
        warnings.append(
            f"[L3] prioriteit is ingevuld ({prioriteit}) maar soort is '{soort}' — "
            f"prioriteit is alleen zinvol bij Specialisatieregels"
        )

    # Specialisatieregel vereist prioriteit
    if soort == "Specialisatieregel" and prioriteit is None:
        warnings.append(
            "[L3] soort is 'Specialisatieregel' maar prioriteit is niet ingevuld — "
            "stel prioriteit in (lager getal = hogere prioriteit)"
        )

    # Specialisatieregel vereist gespecialiseerd-regel-id
    if soort == "Specialisatieregel" and not data.get("gespecialiseerd-regel-id"):
        warnings.append(
            "[L3] soort is 'Specialisatieregel' maar gespecialiseerd-regel-id is niet ingevuld — "
            "stel gespecialiseerd-regel-id in op de regel-id van de hoofdregel"
        )

    return warnings


# ---------------------------------------------------------------------------
# Hoofd-validatiefunctie per bestand
# ---------------------------------------------------------------------------

def validate_file(
    filepath: Path,
    schema_name: str,
    schema: dict,
    begrip_index: dict,
    project_root: Path,
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
    schema_errors = validate_schema(data, schema, filepath)
    result.errors.extend(schema_errors)

    # Laag 2: Integriteitsvalidatie
    if check_integrity:
        if schema_name == "begrip":
            result.errors.extend(
                validate_integrity_begrip(data, filepath, begrip_index, project_root)
            )
        elif schema_name == "regel":
            result.errors.extend(
                validate_integrity_regel(data, filepath, begrip_index, project_root)
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
    elif schema_name == "annotatie-lid":
        result.warnings.extend(validate_quality_annotatie_lid(data, filepath))
    elif schema_name == "annotatie-index":
        result.warnings.extend(validate_quality_annotatie_index(data, filepath))

    return result


# ---------------------------------------------------------------------------
# Bestandsverzameling
# ---------------------------------------------------------------------------

def collect_files_for_schema(project_root: Path, schema_name: str) -> list[Path]:
    """Verzamel alle bestanden die bij een schema-type horen."""
    files = []
    if schema_name == "begrip":
        d = project_root / "begrippen"
        for ext in ("*.md", "*.yaml", "*.yml"):
            files.extend(d.glob(ext))
        files = [f for f in files if f.name != "index.md"]
    elif schema_name == "regel":
        d = project_root / "regels"
        for ext in ("*.md", "*.yaml", "*.yml"):
            files.extend(d.glob(ext))
        files = [f for f in files if f.name != "index.md"]
    elif schema_name in ("annotatie-lid", "annotatie-index"):
        d = project_root / "annotaties"
        for fp in d.rglob("*.md"):
            detected = detect_schema(fp, project_root)
            if detected == schema_name:
                files.append(fp)
        for fp in d.rglob("*.json"):
            detected = detect_schema(fp, project_root)
            if detected == schema_name:
                files.append(fp)
    return sorted(files)


def collect_all_files(project_root: Path) -> list[tuple[Path, str]]:
    """Verzamel alle te valideren bestanden met hun schema-naam."""
    result = []
    for schema_name in ("begrip", "regel"):
        for fp in collect_files_for_schema(project_root, schema_name):
            result.append((fp, schema_name))
    # annotaties
    annotaties_dir = project_root / "annotaties"
    if annotaties_dir.exists():
        for fp in sorted(annotaties_dir.rglob("*.md")):
            detected = detect_schema(fp, project_root)
            if detected in ("annotatie-lid", "annotatie-index"):
                result.append((fp, detected))
        for fp in sorted(annotaties_dir.rglob("*.json")):
            detected = detect_schema(fp, project_root)
            if detected in ("annotatie-lid", "annotatie-index"):
                result.append((fp, detected))
    return result


# ---------------------------------------------------------------------------
# Rapport-output
# ---------------------------------------------------------------------------

def format_rapport_text(
    results: list[ValidationResult],
    project_root: Path,
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
                rel = r.filepath.relative_to(project_root)
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
                rel = r.filepath.relative_to(project_root)
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


def format_rapport_json(results: list[ValidationResult], project_root: Path) -> dict:
    """Formateer JSON-validatierapport."""
    fouten = []
    waarschuwingen = []
    geslaagd = 0

    for r in results:
        try:
            rel = str(r.filepath.relative_to(project_root))
        except ValueError:
            rel = str(r.filepath)
        for e in r.errors:
            fouten.append({"bestand": rel, "boodschap": e})
        for w in r.warnings:
            waarschuwingen.append({"bestand": rel, "boodschap": w})
        if not r.errors:
            geslaagd += 1

    return {"fouten": fouten, "waarschuwingen": waarschuwingen, "geslaagd": geslaagd}


def schrijf_md_rapport(rapport_tekst: str, project_root: Path):
    """Schrijf validatierapport naar rapporten/validatie-rapport.md."""
    rapporten_dir = project_root / "rapporten"
    rapporten_dir.mkdir(exist_ok=True)
    rapport_path = rapporten_dir / "validatie-rapport.md"
    rapport_path.write_text(f"# Validatierapport\n\n```\n{rapport_tekst}\n```\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Valideer projectbestanden tegen JSON Schemas"
    )
    parser.add_argument("--project-dir", default=".", help="Pad naar project-root")
    parser.add_argument("--file", help="Valideer één bestand")
    parser.add_argument("--dir", help="Valideer alle bestanden in een directory")
    parser.add_argument("--schema", help="Schema-naam (begrip, annotatie-lid, annotatie-index, regel)")
    parser.add_argument("--full", action="store_true", help="Volledige projectvalidatie")
    parser.add_argument("--integrity", action="store_true", help="Voeg integriteitsvalidatie toe")
    parser.add_argument("--json", action="store_true", dest="json_output", help="JSON-output")
    args = parser.parse_args()

    project_root = Path(args.project_dir).resolve()
    schema_dir = project_root / "schemas"
    today = date.today().isoformat()
    check_integrity = args.full or args.integrity

    # Bouw begrip-index
    begrip_index = build_begrip_index(project_root)

    # Verzamel te valideren bestanden
    to_validate: list[tuple[Path, str]] = []

    if args.full:
        to_validate = collect_all_files(project_root)
    elif args.file:
        fp = Path(args.file)
        if not fp.is_absolute():
            fp = project_root / fp
        if not fp.exists():
            print(f"FOUT: bestand niet gevonden: {fp}", file=sys.stderr)
            sys.exit(1)
        schema_name = args.schema
        if not schema_name:
            schema_name = detect_schema(fp, project_root)
        if not schema_name:
            print(f"FOUT: kan schema niet detecteren voor {fp}. Geef --schema op.", file=sys.stderr)
            sys.exit(1)
        to_validate = [(fp, schema_name)]
    elif args.dir:
        dp = Path(args.dir)
        if not dp.is_absolute():
            dp = project_root / dp
        for fp in sorted(dp.rglob("*.md")) + sorted(dp.rglob("*.yaml")) + sorted(dp.rglob("*.json")):
            if fp.name == "index.md":
                continue
            schema_detected = args.schema or detect_schema(fp, project_root)
            if schema_detected:
                to_validate.append((fp, schema_detected))
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
            project_root=project_root,
            check_integrity=check_integrity,
        )
        results.append(result)

    # Output
    if args.json_output:
        print(json.dumps(format_rapport_json(results, project_root), ensure_ascii=False, indent=2))
    else:
        rapport_tekst = format_rapport_text(results, project_root, today)
        print(rapport_tekst)
        if args.full:
            schrijf_md_rapport(rapport_tekst, project_root)
            print(f"\nRapport geschreven naar: rapporten/validatie-rapport.md")

    # Exit code
    heeft_fouten = any(r.errors for r in results)
    sys.exit(1 if heeft_fouten else 0)


if __name__ == "__main__":
    main()
