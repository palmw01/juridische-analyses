#!/usr/bin/env python3
"""
migrate_vault.py — Migratiescript voor juridisch kennissysteem vault.

Stappen:
  --step extract     1a begrippen, 1b regels, 1c annotaties migreren naar staging
  --step resolve     Wiki-link resolutie controleren
  --step enrichment  Enrichment-queue aanmaken
  --all              Alle stappen achtereenvolgens
  --commit           Staging naar vault verplaatsen, oud archiveren
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import frontmatter
import yaml

# ---------------------------------------------------------------------------
# ID-toewijzingstabellen
# ---------------------------------------------------------------------------

BEGRIP_ID_MAPPING = {
    "belastingaanslag": "BWBR0004770/art9/lid1/belastingaanslag",
    "invorderbaarheid": "BWBR0004770/art9/lid1/invorderbaarheid",
    "zes-weken-na-dagtekening-aanslagbiljet": "BWBR0004770/art9/lid1/zes-weken-na-dagtekening-aanslagbiljet",
    "zes-weken": "BWBR0004770/art9/lid1/zes-weken",
    "dagtekening-aanslagbiljet": "BWBR0004770/art9/lid1/dagtekening-aanslagbiljet",
    "invorderbaarheid-belastingaanslag": "BWBR0004770/art9/lid1/invorderbaarheid-belastingaanslag",
    "voorlopige-aanslag": "BWBR0004770/art9/lid5/voorlopige-aanslag",
    "logische-of": "BWBR0004770/art9/lid5/logische-of",
    "voorlopige-conserverende-aanslag-ib": "BWBR0004770/art9/lid5/voorlopige-conserverende-aanslag-ib",
    "in-afwijking-van-eerste-lid": "BWBR0004770/art9/lid5/in-afwijking-van-eerste-lid",
    "dagtekening-in-vaststellingsjaar": "BWBR0004770/art9/lid5/dagtekening-in-vaststellingsjaar",
    "maand-dagtekening-aanslagbiljet": "BWBR0004770/art9/lid5/maand-dagtekening-aanslagbiljet",
    "termijnenberekening-resterende-maanden": "BWBR0004770/art9/lid5/termijnenberekening-resterende-maanden",
    "resterende-maanden-jaar": "BWBR0004770/art9/lid5/resterende-maanden-jaar",
    "invorderbaarheid-in-gelijke-termijnen": "BWBR0004770/art9/lid5/invorderbaarheid-in-gelijke-termijnen",
    "vervaldag-eerste-termijn": "BWBR0004770/art9/lid5/vervaldag-eerste-termijn",
    "een-maand-na-dagtekening": "BWBR0004770/art9/lid5/een-maand-na-dagtekening",
    "vervaldag-volgende-termijnen": "BWBR0004770/art9/lid5/vervaldag-volgende-termijnen",
    "telkens-een-maand-later": "BWBR0004770/art9/lid5/telkens-een-maand-later",
    "terugvalregel-lid-1": "BWBR0004770/art9/lid5/terugvalregel-lid-1",
    "termijnbedrag": "BWBR0004770/art9/lid5/termijnbedrag",
    "totaalbedrag-belastingaanslag": "BWBR0004770/art9/lid5/totaalbedrag-belastingaanslag",
    "vervaldag-31-december": "BWBR0004770/art9/lid5/vervaldag-31-december",
    "vervaldag-laatste-dag-maand": "BWBR0004770/art9/lid5/vervaldag-laatste-dag-maand",
    "termijn-eindigt-voor-31-december": "BWBR0004770/art9/lid5/termijn-eindigt-voor-31-december",
    "afwijkend-boekjaar": "BWBR0004770/art9/lid5/afwijkend-boekjaar",
    "dagtekening-in-november-of-eerder": "BWBR0004770/art9/lid5/dagtekening-in-november-of-eerder",
    "31-december": "BWBR0004770/art9/lid5/31-december",
}

REGEL_ID_MAPPING = {
    "AR-9-1": "AR-BWBR0004770-art9-lid1-1",
    "AR-9-5a": "AR-BWBR0004770-art9-lid5-a",
    "AR-9-5b": "AR-BWBR0004770-art9-lid5-b",
    "AR-9-5c": "AR-BWBR0004770-art9-lid5-c",
    "AR-9-5d": "AR-BWBR0004770-art9-lid5-d",
    "AR-9-5e": "AR-BWBR0004770-art9-lid5-e",
    "AR-9-5f": "AR-BWBR0004770-art9-lid5-f",
    "AR-LI-9-1a": "AR-BWBR0024096-art9-par1-a",
    "AR-LI-9-1b": "AR-BWBR0024096-art9-par1-b",
}

SOORT_MAPPING = {
    "waar-niet-waar": "booleaans",
    "datum": "datum",
    "tekst": "tekst",
    "enumeratiewaarde": "enumeratie",
    "getal": "MIGRATIE-ONBEKEND",
}

SOORT_OVERRIDES = {
    "zes-weken": "tijdsduur",
    "een-maand-na-dagtekening": "tijdsduur",
    "telkens-een-maand-later": "tijdsduur",
    "maand-dagtekening-aanslagbiljet": "tijdsduur",
    "resterende-maanden-jaar": "MIGRATIE-ONBEKEND",  # integer (aantal maanden) — vereist handmatige beslissing
    "termijnbedrag": "monetair-bedrag",
    "totaalbedrag-belastingaanslag": "monetair-bedrag",
    "vervaldag-eerste-termijn": "datum",
    "vervaldag-volgende-termijnen": "datum",
    "vervaldag-31-december": "datum",
    "vervaldag-laatste-dag-maand": "datum",
    "31-december": "datum",
}

CSS_NAAR_JAS = {
    "rb": "rechtsbetrekking", "rs": "rechtssubject", "ro": "rechtsobject",
    "rf": "rechtsfeit", "vw": "voorwaarde", "ar": "afleidingsregel",
    "va": "variabele", "pa": "parameter", "ta": "tijdsaanduiding",
    "pl": "plaatsaanduiding", "db": "delegatiebevoegdheid", "bd": "brondefinitie", "op": "operator"
}

# ---------------------------------------------------------------------------
# Hulpfuncties
# ---------------------------------------------------------------------------

def slug_from_wikilink(wikilink: str) -> str:
    """Extraheert slug uit [[begrippen/slug]] of [[regels/id]] → 'slug' / 'id'"""
    m = re.search(r'\[\[(?:[^\]|/]+/)?([^\]|/]+)(?:\|[^\]]*)?\]\]', wikilink)
    return m.group(1) if m else wikilink


def bron_naar_annotatie_id(bron: str) -> str:
    """'Art. 9 lid 1 IW 1990' → 'BWBR0004770/art9/lid1'"""
    m = re.match(r'Art\.\s*(\w+)\s+lid\s+(\d+)\s+IW\s+1990', bron)
    if m:
        return f"BWBR0004770/art{m.group(1)}/lid{m.group(2)}"
    m = re.match(r'Art\.\s*(\w+)\s+IW\s+1990', bron)
    if m:
        return f"BWBR0004770/art{m.group(1)}"
    m = re.match(r'§\s*([\d.]+)\s+LI\s+2008', bron)
    if m:
        return f"BWBR0024096/par{m.group(1).replace('.', '-')}"
    return bron


def annotatie_link_naar_id(slug: str) -> str:
    """'art9-1' → 'BWBR0004770/art9/lid1', 'art9-5' → 'BWBR0004770/art9/lid5', etc."""
    # art9-1 → BWBR0004770/art9/lid1
    m = re.match(r'art(\d+)-(\d+)$', slug)
    if m:
        return f"BWBR0004770/art{m.group(1)}/lid{m.group(2)}"
    # art9-9-1 stijl (LI2008)
    m = re.match(r'art(\d+)-(\d+)-(\d+)$', slug)
    if m:
        return f"BWBR0024096/art{m.group(1)}/par{m.group(2)}-{m.group(3)}"
    return slug


def css_naar_jas(css: str) -> str:
    return CSS_NAAR_JAS.get(css, css)


def parse_begrip_body(body: str) -> tuple:
    """Extraheert (definitie_tekst, voorbeelden_md, kenmerken_md) uit body"""
    sections = {}
    current = None
    lines = []
    for line in body.split('\n'):
        if line.startswith('## '):
            if current:
                sections[current] = '\n'.join(lines).strip()
            current = line[3:].strip()
            lines = []
        elif current:
            lines.append(line)
    if current:
        sections[current] = '\n'.join(lines).strip()

    definitie = sections.get('Definitie', '')
    definitie = re.sub(r'^\*[^*]+\*\s*\*[^*]+\*\s*\n\n?', '', definitie).strip()

    return definitie, sections.get('Voorbeelden', ''), sections.get('Kenmerken', '')


def parse_regel_body(body: str) -> tuple:
    """Extraheert (formele_regel, toelichting, voorbeeldreeksen_list) uit body"""
    sections = {}
    current = None
    lines = []
    for line in body.split('\n'):
        if line.startswith('## '):
            if current:
                sections[current] = '\n'.join(lines).strip()
            current = line[3:].strip()
            lines = []
        elif current:
            lines.append(line)
    if current:
        sections[current] = '\n'.join(lines).strip()

    voorbeelden_md = sections.get('Voorbeeldreeksen', '')
    voorbeeldreeksen = parse_voorbeeldreeksen_tabel(voorbeelden_md)

    return (
        sections.get('Formele regel', ''),
        sections.get('Toelichting', ''),
        voorbeeldreeksen
    )


def parse_voorbeeldreeksen_tabel(md: str) -> list:
    """Parseer Markdown-tabel naar lijst van dicts"""
    rows = []
    lines = [l.strip() for l in md.split('\n') if l.strip().startswith('|')]
    # Sla header en separator over; [0] is header, daarna separator
    data_lines = []
    header_seen = False
    for line in lines:
        if re.match(r'\|[-| ]+\|', line):
            header_seen = True
            continue
        if header_seen:
            data_lines.append(line)
        # Als nog geen separator gezien, skip ook de headerregel
    for line in data_lines:
        cols = [c.strip() for c in line.strip('|').split('|')]
        if len(cols) < 3:
            continue
        juist_str = cols[2].lower()
        juist = 'ja' in juist_str
        toel = cols[3] if len(cols) > 3 else None
        rows.append({
            "invoerwaarden": cols[0],
            "verwachte-uitkomst": cols[1],
            "juridisch-juist": juist,
            "toelichting": toel if toel and toel != '—' else None
        })
    return rows


def parse_annotatietabel(body: str) -> list:
    """Parseer ## Annotatietabel sectie naar lijst van annotatierijen"""
    m = re.search(r'## Annotatietabel\s*\n(.*?)(?=\n## |\Z)', body, re.DOTALL)
    if not m:
        return []
    tabel_md = m.group(1)
    rows = []
    rij_nr = 0
    for line in tabel_md.split('\n'):
        if not line.strip().startswith('|') or re.match(r'\|[-| ]+\|', line.strip()):
            continue
        cols = [c.strip() for c in line.strip('|').split('|')]
        if len(cols) < 6 or cols[0] == 'Nr':
            continue
        rij_nr += 1
        begrip_link = cols[4].strip()
        begrip_slug = slug_from_wikilink(begrip_link) if begrip_link and begrip_link != '—' else None
        begrip_id = BEGRIP_ID_MAPPING.get(begrip_slug, begrip_slug) if begrip_slug else None

        jas = re.sub(r'\*\*([^*]+)\*\*', r'\1', cols[2]).strip()

        rows.append({
            "rij-id": f"r-{rij_nr:03d}",
            "markering": cols[1].strip('"').strip(),
            "jas-klasse": jas,
            "interpretatiemethode": cols[3].strip(),
            "begrip-id": begrip_id,
            "toelichting-klasse": "",
            "signalering": cols[5].strip() if len(cols) > 5 and cols[5].strip() != '—' else None
        })
    return rows


