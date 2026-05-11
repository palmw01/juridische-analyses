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
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = h[0]*2 + h[1]*2 + h[2]*2
    if len(h) != 6:
        return ""
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
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
    "brondefinitie": "#B4C7E7",
}

CSS = """/* Belastingdienst kennismodel — Rijkshuisstijl v2 */

/* RO Sans vereist licentie; Source Sans 3 is de dichtstbijzijnde open-source variant */
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:ital,wght@0,300;0,400;0,600;0,700;1,400&display=swap');

/* ── Design tokens — Rijkshuisstijl officieel ── */
:root {
  --primary: #154273;           /* Lintblauw — officieel Rijkshuisstijl */
  --primary-hover: #0D2B4D;
  --primary-light: #DAE6F0;
  --link: #01689B;              /* Officiële rijksoverheid linkkleur */
  --link-hover: #01568A;
  --accent: #C0392B;            /* Regel-box accent */
  --bg: #F3F6F9;
  --card-bg: #FFFFFF;
  --text: #1A1A1A;
  --text-secondary: #3A4A5C;
  --text-muted: #5C6C7C;
  --border: #C8D4DF;
  --shadow: 0 1px 2px rgba(21,66,115,0.07), 0 1px 4px rgba(21,66,115,0.04);
  --shadow-hover: 0 3px 10px rgba(21,66,115,0.13);
  --success: #1B6B2E;
  --success-bg: #E2F0E6;
  --error: #B52316;
  --error-bg: #FAE9E7;
  --warning: #7A3D00;
  --warning-bg: #FEF3E2;
  --radius: 4px;                /* Rijkshuisstijl: strakke hoeken */
  --radius-btn: 5px;            /* ~10% van 48px knophoogte */
  --radius-input: 3px;          /* ~5% van 48px veldenhoogte */
  --nav-height: 64px;           /* Vergroot voor WCAG 2.5.5 touch targets */
  --max-width: 1200px;
  --font: "RO Sans", "Source Sans 3", "Source Sans Pro", "Segoe UI", Arial, sans-serif;
  --font-serif: "RO Serif", Georgia, "Times New Roman", serif;
  --font-mono: "Cascadia Code", Consolas, "Liberation Mono", monospace;
  --focus-ring: 0 0 0 3px rgba(21,66,115,0.30);
}

/* ── Dark mode — gedempte marine-blauwtinten, geen startup-neon ── */
[data-theme="dark"] {
  --primary: #4A8EC0;
  --primary-hover: #5BA3D8;
  --primary-light: #192C3E;
  --link: #6AAEDD;
  --link-hover: #82C2EF;
  --bg: #0E1720;
  --card-bg: #162030;
  --text: #E6EEF5;
  --text-secondary: #B5C9DB;
  --text-muted: #849DB5;
  --border: #243547;
  --shadow: 0 1px 3px rgba(0,0,0,0.35);
  --shadow-hover: 0 4px 14px rgba(0,0,0,0.45);
  --success-bg: #0B2E14;
  --error-bg: #350A07;
  --warning-bg: #332000;
  --focus-ring: 0 0 0 3px rgba(74,142,192,0.40);
}

/* ── Mermaid dark mode ── */
[data-theme="dark"] .mermaid svg text{fill:#dce8f0!important}
[data-theme="dark"] .mermaid svg .edgeLabel{fill:#b5c9db!important;stroke:none!important}
[data-theme="dark"] .mermaid svg #arrow{fill:#4a6880!important}
[data-theme="dark"] .mermaid{background:var(--card-bg)}
[data-theme="dark"] .mermaid svg .cluster-label text,
[data-theme="dark"] .mermaid svg .label text,
[data-theme="dark"] .mermaid svg .nodeLabel{fill:#dce8f0!important}
[data-theme="dark"] .mermaid svg .edgePath .path{stroke:#4a6880!important}
[data-theme="dark"] .mermaid svg .edge-pattern{stroke:#4a6880!important}
[data-theme="dark"] .mermaid svg .cluster{fill:#162030!important;stroke:#243547!important}
[data-theme="dark"] .mermaid svg .cluster-label span{color:#b5c9db!important}
.mermaid{min-height:120px;background:var(--card-bg);padding:0.5rem 0;overflow-x:auto}
.mermaid svg{max-width:100%;height:auto}

/* ── Reset & base ── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{font-size:100%;-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{font-family:var(--font);color:var(--text);background:var(--bg);line-height:1.6;min-height:100vh;display:flex;flex-direction:column}
img,svg{display:block;max-width:100%}

/* Standaard linkkleur volgt officiële rijksoverheid linkkleur, niet de primaire lintkleur */
a{color:var(--link);text-decoration:underline;text-underline-offset:2px}
a:hover{color:var(--link-hover);text-decoration:underline}
a:focus-visible{outline:2px solid var(--primary);outline-offset:3px;border-radius:2px}
::selection{background:var(--primary);color:#fff}

/* ── Skip naar inhoud — WCAG 2.4.1 ── */
.skip-link{position:absolute;top:-100%;left:0;z-index:1000;padding:0.75rem 1.5rem;background:var(--primary);color:#fff;font-weight:600;font-size:0.9rem;white-space:nowrap;text-decoration:none}
.skip-link:focus{top:0;outline:none}

/* ── Focus rings — WCAG 2.4.7, 2.4.13 ── */
button:focus-visible,input:focus-visible,select:focus-visible,.filter-chip:focus-visible,.dark-toggle:focus-visible,.hamburger:focus-visible{outline:2px solid var(--primary);outline-offset:3px;border-radius:var(--radius)}
.dark-toggle:focus-visible,.hamburger:focus-visible{outline-color:#fff;outline-offset:3px}

/* ── Layout ── */
.container{width:100%;max-width:var(--max-width);margin:0 auto;padding:0 1rem}
@media(min-width:768px){.container{padding:0 1.5rem}}

/* ── Navigatie — Rijkshuisstijl lintblauw ── */
.nav{
  background:var(--primary);
  position:sticky;top:0;z-index:100;
  height:var(--nav-height);
  border-top:4px solid rgba(255,255,255,0.15);
}
/* container erft height:100% + align-items:center van desktop → items altijd verticaal gecentreerd */
.nav .container{display:flex;align-items:center;height:100%;gap:0.25rem;position:relative}

/* Logo */
.nav-logo{
  color:#fff;font-weight:700;
  font-size:clamp(0.95rem,2.5vw,1.1rem);
  white-space:nowrap;
  display:flex;align-items:center;
  padding-right:1.25rem;
  border-right:1px solid rgba(255,255,255,0.25);
  margin-right:0.5rem;
  letter-spacing:0.01em;
  align-self:stretch; /* vul volledige nav-hoogte zodat link-klikgebied groot is */
}
.nav-logo a{color:inherit;text-decoration:none;display:flex;align-items:center}
.nav-logo a:hover{text-decoration:none;opacity:0.9}

/* Nav-links — desktop */
.nav-links{display:flex;gap:0.1rem;margin-left:auto;align-items:center;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;order:2}
.nav-links::-webkit-scrollbar{display:none}
.nav-links a{
  color:rgba(255,255,255,0.85);
  font-size:0.875rem;
  padding:0 0.75rem;
  height:44px;
  display:flex;align-items:center;
  border-radius:var(--radius);
  white-space:nowrap;
  text-decoration:none;
  transition:background 0.15s,color 0.15s;
}
.nav-links a:hover,.nav-links a.active{background:rgba(255,255,255,0.15);color:#fff;text-decoration:none}
.nav-links a.active{font-weight:600}

/* Dark mode toggle */
.dark-toggle{
  background:none;border:none;color:rgba(255,255,255,0.85);
  border-radius:var(--radius);
  width:44px;height:44px;
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;font-size:1.1rem;line-height:1;
  transition:background 0.15s;
  flex-shrink:0;order:3;
}
.dark-toggle:hover{background:rgba(255,255,255,0.15);color:#fff}
.dt-icon{display:flex;align-items:center;justify-content:center;line-height:1}

/* Hamburger — verborgen op desktop */
.hamburger{
  display:none;
  flex-direction:row;align-items:center;gap:8px;
  background:none;border:none;cursor:pointer;
  height:44px;padding:0 0.75rem;
  order:4;flex-shrink:0;
}
.hamburger-lines{display:flex;flex-direction:column;align-items:flex-start;justify-content:center;gap:4px}
.hamburger-lines span{display:block;width:18px;height:2px;background:#fff;border-radius:1px;transition:transform 0.22s,opacity 0.15s}
.hamburger-label{font-size:0.75rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:#fff;line-height:1}
.hamburger.open .hamburger-lines span:nth-child(1){transform:translateY(6px) rotate(45deg)}
.hamburger.open .hamburger-lines span:nth-child(2){opacity:0}
.hamburger.open .hamburger-lines span:nth-child(3){transform:translateY(-6px) rotate(-45deg)}

/* ── Mobiel menu ── */
@media(max-width:767px){
  .hamburger{display:flex;order:3;margin-left:0}
  .dark-toggle{order:2;margin-left:auto}
  /* Logo zonder scheidingslijn op mobiel */
  .nav-logo{border-right:none;padding-right:0;margin-right:0}

  /* Dropdown — wit paneel onder de nav-balk */
  .nav-links{
    display:none;
    position:absolute;top:100%;left:0;right:0;
    flex-direction:column;
    margin:0;padding:0;z-index:99;
    background:var(--card-bg);
    border-top:3px solid var(--primary);
    box-shadow:0 8px 24px rgba(21,66,115,0.18);
  }
  .nav-links.open{display:flex}
  .nav-links a{
    display:flex;align-items:center;
    height:52px;padding:0 1.25rem 0 1rem;
    font-size:1rem;font-weight:400;color:var(--primary);
    border-bottom:1px solid var(--border);
    border-left:4px solid transparent;
    border-radius:0;text-decoration:none;
    transition:background 0.12s,border-color 0.12s;
    white-space:nowrap;
  }
  .nav-links a:hover{background:var(--primary-light);border-left-color:var(--primary);text-decoration:none}
  .nav-links a.active{background:var(--primary-light);border-left-color:var(--primary);font-weight:700}
  .nav-links a:last-child{border-bottom:none}
}

/* ── Main content ── */
main{flex:1;padding:1.5rem 0}
@media(min-width:768px){main{padding:2rem 0}}

/* ── Cards — Belastingdienst-stijl: wit, strak, overzichtelijk ── */
.card{
  background:var(--card-bg);
  border-radius:var(--radius);
  border:1px solid var(--border);
  box-shadow:var(--shadow);
  padding:1.25rem;
  margin-bottom:1rem;
  overflow-wrap:break-word;
  transition:box-shadow 0.15s;
}
@media(min-width:480px){.card{padding:1.5rem}}
.card-title{
  font-size:0.8rem;font-weight:700;
  color:var(--text-secondary);
  margin-bottom:0.875rem;
  padding-bottom:0.5rem;
  border-bottom:1px solid var(--border);
  text-transform:uppercase;letter-spacing:0.06em;
}
.card h2{font-size:1.1rem;color:var(--primary);margin-bottom:0.75rem}

/* ── Grids ── */
.stat-grid{display:grid;grid-template-columns:1fr;gap:0.75rem;margin-bottom:1.5rem}
@media(min-width:480px){.stat-grid{grid-template-columns:repeat(2,1fr)}}
@media(min-width:768px){.stat-grid{grid-template-columns:repeat(4,1fr)}}
.dash-grid{display:grid;grid-template-columns:1fr;gap:1rem;margin-bottom:1.5rem}
@media(min-width:768px){.dash-grid{grid-template-columns:repeat(3,1fr)}}
.card-grid{display:grid;grid-template-columns:1fr;gap:0.75rem}
@media(min-width:768px){.card-grid{grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}}

/* ── Stat cards — professioneel, niet te groot ── */
.stat-card{text-align:center;padding:1.5rem 1.25rem}
.stat-nr{
  font-size:clamp(2rem,5vw,2.75rem);font-weight:700;
  color:var(--primary);line-height:1.1;
  letter-spacing:-0.02em;
}
.stat-label{font-size:0.8rem;color:var(--text-muted);margin-top:0.375rem;text-transform:uppercase;letter-spacing:0.05em}

/* ── Typografie ── */
h1{font-size:clamp(1.3rem,4vw,1.75rem);font-weight:700;color:var(--text);margin-bottom:0.375rem;line-height:1.25}
h2{font-size:clamp(1.05rem,3vw,1.25rem);color:var(--text);margin-bottom:0.625rem;font-weight:600}
.subtitle{color:var(--text-muted);font-size:0.9rem;margin-bottom:1.5rem;line-height:1.5}

/* ── Breadcrumb ── */
.breadcrumb{font-size:0.8rem;color:var(--text-muted);margin-bottom:0.875rem;padding:0;display:flex;flex-wrap:wrap;gap:0.25rem;list-style:none;align-items:center}
.breadcrumb li{display:inline;padding:0;margin:0}
.breadcrumb li+li::before{content:"›";margin:0 0.3rem;color:var(--text-muted)}
.breadcrumb a{color:var(--link);text-decoration:none}
.breadcrumb a:hover{text-decoration:underline}
.breadcrumb [aria-current="page"]{color:var(--text);font-weight:500}

/* ── Badges / Tags ── */
.card ul li,.card ol li{word-break:break-all;overflow-wrap:break-word}
.card a{word-break:break-all;overflow-wrap:break-word}
.tag{display:inline-block;padding:0.2rem 0.5rem;border-radius:3px;font-size:0.73rem;font-weight:600;color:#fff;margin:0.1rem;white-space:nowrap;line-height:1.5;vertical-align:middle}
.badge{display:inline-block;font-size:0.73rem;padding:0.2rem 0.5rem;border-radius:3px;font-weight:600;white-space:nowrap;line-height:1.5;vertical-align:middle}
/* concept: gedempte neutrale stijl — niet als waarschuwing, want dit is de normale werkstatus */
.badge-concept{background:#E8EDF2;color:#3A4A5C;border:1px solid #C8D4DF}
.badge-definitief{background:var(--success-bg);color:var(--success)}
.badge-vervallen{background:var(--border);color:var(--text-muted)}
.badge-type{background:var(--primary-light);color:var(--primary)}
.badge-soort{background:#EFF2F5;color:var(--text-secondary);border:1px solid var(--border)}
.badge-status{background:var(--warning-bg);color:var(--warning)}

/* ── Lijsten ── */
.item-list{list-style:none}
.item-list li{
  display:flex;flex-wrap:wrap;align-items:center;gap:0.5rem;
  padding:0.75rem 0.5rem;
  border-bottom:1px solid var(--border);
  cursor:pointer;
  transition:background 0.12s;
}
.item-list li:hover{background:var(--primary-light)}
.item-list li:focus-within{background:var(--primary-light)}
.item-list li:last-child{border-bottom:none}
.item-list .item-title{flex:1;min-width:150px;font-weight:500;color:var(--text);text-decoration:none}
.item-list a.item-title{color:var(--link);text-decoration:none}
.item-list a.item-title:hover{text-decoration:underline}
.item-list .item-badges{display:flex;flex-wrap:wrap;gap:0.35rem;align-items:center}
.item-list .item-meta{font-size:0.78rem;color:var(--text-muted)}
@media(max-width:767px){
  .item-list li{flex-direction:column;align-items:flex-start;gap:0.3rem}
  .item-list .item-title{min-width:0;width:100%}
  .item-list .item-badges{width:100%}
  .item-list .item-meta{width:100%}
}

/* ── Eigenschappentabel ── */
.prop-table{width:100%;table-layout:fixed;border-collapse:collapse;font-size:0.9rem}
.prop-table td{padding:0.45rem 0;border-bottom:1px solid var(--border);vertical-align:top;overflow-wrap:break-word;word-break:break-word}
.prop-table td:first-child{color:var(--text-muted);width:35%;padding-right:1rem;font-size:0.85rem}
.prop-table tr:last-child td{border-bottom:none}

/* ── Definitie-blok — duidelijk juridisch citaat ── */
.def-block{
  background:var(--primary-light);
  border-left:4px solid var(--primary);
  padding:1rem 1.25rem;
  border-radius:0 var(--radius) var(--radius) 0;
  margin-bottom:1rem;
  font-size:0.95rem;line-height:1.75;
  overflow-wrap:break-word;word-break:break-word;
  font-family:var(--font-serif);
  color:var(--text-secondary);
}

/* ── Wetstekst ── */
.wetstekst{
  background:var(--card-bg);
  border:1px solid var(--border);border-left:4px solid var(--primary);
  padding:1rem 1.25rem;
  border-radius:0 var(--radius) var(--radius) 0;
  margin-bottom:1rem;font-style:italic;
  font-size:0.95rem;line-height:1.8;
  color:var(--text-secondary);
  overflow-wrap:break-word;
  font-family:var(--font-serif);
}

/* ── Annotatietabel ── */
.table-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;margin-bottom:0.25rem}
.ann-table{width:100%;min-width:580px;table-layout:auto;border-collapse:collapse;font-size:0.85rem}
.ann-table th{
  text-align:left;padding:0.5rem 0.625rem;
  color:var(--text-muted);font-weight:700;
  border-bottom:2px solid var(--border);
  font-size:0.73rem;text-transform:uppercase;letter-spacing:0.06em;
  white-space:nowrap;background:var(--bg);
}
.ann-table td{padding:0.5rem 0.625rem;border-bottom:1px solid var(--border);vertical-align:middle;overflow-wrap:break-word;word-break:break-word}
.ann-table tr:hover{background:var(--primary-light)}
.ann-table .mark-text{font-weight:500}
.has-sign{cursor:pointer}
.has-sign:hover,.has-sign:focus{background:var(--primary-light)!important}
.has-sign td:last-child{min-width:2.75rem;text-align:center}
.sign-detail td{padding:0.5rem 1rem 0.5rem 1.5rem}
.sign-content{font-size:0.8rem;color:var(--warning);background:var(--warning-bg);padding:0.5rem 0.75rem;border-radius:var(--radius);display:flex;align-items:flex-start;gap:0.4rem;border-left:3px solid currentColor}
.sign-content::before{content:"!";font-weight:700;flex-shrink:0;width:1rem;text-align:center}
.sign-badge{display:inline-block;font-size:0.65rem;font-weight:700;color:var(--warning);background:var(--warning-bg);border-radius:2px;padding:0.1rem 0.3rem;line-height:1.3;cursor:pointer}
.sign-ref{font-size:0.7rem;font-weight:600;color:var(--text-muted);margin-right:0.25rem}

/* ── Voorbeeldreeksen ── */
.voorbeeld{
  padding:0.75rem 1rem;margin:0.5rem 0;
  border-left:4px solid var(--success);background:var(--success-bg);
  border-radius:0 var(--radius) var(--radius) 0;
  font-size:0.85rem;line-height:1.6;
}
.voorbeeld.ongeldig{border-left-color:var(--error);background:var(--error-bg)}
.voorbeeld-label{font-weight:700;color:var(--success)}
.voorbeeld.ongeldig .voorbeeld-label{color:var(--error)}

/* ── Detail pagina layout ── */
.detail-layout{display:grid;grid-template-columns:1fr;gap:1rem}
.detail-layout > *{min-width:0}
@media(min-width:768px){.detail-layout{grid-template-columns:1fr 300px}}

/* ── Formele regelbox — RS-notatie ── */
.regel-box{
  background:var(--card-bg);
  border:1px solid var(--border);border-left:4px solid var(--accent);
  padding:1rem 1.25rem;
  border-radius:0 var(--radius) var(--radius) 0;
  margin-bottom:1rem;
  font-family:var(--font-serif);font-size:0.95rem;line-height:1.75;
  white-space:pre-wrap;overflow-wrap:break-word;word-break:break-word;
}

/* ── Zoekveld — WCAG-conform, min 48px hoogte ── */
.search-input{
  width:100%;
  padding:0 1rem;min-height:48px;
  border:2px solid var(--border);border-radius:var(--radius-input);
  font-size:1rem;font-family:var(--font);
  background:var(--card-bg);color:var(--text);
  transition:border-color 0.2s,box-shadow 0.2s;
  margin-bottom:1rem;-webkit-appearance:none;
}
.search-input:focus{outline:none;border-color:var(--primary);box-shadow:var(--focus-ring)}
.search-input::placeholder{color:var(--text-muted)}

/* ── Filter chips — pilbuttonvorm toegestaan voor tags (rijkshuisstijl §knoppen) ── */
.search-filters{display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:1rem}
.filter-chip{
  padding:0.3rem 0.875rem;border-radius:20px;
  border:1px solid var(--border);background:var(--card-bg);
  color:var(--text-secondary);font-size:0.8rem;
  cursor:pointer;transition:all 0.15s;
  font-family:var(--font);
}
.filter-chip.active,.filter-chip:hover{border-color:var(--primary);background:var(--primary-light);color:var(--primary)}
.filter-chip:focus-visible{outline:2px solid var(--primary);outline-offset:2px}

/* ── Zoekresultaten ── */
.search-result{padding:0.875rem 0.5rem;border-bottom:1px solid var(--border);cursor:pointer;transition:background 0.15s;border-radius:var(--radius);margin:0 -0.5rem}
.search-result:hover{background:var(--primary-light)}
.search-result:last-child{border-bottom:none}
.search-result-title{font-weight:600;color:var(--text)}
.search-result-excerpt{font-size:0.85rem;color:var(--text-muted);margin-top:0.25rem;line-height:1.45}
.search-result-meta{font-size:0.75rem;color:var(--text-muted);margin-top:0.2rem}
.search-result-meta span{margin-right:0.75rem}
.no-results{color:var(--text-muted);text-align:center;padding:2.5rem;font-size:0.9rem}

/* ── Kennisgraaf ── */
.graph-container{width:100%;height:clamp(400px,60vh,700px);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;position:relative;background:var(--card-bg)}
.graph-container svg{display:block}
.graph-legend{position:absolute;bottom:1rem;right:1rem;background:var(--card-bg);border:1px solid var(--border);border-radius:var(--radius);padding:0.75rem 0.875rem;font-size:0.75rem;z-index:10;box-shadow:var(--shadow);max-width:180px}
.graph-legend-title{font-weight:700;font-size:0.73rem;text-transform:uppercase;letter-spacing:0.06em;color:var(--text-secondary);margin-bottom:0.5rem}
.graph-legend-item{display:flex;align-items:center;gap:0.5rem;margin:0.3rem 0;font-size:0.75rem;color:var(--text-secondary)}
.graph-legend-dot{width:9px;height:9px;border-radius:50%;flex-shrink:0}
.graph-legend-diamond{width:9px;height:9px;flex-shrink:0;transform:rotate(45deg);border-radius:1px}

/* Graph toolbar — filter + reset op één lijn */
.graph-toolbar{
  display:flex;align-items:center;gap:0.75rem;
  margin-bottom:0.75rem;flex-wrap:wrap;
}
.graph-toolbar label{font-size:0.875rem;color:var(--text-secondary);font-weight:500;white-space:nowrap}
.graph-toolbar select{
  height:36px;padding:0 0.75rem;
  border:1px solid var(--border);border-radius:var(--radius-input);
  font-size:0.875rem;font-family:var(--font);
  background:var(--card-bg);color:var(--text);cursor:pointer;
}
.graph-toolbar select:focus{outline:none;border-color:var(--primary);box-shadow:var(--focus-ring)}
.graph-count{font-size:0.8rem;color:var(--text-muted);margin-left:auto}
.btn-secondary{
  height:36px;padding:0 0.875rem;
  border:1px solid var(--border);border-radius:var(--radius-btn);
  font-size:0.875rem;font-family:var(--font);
  background:var(--card-bg);color:var(--text-secondary);
  cursor:pointer;transition:border-color 0.15s,color 0.15s,background 0.15s;
  white-space:nowrap;
}
.btn-secondary:hover{border-color:var(--primary);color:var(--primary);background:var(--primary-light)}
.btn-secondary:focus-visible{outline:2px solid var(--primary);outline-offset:2px}

/* ── Footer — meer ruimte, professionele afstand ── */
footer{
  text-align:center;
  padding:2rem 1.5rem;
  color:var(--text-muted);font-size:0.8rem;
  border-top:1px solid var(--border);
  margin-top:auto;line-height:1.6;
}

/* ── Graaf fullscreen ── */
.graph-fullscreen{
  position:fixed!important;top:0;left:0;
  width:100vw!important;height:100vh!important;
  z-index:9999;border-radius:0!important;border:none!important;
  background:var(--card-bg)!important;
}
.graph-close-btn{
  display:none;
  position:absolute;top:0.75rem;right:0.75rem;z-index:10001;
  width:36px;height:36px;
  align-items:center;justify-content:center;
  background:var(--card-bg);border:1px solid var(--border);
  border-radius:var(--radius);color:var(--text-secondary);
  font-size:1rem;cursor:pointer;line-height:1;
  box-shadow:var(--shadow);
  transition:background 0.15s,color 0.15s;
}
.graph-close-btn:hover{background:var(--primary-light);color:var(--primary)}
.graph-close-btn:focus-visible{outline:2px solid var(--primary);outline-offset:2px}

/* ── 404 ── */
.error-page{text-align:center;padding:4rem 1rem}
.error-page h1{font-size:5rem;color:var(--primary);margin-bottom:0.5rem;font-weight:300;letter-spacing:-0.03em}
.error-page p{color:var(--text-muted);margin-bottom:1.5rem}

/* ── Screenreader-only — WCAG 1.1.1 ── */
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}

/* ── Responsive helpers ── */
@media(min-width:480px){.hide-xs{display:inline!important}}
@media(max-width:479px){.hide-xs{display:none!important}}
@media(min-width:768px){.hide-md{display:none!important}}
@media(max-width:767px){.show-md{display:none!important}}

/* ── Print — WCAG PDF-vriendelijk ── */
@media print {
  .nav,.skip-link,.hamburger,.dark-toggle,.graph-container,.graph-filter,.graph-legend,.search-input,.search-filters{display:none!important}
  body{font-size:11pt;line-height:1.5;color:#000;background:#fff;min-height:auto}
  a{color:#000;text-decoration:underline}
  .card{box-shadow:none;border:1px solid #bbb;break-inside:avoid;page-break-inside:avoid}
  .card-title{border-bottom-color:#bbb}
  .detail-layout{display:block}
  .detail-layout > div{width:100%!important}
  .mermaid svg{max-width:100%;overflow:visible}
  .ann-table{min-width:auto;font-size:8pt}
  a[href]:after{content:" (" attr(href) ")";font-size:0.75rem;color:#555}
  .breadcrumb a[href]:after{content:none}
  .regel-box{white-space:normal;border-color:#bbb}
  footer{display:none}
}
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
        cls = ' class="active" aria-current="page"' if label.lower() == active.lower() else ""
        links += f'<a href="{url}"{cls}>{label}</a>\n'
    return f"""<nav class="nav">
