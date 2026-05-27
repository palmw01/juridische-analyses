# Canon-ankers — herleidbaarheid van uitspraken

> **Doel:** elke uitspraak in `kaders/` en `.claude/skills/**/SKILL.md` heeft één bron — canon (Handleiding/Leidraad Wetsanalyse), schema, of expliciet gelabelde projectconventie. Dit bestand is de centrale herleidbaarheidsmatrix.

## Conventie

| Code | Betekenis |
|------|-----------|
| `HW §X.Y.Z` | Handleiding Wetsanalyse §X.Y.Z (zie `docs/wetsanalyse-methodiek/extracted/handleiding.pages.md`) |
| `LW §X` | Leidraad voor Wetsanalyse op maat §X (zie `docs/wetsanalyse-methodiek/extracted/leidraad.pages.md`) |
| `JAS v1.0.10` | JAS-standaard https://regels.overheid.nl/standaarden/wetsanalyse/v1.0.10 |
| `schema:<naam>` | Canonieke definitie staat in `schemas/<naam>.schema.json` |
| `PROJECT` | Projectconventie — zie `kaders/projectconventies.md` |

---

## Kaders → canon

| Kader-bestand | Hoofdbron | Projectconventie-secties |
|---------------|-----------|--------------------------|
| `jas-taxonomie.md` | JAS v1.0.10 + HW §3.4 (p. 31-35) | operator-hergebruik (§9); rechtssubject-identificatie (slot); operator-soort (slot) |
| `markeerregels.md` | HW §3.4.2a (p. 33) | — |
| `diagramregels.md` | HW §3.4.2c (p. 33-35) | kleurcodering classDef |
| `begripsnaam.md` | HW §3.5.2a (p. 38-41) | bestandsnaamgeving; scenario-specifieke valkuil |
| `definitie.md` | HW §3.5.2a (p. 40-43) | verrijkingsprotocol; soort/herkomst-velden; soort-id-conventie |
| `relaties.md` | HW §3.5.2 (relatie-bestaan) | volledige structuur/kardinaliteit (projectconventie, A6d-georiënteerd) |
| `regeltypen.md` | HW §3.5.2b en §3.6 (p. 50-51, 63-64) + LW §3.8 productentabel #15 | pariteit tenzij-constructies; reeks-statustoets; RegelSpraak-correspondentie; signalering+LI-context |
| `voorbeeldreeks.md` | HW §3.6.2b (p. 52-53) | kolom-semantiek S3; typeafleiding; chained regels; statusovergangen |
| `interpretatie.md` | HW §3.5.3 (p. 44-46) | — |

---

## Schemas → canon

| Schema | Hoofdbron | Projectconventie-velden |
|--------|-----------|--------------------------|
| `annotatie-index` | HW §3.4 (artikelstructuur) | `delegatiestructuur[]`-formaat |
| `annotatie-lid` | HW §3.4 + JAS v1.0.10 (jas-klasse-enum) | `diagram`-structuur; `signalering`-veld |
| `begrip` | HW §3.5.2a + JAS v1.0.10 | status-enum (5 waarden); soort-enum (8 waarden); `soort-id`+`identificatiebegrip`; `tussenresultaat`-vlag; `kenmerken[]`; `scenario-refs[]`; `bronnen-secundair[]` |
| `regel` | HW §3.5.2b + LW §3.8 #15 | regel-id-pattern (AR-…); status-veld (impliciet via geldigheid); `tussenresultaat`-vlag; `prioriteit`-veld |
| `voorbeeldreeks` | HW §3.6.2b | voorbeeldreeks-id (VR-…); kolom-status-enum; `is-voorspelling-juist`-`?`-sentinel |
| `scenario` | LW §2.4 (scenario's voeden A2-A4) + HW §3.3.3 | scenario-id-pattern (scen-…) |
| `bron` | wettenbank-MCP-respons | normalisatie van `bwbId` → `bwb-id`; `opgehaald-op`-veld |

---

## Stand per regel-uitspraak (high-level)

De fijnmazige regel-voor-regel-herleidbaarheid wordt opgevangen door:

1. **Kop-ankers** boven elk kader-bestand (al aanwezig).
2. **Inline `projectconventie`-label** waar een uitspraak geen canon-bron heeft (al toegepast in `definitie.md`, `regeltypen.md`, `voorbeeldreeks.md`, `jas-taxonomie.md`, `begripsnaam.md`, `relaties.md`).
3. **`projectconventies.md`** als gebundelde verzameling met rationale + dichtstbijzijnde canon-anker.

Inconsistenties of nieuwe uitspraken voortaan registreren in dit bestand (via een PR) en/of in `projectconventies.md`.

---

## Termen-glossarium (canon ↔ project)

| Project-term | Canon-term | Status |
|--------------|------------|--------|
| jas-klasse (lowercase, code/YAML) | JAS-element (HW §3.4) | code-conventie; in proza "JAS-klasse" |
| afleidingsregel (4 typen) | afleidingsregel (4 typen) | HW §3.5.2b — ✓ identiek |
| Beperkingsregel | Beperkingsregel | HW §3.5.2b — ✓ identiek |
| Specialisatieregel | "specialisaties" (HW §3.5.2b) | projectextensie van canon-concept |
| voorbeeldreeks (testmatrix) | voorbeeldreeks (HW §3.6.2b) | ✓ identiek |
| centrale klasse | centrale klasse (HW §3.4.2c) | ✓ identiek |
| kern + contexten | "universele betekenis + contextuele aanvullingen" (HW §3.5.2a) | semantisch identiek; project-terminologie |
| markeerregels | markeerregels (HW §3.4.2a) | ✓ identiek |
| rechtsbetrekking, rechtsfeit, voorwaarde | identiek (JAS v1.0.10) | ✓ identiek |
| annotatie-lid (bestandstype) | "geannoteerd lid" (HW §3.4) | projectbestandsnaam |

**Vermijd:** "Bestaansregel" (komt niet in canon voor — gebruik "Beperkingsregel"). "Drempelregel" (alleen als projectjargon in `voorbeeldreeks.md §Algoritmisch bepaalbaar` — daar inmiddels hernoemd naar "Beperkingsregel-detectie").
