---
name: begrip-regel
description: "A3b — maakt een afleidingsregel-YAML voor een begrip met jas-klasse: afleidingsregel. Volgt op begrip-definitie."
context: fork
agent: general-purpose
---

# /begrip-regel — A3b afleidingsregel

Maakt `regels/AR-[bwb-id]-art[N]-lid[L]-[seq].yaml` voor een begrip met `jas-klasse: afleidingsregel`. Wordt alleen aangeroepen als het overeenkomstige begrip die JAS-klasse heeft.

> Lees vóór elke run: `.claude/skills/kaders/regeltypen.md`.

## Trigger

Volgt op `begrip-definitie` wanneer het bijbehorende begrip `jas-klasse: afleidingsregel` heeft. Wordt automatisch aangeroepen door de orchestrator `/wetsanalyse`.

## Invoer

Begrip-YAML `begrippen/[slug].yaml` met:
- `jas-klasse: afleidingsregel`
- `herkomst: afgeleid`
- definitie en relaties ingevuld door `begrip-definitie`

## Werkwijze

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
   - **`formele-regel`**: volledige tekst conform taalpatroon (zie `kaders/regeltypen.md §Taalpatronen`). Scan vóór het invullen alle overige leden van hetzelfde artikel op bepalingen die de werking van deze regel beperken, uitsluiten of modificeren (bijv. uitsluiting van een termijnenwet, afwijkende berekeningsgrondslag). Verwerk bevindingen in `formele-regel` en/of `toelichting`.
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

## Output

- `regels/AR-[bwb-id]-art[N]-lid[L]-[seq].yaml` — conform `schemas/regel.schema.json`.
- Update van `begrippen/[slug].yaml`: veld `afleidingsregel-id` of `uitvoer-van-regel-id`.

Levend voorbeeld: zie bestaande `regels/AR-BWBR0004770-*.yaml`.

## Tussenresultaten

Als de formule meer dan twee invoerregels nodig heeft of meerdere operators bevat: split in tussenresultaten (zie `kaders/regeltypen.md §Tussenresultaten`). Maak voor elk tussenresultaat een eigen begrip (`tussenresultaat: true`) **en** een eigen afleidingsregel.

## Reeks-producerende rekenregels

Wanneer de uitvoer een geordende reeks is (vervaldatums, termijnbedragen): voer de Reeks-statustoets uit (zie `kaders/regeltypen.md`). Maak waar relevant een aanvullende beslissingsregel `bepalen status [element] op peildatum`.

## Vervolg

- `/valideer AR-[id]` (A4b) voor de volledige voorbeeldreeks-testmatrix.
- `/begrip-scenario` en `/begrip-bron` blijven op begrip-niveau (worden niet hier opgeroepen).

## Kwaliteitseisen (proces)

- Elke regel herleidbaar tot één artikel + lid + zinsdeel.
- Altijd invoer- én uitvoerbegrip(pen) als begrip-id-strings.
- `rechtsfeit-id` gevuld (of `null` bij tussenresultaat).
- Voorbeeldreeksen bevatten minimaal één grensgeval (`juridisch-juist: false`).
- Taalpatroon consistent met de tabel in `kaders/regeltypen.md`.
- **Tussenresultaten expliciet:** impliciete algoritmen (tussenstappen/voorwaarden in de wetstekst) als aparte tussenresultaat-regels uitschrijven (`handleiding.pages.md` r. 301-303; `kaders/regeltypen.md`).
- **Menselijke validatie:** de afleidingsregel is een concept dat door vaktechnisch jurist + regelanalist wordt getoetst op juridische volledigheid (`kaders/menselijke-validatie.md`).

## Bronnen

- Schema: `schemas/regel.schema.json`
- Kaders: `kaders/regeltypen.md`, `kaders/menselijke-validatie.md`
- Canon: Handleiding §3.5.2b, §3.6 (`handleiding.pages.md` r. 2273-2299, 301-303)
- Projectconventies: `kaders/projectconventies.md` #15, #21
