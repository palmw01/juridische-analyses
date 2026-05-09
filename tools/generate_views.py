#!/usr/bin/env python3
"""
generate_views.py — Genereer Obsidian-compatibele Markdown-views vanuit bronbestanden.
Bronnen: begrippen/ (MD met frontmatter), annotaties/ (MD met frontmatter), regels/ (MD met frontmatter)
Output: views/begrippen/, views/annotaties/, views/regels/
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import frontmatter
import yaml


# ---------------------------------------------------------------------------
# BWB → wet-afkorting mapping
# ---------------------------------------------------------------------------

BWB_NAAR_WET = {
    "BWBR0004770": "iw1990",
    "BWBR0002226": "awr",
    "BWBR0005537": "awb",
    "BWBR0008003": "li2008",
    "BWBR0003738": "ubib1990",
}

# ---------------------------------------------------------------------------
# JAS-klasse → CSS-class mapping
# ---------------------------------------------------------------------------

JAS_NAAR_CSS = {
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


def jas_klasse_naar_css(jas_klasse: str) -> str:
    return JAS_NAAR_CSS.get(jas_klasse, jas_klasse[:2] if jas_klasse else "xx")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_md_frontmatter(filepath: Path) -> tuple[dict, str]:
    """Laad YAML frontmatter en de body van een Markdown-bestand."""
    post = frontmatter.load(str(filepath))
    return dict(post), post.content


def load_yaml(filepath: Path) -> dict:
    with filepath.open() as f:
        return yaml.safe_load(f)


def load_ontologie_kleuren(vault_root: Path) -> dict[str, str]:
    """Laad classDef-kleuren uit ontologie/jas-ontologie.yaml."""
    ontologie_path = vault_root / "ontologie" / "jas-ontologie.yaml"
    if not ontologie_path.exists():
        return {}
    with ontologie_path.open() as f:
        data = yaml.safe_load(f)
    return data.get("classDef-kleuren", {})


def begrip_id_from_path(bwb_id: str, artikel: str, lid: str, begripsnaam: str) -> str:
    """Bouw een begrip-id op in het formaat BWBR.../artN/lidL/naam."""
    art_num = re.sub(r"[^0-9a-z]", "", artikel.lower().replace("art", "").replace(".", "").strip())
    lid_num = re.sub(r"[^0-9]", "", str(lid))
    return f"{bwb_id}/art{art_num}/lid{lid_num}/{begripsnaam}"


def slugify(tekst: str) -> str:
    """Maak een slug van tekst (lowercase, koppeltekens)."""
    t = tekst.lower().strip()
    t = re.sub(r"[^a-z0-9\-]", "-", t)
    t = re.sub(r"-+", "-", t)
    return t.strip("-")


def extract_slug_from_obsidian_link(link: str) -> str:
    """
    Extraheer de bestandsnaam-slug uit een Obsidian wiki-link.
    [[begrippen/invorderbaarheid]] → invorderbaarheid
    [[begrippen/invorderbaarheid|Invorderbaarheid]] → invorderbaarheid
    """
    m = re.match(r'\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]', str(link).strip())
    if m:
        return Path(m.group(1)).stem
    return Path(str(link).strip()).stem


def tags_uit_begrip_id(begrip_id: str, jas_klasse: str = "") -> list[str]:
    """
    Genereer tags op basis van begrip-id en jas-klasse.
    begrip-id: BWBR0004770/art9/lid1/invorderbaarheid
    → [begrip, jas/rechtsbetrekking, wet/iw1990, art/9]
    """
    tags = ["begrip"]
    if jas_klasse:
        tags.append(f"jas/{jas_klasse}")

    parts = begrip_id.split("/")
    # bwb-id
    if parts:
        bwb = parts[0]
        wet = BWB_NAAR_WET.get(bwb)
        if wet:
            tags.append(f"wet/{wet}")
    # art-nummer
    for part in parts[1:]:
        m = re.match(r'art(\d+[a-z]?)$', part)
        if m:
            tags.append(f"art/{m.group(1)}")
            break

    return tags


def tags_uit_frontmatter(data: dict, fallback_bwb: str = "") -> list[str]:
    """Gebruik bestaande tags uit frontmatter als ze al juist zijn."""
    existing = data.get("tags", [])
    if existing and isinstance(existing, list):
        return existing
    # Genereer op basis van bwb-id en jas-klasse
    bwb_id = data.get("bwb-id", fallback_bwb)
    jas_klasse = data.get("jas-klasse", "")
    begrip_id = data.get("begrip-id", "")
    if begrip_id:
        return tags_uit_begrip_id(begrip_id, jas_klasse)
    return ["begrip"]


def obsidian_link_begrip(slug: str) -> str:
    return f"[[views/begrippen/{slug}]]"


def obsidian_link_regel(slug: str) -> str:
    return f"[[views/regels/{slug}]]"


# ---------------------------------------------------------------------------
# Mermaid-diagram renderer
# ---------------------------------------------------------------------------

def render_mermaid(diagram: dict, jas_kleuren: dict) -> str:
    """
    Render een Mermaid-diagram vanuit de diagram-dict.
    diagram heeft: centrale-klasse, knopen [{id, jas-klasse, label}], kanten [{van, naar, label}]
    """
    lines = ["```mermaid", "graph LR"]

    knopen = diagram.get("knopen") or []
    kanten = diagram.get("kanten") or []

    for knoop in knopen:
        css_class = jas_klasse_naar_css(knoop.get("jas-klasse", ""))
        label = knoop.get("label", knoop.get("id", ""))
        node_id = knoop.get("id", "")
        lines.append(f'    {node_id}["{label}"]:::{css_class}')

    for kant in kanten:
        van = kant.get("van", "")
        naar = kant.get("naar", "")
        label = kant.get("label")
        if label:
            lines.append(f'    {van} -->|{label}| {naar}')
        else:
            lines.append(f'    {van} --- {naar}')

    # classDef alleen voor gebruikte klassen
    gebruikte_css = {jas_klasse_naar_css(k.get("jas-klasse", "")) for k in knopen}
    for css_class in sorted(gebruikte_css):
        if css_class in jas_kleuren:
            lines.append(f"    classDef {css_class} {jas_kleuren[css_class]}")

    lines.append("```")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Begrip-view generatie
# ---------------------------------------------------------------------------

def genereer_begrip_view(filepath: Path, vault_root: Path, jas_kleuren: dict) -> tuple[str, str]:
    """
    Genereer een begrip-view Markdown-bestand.
    Geeft (bestandsnaam, content) terug.
    """
    data, body = load_md_frontmatter(filepath)
    stem = filepath.stem  # bestandsnaam zonder extensie = slug

    # Frontmatter velden
    begrip_id = data.get("begrip-id", stem)
    begripsnaam = data.get("begripsnaam", stem)
    jas_klasse = data.get("jas-klasse", "")
    soort = data.get("soort", "")
    herkomst = data.get("herkomst", "")
    status = data.get("status", "")
    definitie = data.get("definitie", "")
    peildatum = str(data.get("peildatum", ""))
    bron = data.get("bron", "")
    geldigheid_van = str(data.get("geldigheid-van", ""))
    afleidingsregels_raw = data.get("afleidingsregels", [])
    tags = tags_uit_frontmatter(data)

    # Afleidingsregel-links omzetten naar views/regels/
    afleidingsregel_links = []
    for link in (afleidingsregels_raw or []):
        slug = extract_slug_from_obsidian_link(str(link))
        afleidingsregel_links.append(obsidian_link_regel(slug))

    # Frontmatter opbouwen
    fm_lines = [
        "---",
        "type: begrip",
        f"begrip-id: {begrip_id}",
        f"begripsnaam: {begripsnaam}",
    ]
    if jas_klasse:
        fm_lines.append(f"jas-klasse: {jas_klasse}")
    if soort:
        fm_lines.append(f"soort: {soort}")
    if herkomst:
        fm_lines.append(f"herkomst: {herkomst}")
    if status:
        fm_lines.append(f"status: {status}")
    if geldigheid_van:
        fm_lines.append(f"geldigheid-van: {geldigheid_van}")
    fm_lines.append("tags:")
    for tag in tags:
        fm_lines.append(f"  - {tag}")
    if afleidingsregel_links:
        fm_lines.append("afleidingsregels:")
        for link in afleidingsregel_links:
            fm_lines.append(f'  - "{link}"')
    fm_lines.append("---")

    # Body opbouwen
    content_lines = fm_lines + [""]

    # Definitie-sectie
    content_lines.append("## Definitie")
    content_lines.append("")
    markering = data.get("markering", "")
    if markering:
        content_lines.append(f'*"{markering}"*', )
    if bron or peildatum:
        bron_str = bron or ""
        peil_str = f"peildatum {peildatum}" if peildatum else ""
        meta_parts = [p for p in [bron_str, peil_str] if p]
        if meta_parts:
            content_lines.append(f'*({", ".join(meta_parts)})*')
    content_lines.append("")
    if definitie:
        content_lines.append(definitie)
    content_lines.append("")

    # Markeringen — uit de body of uit frontmatter-velden
    # Zoek eerst in body naar een Markeringen-sectie
    markeringen_md = _extract_section(body, "Markeringen")
    content_lines.append("## Markeringen")
    content_lines.append("")
    if markeringen_md:
        content_lines.append(markeringen_md.strip())
    else:
        # Bouw tabel op basis van frontmatter-velden
        content_lines.append("| ID | Bron | Tekst | Bijdrage | Bevestigd |")
        content_lines.append("|----|------|-------|---------|-----------|")
        if markering:
            content_lines.append(f"| m-001 | {bron} | {markering} | primair | — |")
    content_lines.append("")

    # Voorbeelden
    voorbeelden_md = _extract_section(body, "Voorbeelden")
    content_lines.append("## Voorbeelden")
    content_lines.append("")
    if voorbeelden_md:
        content_lines.append(voorbeelden_md.strip())
    content_lines.append("")

    # Kenmerken
    kenmerken_md = _extract_section(body, "Kenmerken")
    content_lines.append("## Kenmerken")
    content_lines.append("")
    if kenmerken_md:
        content_lines.append(kenmerken_md.strip())
    content_lines.append("")

    # Relaties
    content_lines.append("## Relaties")
    content_lines.append("")
    relaties_md = _extract_section(body, "Relaties")
    if relaties_md:
        content_lines.append(relaties_md.strip())
    else:
        # Bouw tabel op basis van frontmatter
        content_lines.append("| Type | Kardinaliteit | Begrip |")
        content_lines.append("|------|---------------|--------|")
        is_een = data.get("is-een", [])
        heeft = data.get("heeft", [])
        leidt_tot = data.get("leidt-tot", [])
        if not is_een and not heeft and not leidt_tot:
            content_lines.append("| — | — | — |")
        for bid in (is_een or []):
            slug = extract_slug_from_obsidian_link(str(bid))
            content_lines.append(f"| is-een | — | {obsidian_link_begrip(slug)} |")
        for item in (heeft or []):
            if isinstance(item, dict):
                bid = item.get("begrip-id", "")
                kard = item.get("kardinaliteit", "—")
            else:
                bid = str(item)
                kard = "—"
            slug = extract_slug_from_obsidian_link(bid)
            content_lines.append(f"| heeft | {kard} | {obsidian_link_begrip(slug)} |")
        for item in (leidt_tot or []):
            if isinstance(item, dict):
                bid = item.get("begrip-id", "")
                kard = item.get("kardinaliteit") or "—"
            else:
                bid = str(item)
                kard = "—"
            slug = extract_slug_from_obsidian_link(bid)
            content_lines.append(f"| leidt-tot | {kard} | {obsidian_link_begrip(slug)} |")
    content_lines.append("")

    bestandsnaam = f"{stem}.md"
    return bestandsnaam, "\n".join(content_lines)


def _extract_section(body: str, heading: str) -> str:
    """Extraheer de inhoud van een Markdown-sectie (## Heading)."""
    pattern = rf"##\s+{re.escape(heading)}\s*\n(.*?)(?=\n##\s|\Z)"
    m = re.search(pattern, body, re.DOTALL)
    if m:
        return m.group(1)
    return ""


# ---------------------------------------------------------------------------
# Annotatie-lid-view generatie
# ---------------------------------------------------------------------------

def genereer_annotatie_view(filepath: Path, vault_root: Path, jas_kleuren: dict) -> tuple[str, str]:
    """
    Genereer een annotatie-lid-view Markdown-bestand.
    Geeft (relatief pad binnen views/annotaties/, content) terug.
    """
    data, body = load_md_frontmatter(filepath)

    bwb_id = data.get("bwb-id", "")
    artikel_str = data.get("artikel", "")  # bijv. "Art. 9 lid 1 IW 1990"
    peildatum = str(data.get("peildatum", ""))
    structuurpositie = data.get("structuurpositie", "")
    tags_raw = data.get("tags", [])
    begrippen_raw = data.get("begrippen", [])

    # Wet-afkorting bepalen
    wet_afkorting = BWB_NAAR_WET.get(bwb_id, "")
    if not wet_afkorting and tags_raw:
        for t in tags_raw:
            m = re.match(r'wet/(.+)', str(t))
            if m:
                wet_afkorting = m.group(1)
                break

    # Tags
    tags = ["annotatie"]
    if wet_afkorting:
        tags.append(f"wet/{wet_afkorting}")
    # art-tag uit bestandsnaam of artikel-string
    art_m = re.search(r'[Aa]rt(?:ikel)?\.?\s*(\d+[a-z]?)', filepath.stem)
    if not art_m and artikel_str:
        art_m = re.search(r'[Aa]rt(?:ikel)?\.?\s*(\d+[a-z]?)', artikel_str)
    if art_m:
        tags.append(f"art/{art_m.group(1)}")

    # Begrip-links omzetten
    begrip_links = []
    for link in (begrippen_raw or []):
        slug = extract_slug_from_obsidian_link(str(link))
        begrip_links.append(obsidian_link_begrip(slug))

    # Bestandsnaam bepalen (relatief pad binnen views/annotaties/)
    # annotaties/iw1990/art9-1.md → BWBR0004770/art9-lid1.md
    # We gebruiken de bwb-id en de bestandsnaam
    stem = filepath.stem  # bijv. art9-1
    # Probeer lid-nummer te extraheren
    lid_m = re.match(r'(art\d+[a-z]?)-(\d+)$', stem)
    if lid_m:
        art_part = lid_m.group(1)
        lid_num = lid_m.group(2)
        output_naam = f"{art_part}-lid{lid_num}.md"
        subdir = bwb_id or filepath.parent.name
    else:
        output_naam = f"{stem}.md"
        subdir = bwb_id or filepath.parent.name

    rel_output_path = f"{subdir}/{output_naam}"

    # Frontmatter opbouwen
    fm_lines = [
        "---",
        "type: annotatie",
    ]
    # annotatie-id
    annotatie_id = data.get("annotatie-id", "")
    if not annotatie_id and bwb_id:
        # Afleiden uit bestandsnaam
        if lid_m:
            annotatie_id = f"{bwb_id}/{art_part}/lid{lid_num}"
        else:
            annotatie_id = f"{bwb_id}/{stem}"
    if annotatie_id:
        fm_lines.append(f"annotatie-id: {annotatie_id}")

    fm_lines.append(f'artikel: "{artikel_str}"')
    if peildatum:
        fm_lines.append(f"peildatum: {peildatum}")
    fm_lines.append("tags:")
    for tag in tags:
        fm_lines.append(f"  - {tag}")
    if begrip_links:
        fm_lines.append("begrippen:")
        for link in begrip_links:
            fm_lines.append(f'  - "{link}"')
    fm_lines.append("---")

    content_lines = fm_lines + [""]

    # Wetstekst
    wetstekst_md = _extract_section(body, r"Wetstekst\s+lid\s+\d+\s+\(letterlijk\)")
    if not wetstekst_md:
        wetstekst_md = _extract_section(body, "Wetstekst")
    content_lines.append("## Wetstekst lid (letterlijk)")
    content_lines.append("")
    if wetstekst_md:
        content_lines.append(wetstekst_md.strip())
    content_lines.append("")

    # Annotatietabel
    content_lines.append("## Annotatietabel")
    content_lines.append("")
    anno_md = _extract_section(body, "Annotatietabel")
    if anno_md:
        content_lines.append(anno_md.strip())
    else:
        content_lines.append("| Nr | Markering | JAS-klasse | Interpretatiemethode | Begrip | Signalering |")
        content_lines.append("|----|-----------|-----------|---------------------|--------|-------------|")
    content_lines.append("")

    # Diagram — vanuit body of vanuit diagram-data (JSON-formaat)
    content_lines.append("## Diagram")
    content_lines.append("")
    diagram_data = data.get("diagram")
    diagram_body = _extract_section(body, "Diagram")
    if diagram_data and isinstance(diagram_data, dict):
        content_lines.append(render_mermaid(diagram_data, jas_kleuren))
    elif diagram_body:
        content_lines.append(diagram_body.strip())
    content_lines.append("")

    # Delegatiestructuur
    content_lines.append("## Delegatiestructuur")
    content_lines.append("")
    delegatie_raw = data.get("delegatiestructuur", [])
    delegatie_body = _extract_section(body, "Delegatiestructuur")
    if delegatie_body:
        content_lines.append(delegatie_body.strip())
    elif delegatie_raw:
        for d in delegatie_raw:
            if isinstance(d, dict):
                content_lines.append(f"- {d.get('omschrijving', '')}")
    else:
        content_lines.append("Geen delegatiebevoegdheden.")
    content_lines.append("")

    return rel_output_path, "\n".join(content_lines)


# ---------------------------------------------------------------------------
# Regel-view generatie
# ---------------------------------------------------------------------------

def genereer_regel_view(filepath: Path, vault_root: Path, jas_kleuren: dict) -> tuple[str, str]:
    """
    Genereer een regel-view Markdown-bestand.
    Geeft (bestandsnaam, content) terug.
    """
    data, body = load_md_frontmatter(filepath)
    stem = filepath.stem

    regel_id = data.get("regel-id", stem)
    naam = data.get("naam", "")
    soort = data.get("soort", "")
    bwb_id = data.get("bwb-id", "")
    artikel = data.get("artikel", "")
    peildatum = str(data.get("peildatum", ""))

    # Tags
    tags = ["afleidingsregel"]
    wet = BWB_NAAR_WET.get(bwb_id, "")
    if not wet:
        # Probeer uit tags
        for t in (data.get("tags") or []):
            m = re.match(r'wet/(.+)', str(t))
            if m:
                wet = m.group(1)
                break
    if wet:
        tags.append(f"wet/{wet}")
    if artikel:
        art_m = re.match(r'\d+[a-z]?', str(artikel).strip())
        if art_m:
            tags.append(f"art/{art_m.group(0)}")
    else:
        for t in (data.get("tags") or []):
            m = re.match(r'art/(.+)', str(t))
            if m:
                tags.append(f"art/{m.group(1)}")
                break

    # bepaalt / rechtsfeit / invoer / uitvoer links
    bepaalt_raw = data.get("bepaalt", "")
    rechtsfeit_raw = data.get("rechtsfeit", "")
    invoer_raw = data.get("invoer", [])
    uitvoer_raw = data.get("uitvoer", [])

    def to_view_link(raw_link: str, prefix: str = "begrippen") -> str:
        slug = extract_slug_from_obsidian_link(str(raw_link))
        return f"[[views/{prefix}/{slug}]]"

    bepaalt_link = to_view_link(bepaalt_raw) if bepaalt_raw else ""
    rechtsfeit_link = to_view_link(rechtsfeit_raw) if rechtsfeit_raw else ""
    invoer_links = [to_view_link(b) for b in (invoer_raw or [])]
    uitvoer_links = [to_view_link(b) for b in (uitvoer_raw or [])]

    # Frontmatter
    fm_lines = [
        "---",
        "type: afleidingsregel",
        f"regel-id: {regel_id}",
        f'naam: "{naam}"',
        f"soort: {soort}",
    ]
    if peildatum:
        fm_lines.append(f"peildatum: {peildatum}")
    fm_lines.append("tags:")
    for tag in tags:
        fm_lines.append(f"  - {tag}")
    if bepaalt_link:
        fm_lines.append(f'bepaalt: "{bepaalt_link}"')
    if rechtsfeit_link:
        fm_lines.append(f'rechtsfeit: "{rechtsfeit_link}"')
    if invoer_links:
        fm_lines.append("invoer:")
        for link in invoer_links:
            fm_lines.append(f'  - "{link}"')
    if uitvoer_links:
        fm_lines.append("uitvoer:")
        for link in uitvoer_links:
            fm_lines.append(f'  - "{link}"')
    fm_lines.append("---")

    content_lines = fm_lines + [""]

    # Formele regel
    content_lines.append("## Formele regel")
    content_lines.append("")
    formele_md = _extract_section(body, "Formele regel")
    if formele_md:
        content_lines.append(formele_md.strip())
    content_lines.append("")

    # Toelichting
    content_lines.append("## Toelichting")
    content_lines.append("")
    toelichting_md = _extract_section(body, "Toelichting")
    if toelichting_md:
        content_lines.append(toelichting_md.strip())
    content_lines.append("")

    # Voorbeeldreeksen
    content_lines.append("## Voorbeeldreeksen")
    content_lines.append("")
    voorbeelden_md = _extract_section(body, "Voorbeeldreeksen")
    if voorbeelden_md:
        content_lines.append(voorbeelden_md.strip())
    else:
        content_lines.append("| Invoerwaarden | Verwachte uitkomst | Juridisch juist? |")
        content_lines.append("|--------------|-------------------|-----------------|")
        for vb in (data.get("voorbeeldreeksen") or []):
            if isinstance(vb, dict):
                inv = vb.get("invoerwaarden", "")
                uit = vb.get("verwachte-uitkomst", "")
                jj = "ja" if vb.get("juridisch-juist") else "nee"
                content_lines.append(f"| {inv} | {uit} | {jj} |")
    content_lines.append("")

    bestandsnaam = f"{stem}.md"
    return bestandsnaam, "\n".join(content_lines)


# ---------------------------------------------------------------------------
# Hoofd-generatiefuncties
# ---------------------------------------------------------------------------

def genereer_begrip_views(vault_root: Path, jas_kleuren: dict) -> int:
    """Genereer alle begrip-views. Geeft aantal gegenereerde views terug."""
    begrippen_dir = vault_root / "begrippen"
    output_dir = vault_root / "views" / "begrippen"
    output_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    if not begrippen_dir.exists():
        return 0

    for fp in sorted(begrippen_dir.glob("*.md")):
        if fp.name == "index.md":
            continue
        try:
            bestandsnaam, content = genereer_begrip_view(fp, vault_root, jas_kleuren)
            (output_dir / bestandsnaam).write_text(content)
            count += 1
        except Exception as e:
            print(f"  WAARSCHUWING: {fp.name} overgeslagen ({e})", file=sys.stderr)

    for fp in sorted(begrippen_dir.glob("*.yaml")):
        try:
            bestandsnaam, content = genereer_begrip_view(fp, vault_root, jas_kleuren)
            (output_dir / bestandsnaam).write_text(content)
            count += 1
        except Exception as e:
            print(f"  WAARSCHUWING: {fp.name} overgeslagen ({e})", file=sys.stderr)

    return count


def genereer_annotatie_views(vault_root: Path, jas_kleuren: dict) -> int:
    """Genereer alle annotatie-views. Geeft aantal gegenereerde views terug."""
    annotaties_dir = vault_root / "annotaties"
    output_base = vault_root / "views" / "annotaties"
    output_base.mkdir(parents=True, exist_ok=True)

    count = 0
    if not annotaties_dir.exists():
        return 0

    for fp in sorted(annotaties_dir.rglob("*.md")):
        if fp.name in ("index.md",):
            continue
        stem = fp.stem
        # Alleen lid-annotaties genereren als view (index-noten worden overgeslagen)
        if not re.match(r'art\d+[a-z]?-\d+', stem):
            continue
        try:
            rel_path, content = genereer_annotatie_view(fp, vault_root, jas_kleuren)
            output_path = output_base / rel_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content)
            count += 1
        except Exception as e:
            print(f"  WAARSCHUWING: {fp.name} overgeslagen ({e})", file=sys.stderr)

    return count