def parse_mermaid_diagram(body: str) -> dict:
    """Parseer ## Diagram sectie → {centrale-klasse, knopen, kanten}"""
    m = re.search(r'```mermaid\s*\ngraph\s+\w+\s*\n(.*?)```', body, re.DOTALL)
    if not m:
        return {"centrale-klasse": None, "knopen": [], "kanten": []}

    mermaid_body = m.group(1)
    knopen = []
    kanten = []

    for line in mermaid_body.split('\n'):
        line = line.strip()
        # Knoop: ID["label"]:::css
        kn = re.match(r'(\w+)\["([^"]+)"\]:::(\w+)', line)
        if kn:
            label = kn.group(2).replace('<br/>', ' ')
            jas = css_naar_jas(kn.group(3))
            knopen.append({"id": kn.group(1), "jas-klasse": jas, "label": label, "begrip-id": None})
            continue
        # Kant met label: A -->|label| B
        ka = re.match(r'(\w+)\s*-->\|([^|]+)\|\s*(\w+)', line)
        if ka:
            kanten.append({"van": ka.group(1), "naar": ka.group(3), "label": ka.group(2)})
            continue
        # Kant zonder label: A --- B
        ka2 = re.match(r'(\w+)\s+---\s+(\w+)', line)
        if ka2:
            kanten.append({"van": ka2.group(1), "naar": ka2.group(2), "label": None})

    if knopen:
        knoop_ids = [k["id"] for k in knopen]
        verbindingen = {kid: sum(1 for ka in kanten if ka["van"] == kid or ka["naar"] == kid)
                       for kid in knoop_ids}
        centrale_id = max(verbindingen, key=verbindingen.get) if verbindingen else knoop_ids[0]
        centrale_klasse = next((k["jas-klasse"] for k in knopen if k["id"] == centrale_id), None)
    else:
        centrale_klasse = None

    return {"centrale-klasse": centrale_klasse, "knopen": knopen, "kanten": kanten}


