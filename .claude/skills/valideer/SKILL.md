---
description: "A4b — voorbeeldreeks-YAML voor een bestaande afleidingsregel. Gebruik: /valideer AR-[bwb-id]-art[nr]-lid[l]-[seq]"
context: fork
agent: general-purpose
---

# /valideer — A4b voorbeeldreeks

Genereert een gestructureerde testmatrix (≥ 3 kolommen) voor één afleidingsregel. Output: één YAML-bestand in `validaties/`.

> Lees vóór elke run: `.claude/skills/kaders/voorbeeldreeks.md`.

**Scope:** de skill vult de structuur, invoerwaarden en — waar algoritmisch bepaalbaar — de verwachte uitvoer in. Juridische beoordeling (`is-voorspelling-juist: ja/nee`) blijft bij de gebruiker; de skill zet die op `?`.

## Trigger

```
/valideer AR-[bwb-id]-art[nr]-lid[l]-[seq]
```

Voorbeeld: `/valideer AR-BWBR0004770-art9-lid1-a`.

## Stappen

1. **Existentiecheck:**
   - `regels/[arg].yaml` moet bestaan; anders stop met foutmelding.
   - VR-id = vervang `AR-` door `VR-` in `[arg]`.
   - `validaties/VR-[id].yaml` mag nog niet bestaan; anders stop met melding.

2. **Regel en begrippen lezen:**
   - Lees `regels/[arg].yaml`. Extraheer `soort`, `invoer`, `uitvoer`, `formele-regel`, `peildatum`.
   - Voor elke `begrip-id` in `invoer` en `uitvoer`: lees het bijbehorende begrip-YAML uit `begrippen/`. Extraheer `soort` en `jas-klasse` voor typeafleiding (zie `kaders/voorbeeldreeks.md §Typeafleiding`).

3. **Kolommen genereren:**
   - Kies het testpatroon op basis van `regel.soort` (Beslissings-/Reken-/Beperkings-/Specialisatieregel) — zie `kaders/voorbeeldreeks.md §Testpatronen`.
   - Minimaal 3 kolommen: happy path, grensgeval, negatief geval.
   - Per kolom:
     - `label`: beschrijvend ("Happy path — invorderbaar", "Op de grens", …).
     - `invoer`: map `{ begrip-id: waarde }` voor alle invoerbegrippen.
     - `is-invoer-juist`: `"ja"` of `"nee"`.
     - `verwachte-uitvoer`: map `{ begrip-id: waarde }`. Algoritmisch bepaalbaar → concrete waarde; anders meest plausibele waarde.
     - `is-voorspelling-juist`:
       - `"nvt"` bij `is-invoer-juist: "nee"`.
       - `"?"` als juridisch oordeel nodig is.
       - `"ja"`/`"nee"` alleen bij exact wiskundige uitkomst of expliciete wettelijke regel.
     - `toelichting` waar nodig (grensgeval-motivering, open interpretatie).

4. **Bestand schrijven:**
   - Roep `stub_voorbeeldreeks(regel_id, naam, peildatum, aangemaakt_op)` aan en vul `kolommen[]`.
   - Schrijf met `schrijf_yaml(Path("validaties/VR-[id].yaml"), data)`.

5. **Valideren:**
   ```
   tools/.venv/bin/python tools/validate_note.py --file validaties/VR-[id].yaml --schema voorbeeldreeks
   ```

6. **Rapportage:**
   - Pad van het aangemaakte bestand.
   - Aantal kolommen en hun labels.
   - Welke `is-voorspelling-juist`-velden nog `?` zijn (vereisen gebruikersbeoordeling).
   - Eventuele L3-waarschuwingen.

## Na de skill

De gebruiker beoordeelt de `?`-velden. Daarna `status: gereviseerd` en na teamvalidatie `status: gevalideerd`.

> Een bestand met status `gereviseerd` of `gevalideerd` mag geen `?`-waarden bevatten. Bij correctie die `?` introduceert: status valt terug naar `concept`.

## Kwaliteitseisen (proces)

Structurele vereisten staan in `schemas/voorbeeldreeks.schema.json` (≥ 3 kolommen; `is-invoer-juist=nee → is-voorspelling-juist=nvt`; enums; status-overgang). Procesregels die het schema niet kan afdwingen:

- Bij Beperkingsregel: kolom voor "Op de grens" én "Boven de grens" verplicht (zie `kaders/voorbeeldreeks.md §Testpatronen`).
- Bij Specialisatieregel: kolom met deelgeval van toepassing én een kolom met hoofdregel van toepassing.
- Status start altijd op `concept`; statusovergang loopt via reviewer/team.
