from html import escape
from pathlib import Path

from sitegen.html import breadcrumb, format_ann_title, schrijf_html


def _render_regel_waarschuwingen(index: dict, regel_id: str, meta: list | None = None) -> str:
    from sitegen.data import zoek_meta
    ws = [w for pad, ws in index.items() if regel_id in pad for w in ws]
    if not ws:
        return ""
    meta_lijst = meta or []
    items = ""
    for w in ws:
        kort = escape(w.removeprefix("[L3] ").removeprefix("[L2] ").removeprefix("[L1] "))
        m = zoek_meta(w, meta_lijst)
        oplossing = ""
        if m:
            stappen_html = "".join(f"<li>{escape(s)}</li>" for s in (m.get("stappen") or []))
            commando = escape(m.get("commando", "") or "")
            commando_html = f'<p class="oplossing-commando">Skill: <code>{commando}</code></p>' if commando else ""
            oplossing = (
                f'<div class="oplossing-blok">'
                f'<div class="oplossing-titel">{escape(m.get("titel", ""))}</div>'
                f'<p class="oplossing-uitleg">{escape(m.get("uitleg", "").strip())}</p>'
                f'<ol class="oplossing-stappen">{stappen_html}</ol>'
                f'{commando_html}'
                f'</div>'
            )
        items += f'<li class="waarschuwing-item"><span class="waarschuwing-melding">{kort}</span>{oplossing}</li>'
    return f'<div class="card card-waarschuwing"><div class="card-title">Kwaliteitspunten ({len(ws)})</div><ul class="waarschuwing-list">{items}</ul></div>'


def _render_vr_matrix(vr: dict, slug_by_bid: dict) -> str:
    """Render één voorbeeldreeks als HTML-matrix (getransponeerd: rijen = begrippen, kolommen = testgevallen)."""
    kolommen = vr.get("kolommen") or []
    if not kolommen:
        return ""

    invoer_begrippen: list[str] = []
    uitvoer_begrippen: list[str] = []
    seen_i: set[str] = set()
    seen_u: set[str] = set()
    for k in kolommen:
        for bid in (k.get("invoer") or {}).keys():
            if bid not in seen_i:
                invoer_begrippen.append(bid)
                seen_i.add(bid)
        for bid in (k.get("verwachte_uitvoer") or {}).keys():
            if bid not in seen_u:
                uitvoer_begrippen.append(bid)
                seen_u.add(bid)

    n = len(kolommen)
    colspan = n + 1

    def _blink(bid: str) -> str:
        slug = slug_by_bid.get(bid)
        naam = bid.split("/")[-1]
        return f'<a href="../../begrippen/{slug}.html">{escape(naam)}</a>' if slug else escape(naam)

    def _val_cel(val) -> str:
        if val is None:
            return '<td class="vr-nvt"><em>null</em></td>'
        s = str(val)
        return f"<td>{escape(s)}</td>"

    def _bool_cel(val: str, prefix: str = "") -> str:
        cls_map = {"ja": "vr-ja", "nee": "vr-nee", "nvt": "vr-nvt", "?": "vr-vraag"}
        cls = cls_map.get(val, "")
        cel = f'<td class="{cls}">{escape(val)}</td>' if cls else f"<td>{escape(val)}</td>"
        return cel

    header_cellen = "".join(f"<th>{escape(k['label'])}</th>" for k in kolommen)
    rows = f'<tr><th></th>{header_cellen}</tr>'

    if invoer_begrippen:
        rows += f'<tr class="vr-sectie"><td colspan="{colspan}">Invoer</td></tr>'
        for bid in invoer_begrippen:
            cellen = "".join(_val_cel(k.get("invoer", {}).get(bid)) for k in kolommen)
            rows += f"<tr><td>{_blink(bid)}</td>{cellen}</tr>"

    if uitvoer_begrippen:
        rows += f'<tr class="vr-sectie"><td colspan="{colspan}">Uitvoer</td></tr>'
        for bid in uitvoer_begrippen:
            cellen = "".join(_val_cel(k.get("verwachte_uitvoer", {}).get(bid)) for k in kolommen)
            rows += f"<tr><td>{_blink(bid)}</td>{cellen}</tr>"

    rows += '<tr class="vr-meta-row">'
    rows += "<td>Invoer juist?</td>"
    rows += "".join(_bool_cel(k.get("is_invoer_juist", "")) for k in kolommen)
    rows += "</tr>"

    rows += '<tr class="vr-meta-row">'
    rows += "<td>Voorspelling juist?</td>"
    rows += "".join(_bool_cel(k.get("is_voorspelling_juist", "?")) for k in kolommen)
    rows += "</tr>"

    toelichtingen = [(i, k["toelichting"]) for i, k in enumerate(kolommen) if k.get("toelichting")]
    toel_html = ""
    if toelichtingen:
        items = "".join(
            f'<li><strong>{escape(kolommen[i]["label"])}:</strong> {escape(t)}</li>'
            for i, t in toelichtingen
        )
        toel_html = f'<ul class="vr-toelichting">{items}</ul>'

    status_cls = {"concept": "badge-status", "gereviseerd": "badge-definitief", "gevalideerd": "badge-definitief"}.get(
        vr.get("status", "concept"), "badge-status"
    )
    header = (
        f'<div class="vr-header">'
        f'<span class="vr-naam">{escape(vr.get("naam", ""))}</span> '
        f'<span class="badge {status_cls}">{escape(vr.get("status", "concept"))}</span>'
        f'</div>'
    )

    return (
        f'{header}'
        f'<div class="table-responsive">'
        f'<table class="vr-matrix"><tbody>{rows}</tbody></table>'
        f'</div>'
        f'{toel_html}'
    )