<div class="container">
  <div class="nav-logo"><a href="{p}index.html" aria-label="Home">Inningsmodel</a></div>
  <button class="dark-toggle" id="darkToggle" aria-label="Donker/licht modus wisselen" title="Donker/licht modus" type="button">
    <span class="dt-icon">&#x2600;</span>
  </button>
  <button class="hamburger" id="hamburger" aria-label="Menu openen" aria-expanded="false" type="button">
    <span class="hamburger-label" aria-hidden="true">Menu</span>
    <span class="hamburger-lines"><span></span><span></span><span></span></span>
  </button>
  <div class="nav-links">
    {links}
  </div>
</div>
</nav>"""


def pagina(title: str, body: str, active: str = "", p: str = "", extra_scripts: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="nl" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Inningsmodel</title>
<link rel="icon" type="image/svg+xml" href="{p}icons/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="{p}icons/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="{p}icons/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="{p}icons/apple-touch-icon.png">
<link rel="manifest" href="{p}manifest.json">
<meta name="theme-color" content="#154273">
<link rel="stylesheet" href="{p}css/style.css">
</head>
<body>
<a href="#main-content" class="skip-link">Direct naar inhoud</a>
{gen_nav(active, p)}
<main id="main-content"><div class="container">
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


def breadcrumb(p: str, active: str, crumbs: list[tuple[str, str]]) -> str:
    items = "".join(f'<li><a href="{url}">{label}</a></li>' for url, label in crumbs)
    return f'<nav aria-label="U bevindt zich hier"><ol class="breadcrumb">{items}<li aria-current="page">{active}</li></ol></nav>'


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
                "rij_id": r.get("rij-id", ""),
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
            "bwb_id": data.get("bwb-id", ""),
            "artikel": str(data.get("artikel", "") or ""),
            "lid": str(data.get("lid", "") or ""),
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
    schrijf_html(out, "index.html", "Dashboard | Belastingdienst", body, active="dashboard")


def gen_begrippen(out: Path, begrippen: list, annotaties: list):
    # Lookup: begrip_id → slug (gebaseerd op naam, niet op ID-deel)
    slug_by_bid: dict[str, str] = {b["id"]: b["slug"] for b in begrippen}
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
        f'<div class="item-badges">{jas_tag(b["jas_klasse"])}<span class="badge badge-soort">{b["soort"]}</span>{status_badge(b["status"])}</div>'
        f'<span class="item-meta">ID: {b["id"]}</span>'
        f'</li>\n'
        for b in begrippen
    )
    body = f"""<h1>Begrippen ({len(begrippen)})</h1>
