from html import escape
from pathlib import Path

from sitegen.config import slugify
from sitegen.html import (
    breadcrumb,
    format_ann_title,
    format_structuurpositie,
    jas_tag,
    schrijf_html,
)
from sitegen.mermaid import diagram_tekst_fallback, diagram_to_mermaid


def gen_annotaties(out: Path, annotaties: list, regels: list, begrippen: list, indices: list | None = None):
    slug_by_bid: dict[str, str] = {b["id"]: b["slug"] for b in begrippen}
    naam_by_bid: dict[str, str] = {b["id"]: b["naam"] for b in begrippen}
    regel_by_bid: dict[str, list[dict]] = {}
    for reg in regels:
        ref = {"id": reg["id"], "naam": reg["naam"]}
        for inv in reg["invoer"]:
            regel_by_bid.setdefault(inv, []).append(ref)
        for uitv in reg["uitvoer"]:
            regel_by_bid.setdefault(uitv, []).append(ref)
    items = "".join(
        f'<li data-id="{idx["id"]}">'
        f'<a href="annotaties/{idx["id"].replace("/","-")}.html" class="item-title">{wet_label} — artikeloverzicht</a>'
        f'<div class="item-badges"><span class="badge badge-type">{idx.get("bwb_id","")}</span>'
        f'<span class="badge badge-soort">index</span></div>'
        f'<span class="item-meta">{idx.get("structuurpositie","")}</span>'
        f'</li>\n'
        for idx, wet_label in [(idx, f'{idx["wet"]} art. {idx["artikel"]}' if idx.get("wet") else idx["id"]) for idx in (indices or [])]
    ) + "".join(
        f'<li data-id="{a["id"]}">'
        f'<a href="annotaties/{a["id"].replace("/","-")}.html" class="item-title">{format_ann_title(a)}</a>'
        f'<div class="item-badges"><span class="badge badge-type">{a.get("bwb_id","")}</span></div>'
        f'<span class="item-meta">{format_structuurpositie(a)}</span>'
        f'</li>\n'
        for a in annotaties
    )
    body = f"""<h1>Annotaties ({len(annotaties)})</h1>
<label for="filterInput" class="sr-only">Filter op wet of artikel</label>
<input type="search" class="search-input" id="filterInput" placeholder="Filter op wet of artikel..."
       data-list="#itemList" data-source="data/annotaties.json"
       data-fields="titel,wetstekst" data-status="#filterStatus" data-empty="#filterEmpty">
<span id="filterStatus" class="result-status" role="status" aria-live="polite"></span>
<div class="item-list" id="itemList">{items}</div>
<div id="filterEmpty" class="empty-state" role="status">
  <div class="empty-state-title">Geen resultaten</div>
  <div>Pas je zoekterm aan of leeg het filter.</div>
</div>
<script src="https://cdn.jsdelivr.net/npm/minisearch@7/dist/umd/index.min.js" integrity="sha384-9Eacb80ywplqCp0P/bR61+zYn5Pg2LmQ7T8rppdoKHcQMmXbRh1wHwRC8avUJvnz" crossorigin="anonymous"></script>
<script src="js/filter-list.js"></script>"""
    schrijf_html(out, "annotaties.html", "Annotaties | Belastingdienst", body, active="annotaties")

    parent_by_ann_id: dict[str, dict] = {}
    for idx in (indices or []):
        for lid_id in idx.get("leden_annotaties") or []:
            parent_by_ann_id[lid_id] = idx

    for a in annotaties:
        rijen = ""
        for idx_r, r in enumerate(a["rijen"]):
            bgp_link = ""
            if r.get("begrip_id"):
                slug = slug_by_bid.get(r["begrip_id"]) or slugify(r["begrip_id"].rsplit("/", 1)[-1])
                naam = escape(naam_by_bid.get(r["begrip_id"]) or r["begrip_id"].rsplit("/", 1)[-1])
                bgp_link = f'<a href="../begrippen/{slug}.html">{naam}</a>'
            sign = escape(r.get("signalering") or "")
            toel_k = escape(r.get("toelichting_klasse", ""))
            rid = escape(r.get("rij_id", ""))
            interp = escape(r.get("interpretatiemethode", ""))
            markering_txt = escape(r.get("markering", ""))
            has_detail = bool(r.get("signalering") or r.get("toelichting_klasse"))
            if has_detail:
                detail_parts = []
                if rid:
                    detail_parts.append(f'<span class="sign-ref">{rid}</span>')
                if toel_k:
                    detail_parts.append(f'<em>{toel_k}</em>')
                if sign:
                    detail_parts.append(f'<strong>[!]</strong> {sign}')
                detail_html = " &mdash; ".join(detail_parts)
                badge_cls = "sign-badge sign-badge-warn" if r.get("signalering") else "sign-badge sign-badge-info"
                badge_sym = "!" if r.get("signalering") else "i"
                detail_id = f'sign-detail-{a["id"].replace("/", "-")}-{idx_r}'
                aria_lbl = "Signalering tonen" if r.get("signalering") else "Toelichting tonen"
                rijen += f'<tr><td class="mark-text">&#8220;{markering_txt}&#8221;</td><td>{jas_tag(r["jas_klasse"])}</td><td class="ann-interpretatie">{interp}</td><td>{bgp_link}</td>'
                rijen += (
                    f'<td class="ann-col-center">'
                    f'<button type="button" class="disclosure-btn" '
                    f'aria-expanded="false" aria-controls="{detail_id}" aria-label="{aria_lbl}">'
                    f'<span class="{badge_cls}" aria-hidden="true">{badge_sym}</span>'
                    f'</button></td></tr>\n'
                )
                rijen += (
                    f'<tr class="sign-detail" id="{detail_id}" hidden>'
                    f'<td colspan="5"><div class="sign-content">{detail_html}</div></td></tr>\n'
                )
            else:
                rijen += f'<tr><td class="mark-text">&#8220;{markering_txt}&#8221;</td><td>{jas_tag(r["jas_klasse"])}</td><td class="ann-interpretatie">{interp}</td><td>{bgp_link}</td><td class="ann-col-center"></td></tr>\n'
        mermaid_src = ""
        extra_scripts = ""
        mermaid_code = diagram_to_mermaid(a.get("diagram") or {})
        if mermaid_code:
            fallback = diagram_tekst_fallback(a.get("diagram") or {})
            mermaid_src = f"""<div class="card"><div class="card-title">Structuurdiagram</div>
<div class="mermaid" role="img" aria-busy="true" aria-label="Structuurdiagram van de annotatie">
{mermaid_code}
</div>
{fallback}
</div>"""
            extra_scripts = '<script type="module">import mermaid from \'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs\';(async function(){mermaid.initialize({startOnLoad:false,theme:\'neutral\',fontFamily:\'system-ui,sans-serif\'});await mermaid.run({querySelector:\'.mermaid\'});document.querySelectorAll(\'.mermaid\').forEach(function(el){el.removeAttribute(\'aria-busy\');});})();</script>'
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
        kruisref_html = ""
        if a.get("kruisreferenties"):
            kr_rows = ""
            for k in a["kruisreferenties"]:
                conf = k.get("confidence")
                conf_str = f'{int(conf * 100)}%' if conf is not None else ""
                doel = escape((k.get("doel_artikel") or k.get("doel_bwb_id", "")))
                if k.get("doel_lid"):
                    doel += f' lid {escape(str(k["doel_lid"]))}'
                kr_rows += f'<tr><td>{escape(k.get("ruwe_tekst",""))}</td><td>{escape(k.get("richting",""))}</td><td>{escape(k.get("doel_bwb_id",""))}</td><td>{doel}</td><td style="text-align:right">{conf_str}</td></tr>\n'
            kruisref_html = f'<div class="card"><div class="card-title">Kruisreferenties</div><div class="table-scroll"><table class="ann-table"><thead><tr><th scope="col">Verwijzing</th><th scope="col">Richting</th><th scope="col">BWB-id</th><th scope="col">Doel</th><th scope="col">Conf.</th></tr></thead><tbody>{kr_rows}</tbody></table></div></div>'
        deleg_html = ""
        if a.get("delegatiestructuur"):
            del_rows = ""
            for d in a["delegatiestructuur"]:
                inv = escape(d.get("invulling") or "-")
                vind_inv = d.get("vindplaats-invulling") or ""
                inv_cell = f'<a href="{escape(vind_inv, quote=True)}">{inv}</a>' if vind_inv and vind_inv.startswith("http") else (f'{inv} <span style="font-size:0.75rem;color:var(--text-muted)">{escape(vind_inv)}</span>' if vind_inv else inv)
                del_rows += f'<tr><td>{escape(d.get("omschrijving",""))}</td><td>{escape(d.get("vindplaats",""))}</td><td><span class="badge badge-soort">{escape(d.get("type",""))}</span></td><td>{inv_cell}</td></tr>\n'
            deleg_html = f'<div class="card"><div class="card-title">Delegatiestructuur</div><div class="table-scroll"><table class="ann-table"><thead><tr><th scope="col">Omschrijving</th><th scope="col">Vindplaats</th><th scope="col">Type</th><th scope="col">Invulling</th></tr></thead><tbody>{del_rows}</tbody></table></div></div>'
        peildatum_str = f' &bull; Peildatum: {escape(str(a["peildatum"]))}' if a.get("peildatum") else ""
        parent_link = ""
        parent_idx = parent_by_ann_id.get(a["id"])
        if parent_idx:
            parent_slug = parent_idx["id"].replace("/", "-")
            parent_titel = f'{parent_idx["wet"]} art. {parent_idx["artikel"]}' if parent_idx.get("wet") else parent_idx["id"]
            parent_link = f'<div class="card"><div class="card-title">Deel van artikel</div><p><a href="../annotaties/{parent_slug}.html">{parent_titel} — artikeloverzicht</a></p></div>'
        ann_title = format_ann_title(a)
        ann_br = breadcrumb("../", ann_title, [("../index.html", "Home"), ("../annotaties.html", "Annotaties")])
        body = f"""{ann_br}
<h1>{ann_title}</h1>
<p class="subtitle">{format_structuurpositie(a)} &bull; {escape(a["bwb_id"])}{peildatum_str}</p>
<div class="wetstekst">&#8220;{escape(a["wetstekst"])}&#8221;</div>
<div class="card">
<div class="card-title">Annotatierijen</div>
<div class="table-scroll">
<table class="ann-table">
  <thead>
    <tr><th scope="col">Markering</th><th scope="col">JAS-klasse</th><th scope="col">Interpretatie</th><th scope="col">Begrip</th><th scope="col" class="ann-col-center">Detail</th></tr>
  </thead>
  <tbody>
  {rijen}
  </tbody>
</table></div>
</div>
{mermaid_src}
{kruisref_html}
{deleg_html}
{parent_link}
{regel_links}"""
        schrijf_html(out, f'annotaties/{a["id"].replace("/","-")}.html', f'Annotatie art. {a["artikel"]} | Belastingdienst', body, active="annotaties", p="../", extra_scripts=extra_scripts)
