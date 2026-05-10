#!/usr/bin/env python3
"""
generate_webapp.py — Genereer statische webapp (Belastingdienst-stijl) uit vault-data.

Gebruik:
    tools/.venv/bin/python tools/generate_webapp.py [--vault-root .] [--out webapp]
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml


def slugify(s: str) -> str:
    return re.sub(r'[^a-z0-9-]', '', s.lower().replace('/', '-').replace('_', '-'))


JAS_KLASSE_TO_ABBR: dict[str, str] = {
    "rechtssubject": "rs", "rechtsobject": "ro", "rechtsbetrekking": "rb",
    "rechtsfeit": "rf", "voorwaarde": "vw", "afleidingsregel": "ar",
    "variabele": "va", "parameter": "pa", "tijdsaanduiding": "ta",
    "plaatsaanduiding": "pl", "delegatiebevoegdheid": "db", "brondefinitie": "bd", "operator": "op",
}


def _text_color_for_bg(hex_color: str) -> str:
    r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return ",color:#fff" if lum < 140 else ""


def diagram_to_mermaid(diagram: dict) -> str:
    if not diagram or not diagram.get("knopen"):
        return ""
    lines = ["graph LR"]
    classes_used: set[str] = set()
    for knoop in diagram["knopen"]:
        nid = knoop["id"]
        jk = knoop["jas-klasse"]
        abbr = JAS_KLASSE_TO_ABBR.get(jk, "xx")
        classes_used.add(jk)
        label = knoop.get("label", jk)
        parts = label.split(" ", 1)
        display = f"{parts[0]}<br/>{parts[1]}" if len(parts) == 2 else label
        display = display.replace('"', '&quot;')
        lines.append(f'    {nid}["{display}"]:::{abbr}')
    for kant in diagram.get("kanten") or []:
        van, naar = kant["van"], kant["naar"]
        lbl = kant.get("label")
        lines.append(f'    {van} -->|{lbl}| {naar}' if lbl else f'    {van} --- {naar}')
    lines.append("")
    for jk in sorted(classes_used):
        abbr = JAS_KLASSE_TO_ABBR.get(jk, "xx")
        c = JAS_KLEUREN.get(jk, "#888")
        lines.append(f'    classDef {abbr} fill:{c}{_text_color_for_bg(c)}')
    return "\n".join(lines)


JAS_KLEUREN: dict[str, str] = {
    "rechtssubject": "#4472C4",
    "rechtsobject": "#70AD47",
    "rechtsbetrekking": "#FF0000",
    "rechtsfeit": "#FFC000",
    "voorwaarde": "#7030A0",
    "afleidingsregel": "#00B0F0",
    "variabele": "#92D050",
    "tijdsaanduiding": "#F4B942",
    "operator": "#808080",
    "parameter": "#FFD966",
    "plaatsaanduiding": "#9DC3E6",
    "delegatiebevoegdheid": "#C9C9C9",
}

CSS = """/* Belastingdienst kennismodel — gegenereerd */
:root {
  --primary: #0047A0;
  --primary-hover: #003277;
  --primary-light: #E8F0FE;
  --accent: #E17000;
  --bg: #F4F5F7;
  --card-bg: #FFFFFF;
  --text: #1A1A1A;
  --text-secondary: #4B5563;
  --text-muted: #9CA3AF;
  --border: #E5E7EB;
  --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-hover: 0 4px 12px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06);
  --success: #1E7E34;
  --success-bg: #E6F4EA;
  --error: #D32F2F;
  --error-bg: #FDECEA;
  --warning: #E65100;
  --warning-bg: #FFF3E0;
  --radius: 8px;
  --nav-height: 56px;
  --max-width: 1200px;
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
[data-theme="dark"] {
  --primary: #3B82F6;
  --primary-hover: #60A5FA;
  --primary-light: #1E3A5F;
  --bg: #0F172A;
  --card-bg: #1E293B;
  --text: #F1F5F9;
  --text-secondary: #CBD5E1;
  --text-muted: #64748B;
  --border: #334155;
  --shadow: 0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2);
  --shadow-hover: 0 4px 12px rgba(0,0,0,0.4), 0 2px 4px rgba(0,0,0,0.3);
  --success-bg: #064E3B;
  --error-bg: #7F1D1D;
  --warning-bg: #78350F;
}
.mermaid {
  min-height: 120px;
  background: var(--card-bg);
  padding: 0.5rem 0;
  overflow-x: auto;
}
.mermaid svg {
  max-width: 100%;
  height: auto;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{font-size:100%;-webkit-text-size-adjust:100%}
body{font-family:var(--font);color:var(--text);background:var(--bg);line-height:1.6;min-height:100vh;display:flex;flex-direction:column}
img,svg{display:block;max-width:100%}
a{color:var(--primary);text-decoration:none}
a:hover{text-decoration:underline}
::selection{background:var(--primary);color:#fff}
.container{width:100%;max-width:var(--max-width);margin:0 auto;padding:0 1rem}
@media(min-width:768px){.container{padding:0 1.5rem}}

/* Header */
.nav{background:var(--primary);position:sticky;top:0;z-index:100;height:var(--nav-height)}
.nav .container{display:flex;align-items:center;height:100%;gap:0.5rem}
.nav-logo{color:#fff;font-weight:700;font-size:clamp(0.9rem,2.5vw,1.1rem);white-space:nowrap;display:flex;align-items:center;gap:0.5rem}
.nav-logo span{opacity:0.75;font-weight:400;display:none}
@media(min-width:480px){.nav-logo span{display:inline}}
.nav-links{display:flex;gap:0.25rem;margin-left:auto;align-items:center;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}
.nav-links::-webkit-scrollbar{display:none}
.nav-links a{color:rgba(255,255,255,0.85);font-size:clamp(0.75rem,2vw,0.875rem);padding:0.35rem 0.5rem;border-radius:4px;white-space:nowrap;transition:background 0.15s,color 0.15s}
.nav-links a:hover,.nav-links a.active{background:rgba(255,255,255,0.15);color:#fff;text-decoration:none}
.nav-links a.active{font-weight:600}

/* Dark mode toggle */
.dark-toggle{background:none;border:1px solid rgba(255,255,255,0.3);color:#fff;border-radius:4px;padding:0.3rem 0.45rem;cursor:pointer;font-size:0.85rem;line-height:1;transition:background 0.15s;margin-left:0.25rem;flex-shrink:0}
.dark-toggle:hover{background:rgba(255,255,255,0.15)}

/* Main content */
main{flex:1;padding:1.5rem 0}
@media(min-width:768px){main{padding:2rem 0}}

/* Cards */
.card{background:var(--card-bg);border-radius:var(--radius);box-shadow:var(--shadow);padding:1.25rem;margin-bottom:1rem;transition:box-shadow 0.2s}
@media(min-width:480px){.card{padding:1.5rem}}
.card:hover{box-shadow:var(--shadow-hover)}
.card-title{font-size:0.875rem;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.75rem;padding-bottom:0.5rem;border-bottom:1px solid var(--border)}
.card h2{font-size:1.1rem;color:var(--primary);margin-bottom:0.75rem}

/* Grids */
.stat-grid{display:grid;grid-template-columns:1fr;gap:0.75rem;margin-bottom:1.5rem}
@media(min-width:480px){.stat-grid{grid-template-columns:repeat(2,1fr)}}
@media(min-width:768px){.stat-grid{grid-template-columns:repeat(4,1fr)}}
.dash-grid{display:grid;grid-template-columns:1fr;gap:1rem;margin-bottom:1.5rem}
@media(min-width:768px){.dash-grid{grid-template-columns:repeat(3,1fr)}}
.card-grid{display:grid;grid-template-columns:1fr;gap:0.75rem}
@media(min-width:768px){.card-grid{grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}}

/* Stat cards */
.stat-card{text-align:center;padding:1.25rem}
.stat-nr{font-size:clamp(1.8rem,5vw,2.5rem);font-weight:700;color:var(--primary);line-height:1.2}
.stat-label{font-size:0.8rem;color:var(--text-muted);margin-top:0.25rem}

/* Headings */
h1{font-size:clamp(1.3rem,4vw,1.8rem);font-weight:700;color:var(--text);margin-bottom:0.5rem}
h2{font-size:clamp(1.1rem,3vw,1.3rem);color:var(--text);margin-bottom:0.75rem}
.subtitle{color:var(--text-muted);font-size:0.9rem;margin-bottom:1.5rem}

/* Badges / Tags */
.card ul li, .card ol li { word-break: break-all; overflow-wrap: break-word; }
.card a { word-break: break-all; overflow-wrap: break-word; }
.tag{display:inline-block;padding:0.15rem 0.45rem;border-radius:4px;font-size:0.7rem;font-weight:600;color:#fff;margin:0.1rem;white-space:nowrap;line-height:1.4}
.badge{display:inline-block;font-size:0.7rem;padding:0.15rem 0.45rem;border-radius:4px;font-weight:600;white-space:nowrap;line-height:1.4}
.badge-concept{background:var(--warning-bg);color:var(--warning)}
.badge-definitief{background:var(--success-bg);color:var(--success)}
.badge-vervallen{background:var(--border);color:var(--text-muted)}
.badge-type{background:var(--primary-light);color:var(--primary)}
.badge-soort{background:var(--border);color:var(--text-secondary)}
.badge-status{background:var(--warning-bg);color:var(--warning)}

/* Lists */
.item-list{list-style:none}
.item-list li{display:flex;flex-wrap:wrap;align-items:center;gap:0.5rem;padding:0.75rem 0;border-bottom:1px solid var(--border);cursor:pointer;transition:background 0.15s;border-radius:4px;margin:0 -0.5rem;padding:0.75rem 0.5rem}
.item-list li:hover{background:var(--primary-light)}
.item-list li:last-child{border-bottom:none}
.item-list .item-title{flex:1;min-width:150px;font-weight:500;color:var(--text)}
.item-list .item-meta{font-size:0.8rem;color:var(--text-muted);width:100}
@media(min-width:480px){.item-list .item-meta{width:auto}}
.item-list a.item-title{color:var(--primary)}

/* Table */
.prop-table{width:100%;border-collapse:collapse;font-size:0.9rem}
.prop-table td{padding:0.4rem 0;border-bottom:1px solid var(--border);vertical-align:top}
.prop-table td:first-child{color:var(--text-muted);width:35%;padding-right:1rem}
.prop-table tr:last-child td{border-bottom:none}

/* Definitions */
.def-block{background:var(--primary-light);border-left:3px solid var(--primary);padding:1rem;border-radius:0 var(--radius) var(--radius) 0;margin-bottom:1rem;font-size:0.95rem;line-height:1.7}

/* Wetstekst */
.wetstekst{background:var(--card-bg);border:1px solid var(--border);border-left:3px solid var(--primary);padding:1rem;border-radius:0 var(--radius) var(--radius) 0;margin-bottom:1rem;font-style:italic;font-size:0.95rem;line-height:1.7;color:var(--text-secondary)}

/* Annotatie rijen */
.ann-table{width:100%;border-collapse:collapse;font-size:0.85rem}
.ann-table th{text-align:left;padding:0.5rem;color:var(--text-muted);font-weight:600;border-bottom:2px solid var(--border);font-size:0.75rem;text-transform:uppercase;letter-spacing:0.05em}
.ann-table td{padding:0.5rem;border-bottom:1px solid var(--border);vertical-align:middle}
.ann-table tr:hover{background:var(--primary-light)}
.ann-table .mark-text{font-weight:500}
.signalering{font-size:0.8rem;color:var(--warning);margin-top:0.5rem;padding:0.5rem;background:var(--warning-bg);border-radius:4px;display:flex;align-items:flex-start;gap:0.4rem}

/* Voorbeeldreeksen */
.voorbeeld{padding:0.75rem;margin:0.5rem 0;border-left:3px solid var(--success);background:var(--success-bg);border-radius:0 var(--radius) var(--radius) 0;font-size:0.85rem;border:1px solid var(--border);border-left:3px solid var(--success)}
.voorbeeld.ongeldig{border-left-color:var(--error);background:var(--error-bg);border-left:3px solid var(--error)}
.voorbeeld-label{font-weight:700;color:var(--success)}
.voorbeeld.ongeldig .voorbeeld-label{color:var(--error)}

/* Detail pagina layout */
.detail-layout{display:grid;grid-template-columns:1fr;gap:1rem}
@media(min-width:768px){.detail-layout{grid-template-columns:1fr 300px}}

/* Formele regel box */
.regel-box{background:var(--card-bg);border:1px solid var(--border);border-left:3px solid var(--accent);padding:1rem;border-radius:0 var(--radius) var(--radius) 0;margin-bottom:1rem;font-family:Georgia,"Times New Roman",serif;font-size:0.95rem;line-height:1.7;white-space:pre-wrap}

/* Zoekpagina */
.search-input{width:100%;padding:0.75rem 1rem;border:2px solid var(--border);border-radius:var(--radius);font-size:1rem;background:var(--card-bg);color:var(--text);transition:border-color 0.2s;margin-bottom:1rem}
.search-input:focus{outline:none;border-color:var(--primary)}
.search-filters{display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:1rem}
.filter-chip{padding:0.3rem 0.75rem;border-radius:20px;border:1px solid var(--border);background:var(--card-bg);color:var(--text-secondary);font-size:0.8rem;cursor:pointer;transition:all 0.15s}
.filter-chip.active,.filter-chip:hover{border-color:var(--primary);background:var(--primary-light);color:var(--primary)}
.search-result{padding:0.75rem;border-bottom:1px solid var(--border);cursor:pointer;transition:background 0.15s;border-radius:4px;margin:0 -0.5rem;padding:0.75rem 0.5rem}
.search-result:hover{background:var(--primary-light)}
.search-result:last-child{border-bottom:none}
.search-result-title{font-weight:600;color:var(--text)}
.search-result-excerpt{font-size:0.85rem;color:var(--text-muted);margin-top:0.2rem;line-height:1.4}
.search-result-meta{font-size:0.75rem;color:var(--text-muted);margin-top:0.15rem}
.search-result-meta span{margin-right:0.75rem}
.no-results{color:var(--text-muted);text-align:center;padding:2rem;font-size:0.9rem}

/* Graaf */
.graph-container{width:100%;height:clamp(400px,60vh,700px);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;position:relative;background:var(--card-bg)}
.graph-container svg{display:block}
.graph-legend{position:absolute;bottom:1rem;right:1rem;background:var(--card-bg);border:1px solid var(--border);border-radius:var(--radius);padding:0.75rem;font-size:0.75rem;z-index:10;box-shadow:var(--shadow);max-width:160px}
.graph-legend-item{display:flex;align-items:center;gap:0.4rem;margin:0.15rem 0}
.graph-legend-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.graph-filter{margin-bottom:0.75rem}
.graph-filter select{padding:0.4rem 0.75rem;border:1px solid var(--border);border-radius:4px;font-size:0.85rem;background:var(--card-bg);color:var(--text)}

/* Footer */
footer{text-align:center;padding:1.5rem;color:var(--text-muted);font-size:0.75rem;border-top:1px solid var(--border);margin-top:auto}

/* 404 */
.error-page{text-align:center;padding:4rem 1rem}
.error-page h1{font-size:5rem;color:var(--primary);margin-bottom:0.5rem}
.error-page p{color:var(--text-muted);margin-bottom:1.5rem}

/* Responsive helpers */
@media(min-width:480px){.hide-xs{display:inline!important}}
@media(max-width:479px){.hide-xs{display:none!important}}
@media(min-width:768px){.hide-md{display:none!important}}
@media(max-width:767px){.show-md{display:none!important}}
"""


def gen_nav(active: str = "", p: str = "") -> str:
    items = [
        (f"{p}index.html", "Dashboard"),
        (f"{p}begrippen.html", "Begrippen"),
        (f"{p}annotaties.html", "Annotaties"),
        (f"{p}regels.html", "Regels"),
        (f"{p}graph.html", "Graaf"),
        (f"{p}search.html", "Zoeken"),
    ]
    links = ""
    for url, label in items:
        cls = ' class="active"' if label.lower() == active.lower() else ""
        links += f'<a href="{url}"{cls}>{label}</a>\n'
    return f"""<nav class="nav">
<div class="container">
  <div class="nav-logo">Belastingdienst<span> | Kennismodel Invordering</span></div>
  <div class="nav-links">
    {links}
    <button class="dark-toggle" id="darkToggle" aria-label="Donker/licht modus wisselen" title="Donker/licht modus">A</button>
  </div>
</div>
</nav>"""


def pagina(title: str, body: str, active: str = "", p: str = "", extra_scripts: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="nl" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Belastingdienst</title>
<link rel="icon" type="image/svg+xml" href="{p}icons/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="{p}icons/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="{p}icons/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="{p}icons/apple-touch-icon.png">
<link rel="manifest" href="{p}manifest.json">
<meta name="theme-color" content="#0047A0">
<link rel="stylesheet" href="{p}css/style.css">
</head>
<body>
{gen_nav(active, p)}
<main><div class="container">
{body}
</div></main>
<footer>Gegenereerd uit de juridische analyses vault &bull; Belastingdienst &bull; Inning &bull; Art. 9 IW 1990</footer>
<script src="{p}js/app.js"></script>
{extra_scripts}
</body>
</html>"""


def schrijf_html(out: Path, rel: str, title: str, body: str, active: str = "", p: str = "", extra_scripts: str = ""):
    pad = out / rel
    pad.parent.mkdir(parents=True, exist_ok=True)
    pad.write_text(pagina(title, body, active, p, extra_scripts))


def jas_tag(klasse: str) -> str:
    kleur = JAS_KLEUREN.get(klasse, "#888")
    return f'<span class="tag" style="background:{kleur}">{klasse}</span>'


def status_badge(status: str) -> str:
    return f'<span class="badge badge-{status or "concept"}">{status or "onbekend"}</span>'


# ── Data laden ────────────────────────────────────────────

def laad_begrippen(vault_root: Path) -> list[dict]:
    begrippen = []
    pad = vault_root / "begrippen"
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
        begrippen.append({
            "id": data.get("begrip-id", f.stem),
            "naam": data.get("begripsnaam", f.stem),
            "slug": slugify(data.get("begripsnaam", f.stem)),
            "definitie": data.get("definitie", "") or "",
            "soort": data.get("soort", "") or "",
            "herkomst": data.get("herkomst", "") or "",
            "status": data.get("status", "concept") or "concept",
            "aliases": data.get("aliases") or [],
            "relaties": {
                "is-een": extract_rel("is-een"),
                "heeft": extract_rel("heeft"),
                "leidt-tot": extract_rel("leidt-tot"),
            },
            "afleidingsregel-id": data.get("afleidingsregel-id"),
            "tussenresultaat": data.get("tussenresultaat", False),
            "jas_klasse": klasse,
            "toelichting_klasse": data.get("toelichting-klasse") or "",
            "markeringen": data.get("markeringen") or [],
            "geldigheid_van": str(data.get("geldigheid-van") or ""),
        })
    return begrippen


def laad_annotaties(vault_root: Path) -> list[dict]:
    annotaties = []
    pad = vault_root / "annotaties"
    for json_file in sorted(pad.rglob("*.json")):
        data = json.loads(json_file.read_text())
        aid = data.get("annotatie-id") or ""
        wetstekst = data.get("wetstekst") or ""
        if not aid or not wetstekst:
            continue
        rijen = []
        for r in data.get("annotatierijen") or []:
            rijen.append({
                "markering": r.get("markering", ""),
                "jas_klasse": r.get("jas-klasse", ""),
                "begrip_id": r.get("begrip-id", ""),
                "signalering": r.get("signalering"),
            })
        annotaties.append({
            "id": aid,
            "bwb_id": data.get("bwb-id", ""),
            "wet": data.get("wet", ""),
            "artikel": data.get("artikel", ""),
            "lid": data.get("lid") or data.get("sectie", ""),
            "structuurpositie": data.get("structuurpositie", ""),
            "wetstekst": wetstekst,
            "rijen": rijen,
            "diagram": data.get("diagram"),
        })
    return annotaties


def laad_regels(vault_root: Path) -> list[dict]:
    regels = []
    pad = vault_root / "regels"
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
        })
    return regels


# ── Pagina generatoren ────────────────────────────────────

def gen_index(out: Path, begrippen: list, annotaties: list, regels: list):
    n_beg = len(begrippen)
    n_ann = len(annotaties)
    n_reg = len(regels)
    n_klassen = len({b["jas_klasse"] for b in begrippen})
    n_def = sum(1 for b in begrippen if b.get("definitie"))
    n_concept = sum(1 for b in begrippen if b["status"] == "concept")
    n_definitief = sum(1 for b in begrippen if b["status"] == "definitief")
    by_klasse: dict[str, int] = {}
    for b in begrippen:
        k = b["jas_klasse"]
        by_klasse[k] = by_klasse.get(k, 0) + 1
    klasse_rows = "".join(f'<tr><td>{jas_tag(k)}</td><td style="text-align:right">{c}</td></tr>' for k, c in sorted(by_klasse.items(), key=lambda x: -x[1]))
    body = f"""<h1>Kennismodel Invordering</h1>
<p class="subtitle">Artikel 9 Invorderingswet 1990 — Gestructureerde wetsanalyse volgens JAS v1.0.10</p>
<div class="stat-grid">
  <div class="card stat-card"><div class="stat-nr">{n_beg}</div><div class="stat-label">Begrippen</div></div>
  <div class="card stat-card"><div class="stat-nr">{n_ann}</div><div class="stat-label">Annotaties</div></div>
  <div class="card stat-card"><div class="stat-nr">{n_reg}</div><div class="stat-label">Afleidingsregels</div></div>
  <div class="card stat-card"><div class="stat-nr">{n_klassen}</div><div class="stat-label">JAS-klassen</div></div>
</div>
<div class="dash-grid">
  <div class="card">
    <div class="card-title">Voortgang</div>
    <table class="prop-table">
      <tr><td>Concept</td><td style="text-align:right">{n_concept}</td></tr>
      <tr><td>Definitief</td><td style="text-align:right">{n_definitief}</td></tr>
      <tr><td>Met definitie</td><td style="text-align:right">{n_def}/{n_beg}</td></tr>
    </table>
  </div>
  <div class="card">
    <div class="card-title">JAS-klassen</div>
    <table class="prop-table">{klasse_rows}</table>
  </div>
  <div class="card">
    <div class="card-title">Snelle links</div>
    <p><a href="begrippen.html">Alle begrippen</a></p>
    <p><a href="annotaties.html">Alle annotaties</a></p>
    <p><a href="regels.html">Alle regels</a></p>
    <p><a href="graph.html">Kennisgraaf</a></p>
    <p><a href="search.html">Zoeken</a></p>
  </div>
</div>"""
    schrijf_html(out, "index.html", "Dashboard — Belastingdienst", body, active="dashboard")


def gen_begrippen(out: Path, begrippen: list, annotaties: list):
    # Build index: begrip_id → annotatie-links
    ann_by_begrip: dict[str, list[dict]] = {}
    for a in annotaties:
        ann_title = f'{a["wet"]} art. {a["artikel"]}{", lid " + a["lid"] if a.get("lid") else ""}'
        ann_url = f'annotaties/{a["id"].replace("/","-")}.html'
        for r in a["rijen"]:
            bid = r.get("begrip_id")
            if bid:
                ann_by_begrip.setdefault(bid, []).append({"titel": ann_title, "url": ann_url})
    items = "".join(
        f'<li onclick="window.location=\'begrippen/{b["slug"]}.html\'">'
        f'<a href="begrippen/{b["slug"]}.html" class="item-title">{b["naam"]}</a>'
        f'{jas_tag(b["jas_klasse"])}'
        f'<span class="badge badge-soort">{b["soort"]}</span>'
        f'{status_badge(b["status"])}'
        f'<span class="item-meta">ID: {b["id"]}</span>'
        f'</li>\n'
        for b in begrippen
    )
    body = f"""<h1>Begrippen ({len(begrippen)})</h1>
<input type="text" class="search-input" id="filterInput" placeholder="Filter op naam..." autofocus>
<div class="item-list" id="itemList">{items}</div>
<script>
document.getElementById('filterInput')?.addEventListener('input',function(){{
  var q=this.value.toLowerCase(),list=document.getElementById('itemList'),li=list.getElementsByTagName('li');
  for(var i=0;i<li.length;i++){{li[i].style.display=li[i].textContent.toLowerCase().indexOf(q)>-1?'':'none'}}
}});
</script>"""
    schrijf_html(out, "begrippen.html", "Begrippen — Belastingdienst", body, active="begrippen")

    pp = "../"  # prefix voor detail-pagina's in subdirectory
    for b in begrippen:
        rel_html = ""
        for rt, label in [("is-een", "Is een"), ("heeft", "Heeft"), ("leidt-tot", "Leidt tot")]:
            targets = b["relaties"][rt]
            if targets:
                rel_html += f"<p style='margin-top:0.5rem'><strong>{label}</strong></p><ul style='margin-left:1.25rem'>"
                for t in targets:
                    t_slug = slugify(t.rsplit("/", 1)[-1])
                    rel_html += f'<li><a href="{pp}begrippen/{t_slug}.html">{t}</a></li>'
                rel_html += "</ul>"
        if not rel_html:
            rel_html = "<p class='item-meta'>Geen relaties</p>"
        def_bron = ""
        if b.get("definitie"):
            bronnen = b.get("markeringen", [])
            if bronnen:
                m_ids = ", ".join(m.get("markering-id", "") for m in bronnen if m.get("bijdrage") == "primair")
                def_bron = f'<div style="font-size:0.8rem;color:var(--text-muted);margin-top:0.25rem">Gebaseerd op: {m_ids}</div>'
        mark_tbl = ""
        for m in b.get("markeringen", []):
            jc = b["jas_klasse"] or ""
            mark_tbl += f'<tr><td>{m.get("markering-id","")}</td><td class="mark-text">"{m.get("tekst","")}"</td><td>{jas_tag(jc) if jc else ""}</td><td>{m.get("interpretatiemethode","")}</td><td><span class="badge badge-soort">{m.get("bijdrage","")}</span></td></tr>\n'
        mp = ""
        if mark_tbl:
            mp = f"""<div class="card">
  <div class="card-title">Markeringen</div>
  <div style="overflow-x:auto">
  <table class="ann-table">
    <tr><th>ID</th><th>Tekst</th><th>JAS-klasse</th><th>Interpretatie</th><th>Bijdrage</th></tr>
    {mark_tbl}
  </table></div>
</div>"""
        reg_lnk = ""
        if b["afleidingsregel-id"]:
            reg_lnk = f'<p style="margin-top:0.5rem"><a href="{pp}regels/{b["afleidingsregel-id"]}.html">{b["afleidingsregel-id"]}</a></p>'
        ann_links = ""
        ann_refs = ann_by_begrip.get(b["id"], [])
        if ann_refs:
            seen: set[str] = set()
            items = ""
            for ref in ann_refs:
                if ref["url"] not in seen:
                    seen.add(ref["url"])
                    items += f'<li><a href="../{ref["url"]}">{ref["titel"]}</a></li>\n'
            ann_links = f'<div class="card"><div class="card-title">Annotaties</div><ul style="margin-left:1.25rem">{items}</ul></div>'
        body = f"""<h1>{b["naam"]}</h1>
<p class="subtitle">{jas_tag(b["jas_klasse"])} <span class="badge badge-soort">{b["soort"]}</span> {status_badge(b["status"])}</p>
<div class="detail-layout">
<div>
  <div class="card">
    <div class="card-title">Definitie</div>
    <div class="def-block">{b["definitie"] or "<em>Geen definitie</em>"}</div>
    {def_bron}
  </div>
  {mp}
</div>
<div>
  <div class="card">
    <div class="card-title">Kenmerken</div>
    <table class="prop-table">
      <tr><td>ID</td><td style="word-break:break-all;font-size:0.8rem">{b["id"]}</td></tr>
      <tr><td>Soort</td><td>{b["soort"] or "-"}</td></tr>
      <tr><td>Herkomst</td><td>{b["herkomst"] or "-"}</td></tr>
      <tr><td>Aliases</td><td>{", ".join(b["aliases"]) or "-"}</td></tr>
      <tr><td>Geldig vanaf</td><td>{b["geldigheid_van"] or "-"}</td></tr>
      <tr><td>Tussenresultaat</td><td>{"Ja" if b["tussenresultaat"] else "Nee"}</td></tr>
    </table>
  </div>
  {f'<div class="card"><div class="card-title">JAS-toelichting</div><p style="font-size:0.85rem;font-style:italic">{b["toelichting_klasse"]}</p></div>' if b["toelichting_klasse"] else ""}
  <div class="card">
    <div class="card-title">Relaties</div>
    {rel_html}
  </div>
  {ann_links}
  {f'<div class="card"><div class="card-title">Afleidingsregel</div>{reg_lnk}</div>' if reg_lnk else ""}
</div>
</div>"""
        schrijf_html(out, f'begrippen/{b["slug"]}.html', f'{b["naam"]} — Belastingdienst', body, active="begrippen", p="../")


def gen_annotaties(out: Path, annotaties: list, regels: list, begrippen: list):
    # Build index: begrip_id → regels die erin/eruit gebruiken
    regel_by_bid: dict[str, list[dict]] = {}
    for reg in regels:
        ref = {"id": reg["id"], "naam": reg["naam"]}
        for inv in reg["invoer"]:
            regel_by_bid.setdefault(inv, []).append(ref)
        for uitv in reg["uitvoer"]:
            regel_by_bid.setdefault(uitv, []).append(ref)
    items = "".join(
        f'<li onclick="window.location=\'annotaties/{a["id"].replace("/","-")}.html\'">'
        f'<a href="annotaties/{a["id"].replace("/","-")}.html" class="item-title">{a["wet"]} art. {a["artikel"]}{", lid " + a["lid"] if a.get("lid") else ""}</a>'
        f'<span class="badge badge-type">{a.get("bwb_id","")}</span>'
        f'<span class="item-meta">{a["structuurpositie"]}</span>'
        f'</li>\n'
        for a in annotaties
    )
    body = f"""<h1>Annotaties ({len(annotaties)})</h1>
<div class="item-list">{items}</div>"""
    schrijf_html(out, "annotaties.html", "Annotaties — Belastingdienst", body, active="annotaties")

    for a in annotaties:
        rijen = ""
        for r in a["rijen"]:
            bgp_link = ""
            if r.get("begrip_id"):
                slug = slugify(r["begrip_id"].rsplit("/", 1)[-1])
                bgp_link = f'<a href="../begrippen/{slug}.html" style="word-break:break-all;font-size:0.8rem">{r["begrip_id"]}</a>'
            rijen += f'<tr><td class="mark-text">"{r["markering"]}"</td><td>{jas_tag(r["jas_klasse"])}</td><td>{bgp_link}</td></tr>\n'
        signaleringen = ""
        for r in a["rijen"]:
            if r.get("signalering"):
                signaleringen += f'<div class="signalering"><span>[!]</span> {r["signalering"]}</div>\n'
        lid = f', lid {a["lid"]}' if a.get("lid") else ""
        mermaid_src = ""
        extra_scripts = ""
        mermaid_code = diagram_to_mermaid(a.get("diagram") or {})
        if mermaid_code:
            mermaid_src = f"""<div class="card"><div class="card-title">Structuurdiagram</div>
<div class="mermaid">
{mermaid_code}
</div></div>"""
            extra_scripts = '<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>\n<script>mermaid.initialize({startOnLoad:true,theme:"neutral",fontFamily:"system-ui,sans-serif"})</script>'
        regel_links = ""
        seen_regels: set[str] = set()
        regel_items = ""
        for r in a["rijen"]:
            bid = r.get("begrip_id")
            if bid:
                for reg_ref in regel_by_bid.get(bid, []):
                    if reg_ref["id"] not in seen_regels:
                        seen_regels.add(reg_ref["id"])
                        regel_items += f'<li><a href="../regels/{reg_ref["id"]}.html">{reg_ref["naam"]}</a></li>\n'
        if regel_items:
            regel_links = f'<div class="card"><div class="card-title">Afleidingsregels</div><ul style="margin-left:1.25rem">{regel_items}</ul></div>'
        body = f"""<h1>{a["wet"]} art. {a["artikel"]}{lid}</h1>
<p class="subtitle">{a["structuurpositie"]} &bull; {a["bwb_id"]}</p>
<div class="wetstekst">"{a["wetstekst"]}"</div>
<div class="card">
<div class="card-title">Annotatierijen</div>
<div style="overflow-x:auto">
<table class="ann-table">
  <tr><th>Markering</th><th>JAS-klasse</th><th>Begrip</th></tr>
  {rijen}
</table></div>
{signaleringen}
</div>
{mermaid_src}
{regel_links}"""
        schrijf_html(out, f'annotaties/{a["id"].replace("/","-")}.html', f'Annotatie art. {a["artikel"]} — Belastingdienst', body, active="annotaties", p="../", extra_scripts=extra_scripts)


def gen_regels(out: Path, regels: list, begrippen: list):
    slug_by_bid = {b["id"]: b["slug"] for b in begrippen}
    def _link(ref: str) -> str:
        slug = slug_by_bid.get(ref)
        return f'<a href="../begrippen/{slug}.html">{ref}</a>' if slug else ref
    items = "".join(
        f'<li onclick="window.location=\'regels/{r["id"]}.html\'">'
        f'<a href="regels/{r["id"]}.html" class="item-title">{r["naam"]}</a>'
        f'<span class="badge badge-definitief">{r["soort"]}</span>'
        f'<span class="item-meta">ID: {r["id"]}</span>'
        f'</li>\n'
        for r in regels
    )
    body = f"""<h1>Afleidingsregels ({len(regels)})</h1>
<div class="item-list">{items}</div>"""
    schrijf_html(out, "regels.html", "Regels — Belastingdienst", body, active="regels")

    for r in regels:
        vb = ""
        for v in r.get("voorbeeldreeksen") or []:
            juist = v.get("juridisch-juist", True)
            cls = "voorbeeld" if juist else "voorbeeld ongeldig"
            label = "[+]" if juist else "[-]"
            vb += f'<div class="{cls}"><span class="voorbeeld-label">{label}</span> <strong>Invoer:</strong> {v.get("invoerwaarden","")}<br><strong>Uitvoer:</strong> {v.get("verwachte-uitkomst","")}</div>'
        ops = ", ".join(r.get("operators") or [])
        body = f"""<h1>{r["naam"]}</h1>
<p class="subtitle"><span class="badge badge-definitief">{r["soort"]}</span> {r["id"]}</p>
<div class="card">
  <div class="card-title">Formele regel</div>
  <div class="regel-box">{r["formele_regel"]}</div>
</div>
<div class="card">
  <div class="card-title">Toelichting</div>
  <p>{r["toelichting"] or "<em>Geen toelichting</em>"}</p>
</div>
<div class="dash-grid">
  <div class="card">
    <div class="card-title">Invoer</div>
    <ul style="margin-left:1.25rem;">{"".join(f'<li>{_link(i)}</li>' for i in r["invoer"]) or "<li class=item-meta>Geen</li>"}</ul>
  </div>
  <div class="card">
    <div class="card-title">Uitvoer</div>
    <ul style="margin-left:1.25rem;">{"".join(f'<li>{_link(o)}</li>' for o in r["uitvoer"]) or "<li class=item-meta>Geen</li>"}</ul>
  </div>
  <div class="card">
    <div class="card-title">Details</div>
    <table class="prop-table">
      <tr><td>Operators</td><td>{ops or "-"}</td></tr>
      <tr><td>Tussenresultaat</td><td>{"Ja" if r["tussenresultaat"] else "Nee"}</td></tr>
    </table>
  </div>
</div>
<div class="card">
<div class="card-title">Voorbeeldreeksen</div>
{vb or "<p class=item-meta>Geen voorbeelden</p>"}
</div>"""
        schrijf_html(out, f'regels/{r["id"]}.html', f'{r["naam"]} — Belastingdienst', body, active="regels", p="../")


def gen_graph(out: Path, begrippen: list, regels: list, annotaties: list):
    nodes: list[dict] = []
    node_ids: set[str] = set()
    links: list[dict] = []
    def add_node(nid: str, label: str, groep: str, node_type: str = "begrip"):
        if nid not in node_ids:
            nodes.append({"id": nid, "label": label, "groep": groep, "type": node_type})
            node_ids.add(nid)
    for b in begrippen:
        add_node(b["id"], b["naam"], b["jas_klasse"], "begrip")
        for rt in ("is-een", "heeft", "leidt-tot"):
            for target in b["relaties"][rt]:
                if target not in node_ids:
                    add_node(target, target.rsplit("/", 1)[-1], "onbekend", "begrip")
                links.append({"source": b["id"], "target": target, "relatie": rt})
    for r in regels:
        add_node(r["id"], r["naam"], "afleidingsregel", "regel")
        for inv in r.get("invoer") or []:
            if inv not in node_ids:
                add_node(inv, inv.rsplit("/", 1)[-1], "onbekend", "begrip")
            links.append({"source": r["id"], "target": inv, "relatie": "invoer"})
    gr_data = json.dumps({"nodes": nodes, "links": links}, ensure_ascii=False)
    kleuren_json = json.dumps(JAS_KLEUREN, ensure_ascii=False)
    body = f"""<h1>Kennisgraaf</h1>
<p class="subtitle">Interactieve graaf van begrippen (cirkels) en afleidingsregels (ruiten). Sleep nodes om te herschikken.</p>
<div class="graph-filter">
  <label for="klasseFilter">JAS-klasse filter: </label>
  <select id="klasseFilter">
    <option value="all">Alle</option>
    {"".join(f'<option value="{k}">{k}</option>' for k in sorted(JAS_KLEUREN.keys()))}
  </select>
</div>
<div class="graph-container" id="graphContainer">
  <div class="graph-legend" id="graphLegend"></div>
</div>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
var data = {gr_data};
var colorMap = {kleuren_json};
var width = document.getElementById('graphContainer').clientWidth;
var height = Math.max(400, Math.min(window.innerHeight * 0.6, 700));
var svg = d3.select("#graphContainer").append("svg").attr("width", width).attr("height", height);
var g = svg.append("g");
// Zoom + pan
var zoom = d3.zoom().scaleExtent([0.1, 8]).on("zoom", function(e){{ g.attr("transform", e.transform); }});
svg.call(zoom).on("dblclick.zoom", null);
// Background rect voor pan
g.append("rect").attr("x", -width*5).attr("y", -height*5).attr("width", width*10).attr("height", height*10).attr("fill", "none").attr("pointer-events", "all");
svg.append("defs").append("marker").attr("id","arrow").attr("viewBox","0 -5 10 10").attr("refX",20).attr("refY",0).attr("markerWidth",6).attr("markerHeight",6).attr("orient","auto")
  .append("path").attr("d","M0,-5L10,0L0,5").attr("fill","#94a3b8");
var link = g.append("g").selectAll("line").data(data.links).join("line")
  .attr("stroke","#94a3b8").attr("stroke-width",1).attr("stroke-opacity",0.5).attr("marker-end","url(#arrow)");
var node = g.append("g").selectAll("g").data(data.nodes).join("g").call(
  d3.drag().on("start",function(e,d){{if(!e.active)simulation.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y}})
  .on("drag",function(e,d){{d.fx=e.x;d.fy=e.y}})
  .on("end",function(e,d){{if(!e.active)simulation.alphaTarget(0);d.fx=null;d.fy=null}}));
node.append("title").text(function(d){{return d.label}});
node.append("path").attr("d",function(d){{var s=7;return d.type==='regel'?d3.symbol().type(d3.symbolDiamond).size(200)():null}})
  .attr("fill",function(d){{return colorMap[d.groep]||'#94a3b8'}}).attr("stroke","#fff").attr("stroke-width",1.5)
  .attr("opacity",function(d){{return d.type==='regel'?1:0}});
node.append("circle").attr("r",7).attr("fill",function(d){{return colorMap[d.groep]||'#94a3b8'}}).attr("stroke","#fff").attr("stroke-width",1.5)
  .attr("opacity",function(d){{return d.type==='begrip'?1:0}});
node.append("text").attr("dx",12).attr("dy",4).attr("font-size","11px").attr("fill",function(){{var root=document.documentElement;return root.getAttribute('data-theme')==='dark'?'#e2e8f0':'#334155'}})
  .text(function(d){{return d.label.length>25?d.label.slice(0,22)+'...':d.label}});
var simulation = d3.forceSimulation(data.nodes)
  .force("link",d3.forceLink(data.links).id(function(d){{return d.id}}).distance(100))
  .force("charge",d3.forceManyBody().strength(-150))
  .force("center",d3.forceCenter(width/2,height/2)).force("collision",d3.forceCollide(15));
simulation.on("tick",function(){{
  link.attr("x1",function(d){{return d.source.x}}).attr("y1",function(d){{return d.source.y}}).attr("x2",function(d){{return d.target.x}}).attr("y2",function(d){{return d.target.y}});
  node.attr("transform",function(d){{return"translate("+d.x+","+d.y+")"}});
}});
// Auto-center na stabilisatie
simulation.on("end",function(){{
  svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity.translate(width/2,height/2).scale(0.8).translate(-width/2,-height/2));
}});
function resetView(){{
  svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity.translate(width/2,height/2).scale(0.8).translate(-width/2,-height/2));
}}
// Legend
var legend = d3.select("#graphLegend");
legend.append("div").style("font-weight","600").style("margin-bottom","0.3rem").text("Legenda");
Object.entries(colorMap).forEach(function(entry){{
  var row = legend.append("div").attr("class","graph-legend-item");
  row.append("div").attr("class","graph-legend-dot").style("background",entry[1]);
  row.append("span").text(entry[0]);
}});
// Filter
document.getElementById('klasseFilter').addEventListener('change',function(){{
  var v=this.value;
  node.attr("opacity",function(d){{return v==='all'||d.groep===v?1:0.1}});
  link.attr("opacity",function(d){{return v==='all'||d.source.groep===v||d.target.groep===v?0.5:0.05}});
}});
</script>"""
    schrijf_html(out, "graph.html", "Kennisgraaf — Belastingdienst", body, active="graaf")


def gen_search(out: Path, begrippen: list, annotaties: list, regels: list):
    bron_data = []
    for b in begrippen:
        bron_data.append({"type": "Begrip", "titel": b["naam"], "url": f'begrippen/{b["slug"]}.html', "tekst": b.get("definitie","") + " " + b["naam"] + " " + " ".join(b["aliases"]), "jas_klasse": b["jas_klasse"]})
    for a in annotaties:
        bron_data.append({"type": "Annotatie", "titel": f'{a["wet"]} art. {a["artikel"]}{", lid " + a["lid"] if a.get("lid") else ""}', "url": f'annotaties/{a["id"].replace("/","-")}.html', "tekst": a.get("wetstekst",""), "jas_klasse": ""})
    for r in regels:
        bron_data.append({"type": "Regel", "titel": r["naam"], "url": f'regels/{r["id"]}.html', "tekst": (r.get("formele_regel","") + " " + (r.get("toelichting","") or "")), "jas_klasse": "afleidingsregel"})
    data_json = json.dumps(bron_data, ensure_ascii=False)
    body = f"""<h1>Zoeken</h1>
<input type="text" class="search-input" id="searchInput" placeholder="Zoek in begrippen, annotaties en regels..." autofocus>
<div class="search-filters" id="searchFilters">
  <span class="filter-chip active" data-type="all">Alle</span>
  <span class="filter-chip" data-type="Begrip">Begrippen</span>
  <span class="filter-chip" data-type="Annotatie">Annotaties</span>
  <span class="filter-chip" data-type="Regel">Regels</span>
</div>
<div id="searchResults"></div>
<script>
var data = {data_json};
var currentFilter = 'all';
document.querySelectorAll('.filter-chip').forEach(function(chip){{
  chip.addEventListener('click',function(){{
    document.querySelectorAll('.filter-chip').forEach(function(c){{c.classList.remove('active')}});
    this.classList.add('active');
    currentFilter = this.getAttribute('data-type');
    doSearch();
  }});
}});
function doSearch(){{
  var q = document.getElementById('searchInput').value.toLowerCase();
  var out = document.getElementById('searchResults');
  out.innerHTML = '';
  if(q.length < 2){{out.innerHTML='<div class="item-list"><li class="item-meta" style="list-style:none;padding:1rem 0">Typ minimaal 2 tekens om te zoeken</li></div>';return}}
  var hits = data.filter(function(d){{
    if(currentFilter !== 'all' && d.type !== currentFilter) return false;
    return d.titel.toLowerCase().indexOf(q) > -1 || d.tekst.toLowerCase().indexOf(q) > -1;
  }});
  if(hits.length === 0){{out.innerHTML='<div class="no-results">Geen resultaten voor "'+q+'"</div>';return}}
  out.innerHTML = '<div style="font-size:0.85rem;color:var(--text-muted);margin-bottom:0.5rem">'+hits.length+' resultaten</div>';
  hits.slice(0,50).forEach(function(d){{
    var excerpt = d.tekst.length > 150 ? d.tekst.substring(0,150)+'...' : d.tekst;
    out.innerHTML += '<div class="search-result" onclick="window.location=\\''+d.url+'\\'">'+
      '<div class="search-result-title">'+d.titel+'</div>'+
      '<div class="search-result-excerpt">'+excerpt+'</div>'+
      '<div class="search-result-meta"><span>Type: '+d.type+'</span>'+
      (d.jas_klasse?'<span>JAS: '+d.jas_klasse+'</span>':'')+'</div></div>';
  }});
}}
document.getElementById('searchInput').addEventListener('input',function(){{var t=this;setTimeout(function(){{if(t.value===document.getElementById('searchInput').value)doSearch()}},200)}});
</script>"""
    schrijf_html(out, "search.html", "Zoeken — Belastingdienst", body, active="zoeken")


def gen_404(out: Path):
    body = """<div class="error-page">
<h1>404</h1>
<p>Deze pagina bestaat niet.</p>
<a href="./" class="filter-chip active">Terug naar dashboard</a>
</div>"""
    schrijf_html(out, "404.html", "Pagina niet gevonden — Belastingdienst", body)


def gen_css_js(out: Path):
    (out / "css").mkdir(parents=True, exist_ok=True)
    (out / "css/style.css").write_text(CSS)
    js = """document.addEventListener('DOMContentLoaded',function(){
  var toggle=document.getElementById('darkToggle');
  var root=document.documentElement;
  function setTheme(t){root.setAttribute('data-theme',t);localStorage.setItem('theme',t);
    if(toggle)toggle.textContent=t==='dark'?'\u25D0':'A';}
  var stored=localStorage.getItem('theme');
  if(stored){setTheme(stored)}else if(window.matchMedia&&window.matchMedia('(prefers-color-scheme:dark)').matches){setTheme('dark')}else{setTheme('light')}
  if(toggle)toggle.addEventListener('click',function(){setTheme(root.getAttribute('data-theme')==='dark'?'light':'dark')});
  window.matchMedia('(prefers-color-scheme:dark)').addEventListener('change',function(e){if(!localStorage.getItem('theme'))setTheme(e.matches?'dark':'light')});
});"""
    (out / "js").mkdir(parents=True, exist_ok=True)
    (out / "js/app.js").write_text(js)


def gen_icons(vault: Path, out: Path):
    src = vault / "icons"
    dst = out / "icons"
    dst.mkdir(parents=True, exist_ok=True)
    if src.exists():
        for f in src.iterdir():
            if f.is_file():
                shutil.copy2(f, dst / f.name)
    manifest = out / "manifest.json"
    if not manifest.exists():
        manifest.write_text("""{"name":"Belastingdienst — Kennismodel Invordering","short_name":"Kennismodel","start_url":".","display":"standalone","background_color":"#0047A0","theme_color":"#0047A0","icons":[{"src":"icons/favicon-192.png","sizes":"192x192","type":"image/png"},{"src":"icons/favicon-512.png","sizes":"512x512","type":"image/png"}]}""")


def main():
    parser = argparse.ArgumentParser(description="Genereer statische webapp uit vault")
    parser.add_argument("--vault-root", default=".", help="Pad naar vault-root")
    parser.add_argument("--out", default="webapp", help="Output directory")
    args = parser.parse_args()

    vault = Path(args.vault_root)
    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)

    print("Data laden...", file=sys.stderr)
    begrippen = laad_begrippen(vault)
    annotaties = laad_annotaties(vault)
    regels = laad_regels(vault)
    print(f"  {len(begrippen)} begrippen, {len(annotaties)} annotaties, {len(regels)} regels", file=sys.stderr)

    print("CSS, JS en icons genereren...", file=sys.stderr)
    gen_css_js(out)
    gen_icons(vault, out)

    print("Pagina's genereren...", file=sys.stderr)
    gen_index(out, begrippen, annotaties, regels)
    gen_404(out)
    gen_begrippen(out, begrippen, annotaties)
    gen_annotaties(out, annotaties, regels, begrippen)
    gen_regels(out, regels, begrippen)
    gen_graph(out, begrippen, regels, annotaties)
    gen_search(out, begrippen, annotaties, regels)

    print(f"Webapp gegenereerd in {out}/ ({len(list(out.rglob('*')))} bestanden)", file=sys.stderr)


if __name__ == "__main__":
    main()
