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

SOORT_ICON: dict[str, str] = {
    "booleaans": "✓",
    "datum": "📅",
    "entiteit": "🏛",
    "enumeratie": "📋",
    "monetair-bedrag": "€",
    "percentage": "%",
    "tekst": "Aa",
    "tijdsduur": "⏱",
}


def laad_begrippen(vault_root: Path) -> list[dict]:
    begrippen = []
    pad = vault_root / "begrippen"
    for f in sorted(pad.glob("*.yaml")):
        data = yaml.safe_load(f.read_text()) or {}
        relaties: dict = data.get("relaties") or {}
        klasse = "onbekend"
        # Bepaal JAS-klasse op basis van markeringen
        for m in data.get("markeringen") or []:
            if m.get("bijdrage") == "primair":
                break
        else:
            # Val terug op basis van soort
            soort = data.get("soort", "")
            if soort == "booleaans":
                klasse = "voorwaarde"
            elif soort in ("datum", "tijdsduur"):
                klasse = "tijdsaanduiding"
            elif soort == "monetair-bedrag":
                klasse = "variabele"
            elif soort == "enumeratie":
                klasse = "rechtsobject"
        begrippen.append({
            "id": data.get("begrip-id", f.stem),
            "naam": data.get("begripsnaam", f.stem),
            "slug": slugify(data.get("begripsnaam", f.stem)),
            "definitie": data.get("definitie", ""),
            "soort": data.get("soort", ""),
            "herkomst": data.get("herkomst", ""),
            "status": data.get("status", "concept"),
            "aliases": data.get("aliases") or [],
            "relaties": {
                "is-een": [r if isinstance(r, str) else r.get("begrip-id", "") for r in (relaties.get("is-een") or [])],
                "heeft": [r if isinstance(r, str) else r.get("begrip-id", "") for r in (relaties.get("heeft") or [])],
                "leidt-tot": [r if isinstance(r, str) else r.get("begrip-id", "") for r in (relaties.get("leidt-tot") or [])],
            },
            "afleidingsregel-id": data.get("afleidingsregel-id"),
            "tussenresultaat": data.get("tussenresultaat", False),
            "jas_klasse": klasse,
        })
    return begrippen


def laad_annotaties(vault_root: Path) -> list[dict]:
    annotaties = []
    pad = vault_root / "annotaties"
    for json_file in sorted(pad.rglob("*.json")):
        data = json.loads(json_file.read_text())
        aid = data.get("annotatie-id") or ""
        wetstekst = data.get("wetstekst") or ""
        # Skip metadata-only bestanden (geen annotatie-id of geen wetstekst)
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
            "id": data.get("annotatie-id", ""),
            "bwb_id": data.get("bwb-id", ""),
            "wet": data.get("wet", ""),
            "artikel": data.get("artikel", ""),
            "lid": data.get("lid") or data.get("sectie", ""),
            "structuurpositie": data.get("structuurpositie", ""),
            "wetstekst": data.get("wetstekst", ""),
            "rijen": rijen,
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


# ── Templates ──────────────────────────────────────────────

