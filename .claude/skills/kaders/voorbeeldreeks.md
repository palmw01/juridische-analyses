# Voorbeeldreeksen (A4b)

> **Bron:** Handleiding Wetsanalyse §3.6.2b (p. 52-53). Gebruikt door `valideer`.

---

## Doel

Een voorbeeldreeks is een gestructureerde testmatrix voor één afleidingsregel. Per kolom (≥ 3 verplicht):
- concrete invoerwaarden per invoerbegrip
- of de invoercombinatie geldig is (`is-invoer-juist`)
- de verwachte uitvoerwaarden
- of de verwachte uitkomst juridisch juist is (`is-voorspelling-juist`)

**Grens:** de skill vult `is-voorspelling-juist` op `?` tenzij algoritmisch bepaalbaar (zie §Algoritmisch bepaalbaar). De juridische beoordeling blijft bij de gebruiker.

## Minimumvereisten

Elke voorbeeldreeks bevat:
- een **happy-path-kolom** (alle voorwaarden vervuld, geldige invoer);
- een **grensgeval-kolom** (één grenswaarde of randconditie);
- een **negatief-geval-kolom** (uitkomst wijkt af van happy path, of ongeldige invoer).

Schema dwingt `minItems: 3` af.

## Testpatronen per regeltype

### Beslissingsregel (uitkomst ja/nee)

| Kolom | Label | Patroon |
|-------|-------|---------|
| 1 | Happy path | Alle voorwaarden vervuld → `ja` |
| 2 | Grensgeval | Eén voorwaarde net op de grens |
| 3 | Negatief — voorwaarde gefaald | Eén voorwaarde gefaald → `nee` |
| 4+ (optioneel) | Per aanvullende voorwaarde | Elke voorwaarde afzonderlijk gefaald |

**Algoritmisch bepaalbaar:** bij expliciete `indien … dan ja`-structuur kan de uitvoer voor kolom 1 en 3 worden ingevuld. Grensgeval (kolom 2) op `?` tenzij wiskundig exact te bepalen.

### Rekenregel (numerieke uitkomst)

| Kolom | Label | Patroon |
|-------|-------|---------|
| 1 | Standaard positief | Positieve invoer → positief resultaat |
| 2 | Nul-geval | Eén of meer invoerwaarden = 0 |
| 3 | Negatief of omgekeerd | Invoer leidt tot negatief of afwijkend resultaat |
| 4 | Grenswaarde | Invoer exact op een drempel |
| 5 (optioneel) | Onbekende invoer | Invoerwaarde `onbekend` → uitvoer `nvt` |

**Algoritmisch bepaalbaar:** eenvoudige bewerkingen (optellen, aftrekken, vermenigvuldigen met constante). Houd `is-voorspelling-juist: ?` — gebruiker bevestigt.

### Beperkingsregel (begrensde uitkomst)

| Kolom | Label | Patroon |
|-------|-------|---------|
| 1 | Onder de grens | Invoer < grens → uitvoer = invoer |
| 2 | Op de grens | Invoer = grens → uitvoer = grens |
| 3 | Boven de grens | Invoer > grens → uitvoer = grens |

**Algoritmisch bepaalbaar:** als de grenswaarde een parameter in de regel is.

**Kolom-semantiek S3 (projectconventie):** onderscheid twee typen grensgevallen:
- **Grens van de beperking:** invoerwaarde is exact de drempel die bepaalt of de cap actief is — kolom 2 "Op de grens".
- **Grens van het toepassingsbereik:** andere voorwaarde niet vervuld waardoor de regel überhaupt niet van toepassing is — label "Grens toepassingsbereik — [omschrijving]".

### Specialisatieregel (deelgeval overschrijft hoofdregel)

| Kolom | Label | Patroon |
|-------|-------|---------|
| 1 | Valt onder specialisatie | Alle criteria vervuld → uitvoer specialisatieregel |
| 2 | Valt niet onder specialisatie | Eén criterium niet vervuld → hoofdregel |
| 3 | Grensgeval criterium | Eén criterium op de grens |

## Typeafleiding per begripsoort — projectconventie

> **Projectconventie.** De koppeling van begrip-soort aan testwaarden is een projectspecifieke conventies die aansluit op de soort-enum in `schemas/begrip.schema.json`; de Handleiding schrijft geen testwaarden per datatype voor.