def gen_regels(out: Path, regels: list, begrippen: list, annotaties: list, waarschuwingen: dict | None = None, meta: list | None = None, voorbeeldreeksen: list | None = None):
    slug_by_bid = {b["id"]: b["slug"] for b in begrippen}
    vr_by_ar: dict[str, list[dict]] = {}
    for vr in (voorbeeldreeksen or []):
        ar_id = vr.get("afleidingsregel_id", "")
        if ar_id:
            vr_by_ar.setdefault(ar_id, []).append(vr)

    def _link(ref: str) -> str:
        slug = slug_by_bid.get(ref)
        return f'<a href="../begrippen/{slug}.html">{escape(ref)}</a>' if slug else escape(ref)

    ws_index = waarschuwingen or {}
    meta_lijst = meta or []
    ann_by_key: dict[tuple[str, str, str], dict] = {}
    for a in annotaties:
        ann_by_key[(a["bwb_id"], a["artikel"], a.get("lid", ""))] = a

    items = "".join(
        f'<li data-id="{r["id"]}" onclick="window.location=\'regels/{r["id"]}.html\'">'
        f'<a href="regels/{r["id"]}.html" class="item-title">{escape(r["naam"])}</a>'
        f'<div class="item-badges"><span class="badge badge-definitief">{escape(r["soort"])}</span></div>'
        f'<span class="item-meta">ID: {escape(r["id"])} &nbsp; Geldig vanaf: {escape(r.get("geldigheid_van") or "-")}</span>'
        f'</li>\n'
        for r in regels
    )
    body = f"""<h1>Afleidingsregels ({len(regels)})</h1>
<label for="filterInput" class="sr-only">Filter op naam of ID</label>
<input type="text" class="search-input" id="filterInput" placeholder="Filter op naam of ID..." autofocus>
<div class="item-list" id="itemList">{items}</div>
<script src="https://cdn.jsdelivr.net/npm/minisearch@7/dist/umd/index.min.js" integrity="sha384-9Eacb80ywplqCp0P/bR61+zYn5Pg2LmQ7T8rppdoKHcQMmXbRh1wHwRC8avUJvnz" crossorigin="anonymous"></script>
<script>
var _dr=false;
var _inp=document.getElementById('filterInput');
var _ms=new MiniSearch({{fields:['titel','formele_regel','toelichting'],storeFields:['titel'],searchOptions:{{prefix:true,fuzzy:0.2}}}});
if(_inp)_inp.placeholder='Zoekindex laden...';
fetch('data/regels.json').then(function(r){{return r.json()}}).then(function(d){{_ms.addAll(d);_dr=true;if(_inp)_inp.placeholder='Filter op naam of ID...'}});
_inp?.addEventListener('input',function(){{
  var q=this.value.trim();
  if(!q||!_dr){{document.querySelectorAll('#itemList li').forEach(function(l){{l.style.display=''}});return}}
  var s=new Set(_ms.search(q).map(function(r){{return r.id}}));
  document.querySelectorAll('#itemList li').forEach(function(l){{l.style.display=s.has(l.getAttribute('data-id'))?'':'none'}});
}});
</script>"""
    schrijf_html(out, "regels.html", "Regels | Belastingdienst", body, active="regels")

    for r in regels:
        vr_matrices = ""
        for vr in vr_by_ar.get(r["id"], []):
            vr_matrices += _render_vr_matrix(vr, slug_by_bid)
        vb_inline = ""
        for v in r.get("voorbeeldreeksen") or []:
            juist = v.get("juridisch-juist", True)
            cls = "voorbeeld" if juist else "voorbeeld ongeldig"
            label = "[+]" if juist else "[-]"
            toel_v = escape(v.get("toelichting") or "")
            toel_html = f'<div style="font-size:0.8rem;color:var(--text-muted);margin-top:0.3rem">{toel_v}</div>' if toel_v else ""
            vb_inline += f'<div class="{cls}"><span class="voorbeeld-label">{label}</span> <strong>Invoer:</strong> {escape(str(v.get("invoerwaarden","")))} <strong>Uitvoer:</strong> {escape(str(v.get("verwachte-uitkomst","")))}{toel_html}</div>'
        vb = vr_matrices or vb_inline
        ops = escape(", ".join(r.get("operators") or []))
        ann_link = ""
        if r["bwb_id"] and r["artikel"]:
            match = ann_by_key.get((r["bwb_id"], r["artikel"], r["lid"]))
            if match:
                ann_url = f'../annotaties/{match["id"].replace("/","-")}.html'
                ann_title = format_ann_title(match)
                ann_link = f'<div class="card"><div class="card-title">Annotatie</div><p><a href="{ann_url}">{ann_title}</a></p></div>'
        r_br = breadcrumb("../", r["naam"], [("../index.html", "Home"), ("../regels.html", "Regels")])
        body = f"""{r_br}
<h1>{escape(r["naam"])}</h1>
<p class="subtitle"><span class="badge badge-definitief">{escape(r["soort"])}</span> {escape(r["id"])}</p>
<div class="card">
  <div class="card-title">Formele regel</div>
  <div class="regel-box">{escape(r["formele_regel"])}</div>
</div>
<div class="card">
  <div class="card-title">Toelichting</div>
  <p>{escape(r["toelichting"]) if r["toelichting"] else "<em>Geen toelichting</em>"}</p>
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
      <tr><td>Geldig vanaf</td><td>{r.get("geldigheid_van") or "&#8212;"}</td></tr>
      {f'<tr><td>Geldig tot</td><td>{r["geldigheid_tot"]}</td></tr>' if r.get("geldigheid_tot") else ""}
      {f'<tr><td>Prioriteit</td><td>{r["prioriteit"]}</td></tr>' if r.get("prioriteit") is not None else ""}
      <tr><td>Rechtsfeit</td><td>{_link(r["rechtsfeit_id"]) if r.get("rechtsfeit_id") else "-"}</td></tr>
      {f'<tr><td>Vervangt</td><td><a href="{r["vervangt_regel_id"]}.html">{r["vervangt_regel_id"]}</a></td></tr>' if r.get("vervangt_regel_id") else ""}
      {f'<tr><td>Gespecialiseert</td><td><a href="{r["gespecialiseerd_regel_id"]}.html">{r["gespecialiseerd_regel_id"]}</a></td></tr>' if r.get("gespecialiseerd_regel_id") else ""}
      {f'<tr><td>Annotatie-id</td><td>{escape(r["annotatie_id"])}</td></tr>' if r.get("annotatie_id") else ""}
    </table>
  </div>
</div>
<div class="card">
<div class="card-title">Voorbeeldreeksen</div>
{vb or "<p class=item-meta>Geen voorbeelden</p>"}
</div>
{_render_regel_waarschuwingen(ws_index, r["id"], meta_lijst)}"""
        schrijf_html(out, f'regels/{r["id"]}.html', f'{r["naam"]} | Belastingdienst', body, active="regels", p="../")
