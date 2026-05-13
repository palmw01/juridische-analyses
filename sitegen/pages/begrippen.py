from pathlib import Path

from sitegen.config import slugify
from sitegen.html import (
    breadcrumb,
    format_ann_title,
    jas_tag,
    schrijf_html,
    status_badge,
)


def _render_begrip_voorbeelden(voorbeelden: list) -> str:
    if not voorbeelden:
        return ""
    rows = ""
    for v in voorbeelden:
        label = "✓" if v.get("waar") else "✗"
        cls = "voorbeeld" if v.get("waar") else "voorbeeld ongeldig"
        toel = v.get("toelichting") or ""
        stelling = v.get("stelling", "")
        rows += f'<div class="{cls}"><span class="voorbeeld-label">{label}</span> {stelling}'
        if toel:
            rows += f'<div style="font-size:0.8rem;color:var(--text-muted);margin-top:0.2rem">{toel}</div>'
        rows += "</div>\n"
    return f'<div class="card"><div class="card-title">Voorbeelden</div>{rows}</div>'


def _render_begrip_kenmerken(kenmerken: list) -> str:
    if not kenmerken:
        return ""
    items = "".join(f"<li>{k}</li>" for k in kenmerken)
    return f'<div class="card"><div class="card-title">Kenmerken</div><ul style="margin-left:1.25rem">{items}</ul></div>'


