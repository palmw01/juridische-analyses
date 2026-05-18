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

**Schema-patroon (L1, afgedwongen):** `voorbeeldreeks-id` en `afleidingsregel-id` moeten matchen op `^(VR|AR)-BWBR[0-9]+-(art[0-9]+[a-z]?-lid[0-9]+|art[0-9]+[a-z]?-par[0-9]+|par[0-9]+-[0-9]+)-[a-z0-9]+$`. Drie geldige varianten: `…-art9-lid1-a`, `…-art9-par1-a`, `…-par9-5-a`. Een waarde als `VR-foo` of `AR-0001` faalt L1.

**Minimum kolommen (L1, afgedwongen):** elke voorbeeldreeks moet ten minste 3 kolommen bevatten (happy path + grensgeval + negatief-geval).

---

## Drempelregel voor `is-voorspelling-juist: ?` (S1)

Gebruik `?` (nog te beoordelen door de jurist) voor grensgevallen als:
- de uitkomst afhangt van een **niet-wettelijk vastgelegde interpretatie** (grammaticaal, systematisch, teleologisch of historisch) — ook als de interpretatie plausibel is;
- de rekenregel een **afrondingsvraag** opwerpt die de wet niet regelt (bijv. "gelijke termijnen" zonder afrondingsregel);
- de toepassingsdrempel van een beperkings- of specialisatieregel **exact op de grenswaarde** ligt en de wet de grens niet expliciet in- of uitsluit.

Gebruik `ja` of `nee` alleen als:
- de grens **exact wiskundig bepaald** is (bijv. ≤ 1 resterende maand = 0 of 1);
- de wet of Leidraad de grens **expliciet benoemt** en er geen interpretatieruimte is.

**Let op:** een `?`-waarde markeert een A5-signaal (zie §A5-signalering). De skill noteert in de toelichting welke interpretatie openligt en waarom uitvoeringsbeleid vereist is.

---

## Chained regels en uitvoer-eigenaarschap (S2)

Als een Beslissingsregel of terugvalregel de uitvoering van een andere regel activeert (bijv. "herneemt art. 9 lid 1 IW 1990"), geldt:

1. De **activerende regel** produceert uitsluitend het activatie-signaal als uitvoer (bijv. `terugvalregel-lid-1: ja/nee`).
2. Het eindresultaat van de geactiveerde regel (bijv. `invorderbaarheid-belastingaanslag`) is de uitvoer van **die** geactiveerde regel — niet van de activerende.
3. In de voorbeeldreeks (VR): neem als `invoer` alleen de begrippen op die de activerende regel nodig heeft. De begrippen van de geactiveerde regel horen in een aparte VR bij die geactiveerde afleidingsregel.

---

## Beperkingsregel: kolom-semantiek en volgorde (S3)

Het patroon voor Beperkingsregel is: kolom 1 = **onder**, kolom 2 = **op de grens van de beperking**, kolom 3 = **boven**.

Onderscheid twee soorten grensgevallen:
- **Grens van de beperking:** de invoerwaarde is exact de drempel die bepaalt of de cap actief is (bijv. "31e dag van een maand die niet bestaat"). Dit hoort in kolom 2 als "Op de grens".
- **Grens van het toepassingsbereik:** de dagtekening-voorwaarde of termijn-voorwaarde is vervuld maar de andere voorwaarde niet, waardoor de regel überhaupt niet van toepassing is. Label dit als "Grens toepassingsbereik — [omschrijving]", niet als "Op de grens".

---

## Statusovergangen (M1)

| Status | Betekenis | `?`-waarden toegestaan? |
|--------|-----------|------------------------|
| `concept` | AI heeft ingevuld wat algoritmisch bepaalbaar is; openstaande juridische oordelen als `?` gemarkeerd | Ja |
| `gereviseerd` | Team heeft alle `?`-waarden beoordeeld; alleen `ja`, `nee` en `nvt` resten; A5-signalen geïdentificeerd | Nee |
| `gevalideerd` | Team heeft bevestigd dat alle oordelen juridisch verdedigbaar zijn | Nee |

**Regel:** een bestand met status `gereviseerd` of `gevalideerd` mag geen `?`-waarden bevatten. Als een correctie een `?` introduceert, valt de status terug naar `concept`.

---

## A5-signalering (M2)

Wanneer tijdens A4b een interpretatievraag opkomt die niet algoritmisch te beantwoorden is, hoort die vraag thuis in **Activiteit 5 (Signaleren ontbrekende beleidsregels)** — niet als permanente `?` in A4b.

Werkwijze:
1. De skill markeert het geval met `is-voorspelling-juist: ?` en noteert in de `toelichting` welke interpretatie openligt (A5-signaal), met de formulering: *"A5-signaal: [beschrijving]. Juridisch oordeel door de jurist in te vullen."*
2. Het team beoordeelt de `?`-waarden en vult `ja` of `nee` in zodra het juridisch oordeel is bepaald (bijv. via uitvoeringsbeleid, intern besluit of expliciete wetstekst).
3. Zolang een A5-signaal niet is vastgesteld, blijft de status `concept` (niet `gereviseerd`).

---

## Regeltype-extensies buiten de PDF-methodologie (M3)

De *Leidraad voor Wetsanalyse op maat* (productentabel nr. 20) noemt drie regeltypen voor A4b: **Beslissingsregel**, **Rekenregel** en **Beperkingsregel**. De testgevallenpatronen in dit kaders-document zijn ontworpen conform die drie typen.

De typen **Specialisatieregel** en **Terugvalregel** zijn extensies van de implementatie in dit project. Ze zijn niet onjuist, maar vloeien niet rechtstreeks voort uit de PDF-methodologie. De testpatronen voor deze regeltypen (zie §Testgevallenpatronen) zijn afgeleid van de PDF-methodologie maar er niet letterlijk uit terug te lezen.
