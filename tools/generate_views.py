#!/usr/bin/env python3
"""
generate_views.py — Genereer Obsidian-compatibele Markdown-views vanuit bronbestanden.

Bronnen (nieuwe schema-architectuur):
  begrippen/*.yaml        → views/begrippen/{slug}.md
  begrippen/*.extra.json  → worden meegegeven voor voorbeelden/kenmerken
  annotaties/**/*.json    → views/annotaties/{bwb-id}/{bestand}.md
  regels/*.yaml           → views/regels/{regel-id}.md

Gebruik:
    cd vault-root/
    tools/.venv/bin/python tools/generate_views.py [--vault-root .] [--type begrip|annotatie|regel] [--file PAD]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

from jas_index_lib import bouw_jas_index

# ---------------------------------------------------------------------------
# Constanten
# ---------------------------------------------------------------------------

BWB_NAAR_WET: dict[str, str] = {
    "BWBR0004770": "iw1990",
    "BWBR0002320": "awr",
    "BWBR0005537": "awb",
    "BWBR0024096": "li2008",
    "BWBR0003738": "ubib1990",
}

JAS_NAAR_CSS: dict[str, str] = {
    "rechtsbetrekking": "rb",
    "rechtssubject": "rs",
    "rechtsobject": "ro",
    "rechtsfeit": "rf",
    "voorwaarde": "vw",
    "afleidingsregel": "ar",
    "variabele": "va",
    "variabelewaarde": "va",
    "parameter": "pa",
    "parameterwaarde": "pa",
    "tijdsaanduiding": "ta",
    "plaatsaanduiding": "pl",
    "delegatiebevoegdheid": "db",
    "delegatie-invulling": "db",
    "brondefinitie": "bd",
    "operator": "op",
}


# ---------------------------------------------------------------------------
# Hulpfuncties
# ---------------------------------------------------------------------------

def jas_naar_css(jas_klasse: str) -> str:
    return JAS_NAAR_CSS.get(jas_klasse, jas_klasse[:2] if jas_klasse else "xx")


def wet_van_bwb(bwb_id: str) -> str:
    return BWB_NAAR_WET.get(bwb_id, "")


def begrip_slug_van_id(begrip_id: str) -> str:
    """Extraheert de slug (laatste segment) uit een begrip-id URI."""
    return begrip_id.split("/")[-1] if begrip_id else ""


def art_tag_van_id(begrip_id_of_annotatie_id: str) -> str | None:
    """Extraheert 'art/9' uit een ID als 'BWBR0004770/art9/lid1/invorderbaarheid'."""
    for segment in begrip_id_of_annotatie_id.split("/"):
        m = re.match(r"art(\d+[a-z]?)$", segment)
        if m:
            return f"art/{m.group(1)}"
    return None


def tags_van_begrip(fm: dict, jas_klasse: str = "") -> list[str]:
    tags = ["begrip"]
    if jas_klasse:
        tags.append(f"jas/{jas_klasse}")
    bwb = fm.get("begrip-id", "").split("/")[0] if fm.get("begrip-id") else ""
    wet = wet_van_bwb(bwb)
    if wet:
        tags.append(f"wet/{wet}")
    art = art_tag_van_id(fm.get("begrip-id", ""))
    if art:
        tags.append(art)
    return tags


def tags_van_annotatie(data: dict) -> list[str]:
    tags = ["annotatie"]
    wet = wet_van_bwb(data.get("bwb-id", ""))
    if wet:
        tags.append(f"wet/{wet}")
    art = art_tag_van_id(data.get("annotatie-id", ""))
    if art:
        tags.append(art)
    return tags


def tags_van_regel(fm: dict) -> list[str]:
    tags = ["afleidingsregel"]
    wet = wet_van_bwb(fm.get("bwb-id", ""))
    if wet:
        tags.append(f"wet/{wet}")
    artikel = str(fm.get("artikel", "")).strip()
    if artikel:
        m = re.match(r"(\d+[a-z]?)$", artikel)
        if m:
            tags.append(f"art/{m.group(1)}")
    return tags


def view_link_begrip(begrip_id: str) -> str:
    slug = begrip_slug_van_id(begrip_id)
    return f"[[views/begrippen/{slug}]]"


def view_link_regel(regel_id: str) -> str:
    return f"[[views/regels/{regel_id}]]"


def laad_jas_kleuren(vault_root: Path) -> dict[str, str]:
    """Laad classDef-kleuren uit ontologie/jas-ontologie.yaml."""
    pad = vault_root / "ontologie" / "jas-ontologie.yaml"
    if not pad.exists():
        return {}
    with pad.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("classDef-kleuren", {}) if isinstance(data, dict) else {}


# bouw_begrip_jas_index wordt geïmporteerd uit jas_index_lib


# ---------------------------------------------------------------------------
# Mermaid-diagram renderer (vanuit JSON diagram-struct)
# ---------------------------------------------------------------------------

def render_mermaid(diagram: dict, jas_kleuren: dict) -> str:
    """Render Mermaid LR-diagram vanuit JSON diagram-dict (knopen + kanten)."""
    knopen = diagram.get("knopen") or []
    kanten = diagram.get("kanten") or []
    if not knopen:
        return ""

    lines = ["```mermaid", "graph LR"]
    for k in knopen:
        css = jas_naar_css(k.get("jas-klasse", ""))
        label = k.get("label", k.get("id", ""))
        lines.append(f'    {k["id"]}["{label}"]:::{css}')

    for kant in kanten:
        van = kant.get("van", "")
        naar = kant.get("naar", "")
        label = kant.get("label")
        if label:
            lines.append(f"    {van} -->|{label}| {naar}")
        else:
            lines.append(f"    {van} --- {naar}")

    gebruikte_css = {jas_naar_css(k.get("jas-klasse", "")) for k in knopen}
    for css in sorted(gebruikte_css):
        if css in jas_kleuren:
            lines.append(f"    classDef {css} {jas_kleuren[css]}")

    lines.append("```")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Begrip-view
# ---------------------------------------------------------------------------

def genereer_begrip_view(
    yaml_path: Path,
    vault_root: Path,
    jas_kleuren: dict,
    jas_index: dict[str, str],
) -> str:
    with yaml_path.open(encoding="utf-8") as f:
        fm: dict = yaml.safe_load(f) or {}

    stem = yaml_path.stem
    begrip_id = fm.get("begrip-id") or stem
    begripsnaam = fm.get("begripsnaam") or stem
    soort = fm.get("soort") or ""
    soort_id = fm.get("soort-id", False)
    herkomst = fm.get("herkomst") or ""
    status = fm.get("status") or "concept"
    definitie = fm.get("definitie") or ""
    geldigheid_van = str(fm.get("geldigheid-van") or "")
    geldigheid_tot = fm.get("geldigheid-tot")
    aliases = fm.get("aliases") or []
    identificatiebegrip = fm.get("identificatiebegrip", False)
    tussenresultaat = fm.get("tussenresultaat", False)
    afleidingsregel_id = fm.get("afleidingsregel-id")
    markeringen: list[dict] = fm.get("markeringen") or []
    relaties: dict = fm.get("relaties") or {}

    jas_klasse = jas_index.get(begrip_id, "")
    tags = tags_van_begrip(fm, jas_klasse)

    # Extra-bestand (voorbeelden + kenmerken)
    extra_pad = vault_root / "begrippen" / f"{stem}.extra.json"
    extra: dict = {}
    if extra_pad.exists():
        with extra_pad.open(encoding="utf-8") as f:
            try:
                extra = json.load(f)
            except json.JSONDecodeError:
                pass
    voorbeelden: list[dict] = extra.get("voorbeelden") or []
    kenmerken: list[str] = extra.get("kenmerken") or []

    lines: list[str] = []

    # --- Frontmatter ---
    lines += ["---"]
    lines.append(f"begrip-id: {begrip_id}")
    lines.append(f"begripsnaam: {begripsnaam}")
    if jas_klasse:
        lines.append(f"jas-klasse: {jas_klasse}")
    if soort:
        lines.append(f"soort: {soort}")
    lines.append(f"herkomst: {herkomst}")
    lines.append(f"status: {status}")
    if geldigheid_van:
        lines.append(f"geldigheid-van: {geldigheid_van}")
    if geldigheid_tot:
        lines.append(f"geldigheid-tot: {geldigheid_tot}")
    lines.append("tags:")
    for t in tags:
        lines.append(f"  - {t}")
    if aliases:
        lines.append("aliases:")
        for a in aliases:
            lines.append(f"  - {a}")
    if afleidingsregel_id:
        lines.append(f'afleidingsregel: "{view_link_regel(afleidingsregel_id)}"')
    lines += ["---", ""]

    # --- Definitie ---
    lines.append("## Definitie")
    lines.append("")
    primaire = [m for m in markeringen if m.get("bijdrage") == "primair"]
    if primaire:
        for m in primaire:
            tekst = m.get("tekst", "")
            bron = m.get("bron-annotatie-id", "")
            methode = m.get("interpretatiemethode", "")
            lines.append(f'*"{tekst}"* *({bron}, {methode})*')
    lines.append("")
    if definitie:
        lines.append(definitie)
    else:
        lines.append("*(Definitie nog niet ingevuld — gebruik `/begrip`)*")
    lines.append("")

    # --- Markeringen ---
    lines.append("## Markeringen")
    lines.append("")
    if markeringen:
        lines.append("| ID | Bron-annotatie | Tekst | Bijdrage | Methode | Bevestigd |")
        lines.append("|----|---------------|-------|---------|---------|-----------|")
        for m in markeringen:
            mid = m.get("markering-id", "")
            bron = m.get("bron-annotatie-id", "")
            tekst = m.get("tekst", "").replace("|", "\\|")
            bijdr = m.get("bijdrage", "")
            methode = m.get("interpretatiemethode", "")
            bev = "ja" if m.get("bevestigd") else "nee"
            lines.append(f"| {mid} | {bron} | {tekst} | {bijdr} | {methode} | {bev} |")
    else:
        lines.append("*Geen markeringen.*")
    lines.append("")

    # --- Voorbeelden ---
    lines.append("## Voorbeelden")
    lines.append("")
    if voorbeelden:
        lines.append("| Stelling | Waar? | Toelichting |")
        lines.append("|----------|-------|-------------|")
        for vb in voorbeelden:
            stelling = str(vb.get("stelling", "")).replace("|", "\\|")
            waar = "ja" if vb.get("waar") else "nee"
            toel = str(vb.get("toelichting", "")).replace("|", "\\|")
            lines.append(f"| {stelling} | {waar} | {toel} |")
    else:
        lines.append("*(Voorbeelden nog niet ingevuld)*")
    lines.append("")

    # --- Kenmerken ---
    lines.append("## Kenmerken")
    lines.append("")
    if kenmerken:
        for k in kenmerken:
            lines.append(f"- {k}")
    else:
        lines.append("*(Kenmerken nog niet ingevuld)*")
    lines.append("")

    # --- Metavelden ---
    meta: list[str] = []
    if identificatiebegrip:
        meta.append("identificatiebegrip")
    if soort_id:
        meta.append("soort-id")
    if tussenresultaat:
        meta.append("tussenresultaat")
    if meta:
        lines.append(f"> **Kenmerken:** {', '.join(meta)}")
        lines.append("")

    # --- Relaties ---
    lines.append("## Relaties")
    lines.append("")
    is_een: list[str] = relaties.get("is-een") or []
    heeft: list[dict] = relaties.get("heeft") or []
    leidt_tot: list[dict] = relaties.get("leidt-tot") or []

    if is_een or heeft or leidt_tot:
        lines.append("| Type | Kardinaliteit | Begrip |")
        lines.append("|------|---------------|--------|")
        for bid in is_een:
            lines.append(f"| is-een | — | {view_link_begrip(bid)} |")
        for item in heeft:
            if isinstance(item, dict):
                bid = item.get("begrip-id", "")
                kard = item.get("kardinaliteit", "—")
            else:
                bid = str(item)
                kard = "—"
            lines.append(f"| heeft | {kard} | {view_link_begrip(bid)} |")
        for item in leidt_tot:
            if isinstance(item, dict):
                bid = item.get("begrip-id", "")
                kard = item.get("kardinaliteit") or "—"
                rsoort = item.get("relatie-soort", "leidt-tot")
            else:
                bid = str(item)
                kard = "—"
                rsoort = "leidt-tot"
            lines.append(f"| {rsoort} | {kard} | {view_link_begrip(bid)} |")
    else:
        lines.append("| — | — | — |")
    lines.append("")

    # --- Afleidingsregel-link ---
    if afleidingsregel_id:
        lines.append("## Afleidingsregel")
        lines.append("")
        lines.append(view_link_regel(afleidingsregel_id))
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Annotatie-view
# ---------------------------------------------------------------------------

def genereer_annotatie_view(json_path: Path, vault_root: Path, jas_kleuren: dict) -> tuple[str, str]:
    """
    Geeft (relatief uitvoerpad binnen views/annotaties/, Markdown-content).
    """
    with json_path.open(encoding="utf-8") as f:
        data: dict = json.load(f)

    annotatie_id = data.get("annotatie-id") or json_path.stem
    bwb_id = data.get("bwb-id", "")
    wet = data.get("wet", "")
    artikel = data.get("artikel", "")
    lid = data.get("lid", "")
    peildatum = str(data.get("peildatum") or "")
    structuurpositie = data.get("structuurpositie", "")
    wetstekst = data.get("wetstekst", "")
    annotatierijen: list[dict] = data.get("annotatierijen") or []
    diagram: dict = data.get("diagram") or {}
    kruisrefs: list = data.get("kruisreferenties") or []
    delegatiestructuur: list = data.get("delegatiestructuur") or []

    tags = tags_van_annotatie(data)

    # Uitvoerpad bepalen
    stem = json_path.stem  # bijv. art9-lid1
    subdir = bwb_id or json_path.parent.name
    rel_pad = f"{subdir}/{stem}.md"

    # Begrip-links vanuit annotatierijen (deduplicated)
    begrip_ids_gezien: set[str] = set()
    begrip_links: list[str] = []
    for rij in annotatierijen:
        bid = rij.get("begrip-id", "")
        if bid and bid not in begrip_ids_gezien:
            begrip_ids_gezien.add(bid)
            begrip_links.append(view_link_begrip(bid))

    # Artikel-label
    if lid:
        artikel_label = f"Art. {artikel} lid {lid} {wet}"
    else:
        artikel_label = f"Art. {artikel} {wet}".strip()

    lines: list[str] = []

    # --- Frontmatter ---
    lines += ["---", "type: annotatie"]
    lines.append(f"annotatie-id: {annotatie_id}")
    lines.append(f'artikel: "{artikel_label}"')
    if bwb_id:
        lines.append(f"bwb-id: {bwb_id}")
    if peildatum:
        lines.append(f"peildatum: {peildatum}")
    lines.append("tags:")
    for t in tags:
        lines.append(f"  - {t}")
    if begrip_links:
        lines.append("begrippen:")
        for link in begrip_links:
            lines.append(f'  - "{link}"')
    lines += ["---", ""]

    # --- Wetstekst ---
    lines.append(f"## Wetstekst{' lid ' + lid if lid else ''} (letterlijk)")
    lines.append("")
    if wetstekst:
        lines.append(f"> **{lid or artikel}** {wetstekst}")
    if structuurpositie:
        lines.append(f"")
        lines.append(f"*{structuurpositie}*")
    lines.append("")

    # --- Annotatietabel ---
    lines.append("## Annotatietabel")
    lines.append("")
    if annotatierijen:
        lines.append("| Nr | Markering | JAS-klasse | Methode | Begrip | Signalering |")
        lines.append("|----|-----------|-----------|---------|--------|-------------|")
        for rij in annotatierijen:
            nr = rij.get("rij-id", "")
            markering = rij.get("markering", "").replace("|", "\\|")
            jas = rij.get("jas-klasse", "")
            methode = rij.get("interpretatiemethode", "")
            bid = rij.get("begrip-id", "")
            begrip_link = view_link_begrip(bid) if bid else "—"
            sig = rij.get("signalering") or "—"
            sig = str(sig).replace("|", "\\|")
            lines.append(f"| {nr} | {markering} | **{jas}** | {methode} | {begrip_link} | {sig} |")
    else:
        lines.append("*(Geen annotatierijen)*")
    lines.append("")

    # --- Diagram ---
    lines.append("## Diagram")
    lines.append("")
    if diagram.get("knopen"):
        mermaid = render_mermaid(diagram, jas_kleuren)
        if mermaid:
            lines.append(mermaid)
        else:
            lines.append("*(Diagram niet beschikbaar)*")
    else:
        lines.append("*(Geen diagram)*")
    lines.append("")

    # --- Kruisreferenties ---
    if kruisrefs:
        lines.append("## Kruisreferenties")
        lines.append("")
        for ref in kruisrefs:
            if isinstance(ref, dict):
                doel = ref.get("doel-artikel") or ref.get("doel-bwb-id", "")
                richting = ref.get("richting", "")
                lines.append(f"- {doel} ({richting})")
            else:
                lines.append(f"- {ref}")
        lines.append("")

    # --- Delegatiestructuur ---
    lines.append("## Delegatiestructuur")
    lines.append("")
    if delegatiestructuur:
        lines.append("| Bevoegdheid | Vindplaats | Type | Invulling |")
        lines.append("|------------|------------|------|-----------|")
        for d in delegatiestructuur:
            if isinstance(d, dict):
                omschr = d.get("omschrijving", "")
                vindpl = d.get("vindplaats", "")
                dtype = d.get("type", "")
                invull = d.get("invulling") or "—"
                lines.append(f"| {omschr} | {vindpl} | {dtype} | {invull} |")
    else:
        lines.append("Geen delegatiebevoegdheden.")
    lines.append("")

    return rel_pad, "\n".join(lines)


# ---------------------------------------------------------------------------
# Regel-view
# ---------------------------------------------------------------------------

def genereer_regel_view(yaml_path: Path, vault_root: Path, jas_kleuren: dict) -> str:
    with yaml_path.open(encoding="utf-8") as f:
        fm: dict = yaml.safe_load(f) or {}

    stem = yaml_path.stem
    regel_id = fm.get("regel-id") or stem
    naam = fm.get("naam") or ""
    soort = fm.get("soort") or ""
    bwb_id = fm.get("bwb-id") or ""
    artikel = str(fm.get("artikel") or "")
    lid = str(fm.get("lid") or "")
    peildatum = str(fm.get("peildatum") or "")
    annotatie_id = fm.get("annotatie-id") or ""
    rechtsfeit_id = fm.get("rechtsfeit-id") or ""
    invoer: list[str] = fm.get("invoer") or []
    uitvoer: list[str] = fm.get("uitvoer") or []
    operators: list[str] = fm.get("operators") or []
    formele_regel = fm.get("formele-regel") or ""
    toelichting = fm.get("toelichting") or ""
    voorbeeldreeksen: list[dict] = fm.get("voorbeeldreeksen") or []
    tussenresultaat = fm.get("tussenresultaat", False)

    tags = tags_van_regel(fm)
    if tussenresultaat:
        tags.append("tussenresultaat")

    lines: list[str] = []

    # --- Frontmatter ---
    lines += ["---"]
    lines.append(f"regel-id: {regel_id}")
    lines.append(f'naam: "{naam}"')
    lines.append(f"soort: {soort}")
    if peildatum:
        lines.append(f"peildatum: {peildatum}")
    lines.append("tags:")
    for t in tags:
        lines.append(f"  - {t}")
    if annotatie_id:
        lines.append(f"annotatie-id: {annotatie_id}")
    if uitvoer:
        lines.append("uitvoer:")
        for bid in uitvoer:
            lines.append(f'  - "{view_link_begrip(bid)}"')
    if invoer:
        lines.append("invoer:")
        for bid in invoer:
            lines.append(f'  - "{view_link_begrip(bid)}"')
    lines += ["---", ""]

    # --- Koptekst ---
    lines.append(f"# {naam or regel_id}")
    lines.append("")
    meta_parts = [soort]
    if artikel:
        meta_parts.append(f"art. {artikel}" + (f" lid {lid}" if lid else ""))
    if bwb_id:
        wet = wet_van_bwb(bwb_id)
        if wet:
            meta_parts.append(wet.upper())
    lines.append(f"*{' · '.join(meta_parts)}*")
    lines.append("")

    # --- Invoer / Uitvoer ---
    if invoer or uitvoer:
        lines.append("## Invoer en uitvoer")
        lines.append("")
        if rechtsfeit_id:
            lines.append(f"**Rechtsfeit:** {view_link_begrip(rechtsfeit_id)}")
            lines.append("")
        if invoer:
            lines.append("**Invoer:**")
            for bid in invoer:
                lines.append(f"- {view_link_begrip(bid)}")
            lines.append("")
        if uitvoer:
            lines.append("**Uitvoer:**")
            for bid in uitvoer:
                lines.append(f"- {view_link_begrip(bid)}")
            lines.append("")
        if operators:
            lines.append(f"**Operators:** {', '.join(operators)}")
            lines.append("")

    # --- Formele regel ---
    lines.append("## Formele regel")
    lines.append("")
    if formele_regel:
        lines.append(formele_regel)
    else:
        lines.append("*(Formele regel nog niet ingevuld)*")
    lines.append("")

    # --- Toelichting ---
    lines.append("## Toelichting")
    lines.append("")
    if toelichting:
        lines.append(toelichting)
    else:
        lines.append("*(Toelichting nog niet ingevuld)*")
    lines.append("")

    # --- Voorbeeldreeksen ---
    lines.append("## Voorbeeldreeksen")
    lines.append("")
    if voorbeeldreeksen:
        lines.append("| Invoerwaarden | Verwachte uitkomst | Juist? | Toelichting |")
        lines.append("|--------------|-------------------|--------|-------------|")
        for vb in voorbeeldreeksen:
            if isinstance(vb, dict):
                inv = str(vb.get("invoerwaarden") or "").replace("|", "\\|")
                uit = str(vb.get("verwachte-uitkomst") or "").replace("|", "\\|")
                juist = "ja" if vb.get("juridisch-juist") else "nee"
                toel = str(vb.get("toelichting") or "").replace("|", "\\|")
                lines.append(f"| {inv} | {uit} | {juist} | {toel} |")
    else:
        lines.append("*(Nog geen voorbeeldreeksen)*")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Batch-generatie per type
# ---------------------------------------------------------------------------

def genereer_begrip_views(vault_root: Path, jas_kleuren: dict, jas_index: dict, enkel_bestand: Path | None) -> int:
    begrippen_dir = vault_root / "begrippen"
    output_dir = vault_root / "views" / "begrippen"
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    bronnen = [enkel_bestand] if enkel_bestand else sorted(begrippen_dir.glob("*.yaml"))
    for fp in bronnen:
        if not fp.suffix == ".yaml":
            continue
        try:
            content = genereer_begrip_view(fp, vault_root, jas_kleuren, jas_index)
            (output_dir / f"{fp.stem}.md").write_text(content, encoding="utf-8")
            count += 1
        except Exception as e:
            print(f"  WAARSCHUWING begrip {fp.name}: {e}", file=sys.stderr)

    return count


def genereer_annotatie_views(vault_root: Path, jas_kleuren: dict, enkel_bestand: Path | None) -> int:
    annotaties_dir = vault_root / "annotaties"
    output_base = vault_root / "views" / "annotaties"
    output_base.mkdir(parents=True, exist_ok=True)
    count = 0

    if enkel_bestand:
        bronnen = [enkel_bestand]
    else:
        bronnen = sorted(annotaties_dir.glob("**/*.json"))

    for fp in bronnen:
        if fp.suffix != ".json":
            continue
        try:
            rel_parts = fp.relative_to(annotaties_dir).parts
            if any(part.startswith(".") for part in rel_parts):
                continue
        except ValueError:
            pass
        try:
            rel_pad, content = genereer_annotatie_view(fp, vault_root, jas_kleuren)
            output_path = output_base / rel_pad
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
            count += 1
        except Exception as e:
            print(f"  WAARSCHUWING annotatie {fp.name}: {e}", file=sys.stderr)

    return count


def genereer_regel_views(vault_root: Path, jas_kleuren: dict, enkel_bestand: Path | None) -> int:
    regels_dir = vault_root / "regels"
    output_dir = vault_root / "views" / "regels"
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    bronnen = [enkel_bestand] if enkel_bestand else sorted(regels_dir.glob("*.yaml"))
    for fp in bronnen:
        if not fp.suffix == ".yaml":
            continue
        try:
            content = genereer_regel_view(fp, vault_root, jas_kleuren)
            (output_dir / f"{fp.stem}.md").write_text(content, encoding="utf-8")
            count += 1
        except Exception as e:
            print(f"  WAARSCHUWING regel {fp.name}: {e}", file=sys.stderr)

    return count


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Genereer Obsidian-views vanuit vault-bronbestanden")
    parser.add_argument("--vault-root", default=".", help="Pad naar de vault-root (default: .)")
    parser.add_argument(
        "--type",
        choices=["begrip", "annotatie", "regel", "wetstekst"],
        help="Alleen dit type views genereren",
    )
    parser.add_argument(
        "--file",
        metavar="PAD",
        help="Verwerk alleen dit bestand (relatief of absoluut pad)",
    )
    args = parser.parse_args()

    vault_root = Path(args.vault_root).resolve()
    jas_kleuren = laad_jas_kleuren(vault_root)
    jas_index = bouw_jas_index(vault_root)

    enkel_bestand: Path | None = None
    if args.file:
        enkel_bestand = Path(args.file).resolve()
        if not enkel_bestand.exists():
            print(f"Fout: bestand niet gevonden: {enkel_bestand}", file=sys.stderr)
            return 1

    begrippen_count = annotaties_count = regels_count = wetsteksten_count = 0

    if args.type in (None, "begrip"):
        eb = enkel_bestand if (enkel_bestand and enkel_bestand.suffix == ".yaml"
                               and "begrippen" in str(enkel_bestand)) else None
        begrippen_count = genereer_begrip_views(vault_root, jas_kleuren, jas_index,
                                                eb if not args.type else enkel_bestand)

    if args.type in (None, "annotatie"):
        eb = enkel_bestand if (enkel_bestand and enkel_bestand.suffix == ".json") else None
        annotaties_count = genereer_annotatie_views(vault_root, jas_kleuren,
                                                    eb if not args.type else enkel_bestand)

    if args.type in (None, "regel"):
        eb = enkel_bestand if (enkel_bestand and enkel_bestand.suffix == ".yaml"
                               and "regels" in str(enkel_bestand)) else None
        regels_count = genereer_regel_views(vault_root, jas_kleuren,
                                            eb if not args.type else enkel_bestand)

    if args.type in (None, "wetstekst"):
        eb = enkel_bestand if (enkel_bestand and enkel_bestand.suffix == ".json"
                               and "bronnen" in str(enkel_bestand)) else None
        wetsteksten_count = genereer_wetstekst_views(vault_root, eb if not args.type else enkel_bestand)

    print(
        f"Views gegenereerd: {begrippen_count} begrippen, "
        f"{annotaties_count} annotaties, {regels_count} regels, {wetsteksten_count} wetsteksten"
    )
    return 0


def genereer_wetstekst_view(json_file: Path, vault_root: Path) -> str:
    with json_file.open(encoding="utf-8") as f:
        data = json.load(f)

    bwb_id = data.get("bwb-id") or data.get("bwbId")
    artikel = data.get("artikel", "")
    citeertitel = data.get("citeertitel", "")
    versiedatum = data.get("versiedatum", "")
    pad = data.get("pad", "")
    bronreferentie = data.get("bronreferentie", "")

    wet = wet_van_bwb(bwb_id)

    lines = [
        "---",
        "type: wetstekst",
        f'title: "{artikel} {citeertitel}"',
        f"bwb-id: {bwb_id}",
        f'artikel: "{artikel}"',
        f"peildatum: {versiedatum}",
        f'structuurpositie: "{pad}"',
        "tags:",
        "  - wetstekst",
    ]
    if wet:
        lines.append(f"  - wet/{wet}")
    if artikel:
        m = re.match(r"(\d+[a-z]?)$", str(artikel))
        if m:
            lines.append(f"  - art/{m.group(1)}")

    lines.extend([
        f'bronreferentie: "{bronreferentie}"',
        "---",
        "",
        f"# {artikel} {citeertitel}",
        "",
    ])

    for lid_obj in data.get("leden", []):
        lid_nr = lid_obj.get("lid", "")
        tekst = lid_obj.get("tekst", "")
        if lid_nr:
            lines.append(f"> **{lid_nr}** {tekst}")
        else:
            lines.append(f"> {tekst}")
        lines.append("")

    return "\n".join(lines)


def genereer_wetstekst_views(vault_root: Path, enkel_bestand: Path | None) -> int:
    bronnen_dir = vault_root / "bronnen"
    output_base = vault_root / "views" / "wetteksten"
    output_base.mkdir(parents=True, exist_ok=True)
    count = 0

    if enkel_bestand:
        bestanden = [enkel_bestand]
    else:
        bestanden = sorted(bronnen_dir.rglob("*.json"))

    for fp in bestanden:
        if not fp.suffix == ".json":
            continue
        try:
            content = genereer_wetstekst_view(fp, vault_root)
            # Pad bepalen: views/wetteksten/{wet}/{artikel}.md
            with fp.open(encoding="utf-8") as f:
                data = json.load(f)
            bwb_id = data.get("bwb-id") or data.get("bwbId")
            wet_slug = wet_van_bwb(bwb_id) or bwb_id.lower()
            art_slug = str(data.get("artikel", fp.stem)).replace(".", "-").lower()

            output_path = output_base / wet_slug / f"art{art_slug}.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
            count += 1
        except Exception as e:
            print(f"  WAARSCHUWING wetstekst {fp.name}: {e}", file=sys.stderr)

    return count


if __name__ == "__main__":
    sys.exit(main())