<label for="filterInput" class="sr-only">Filter op naam</label>
<input type="text" class="search-input" id="filterInput" placeholder="Filter op naam..." autofocus>
<div class="item-list" id="itemList">{items}</div>
<script>
document.getElementById('filterInput')?.addEventListener('input',function(){{
  var q=this.value.toLowerCase(),list=document.getElementById('itemList'),li=list.getElementsByTagName('li');
  for(var i=0;i<li.length;i++){{li[i].style.display=li[i].textContent.toLowerCase().indexOf(q)>-1?'':'none'}}
}});
</script>"""
    schrijf_html(out, "begrippen.html", "Begrippen | Belastingdienst", body, active="begrippen")

    pp = "../"  # prefix voor detail-pagina's in subdirectory
    for b in begrippen:
        rel_html = ""
        for rt, label in [("is-een", "Is een"), ("heeft", "Heeft"), ("leidt-tot", "Leidt tot")]:
            targets = b["relaties"][rt]
            if targets:
                rel_html += f"<p style='margin-top:0.5rem'><strong>{label}</strong></p><ul style='margin-left:1.25rem'>"
                for t in targets:
                    t_slug = slug_by_bid.get(t) or slugify(t.rsplit("/", 1)[-1])
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
  <div class="table-scroll">
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
        b_br = breadcrumb(pp, b["naam"], [(f"{pp}index.html", "Home"), (f"{pp}begrippen.html", "Begrippen")])
        body = f"""{b_br}
