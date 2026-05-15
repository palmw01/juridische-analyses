from pathlib import Path

from sitegen.html import jas_tag, schrijf_html


def gen_index(out: Path, begrippen: list, annotaties: list, regels: list, waarschuwingen: dict | None = None):
    n_beg = len(begrippen)
    n_ann = len(annotaties)
    n_reg = len(regels)
    n_klassen = len({b["jas_klasse"] for b in begrippen})
    n_ws = sum(len(ws) for ws in (waarschuwingen or {}).values())
    n_def = sum(1 for b in begrippen if b.get("definitie"))
    n_concept = sum(1 for b in begrippen if b["status"] == "concept")
    n_definitief = sum(1 for b in begrippen if b["status"] == "definitief")
    by_klasse: dict[str, int] = {}
    for b in begrippen:
        k = b["jas_klasse"]
        by_klasse[k] = by_klasse.get(k, 0) + 1
    klasse_rows = "".join(f'<tr><td>{jas_tag(k)}</td><td style="text-align:right">{c}</td></tr>' for k, c in sorted(by_klasse.items(), key=lambda x: -x[1]))
    body = f"""<h1>Rechtsgraaf</h1>
<p class="subtitle">Artikel 9 Invorderingswet 1990 — Gestructureerde wetsanalyse volgens JAS v1.0.10</p>
<div class="stat-grid">
  <div class="card stat-card"><div class="stat-nr">{n_beg}</div><div class="stat-label">Begrippen</div></div>
  <div class="card stat-card"><div class="stat-nr">{n_ann}</div><div class="stat-label">Annotaties</div></div>
  <div class="card stat-card"><div class="stat-nr">{n_reg}</div><div class="stat-label">Afleidingsregels</div></div>
  <div class="card stat-card"><div class="stat-nr">{n_klassen}</div><div class="stat-label">JAS-klassen</div></div>
  <div class="card stat-card"><div class="stat-nr">{n_ws}</div><div class="stat-label">Kwaliteitspunten</div></div>
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


def gen_404(out: Path):
    body = """<div class="error-page">
<h1>404</h1>
<p>Deze pagina bestaat niet.</p>
<a href="./" class="filter-chip active">Terug naar dashboard</a>
</div>"""
    schrijf_html(out, "404.html", "Pagina niet gevonden | Belastingdienst", body)
