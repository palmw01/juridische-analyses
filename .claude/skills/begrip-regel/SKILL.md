---
description: "A3b — maakt een afleidingsregel-YAML voor een begrip met jas-klasse: afleidingsregel. Volgt op begrip-definitie."
context: fork
agent: general-purpose
---

# /begrip-regel — A3b afleidingsregel

Maakt `regels/AR-[bwb-id]-art[N]-lid[L]-[seq].yaml` voor een begrip met `jas-klasse: afleidingsregel`. Wordt alleen aangeroepen als het overeenkomstige begrip die JAS-klasse heeft.

> Lees vóór elke run: `.claude/skills/kaders/regeltypen.md`.

## Invoer

Begrip-YAML `begrippen/[slug].yaml` met:
- `jas-klasse: afleidingsregel`
- `herkomst: afgeleid`
- definitie en relaties ingevuld door `begrip-definitie`

## Stappen

1. **Bepaal het regeltype** via de beslisboom in `kaders/regeltypen.md`:
   - Ja/nee uitkomst → Beslissingsregel
   - Berekening zonder begrenzing → Rekenregel
   - Berekening met begrenzing → Beperkingsregel
   - "In afwijking van"-constructie → Specialisatieregel
2. **Bepaal de seq-letter** (`a`, `b`, …): kijk naar bestaande regels in `regels/` voor dit lid en kies de volgende beschikbare.
3. Roep `stub_regel(bwb_id, artikel, lid, seq, naam, soort, peildatum, rechtsfeit_id)` uit `tools/jas_index_lib.py` aan. Naam in actieve werkwoordsvorm (`bepalen`, `berekenen`, `vaststellen`, `beoordelen`).
4. Vul de overige velden:
   - **`invoer`**: lijst van begrip-id-strings (JAS-klasse Variabele, Parameter, Tijdsaanduiding).
   - **`uitvoer`**: één begrip-id-string (zelden meerdere — bij meerdere uitvoerbegrippen: maak aparte regels).
   - **`operators`**: lijst uit `EN/OF/NIET/plus/min/maal/gedeeld-door/kleiner-dan/groter-dan/gelijk-aan/ten-hoogste/ten-minste`.
   - **`formele-regel`**: volledige tekst conform taalpatroon (zie `kaders/regeltypen.md §Taalpatronen`).
   - **`toelichting`**: tracering naar artikel + lid + zinsdeel + interpretatiemotivering.
   - **`voorbeeldreeksen`**: minimaal 2 illustratieve combinaties incl. ≥ 1 grensgeval. Dit zijn beknopte voorbeelden (kort beschreven); de volledige testmatrix komt in A4b (`valideer`).
   - **`tussenresultaat`**: `true` als het uitvoerbegrip uitsluitend als invoer voor een andere regel dient.
5. **Specialisatieregel-specifiek**:
   - Vul `gespecialiseerd-regel-id` met de regel-id van de overschreven hoofdregel.
   - Vul `prioriteit` **niet** speculatief — alleen als meerdere Specialisatieregels op hetzelfde invoergeval kunnen worden toegepast.
6. **Tenzij-pariteit** (zie `kaders/regeltypen.md`): als de wetstekst twee expliciete uitkomsten benoemt (hoofdzin + tenzij-variant), maak beide regels — hoofdregel én Specialisatieregel met `gespecialiseerd-regel-id`.
7. Schrijf de regel-YAML met `schrijf_yaml`.
8. **Update het begrip-YAML**:
   - `afleidingsregel-id: AR-[bwb-id]-art[N]-lid[L]-[seq]` (alleen bij JAS-klasse afleidingsregel).
   - Voor een ander begrip dat herkomst `afgeleid` heeft maar JAS-klasse ≠ afleidingsregel: `uitvoer-van-regel-id` op die regel zetten.
9. Valideer:
   ```
   tools/.venv/bin/python tools/validate_note.py --file regels/AR-[...].yaml
   tools/.venv/bin/python tools/validate_note.py --file begrippen/[slug].yaml
   ```

## Tussenresultaten

Als de formule meer dan twee invoerregels nodig heeft of meerdere operators bevat: split in tussenresultaten (zie `kaders/regeltypen.md §Tussenresultaten`). Maak voor elk tussenresultaat een eigen begrip (`tussenresultaat: true`) **en** een eigen afleidingsregel.

## Reeks-producerende rekenregels

Wanneer de uitvoer een geordende reeks is (vervaldatums, termijnbedragen): voer de Reeks-statustoets uit (zie `kaders/regeltypen.md`). Maak waar relevant een aanvullende beslissingsregel `bepalen status [element] op peildatum`.

## Kwaliteitseisen

- Elke regel herleidbaar tot één artikel + lid + zinsdeel.
- Altijd invoer- én uitvoerbegrip(pen) als begrip-id-strings.
- `rechtsfeit-id` gevuld (of `null` bij tussenresultaat).
- Voorbeeldreeksen bevatten minimaal één grensgeval (`juridisch-juist: false`).
- Taalpatroon consistent met de tabel in `kaders/regeltypen.md`.