def artikel_naar_annotatie_id(artikel: str) -> str:
    """Frontmatter 'artikel' veld → annotatie-id"""
    m = re.match(r'Art\.\s*(\w+)\s+lid\s+(\d+)\s+IW\s+1990', artikel)
    if m:
        return f"BWBR0004770/art{m.group(1)}/lid{m.group(2)}"
    m = re.match(r'Art\.\s*(\w+)\s+IW\s+1990', artikel)
    if m:
        return f"BWBR0004770/art{m.group(1)}"
    m = re.match(r'§\s*([\d.]+)\s+LI\s+2008', artikel)
    if m:
        par = m.group(1).replace('.', '-')
        return f"BWBR0024096/par{par}"
    return artikel


def yaml_dump(data: dict) -> str:
    return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)


# ---------------------------------------------------------------------------
# Stap 1a: Begrippen migreren
# ---------------------------------------------------------------------------

def migrate_begrip(slug: str, fm: dict, body: str) -> tuple:
    """Migreer een begrip-noot. Retourneert (begrip_dict, extra_dict)."""
    begrip_id = BEGRIP_ID_MAPPING.get(slug)
    if not begrip_id:
        print(f"WAARSCHUWING: geen ID-mapping voor '{slug}'", file=sys.stderr)
        begrip_id = f"ONBEKEND/{slug}"

    oud_soort = fm.get("soort", "")
    nieuw_soort = SOORT_OVERRIDES.get(slug) or SOORT_MAPPING.get(oud_soort, "MIGRATIE-ONBEKEND")

    primaire_bron = fm.get("bron", "")
    alle_bronnen = fm.get("bronnen", [])
    if not alle_bronnen:
        alle_bronnen = [primaire_bron] if primaire_bron else []

    markeringen = []
    for i, bron in enumerate(alle_bronnen):
        markering_id = f"m-{i+1:03d}"
        bijdrage = "primair" if bron == primaire_bron else "aanvullend"
        peildatum = fm.get("peildatum", None)
        peildatum_str = str(peildatum) if peildatum else None
        markeringen.append({
            "markering-id": markering_id,
            "bron-annotatie-id": bron_naar_annotatie_id(bron),
            "tekst": fm.get("markering", ""),
            "interpretatiemethode": fm.get("interpretatiemethode", "grammaticaal"),
            "bijdrage": bijdrage,
            "bevestigd": True,
            "bevestigd-op": peildatum_str,
        })

    # Relaties converteren
    def resolve_list(items):
        return [BEGRIP_ID_MAPPING.get(slug_from_wikilink(w), slug_from_wikilink(w))
                for w in (items or [])]

    is_een_ids = resolve_list(fm.get("is-een", []))
    heeft_items = [
        {"begrip-id": BEGRIP_ID_MAPPING.get(slug_from_wikilink(w), slug_from_wikilink(w)),
         "kardinaliteit": "1:1"}
        for w in (fm.get("heeft", []) or [])
    ]
    leidt_tot_items = [
        {"begrip-id": BEGRIP_ID_MAPPING.get(slug_from_wikilink(w), slug_from_wikilink(w)),
         "relatie-soort": "causaal"}
        for w in (fm.get("leidt-tot", []) or [])
    ]

    relaties = {
        "is-een": is_een_ids,
        "heeft": heeft_items,
        "leidt-tot": leidt_tot_items,
    }

    # afleidingsregel-id
    ar_links = fm.get("afleidingsregels", []) or []
    afleidingsregel_id = None
    if ar_links:
        old_id = slug_from_wikilink(ar_links[0])
        afleidingsregel_id = REGEL_ID_MAPPING.get(old_id, old_id)

    definitie, voorbeelden, kenmerken = parse_begrip_body(body)

    geldigheid_van = fm.get("geldigheid-van", fm.get("peildatum", ""))
    geldigheid_van_str = str(geldigheid_van) if geldigheid_van else ""

    geldigheid_tot = fm.get("geldigheid-tot")
    # Lege string → None
    if geldigheid_tot == "" or geldigheid_tot is None:
        geldigheid_tot = None

    status = fm.get("status", "concept")
    if len(markeringen) > 1:
        status = "te-verrijken"

    # soort-id: True als "[id]" in de soort-string stond
    soort_id_flag = "[id]" in str(fm.get("soort", ""))

    begrip = {
        "begrip-id": begrip_id,
        "begripsnaam": fm.get("begripsnaam", slug),
        "aliases": fm.get("aliases", []) or [],
        "soort": nieuw_soort,
        "soort-id": soort_id_flag,
        "herkomst": fm.get("herkomst", "direct"),
        "status": status,
        "definitie": definitie,
        "definitie-versie": 1,
        "definitie-gebaseerd-op": ["m-001"],
        "markeringen": markeringen,
        "geldigheid-van": geldigheid_van_str,
        "geldigheid-tot": geldigheid_tot,
        "vervangen-door": None,
        "relaties": relaties,
        "identificatiebegrip": soort_id_flag,
        "afleidingsregel-id": afleidingsregel_id,
        "tussenresultaat": "tussenresultaat" in (fm.get("tags", []) or []),
    }

    extra = {
        "begrip-id": begrip_id,
        "slug": slug,
        "voorbeelden": voorbeelden,
        "kenmerken": kenmerken,
    }

    return begrip, extra