HEAD = """<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Belastingdienst</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif; background: #f5f5f5; color: #1a1a1a; line-height: 1.6; }}
a {{ color: #0047A0; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.topbar {{ background: #0047A0; color: #fff; padding: 0.75rem 2rem; display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }}
.topbar .logo {{ font-weight: 700; font-size: 1.2rem; letter-spacing: 0.02em; }}
.topbar .logo span {{ opacity: 0.8; font-weight: 400; }}
.topbar nav {{ display: flex; gap: 1.5rem; margin-left: auto; }}
.topbar nav a {{ color: #fff; font-size: 0.9rem; padding: 0.25rem 0; border-bottom: 2px solid transparent; }}
.topbar nav a:hover {{ border-bottom-color: #fff; text-decoration: none; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
.card {{ background: #fff; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1.5rem; }}
.card h2 {{ color: #0047A0; font-size: 1.1rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #e8e8e8; }}
h1 {{ font-size: 1.8rem; color: #1a1a1a; margin-bottom: 1rem; }}
h2 {{ font-size: 1.3rem; color: #0047A0; margin-bottom: 0.75rem; }}
h3 {{ font-size: 1.1rem; color: #333; margin-bottom: 0.5rem; }}
.badge {{ display: inline-block; font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 3px; font-weight: 600; }}
.badge-blue {{ background: #e0ecf7; color: #0047A0; }}
.badge-green {{ background: #e6f4ea; color: #1e7e34; }}
.badge-orange {{ background: #fef3e0; color: #e65100; }}
.badge-gray {{ background: #eee; color: #666; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }}
.stat {{ text-align: center; padding: 1.5rem; }}
.stat-nr {{ font-size: 2.5rem; font-weight: 700; color: #0047A0; }}
.stat-label {{ font-size: 0.85rem; color: #666; margin-top: 0.25rem; }}
.tag {{ display: inline-block; padding: 0.1rem 0.4rem; border-radius: 3px; font-size: 0.75rem; color: #fff; margin: 0.1rem; }}
.wetstekst {{ background: #f8f9fa; border-left: 3px solid #0047A0; padding: 1rem; font-style: italic; margin-bottom: 1rem; border-radius: 0 4px 4px 0; }}
.annotatie-rij {{ display: flex; gap: 0.75rem; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #eee; }}
.annotatie-rij:last-child {{ border-bottom: none; }}
.rij-markering {{ flex: 1; }}
.rij-klasse {{ min-width: 110px; text-align: center; }}
.rij-begrip {{ min-width: 180px; }}
.search-box {{ width: 100%; padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; margin-bottom: 1rem; }}
.search-box:focus {{ outline: none; border-color: #0047A0; box-shadow: 0 0 0 2px rgba(0,71,160,0.15); }}
.results {{ list-style: none; }}
.results li {{ padding: 0.75rem; border-bottom: 1px solid #eee; cursor: pointer; }}
.results li:hover {{ background: #f0f4ff; }}
.voorbeeld {{ background: #f8f9fa; border-left: 3px solid #70AD47; padding: 0.75rem; margin: 0.5rem 0; border-radius: 0 4px 4px 0; font-size: 0.9rem; }}
.voorbeeld.fout {{ border-left-color: #FF0000; }}
footer {{ text-align: center; padding: 2rem; color: #999; font-size: 0.8rem; }}
@media (max-width: 768px) {{ .topbar {{ flex-direction: column; text-align: center; }} .topbar nav {{ margin-left: 0; }} .grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<div class="topbar">
  <div class="logo">Belastingdienst <span>| Kennismodel Invordering</span></div>
  <nav>
    <a href="../index.html">Dashboard</a>
    <a href="../begrippen.html">Begrippen</a>
    <a href="../annotaties.html">Annotaties</a>
    <a href="../regels.html">Regels</a>
    <a href="../graph.html">Graaf</a>
    <a href="../search.html">Zoeken</a>
  </nav>
</div>
<div class="container">
"""

FOOT = """</div>
<footer>Gegenereerd uit de juridische analyses vault &bull; Belastingdienst &bull; Inning &bull; Art. 9 IW 1990</footer>
</body>
</html>"""


def schrijf_html(out: Path, rel: str, title: str, body: str):
    pad = out / rel
    pad.parent.mkdir(parents=True, exist_ok=True)
    html = HEAD.format(title=title) + body + FOOT
    pad.write_text(html)


def jas_tag(klasse: str) -> str:
    kleur = JAS_KLEUREN.get(klasse, "#999")
    return f'<span class="tag" style="background:{kleur}">{klasse}</span>'