<h1>{b["naam"]}</h1>
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
        schrijf_html(out, f'begrippen/{b["slug"]}.html', f'{b["naam"]} | Belastingdienst', body, active="begrippen", p="../")


def gen_annotaties(out: Path, annotaties: list, regels: list, begrippen: list):
    # Lookup: begrip_id → slug (gebaseerd op naam, niet op ID-deel)
    slug_by_bid: dict[str, str] = {b["id"]: b["slug"] for b in begrippen}
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
        f'<div class="item-badges"><span class="badge badge-type">{a.get("bwb_id","")}</span></div>'
        f'<span class="item-meta">{a["structuurpositie"]}</span>'
        f'</li>\n'
        for a in annotaties
    )
    body = f"""<h1>Annotaties ({len(annotaties)})</h1>
<label for="filterInput" class="sr-only">Filter op wet of artikel</label>
<input type="text" class="search-input" id="filterInput" placeholder="Filter op wet of artikel..." autofocus>
<div class="item-list" id="itemList">{items}</div>
<script>
document.getElementById('filterInput')?.addEventListener('input',function(){{
  var q=this.value.toLowerCase(),list=document.getElementById('itemList'),li=list.getElementsByTagName('li');
  for(var i=0;i<li.length;i++){{li[i].style.display=li[i].textContent.toLowerCase().indexOf(q)>-1?'':'none'}}
}});
</script>"""
    schrijf_html(out, "annotaties.html", "Annotaties | Belastingdienst", body, active="annotaties")

    for a in annotaties:
        rijen = ""
        for r in a["rijen"]:
            bgp_link = ""
            if r.get("begrip_id"):
                slug = slug_by_bid.get(r["begrip_id"]) or slugify(r["begrip_id"].rsplit("/", 1)[-1])
                bgp_link = f'<a href="../begrippen/{slug}.html" style="word-break:break-all;font-size:0.8rem">{r["begrip_id"]}</a>'
            sign = r.get("signalering")
            if sign:
                # Expandable row met signalering
                rid = r.get("rij_id", "")
                label = f'<span class="sign-ref">{rid}</span>' if rid else ""
                rijen += f'<tr class="has-sign" onclick="var d=this.nextElementSibling;d.style.display=d.style.display===\'none\'?\'table-row\':\'none\'">'
                rijen += f'<td class="mark-text">"{r["markering"]}"</td><td>{jas_tag(r["jas_klasse"])}</td><td>{bgp_link}</td>'
                rijen += f'<td style="text-align:center"><span class="sign-badge">[!]</span></td></tr>\n'
                rijen += f'<tr class="sign-detail" style="display:none"><td colspan="4"><div class="sign-content">{label}{sign}</div></td></tr>\n'
            else:
                rijen += f'<tr><td class="mark-text">"{r["markering"]}"</td><td>{jas_tag(r["jas_klasse"])}</td><td>{bgp_link}</td><td style="text-align:center"></td></tr>\n'
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
        ann_title = f'{a["wet"]} art. {a["artikel"]}{lid}'
        ann_br = breadcrumb("../", ann_title, [("../index.html", "Home"), ("../annotaties.html", "Annotaties")])
        body = f"""{ann_br}
<h1>{ann_title}</h1>
<p class="subtitle">{a["structuurpositie"]} &bull; {a["bwb_id"]}</p>
<div class="wetstekst">"{a["wetstekst"]}"</div>
<div class="card">
<div class="card-title">Annotatierijen</div>
<div class="table-scroll">
<table class="ann-table">
  <tr><th>Markering</th><th>JAS-klasse</th><th>Begrip</th><th style="text-align:center">Signaal</th></tr>
  {rijen}
</table></div>
</div>
{mermaid_src}
{regel_links}"""
        schrijf_html(out, f'annotaties/{a["id"].replace("/","-")}.html', f'Annotatie art. {a["artikel"]} | Belastingdienst', body, active="annotaties", p="../", extra_scripts=extra_scripts)


