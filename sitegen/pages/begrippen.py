from html import escape
from pathlib import Path

from sitegen.config import slugify
from sitegen.html import (
    breadcrumb,
    format_ann_title,
    jas_tag,
    schrijf_html,
    status_badge,
)


def _render_waarschuwingen(index: dict, sleutel: str, meta: list | None = None) -> str:
    from sitegen.data import zoek_meta
    ws = [w for pad, ws in index.items() if Path(pad).stem == sleutel for w in ws]
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


def _render_begrip_voorbeelden(voorbeelden: list) -> str:
    if not voorbeelden:
        return ""
    rows = ""
    for v in voorbeelden:
        label = "✓" if v.get("waar") else "✗"
        cls = "voorbeeld" if v.get("waar") else "voorbeeld ongeldig"
        toel = escape(v.get("toelichting") or "")
        stelling = escape(v.get("stelling") or "")
        rows += f'<div class="{cls}"><span class="voorbeeld-label">{label}</span> {stelling}'
        if toel:
            rows += f'<div style="font-size:0.8rem;color:var(--text-muted);margin-top:0.2rem">{toel}</div>'
        rows += "</div>\n"
    return f'<div class="card"><div class="card-title">Voorbeelden</div>{rows}</div>'


def _render_begrip_kenmerken(kenmerken: list) -> str:
    if not kenmerken:
        return ""
    items = "".join(f"<li>{escape(k)}</li>" for k in kenmerken)
    return f'<div class="card"><div class="card-title">Kenmerken</div><ul style="margin-left:1.25rem">{items}</ul></div>'


