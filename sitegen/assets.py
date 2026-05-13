import json
import shutil
from pathlib import Path

from sitegen.config import slugify
from sitegen.html import format_ann_title


def gen_css_js(out: Path, project_root: Path | None = None):
    static_dir = Path(__file__).resolve().parent / "static"
    (out / "css").mkdir(parents=True, exist_ok=True)
    (out / "js").mkdir(parents=True, exist_ok=True)
    css_src = static_dir / "style.css"
    js_src = static_dir / "app.js"
    if css_src.exists():
        (out / "css/style.css").write_text(css_src.read_text())
    if js_src.exists():
        (out / "js/app.js").write_text(js_src.read_text())
    build_dir = (project_root or Path(".")).resolve() / ".build"
    comunica_src = build_dir / "comunica.min.js"
    if comunica_src.exists() and comunica_src.stat().st_size > 100:
        (out / "js/comunica.min.js").write_bytes(comunica_src.read_bytes())


def gen_icons(project_dir: Path, out: Path):
    src = project_dir / "icons"
    dst = out / "icons"
    dst.mkdir(parents=True, exist_ok=True)
    if src.exists():
        for f in src.iterdir():
            if f.is_file():
                shutil.copy2(f, dst / f.name)
    manifest = out / "manifest.json"
    if not manifest.exists():
        manifest.write_text("""{"name":"Rechtsgraaf — Kennismodel Invordering","short_name":"Rechtsgraaf","start_url":".","display":"standalone","background_color":"#154273","theme_color":"#154273","icons":[{"src":"icons/favicon-192.png","sizes":"192x192","type":"image/png"},{"src":"icons/favicon-512.png","sizes":"512x512","type":"image/png"}]}""")


def gen_data_files(out: Path, begrippen: list, annotaties: list, regels: list, indices: list, project_root: Path | None = None):
    data_dir = out / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    b_data = []
    for b in begrippen:
        b_data.append({
            "id": b["slug"],
            "titel": b["naam"],
            "url": f'begrippen/{b["slug"]}.html',
            "type": "Begrip",
            "definitie": b["definitie"],
            "tekst": b["definitie"],
            "aliases": " ".join(b["aliases"]),
            "jas_klasse": b["jas_klasse"],
            "soort": b["soort"],
            "status": b["status"],
        })

    a_data = []
    for a in annotaties:
        a_data.append({
            "id": a["id"],
            "titel": format_ann_title(a),
            "url": f'annotaties/{a["id"].replace("/","-")}.html',
            "type": "Annotatie",
            "wetstekst": a["wetstekst"],
            "tekst": a["wetstekst"],
            "bwb_id": a["bwb_id"],
        })
    for idx in indices:
        wet_label = f'{idx["wet"]} art. {idx["artikel"]}' if idx.get("wet") else idx["id"]
        a_data.append({
            "id": idx["id"],
            "titel": f'{wet_label} — artikeloverzicht',
            "url": f'annotaties/{slugify(idx["id"])}.html',
            "type": "Annotatie",
            "wetstekst": "",
            "tekst": f'{idx.get("structuurpositie","")} {idx.get("bwb_id","")}',
            "bwb_id": idx.get("bwb_id", ""),
        })

    r_data = []
    for r in regels:
        r_data.append({
            "id": r["id"],
            "titel": r["naam"],
            "url": f'regels/{r["id"]}.html',
            "type": "Regel",
            "formele_regel": r["formele_regel"],
            "toelichting": r["toelichting"],
            "tekst": r["formele_regel"],
            "soort": r["soort"],
        })

    (data_dir / "begrippen.json").write_text(json.dumps(b_data, ensure_ascii=False))
    (data_dir / "annotaties.json").write_text(json.dumps(a_data, ensure_ascii=False))
    (data_dir / "regels.json").write_text(json.dumps(r_data, ensure_ascii=False))

    # RDF Turtle voor SPARQL (optioneel, na make export-rdf)
    ttl_src = (project_root or Path(".")) / "kennisgraaf" / "begrippen.ttl"
    if ttl_src.exists():
        shutil.copy2(ttl_src, data_dir / "begrippen.ttl")