def step_extract_begrippen(vault_root: Path, staging_dir: Path) -> int:
    begrippen_dir = vault_root / "begrippen"
    out_dir = staging_dir / "begrippen"
    out_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for md_file in sorted(begrippen_dir.glob("*.md")):
        if md_file.name == "index.md":
            continue
        slug = md_file.stem
        post = frontmatter.load(str(md_file))
        fm = dict(post.metadata)
        body = post.content

        begrip, extra = migrate_begrip(slug, fm, body)

        # Bestandsnaam = laatste pad-segment van begrip-id
        begrip_id = begrip["begrip-id"]
        file_slug = begrip_id.split("/")[-1]

        # YAML opslaan
        yaml_path = out_dir / f"{file_slug}.yaml"
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_dump(begrip))

        # Extra JSON opslaan in aparte submap zodat de validator het niet oppikt
        extra_dir = out_dir / "extra"
        extra_dir.mkdir(exist_ok=True)
        extra_path = extra_dir / f"{file_slug}.extra.json"
        with open(extra_path, 'w', encoding='utf-8') as f:
            json.dump(extra, f, ensure_ascii=False, indent=2)

        count += 1
        print(f"  begrip: {slug} → {file_slug}.yaml")

    return count


# ---------------------------------------------------------------------------
# Stap 1b: Regels migreren
# ---------------------------------------------------------------------------

