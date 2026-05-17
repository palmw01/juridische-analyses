from html import escape

from sitegen.config import JAS_KLEUREN, JAS_KLASSE_TO_ABBR, _text_color_for_bg


def diagram_tekst_fallback(diagram: dict) -> str:
    """Tekstuele samenvatting van een diagram voor screenreaders en pre-render fallback.
    Beschrijft de knopen en de relaties tussen knopen in proza."""
    if not diagram or not diagram.get("knopen"):
        return ""
    knopen = diagram["knopen"]
    label_by_id = {k["id"]: k.get("label", k.get("jas-klasse", k["id"])) for k in knopen}
    n_kn = len(knopen)
    kant_zinnen: list[str] = []
    for kant in diagram.get("kanten") or []:
        van = label_by_id.get(kant["van"], kant["van"])
        naar = label_by_id.get(kant["naar"], kant["naar"])
        lbl = kant.get("label")
        if lbl:
            kant_zinnen.append(f"{van} → {lbl} → {naar}")
        else:
            kant_zinnen.append(f"{van} — {naar}")
    knoop_items = "".join(
        f'<li><strong>{escape(k.get("label", k.get("jas-klasse", k["id"])))}</strong> '
        f'<span class="diagram-fallback-klasse">({escape(k.get("jas-klasse", ""))})</span></li>'
        for k in knopen
    )
    kant_items = "".join(f"<li>{escape(z)}</li>" for z in kant_zinnen)
    relatie_blok = (
        f'<p>Relaties tussen knopen ({len(kant_zinnen)}):</p><ul>{kant_items}</ul>'
        if kant_zinnen else '<p>Geen relaties tussen knopen.</p>'
    )
    return (
        f'<details class="diagram-fallback">'
        f'<summary>Tekstuele beschrijving van het diagram ({n_kn} knopen)</summary>'
        f'<p>Knopen:</p><ul>{knoop_items}</ul>'
        f'{relatie_blok}'
        f'</details>'
    )


def diagram_to_mermaid(diagram: dict) -> str:
    if not diagram or not diagram.get("knopen"):
        return ""
    lines = ["graph LR"]
    classes_used: set[str] = set()
    for knoop in diagram["knopen"]:
        nid = knoop["id"]
        jk = knoop["jas-klasse"]
        abbr = JAS_KLASSE_TO_ABBR.get(jk, "xx")
        classes_used.add(jk)
        label = knoop.get("label", jk)
        parts = label.split(" ", 1)
        display = f"{parts[0]}<br/>{parts[1]}" if len(parts) == 2 else label
        display = display.replace('"', '&quot;')
        lines.append(f'    {nid}["{display}"]:::{abbr}')
    for kant in diagram.get("kanten") or []:
        van, naar = kant["van"], kant["naar"]
        lbl = kant.get("label")
        lines.append(f'    {van} -->|{lbl}| {naar}' if lbl else f'    {van} --- {naar}')
    lines.append("")
    for jk in sorted(classes_used):
        abbr = JAS_KLASSE_TO_ABBR.get(jk, "xx")
        c = JAS_KLEUREN.get(jk, "#888")
        lines.append(f'    classDef {abbr} fill:{c}{_text_color_for_bg(c)}')
    return "\n".join(lines)
