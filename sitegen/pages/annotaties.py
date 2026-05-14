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
from sitegen.mermaid import diagram_to_mermaid


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
        f'<li data-id="{idx["id"]}" onclick="window.location=\'annotaties/{idx["id"].replace("/","-")}.html\'">'
        f'<a href="annotaties/{idx["id"].replace("/","-")}.html" class="item-title">{wet_label} — artikeloverzicht</a>'
        f'<div class="item-badges"><span class="badge badge-type">{idx.get("bwb_id","")}</span>'
        f'<span class="badge badge-soort">index</span></div>'
        f'<span class="item-meta">{idx.get("structuurpositie","")}</span>'
        f'</li>\n'
        for idx, wet_label in [(idx, f'{idx["wet"]} art. {idx["artikel"]}' if idx.get("wet") else idx["id"]) for idx in (indices or [])]
    ) + "".join(
        f'<li data-id="{a["id"]}" onclick="window.location=\'annotaties/{a["id"].replace("/","-")}.html\'">'
        f'<a href="annotaties/{a["id"].replace("/","-")}.html" class="item-title">{format_ann_title(a)}</a>'
        f'<div class="item-badges"><span class="badge badge-type">{a.get("bwb_id","")}</span></div>'
        f'<span class="item-meta">{format_structuurpositie(a)}</span>'
        f'</li>\n'
        for a in annotaties
    )
    body = f"""<h1>Annotaties ({len(annotaties)})</h1>
<label for="filterInput" class="sr-only">Filter op wet of artikel</label>
<input type="text" class="search-input" id="filterInput" placeholder="Filter op wet of artikel..." autofocus>
<div class="item-list" id="itemList">{items}</div>
<script src="https://cdn.jsdelivr.net/npm/minisearch@7/dist/umd/index.min.js" integrity="sha384-9Eacb80ywplqCp0P/bR61+zYn5Pg2LmQ7T8rppdoKHcQMmXbRh1wHwRC8avUJvnz" crossorigin="anonymous"></script>
<script>
var _dr=false;
var _inp=document.getElementById('filterInput');
var _ms=new MiniSearch({{fields:['titel','wetstekst'],storeFields:['titel'],searchOptions:{{prefix:true,fuzzy:0.2}}}});
if(_inp)_inp.placeholder='Zoekindex laden...';
fetch('data/annotaties.json').then(function(r){{return r.json()}}).then(function(d){{_ms.addAll(d);_dr=true;if(_inp)_inp.placeholder='Filter op wet of artikel...'}});
_inp?.addEventListener('input',function(){{
  var q=this.value.trim();
  if(!q||!_dr){{document.querySelectorAll('#itemList li').forEach(function(l){{l.style.display=''}});return}}
  var s=new Set(_ms.search(q).map(function(r){{return r.id}}));
  document.querySelectorAll('#itemList li').forEach(function(l){{l.style.display=s.has(l.getAttribute('data-id'))?'':'none'}});
}});
</script>"""
    schrijf_html(out, "annotaties.html", "Annotaties | Belastingdienst", body, active="annotaties")

    parent_by_ann_id: dict[str, dict] = {}
    for idx in (indices or []):
        for lid_id in idx.get("leden_annotaties") or []:
            parent_by_ann_id[lid_id] = idx

    for a in annotaties:
        rijen = ""
        for r in a["rijen"]:
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
                rijen += f'<tr class="has-sign" onclick="var d=this.nextElementSibling;d.style.display=d.style.display===\'none\'?\'table-row\':\'none\'">'
                rijen += f'<td class="mark-text">&#8220;{markering_txt}&#8221;</td><td>{jas_tag(r["jas_klasse"])}</td><td style="font-size:0.8rem;color:var(--text-muted)">{interp}</td><td>{bgp_link}</td>'
                rijen += f'<td style="text-align:center"><span class="sign-badge">{"[!]" if r.get("signalering") else "i"}</span></td></tr>\n'
                rijen += f'<tr class="sign-detail" style="display:none"><td colspan="5"><div class="sign-content">{detail_html}</div></td></tr>\n'
            else:
                rijen += f'<tr><td class="mark-text">&#8220;{markering_txt}&#8221;</td><td>{jas_tag(r["jas_klasse"])}</td><td style="font-size:0.8rem;color:var(--text-muted)">{interp}</td><td>{bgp_link}</td><td style="text-align:center"></td></tr>\n'
        mermaid_src = ""
        extra_scripts = ""
        mermaid_code = diagram_to_mermaid(a.get("diagram") or {})
        if mermaid_code:
            mermaid_src = f"""<div class="card"><div class="card-title">Structuurdiagram</div>
<div class="mermaid">
{mermaid_code}
</div></div>"""
            extra_scripts = '<script type="module">import mermaid from \'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs\';(async function(){mermaid.initialize({startOnLoad:false,theme:\'neutral\',fontFamily:\'system-ui,sans-serif\'});await mermaid.run({querySelector:\'.mermaid\'});})();</script>'
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
            kruisref_html = f'<div class="card"><div class="card-title">Kruisreferenties</div><div class="table-scroll"><table class="ann-table"><tr><th>Verwijzing</th><th>Richting</th><th>BWB-id</th><th>Doel</th><th>Conf.</th></tr>{kr_rows}</table></div></div>'
        deleg_html = ""
        if a.get("delegatiestructuur"):
            del_rows = ""
            for d in a["delegatiestructuur"]:
                inv = escape(d.get("invulling") or "-")
                vind_inv = d.get("vindplaats-invulling") or ""
                inv_cell = f'<a href="{escape(vind_inv, quote=True)}">{inv}</a>' if vind_inv and vind_inv.startswith("http") else (f'{inv} <span style="font-size:0.75rem;color:var(--text-muted)">{escape(vind_inv)}</span>' if vind_inv else inv)
                del_rows += f'<tr><td>{escape(d.get("omschrijving",""))}</td><td>{escape(d.get("vindplaats",""))}</td><td><span class="badge badge-soort">{escape(d.get("type",""))}</span></td><td>{inv_cell}</td></tr>\n'
            deleg_html = f'<div class="card"><div class="card-title">Delegatiestructuur</div><div class="table-scroll"><table class="ann-table"><tr><th>Omschrijving</th><th>Vindplaats</th><th>Type</th><th>Invulling</th></tr>{del_rows}</table></div></div>'
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
  <tr><th>Markering</th><th>JAS-klasse</th><th>Interpretatie</th><th>Begrip</th><th style="text-align:center">Detail</th></tr>
  {rijen}
</table></div>
</div>
{mermaid_src}
{kruisref_html}
{deleg_html}
{parent_link}
{regel_links}"""
        schrijf_html(out, f'annotaties/{a["id"].replace("/","-")}.html', f'Annotatie art. {a["artikel"]} | Belastingdienst', body, active="annotaties", p="../", extra_scripts=extra_scripts)