def migrate_regel(regel_id_oud: str, fm: dict, body: str) -> dict:
    nieuw_id = REGEL_ID_MAPPING.get(regel_id_oud, regel_id_oud)

    afgeleid_van = fm.get("afgeleid-van", "")
    afgeleid_slug = slug_from_wikilink(afgeleid_van)
    annotatie_id = annotatie_link_naar_id(afgeleid_slug)

    bepaalt = fm.get("bepaalt", "")
    uitvoer_slug = slug_from_wikilink(bepaalt)
    uitvoer_id = BEGRIP_ID_MAPPING.get(uitvoer_slug, uitvoer_slug)

    rf_link = fm.get("rechtsfeit", "")
    rf_slug = slug_from_wikilink(rf_link) if rf_link else None
    rechtsfeit_id = BEGRIP_ID_MAPPING.get(rf_slug) if rf_slug else None

    invoer_ids = [
        BEGRIP_ID_MAPPING.get(slug_from_wikilink(w), slug_from_wikilink(w))
        for w in (fm.get("invoer", []) or [])
    ]
    uitvoer_ids = [
        BEGRIP_ID_MAPPING.get(slug_from_wikilink(w), slug_from_wikilink(w))
        for w in (fm.get("uitvoer", []) or [])
    ]
    if uitvoer_id and uitvoer_id not in uitvoer_ids:
        uitvoer_ids = [uitvoer_id] + uitvoer_ids

    formele_regel, toelichting, voorbeeldreeksen = parse_regel_body(body)

    # Artikel en lid afleiden uit nieuw_id
    # AR-BWBR0004770-art9-lid1-1 → artikel=9, lid=1
    # AR-BWBR0004770-art9-lid5-a → artikel=9, lid=5
    # AR-BWBR0024096-art9-par1-a → artikel=9, lid=par1
    art_m = re.search(r'-art(\d+)-', nieuw_id)
    artikel = art_m.group(1) if art_m else "9"
    lid_m = re.search(r'-lid(\d+)-', nieuw_id)
    par_m = re.search(r'-par([\d-]+)-', nieuw_id)
    if lid_m:
        lid = lid_m.group(1)
    elif par_m:
        lid = f"par{par_m.group(1)}"
    else:
        lid = ""

    peildatum = fm.get("peildatum", "")
    peildatum_str = str(peildatum) if peildatum else ""

    operators_raw = fm.get("operators", []) or []
    if isinstance(operators_raw, str):
        operators_raw = [operators_raw]
    operators = list(operators_raw)

    return {
        "regel-id": nieuw_id,
        "naam": fm.get("naam", ""),
        "soort": fm.get("soort", "Beslissingsregel"),
        "bwb-id": fm.get("bwb-id", "BWBR0004770"),
        "artikel": artikel,
        "lid": lid,
        "peildatum": peildatum_str,
        "annotatie-id": annotatie_id,
        "rechtsfeit-id": rechtsfeit_id,
        "invoer": invoer_ids,
        "uitvoer": uitvoer_ids,
        "operators": operators,
        "formele-regel": formele_regel,
        "toelichting": toelichting,
        "voorbeeldreeksen": voorbeeldreeksen,
        "tussenresultaat": False,
    }


def step_extract_regels(vault_root: Path, staging_dir: Path) -> int:
    regels_dir = vault_root / "regels"
    out_dir = staging_dir / "regels"
    out_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for md_file in sorted(regels_dir.glob("AR-*.md")):
        regel_id_oud = md_file.stem
        post = frontmatter.load(str(md_file))
        fm = dict(post.metadata)
        body = post.content

        regel = migrate_regel(regel_id_oud, fm, body)
        nieuw_id = regel["regel-id"]

        yaml_path = out_dir / f"{nieuw_id}.yaml"
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_dump(regel))

        count += 1
        print(f"  regel: {regel_id_oud} → {nieuw_id}.yaml")

    return count


# ---------------------------------------------------------------------------
# Stap 1c: Annotaties migreren
# ---------------------------------------------------------------------------

def parse_wetstekst_uit_body(body: str) -> str:
    """Extraheer de wetstekst uit het '## Wetstekst ...' gedeelte van de body."""
    m = re.search(r'## Wetstekst[^\n]*\n\s*\n(.*?)(?=\n## |\Z)', body, re.DOTALL)
    if not m:
        return ""
    # Verwijder blockquote-markeringen (> ) en trim
    tekst = m.group(1).strip()
    tekst = re.sub(r'^>\s?', '', tekst, flags=re.MULTILINE)
    # Verwijder bold-markeringen voor lidnummers **1**
    tekst = re.sub(r'\*\*(\d+)\*\*\s*', '', tekst)
    return tekst.strip()


def parse_kruisreferenties_naar_schema(kruisrefs_raw: list, bwb_id: str) -> list:
    """Converteer ruwe kruisreferentie-strings naar schema-conform formaat."""
    result = []
    for ref in kruisrefs_raw:
        # Probeer te parsen: "Art. 2 IW 1990", "Algemene termijnenwet", etc.
        m = re.match(r'Art\.\s*(\w+)\s+IW\s+1990', ref)
        if m:
            result.append({
                "doel-bwb-id": "BWBR0004770",
                "doel-artikel": m.group(1),
                "doel-lid": None,
                "richting": "forward",
                "confidence": 1.0,
                "ruwe-tekst": ref,
            })
            continue
        m = re.match(r'Art\.\s*(\w+)\s+(Wet\s+\w+.*?)$', ref)
        if m:
            result.append({
                "doel-bwb-id": "ONBEKEND",
                "doel-artikel": m.group(1),
                "doel-lid": None,
                "richting": "forward",
                "confidence": 0.8,
                "ruwe-tekst": ref,
            })
            continue
        # Generiek geval (bijv. Algemene termijnenwet, Art. 167 Douanewetboek)
        result.append({
            "doel-bwb-id": "ONBEKEND",
            "doel-artikel": None,
            "doel-lid": None,
            "richting": "forward",
            "confidence": 0.8,
            "ruwe-tekst": ref,
        })
    return result