def genereer_regel_views(vault_root: Path, jas_kleuren: dict) -> int:
    """Genereer alle regel-views. Geeft aantal gegenereerde views terug."""
    regels_dir = vault_root / "regels"
    output_dir = vault_root / "views" / "regels"
    output_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    if not regels_dir.exists():
        return 0

    for fp in sorted(regels_dir.glob("*.md")):
        if fp.name == "index.md":
            continue
        try:
            bestandsnaam, content = genereer_regel_view(fp, vault_root, jas_kleuren)
            (output_dir / bestandsnaam).write_text(content)
            count += 1
        except Exception as e:
            print(f"  WAARSCHUWING: {fp.name} overgeslagen ({e})", file=sys.stderr)

    for fp in sorted(regels_dir.glob("*.yaml")):
        try:
            bestandsnaam, content = genereer_regel_view(fp, vault_root, jas_kleuren)
            (output_dir / bestandsnaam).write_text(content)
            count += 1
        except Exception as e:
            print(f"  WAARSCHUWING: {fp.name} overgeslagen ({e})", file=sys.stderr)

    return count


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Genereer Obsidian-compatibele Markdown-views vanuit bronbestanden"
    )
    parser.add_argument("--vault-root", default=".", help="Pad naar vault-root")
    parser.add_argument(
        "--type",
        choices=["begrip", "annotatie", "regel"],
        help="Alleen dit type views genereren",
    )
    args = parser.parse_args()

    vault_root = Path(args.vault_root).resolve()
    jas_kleuren = load_ontologie_kleuren(vault_root)

    begrippen_count = 0
    annotaties_count = 0
    regels_count = 0

    if args.type is None or args.type == "begrip":
        begrippen_count = genereer_begrip_views(vault_root, jas_kleuren)

    if args.type is None or args.type == "annotatie":
        annotaties_count = genereer_annotatie_views(vault_root, jas_kleuren)

    if args.type is None or args.type == "regel":
        regels_count = genereer_regel_views(vault_root, jas_kleuren)

    print(
        f"Views gegenereerd: {begrippen_count} begrippen, "
        f"{annotaties_count} annotaties, {regels_count} regels"
    )


if __name__ == "__main__":
    main()
