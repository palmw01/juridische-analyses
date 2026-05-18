#!/usr/bin/env python3
"""Extraheer en valideer een `/annoteer`-commando uit een GitHub issue body.

Wordt aangeroepen vanuit `.github/workflows/annoteer.yml`. Faalt hard bij
elke afwijking van het toegestane commandopatroon zodat alleen exact ons
syntax-patroon wordt doorgegeven aan de Claude-runner. Lees `ISSUE_BODY`
en `ISSUE_NUMBER` uit de omgeving en schrijf `command=` en `branch=` naar
`$GITHUB_OUTPUT` (of stdout bij lokale aanroep).
"""
from __future__ import annotations

import os
import re
import sys

# ---------------------------------------------------------------------------
# Patronen
# ---------------------------------------------------------------------------

# Drie toegestane vormen — geen variaties, geen optionele flags.
COMMANDO_PATROON = re.compile(
    r"^/annoteer\s+"
    r"(?:"
        r"art\.\s+(?P<artikel>[A-Za-z0-9:.]+)(?:\s+lid\s+(?P<lid>[A-Za-z0-9]+))?"
        r"|sectie\s+(?P<sectie>[A-Za-z0-9_.-]+)"
    r")"
    r"\s+(?P<wet>[A-Za-z][A-Za-z0-9 .]{0,40}[A-Za-z0-9])$"
)

FENCE_PATROON = re.compile(r"```(?:[A-Za-z0-9_-]+)?\s*\n?(.*?)```", re.DOTALL)

MAX_BODY = 20_000
MAX_COMMANDO = 200


class ParseError(ValueError):
    """Het commando voldoet niet aan het strikte patroon."""


# ---------------------------------------------------------------------------
# Extractie
# ---------------------------------------------------------------------------

def _eerste_annoteer_regel(blok: str) -> str | None:
    for regel in blok.splitlines():
        gestript = regel.strip()
        if gestript.startswith("/annoteer"):
            return gestript
    return None


def extraheer_commando(body: str) -> str:
    """Vind het eerste `/annoteer`-commando in `body`.

    Voorkeursbron is een gefenced code-blok; valt anders terug op de eerste
    losse regel die met `/annoteer` begint.
    """
    if not body:
        raise ParseError("Lege issue-body — geen /annoteer-commando gevonden.")
    if len(body) > MAX_BODY:
        raise ParseError(f"Issue-body is te lang ({len(body)} tekens; max {MAX_BODY}).")
    for blok in FENCE_PATROON.findall(body):
        regel = _eerste_annoteer_regel(blok)
        if regel is not None:
            if len(regel) > MAX_COMMANDO:
                raise ParseError(f"Commando is te lang ({len(regel)} tekens; max {MAX_COMMANDO}).")
            return regel
    regel = _eerste_annoteer_regel(body)
    if regel is None:
        raise ParseError("Geen /annoteer-commando gevonden in issue-body.")
    if len(regel) > MAX_COMMANDO:
        raise ParseError(f"Commando is te lang ({len(regel)} tekens; max {MAX_COMMANDO}).")
    return regel


# ---------------------------------------------------------------------------
# Validatie + branchnaam
# ---------------------------------------------------------------------------

def valideer_commando(commando: str) -> re.Match[str]:
    match = COMMANDO_PATROON.match(commando)
    if match is None:
        raise ParseError(f"Commando voldoet niet aan toegestaan patroon: {commando!r}")
    return match


def _slug(tekst: str) -> str:
    schoon = re.sub(r"[^A-Za-z0-9-]+", "-", tekst.lower()).strip("-")
    return schoon[:40] or "x"


def bouw_branch(match: re.Match[str], issue_nummer: str) -> str:
    nr = re.sub(r"[^0-9]", "", issue_nummer or "")[:6] or "0"
    sectie = match.group("sectie")
    if sectie:
        return f"claude/annoteer-sectie-{_slug(sectie)}-issue{nr}"
    artikel = _slug(match.group("artikel"))
    lid = match.group("lid")
    if lid:
        return f"claude/annoteer-art{artikel}-lid{_slug(lid)}-issue{nr}"
    return f"claude/annoteer-art{artikel}-issue{nr}"


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def schrijf_outputs(commando: str, branch: str, output_pad: str | None) -> None:
    regels = [f"command={commando}\n", f"branch={branch}\n"]
    if not output_pad:
        sys.stdout.writelines(regels)
        return
    with open(output_pad, "a", encoding="utf-8") as fh:
        fh.writelines(regels)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main(env: dict[str, str] | None = None) -> int:
    omgeving = env if env is not None else os.environ
    body = omgeving.get("ISSUE_BODY", "")
    nummer = omgeving.get("ISSUE_NUMBER", "0")
    try:
        commando = extraheer_commando(body)
        match = valideer_commando(commando)
    except ParseError as exc:
        sys.stderr.write(f"::error::{exc}\n")
        return 1
    branch = bouw_branch(match, nummer)
    schrijf_outputs(commando, branch, omgeving.get("GITHUB_OUTPUT"))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