def generate_index(out: Path, begrippen: list, annotaties: list, regels: list):
    n_begrip = len(begrippen)
    n_regel = len(regels)
    n_annotatie = len(annotaties)
    n_afleiding = sum(1 for r in regels if r.get("soort") in ("Rekenregel", "Beslissingsregel", "Beperkingsregel", "Specialisatieregel"))
    n_def = sum(1 for b in begrippen if b.get("definitie"))
    n_geen_rel = sum(1 for b in begrippen if not any(b["relaties"].values()))
    by_status: dict[str, int] = {}
    for b in begrippen:
        by_status[b["status"]] = by_status.get(b["status"], 0) + 1
    by_soort: dict[str, int] = {}
    for b in begrippen:
        s = b["soort"] or "onbekend"
        by_soort[s] = by_soort.get(s, 0) + 1
    body = f"""
<h1>Kennismodel Invordering</h1>
<p>Artikel 9 Invorderingswet 1990 — Gestructureerde wetsanalyse volgens JAS v1.0.10</p>
<br>
<div class="grid">
  <div class="card stat"><div class="stat-nr">{n_begrip}</div><div class="stat-label">Begrippen</div></div>
  <div class="card stat"><div class="stat-nr">{n_annotatie}</div><div class="stat-label">Annotaties</div></div>
  <div class="card stat"><div class="stat-nr">{n_regel}</div><div class="stat-label">Afleidingsregels</div></div>
  <div class="card stat"><div class="stat-nr">{n_afleiding}</div><div class="stat-label">Waarvan rekenregels</div></div>
</div>
<div class="grid">
  <div class="card">
    <h2>Voortgang</h2>
    <table style="width:100%;border-collapse:collapse;">
"""
    for status, count in sorted(by_status.items(), reverse=True):
        badge = {"concept": "badge-orange", "definitief": "badge-green", "vervallen": "badge-gray"}.get(status, "badge-blue")
        body += f'      <tr><td><span class="badge {badge}">{status}</span></td><td style="text-align:right">{count}</td></tr>\n'
    body += f"""
    </table>
  </div>
  <div class="card">
    <h2>Soorten begrippen</h2>
    <table style="width:100%;border-collapse:collapse;">
"""
    for soort, count in sorted(by_soort.items()):
        icoon = SOORT_ICON.get(soort, "•")
        body += f'      <tr><td>{icoon} {soort}</td><td style="text-align:right">{count}</td></tr>\n'
    body += f"""
    </table>
  </div>
  <div class="card">
    <h2>Kwaliteit</h2>
    <table style="width:100%;border-collapse:collapse;">
      <tr><td>Met definitie</td><td style="text-align:right">{n_def}/{n_begrip}</td></tr>
      <tr><td>Zonder relaties</td><td style="text-align:right">{n_geen_rel}</td></tr>
    </table>
  </div>
</div>
"""
    schrijf_html(out, "index.html", "Dashboard — Belastingdienst", body)


def generate_begrippen_pagina(out: Path, begrippen: list):
    # Overzicht
    items = "".join(
        f'<li><a href="begrippen/{b["slug"]}.html">{b["naam"]}</a> {jas_tag(b["jas_klasse"])}'
        f' <span class="badge badge-blue">{b["soort"]}</span></li>\n'
        for b in begrippen
    )
    body = f"""
<h1>Begrippen ({len(begrippen)})</h1>
<input type="text" class="search-box" id="filterInput" onkeyup="filterList()" placeholder="Filter begrippen..." autofocus>
<ul class="results" id="itemList">
{items}
</ul>
<script>
function filterList() {{
    var input = document.getElementById('filterInput');
    var filter = input.value.toLowerCase();
    var ul = document.getElementById('itemList');
    var li = ul.getElementsByTagName('li');
    for (var i = 0; i < li.length; i++) {{
        var txt = li[i].textContent || li[i].innerText;
        li[i].style.display = txt.toLowerCase().indexOf(filter) > -1 ? '' : 'none';
    }}
}}
</script>
"""
    schrijf_html(out, "begrippen.html", "Begrippen — Belastingdienst", body)

    # Detailpagina's
    for b in begrippen:
        rel_html = ""
        for rel_type, targets in b["relaties"].items():
            if targets:
                label = {"is-een": "Is een", "heeft": "Heeft", "leidt-tot": "Leidt tot"}.get(rel_type, rel_type)
                rel_html += f"<h3>{label}</h3><ul>"
                for t in targets:
                    t_slug = slugify(t.rsplit("/", 1)[-1])
                    rel_html += f'<li><a href="../begrippen/{t_slug}.html">{t}</a></li>\n'
                rel_html += "</ul>"
        if not rel_html:
            rel_html = '<p class="badge badge-gray">Geen relaties</p>'
        markeringen = ""
        for m in b.get("markeringen", []):
            pass
        jc = b["jas_klasse"]
        body = f"""
<h1>{b["naam"]}</h1>
<p>{jas_tag(jc)} <span class="badge badge-blue">{b["soort"]}</span> <span class="badge badge-orange">{b["status"]}</span></p>
<div class="card">
  <h2>Definitie</h2>
  <p>{b["definitie"] or '<em>Geen definitie</em>'}</p>
  <p style="margin-top:0.5rem;font-size:0.85rem;color:#666;">Herkomst: {b["herkomst"] or "onbekend"} &bull; ID: {b["id"]}</p>
</div>
<div class="card">
  <h2>Relaties</h2>
  {rel_html}
</div>
"""
        schrijf_html(out, f'begrippen/{b["slug"]}.html', f'{b["naam"]} — Belastingdienst', body)


