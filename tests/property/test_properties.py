"""Property-based tests met Hypothesis — invarianten over grote invoerdomeinen."""
import re

from hypothesis import given, settings
from hypothesis import strategies as st

from sitegen.config import slugify, _text_color_for_bg


# ---------- slugify ----------

@given(st.text(min_size=0, max_size=200))
def test_slugify_idempotent(tekst):
    """slugify(slugify(x)) == slugify(x) voor alle strings."""
    s = slugify(tekst)
    assert slugify(s) == s


@given(st.text(min_size=0, max_size=200))
def test_slugify_geldige_tekenset(tekst):
    """Output bevat uitsluitend a-z, 0-9 en koppeltekens."""
    assert re.fullmatch(r"[a-z0-9-]*", slugify(tekst))


@given(st.text(min_size=0, max_size=200))
def test_slugify_geeft_string(tekst):
    """slugify retourneert altijd een string."""
    assert isinstance(slugify(tekst), str)


@given(st.text(min_size=1, max_size=200, alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"))))
def test_slugify_niet_leeg_bij_ascii_alnum(tekst):
    """Als invoer uitsluitend ASCII letters/cijfers bevat, is de output niet leeg."""
    if any(c.isascii() and c.isalnum() for c in tekst):
        assert slugify(tekst) != ""


# ---------- _text_color_for_bg ----------

@given(st.integers(min_value=0, max_value=0xFFFFFF))
def test_text_color_deterministisch(kleur_int):
    """Dezelfde kleur geeft altijd dezelfde tekstkleur."""
    hex_kleur = f"#{kleur_int:06x}"
    assert _text_color_for_bg(hex_kleur) == _text_color_for_bg(hex_kleur)


@given(st.integers(min_value=0, max_value=0xFFFFFF))
def test_text_color_geeft_geldige_waarde(kleur_int):
    """Output is altijd "" of ",color:#fff" — nooit een andere waarde."""
    hex_kleur = f"#{kleur_int:06x}"
    result = _text_color_for_bg(hex_kleur)
    assert result in ("", ",color:#fff")
