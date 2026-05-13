import re


JAS_KLEUREN: dict[str, str] = {
    "rechtssubject": "#4472C4",
    "rechtsobject": "#70AD47",
    "rechtsbetrekking": "#FF0000",
    "rechtsfeit": "#FFC000",
    "voorwaarde": "#7030A0",
    "afleidingsregel": "#00B0F0",
    "variabele": "#92D050",
    "tijdsaanduiding": "#F4B942",
    "operator": "#808080",
    "parameter": "#FFD966",
    "plaatsaanduiding": "#9DC3E6",
    "delegatiebevoegdheid": "#C9C9C9",
    "brondefinitie": "#B4C7E7",
}

JAS_KLASSE_TO_ABBR: dict[str, str] = {
    "rechtssubject": "rs",
    "rechtsobject": "ro",
    "rechtsbetrekking": "rb",
    "rechtsfeit": "rf",
    "voorwaarde": "vw",
    "afleidingsregel": "ar",
    "variabele": "va",
    "parameter": "pa",
    "tijdsaanduiding": "ta",
    "plaatsaanduiding": "pl",
    "delegatiebevoegdheid": "db",
    "brondefinitie": "bd",
    "operator": "op",
}


def slugify(s: str) -> str:
    return re.sub(r'[^a-z0-9-]', '', s.lower().replace('/', '-').replace('_', '-'))


def _text_color_for_bg(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = h[0]*2 + h[1]*2 + h[2]*2
    if len(h) != 6:
        return ""
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return ",color:#fff" if lum < 140 else ""