def generate_annotaties_pagina(out: Path, annotaties: list):
    items = "".join(
        f'<li><a href="annotaties/{a["id"].replace("/","-")}.html">{a["wet"]} art. {a["artikel"]}'
        f'{", lid " + a["lid"] if a.get("lid") else ""}</a>'
        f' <span class="badge badge-blue">{a.get("bwb_id","")}</span></li>\n'
        for a in annotaties
    )
    body = f"""
<h1>Annotaties ({len(annotaties)})</h1>
<ul class="results">
{items}
</ul>
"""
    schrijf_html(out, "annotaties.html", "Annotaties — Belastingdienst", body)

    for a in annotaties:
        rijen = ""
        for r in a["rijen"]:
            bgp = ""
            if r.get("begrip_id"):
                slug = slugify(r["begrip_id"].rsplit("/", 1)[-1])
                bgp = f'<a href="../begrippen/{slug}.html">{r["begrip_id"]}</a>'
            sign = ""
            if r.get("signalering"):
                sign = f'<div style="font-size:0.8rem;color:#e65100;margin-top:0.25rem;">⚠ {r["signalering"]}</div>'
            rijen += f"""
<div class="annotatie-rij">
  <div class="rij-markering"><strong>"{r["markering"]}"</strong>{sign}</div>
  <div class="rij-klasse">{jas_tag(r["jas_klasse"])}</div>
  <div class="rij-begrip">{bgp}</div>
</div>"""
        lid = f', lid {a["lid"]}' if a.get("lid") else ""
        body = f"""
<h1>{a["wet"]} art. {a["artikel"]}{lid}</h1>
<p style="color:#666;font-size:0.9rem;">{a["structuurpositie"]} &bull; {a["bwb_id"]}</p>
<div class="wetstekst">"{a["wetstekst"]}"</div>
<div class="card">
  <h2>Annotatierijen</h2>
  {rijen}
</div>
"""
        schrijf_html(out, f'annotaties/{a["id"].replace("/","-")}.html', f'Annotatie art. {a["artikel"]} — Belastingdienst', body)


