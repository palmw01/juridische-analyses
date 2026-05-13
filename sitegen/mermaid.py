from sitegen.config import JAS_KLEUREN, JAS_KLASSE_TO_ABBR, _text_color_for_bg


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
