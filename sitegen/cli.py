import argparse
import shutil
import sys
from pathlib import Path

from sitegen import assets
from sitegen.data import laad_annotaties, laad_artikel_indices, laad_begrippen, laad_regels, laad_voorbeeldreeksen, laad_waarschuwingen, laad_waarschuwingen_meta
from sitegen.pages.annotaties import gen_annotaties
from sitegen.pages.artikel_indices import gen_artikel_indices
from sitegen.pages.begrippen import gen_begrippen
from sitegen.pages.graph import gen_graph
from sitegen.pages.index import gen_404, gen_index
from sitegen.pages.kwaliteit import gen_kwaliteit
from sitegen.pages.regels import gen_regels
from sitegen.pages.search import gen_search
from sitegen.pages.sparql import gen_sparql


def main():
    parser = argparse.ArgumentParser(description="Genereer statische webapp uit project")
    parser.add_argument("--project-dir", default=".", help="Pad naar project-root")
    parser.add_argument("--out", default="webapp", help="Output directory")
    args = parser.parse_args()

    project_dir = Path(args.project_dir)
    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)

    print("Data laden...", file=sys.stderr)
    begrippen = laad_begrippen(project_dir)
    annotaties = laad_annotaties(project_dir)
    regels = laad_regels(project_dir)
    voorbeeldreeksen = laad_voorbeeldreeksen(project_dir)
    artikel_indices = laad_artikel_indices(project_dir)
    waarschuwingen = laad_waarschuwingen(project_dir)
    meta = laad_waarschuwingen_meta(project_dir)
    print(f"  {len(begrippen)} begrippen, {len(annotaties)} annotaties, {len(regels)} regels, {len(voorbeeldreeksen)} voorbeeldreeksen, {len(artikel_indices)} artikel-indices", file=sys.stderr)

    print("CSS, JS en icons genereren...", file=sys.stderr)
    assets.gen_css_js(out, project_dir)
    assets.gen_icons(project_dir, out)

    print("Pagina's genereren...", file=sys.stderr)
    gen_index(out, begrippen, annotaties, regels, waarschuwingen)
    gen_404(out)
    gen_begrippen(out, begrippen, annotaties, waarschuwingen, meta)
    gen_annotaties(out, annotaties, regels, begrippen, indices=artikel_indices)
    gen_artikel_indices(out, artikel_indices, annotaties)
    gen_regels(out, regels, begrippen, annotaties, waarschuwingen, meta, voorbeeldreeksen)
    gen_kwaliteit(out, waarschuwingen, meta)
    gen_graph(out, begrippen, regels, annotaties)
    gen_search(out, begrippen, annotaties, regels)
    gen_sparql(out)
    assets.gen_data_files(out, begrippen, annotaties, regels, artikel_indices, project_root=project_dir)
    assets.gen_seo_files(out)

    print(f"Webapp gegenereerd in {out}/ ({len(list(out.rglob('*')))} bestanden)", file=sys.stderr)
