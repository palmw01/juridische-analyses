"""Tests voor sitegen/cli.py — main() paginagenerator."""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from sitegen.cli import main
from tests.fixtures.begrippen import maak_begrip
from tests.fixtures.regels import maak_regel
from tests.fixtures.annotaties import maak_annotatie


def test_main_genereert_index_html(project_root, tmp_path):
    out = tmp_path / "webapp_test"
    with patch.object(sys, "argv", ["sitegen", "--project-dir", str(project_root), "--out", str(out)]):
        main()
    assert (out / "index.html").exists()


def test_main_genereert_alle_kernpaginas(project_root, tmp_path):
    out = tmp_path / "webapp_test"
    with patch.object(sys, "argv", ["sitegen", "--project-dir", str(project_root), "--out", str(out)]):
        main()
    for pagina in ("begrippen.html", "annotaties.html", "regels.html", "sparql.html", "search.html", "graph.html", "404.html"):
        assert (out / pagina).exists(), f"{pagina} ontbreekt"


def test_main_genereert_css_en_js(project_root, tmp_path):
    out = tmp_path / "webapp_test"
    with patch.object(sys, "argv", ["sitegen", "--project-dir", str(project_root), "--out", str(out)]):
        main()
    assert (out / "css").is_dir()
    assert (out / "js").is_dir()


def test_main_genereert_data_json(project_root, tmp_path):
    out = tmp_path / "webapp_test"
    with patch.object(sys, "argv", ["sitegen", "--project-dir", str(project_root), "--out", str(out)]):
        main()
    assert (out / "data" / "begrippen.json").exists()
    assert (out / "data" / "annotaties.json").exists()
    assert (out / "data" / "regels.json").exists()


def test_main_met_begrip_en_regel(project_root, tmp_path):
    (project_root / "begrippen" / "test.yaml").write_text(yaml.dump(maak_begrip(), allow_unicode=True))
    (project_root / "regels" / "test.yaml").write_text(yaml.dump(maak_regel(), allow_unicode=True))
    out = tmp_path / "webapp_test"
    with patch.object(sys, "argv", ["sitegen", "--project-dir", str(project_root), "--out", str(out)]):
        main()
    assert (out / "begrippen" / "belastingschuldige.html").exists()


def test_main_verwijdert_bestaande_out_dir(project_root, tmp_path):
    out = tmp_path / "webapp_test"
    out.mkdir()
    (out / "oud_bestand.html").write_text("oud")
    with patch.object(sys, "argv", ["sitegen", "--project-dir", str(project_root), "--out", str(out)]):
        main()
    assert not (out / "oud_bestand.html").exists()


def test_main_print_statistieken(project_root, tmp_path, capsys):
    out = tmp_path / "webapp_test"
    with patch.object(sys, "argv", ["sitegen", "--project-dir", str(project_root), "--out", str(out)]):
        main()
    err = capsys.readouterr().err
    assert "begrippen" in err
    assert "annotaties" in err


def test_main_genereert_sitemap_en_robots(project_root, tmp_path):
    out = tmp_path / "webapp_test"
    with patch.object(sys, "argv", ["sitegen", "--project-dir", str(project_root), "--out", str(out)]):
        main()
    sitemap = out / "sitemap.xml"
    robots = out / "robots.txt"
    assert sitemap.exists()
    assert robots.exists()
    sitemap_txt = sitemap.read_text(encoding="utf-8")
    assert "<urlset" in sitemap_txt
    assert "index.html" in sitemap_txt
    assert "begrippen.html" in sitemap_txt
    # 404 mag niet in sitemap zitten
    assert "404.html" not in sitemap_txt
    robots_txt = robots.read_text(encoding="utf-8")
    assert "User-agent: *" in robots_txt
    assert "Sitemap:" in robots_txt
    assert "sitemap.xml" in robots_txt


def test_main_canonical_link_in_pagina(project_root, tmp_path):
    out = tmp_path / "webapp_test"
    with patch.object(sys, "argv", ["sitegen", "--project-dir", str(project_root), "--out", str(out)]):
        main()
    content = (out / "index.html").read_text(encoding="utf-8")
    assert '<link rel="canonical"' in content
    assert "/index.html" in content


def test_sitegen_main_als_module(project_root, tmp_path):
    """Dekt sitegen/__main__.py via runpy.run_module."""
    import runpy
    out = tmp_path / "webapp"
    with patch.object(sys, "argv", ["sitegen", "--project-dir", str(project_root), "--out", str(out)]):
        runpy.run_module("sitegen", run_name="__main__", alter_sys=False)
    assert (out / "index.html").exists()
