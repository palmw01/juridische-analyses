"""Tests voor sitegen/pages/kwaliteit.py."""
from sitegen.pages.kwaliteit import gen_kwaliteit


def test_gen_kwaliteit_maakt_kwaliteit_html(tmp_path):
    gen_kwaliteit(tmp_path, {})
    assert (tmp_path / "kwaliteit.html").exists()


def test_gen_kwaliteit_leeg_geen_crash(tmp_path):
    gen_kwaliteit(tmp_path, {})
    content = (tmp_path / "kwaliteit.html").read_text()
    assert "0 openstaande punten" in content


def test_gen_kwaliteit_toont_waarschuwing(tmp_path):
    ws = {"begrippen/belastingaanslag.yaml": ["[L3] Relaties leeg — overweeg is-een relatie"]}
    gen_kwaliteit(tmp_path, ws)
    content = (tmp_path / "kwaliteit.html").read_text()
    assert "1 openstaande punten" in content
    assert "belastingaanslag" in content
    assert "Relaties leeg" in content


def test_gen_kwaliteit_meerdere_waarschuwingen(tmp_path):
    ws = {
        "begrippen/belastingaanslag.yaml": ["[L3] Relaties leeg — overweeg is-een"],
        "regels/AR-001.yaml": ["[L3] soort is Specialisatieregel maar id ontbreekt"],
    }
    gen_kwaliteit(tmp_path, ws)
    content = (tmp_path / "kwaliteit.html").read_text()
    assert "2 openstaande punten" in content
    assert "belastingaanslag" in content
    assert "AR-001" in content


def test_gen_kwaliteit_begrip_link_correct(tmp_path):
    ws = {"begrippen/belastingaanslag.yaml": ["[L3] test"]}
    gen_kwaliteit(tmp_path, ws)
    content = (tmp_path / "kwaliteit.html").read_text()
    assert 'href="begrippen/belastingaanslag.html"' in content


def test_gen_kwaliteit_regel_link_correct(tmp_path):
    ws = {"regels/AR-001.yaml": ["[L3] test"]}
    gen_kwaliteit(tmp_path, ws)
    content = (tmp_path / "kwaliteit.html").read_text()
    assert 'href="regels/AR-001.html"' in content


def test_gen_kwaliteit_onbekend_pad_geen_link(tmp_path):
    ws = {"overig/onbekend.yaml": ["[L3] test"]}
    gen_kwaliteit(tmp_path, ws)
    content = (tmp_path / "kwaliteit.html").read_text()
    assert "overig/onbekend.yaml" in content
    assert 'href=""' not in content


def test_gen_kwaliteit_filter_script_aanwezig(tmp_path):
    gen_kwaliteit(tmp_path, {})
    content = (tmp_path / "kwaliteit.html").read_text()
    assert "filterInput" in content
    assert "MiniSearch" in content


def test_gen_kwaliteit_toont_oplossing_als_meta_aanwezig(tmp_path):
    ws = {"begrippen/test.yaml": ["[L3] definitie.kern is leeg — gebruik /begrip"]}
    meta = [{"sleutel": "definitie.kern is leeg", "titel": "Kern ontbreekt", "uitleg": "Uitleg hier.", "stappen": ["Stap 1", "Stap 2"], "commando": "/begrip"}]
    gen_kwaliteit(tmp_path, ws, meta)
    content = (tmp_path / "kwaliteit.html").read_text()
    assert "oplossing-blok" in content
    assert "Kern ontbreekt" in content
    assert "Stap 1" in content
    assert "Skill" in content


def test_gen_kwaliteit_geen_oplossing_zonder_meta(tmp_path):
    ws = {"begrippen/test.yaml": ["[L3] definitie.kern is leeg"]}
    gen_kwaliteit(tmp_path, ws)
    content = (tmp_path / "kwaliteit.html").read_text()
    assert "oplossing-blok" not in content


def test_gen_kwaliteit_oplossing_zonder_commando(tmp_path):
    ws = {"begrippen/test.yaml": ["[L3] alle relaties leeg (is-een, heeft, leidt-tot)"]}
    meta = [{"sleutel": "alle relaties leeg", "titel": "Geen relaties", "uitleg": "U.", "stappen": ["Stap"]}]
    gen_kwaliteit(tmp_path, ws, meta)
    content = (tmp_path / "kwaliteit.html").read_text()
    assert "oplossing-blok" in content
    assert "oplossing-commando" not in content
