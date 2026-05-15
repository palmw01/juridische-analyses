import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from jas_index_lib import haal_kern, haal_contexten

from sitegen.config import slugify


def laad_begrippen(project_root: Path) -> list[dict]:
    begrippen = []
    pad = project_root / "begrippen"
    for f in sorted(pad.glob("*.yaml")):
        data = yaml.safe_load(f.read_text()) or {}
        relaties: dict = data.get("relaties") or {}
        def extract_rel(key):
            return [r if isinstance(r, str) else r.get("begrip-id", "") for r in (relaties.get(key) or [])]
        klasse = data.get("jas-klasse") or "onbekend"
        if klasse == "onbekend":
            for m in data.get("markeringen") or []:
                if m.get("bijdrage") == "primair":
                    jc = m.get("jas-klasse") or ""
                    if jc:
                        klasse = jc
                    break
            else:
                soort = data.get("soort", "")
                if soort in ("datum", "tijdsduur"):
                    klasse = "tijdsaanduiding"
                elif soort == "monetair-bedrag":
                    klasse = "variabele"
                elif soort == "enumeratie":
                    klasse = "rechtsobject"
        definitie_obj = data.get("definitie") or {}
        begrippen.append({
            "id": data.get("begrip-id", f.stem),
            "naam": data.get("begripsnaam", f.stem),
            "slug": slugify(data.get("begripsnaam", f.stem)),
            "definitie": haal_kern(definitie_obj),
            "definitie_contexten": haal_contexten(definitie_obj),
            "definitie_versie": data.get("definitie-versie"),
            "definitie_gebaseerd_op": data.get("definitie-gebaseerd-op") or [],
            "soort": data.get("soort", "") or "",
            "soort_id": data.get("soort-id", False),
            "herkomst": data.get("herkomst", "") or "",
            "status": data.get("status", "concept") or "concept",
            "aliases": data.get("aliases") or [],
            "relaties": {
                "is-een": extract_rel("is-een"),
                "heeft": extract_rel("heeft"),
                "leidt-tot": extract_rel("leidt-tot"),
            },
            "afleidingsregel-id": data.get("afleidingsregel-id"),
            "uitvoer-van-regel-id": data.get("uitvoer-van-regel-id"),
            "tussenresultaat": data.get("tussenresultaat", False),
            "identificatiebegrip": data.get("identificatiebegrip", False),
            "jas_klasse": klasse,
            "toelichting_klasse": data.get("toelichting-klasse") or "",
            "markeringen": data.get("markeringen") or [],
            "geldigheid_van": str(data.get("geldigheid-van") or ""),
            "geldigheid_tot": str(data.get("geldigheid-tot") or "") if data.get("geldigheid-tot") else "",
            "vervangen_door": data.get("vervangen-door") or "",
            "voorbeelden": data.get("voorbeelden") or [],
            "kenmerken": data.get("kenmerken") or [],
        })
    return begrippen


def laad_annotaties(project_root: Path) -> list[dict]:
    annotaties = []
    pad = project_root / "annotaties"
    for json_file in sorted(pad.rglob("*.json")):
        data = json.loads(json_file.read_text())
        aid = data.get("annotatie-id") or ""
        wetstekst = data.get("wetstekst") or ""
        if not aid or not wetstekst:
            continue
        rijen = []
        for r in data.get("annotatierijen") or []:
            rijen.append({
                "rij_id": r.get("rij-id", ""),
                "markering": r.get("markering", ""),
                "jas_klasse": r.get("jas-klasse", ""),
                "interpretatiemethode": r.get("interpretatiemethode", ""),
                "begrip_id": r.get("begrip-id", ""),
                "toelichting_klasse": r.get("toelichting-klasse", ""),
                "signalering": r.get("signalering"),
            })
        kruisrefs = []
        for k in data.get("kruisreferenties") or []:
            kruisrefs.append({
                "doel_bwb_id": k.get("doel-bwb-id", ""),
                "doel_artikel": k.get("doel-artikel") or "",
                "doel_lid": k.get("doel-lid") or "",
                "richting": k.get("richting", ""),
                "confidence": k.get("confidence"),
                "ruwe_tekst": k.get("ruwe-tekst", ""),
            })
        annotaties.append({
            "id": aid,
            "bwb_id": data.get("bwb-id", ""),
            "wet": data.get("wet", ""),
            "artikel": data.get("artikel", ""),
            "lid": data.get("lid") or data.get("sectie", ""),
            "peildatum": str(data.get("peildatum") or ""),
            "structuurpositie": data.get("structuurpositie", ""),
            "wetstekst": wetstekst,
            "rijen": rijen,
            "diagram": data.get("diagram"),
            "kruisreferenties": kruisrefs,
            "delegatiestructuur": data.get("delegatiestructuur") or [],
        })
    return annotaties