def generate_regels_pagina(out: Path, regels: list):
    items = "".join(
        f'<li><a href="regels/{r["id"]}.html">{r["naam"]}</a>'
        f' <span class="badge badge-green">{r["soort"]}</span></li>\n'
        for r in regels
    )
    body = f"""
<h1>Afleidingsregels ({len(regels)})</h1>
<ul class="results">
{items}
</ul>
"""
    schrijf_html(out, "regels.html", "Regels — Belastingdienst", body)

    for r in regels:
        voorbeelden = ""
        for v in r.get("voorbeeldreeksen") or []:
            cls = "voorbeeld" + ("" if v.get("juridisch-juist") else " fout")
            juist = "✅" if v.get("juridisch-juist") else "❌"
            voorbeelden += f'<div class="{cls}">{juist} <strong>Invoer:</strong> {v.get("invoerwaarden","")}<br><strong>Uitvoer:</strong> {v.get("verwachte-uitkomst","")}</div>\n'
        ops = ", ".join(r.get("operators") or [])
        body = f"""
<h1>{r["naam"]}</h1>
<p><span class="badge badge-green">{r["soort"]}</span> ID: {r["id"]}</p>
<div class="card">
  <h2>Formele regel</h2>
  <div class="wetstekst">{r["formele_regel"]}</div>
</div>
<div class="card">
  <h2>Toelichting</h2>
  <p>{r["toelichting"] or "<em>Geen toelichting</em>"}</p>
</div>
<div class="card">
  <h2>Details</h2>
  <table style="width:100%;border-collapse:collapse;">
    <tr><td style="padding:0.25rem 0;color:#666;">Invoer</td><td>{", ".join(r["invoer"]) or "-"}</td></tr>
    <tr><td style="padding:0.25rem 0;color:#666;">Uitvoer</td><td>{", ".join(r["uitvoer"]) or "-"}</td></tr>
    <tr><td style="padding:0.25rem 0;color:#666;">Operators</td><td>{ops or "-"}</td></tr>
    <tr><td style="padding:0.25rem 0;color:#666;">Tussenresultaat</td><td>{"Ja" if r["tussenresultaat"] else "Nee"}</td></tr>
  </table>
</div>
<div class="card">
  <h2>Voorbeeldreeksen</n>
  {voorbeelden or "<p>Geen voorbeelden</p>"}
</div>
"""
        schrijf_html(out, f'regels/{r["id"]}.html', f'{r["naam"]} — Belastingdienst', body)


def generate_search(out: Path, begrippen: list, annotaties: list, regels: list):
    data_begrip = [{"titel": b["naam"], "url": f'begrippen/{b["slug"]}.html', "type": "Begrip", "tekst": (b.get("definitie") or "") + " " + b["naam"]} for b in begrippen]
    data_annot = [{"titel": f'{a["wet"]} art. {a["artikel"]}', "url": f'annotaties/{a["id"].replace("/","-")}.html', "type": "Annotatie", "tekst": a.get("wetstekst","")} for a in annotaties]
    data_regel = [{"titel": r["naam"], "url": f'regels/{r["id"]}.html', "type": "Regel", "tekst": r.get("formele_regel","") + " " + r.get("toelichting","")} for r in regels]
    alles = data_begrip + data_annot + data_regel
    body = f"""
<h1>Zoeken</h1>
<input type="text" class="search-box" id="searchInput" placeholder="Zoek in begrippen, annotaties en regels..." autofocus>
<ul class="results" id="searchResults"></ul>
<script>
var data = {json.dumps(alles, ensure_ascii=False)};
var input = document.getElementById('searchInput');
var results = document.getElementById('searchResults');
input.addEventListener('input', function() {{
    var q = this.value.toLowerCase();
    results.innerHTML = '';
    if (q.length < 2) return;
    var hits = data.filter(function(d) {{
        return d.titel.toLowerCase().indexOf(q) > -1 || d.tekst.toLowerCase().indexOf(q) > -1;
    }});
    if (hits.length === 0) {{
        results.innerHTML = '<li style="color:#666;cursor:default;">Geen resultaten</li>';
        return;
    }}
    hits.slice(0, 50).forEach(function(d) {{
        var li = document.createElement('li');
        li.innerHTML = '<span class=\"badge badge-blue\">' + d.type + '</span> <a href=\"' + d.url + '\">' + d.titel + '</a>';
        results.appendChild(li);
    }});
}});
</script>
"""
    schrijf_html(out, "search.html", "Zoeken — Belastingdienst", body)


