from html import escape
from pathlib import Path

from sitegen.html import breadcrumb, schrijf_html


def _waarschuwing_type(boodschap: str) -> str:
    tekst = boodschap
    for prefix in ("[L3] ", "[L2] ", "[L1] "):
        tekst = tekst.removeprefix(prefix)
    return tekst.split(" — ")[0]


def _pad_naar_url(bestand: str) -> str:
    if bestand.startswith("begrippen/"):
        return f"begrippen/{Path(bestand).stem}.html"
    if bestand.startswith("regels/"):
        return f"regels/{Path(bestand).stem}.html"
    return ""


def _render_oplossing(meta_entry: dict | None) -> str:
    if not meta_entry:
        return ""
    titel = escape(meta_entry.get("titel", ""))
    uitleg = escape(meta_entry.get("uitleg", "").strip())
    stappen = meta_entry.get("stappen") or []
    commando = escape(meta_entry.get("commando", "") or "")
    stappen_html = "".join(f"<li>{escape(s)}</li>" for s in stappen)
    commando_html = f'<p class="oplossing-commando">Skill: <code>{commando}</code></p>' if commando else ""
    return (
        f'<div class="oplossing-blok">'
        f'<div class="oplossing-titel">{titel}</div>'
        f'<p class="oplossing-uitleg">{uitleg}</p>'
        f'<ol class="oplossing-stappen">{stappen_html}</ol>'
        f'{commando_html}'
        f'</div>'
    )


def gen_kwaliteit(out: Path, waarschuwingen: dict[str, list[str]], meta: list | None = None):
    from sitegen.data import zoek_meta
    meta_lijst = meta or []
    items_data = []
    idx = 0
    for bestand, ws in sorted(waarschuwingen.items()):
        for w in ws:
            items_data.append({
                "id": str(idx),
                "bestand": bestand,
                "boodschap": w,
                "type": _waarschuwing_type(w),
                "url": _pad_naar_url(bestand),
            })
            idx += 1

    totaal = len(items_data)

    items_html = ""
    for item in items_data:
        url = item["url"]
        bestand_html = (
            f'<a href="{escape(url)}">{escape(item["bestand"])}</a>'
            if url else escape(item["bestand"])
        )
        boodschap_kort = escape(item["boodschap"].removeprefix("[L3] ").removeprefix("[L2] ").removeprefix("[L1] "))
        oplossing_html = _render_oplossing(zoek_meta(item["boodschap"], meta_lijst))
        items_html += (
            f'<li data-id="{item["id"]}">'
            f'<span class="badge badge-soort">{escape(item["type"])}</span> '
            f'{bestand_html}'
            f'<div class="item-detail">'
            f'<div class="item-meta">{boodschap_kort}</div>'
            f'{oplossing_html}'
            f'</div>'
            f'</li>\n'
        )

    import json as _json
    ms_data = _json.dumps(items_data, ensure_ascii=False)

    body = f"""<h1>Kwaliteitsrapport ({totaal} openstaande punten)</h1>
<label for="filterInput" class="sr-only">Filter op bestand, type of boodschap</label>
<input type="search" class="search-input" id="filterInput" placeholder="Filter op bestand, type of boodschap..."
       data-list="#itemList" data-inline="kwaliteitData"
       data-fields="bestand,boodschap,type" data-status="#filterStatus" data-empty="#filterEmpty">
<span id="filterStatus" class="result-status" role="status" aria-live="polite"></span>
<div class="item-list" id="itemList">{items_html}</div>
<div id="filterEmpty" class="empty-state" role="status">
  <div class="empty-state-title">Geen resultaten</div>
  <div>Pas je zoekterm aan of leeg het filter.</div>
</div>
<script id="kwaliteitData" type="application/json">{ms_data}</script>
<script src="https://cdn.jsdelivr.net/npm/minisearch@7/dist/umd/index.min.js" integrity="sha384-9Eacb80ywplqCp0P/bR61+zYn5Pg2LmQ7T8rppdoKHcQMmXbRh1wHwRC8avUJvnz" crossorigin="anonymous"></script>
<script src="js/filter-list.js"></script>"""

    schrijf_html(out, "kwaliteit.html", "Kwaliteitsrapport | Belastingdienst", body, active="kwaliteit")