def gen_begrippen(out: Path, begrippen: list, annotaties: list, waarschuwingen: dict | None = None, meta: list | None = None):
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
        f'<li data-id="{b["slug"]}">'
        f'<a href="begrippen/{b["slug"]}.html" class="item-title">{escape(b["naam"])}</a>'
        f'<div class="item-badges">{jas_tag(b["jas_klasse"])}<span class="badge badge-soort">{escape(b["soort"])}</span>{status_badge(b["status"])}</div>'
        f'<span class="item-meta">ID: {escape(b["id"])}</span>'
        f'</li>\n'
        for b in begrippen
    )
    body = f"""<h1>Begrippen ({len(begrippen)})</h1>
<label for="filterInput" class="sr-only">Filter op naam of definitie</label>
<input type="search" class="search-input" id="filterInput" placeholder="Filter op naam of definitie..."
       data-list="#itemList" data-source="data/begrippen.json"
       data-fields="titel,definitie" data-status="#filterStatus" data-empty="#filterEmpty">
<span id="filterStatus" class="result-status" role="status" aria-live="polite"></span>
<div class="item-list" id="itemList">{items}</div>
<div id="filterEmpty" class="empty-state" role="status">
  <div class="empty-state-title">Geen resultaten</div>
  <div>Pas je zoekterm aan of leeg het filter.</div>
</div>
<script src="https://cdn.jsdelivr.net/npm/minisearch@7/dist/umd/index.min.js" integrity="sha384-9Eacb80ywplqCp0P/bR61+zYn5Pg2LmQ7T8rppdoKHcQMmXbRh1wHwRC8avUJvnz" crossorigin="anonymous"></script>
<script src="js/filter-list.js"></script>"""
    schrijf_html(out, "begrippen.html", "Begrippen | Belastingdienst", body, active="begrippen")

    ws_index = waarschuwingen or {}
    ann_titel_by_id: dict[str, str] = {
        a["id"]: format_ann_title(a)
        for a in annotaties
    }

    def ann_url(bron_annotatie_id: str) -> str:
        return f'../annotaties/{bron_annotatie_id.replace("/", "-")}.html'

    def ann_label(bron_annotatie_id: str) -> str:
        return ann_titel_by_id.get(bron_annotatie_id, bron_annotatie_id)

    pp = "../"
    for b in begrippen:
        rel_html = ""
        for rt, label in [("is-een", "Is een"), ("heeft", "Heeft"), ("leidt-tot", "Leidt tot")]:
            targets = b["relaties"][rt]
            if targets:
                rel_html += f"<p style='margin-top:0.5rem'><strong>{label}</strong></p><ul style='margin-left:1.25rem'>"
                for t in targets:
                    t_slug = slug_by_bid.get(t) or slugify(t.rsplit("/", 1)[-1])
                    rel_html += f'<li><a href="{pp}begrippen/{t_slug}.html">{escape(t)}</a></li>'
                rel_html += "</ul>"
        if not rel_html:
            rel_html = "<p class='item-meta'>Geen relaties</p>"

        def_bron = ""
        if b.get("definitie"):
            bronnen = b.get("markeringen", [])
            if bronnen:
                links = []
                for m in bronnen:
                    if m.get("bijdrage") == "primair":
                        mid = escape(m.get("markering-id", ""))
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
            ctx_tekst = escape(ctx.get("tekst", ""))
            ctx_toel = escape(ctx.get("toelichting", ""))
            mid = ctx.get("markering-id", "")
            bron = mid_to_bron.get(mid, "")
            badge_label = escape(bijdrage.capitalize())
            ref_parts = []
            if mid:
                ref_parts.append(escape(mid))
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
            jc = m.get("jas-klasse") or b["jas_klasse"] or ""
            mid = escape(m.get("markering-id", ""))
            baid = m.get("bron-annotatie-id", "")
            if baid:
                mid_cell = f'<a class="ann-id-badge" href="{ann_url(baid)}">{mid}</a><span class="ann-sub">{ann_label(baid)}</span>'
            else:
                mid_cell = f'<span class="ann-id-badge">{mid}</span>'
            bev = m.get("bevestigd", False)
            bev_op = escape(m.get("bevestigd-op") or "")
            bev_label = f'<span class="ann-bev-ok" title="Gevalideerd{" op " + bev_op if bev_op else ""}">&#10003;</span>' if bev else '<span class="ann-bev-todo" title="AI-output, nog niet gevalideerd">&#9888;</span>'
            mark_tbl += f'<tr><td>{mid_cell}</td><td class="mark-text">&#8220;{escape(m.get("tekst",""))}&#8221;</td><td>{jas_tag(jc) if jc else ""}</td><td class="ann-interpretatie">{escape(m.get("interpretatiemethode",""))}</td><td><span class="badge badge-soort">{escape(m.get("bijdrage",""))}</span></td><td class="ann-col-center">{bev_label}</td></tr>\n'
        mp = ""
        if mark_tbl:
            mp = f"""<div class="card">
  <div class="card-title">Markeringen</div>
  <div class="table-scroll">
  <table class="ann-table">
    <thead>
      <tr><th scope="col">ID</th><th scope="col">Tekst</th><th scope="col">JAS-klasse</th><th scope="col">Interpretatie</th><th scope="col">Bijdrage</th><th scope="col" class="ann-col-center">Bevestigd</th></tr>
    </thead>
    <tbody>
    {mark_tbl}
    </tbody>
  </table></div>
</div>"""
        reg_lnk = ""
        if b["afleidingsregel-id"]:
            reg_lnk = f'<p style="margin-top:0.5rem"><a href="{pp}regels/{b["afleidingsregel-id"]}.html">{b["afleidingsregel-id"]}</a></p>'
        uitvoer_lnk = ""
        if b["uitvoer-van-regel-id"]:
            uitvoer_lnk = f'<p style="margin-top:0.5rem"><a href="{pp}regels/{b["uitvoer-van-regel-id"]}.html">{b["uitvoer-van-regel-id"]}</a></p>'
        ann_links = ""
        ann_refs = ann_by_begrip.get(b["id"], [])
        if ann_refs:
            seen: set[str] = set()
            ann_items = ""
            for ref in ann_refs:
                if ref["url"] not in seen:
                    seen.add(ref["url"])
                    ann_items += f'<li><a href="../{ref["url"]}">{ref["titel"]}</a></li>\n'
            ann_links = f'<div class="card"><div class="card-title">Annotaties</div><ul style="margin-left:1.25rem">{ann_items}</ul></div>'
        b_naam = escape(b["naam"])
        b_br = breadcrumb(pp, b["naam"], [(f"{pp}index.html", "Home"), (f"{pp}begrippen.html", "Begrippen")])
        body = f"""{b_br}
<h1>{b_naam}</h1>
<p class="subtitle">{jas_tag(b["jas_klasse"])} <span class="badge badge-soort">{escape(b["soort"])}</span> {status_badge(b["status"])}</p>
<div class="detail-layout">
<div>
  <div class="card">
    <div class="card-title">Definitie</div>
    <div class="def-kern-label">Kern</div>
    <div class="def-block">{escape(b["definitie"]) if b["definitie"] else "<em>Geen definitie</em>"}</div>
    {def_bron}
    {ctx_block}
  </div>
  {mp}
</div>
<div>
  <div class="card">
    <div class="card-title">Kenmerken</div>
    <table class="prop-table">
      <tr><td>ID</td><td style="word-break:break-all;font-size:0.8rem">{escape(b["id"])}</td></tr>
      <tr><td>Soort</td><td>{escape(b["soort"] or "-")}{"&nbsp;<span class='badge badge-soort'>sleutel-id</span>" if b.get("soort_id") else ""}</td></tr>
      <tr><td>Herkomst</td><td>{escape(b["herkomst"] or "-")}</td></tr>
      <tr><td>Aliases</td><td>{", ".join(escape(a) for a in b["aliases"]) or "-"}</td></tr>
      <tr><td>Identificatiebegrip</td><td>{"Ja" if b.get("identificatiebegrip") else "Nee"}</td></tr>
      <tr><td>Tussenresultaat</td><td>{"Ja" if b["tussenresultaat"] else "Nee"}</td></tr>
      <tr><td>Definitie versie</td><td>{escape(str(b["definitie_versie"])) if b.get("definitie_versie") else "-"}</td></tr>
      <tr><td>Geldig vanaf</td><td>{escape(b["geldigheid_van"] or "-")}</td></tr>
      <tr><td>Geldig tot</td><td>{escape(b["geldigheid_tot"]) if b["geldigheid_tot"] else "&#8212;"}</td></tr>
      {f'<tr><td>Vervangen door</td><td><a href="{pp}begrippen/{slugify(b["vervangen_door"].rsplit("/",1)[-1])}.html">{escape(b["vervangen_door"])}</a></td></tr>' if b.get("vervangen_door") else ""}
    </table>
  </div>
  {f'<div class="card"><div class="card-title">JAS-toelichting</div><p style="font-size:0.85rem;font-style:italic">{escape(b["toelichting_klasse"])}</p></div>' if b["toelichting_klasse"] else ""}
  <div class="card">
    <div class="card-title">Relaties</div>
    {rel_html}
  </div>
  {ann_links}
  {f'<div class="card"><div class="card-title">Afleidingsregel</div>{reg_lnk}</div>' if reg_lnk else ""}
  {f'<div class="card"><div class="card-title">Uitvoer van regel</div>{uitvoer_lnk}</div>' if uitvoer_lnk else ""}
</div>
</div>
{_render_begrip_voorbeelden(b["voorbeelden"])}
{_render_begrip_kenmerken(b["kenmerken"])}
{_render_waarschuwingen(ws_index, b["slug"], meta)}"""
        schrijf_html(out, f'begrippen/{b["slug"]}.html', f'{b["naam"]} | Belastingdienst', body, active="begrippen", p="../")
