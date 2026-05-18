from html import escape
from pathlib import Path

from sitegen.config import JAS_KLEUREN


def gen_nav(active: str = "", p: str = "") -> str:
    items = [
        (f"{p}index.html", "Dashboard"),
        (f"{p}begrippen.html", "Begrippen"),
        (f"{p}annotaties.html", "Annotaties"),
        (f"{p}start_annotatie.html", "Annotatie starten"),
        (f"{p}regels.html", "Regels"),
        (f"{p}kwaliteit.html", "Kwaliteit"),
        (f"{p}graph.html", "Kennisgraaf"),
        (f"{p}sparql.html", "SPARQL"),
        (f"{p}search.html", "Zoeken"),
    ]
    links = ""
    for url, label in items:
        cls = ' class="active" aria-current="page"' if label.lower() == active.lower() else ""
        links += f'<a href="{url}"{cls}>{label}</a>\n'
    return f"""<nav class="nav">
<div class="container">
  <div class="nav-logo"><a href="{p}index.html" aria-label="Home">Rechtsgraaf</a></div>
  <button class="dark-toggle" id="darkToggle" aria-label="Donker/licht modus wisselen" title="Donker/licht modus" type="button">
    <span class="dt-icon">&#x2600;</span>
  </button>
  <button class="hamburger" id="hamburger" aria-label="Menu openen" aria-expanded="false" type="button">
    <span class="hamburger-label" aria-hidden="true">Menu</span>
    <span class="hamburger-lines"><span></span><span></span><span></span></span>
  </button>
  <div class="nav-links">
    {links}
  </div>
</div>
</nav>"""


DEFAULT_DESCRIPTION = (
    "Gestructureerde wetsanalyse Artikel 9 Invorderingswet 1990 volgens "
    "JAS v1.0.10 — begrippen, annotaties, afleidingsregels en kennisgraaf "
    "voor de Belastingdienst (domein Inning)."
)

# Canonical base-URL; mag door cli overschreven worden via env SITEGEN_BASE_URL.
SITE_BASE_URL = "https://palmw01.github.io/juridische-analyses"


def _canonical(p: str, rel: str) -> str:
    base = SITE_BASE_URL.rstrip("/")
    return f"{base}/{rel.lstrip('/')}"


def pagina(
    title: str,
    body: str,
    active: str = "",
    p: str = "",
    extra_scripts: str = "",
    description: str = "",
    canonical_path: str = "",
) -> str:
    desc = escape(description or DEFAULT_DESCRIPTION)
    canonical_tag = ""
    if canonical_path:
        canonical_tag = f'<link rel="canonical" href="{escape(_canonical(p, canonical_path), quote=True)}">'
    return f"""<!DOCTYPE html>
<html lang="nl" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{desc}">
{canonical_tag}
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary">
<link rel="icon" type="image/svg+xml" href="{p}icons/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="{p}icons/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="{p}icons/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="{p}icons/apple-touch-icon.png">
<link rel="manifest" href="{p}manifest.json">
<meta name="theme-color" content="#154273">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{p}css/style.css">
</head>
<body>
<a href="#main-content" class="skip-link">Direct naar inhoud</a>
{gen_nav(active, p)}
<main id="main-content"><div class="container">
{body}
</div></main>
<footer>Rechtsgraaf &bull; Belastingdienst &bull; Inning &bull; Art. 9 IW 1990 &bull; <a href="https://github.com/palmw01/juridische-analyses" target="_blank" rel="noopener noreferrer">GitHub<span class="ext-link-icon" aria-hidden="true">&#x2197;</span><span class="sr-only"> (opent in nieuw venster)</span></a></footer>
<script src="{p}js/app.js"></script>
<script src="{p}js/copy.js" defer></script>
{extra_scripts}
</body>
</html>"""


def schrijf_html(out: Path, rel: str, title: str, body: str, active: str = "", p: str = "", extra_scripts: str = "", description: str = ""):
    pad = out / rel
    pad.parent.mkdir(parents=True, exist_ok=True)
    pad.write_text(pagina(title, body, active, p, extra_scripts, description, canonical_path=rel), encoding="utf-8")


def breadcrumb(p: str, active: str, crumbs: list[tuple[str, str]]) -> str:
    items = "".join(f'<li><a href="{url}">{escape(label)}</a></li>' for url, label in crumbs)
    return f'<nav aria-label="U bevindt zich hier"><ol class="breadcrumb">{items}<li aria-current="page">{escape(active)}</li></ol></nav>'


def jas_tag(klasse: str) -> str:
    kleur = JAS_KLEUREN.get(klasse, "#888")
    return f'<span class="tag" style="background:{kleur}">{escape(klasse)}</span>'


def status_badge(status: str) -> str:
    s = status or "concept"
    return f'<span class="badge badge-{s}">{escape(status or "onbekend")}</span>'


COPY_ICON_SVG = (
    '<svg class="copy-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true">'
    '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>'
    '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>'
)


def copy_button(target_selector: str, label: str = "Kopieer naar klembord") -> str:
    return (
        f'<button type="button" class="copy-btn" '
        f'data-copy-target="{escape(target_selector, quote=True)}" '
        f'aria-label="{escape(label)}" title="{escape(label)}">'
        f'{COPY_ICON_SVG}<span class="copy-status" aria-hidden="true"></span></button>'
    )


def format_ann_title(a: dict) -> str:
    wet = escape(a.get("wet", ""))
    artikel = escape(str(a.get("artikel", "")))
    lid = escape(str(a.get("lid", "")))
    if a.get("wet", "").startswith("LI "):
        return f'{wet} § {lid}' if lid else f'{wet} § {artikel}'
    return f'{wet} art. {artikel}{", lid " + lid if lid else ""}'


def format_structuurpositie(a: dict) -> str:
    pos = a.get("structuurpositie", "")
    if a.get("wet", "").startswith("LI ") and pos:
        pos = pos.replace("Lid ", "§ ")
    return escape(pos)