def gen_regels(out: Path, regels: list, begrippen: list, annotaties: list):
    slug_by_bid = {b["id"]: b["slug"] for b in begrippen}
    def _link(ref: str) -> str:
        slug = slug_by_bid.get(ref)
        return f'<a href="../begrippen/{slug}.html">{ref}</a>' if slug else ref
    # Build annotation lookup: (bwb_id, artikel, lid) → annotatie data
    ann_by_key: dict[tuple[str, str, str], dict] = {}
    for a in annotaties:
        ann_by_key[(a["bwb_id"], a["artikel"], a.get("lid", ""))] = a
    items = "".join(
        f'<li onclick="window.location=\'regels/{r["id"]}.html\'">'
        f'<a href="regels/{r["id"]}.html" class="item-title">{r["naam"]}</a>'
        f'<div class="item-badges"><span class="badge badge-definitief">{r["soort"]}</span></div>'
        f'<span class="item-meta">ID: {r["id"]}</span>'
        f'</li>\n'
        for r in regels
    )
    body = f"""<h1>Afleidingsregels ({len(regels)})</h1>
<label for="filterInput" class="sr-only">Filter op naam of ID</label>
<input type="text" class="search-input" id="filterInput" placeholder="Filter op naam of ID..." autofocus>
<div class="item-list" id="itemList">{items}</div>
<script>
document.getElementById('filterInput')?.addEventListener('input',function(){{
  var q=this.value.toLowerCase(),list=document.getElementById('itemList'),li=list.getElementsByTagName('li');
  for(var i=0;i<li.length;i++){{li[i].style.display=li[i].textContent.toLowerCase().indexOf(q)>-1?'':'none'}}
}});
</script>"""
    schrijf_html(out, "regels.html", "Regels | Belastingdienst", body, active="regels")

    for r in regels:
        vb = ""
        for v in r.get("voorbeeldreeksen") or []:
            juist = v.get("juridisch-juist", True)
            cls = "voorbeeld" if juist else "voorbeeld ongeldig"
            label = "[+]" if juist else "[-]"
            vb += f'<div class="{cls}"><span class="voorbeeld-label">{label}</span> <strong>Invoer:</strong> {v.get("invoerwaarden","")}<br><strong>Uitvoer:</strong> {v.get("verwachte-uitkomst","")}</div>'
        ops = ", ".join(r.get("operators") or [])
        ann_link = ""
        if r["bwb_id"] and r["artikel"]:
            match = ann_by_key.get((r["bwb_id"], r["artikel"], r["lid"]))
            if match:
                ann_url = f'../annotaties/{match["id"].replace("/","-")}.html'
                ann_title = f'{match["wet"]} art. {match["artikel"]}{", lid " + match["lid"] if match.get("lid") else ""}'
                ann_link = f'<div class="card"><div class="card-title">Annotatie</div><p><a href="{ann_url}">{ann_title}</a></p></div>'
        r_br = breadcrumb("../", r["naam"], [("../index.html", "Home"), ("../regels.html", "Regels")])
        body = f"""{r_br}
<h1>{r["naam"]}</h1>
<p class="subtitle"><span class="badge badge-definitief">{r["soort"]}</span> {r["id"]}</p>
<div class="card">
  <div class="card-title">Formele regel</div>
  <div class="regel-box">{r["formele_regel"]}</div>
</div>
<div class="card">
  <div class="card-title">Toelichting</div>
  <p>{r["toelichting"] or "<em>Geen toelichting</em>"}</p>
</div>
{ann_link}
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
        schrijf_html(out, f'regels/{r["id"]}.html', f'{r["naam"]} | Belastingdienst', body, active="regels", p="../")


def gen_graph(out: Path, begrippen: list, regels: list, annotaties: list):
    nodes: list[dict] = []
    node_ids: set[str] = set()
    links: list[dict] = []
    def add_node(nid: str, label: str, groep: str, node_type: str = "begrip", page: str | None = None):
        if nid not in node_ids:
            nd: dict[str, Any] = {"id": nid, "label": label, "groep": groep, "type": node_type}
            if page:
                nd["page"] = page
            nodes.append(nd)
            node_ids.add(nid)
    # First pass: alle bekende begrippen (zodat JAS-klasse niet overschreven wordt)
    for b in begrippen:
        add_node(b["id"], b["naam"], b["jas_klasse"], "begrip", f'begrippen/{b["slug"]}.html')
    # Second pass: relaties (onbekende nodes alleen als ze niet in de vault zitten)
    for b in begrippen:
        for rt in ("is-een", "heeft", "leidt-tot"):
            for target in b["relaties"][rt]:
                if target not in node_ids:
                    add_node(target, target.rsplit("/", 1)[-1], "onbekend", "begrip", None)
                links.append({"source": b["id"], "target": target, "relatie": rt})
    for r in regels:
        add_node(r["id"], r["naam"], "afleidingsregel", "regel", f'regels/{r["id"]}.html')
        for inv in r.get("invoer") or []:
            if inv not in node_ids:
                add_node(inv, inv.rsplit("/", 1)[-1], "onbekend", "begrip", None)
            links.append({"source": r["id"], "target": inv, "relatie": "invoer"})
        for uitv in r.get("uitvoer") or []:
            if uitv not in node_ids:
                add_node(uitv, uitv.rsplit("/", 1)[-1], "onbekend", "begrip", None)
            links.append({"source": r["id"], "target": uitv, "relatie": "uitvoer"})
    gr_data = json.dumps({"nodes": nodes, "links": links}, ensure_ascii=False)
    kleuren_json = json.dumps(JAS_KLEUREN, ensure_ascii=False)
    # Alleen klassen die ook daadwerkelijk in de data voorkomen
    aanwezige_klassen = sorted({n["groep"] for n in nodes if n["groep"] != "onbekend"})
    klasse_opties = "".join(f'<option value="{k}">{k}</option>' for k in aanwezige_klassen)
    body = f"""<h1>Kennisgraaf</h1>
