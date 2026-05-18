"""Unit tests voor tools/parse_annoteer_issue.py."""
from __future__ import annotations

import pytest

from tools.parse_annoteer_issue import (
    MAX_BODY,
    MAX_COMMANDO,
    ParseError,
    bouw_branch,
    extraheer_commando,
    main,
    schrijf_outputs,
    valideer_commando,
)


# ===== extraheer_commando =====

def test_extraheer_uit_fenced_block():
    body = "Iets ervoor\n\n```\n/annoteer art. 9 lid 1 IW 1990\n```\n\nNawoord."
    assert extraheer_commando(body) == "/annoteer art. 9 lid 1 IW 1990"


def test_extraheer_uit_fenced_block_met_taalhint():
    body = "```bash\n/annoteer sectie par1-1 Leidraad Invordering 2008\n```"
    assert extraheer_commando(body) == "/annoteer sectie par1-1 Leidraad Invordering 2008"


def test_extraheer_uit_losse_regel_als_geen_fence():
    body = "Hallo\n/annoteer art. 9 IW 1990\nDoei"
    assert extraheer_commando(body) == "/annoteer art. 9 IW 1990"


def test_extraheer_pakt_eerste_fence_met_annoteer():
    body = "```\nirrelevant\n```\n```\n/annoteer art. 2 IW 1990\n```"
    assert extraheer_commando(body) == "/annoteer art. 2 IW 1990"


def test_extraheer_pakt_alleen_eerste_annoteer_regel_in_fence():
    body = "```\n/annoteer art. 9 IW 1990\n/annoteer art. 10 IW 1990\n```"
    assert extraheer_commando(body) == "/annoteer art. 9 IW 1990"


def test_extraheer_negeert_inline_in_tabelcel():
    body = "| col1 | /annoteer art. 9 IW 1990 |\n/annoteer art. 2 IW 1990"
    assert extraheer_commando(body) == "/annoteer art. 2 IW 1990"


def test_extraheer_leeg_geeft_fout():
    with pytest.raises(ParseError, match="Lege issue-body"):
        extraheer_commando("")


def test_extraheer_te_lang_geeft_fout():
    body = "x" * (MAX_BODY + 1)
    with pytest.raises(ParseError, match="te lang"):
        extraheer_commando(body)


def test_extraheer_geen_commando_geeft_fout():
    with pytest.raises(ParseError, match="Geen /annoteer"):
        extraheer_commando("Tekst zonder commando.")


def test_extraheer_commando_in_fence_te_lang_geeft_fout():
    lang = "/annoteer art. 9 lid 1 " + ("X" * MAX_COMMANDO) + " IW 1990"
    body = f"```\n{lang}\n```"
    with pytest.raises(ParseError, match="Commando is te lang"):
        extraheer_commando(body)


def test_extraheer_commando_in_losse_regel_te_lang_geeft_fout():
    lang = "/annoteer art. 9 lid 1 " + ("X" * MAX_COMMANDO) + " IW 1990"
    with pytest.raises(ParseError, match="Commando is te lang"):
        extraheer_commando(lang)


def test_extraheer_lege_fence_overgeslagen():
    body = "```\n\n```\n/annoteer art. 9 IW 1990"
    assert extraheer_commando(body) == "/annoteer art. 9 IW 1990"


# ===== valideer_commando =====

def test_valideer_art_zonder_lid():
    m = valideer_commando("/annoteer art. 9 IW 1990")
    assert m.group("artikel") == "9"
    assert m.group("lid") is None
    assert m.group("sectie") is None
    assert m.group("wet") == "IW 1990"


def test_valideer_art_met_lid():
    m = valideer_commando("/annoteer art. 9 lid 1 IW 1990")
    assert m.group("artikel") == "9"
    assert m.group("lid") == "1"


def test_valideer_artikel_met_letter():
    m = valideer_commando("/annoteer art. 2a IW 1990")
    assert m.group("artikel") == "2a"


def test_valideer_sectie():
    m = valideer_commando("/annoteer sectie par1-1 Leidraad Invordering 2008")
    assert m.group("sectie") == "par1-1"
    assert m.group("artikel") is None
    assert m.group("wet") == "Leidraad Invordering 2008"


def test_valideer_onbekend_subcommando_faalt():
    with pytest.raises(ParseError, match="patroon"):
        valideer_commando("/annoteer hoofdstuk 1 IW 1990")


def test_valideer_ander_slashcommando_faalt():
    with pytest.raises(ParseError, match="patroon"):
        valideer_commando("/begrip belastingschuldige")