def is_lid_annotatie(fm: dict) -> bool:
    """True als dit een lid-annotatie is (niet een index-annotatie)."""
    artikel = fm.get("artikel", "")
    return "lid" in artikel.lower() or "§" in artikel


def is_index_annotatie(fm: dict) -> bool:
    """True als dit een index-annotatie is."""
    artikel = fm.get("artikel", "")
    return not is_lid_annotatie(fm) and "§" not in artikel


def migrate_lid_annotatie(fm: dict, body: str) -> tuple:
    """Migreer een lid-annotatie naar schema. Retourneert (annotatie_id, annotatie_dict)."""
    artikel_str = fm.get("artikel", "")
    annotatie_id = artikel_naar_annotatie_id(artikel_str)
    bwb_id = fm.get("bwb-id", "BWBR0004770")

    # Extraheer wet-naam en artikel/lid
    m_iw = re.match(r'Art\.\s*(\w+)\s+lid\s+(\d+)\s+IW\s+1990', artikel_str)
    m_li = re.match(r'§\s*([\d.]+)\s+LI\s+2008', artikel_str)

    if m_iw:
        wet = "IW 1990"
        artikel_nr = m_iw.group(1)
        lid_nr = m_iw.group(2)
    elif m_li:
        wet = "LI 2008"
        par = m_li.group(1)
        artikel_nr = par.split(".")[0]
        lid_nr = par  # bijv. "9.9.1"
        # LI2008 annotatie-id heeft een speciaal patroon dat buiten het schema valt
    else:
        wet = ""
        artikel_nr = ""
        lid_nr = ""

    peildatum = fm.get("peildatum", "")
    peildatum_str = str(peildatum) if peildatum else ""

    kruisrefs_raw = fm.get("kruisreferenties", []) or []
    kruisreferenties = parse_kruisreferenties_naar_schema(kruisrefs_raw, bwb_id)

    annotatierijen = parse_annotatietabel(body)
    diagram = parse_mermaid_diagram(body)
    wetstekst = parse_wetstekst_uit_body(body)

    annotatie = {
        "annotatie-id": annotatie_id,
        "bwb-id": bwb_id,
        "wet": wet,
        "artikel": artikel_nr,
        "lid": lid_nr,
        "peildatum": peildatum_str,
        "structuurpositie": fm.get("structuurpositie", ""),
        "wetstekst": wetstekst,
        "annotatierijen": annotatierijen,
        "diagram": diagram,
        "kruisreferenties": kruisreferenties,
    }

    return annotatie_id, annotatie


def migrate_index_annotatie(fm: dict, body: str) -> tuple:
    """Migreer een index-annotatie naar schema. Retourneert (artikel_id, annotatie_dict)."""
    artikel_str = fm.get("artikel", "")
    bwb_id = fm.get("bwb-id", "BWBR0004770")

    # artikel_id = bwb_id/artN
    m_iw = re.match(r'Art\.\s*(\w+)\s+IW\s+1990', artikel_str)
    if m_iw:
        artikel_id = f"{bwb_id}/art{m_iw.group(1)}"
        wet = "IW 1990"
        artikel_nr = m_iw.group(1)
    else:
        artikel_id = bwb_id + "/art9"
        wet = ""
        artikel_nr = "9"

    peildatum = fm.get("peildatum", "")
    peildatum_str = str(peildatum) if peildatum else ""

    # Leden-noten links → annotatie-ids
    leden_noten = fm.get("leden-noten", []) or []
    leden_annotaties = []
    for ln in leden_noten:
        slug = slug_from_wikilink(ln)
        leden_annotaties.append(annotatie_link_naar_id(slug))

    # Kruisreferenties als strings (index-annotatie schema verwacht strings)
    kruisrefs_raw = fm.get("kruisreferenties", []) or []

    annotatie = {
        "artikel-id": artikel_id,
        "bwb-id": bwb_id,
        "wet": wet,
        "artikel": artikel_nr,
        "peildatum": peildatum_str,
        "structuurpositie": fm.get("structuurpositie", ""),
        "leden-annotaties": leden_annotaties,
        "kruisreferenties": kruisrefs_raw,  # strings, conform schema
    }

    return artikel_id, annotatie


def migrate_annotatie(md_file: Path, fm: dict, body: str) -> tuple:
    """Retourneert (id, annotatie_dict, schema_type)"""
    if is_lid_annotatie(fm):
        annotatie_id, annotatie = migrate_lid_annotatie(fm, body)
        return annotatie_id, annotatie, "lid"
    else:
        artikel_id, annotatie = migrate_index_annotatie(fm, body)
        return artikel_id, annotatie, "index"


def annotatie_id_naar_pad(annotatie_id: str) -> str:
    """'BWBR0004770/art9/lid1' → 'BWBR0004770/art9-lid1.json'"""
    parts = annotatie_id.split("/")
    if len(parts) == 3:
        bwb, art, lid = parts
        return f"{bwb}/{art}-{lid}.json"
    elif len(parts) == 2:
        bwb, art = parts
        return f"{bwb}/{art}.json"
    elif len(parts) >= 2:
        bwb = parts[0]
        rest = "-".join(parts[1:])
        return f"{bwb}/{rest}.json"
    return f"{annotatie_id}.json"