<p class="subtitle">Interactieve graaf van begrippen (cirkels) en afleidingsregels (ruiten). Sleep nodes om te herschikken.</p>
<div class="graph-toolbar">
  <label for="klasseFilter">JAS-klasse:</label>
  <select id="klasseFilter" aria-label="Filter op JAS-klasse">
    <option value="all">Alle klassen</option>
    {klasse_opties}
  </select>
  <span class="graph-count" id="nodeCount"></span>
  <button class="btn-secondary" id="resetBtn" type="button">Reset weergave</button>
  <button class="btn-secondary" id="fullscreenBtn" type="button" aria-label="Volledig scherm" title="Volledig scherm">&#x26F6; Volledig scherm</button>
</div>
<div class="graph-container" id="graphContainer">
  <button class="graph-close-btn" id="graphCloseBtn" type="button" aria-label="Volledig scherm sluiten" title="Sluiten">&#x2715;</button>
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
var zoom = d3.zoom().scaleExtent([0.1, 8]).on("zoom", function(e){{ g.attr("transform", e.transform); }});
svg.call(zoom).on("dblclick.zoom", null);
g.append("rect").attr("x",-width*5).attr("y",-height*5).attr("width",width*10).attr("height",height*10).attr("fill","none").attr("pointer-events","all");
svg.append("defs").append("marker").attr("id","arrow").attr("viewBox","0 -5 10 10").attr("refX",20).attr("refY",0).attr("markerWidth",6).attr("markerHeight",6).attr("orient","auto")
  .append("path").attr("d","M0,-5L10,0L0,5").attr("fill","#94a3b8");
