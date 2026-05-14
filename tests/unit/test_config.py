import re

import pytest

from sitegen.config import slugify, _text_color_for_bg


# ---------- slugify ----------

@pytest.mark.parametrize("invoer,verwacht", [
    ("belastingschuldige", "belastingschuldige"),
    ("Belastingschuldige", "belastingschuldige"),
    # spaties worden verwijderd (niet vervangen door koppelteken)
    ("loon uit dienstbetrekking", "loonuitdienstbetrekking"),
    ("art. 9 IW 1990", "art9iw1990"),
    # '/' en '_' worden wél omgezet naar koppelteken
    ("BWBR0004770/art9/lid1", "bwbr0004770-art9-lid1"),
    ("ABC_DEF", "abc-def"),
    ("", ""),
    ("---", "---"),
    ("123", "123"),
])
def test_slugify_cases(invoer, verwacht):
    assert slugify(invoer) == verwacht


def test_slugify_idempotent():
    for s in ["Belastingschuldige", "Art. 9 IW 1990", "BWBR0004770/art9"]:
        assert slugify(slugify(s)) == slugify(s)


def test_slugify_alleen_geldige_tekens():
    for s in ["Loon uit dienstbetrekking", "art. 9 lid 1", "BWBR0004770/art9/lid1"]:
        assert re.fullmatch(r"[a-z0-9-]*", slugify(s))


# ---------- _text_color_for_bg ----------

@pytest.mark.parametrize("hex_kleur,verwacht", [
    # lum = 109.6 < 140 → donker → witte tekst
    ("#4472C4", ",color:#fff"),
    # lum = 143.1 > 140 → licht → zwarte tekst (geen modifier)
    ("#70AD47", ""),
    # lum = 188.9 > 140 → licht → zwarte tekst
    ("#FFC000", ""),
    # lum = 255 > 140 → wit → zwarte tekst
    ("#FFFFFF", ""),
    # lum = 0 < 140 → zwart → witte tekst
    ("#000000", ",color:#fff"),
])
def test_text_color_for_bg(hex_kleur, verwacht):
    assert _text_color_for_bg(hex_kleur) == verwacht


def test_text_color_deterministisch():
    for kleur in ("#4472C4", "#FFC000", "#000000"):
        assert _text_color_for_bg(kleur) == _text_color_for_bg(kleur)


def test_text_color_driecijferige_hex():
    # #fff == #ffffff → lum = 255 > 140 → zwarte tekst (geen modifier)
    assert _text_color_for_bg("#fff") == ""


def test_text_color_te_kort_geeft_leeg():
    # len(h) != 6 na lstrip → early return ""
    assert _text_color_for_bg("#AB") == ""
    assert _text_color_for_bg("") == ""
