from pathlib import Path

from sitegen.html import breadcrumb, format_ann_title, schrijf_html


def gen_regels(out: Path, regels: list, begrippen: list, annotaties: list):
    slug_by_bid = {b["id"]: b["slug"] for b in begrippen}

    def _link(ref: str) -> str:
        slug = slug_by_bid.get(ref)
        return f'<a href="../begrippen/{slug}.html">{ref}</a>' if slug else ref

    ann_by_key: dict[tuple[str, str, str], dict] = {}
    for a in annotaties:
        ann_by_key[(a["bwb_id"], a["artikel"], a.get("lid", ""))] = a

    items = "".join(
        f'<li data-id="{r["id"]}" onclick="window.location=\'regels/{r["id"]}.html\'">'
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
<script src="https://cdn.jsdelivr.net/npm/minisearch@7/dist/umd/index.min.js"></script>
<script>
var _dr=false;
var _ms=new MiniSearch({{fields:['titel','formele_regel','toelichting'],storeFields:['titel'],searchOptions:{{prefix:true,fuzzy:0.2}}}});
fetch('data/regels.json').then(function(r){{return r.json()}}).then(function(d){{_ms.addAll(d);_dr=true}});
document.getElementById('filterInput')?.addEventListener('input',function(){{
  var q=this.value.trim();
  if(!q||!_dr){{document.querySelectorAll('#itemList li').forEach(function(l){{l.style.display=''}});return}}
  var s=new Set(_ms.search(q).map(function(r){{return r.id}}));
  document.querySelectorAll('#itemList li').forEach(function(l){{l.style.display=s.has(l.getAttribute('data-id'))?'':'none'}});
}});
</script>"""
    schrijf_html(out, "regels.html", "Regels | Belastingdienst", body, active="regels")

    for r in regels:
        vb = ""
        for v in r.get("voorbeeldreeksen") or []:
            juist = v.get("juridisch-juist", True)
            cls = "voorbeeld" if juist else "voorbeeld ongeldig"
            label = "[+]" if juist else "[-]"
            toel_v = v.get("toelichting") or ""
            toel_html = f'<div style="font-size:0.8rem;color:var(--text-muted);margin-top:0.3rem">{toel_v}</div>' if toel_v else ""
            vb += f'<div class="{cls}"><span class="voorbeeld-label">{label}</span> <strong>Invoer:</strong> {v.get("invoerwaarden","")}<br><strong>Uitvoer:</strong> {v.get("verwachte-uitkomst","")}{toel_html}</div>'
        ops = ", ".join(r.get("operators") or [])
        ann_link = ""
        if r["bwb_id"] and r["artikel"]:
            match = ann_by_key.get((r["bwb_id"], r["artikel"], r["lid"]))
            if match:
                ann_url = f'../annotaties/{match["id"].replace("/","-")}.html'
                ann_title = format_ann_title(match)
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
      <tr><td>Peildatum</td><td>{r.get("peildatum") or "-"}</td></tr>
      <tr><td>Rechtsfeit</td><td>{_link(r["rechtsfeit_id"]) if r.get("rechtsfeit_id") else "-"}</td></tr>
      {f'<tr><td>Vervangt</td><td><a href="{r["vervangt_regel_id"]}.html">{r["vervangt_regel_id"]}</a></td></tr>' if r.get("vervangt_regel_id") else ""}
    </table>
  </div>
</div>
<div class="card">
<div class="card-title">Voorbeeldreeksen</div>
{vb or "<p class=item-meta>Geen voorbeelden</p>"}
</div>"""
        schrijf_html(out, f'regels/{r["id"]}.html', f'{r["naam"]} | Belastingdienst', body, active="regels", p="../")
