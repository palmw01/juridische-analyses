#!/usr/bin/env python3
"""
extract_kruisrefs.py — Extraheer kruisreferenties uit een genormaliseerde bronnen-JSON.

Implementeert het volledige JCI URI-extractieprotocol (JAS v1.0.10).

Gebruik:
    python tools/extract_kruisrefs.py --input bronnen/BWBR0004770/art9.json
    python tools/extract_kruisrefs.py --input bronnen/BWBR0004770/art9.json --bron-lid 1
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# BWB-mapping
# ---------------------------------------------------------------------------

BWB_MAPPING = {
    "BWBR0004770": "IW 1990",
    "BWBR0002226": "AWR",
    "BWBR0005537": "Awb",
    "BWBR0008003": "LI 2008",
    "BWBR0003738": "UBIB 1990",
    "BWBR0011987": "URIW 1990",
}

WET_NAAR_BWB: dict[str, str] = {v: k for k, v in BWB_MAPPING.items()}

# ---------------------------------------------------------------------------
# Rangnamentabel
# ---------------------------------------------------------------------------

RANGNAM: dict[str, int] = {
    "eerste": 1, "tweede": 2, "derde": 3, "vierde": 4, "vijfde": 5,
    "zesde": 6, "zevende": 7, "achtste": 8, "negende": 9, "tiende": 10,
    "elfde": 11, "twaalfde": 12, "dertiende": 13, "veertiende": 14,
    "vijftiende": 15, "zestiende": 16, "zeventiende": 17, "achttiende": 18,
    "negentiende": 19, "twintigste": 20,
}

# ---------------------------------------------------------------------------
# Reguliere expressies
# ---------------------------------------------------------------------------

# Fase 1: JCI Markdown-links
RE_JCI_LINK = re.compile(r'\[([^\]]+)\]\(jci1\.3:c:([^)]+)\)')

# Lidnummer-patronen
RE_LID_REEKS = re.compile(
    r'leden\s+(\d+)\s+(?:en|tot en met)\s+(\d+)', re.IGNORECASE
)
RE_LID_GETAL = re.compile(r'lid\s+(\d+)', re.IGNORECASE)

# Rangnam + lid (bijv. "derde lid", "vijfde lid")
_rangnam_pattern = '|'.join(re.escape(k) for k in RANGNAM)
RE_LID_RANG = re.compile(
    rf'({_rangnam_pattern})\s+lid', re.IGNORECASE
)

# Meerdere rangnames voor hetzelfde artikel (bijv. "derde, vijfde en negende lid")
RE_LID_MULTI_RANG = re.compile(
    rf'((?:(?:{_rangnam_pattern})(?:\s*,\s*|\s+en\s+))+(?:{_rangnam_pattern}))\s+lid',
    re.IGNORECASE,
)

# Fase 2: platte-tekst artikel-referenties
RE_ARTIKEL_PLAIN = re.compile(
    r'artikel\s+[0-9]+[a-z]?(?:\s*,\s*[0-9]+[a-z]?)*(?:\s+en\s+[0-9]+[a-z]?)?',
    re.IGNORECASE,
)

# Wetnaam-kwalificatie in de zin ("van de Awb", "van het Besluit X")
RE_WETKWAL = re.compile(
    r'\bvan\s+(?:de|het|[A-Z])\s*([A-Za-z0-9 \-]+?)(?=[,\.;]|$|\s{2})',
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# JCI URI-parser
# ---------------------------------------------------------------------------

def parse_jci_uri(uri: str) -> dict:
    """
    Parse een JCI URI van de vorm jci1.3:c:{bwbId}&{param}={waarde}&...

    Retourneert: {"bwb_id": str, "artikel": str | None}
    Negeert: hoofdstuk=, afdeling=, paragraaf=, z=, g=
    """
    # Haal alles na 'c:' op
    after_c = uri.split("c:", 1)[-1] if "c:" in uri else uri

    # bwbId is alles tot de eerste '&'; ontbreekt '&' → alles
    if "&" in after_c:
        bwb_id, rest = after_c.split("&", 1)
    else:
        return {"bwb_id": after_c, "artikel": None}

    # Zoek artikel=-parameter
    artikel = None
    for param in rest.split("&"):
        if param.startswith("artikel="):
            artikel = param[len("artikel="):].strip()
            break

    return {"bwb_id": bwb_id.strip(), "artikel": artikel}


# ---------------------------------------------------------------------------
# Hulpfuncties voor lidextractie
# ---------------------------------------------------------------------------

def extract_lids_from_display(display: str) -> list[str | None]:
    """
    Extraheer lidnummer(s) uit de display-tekst van een JCI-link.

    Patronen in volgorde (zie protocol):
    1. Reeks: "leden 2 en 5" / "leden 2 tot en met 5"
    2. Meerdere rangnames: "derde, vijfde en negende lid"
    3. Enkelvoudige rangname: "derde lid"
    4. Getal: "lid 3"
    5. Geen match → [None]

    Retourneert een lijst van lid-strings (als ordinaal-getal-string, bijv. "3").
    """
    # Patroon 1: reeks
    m = RE_LID_REEKS.search(display)
    if m:
        start, eind = int(m.group(1)), int(m.group(2))
        return [str(i) for i in range(start, eind + 1)]

    # Patroon 2 (meerdere rangnames) + Patroon 3 (enkelvoudig)
    rangmatches = RE_LID_RANG.findall(display)
    if rangmatches:
        return [str(RANGNAM[r.lower()]) for r in rangmatches]

    # Patroon 4: lid N
    m = RE_LID_GETAL.search(display)
    if m:
        return [m.group(1)]

    return [None]


def extract_artikelnrs_from_display(display: str, default_artikel: str | None) -> list[str]:
    """
    Extraheer één of meerdere artikelnummers uit de display-tekst.

    "artikelen X en Y" of "artikelen X, Y en Z" → lijst per artikel.
    Geen meervoud → [default_artikel] (kan None zijn → [""] als fallback).
    """
    # Meerdere artikelen?
    m = re.search(
        r'artikelen\s+([0-9]+[a-z]?)(?:\s*,\s*([0-9]+[a-z]?))*(?:\s+en\s+([0-9]+[a-z]?))?',
        display,
        re.IGNORECASE,
    )
    if m:
        nrs = re.findall(r'[0-9]+[a-z]?', display[m.start():m.end()])
        return nrs if nrs else [default_artikel or ""]

    return [default_artikel or ""] if default_artikel else []


# ---------------------------------------------------------------------------
# Fase 1: JCI Markdown-links
# ---------------------------------------------------------------------------

def fase1(tekst: str, bron_bwb_id: str, bron_artikel: str, bron_lid: str) -> list[dict]:
    records: list[dict] = []

    for m in RE_JCI_LINK.finditer(tekst):
        display = m.group(1)
        uri = m.group(2)

        parsed = parse_jci_uri(uri)
        doel_bwb_id = parsed["bwb_id"]
        doel_artikel_uri = parsed["artikel"]

        # confidence
        confidence = 1.0 if doel_artikel_uri else 0.8

        # wetnaam
        doel_wet = BWB_MAPPING.get(doel_bwb_id, display)

        # artikelnummers
        artikel_nrs = extract_artikelnrs_from_display(display, doel_artikel_uri)

        # lidnummers
        lids = extract_lids_from_display(display)

        for art_nr in (artikel_nrs or [doel_artikel_uri]):
            for lid in lids:
                record = _maak_record(
                    bron_bwb_id=bron_bwb_id,
                    bron_artikel=bron_artikel,
                    bron_lid=bron_lid,
                    doel_bwb_id=doel_bwb_id,
                    doel_wet=doel_wet,
                    doel_artikel=art_nr,
                    doel_lid=lid,
                    ruwe_tekst=display,
                    confidence=confidence,
                )
                records.append(record)

    return records


# ---------------------------------------------------------------------------
# Fase 2: platte tekst
# ---------------------------------------------------------------------------

def _zin_van(tekst: str, match_start: int, match_end: int) -> str:
    """Retourneer de zin rondom de match (afgebakend door . ! ? of regeleindes)."""
    zin_einde_re = re.compile(r'[.!?\n]')

    # Zoek begin van de zin
    begin = match_start
    for i in range(match_start - 1, -1, -1):
        if tekst[i] in '.!?\n':
            begin = i + 1
            break

    # Zoek einde van de zin
    einde = match_end
    m_einde = zin_einde_re.search(tekst, match_end)
    if m_einde:
        einde = m_einde.start()
    else:
        einde = len(tekst)

    return tekst[begin:einde].strip()


def _zoek_wet_in_zin(zin: str) -> str | None:
    """
    Zoek wetkwalificatie ("van de Awb", "van het Besluit X") in een zin.

    Retourneert de BWB-id als gevonden in de mapping, anders None.
    """
    # Zoek "van de/het <wetnaam>" of "van <AFKORTING>"
    m = re.search(
        r'\bvan\s+(?:de\s+|het\s+)?([A-Za-z][A-Za-z0-9 \-]{1,60}?)(?=[,\.;:\s]|$)',
        zin,
        re.IGNORECASE,
    )
    if not m:
        return None

    kandidaat = m.group(1).strip()

    # Directe match in WET_NAAR_BWB (afkortingen en volledige namen)
    if kandidaat in WET_NAAR_BWB:
        return WET_NAAR_BWB[kandidaat]

    # Probeer gedeeltelijke match (kandidaat start de sleutel)
    for naam, bwb in WET_NAAR_BWB.items():
        if naam.lower().startswith(kandidaat.lower()) or kandidaat.lower().startswith(naam.lower()):
            return bwb

    return None


def fase2(
    tekst_origineel: str,
    jci_matches: list[re.Match],
    bron_bwb_id: str,
    bron_artikel: str,
    bron_lid: str,
) -> list[dict]:
    """Extraheer artikel-referenties uit tekst zonder JCI-links."""
    # Verwijder JCI-passages uit de tekst (vervang door spaties om positie te bewaren)
    tekst = tekst_origineel
    for m in sorted(jci_matches, key=lambda x: x.start(), reverse=True):
        tekst = tekst[:m.start()] + " " * (m.end() - m.start()) + tekst[m.end():]

    records: list[dict] = []

    for m in RE_ARTIKEL_PLAIN.finditer(tekst):
        match_tekst = m.group(0)
        zin = _zin_van(tekst, m.start(), m.end())

        # Wetnaam in dezelfde zin?
        doel_bwb_id_gevonden = _zoek_wet_in_zin(zin)
        if doel_bwb_id_gevonden:
            doel_bwb_id = doel_bwb_id_gevonden
            confidence = 0.9
        else:
            doel_bwb_id = bron_bwb_id
            confidence = 0.7

        doel_wet = BWB_MAPPING.get(doel_bwb_id, doel_bwb_id)

        # Artikelnummers uit de match
        art_nrs = re.findall(r'[0-9]+[a-z]?', match_tekst)

        # Lidnummer uit de zin
        lids = extract_lids_from_display(zin)

        for art_nr in art_nrs:
            for lid in lids:
                record = _maak_record(
                    bron_bwb_id=bron_bwb_id,
                    bron_artikel=bron_artikel,
                    bron_lid=bron_lid,
                    doel_bwb_id=doel_bwb_id,
                    doel_wet=doel_wet,
                    doel_artikel=art_nr,
                    doel_lid=lid,
                    ruwe_tekst=match_tekst,
                    confidence=confidence,
                )
                records.append(record)

    return records


# ---------------------------------------------------------------------------
# Record-constructie
# ---------------------------------------------------------------------------

def _maak_record(
    *,
    bron_bwb_id: str,
    bron_artikel: str,
    bron_lid: str,
    doel_bwb_id: str,
    doel_wet: str,
    doel_artikel: str | None,
    doel_lid: str | None,
    ruwe_tekst: str,
    confidence: float,
) -> dict:
    # Zelfverwijzing?
    if (
        doel_bwb_id == bron_bwb_id
        and doel_artikel == bron_artikel
        and doel_lid == bron_lid
    ):
        ruwe_tekst = "zelfverwijzing"

    # Richting
    richting = "intern" if doel_bwb_id == bron_bwb_id else "forward"

    return {
        "bron-bwb-id": bron_bwb_id,
        "bron-artikel": bron_artikel,
        "bron-lid": bron_lid,
        "doel-bwb-id": doel_bwb_id,
        "doel-wet": doel_wet,
        "doel-artikel": doel_artikel,
        "doel-lid": doel_lid,
        "ruwe-tekst": ruwe_tekst,
        "richting": richting,
        "confidence": confidence,
    }


# ---------------------------------------------------------------------------
# Deduplicatie
# ---------------------------------------------------------------------------

def dedupliceer(records: list[dict]) -> list[dict]:
    seen: set[tuple] = set()
    result: list[dict] = []
    for r in records:
        sleutel = (
            r["bron-bwb-id"],
            r["bron-artikel"],
            r["bron-lid"],
            r["doel-bwb-id"],
            r["doel-artikel"],
            r["doel-lid"],
        )
        if sleutel not in seen:
            seen.add(sleutel)
            result.append(r)
    return result


# ---------------------------------------------------------------------------
# Verwerk één lid
# ---------------------------------------------------------------------------

def verwerk_lid(lid_obj: dict, bron_bwb_id: str, bron_artikel: str) -> list[dict]:
    bron_lid = str(lid_obj.get("lid", ""))
    tekst = lid_obj.get("tekst", "")

    # Fase 1
    jci_matches = list(RE_JCI_LINK.finditer(tekst))
    records = fase1(tekst, bron_bwb_id, bron_artikel, bron_lid)

    # Fase 2
    records += fase2(tekst, jci_matches, bron_bwb_id, bron_artikel, bron_lid)

    return records


# ---------------------------------------------------------------------------
# Argumentverwerking en main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extraheer kruisreferenties uit een genormaliseerde bronnen-JSON."
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        metavar="FILE",
        help="Pad naar de bronnen-JSON (bijv. bronnen/BWBR0004770/art9.json)",
    )
    parser.add_argument(
        "--bron-lid",
        metavar="N",
        help="Verwerk alleen dit lid (bijv. 1); default: alle leden",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Fout: bestand niet gevonden: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Fout: kan JSON niet lezen — {exc}", file=sys.stderr)
        sys.exit(1)

    bron_bwb_id = data.get("bwb-id", "")
    bron_artikel = data.get("artikel", "")
    leden = data.get("leden", [])

    if not leden:
        print("[]")
        return

    # Filter op gevraagd lid
    if args.bron_lid is not None:
        leden = [l for l in leden if str(l.get("lid", "")) == args.bron_lid]
        if not leden:
            print(f"Fout: lid {args.bron_lid} niet gevonden in {input_path}", file=sys.stderr)
            sys.exit(1)

    alle_records: list[dict] = []
    for lid_obj in leden:
        alle_records.extend(verwerk_lid(lid_obj, bron_bwb_id, bron_artikel))

    alle_records = dedupliceer(alle_records)

    print(json.dumps(alle_records, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
