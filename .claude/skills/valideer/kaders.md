# Kaders — Activiteit 4b: Voorbeeldreeksen (v1.0)

> Gebaseerd op: *Handleiding Wetsanalyse in de praktijk* (v1.0, 9 feb 2023) §3.6.2b
> Uitgever: EBM Belastingdienst

---

## Doel van voorbeeldreeksen (A4b)

Een voorbeeldreeks is een gestructureerde testmatrix voor één afleidingsregel. Elke kolom is één testgeval. Per kolom staat:
- de concrete invoerwaarden per invoerbegrip
- of de invoercombinatie geldig is (`is-invoer-juist`)
- de verwachte uitvoerwaarden
- of de verwachte uitkomst juridisch juist is (`is-voorspelling-juist`)

**Cruciale grens:** de skill vult `is-voorspelling-juist` in op `?` tenzij het geval algoritmisch bepaalbaar is (zie §Algoritmisch bepaalbare uitvoer). De juridische beoordeling blijft bij de gebruiker.

---

## Minimumvereisten

- **Minimaal 3 kolommen** per voorbeeldreeks.
- Elke voorbeeldreeks bevat altijd:
  - Een happy-path-kolom (alle voorwaarden vervuld, geldige invoer)
  - Een grensgeval-kolom (één grenswaarde of randconditie)
  - Een negatief-geval-kolom (uitkomst wijkt af van happy path, of ongeldige invoer)

---

## Testgevallenpatronen per regeltype

### Beslissingsregel (uitkomst: ja/nee)

| Kolom | Label | Patroon |
|-------|-------|---------|
| 1 | Happy path | Alle voorwaarden vervuld → uitvoer `ja` |
| 2 | Grensgeval | Één voorwaarde net op de grens → uitvoer afhankelijk |
| 3 | Negatief — één voorwaarde niet vervuld | Één voorwaarde gefaald → uitvoer `nee` |
| 4+ (optioneel) | Per aanvullende voorwaarde | Elke voorwaarde afzonderlijk gefaald |

**Algoritmisch bepaalbaar:** als de formele regel een expliciete `indien … dan ja`-structuur heeft, vul dan de verwachte uitvoer in voor kolom 1 en 3. Zet `is-voorspelling-juist: ?` voor het grensgeval (kolom 2) tenzij de grens exact mathematisch te bepalen is.

### Rekenregel (uitkomst: numerieke waarde)

| Kolom | Label | Patroon |
|-------|-------|---------|
| 1 | Standaard positief | Positieve invoerwaarden → positief resultaat |
| 2 | Nul-geval | Eén of meer invoerwaarden = 0 |
| 3 | Negatief of omgekeerd | Invoer leidt tot negatief of afwijkend resultaat |
| 4 | Grenswaarde | Invoer exact op een drempel |
| 5 (optioneel) | Onbekende invoer | Één invoerwaarde `onbekend` → uitvoer `nvt` |

**Algoritmisch bepaalbaar:** voor eenvoudige rekenregels (optelling, aftrekking, vermenigvuldiging met constante) kan de skill de verwachte uitvoer berekenen. Gebruik dan `is-voorspelling-juist: ?` — de gebruiker bevestigt.

### Beperkingsregel (uitkomst: begrensd waarde)

| Kolom | Label | Patroon |
|-------|-------|---------|
| 1 | Onder de grens | Invoer < grens → uitvoer = invoer (beperking niet actief) |
| 2 | Op de grens | Invoer = grens → uitvoer = grens |
| 3 | Boven de grens | Invoer > grens → uitvoer = grens (beperking actief) |

**Algoritmisch bepaalbaar:** als de grenswaarde een parameter is die in de regel staat, vul de verwachte uitvoer in.

### Specialisatieregel (uitkomst: deelgeval overschrijft hoofdregel)

| Kolom | Label | Patroon |
|-------|-------|---------|
| 1 | Valt onder specialisatie | Alle specialisatiecriteria vervuld → uitvoer conform specialisatieregel |
| 2 | Valt niet onder specialisatie | Eén criterium niet vervuld → hoofdregel van toepassing |
| 3 | Grensgeval criterium | Eén criterium op de grens van toe/niet-toepassen |

---

## Typeafleiding per begripsoort

Gebruik het `soort`-veld van het begrip-YAML om de invoerwaarden te typeren:

| Begrip-soort | Testwaarden |
|---|---|
| `datum` of `tijdsduur` | ISO-datumstrings (`'2026-01-01'`), `null` voor onbekend |
| `monetair-bedrag` | Decimale bedragen als string (`'1000.00'`), `'0'`, `'-500.00'` |
| `getal` | Getallen als string, `'0'`, negatieve waarden |
| JAS-klasse `variabele` (boolean) | `'ja'` of `'nee'` |
| JAS-klasse `parameter` | Concrete numerieke waarde |
| JAS-klasse `tijdsaanduiding` | ISO-datum |
| JAS-klasse `afleidingsregel` (uitvoer Beslissingsregel) | `'ja'`, `'nee'` |
| Overig / onbekend | Vrije tekst beschrijving |

---

## Algoritmisch bepaalbare uitvoer

Vul `verwachte-uitvoer` met een concrete waarde (niet `?`) als:
- **Beslissingsregel:** het geval valt duidelijk wel/niet onder de voorwaarden van de `formele-regel`
- **Rekenregel:** de berekening is een directe formule (bijv. `a - b`) en de invoerwaarden zijn getallen
- **Beperkingsregel:** de grenswaarde is expliciet in de `formele-regel` vermeld

Zet in alle andere gevallen `verwachte-uitvoer` op de meest plausibele waarde met `is-voorspelling-juist: ?`.

---

## Ongeldige invoer

Als `is-invoer-juist: nee`:
- Zet `verwachte-uitvoer` leeg of met toelichting als tekst
- Zet `is-voorspelling-juist: nvt`
- Gebruik kolom-`toelichting` om te motiveren waarom de invoer ongeldig is

---

## Bestandsnaamgeving

| Veld | Patroon |
|---|---|
| Bestandsnaam | `validaties/VR-[bwb-id]-art[nr]-lid[l]-[seq].yaml` |
| `voorbeeldreeks-id` | `VR-` gevolgd door het deel van `regel-id` na `AR-` |
| `afleidingsregel-id` | identiek aan `regel-id` van de afleidingsregel |

Voorbeeld: voor `AR-BWBR0004770-art9-lid1-a` → bestand `validaties/VR-BWBR0004770-art9-lid1-a.yaml`, id `VR-BWBR0004770-art9-lid1-a`.