| Begrip-soort | Testwaarden |
|---|---|
| `datum` / `tijdsduur` | ISO-datumstrings (`'2026-01-01'`), `null` voor onbekend |
| `monetair-bedrag` | Decimale bedragen als string (`'1000.00'`), `'0'`, `'-500.00'` |
| `getal` / `percentage` | Getallen als string, `'0'`, negatieve waarden |
| `booleaans` | `'ja'` / `'nee'` |
| `enumeratie` | Concrete enum-waarde |
| Overig | Vrije tekstbeschrijving |

## Algoritmisch bepaalbaar — wanneer een concrete `verwachte-uitvoer` toelaatbaar is

Vul `verwachte-uitvoer` met een concrete waarde (en zet `is-voorspelling-juist: ?` of `ja` indien wiskundig zeker) als:

- **Beslissingsregel:** geval valt duidelijk wel/niet onder de voorwaarden van `formele-regel`.
- **Rekenregel:** berekening is een directe formule (bijv. `a - b`) met numerieke invoer.
- **Beperkingsregel:** de grenswaarde is expliciet in `formele-regel` vermeld.

In alle andere gevallen: meest plausibele waarde + `is-voorspelling-juist: ?`.

## Gebruik van `?` (open interpretatie)

`?` markeert dat juridische beoordeling nodig is. Gebruik `?` bij:
- uitkomst hangt af van niet-wettelijk vastgelegde interpretatie (grammaticaal/systematisch/teleologisch/wetshistorisch);
- rekenregel met afrondingsvraag die de wet niet regelt;
- toepassingsdrempel exact op grenswaarde die de wet niet expliciet in- of uitsluit.

Gebruik `ja`/`nee` alleen bij:
- exact wiskundig bepaalde grens;
- wet of Leidraad benoemt grens expliciet zonder interpretatieruimte.

Documenteer in `toelichting`: *"Open interpretatie: [beschrijving]. Juridisch oordeel door de jurist in te vullen."*

> Duiden of vaststellen van uitvoeringsbeleid is **Activiteit 5** (Signaleren) en valt buiten AI-scope.

## Ongeldige invoer

Bij `is-invoer-juist: nee`:
- `verwachte-uitvoer`: leeg of beschrijving als tekst.
- `is-voorspelling-juist: nvt`.
- `toelichting` motiveert waarom de invoer ongeldig is.

## Chained regels en uitvoer-eigenaarschap — projectconventie

> **Projectconventie.** De uitvoer-eigenaarschapsregel voor geketende regels is een projectspecifieke uitwerking; de Handleiding §3.6 beschrijft geen afzonderlijke VR per keten-stap.

Bij een Beslissings- of terugvalregel die een andere regel activeert ("herneemt art. 9 lid 1 IW 1990"):

1. De **activerende regel** produceert uitsluitend het activatie-signaal als uitvoer (bijv. `terugvalregel-lid-1: ja/nee`).
2. Het eindresultaat van de geactiveerde regel is de uitvoer van die geactiveerde regel — niet van de activerende.
3. In de VR: neem als `invoer` alleen de begrippen op die de activerende regel zelf nodig heeft. Voor de geactiveerde regel: aparte VR.

> **Terugvalregel** is geen soort, maar een patroon: een Beslissingsregel die een andere regel activeert.

## Statusovergangen — projectconventie

> **Projectconventie.** De statusnamen (concept / gereviseerd / gevalideerd) en de overgangsregels zijn projectspecifiek; ze zijn afgedwongen door de `status`-enum in `schemas/voorbeeldreeks.schema.json`.

| Status | Betekenis | `?`-waarden toegestaan? |
|--------|-----------|------------------------|
| `concept` | AI heeft ingevuld wat algoritmisch bepaalbaar is; open oordelen als `?` | Ja |
| `gereviseerd` | Team heeft alle `?`-waarden beoordeeld; alleen `ja`, `nee` en `nvt` | Nee |
| `gevalideerd` | Team heeft alle oordelen bevestigd als juridisch verdedigbaar | Nee |

Een bestand met status `gereviseerd`/`gevalideerd` mag geen `?`-waarden bevatten. Bij correctie die `?` introduceert: status valt terug naar `concept`.

## Bestandsnaamgeving

| Veld | Patroon |
|---|---|
| Bestandsnaam | `validaties/VR-{bwb-id}-art{N}-lid{L}-{seq}.yaml` |
| `voorbeeldreeks-id` | `VR-` gevolgd door de identifier ná `AR-` |
| `afleidingsregel-id` | identiek aan `regel-id` |

Voorbeeld: `AR-BWBR0004770-art9-lid1-a` → `validaties/VR-BWBR0004770-art9-lid1-a.yaml`.
