"""Schrijf een Markdown-rapport voor één /wetsanalyse-run.

Wordt aangeroepen door de orchestrator-skill aan het einde van een run.
Gebruikt het bestaande validatie-rapport (rapporten/validatie-rapport.json)
en een opgegeven stap-status (JSON) om een per-run rapport te genereren met
Mermaid-diagram, gewijzigde-bestanden-lijst en openstaande punten.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from jas_index_lib import load_json, load_yaml

STATUS_KLEUR = {
    "completed": "fill:#c8e6c9,stroke:#2e7d32",  # groen
    "warning":   "fill:#fff9c4,stroke:#f9a825",  # oranje
    "blocked":   "fill:#ffcdd2,stroke:#c62828",  # rood
    "skipped":   "fill:#e0e0e0,stroke:#616161",  # grijs
    "pending":   "fill:#e1f5fe,stroke:#0277bd",  # lichtblauw
}

STATUS_ICON = {
    "completed": "✓",
    "warning":   "⚠",
    "blocked":   "✗",
    "skipped":   "○",
    "pending":   "·",
}


def lees_stap_status(pad: Path) -> list[dict]:
    """Lees een JSON-bestand met een lijst {name, status, summary?}."""
    data = load_json(pad, silent=False)
    if not isinstance(data, list):
        raise ValueError(f"{pad}: verwacht een JSON-lijst van stap-objecten")
    return data


def bouw_mermaid(stappen: list[dict]) -> str:
    """Bouw een Mermaid graph LR met node per stap."""
    lijnen = ["```mermaid", "graph LR"]
    vorige: str | None = None
    for i, stap in enumerate(stappen):
        node_id = f"S{i}"
        naam = stap.get("name", f"stap-{i}").replace('"', "'")
        icon = STATUS_ICON.get(stap.get("status", "pending"), "·")
        lijnen.append(f'    {node_id}["{icon} {naam}"]')
        if vorige is not None:
            lijnen.append(f"    {vorige} --> {node_id}")
        vorige = node_id
    # classDef per status
    for status, kleur in STATUS_KLEUR.items():
        lijnen.append(f"    classDef {status} {kleur}")
    for i, stap in enumerate(stappen):
        status = stap.get("status", "pending")
        lijnen.append(f"    class S{i} {status}")
    lijnen.append("```")
    return "\n".join(lijnen)


def lees_validatie_rapport(project_root: Path) -> dict:
    """Lees rapporten/validatie-rapport.json indien aanwezig."""
    pad = project_root / "rapporten" / "validatie-rapport.json"
    if not pad.exists():
        return {"l1": 0, "l2": 0, "l3": 0, "bestanden": 0, "details": []}
    data = load_json(pad, silent=True) or {}
    fouten = data.get("blokkeerfouten", [])
    waarschuwingen = data.get("waarschuwingen", [])
    return {
        "l1": sum(1 for f in fouten if f.get("laag") == "L1"),
        "l2": sum(1 for f in fouten if f.get("laag") == "L2"),
        "l3": len(waarschuwingen),
        "bestanden": data.get("geslaagd", 0),
        "details": waarschuwingen,
    }


def tel_open_velden(project_root: Path) -> dict:
    """Tel ?-velden, onbevestigde markeringen en nog niet-gevalideerde artefacten."""
    open_voorspellingen = 0
    onbevestigde_markeringen = 0
    te_valideren = 0
    validaties_dir = project_root / "validaties"
    if validaties_dir.exists():
        for yaml_file in validaties_dir.glob("*.yaml"):
            data = load_yaml(yaml_file) or {}
            for kolom in data.get("kolommen") or []:
                if kolom.get("is-voorspelling-juist") == "?":
                    open_voorspellingen += 1
            if not data.get("validatie"):
                te_valideren += 1
    begrippen_dir = project_root / "begrippen"
    if begrippen_dir.exists():
        for yaml_file in begrippen_dir.glob("*.yaml"):
            data = load_yaml(yaml_file) or {}
            for m in data.get("markeringen") or []:
                if not m.get("bevestigd"):
                    onbevestigde_markeringen += 1
            if not data.get("validatie"):
                te_valideren += 1
    return {
        "open_voorspellingen": open_voorspellingen,
        "onbevestigde_markeringen": onbevestigde_markeringen,
        "te_valideren": te_valideren,
    }


def schrijf_rapport(
    *,
    output_pad: Path,
    artikel: str,
    lid: str,
    wet: str,
    bwb_id: str,
    peildatum: str,
    gestart_op: str,
    klaar_op: str,
    stappen: list[dict],
    gewijzigde_bestanden: list[str],
    validatie: dict,
    open_velden: dict,
) -> None:
    mermaid = bouw_mermaid(stappen)
    details_l3 = "\n".join(
        f"- `{w.get('bestand', '?')}` — {w.get('boodschap', '')}"
        for w in (validatie.get("details") or [])[:20]
    ) or "_(geen L3-waarschuwingen)_"
    rest_count = max(0, len(validatie.get("details") or []) - 20)
    if rest_count:
        details_l3 += f"\n- _(+{rest_count} verdere L3-meldingen — zie rapporten/validatie-rapport.md)_"

    bestanden_lijst = "\n".join(f"- `{p}`" for p in gewijzigde_bestanden) or "_(geen)_"
    stap_lijst = "\n".join(
        f"- {STATUS_ICON.get(s.get('status', 'pending'), '·')} **{s.get('name', '?')}** — "
        f"{s.get('summary', s.get('status', 'pending'))}"
        for s in stappen
    )

    rapport = f"""# Wetsanalyse-run — art. {artikel} lid {lid} {wet}

