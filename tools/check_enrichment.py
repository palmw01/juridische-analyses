"""
Detecteert enrichment-kandidaten in de begrippen-vault en werkt rapporten/enrichment-queue.json bij.

Een begrip is een enrichment-kandidaat als:
  1. Het 2+ markeringen heeft (hergebruik vanuit meerdere annotaties)
  2. De primaire markeringen conflicterende tekst-waarden hebben
  3. Status 'te-verrijken' heeft
  4. Een of meer markeringen niet zijn bevestigd (bevestigd: false)

Het script voegt alleen nieuw ontdekte kandidaten toe — bestaande queue-items worden nooit overschreven.

Gebruik:
    cd vault-root/
    tools/.venv/bin/python tools/check_enrichment.py [opties]

Opties:
    --vault-root PATH   Pad naar de vault-root (default: huidige map)
    --dry-run           Toon kandidaten zonder de queue bij te werken
    --since YYYY-MM-DD  Verwerk alleen begrippen bijgewerkt na deze datum (op basis van geldigheid-van)
    --verbose           Toon ook begrippen die al in de queue zitten
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Trigger-detectie
# ---------------------------------------------------------------------------

class Trigger:
    MEERDERE_MARKERINGEN = "meerdere-markeringen"
    CONFLICTERENDE_PRIMAIR = "conflicterende-primaire-markeringen"
    STATUS_TE_VERRIJKEN = "status-te-verrijken"
    ONBEVESTIGD = "onbevestigde-markering"
    DEFINITIE_BASIS_VERLOPEN = "definitie-basis-verlopen"


def detecteer_triggers(fm: dict) -> list[str]:
    triggers = []
    markeringen = fm.get("markeringen") or []
    status = fm.get("status", "")
    definitie = fm.get("definitie", "")
    definitie_gebaseerd_op = set(fm.get("definitie-gebaseerd-op") or [])

    if len(markeringen) >= 2:
        triggers.append(Trigger.MEERDERE_MARKERINGEN)

    primaire = [m for m in markeringen if m.get("bijdrage") == "primair"]
    primaire_teksten = {m.get("tekst", "").strip().lower() for m in primaire}
    if len(primaire) >= 2 and len(primaire_teksten) > 1:
        triggers.append(Trigger.CONFLICTERENDE_PRIMAIR)

    if status == "te-verrijken":
        triggers.append(Trigger.STATUS_TE_VERRIJKEN)

    if any(not m.get("bevestigd", True) for m in markeringen):
        triggers.append(Trigger.ONBEVESTIGD)

    if definitie and definitie_gebaseerd_op:
        markering_ids = {m.get("markering-id") for m in markeringen}
        if not definitie_gebaseerd_op.issubset(markering_ids):
            verlopen = definitie_gebaseerd_op - markering_ids
            if verlopen:
                triggers.append(Trigger.DEFINITIE_BASIS_VERLOPEN)

    return triggers


# ---------------------------------------------------------------------------
# Delta-analyse en advies genereren (heuristisch)
# ---------------------------------------------------------------------------

def genereer_delta_analyse(fm: dict, triggers: list[str]) -> str:
    markeringen = fm.get("markeringen") or []
    begripsnaam = fm.get("begripsnaam", "")
    onderdelen = []

    if Trigger.MEERDERE_MARKERINGEN in triggers:
        bronnen = [m.get("bron-annotatie-id", "?") for m in markeringen]
        bijdragen = [m.get("bijdrage", "?") for m in markeringen]
        primaire = [m for m in markeringen if m.get("bijdrage") == "primair"]
        context = [m for m in markeringen if m.get("bijdrage") == "context"]
        aanvullend = [m for m in markeringen if m.get("bijdrage") == "aanvullend"]

        primaire_teksten = list({m.get("tekst", "").strip() for m in primaire})
        alle_teksten = list({m.get("tekst", "").strip() for m in markeringen})

        if Trigger.CONFLICTERENDE_PRIMAIR in triggers:
            onderdelen.append(
                f"Conflicterende primaire markeringen: "
                + " vs ".join(f"'{t[:60]}'" for t in primaire_teksten[:3])
                + f" (bronnen: {', '.join(m.get('bron-annotatie-id','?') for m in primaire)})."
                + " Definitie herschrijven of begrip afsplitsen."
            )
        elif len(alle_teksten) == 1:
            onderdelen.append(
                f"Identieke markering '{alle_teksten[0][:60]}' in "
                + ", ".join(bronnen)
                + f" (bijdragen: {', '.join(bijdragen)}). "
                + "Controleer of de definitie in beide contexten geldig is."
            )
        else:
            if context:
                ctx_bronnen = [m.get("bron-annotatie-id","?") for m in context]
                ctx_teksten = [m.get("tekst","")[:60] for m in context]
                onderdelen.append(
                    f"Context-markering(en) toegevoegd vanuit {', '.join(ctx_bronnen)}: "
                    + "; ".join(f"'{t}'" for t in ctx_teksten)
                    + ". Definitie-impact beperkt — verifieer of de context de definitie verrijkt."
                )
            if aanvullend:
                aav_bronnen = [m.get("bron-annotatie-id","?") for m in aanvullend]
                aav_teksten = [m.get("tekst","")[:60] for m in aanvullend]
                onderdelen.append(
                    f"Aanvullende markering(en) vanuit {', '.join(aav_bronnen)}: "
                    + "; ".join(f"'{t}'" for t in aav_teksten)
                    + ". Definitie uitbreiden?"
                )

    if Trigger.STATUS_TE_VERRIJKEN in triggers:
        onderdelen.append(f"Begrip '{begripsnaam}' heeft status 'te-verrijken' — herziening vereist.")

    if Trigger.ONBEVESTIGD in triggers:
        onbev = [m.get("bron-annotatie-id","?") for m in markeringen if not m.get("bevestigd", True)]
        onderdelen.append(
            f"Niet-bevestigde markering(en) vanuit: {', '.join(onbev)}. "
            "Juridische verificatie vereist vóór definitieve invulling."
        )

    if Trigger.DEFINITIE_BASIS_VERLOPEN in triggers:
        gebaseerd_op = set(fm.get("definitie-gebaseerd-op") or [])
        markering_ids = {m.get("markering-id") for m in markeringen}
        verlopen = gebaseerd_op - markering_ids
        onderdelen.append(
            f"Definitie-basis verwijst naar niet-bestaande markering-id(s): {', '.join(sorted(verlopen))}. "
            "definitie-gebaseerd-op bijwerken."
        )

    return " ".join(onderdelen) if onderdelen else "Automatisch gedetecteerd als enrichment-kandidaat."


def genereer_advies(fm: dict, triggers: list[str]) -> str:
    if Trigger.CONFLICTERENDE_PRIMAIR in triggers:
        return "conflicterend — afsplitsen overwegen of definitie herschrijven"
    if Trigger.STATUS_TE_VERRIJKEN in triggers:
        return "herziening vereist — definitie invullen of bijstellen"
    if Trigger.DEFINITIE_BASIS_VERLOPEN in triggers:
        return "definitie-gebaseerd-op bijwerken na markering-wijziging"
    if Trigger.ONBEVESTIGD in triggers:
        return "bevestiging vereist — markering(en) nog niet geverifieerd door jurist"

    markeringen = fm.get("markeringen") or []
    primaire = [m for m in markeringen if m.get("bijdrage") == "primair"]
    alle_teksten = {m.get("tekst","").strip().lower() for m in markeringen}
    if len(alle_teksten) == 1:
        return "context — definitie ongewijzigd"
    if all(m.get("bijdrage") in ("context", "aanvullend") for m in markeringen[1:]):
        return "context — definitie mogelijk uitbreiden"
    return "beoordelen — definitie controleren op volledigheid"


# ---------------------------------------------------------------------------
# Queue-beheer
# ---------------------------------------------------------------------------

def laad_queue(queue_pad: Path) -> list[dict]:
    if not queue_pad.exists():
        return []
    with queue_pad.open(encoding="utf-8") as f:
        return json.load(f)


def sla_queue_op(queue_pad: Path, queue: list[dict]) -> None:
    queue_pad.parent.mkdir(parents=True, exist_ok=True)
    with queue_pad.open("w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)
        f.write("\n")


def is_in_queue(begrip_id: str, queue: list[dict]) -> bool:
    return any(item.get("begrip-id") == begrip_id for item in queue)


def is_gesloten(begrip_id: str, queue: list[dict]) -> bool:
    for item in queue:
        if item.get("begrip-id") == begrip_id and item.get("beslissing"):
            return True
    return False


# ---------------------------------------------------------------------------
# Hoofdlogica
# ---------------------------------------------------------------------------

def scan_begrippen(
    vault_root: Path,
    queue: list[dict],
    since: date | None,
    verbose: bool,
) -> tuple[list[dict], list[str], list[str]]:
    """
    Retourneert (nieuwe_kandidaten, overgeslagen_ids, al_gesloten_ids).
    """
    begrippen_dir = vault_root / "begrippen"
    nieuwe_kandidaten: list[dict] = []
    overgeslagen: list[str] = []
    al_gesloten: list[str] = []
    vandaag = date.today().isoformat()

    if not begrippen_dir.exists():
        print(f"Waarschuwing: begrippen-map niet gevonden: {begrippen_dir}", file=sys.stderr)
        return nieuwe_kandidaten, overgeslagen, al_gesloten

    for yaml_file in sorted(begrippen_dir.glob("*.yaml")):
        with yaml_file.open(encoding="utf-8") as f:
            fm = yaml.safe_load(f)
        if not fm or not isinstance(fm, dict):
            continue

        begrip_id = fm.get("begrip-id") or yaml_file.stem
        begripsnaam = fm.get("begripsnaam", yaml_file.stem)

        # Since-filter op bestandswijzigingsdatum
        if since:
            try:
                mtime = date.fromtimestamp(yaml_file.stat().st_mtime)
                if mtime < since:
                    continue
            except (OSError, ValueError):
                pass

        triggers = detecteer_triggers(fm)
        if not triggers:
            continue

        if is_gesloten(begrip_id, queue):
            al_gesloten.append(begrip_id)
            if verbose:
                print(f"  gesloten (overgeslagen): {begrip_id}")
            continue

        if is_in_queue(begrip_id, queue):
            overgeslagen.append(begrip_id)
            if verbose:
                print(f"  al in queue (open): {begrip_id}")
            continue

        markeringen = fm.get("markeringen") or []
        delta = genereer_delta_analyse(fm, triggers)
        advies = genereer_advies(fm, triggers)

        kandidaat: dict[str, Any] = {
            "begrip-id": begrip_id,
            "begripsnaam": begripsnaam,
            "aangemeld-op": vandaag,
            "triggers": triggers,
            "markeringen-count": len(markeringen),
            "markeringen": [
                {
                    "markering-id": m.get("markering-id"),
                    "bron-annotatie-id": m.get("bron-annotatie-id"),
                    "tekst": m.get("tekst"),
                    "interpretatiemethode": m.get("interpretatiemethode"),
                    "bijdrage": m.get("bijdrage"),
                    "bevestigd": m.get("bevestigd"),
                    "bevestigd-op": m.get("bevestigd-op"),
                }
                for m in markeringen
            ],
            "delta-analyse": delta,
            "advies": advies,
        }
        nieuwe_kandidaten.append(kandidaat)

    return nieuwe_kandidaten, overgeslagen, al_gesloten


# ---------------------------------------------------------------------------
# Rapport afdrukken
# ---------------------------------------------------------------------------

def druk_rapport(
    nieuwe: list[dict],
    overgeslagen: list[str],
    gesloten: list[str],
    dry_run: bool,
    queue_pad: Path,
) -> None:
    print()
    print("=" * 60)
    print("Enrichment-scan rapport")
    print("=" * 60)

    if nieuwe:
        print(f"\nNieuwe kandidaten ({len(nieuwe)}):")
        for k in nieuwe:
            print(f"  + {k['begrip-id']}")
            print(f"    Triggers: {', '.join(k['triggers'])}")
            print(f"    Advies:   {k['advies']}")
    else:
        print("\nGeen nieuwe enrichment-kandidaten gevonden.")

    if overgeslagen:
        print(f"\nAl open in queue ({len(overgeslagen)}): {', '.join(overgeslagen)}")

    if gesloten:
        print(f"Al gesloten in queue ({len(gesloten)}): {', '.join(gesloten)}")

    print()
    if dry_run:
        print(f"Dry-run: geen wijzigingen geschreven naar {queue_pad}")
    elif nieuwe:
        print(f"Queue bijgewerkt: {queue_pad}")
        print(f"  +{len(nieuwe)} nieuw toegevoegd")
    else:
        print(f"Queue ongewijzigd: {queue_pad}")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detecteer enrichment-kandidaten in de begrippen-vault."
    )
    parser.add_argument(
        "--vault-root", default=".", help="Pad naar de vault-root (default: huidige map)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Toon kandidaten zonder de queue bij te werken"
    )
    parser.add_argument(
        "--since",
        metavar="YYYY-MM-DD",
        help="Verwerk alleen begrippen met geldigheid-van op of na deze datum",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Toon ook begrippen die al in de queue zitten"
    )
    args = parser.parse_args()

    vault_root = Path(args.vault_root).resolve()
    queue_pad = vault_root / "rapporten" / "enrichment-queue.json"

    since: date | None = None
    if args.since:
        try:
            since = date.fromisoformat(args.since)
        except ValueError:
            print(f"Fout: ongeldige datum '{args.since}'. Gebruik YYYY-MM-DD.", file=sys.stderr)
            return 1

    print(f"Vault:  {vault_root}")
    print(f"Queue:  {queue_pad}")
    if since:
        print(f"Since:  {since}")
    if args.dry_run:
        print("Modus:  dry-run (geen schrijfacties)")

    queue = laad_queue(queue_pad)
    print(f"Queue geladen: {len(queue)} item(s) ({sum(1 for i in queue if i.get('beslissing')) } gesloten)")

    nieuwe, overgeslagen, gesloten = scan_begrippen(vault_root, queue, since, args.verbose)

    if nieuwe and not args.dry_run:
        bijgewerkte_queue = queue + nieuwe
        sla_queue_op(queue_pad, bijgewerkte_queue)

    druk_rapport(nieuwe, overgeslagen, gesloten, args.dry_run, queue_pad)

    return 0 if not nieuwe else 2  # exit 2 = nieuwe kandidaten gevonden (informatief, geen fout)


if __name__ == "__main__":
    sys.exit(main())