def laad_regels(project_root: Path) -> list[dict]:
    regels = []
    pad = project_root / "regels"
    for f in sorted(pad.glob("*.yaml")):
        data = yaml.safe_load(f.read_text()) or {}
        regels.append({
            "id": data.get("regel-id", f.stem),
            "naam": data.get("naam", ""),
            "soort": data.get("soort", ""),
            "formele_regel": data.get("formele-regel", ""),
            "toelichting": data.get("toelichting", ""),
            "invoer": data.get("invoer") or [],
            "uitvoer": data.get("uitvoer") or [],
            "operators": data.get("operators") or [],
            "voorbeeldreeksen": data.get("voorbeeldreeksen") or [],
            "tussenresultaat": data.get("tussenresultaat", False),
            "bwb_id": data.get("bwb-id", ""),
            "artikel": str(data.get("artikel", "") or ""),
            "lid": str(data.get("lid", "") or ""),
            "peildatum": str(data.get("peildatum") or ""),
            "annotatie_id": data.get("annotatie-id", ""),
            "rechtsfeit_id": data.get("rechtsfeit-id") or "",
            "vervangt_regel_id": data.get("vervangt-regel-id") or "",
            "gespecialiseerd_regel_id": data.get("gespecialiseerd-regel-id") or "",
            "geldigheid_van": str(data.get("geldigheid-van") or ""),
            "geldigheid_tot": str(data.get("geldigheid-tot") or "") if data.get("geldigheid-tot") else "",
            "prioriteit": data.get("prioriteit"),
        })
    return regels


def laad_waarschuwingen(project_root: Path) -> dict[str, list[str]]:
    """Laad L3-waarschuwingen uit rapporten/validatie-rapport.json.
    Retourneert {relatief_pad: [waarschuwing_strings]}.
    Geeft leeg dict terug als het rapport ontbreekt."""
    pad = project_root / "rapporten" / "validatie-rapport.json"
    if not pad.exists():
        return {}
    data = json.loads(pad.read_text())
    result: dict[str, list[str]] = {}
    for item in data.get("waarschuwingen") or []:
        bestand = item["bestand"]
        result.setdefault(bestand, []).append(item["boodschap"])
    return result


def waarschuwingen_voor(slug_of_id: str, index: dict[str, list[str]]) -> list[str]:
    """Geef waarschuwingen voor een begrip-slug of regel-id."""
    for pad, ws in index.items():
        if slug_of_id in pad:
            return ws
    return []


def laad_waarschuwingen_meta(project_root: Path) -> list[dict]:
    """Laad oplossings-meta uit tools/waarschuwingen-meta.yaml.
    Retourneert entries gesorteerd op sleutellengte aflopend (langste eerst)
    zodat startswith-matching altijd de meest specifieke entry vindt."""
    pad = project_root / "tools" / "waarschuwingen-meta.yaml"
    if not pad.exists():
        return []
    data = yaml.safe_load(pad.read_text()) or []
    return sorted(data, key=lambda e: -len(e.get("sleutel", "")))


def zoek_meta(boodschap: str, meta: list[dict]) -> dict | None:
    """Vind de meta-entry voor een waarschuwingstekst via startswith-matching."""
    tekst = boodschap
    for prefix in ("[L3] ", "[L2] ", "[L1] "):
        tekst = tekst.removeprefix(prefix)
    for entry in meta:
        if tekst.startswith(entry["sleutel"]):
            return entry
    return None


def laad_artikel_indices(project_root: Path) -> list[dict]:
    indices = []
    pad = project_root / "annotaties"
    for json_file in sorted(pad.rglob("*.json")):
        data = json.loads(json_file.read_text())
        if "artikel-id" not in data:
            continue
        leden = [str(link).strip() for link in (data.get("leden-annotaties") or []) if link]
        indices.append({
            "id": data["artikel-id"],
            "bwb_id": data.get("bwb-id", ""),
            "wet": data.get("wet", ""),
            "artikel": data.get("artikel", ""),
            "peildatum": str(data.get("peildatum") or ""),
            "structuurpositie": data.get("structuurpositie", ""),
            "leden_annotaties": leden,
            "kruisreferenties": data.get("kruisreferenties") or [],
            "delegatiestructuur": data.get("delegatiestructuur") or [],
        })
    return indices