| Veld | Waarde |
|------|--------|
| Artikel | {artikel} lid {lid} {wet} ({bwb_id}) |
| Peildatum | {peildatum} |
| Gestart op | {gestart_op} |
| Klaar op | {klaar_op} |

## Keten

{mermaid}

### Stap-overzicht

{stap_lijst}

## Gewijzigde bestanden

{bestanden_lijst}

## Validatie

- L1 blokkeerfouten: **{validatie['l1']}**
- L2 integriteitsfouten: **{validatie['l2']}**
- L3 waarschuwingen: **{validatie['l3']}**
- Aantal valide bestanden: {validatie['bestanden']}

### L3-meldingen

{details_l3}

## Openstaande punten

- `?`-velden in voorbeeldreeksen (juridisch oordeel nodig): **{open_velden['open_voorspellingen']}**
- Onbevestigde markeringen (A4-validatie nodig): **{open_velden['onbevestigde_markeringen']}**
- Artefacten zonder menselijk validatie-blok (nog te beoordelen): **{open_velden['te_valideren']}**

## Volgende stappen

- Menselijke validatie: draai `/beoordeel art. {artikel} lid {lid} {wet}` om de producten te beoordelen en het oordeel (jurist/regelanalist) vast te leggen.
- Reviewer-actie: beoordeel `?`-velden in `validaties/`.
- Domeinexpert: bevestig markeringen in `begrippen/` waar `bevestigd: false`.
- Bij L1/L2-fouten: zie `rapporten/validatie-rapport.md` voor details en herstel.
"""

    output_pad.parent.mkdir(parents=True, exist_ok=True)
    output_pad.write_text(rapport, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Genereer Markdown-rapport voor één /wetsanalyse-run"
    )
    parser.add_argument("--project-dir", default=".", help="Project-root")
    parser.add_argument("--artikel", required=True)
    parser.add_argument("--lid", required=True)
    parser.add_argument("--wet", required=True)
    parser.add_argument("--bwb-id", required=True)
    parser.add_argument("--peildatum", required=True)
    parser.add_argument(
        "--steps-json",
        required=True,
        help="Pad naar JSON-bestand met lijst van {name, status, summary?}",
    )
    parser.add_argument(
        "--gewijzigde-bestanden",
        default="",
        help="Door komma's gescheiden lijst van bestanden (output van git diff --name-only)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output-pad; default rapporten/runs/run-{datum}-{slug}.md",
    )
    parser.add_argument("--gestart-op", default=None)
    args = parser.parse_args(argv)

    project_root = Path(args.project_dir).resolve()
    stappen = lees_stap_status(Path(args.steps_json).resolve())

    nu = datetime.now()
    klaar_op = nu.strftime("%Y-%m-%d %H:%M")
    gestart_op = args.gestart_op or klaar_op
    slug = f"art{args.artikel}-lid{args.lid}"

    if args.output:
        output_pad = Path(args.output).resolve()
    else:
        bestand = f"run-{nu.strftime('%Y-%m-%d-%H%M')}-{slug}.md"
        output_pad = project_root / "rapporten" / "runs" / bestand

    validatie = lees_validatie_rapport(project_root)
    open_velden = tel_open_velden(project_root)
    gewijzigd = [b for b in args.gewijzigde_bestanden.split(",") if b.strip()]

    schrijf_rapport(
        output_pad=output_pad,
        artikel=args.artikel,
        lid=args.lid,
        wet=args.wet,
        bwb_id=args.bwb_id,
        peildatum=args.peildatum,
        gestart_op=gestart_op,
        klaar_op=klaar_op,
        stappen=stappen,
        gewijzigde_bestanden=gewijzigd,
        validatie=validatie,
        open_velden=open_velden,
    )

    print(f"Rapport geschreven naar: {output_pad}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
