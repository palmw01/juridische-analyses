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


# ---------------------------------------------------------------------------
# Stub-templates — deterministische skeletten voor /annoteer en /begrip
# Eén bron van waarheid; SKILL.md's roepen deze functies aan i.p.v. templates
# inline te onderhouden.
# ---------------------------------------------------------------------------

def stub_annotatie_index(
    bwb_id: str,
    wet: str,
    artikel: str,
    peildatum: str,
    structuurpositie: str,
    kruisreferenties: list[str] | None = None,
) -> dict:
    """Skelet voor annotaties/{bwb-id}/art{N}.json (Flow A)."""
    return {
        "artikel-id": f"{bwb_id}/art{artikel}",
        "bwb-id": bwb_id,
        "wet": wet,
        "artikel": artikel,
        "peildatum": peildatum,
        "structuurpositie": structuurpositie,
        "leden-annotaties": [],
        "kruisreferenties": list(kruisreferenties or []),
    }


def stub_annotatie_lid(
    bwb_id: str,
    wet: str,
    artikel: str,
    lid: str,
    peildatum: str,
    structuurpositie: str,
    wetstekst: str,
) -> dict:
    """Skelet voor annotaties/{bwb-id}/art{N}-lid{L}.json (Flow B)."""
    return {
        "annotatie-id": f"{bwb_id}/art{artikel}/lid{lid}",
        "bwb-id": bwb_id,
        "wet": wet,
        "artikel": artikel,
        "lid": lid,
        "peildatum": peildatum,
        "structuurpositie": structuurpositie,
        "wetstekst": wetstekst,
        "annotatierijen": [],
        "kruisreferenties": [],
    }


def stub_annotatierij(
    rij_id: str,
    markering: str,
    jas_klasse: str,
    interpretatiemethode: str,
    begrip_id: str,
    toelichting_klasse: str,
    signalering: str | None = None,
) -> dict:
    """Eén rij in annotatie-lid.annotatierijen."""
    return {
        "rij-id": rij_id,
        "markering": markering,
        "jas-klasse": jas_klasse,
        "interpretatiemethode": interpretatiemethode,
        "begrip-id": begrip_id,
        "toelichting-klasse": toelichting_klasse,
        "signalering": signalering,
    }


def stub_begrip(
    bwb_id: str,
    artikel: str,
    lid: str,
    slug: str,
    jas_klasse: str,
    markering_tekst: str,
    interpretatiemethode: str,
    peildatum: str,
    toelichting_klasse: str = "",
) -> dict:
    """Skelet voor begrippen/{slug}.yaml — schema-valid na /annoteer.

    `soort` krijgt een veilige default ("tekst") zodat het stub-bestand direct
    L1-valid is; /begrip moet de juiste soort kiezen (zie kaders/definitie.md).
    `toelichting-klasse` krijgt ook een placeholder omdat het schema minLength
    forceert; /begrip overschrijft deze met de echte juridische motivering.
    """
    begrip_id = f"{bwb_id}/art{artikel}/lid{lid}/{slug}"
    annotatie_id = f"{bwb_id}/art{artikel}/lid{lid}"
    herkomst = "afgeleid" if jas_klasse == "afleidingsregel" else "direct"
    return {
        "begrip-id": begrip_id,
        "begripsnaam": slug,
        "aliases": [],
        "soort": "tekst",
        "soort-id": False,
        "jas-klasse": jas_klasse,
        "toelichting-klasse": toelichting_klasse or "stub — wordt ingevuld door /begrip",
        "herkomst": herkomst,
        "status": "concept",
        "definitie": {"kern": "", "contexten": []},
        "definitie-versie": 1,
        "definitie-gebaseerd-op": ["m-001"],
        "markeringen": [
            {
                "markering-id": "m-001",
                "bron-annotatie-id": annotatie_id,
                "tekst": markering_tekst,
                "interpretatiemethode": interpretatiemethode,
                "bijdrage": "primair",
                "bevestigd": False,
                "bevestigd-op": None,
            }
        ],
        "geldigheid-van": peildatum,
        "geldigheid-tot": None,
        "vervangen-door": None,
        "relaties": {"is-een": [], "heeft": [], "leidt-tot": []},
        "identificatiebegrip": False,
        "afleidingsregel-id": None,
        "tussenresultaat": False,
    }


def stub_regel(
    bwb_id: str,
    artikel: str,
    lid: str,
    seq: str,
    naam: str,
    soort: str,
    peildatum: str,
    rechtsfeit_id: str | None = None,
) -> dict:
    """Skelet voor regels/AR-{bwb-id}-art{N}-lid{L}-{seq}.yaml."""
    return {
        "regel-id": f"AR-{bwb_id}-art{artikel}-lid{lid}-{seq}",
        "naam": naam,
        "soort": soort,
        "bwb-id": bwb_id,
        "artikel": artikel,
        "lid": lid,
        "peildatum": peildatum,
        "geldigheid-van": peildatum,
        "annotatie-id": f"{bwb_id}/art{artikel}/lid{lid}",
        "rechtsfeit-id": rechtsfeit_id,
        "invoer": [],
        "uitvoer": [],
        "operators": [],
        "formele-regel": "",
        "toelichting": "",
        "voorbeeldreeksen": [],
        "tussenresultaat": False,
    }


def stub_voorbeeldreeks(
    regel_id: str,
    naam: str,
    peildatum: str,
    aangemaakt_op: str,
) -> dict:
    """Skelet voor validaties/VR-{...}.yaml."""
    if not regel_id.startswith("AR-"):
        raise ValueError(f"regel_id moet beginnen met 'AR-': {regel_id}")
    vr_id = "VR-" + regel_id[3:]
    return {
        "voorbeeldreeks-id": vr_id,
        "afleidingsregel-id": regel_id,
        "naam": naam,
        "status": "concept",
        "peildatum": peildatum,
        "aangemaakt-op": aangemaakt_op,
        "kolommen": [],
    }


def stub_validatie(
    gevalideerd_door: str,
    oordeel: str,
    gevalideerd_op: str,
    discipline: str | None = None,
    notitie: str | None = None,
) -> dict:
    """Skelet voor het validatie-blok (menselijke beoordeling, A4) op begrip/regel/voorbeeldreeks.

    Wordt door /beoordeel ingevuld; de AI roept dit nooit autonoom aan. `oordeel` is
    een van 'goedgekeurd' | 'afgekeurd' | 'voorbehoud'; `discipline` (optioneel) is
    'jurist' | 'regelanalist'. Zie kaders/samenwerking.md.
    """
    blok = {
        "gevalideerd-door": gevalideerd_door,
        "gevalideerd-op": gevalideerd_op,
        "oordeel": oordeel,
    }
    if discipline is not None:
        blok["discipline"] = discipline
    if notitie is not None:
        blok["notitie"] = notitie
    return blok


def schrijf_yaml(path: Path, data: dict) -> None:
    """Schrijf een dict naar YAML met de project-conventies (Unicode, blokstijl)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            data,
            f,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )


def schrijf_json(path: Path, data: dict, *, indent: int = 2) -> None:
    """Schrijf een dict naar JSON met UTF-8 en stabiele inspringing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
        f.write("\n")