def generate_graph(out: Path, begrippen: list, regels: list):
    nodes = []
    node_ids = set()
    links = []
    for b in begrippen:
        nid = b["id"]
        if nid not in node_ids:
            nodes.append({"id": nid, "label": b["naam"], "groep": b["jas_klasse"]})
            node_ids.add(nid)
        for rtype in ("is-een", "heeft", "leidt-tot"):
            for target in b["relaties"][rtype]:
                if target not in node_ids:
                    nodes.append({"id": target, "label": target.rsplit("/", 1)[-1], "groep": "onbekend"})
                    node_ids.add(target)
                links.append({"source": nid, "target": target, "relatie": rtype})
    for r in regels:
        nid = r["id"]
        if nid not in node_ids:
            nodes.append({"id": nid, "label": r["naam"], "groep": "afleidingsregel"})
            node_ids.add(nid)
        for inv in r.get("invoer") or []:
            if inv not in node_ids:
                nodes.append({"id": inv, "label": inv.rsplit("/", 1)[-1], "groep": "onbekend"})
                node_ids.add(inv)
            links.append({"source": nid, "target": inv, "relatie": "invoer"})
    graf_data = json.dumps({"nodes": nodes, "links": links}, ensure_ascii=False)
    body = f"""
<h1>Kennisgraaf</h1>
<p>Interactieve force-directed graph van begrippen (blauw) en regels (oranje). Sleep nodes om de graaf te herschikken.</p>
<div class="card">
<div id="graph" style="width:100%;height:600px;border:1px solid #ddd;border-radius:4px;overflow:hidden;"></div>
</div>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
var width = document.getElementById('graph').clientWidth;
var height = 600;
var svg = d3.select("#graph").append("svg").attr("width", width).attr("height", height);
var data = {graf_data};
var color = d3.scaleOrdinal()
    .domain({json.dumps(list(JAS_KLEUREN.keys()), ensure_ascii=False)})
    .range({json.dumps(list(JAS_KLEUREN.values()), ensure_ascii=False)});
var simulation = d3.forceSimulation(data.nodes)
    .force("link", d3.forceLink(data.links).id(function(d) {{ return d.id; }}).distance(120))
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2));
var link = svg.append("g").selectAll("line")
    .data(data.links).join("line")
    .attr("stroke", "#ccc").attr("stroke-width", 1.5).attr("stroke-opacity", 0.6);
var node = svg.append("g").selectAll("circle")
    .data(data.nodes).join("circle")
    .attr("r", 8).attr("fill", function(d) {{ return color(d.groep) || "#999"; }})
    .attr("stroke", "#fff").attr("stroke-width", 1.5)
    .call(d3.drag().on("start", function(event,d) {{ if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }})
        .on("drag", function(event,d) {{ d.fx = event.x; d.fy = event.y; }})
        .on("end", function(event,d) {{ if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }}));
var label = svg.append("g").selectAll("text")
    .data(data.nodes).join("text")
    .attr("dx", 12).attr("dy", 4).attr("font-size", "11px").attr("fill", "#333")
    .text(function(d) {{ return d.label; }});
simulation.on("tick", function() {{
    link.attr("x1", function(d) {{ return d.source.x; }}).attr("y1", function(d) {{ return d.source.y; }})
        .attr("x2", function(d) {{ return d.target.x; }}).attr("y2", function(d) {{ return d.target.y; }});
    node.attr("cx", function(d) {{ return d.x; }}).attr("cy", function(d) {{ return d.y; }});
    label.attr("x", function(d) {{ return d.x; }}).attr("y", function(d) {{ return d.y; }});
}});
</script>
"""
    schrijf_html(out, "graph.html", "Kennisgraaf — Belastingdienst", body)


def main():
    parser = argparse.ArgumentParser(description="Genereer statische webapp uit vault")
    parser.add_argument("--vault-root", default=".", help="Pad naar vault-root")
    parser.add_argument("--out", default="webapp", help="Output directory voor webapp")
    args = parser.parse_args()

    vault = Path(args.vault_root)
    out = Path(args.out)

    # Clean output
    if out.exists():
        shutil.rmtree(out)

    print("Data laden...", file=sys.stderr)
    begrippen = laad_begrippen(vault)
    annotaties = laad_annotaties(vault)
    regels = laad_regels(vault)
    print(f"  {len(begrippen)} begrippen, {len(annotaties)} annotaties, {len(regels)} regels", file=sys.stderr)

    print("Pagina's genereren...", file=sys.stderr)
    generate_index(out, begrippen, annotaties, regels)
    generate_begrippen_pagina(out, begrippen)
    generate_annotaties_pagina(out, annotaties)
    generate_regels_pagina(out, regels)
    generate_search(out, begrippen, annotaties, regels)
    generate_graph(out, begrippen, regels)

    print(f"Webapp gegenereerd in {out}/", file=sys.stderr)


if __name__ == "__main__":
    main()