var link = g.append("g").selectAll("line").data(data.links).join("line")
  .attr("stroke","#94a3b8").attr("stroke-width",1).attr("stroke-opacity",0.5).attr("marker-end","url(#arrow)");
var node = g.append("g").selectAll("g").data(data.nodes).join("g").call(
  d3.drag().on("start",function(e,d){{if(!e.active)simulation.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y}})
  .on("drag",function(e,d){{d.fx=e.x;d.fy=e.y}})
  .on("end",function(e,d){{if(!e.active)simulation.alphaTarget(0);d.fx=null;d.fy=null}}));
node.append("title").text(function(d){{return d.label}});
node.append("path")
  .attr("d",function(d){{return d.type==='regel'?d3.symbol().type(d3.symbolDiamond).size(220)():null}})
  .attr("fill",function(d){{return colorMap[d.groep]||'#94a3b8'}}).attr("stroke","#fff").attr("stroke-width",1.5)
  .attr("opacity",function(d){{return d.type==='regel'?1:0}});
node.append("circle").attr("r",7)
  .attr("fill",function(d){{return colorMap[d.groep]||'#94a3b8'}}).attr("stroke","#fff").attr("stroke-width",1.5)
  .attr("opacity",function(d){{return d.type==='begrip'?1:0}});
var nodeText = node.append("text").attr("dx",12).attr("dy",4).attr("font-size","11px")
  .text(function(d){{return d.label.length>28?d.label.slice(0,25)+'…':d.label}});
function updateTextColor(){{
  nodeText.attr("fill",document.documentElement.getAttribute('data-theme')==='dark'?'#dce8f0':'#2d3f52');
}}
updateTextColor();
new MutationObserver(updateTextColor).observe(document.documentElement,{{attributes:true,attributeFilter:['data-theme']}});
node.on("click",function(e,d){{if(d.page)window.location.href=d.page;}});
node.style("cursor",function(d){{return d.page?'pointer':'default'}});
var simulation = d3.forceSimulation(data.nodes)
  .force("link",d3.forceLink(data.links).id(function(d){{return d.id}}).distance(100))
  .force("charge",d3.forceManyBody().strength(-180))
  .force("center",d3.forceCenter(width/2,height/2))
  .force("collision",d3.forceCollide(18));
simulation.on("tick",function(){{
  link.attr("x1",function(d){{return d.source.x}}).attr("y1",function(d){{return d.source.y}})
      .attr("x2",function(d){{return d.target.x}}).attr("y2",function(d){{return d.target.y}});
  node.attr("transform",function(d){{return"translate("+d.x+","+d.y+")"}});
}});
var defaultTransform = d3.zoomIdentity.translate(width/2,height/2).scale(0.85).translate(-width/2,-height/2);
simulation.on("end",function(){{
  svg.transition().duration(600).call(zoom.transform, defaultTransform);
}});
function resetView(){{
  document.getElementById('klasseFilter').value='all';
  applyFilter('all');
  svg.transition().duration(500).call(zoom.transform, defaultTransform);
}}
document.getElementById('resetBtn').addEventListener('click', resetView);

// Legenda — alleen klassen die in de data voorkomen
var aanwezigeKlassen = Array.from(new Set(data.nodes.map(function(d){{return d.groep}}))).filter(function(k){{return k!=='onbekend'&&colorMap[k]}});
var legend = d3.select("#graphLegend");
legend.append("div").attr("class","graph-legend-title").text("Legenda");
// begrippen (cirkel)
var bRow = legend.append("div").attr("class","graph-legend-item");
bRow.append("div").attr("class","graph-legend-dot").style("background","#94a3b8");
bRow.append("span").text("begrip");
// regels (ruit)
var rRow = legend.append("div").attr("class","graph-legend-item");
rRow.append("div").attr("class","graph-legend-diamond").style("background","#94a3b8");
rRow.append("span").text("afleidingsregel (ruit)");
legend.append("div").style("border-top","1px solid var(--border)").style("margin","0.4rem 0");
// kleurlegende
aanwezigeKlassen.sort().forEach(function(k){{
  var row = legend.append("div").attr("class","graph-legend-item");
  row.append("div").attr("class","graph-legend-dot").style("background",colorMap[k]);
  row.append("span").text(k);
}});

// Filter — toont gefilterde nodes volledig, directe buren gedimd, rest verborgen
function updateCount(matchedIds){{
  var el = document.getElementById('nodeCount');
  if(!el) return;
  el.textContent = matchedIds ? matchedIds.size + ' nodes' : '';
}}
function applyFilter(v){{
  if(v==='all'){{
    node.attr("opacity",1);
    link.attr("stroke-opacity",0.5);
    updateCount(null);
    return;
  }}
  var matchedIds = new Set(data.nodes.filter(function(d){{return d.groep===v}}).map(function(d){{return d.id}}));
  var neighborIds = new Set();
  data.links.forEach(function(l){{
    var sid=l.source.id||l.source, tid=l.target.id||l.target;
    if(matchedIds.has(sid)) neighborIds.add(tid);
    if(matchedIds.has(tid)) neighborIds.add(sid);
  }});
  node.attr("opacity",function(d){{
    return matchedIds.has(d.id)?1:neighborIds.has(d.id)?0.35:0.06;
  }});
  link.attr("stroke-opacity",function(d){{
    var sid=d.source.id||d.source, tid=d.target.id||d.target;
    if(matchedIds.has(sid)&&matchedIds.has(tid)) return 0.7;
    if(matchedIds.has(sid)||matchedIds.has(tid)) return 0.3;
    return 0.04;
  }});
  updateCount(matchedIds);
}}
document.getElementById('klasseFilter').addEventListener('change',function(){{applyFilter(this.value)}});

// Resize-handler: past SVG-afmetingen aan bij vensterformaat-wijziging én fullscreen
function resizeGraph(){{
  var container=document.getElementById('graphContainer');
  var newW=container.clientWidth;
  var fs=document.fullscreenElement===container||document.webkitFullscreenElement===container;
  var newH=fs?window.screen.height:Math.max(400,Math.min(window.innerHeight*0.6,700));
  svg.attr('width',newW).attr('height',newH);
  simulation.force('center',d3.forceCenter(newW/2,newH/2)).alpha(0.3).restart();
  defaultTransform=d3.zoomIdentity.translate(newW/2,newH/2).scale(0.85).translate(-newW/2,-newH/2);
}}
window.addEventListener('resize',resizeGraph);