def gen_begrippen(out: Path, begrippen: list, annotaties: list):
    slug_by_bid: dict[str, str] = {b["id"]: b["slug"] for b in begrippen}
    ann_by_begrip: dict[str, list[dict]] = {}
    for a in annotaties:
        ann_title = format_ann_title(a)
        ann_url = f'annotaties/{a["id"].replace("/","-")}.html'
        for r in a["rijen"]:
            bid = r.get("begrip_id")
            if bid:
                ann_by_begrip.setdefault(bid, []).append({"titel": ann_title, "url": ann_url})
    items = "".join(
        f'<li data-id="{b["slug"]}" onclick="window.location=\'begrippen/{b["slug"]}.html\'">'
        f'<a href="begrippen/{b["slug"]}.html" class="item-title">{b["naam"]}</a>'
        f'<div class="item-badges">{jas_tag(b["jas_klasse"])}<span class="badge badge-soort">{b["soort"]}</span>{status_badge(b["status"])}</div>'
        f'<span class="item-meta">ID: {b["id"]}</span>'
        f'</li>\n'
        for b in begrippen
    )
    body = f"""<h1>Begrippen ({len(begrippen)})</h1>
<label for="filterInput" class="sr-only">Filter op naam</label>
<input type="text" class="search-input" id="filterInput" placeholder="Filter op naam of definitie..." autofocus>
<div class="item-list" id="itemList">{items}</div>
<script src="https://cdn.jsdelivr.net/npm/minisearch@7/dist/umd/index.min.js"></script>
<script>
var _dr=false;
var _ms=new MiniSearch({{fields:['titel','definitie'],storeFields:['titel'],searchOptions:{{prefix:true,fuzzy:0.2}}}});
fetch('data/begrippen.json').then(function(r){{return r.json()}}).then(function(d){{_ms.addAll(d);_dr=true}});
document.getElementById('filterInput')?.addEventListener('input',function(){{
  var q=this.value.trim();
  if(!q||!_dr){{document.querySelectorAll('#itemList li').forEach(function(l){{l.style.display=''}});return}}
  var s=new Set(_ms.search(q).map(function(r){{return r.id}}));
  document.querySelectorAll('#itemList li').forEach(function(l){{l.style.display=s.has(l.getAttribute('data-id'))?'':'none'}});
}});
</script>"""
    schrijf_html(out, "begrippen.html", "Begrippen | Belastingdienst", body, active="begrippen")

    ann_titel_by_id: dict[str, str] = {
        a["id"]: format_ann_title(a)
        for a in annotaties
    }

    pp = "../"
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

        def ann_url(bron_annotatie_id: str) -> str:
            return f'../annotaties/{bron_annotatie_id.replace("/", "-")}.html'

        def ann_label(bron_annotatie_id: str) -> str:
            return ann_titel_by_id.get(bron_annotatie_id, bron_annotatie_id)

        def_bron = ""
        if b.get("definitie"):
            bronnen = b.get("markeringen", [])
            if bronnen:
                links = []
                for m in bronnen:
                    if m.get("bijdrage") == "primair":
                        mid = m.get("markering-id", "")
                        baid = m.get("bron-annotatie-id", "")
                        if baid:
                            links.append(f'<a href="{ann_url(baid)}">{mid} ({ann_label(baid)})</a>')
                        else:
                            links.append(mid)
                def_bron = f'<div style="font-size:0.8rem;color:var(--text-muted);margin-top:0.25rem">Kern gebaseerd op: {", ".join(links)}</div>'

        mid_to_bron = {
            m.get("markering-id", ""): m.get("bron-annotatie-id", "")
            for m in b.get("markeringen", [])
        }
        ctx_html = ""
        for ctx in b.get("definitie_contexten", []):
            bijdrage = ctx.get("bijdrage", "")
            ctx_tekst = ctx.get("tekst", "")
            ctx_toel = ctx.get("toelichting", "")
            mid = ctx.get("markering-id", "")
            bron = mid_to_bron.get(mid, "")
            badge_label = bijdrage.capitalize()
            ref_parts = []
            if mid:
                ref_parts.append(mid)
            if bron:
                ref_parts.append(f'<a href="{ann_url(bron)}">{ann_label(bron)}</a>')
            ref_str = " · ".join(ref_parts)
            toel_html = f'<div class="def-context-toelichting">{ctx_toel}</div>' if ctx_toel else ""
            ctx_html += (
                f'<div class="def-context def-context-{bijdrage}">'
                f'<div class="def-context-header">'
                f'<span class="ctx-badge ctx-badge-{bijdrage}">{badge_label}</span>'
                f'<span class="ctx-ref">{ref_str}</span>'
                f'</div>'
                f'<div>{ctx_tekst}</div>'
                f'{toel_html}'
                f'</div>\n'
            )
        ctx_block = f'<div class="def-contexten">{ctx_html}</div>' if ctx_html else ""

        mark_tbl = ""
        for m in b.get("markeringen", []):
            jc = b["jas_klasse"] or ""
            mid = m.get("markering-id", "")
            baid = m.get("bron-annotatie-id", "")
            mid_cell = f'<a href="{ann_url(baid)}">{mid} ({ann_label(baid)})</a>' if baid else mid
            bev = m.get("bevestigd", False)
            bev_op = m.get("bevestigd-op") or ""
            bev_label = f'<span title="Gevalideerd{" op " + bev_op if bev_op else ""}" style="color:var(--success,#2e7d32)">&#10003;</span>' if bev else '<span title="AI-output, nog niet gevalideerd" style="color:var(--warning,#e65100)">&#9888;</span>'
            mark_tbl += f'<tr><td>{mid_cell}</td><td class="mark-text">"{m.get("tekst","")}"</td><td>{jas_tag(jc) if jc else ""}</td><td>{m.get("interpretatiemethode","")}</td><td><span class="badge badge-soort">{m.get("bijdrage","")}</span></td><td style="text-align:center">{bev_label}</td></tr>\n'
        mp = ""
        if mark_tbl:
            mp = f"""<div class="card">
  <div class="card-title">Markeringen</div>
  <div class="table-scroll">
  <table class="ann-table">
    <tr><th>ID</th><th>Tekst</th><th>JAS-klasse</th><th>Interpretatie</th><th>Bijdrage</th><th style="text-align:center">Bevestigd</th></tr>
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
    <div class="def-kern-label">Kern</div>
    <div class="def-block">{b["definitie"] or "<em>Geen definitie</em>"}</div>
    {def_bron}
    {ctx_block}
  </div>
  {mp}
</div>
<div>
  <div class="card">
    <div class="card-title">Kenmerken</div>
    <table class="prop-table">
      <tr><td>ID</td><td style="word-break:break-all;font-size:0.8rem">{b["id"]}</td></tr>
      <tr><td>Soort</td><td>{b["soort"] or "-"}{"&nbsp;<span class='badge badge-soort'>sleutel-id</span>" if b.get("soort_id") else ""}</td></tr>
      <tr><td>Herkomst</td><td>{b["herkomst"] or "-"}</td></tr>
      <tr><td>Aliases</td><td>{", ".join(b["aliases"]) or "-"}</td></tr>
      <tr><td>Identificatiebegrip</td><td>{"Ja" if b.get("identificatiebegrip") else "Nee"}</td></tr>
      <tr><td>Tussenresultaat</td><td>{"Ja" if b["tussenresultaat"] else "Nee"}</td></tr>
      <tr><td>Definitie versie</td><td>{b["definitie_versie"] if b.get("definitie_versie") else "-"}</td></tr>
      <tr><td>Geldig vanaf</td><td>{b["geldigheid_van"] or "-"}</td></tr>
      <tr><td>Geldig tot</td><td>{b["geldigheid_tot"] or "&#8212;"}</td></tr>
      {f'<tr><td>Vervangen door</td><td><a href="{pp}begrippen/{slugify(b["vervangen_door"].rsplit("/",1)[-1])}.html">{b["vervangen_door"]}</a></td></tr>' if b.get("vervangen_door") else ""}
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
</div>
{_render_begrip_voorbeelden(b["voorbeelden"])}
{_render_begrip_kenmerken(b["kenmerken"])}"""
        schrijf_html(out, f'begrippen/{b["slug"]}.html', f'{b["naam"]} | Belastingdienst', body, active="begrippen", p="../")