def step_extract_annotaties(vault_root: Path, staging_dir: Path) -> int:
    out_base = staging_dir / "annotaties"
    count = 0

    annotatie_files = []
    for subdir in ["iw1990", "li2008"]:
        subpath = vault_root / "annotaties" / subdir
        if subpath.exists():
            for md_file in sorted(subpath.glob("*.md")):
                annotatie_files.append(md_file)

    for md_file in annotatie_files:
        post = frontmatter.load(str(md_file))
        fm = dict(post.metadata)
        body = post.content

        annotatie_id, annotatie, schema_type = migrate_annotatie(md_file, fm, body)

        # Uitvoerpad afleiden
        rel_pad = annotatie_id_naar_pad(annotatie_id)
        out_path = out_base / rel_pad
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(annotatie, f, ensure_ascii=False, indent=2)

        count += 1
        print(f"  annotatie: {md_file.name} → {rel_pad} ({schema_type})")

    return count


# ---------------------------------------------------------------------------
# Stap 2: Resolve
# ---------------------------------------------------------------------------

def step_resolve(vault_root: Path, staging_dir: Path) -> None:
    begrippen_staging = staging_dir / "begrippen"
    alle_bekende_ids = set(BEGRIP_ID_MAPPING.values())

    unresolved = []

    for yaml_file in sorted(begrippen_staging.glob("*.yaml")):
        if yaml_file.suffix != ".yaml":
            continue
        with open(yaml_file, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if not data:
            continue

        relaties = data.get("relaties", {})
        for rel_type, items in relaties.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, str):
                        bid = item
                    elif isinstance(item, dict):
                        bid = item.get("begrip-id", "")
                    else:
                        continue
                    if bid and bid not in alle_bekende_ids and not bid.startswith("ONBEKEND/"):
                        unresolved.append({
                            "bestand": yaml_file.name,
                            "relatie-type": rel_type,
                            "begrip-id": bid,
                        })

    out_path = vault_root / "migratie" / "unresolved-links.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(unresolved, f, ensure_ascii=False, indent=2)

    print(f"\nStap 2 — resolve: {len(unresolved)} onopgeloste links → migratie/unresolved-links.json")
    if unresolved:
        for item in unresolved:
            print(f"  {item['bestand']}: {item['relatie-type']} → {item['begrip-id']}")


# ---------------------------------------------------------------------------
# Stap 3: Enrichment
# ---------------------------------------------------------------------------

ENRICHMENT_QUEUE_HANDMATIG = [
    {
        "begrip-id": "BWBR0004770/art9/lid1/dagtekening-aanslagbiljet",
        "reden": "Dubbelclassificatie: tijdsaanduiding (rij 5 art9-1) + rechtsfeit (rij 6 art9-1). "
                 "In art9-5 context is het begrip hergebruikt als ankerpunt voor termijnenberekening.",
        "advies": "splitsen-of-verfijnen",
    },
    {
        "begrip-id": "BWBR0004770/art9/lid5/termijnbedrag",
        "reden": "Rijen 17 en 18 in art9-5 verwijzen beide naar hetzelfde begrip termijnbedrag "
                 "(rij 17: afleidingsregel 'gelijke', rij 18: variabele 'gelijke termijnen'). "
                 "Dubbele markering voor hetzelfde begrip vanuit verschillende JAS-klassen.",
        "advies": "bevestigen-of-samenvoegen",
    },
]