def test_valideer_wet_zonder_letter_faalt():
    with pytest.raises(ParseError, match="patroon"):
        valideer_commando("/annoteer art. 9 1990")


def test_valideer_wet_met_shellinjectie_faalt():
    with pytest.raises(ParseError, match="patroon"):
        valideer_commando("/annoteer art. 9 IW 1990; rm -rf /")


# ===== bouw_branch =====

def test_bouw_branch_art_zonder_lid():
    m = valideer_commando("/annoteer art. 9 IW 1990")
    assert bouw_branch(m, "42") == "claude/annoteer-art9-issue42"


def test_bouw_branch_art_met_lid():
    m = valideer_commando("/annoteer art. 9 lid 1 IW 1990")
    assert bouw_branch(m, "42") == "claude/annoteer-art9-lid1-issue42"


def test_bouw_branch_sectie():
    m = valideer_commando("/annoteer sectie par1-1 Leidraad Invordering 2008")
    assert bouw_branch(m, "7") == "claude/annoteer-sectie-par1-1-issue7"


def test_bouw_branch_negeert_niet_cijfers_in_nummer():
    m = valideer_commando("/annoteer art. 9 IW 1990")
    assert bouw_branch(m, "PR-42abc") == "claude/annoteer-art9-issue42"


def test_bouw_branch_leeg_nummer_geeft_0():
    m = valideer_commando("/annoteer art. 9 IW 1990")
    assert bouw_branch(m, "") == "claude/annoteer-art9-issue0"


def test_bouw_branch_slug_kapt_te_lange_input():
    # artikel met heel veel tekens — slug max 40
    m = valideer_commando("/annoteer art. 2a IW 1990")
    assert "art2a" in bouw_branch(m, "1")


def test_bouw_branch_slug_fallback_naar_x():
    from tools.parse_annoteer_issue import _slug
    assert _slug("---") == "x"


# ===== schrijf_outputs =====

def test_schrijf_outputs_naar_bestand(tmp_path):
    pad = tmp_path / "out.txt"
    schrijf_outputs("/annoteer art. 9 IW 1990", "claude/x", str(pad))
    inhoud = pad.read_text(encoding="utf-8")
    assert "command=/annoteer art. 9 IW 1990\n" in inhoud
    assert "branch=claude/x\n" in inhoud


def test_schrijf_outputs_appendt(tmp_path):
    pad = tmp_path / "out.txt"
    pad.write_text("bestaand=1\n", encoding="utf-8")
    schrijf_outputs("/annoteer art. 9 IW 1990", "claude/x", str(pad))
    inhoud = pad.read_text(encoding="utf-8")
    assert inhoud.startswith("bestaand=1\n")
    assert "command=/annoteer art. 9 IW 1990\n" in inhoud


def test_schrijf_outputs_naar_stdout(capsys):
    schrijf_outputs("/annoteer art. 9 IW 1990", "claude/x", None)
    out = capsys.readouterr().out
    assert "command=/annoteer art. 9 IW 1990" in out
    assert "branch=claude/x" in out


# ===== main =====

def test_main_happy_path(tmp_path):
    output = tmp_path / "gh.out"
    env = {
        "ISSUE_BODY": "```\n/annoteer art. 9 lid 1 IW 1990\n```",
        "ISSUE_NUMBER": "42",
        "GITHUB_OUTPUT": str(output),
    }
    assert main(env) == 0
    inhoud = output.read_text(encoding="utf-8")
    assert "command=/annoteer art. 9 lid 1 IW 1990\n" in inhoud
    assert "branch=claude/annoteer-art9-lid1-issue42\n" in inhoud


def test_main_extractie_faalt_returncode_1(capsys):
    env = {"ISSUE_BODY": "", "ISSUE_NUMBER": "1"}
    assert main(env) == 1
    err = capsys.readouterr().err
    assert "::error::" in err
    assert "Lege issue-body" in err


def test_main_validatie_faalt_returncode_1(capsys):
    env = {"ISSUE_BODY": "/annoteer iets-onbekends X", "ISSUE_NUMBER": "1"}
    assert main(env) == 1
    err = capsys.readouterr().err
    assert "::error::" in err


def test_main_zonder_env_argument_gebruikt_os_environ(monkeypatch, tmp_path):
    output = tmp_path / "gh.out"
    monkeypatch.setenv("ISSUE_BODY", "/annoteer art. 9 IW 1990")
    monkeypatch.setenv("ISSUE_NUMBER", "5")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    assert main() == 0
    assert "branch=claude/annoteer-art9-issue5\n" in output.read_text(encoding="utf-8")