// Fullscreen
var fsBtn=document.getElementById('fullscreenBtn');
var closeBtn=document.getElementById('graphCloseBtn');
var container=document.getElementById('graphContainer');
function enterFullscreen(){{
  if(container.requestFullscreen){{container.requestFullscreen();}}
  else if(container.webkitRequestFullscreen){{container.webkitRequestFullscreen();}}
}}
function exitFullscreen(){{
  if(document.exitFullscreen){{document.exitFullscreen();}}
  else if(document.webkitExitFullscreen){{document.webkitExitFullscreen();}}
}}
function onFullscreenChange(){{
  var fs=document.fullscreenElement===container||document.webkitFullscreenElement===container;
  container.classList.toggle('graph-fullscreen',fs);
  closeBtn.style.display=fs?'flex':'none';
  fsBtn.innerHTML=fs?'&#x2B1C; Normaal':'&#x26F6; Volledig scherm';
  fsBtn.title=fs?'Volledig scherm afsluiten':'Volledig scherm';
  setTimeout(resizeGraph,50);
}}
document.addEventListener('fullscreenchange',onFullscreenChange);
document.addEventListener('webkitfullscreenchange',onFullscreenChange);
if(fsBtn)fsBtn.addEventListener('click',function(){{
  var fs=document.fullscreenElement===container||document.webkitFullscreenElement===container;
  fs?exitFullscreen():enterFullscreen();
}});
if(closeBtn)closeBtn.addEventListener('click',exitFullscreen);
document.addEventListener('keydown',function(e){{
  if(e.key==='Escape'&&(document.fullscreenElement===container||document.webkitFullscreenElement===container))exitFullscreen();
}});
</script>"""
    schrijf_html(out, "graph.html", "Kennisgraaf | Belastingdienst", body, active="graaf")


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
<label for="searchInput" class="sr-only">Zoekterm</label>
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
function escHtml(s){{return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}}
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
  if(q.length < 2){{out.innerHTML='<p class="item-meta" style="padding:1rem 0">Typ minimaal 2 tekens om te zoeken</p>';return}}
  var hits = data.filter(function(d){{
    if(currentFilter !== 'all' && d.type !== currentFilter) return false;
    return d.titel.toLowerCase().indexOf(q) > -1 || d.tekst.toLowerCase().indexOf(q) > -1;
  }});
  if(hits.length === 0){{out.innerHTML='<div class="no-results">Geen resultaten voor "'+escHtml(q)+'"</div>';return}}
  out.innerHTML = '<div style="font-size:0.85rem;color:var(--text-muted);margin-bottom:0.5rem">'+hits.length+' resultaten</div>';
  var html='';
  hits.slice(0,50).forEach(function(d){{
    var rawExcerpt = d.tekst.length > 150 ? d.tekst.substring(0,150)+'...' : d.tekst;
    html += '<div class="search-result" onclick="window.location=\''+d.url+'\'">'+
      '<div class="search-result-title">'+escHtml(d.titel)+'</div>'+
      '<div class="search-result-excerpt">'+escHtml(rawExcerpt)+'</div>'+
      '<div class="search-result-meta"><span>Type: '+escHtml(d.type)+'</span>'+
      (d.jas_klasse?'<span>JAS: '+escHtml(d.jas_klasse)+'</span>':'')+'</div></div>';
  }});
  out.innerHTML += html;
}}
var _st;document.getElementById('searchInput').addEventListener('input',function(){{clearTimeout(_st);_st=setTimeout(doSearch,200)}});
</script>"""
    schrijf_html(out, "search.html", "Zoeken | Belastingdienst", body, active="zoeken")


def gen_404(out: Path):
    body = """<div class="error-page">
<h1>404</h1>
<p>Deze pagina bestaat niet.</p>
<a href="./" class="filter-chip active">Terug naar dashboard</a>
</div>"""
    schrijf_html(out, "404.html", "Pagina niet gevonden | Belastingdienst", body)


def gen_css_js(out: Path):
    (out / "css").mkdir(parents=True, exist_ok=True)
    (out / "css/style.css").write_text(CSS)
    js = """document.addEventListener('DOMContentLoaded',function(){
  var toggle=document.getElementById('darkToggle'),root=document.documentElement;
  function setTheme(t){
    root.setAttribute('data-theme',t);localStorage.setItem('theme',t);
    if(toggle){
      var ic=toggle.querySelector('.dt-icon');
      if(ic)ic.textContent=t==='dark'?'\u263D':'\u2600';
    }
  }
  var stored=localStorage.getItem('theme');
  if(stored){setTheme(stored)}else if(window.matchMedia&&window.matchMedia('(prefers-color-scheme:dark)').matches){setTheme('dark')}else{setTheme('light')}
  if(toggle)toggle.addEventListener('click',function(){setTheme(root.getAttribute('data-theme')==='dark'?'light':'dark')});
  window.matchMedia('(prefers-color-scheme:dark)').addEventListener('change',function(e){if(!localStorage.getItem('theme'))setTheme(e.matches?'dark':'light')});
  var hamburger=document.getElementById('hamburger'),navLinks=document.querySelector('.nav-links');
  if(hamburger&&navLinks){
    function setMenu(open){
      hamburger.setAttribute('aria-expanded',String(open));
      hamburger.setAttribute('aria-label',open?'Menu sluiten':'Menu openen');
      hamburger.classList.toggle('open',open);
      navLinks.classList.toggle('open',open);
      var lbl=hamburger.querySelector('.hamburger-label');
      if(lbl)lbl.textContent=open?'Sluit':'Menu';
    }
    hamburger.addEventListener('click',function(){
      setMenu(hamburger.getAttribute('aria-expanded')!=='true');
    });
    navLinks.querySelectorAll('a').forEach(function(l){l.addEventListener('click',function(){setMenu(false)})});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&navLinks.classList.contains('open')){setMenu(false);hamburger.focus()}});
    document.addEventListener('click',function(e){if(navLinks.classList.contains('open')&&!navLinks.contains(e.target)&&!hamburger.contains(e.target)){setMenu(false)}});
  }
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
        manifest.write_text("""{"name":"Belastingdienst — Kennismodel Invordering","short_name":"Kennismodel","start_url":".","display":"standalone","background_color":"#154273","theme_color":"#154273","icons":[{"src":"icons/favicon-192.png","sizes":"192x192","type":"image/png"},{"src":"icons/favicon-512.png","sizes":"512x512","type":"image/png"}]}""")


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
    gen_regels(out, regels, begrippen, annotaties)
    gen_graph(out, begrippen, regels, annotaties)
    gen_search(out, begrippen, annotaties, regels)

    print(f"Webapp gegenereerd in {out}/ ({len(list(out.rglob('*')))} bestanden)", file=sys.stderr)


if __name__ == "__main__":
    main()