def step_enrichment(vault_root: Path, staging_dir: Path) -> None:
    begrippen_staging = staging_dir / "begrippen"
    vandaag = str(date.today())

    queue = []

    for yaml_file in sorted(begrippen_staging.glob("*.yaml")):
        with open(yaml_file, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if not data:
            continue

        markeringen = data.get("markeringen", [])
        if len(markeringen) > 1:
            # Delta-analyse
            bron_ids = [m.get("bron-annotatie-id", "") for m in markeringen]
            bijdragen = [m.get("bijdrage", "") for m in markeringen]
            delta = (
                f"Begrip heeft {len(markeringen)} bronnen: "
                + ", ".join(f"{b} ({bj})" for b, bj in zip(bron_ids, bijdragen))
                + "."
            )

            # Zoek handmatige toelichting
            handmatig = next(
                (h for h in ENRICHMENT_QUEUE_HANDMATIG
                 if h["begrip-id"] == data.get("begrip-id")),
                None
            )
            if handmatig:
                delta += " " + handmatig["reden"]
                advies = handmatig["advies"]
            else:
                advies = "afsplitsen"

            queue.append({
                "begrip-id": data["begrip-id"],
                "begripsnaam": data.get("begripsnaam", ""),
                "aangemeld-op": vandaag,
                "markeringen-count": len(markeringen),
                "markeringen": markeringen,
                "delta-analyse": delta,
                "advies": advies,
                "beslissing": None,
            })

    # Voeg handmatige items toe die niet door automatische detectie zijn gevonden
    auto_ids = {item["begrip-id"] for item in queue}
    for h in ENRICHMENT_QUEUE_HANDMATIG:
        if h["begrip-id"] not in auto_ids:
            # Laad het begrip uit staging
            slug = h["begrip-id"].split("/")[-1]
            yaml_path = begrippen_staging / f"{slug}.yaml"
            if yaml_path.exists():
                with open(yaml_path, encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                markeringen = data.get("markeringen", []) if data else []
                queue.append({
                    "begrip-id": h["begrip-id"],
                    "begripsnaam": data.get("begripsnaam", slug) if data else slug,
                    "aangemeld-op": vandaag,
                    "markeringen-count": len(markeringen),
                    "markeringen": markeringen,
                    "delta-analyse": h["reden"],
                    "advies": h["advies"],
                    "beslissing": None,
                })

    rapporten_dir = vault_root / "rapporten"
    rapporten_dir.mkdir(parents=True, exist_ok=True)
    out_path = rapporten_dir / "enrichment-queue.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

    print(f"\nStap 3 — enrichment: {len(queue)} begrippen in enrichment-queue → rapporten/enrichment-queue.json")
    for item in queue:
        print(f"  {item['begrip-id']} (n={item['markeringen-count']}, advies={item['advies']})")


# ---------------------------------------------------------------------------
# Stap 4: --commit
# ---------------------------------------------------------------------------

def step_commit(vault_root: Path, staging_dir: Path) -> None:
    archief_base = vault_root / "migratie" / "archief"

    totalen = {"begrippen": 0, "regels": 0, "annotaties": 0}

    # Begrippen: staging → begrippen/
    out_begrippen = vault_root / "begrippen"
    for yaml_file in sorted((staging_dir / "begrippen").glob("*.yaml")):
        dest = out_begrippen / yaml_file.name
        shutil.copy2(str(yaml_file), str(dest))
        totalen["begrippen"] += 1

    # Regels: staging → regels/
    out_regels = vault_root / "regels"
    for yaml_file in sorted((staging_dir / "regels").glob("*.yaml")):
        dest = out_regels / yaml_file.name
        shutil.copy2(str(yaml_file), str(dest))
        totalen["regels"] += 1

    # Annotaties: staging → annotaties/
    out_annotaties = vault_root / "annotaties"
    for json_file in sorted((staging_dir / "annotaties").rglob("*.json")):
        rel = json_file.relative_to(staging_dir / "annotaties")
        dest = out_annotaties / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(json_file), str(dest))
        totalen["annotaties"] += 1

    # Archiveer oude .md bestanden
    # begrippen/*.md
    archief_begrippen = archief_base / "begrippen"
    archief_begrippen.mkdir(parents=True, exist_ok=True)
    for md_file in sorted((vault_root / "begrippen").glob("*.md")):
        shutil.move(str(md_file), str(archief_begrippen / md_file.name))

    # regels/AR-*.md
    archief_regels = archief_base / "regels"
    archief_regels.mkdir(parents=True, exist_ok=True)
    for md_file in sorted((vault_root / "regels").glob("AR-*.md")):
        shutil.move(str(md_file), str(archief_regels / md_file.name))

    # annotaties/**/*.md
    archief_annotaties = archief_base / "annotaties"
    archief_annotaties.mkdir(parents=True, exist_ok=True)
    for md_file in sorted((vault_root / "annotaties").rglob("*.md")):
        rel = md_file.relative_to(vault_root / "annotaties")
        dest = archief_annotaties / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(md_file), str(dest))

    print(f"\n--commit voltooid:")
    print(f"  begrippen gemigreerd: {totalen['begrippen']}")
    print(f"  regels gemigreerd:    {totalen['regels']}")
    print(f"  annotaties gemigreerd:{totalen['annotaties']}")
    print(f"  oud-bestanden gearchiveerd naar migratie/archief/")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Vault migratiescript")
    parser.add_argument("--vault-root", default=".", help="Pad naar vault root")
    parser.add_argument("--step", choices=["extract", "resolve", "enrichment"],
                        help="Voer één stap uit")
    parser.add_argument("--all", action="store_true", dest="all_steps",
                        help="Voer alle stappen achtereenvolgens uit")
    parser.add_argument("--commit", action="store_true",
                        help="Productie-commit: verplaats staging naar vault")
    args = parser.parse_args()

    vault_root = Path(args.vault_root).resolve()
    staging_dir = vault_root / "migratie" / "staging"
    staging_dir.mkdir(parents=True, exist_ok=True)

    if args.commit:
        print("=== --commit: staging naar vault ===")
        step_commit(vault_root, staging_dir)
        return

    steps = []
    if args.all_steps:
        steps = ["extract", "resolve", "enrichment"]
    elif args.step:
        steps = [args.step]
    else:
        parser.print_help()
        sys.exit(1)

    for step in steps:
        if step == "extract":
            print("=== Stap 1a: begrippen ===")
            n_b = step_extract_begrippen(vault_root, staging_dir)
            print(f"  → {n_b} begrippen gemigreerd\n")

            print("=== Stap 1b: regels ===")
            n_r = step_extract_regels(vault_root, staging_dir)
            print(f"  → {n_r} regels gemigreerd\n")

            print("=== Stap 1c: annotaties ===")
            n_a = step_extract_annotaties(vault_root, staging_dir)
            print(f"  → {n_a} annotaties gemigreerd\n")

        elif step == "resolve":
            step_resolve(vault_root, staging_dir)

        elif step == "enrichment":
            step_enrichment(vault_root, staging_dir)


if __name__ == "__main__":
    main()
