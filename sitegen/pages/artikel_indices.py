from pathlib import Path

from sitegen.config import slugify
from sitegen.html import breadcrumb, format_ann_title, schrijf_html


def gen_artikel_indices(out: Path, indices: list, annotaties: list):
    ann_by_id: dict[str, dict] = {a["id"]: a for a in annotaties}
    p = "../"
    for idx in indices:
        slug = slugify(idx["id"])
        titel = f'{idx["wet"]} art. {idx["artikel"]}' if idx.get("wet") else idx["id"]
        leden_html = ""
        for lid_id in idx["leden_annotaties"]:
            a = ann_by_id.get(lid_id)
            if a:
                a_url = f'../annotaties/{a["id"].replace("/","-")}.html'
                a_titel = format_ann_title(a)
                leden_html += f'<li><a href="{a_url}">{a_titel}</a></li>\n'
            else:
                leden_html += f'<li class="item-meta">{lid_id}</li>\n'
        if not leden_html:
            leden_html = '<li class="item-meta">Geen lid-annotaties gevonden</li>'
        kr_rows = ""
        for k in idx["kruisreferenties"]:
            kr_rows += f'<tr><td>{k}</td></tr>\n'
        kruisref_html = (
            f'<div class="card"><div class="card-title">Kruisreferenties</div>'
            f'<div class="table-scroll"><table class="ann-table"><tr><th>Verwijzing</th></tr>{kr_rows}</table></div></div>'
        ) if kr_rows else ""
        deleg_html = ""
        if idx["delegatiestructuur"]:
            del_rows = ""
            for d in idx["delegatiestructuur"]:
                inv = d.get("invulling") or "-"
                vind_inv = d.get("vindplaats-invulling") or ""
                inv_cell = f'{inv} <span style="font-size:0.75rem;color:var(--text-muted)">{vind_inv}</span>' if vind_inv else inv
                del_rows += f'<tr><td>{d.get("omschrijving","")}</td><td>{d.get("vindplaats","")}</td><td><span class="badge badge-soort">{d.get("type","")}</span></td><td>{inv_cell}</td></tr>\n'
            deleg_html = (
                f'<div class="card"><div class="card-title">Delegatiestructuur</div>'
                f'<div class="table-scroll"><table class="ann-table">'
                f'<tr><th>Omschrijving</th><th>Vindplaats</th><th>Type</th><th>Invulling</th></tr>'
                f'{del_rows}</table></div></div>'
            )
        peildatum_str = f' &bull; Peildatum: {idx["peildatum"]}' if idx.get("peildatum") else ""
        br = breadcrumb(p, titel, [(f"{p}index.html", "Home"), (f"{p}annotaties.html", "Annotaties")])
        body = f"""{br}
<h1>{titel}</h1>
<p class="subtitle">{idx.get("structuurpositie","")}{peildatum_str}</p>
<div class="card">
  <div class="card-title">Lid-annotaties</div>
  <ul style="margin-left:1.25rem">{leden_html}</ul>
</div>
{kruisref_html}
{deleg_html}"""
        schrijf_html(out, f'annotaties/{slug}.html', f'{titel} | Belastingdienst', body, active="annotaties", p=p)
