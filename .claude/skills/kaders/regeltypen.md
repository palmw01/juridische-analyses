# Afleidingsregels — typen en taalpatronen (A3b)

> **Bron:** Handleiding Wetsanalyse §3.5.2b en §3.6 (p. 50-51, 63-64); Leidraad §3.8 productentabel #15. Gebruikt door `begrip-regel`, `valideer`.

---

## Doel

Afleidingsregels duiden en leggen vast welke **berekeningen, beslissingen, specialisaties en voorwaarden** in wetgeving zijn opgenomen. Ze zijn de bouwstenen van het regelmodel (A6e, buiten scope).

Architectuurprincipe:
```
annotatie-noot (A2) → begrip-noot (A3a) [JAS-klasse: Afleidingsregel]
                    → regel-noot  (A3b) → regelmodel-input (A6e)
```

Regel-noten worden **alleen** aangemaakt bij begrippen met JAS-klasse `afleidingsregel`.

## De vier typen

| Type | Uitkomst | Typisch taalpatroon |
|------|----------|---------------------|
| **Beslissingsregel** | Ja/nee — recht bestaat of niet | `[rechtssubject] is [uitvoerbegrip] indien …` |
| **Rekenregel** | Numerieke waarde | `[uitvoerbegrip] moet berekend worden als [invoer] [operator] [invoer]` |
| **Beperkingsregel** | Beperking of maximering | `[uitvoerbegrip] bedraagt ten hoogste/ten minste [grens]` |
| **Specialisatieregel** | Deelgeval t.o.v. hoofdregel | `In afwijking van [naam hoofdregel]: … indien …` |

> Leidraad product #15 noemt drie typen (beslissings-, reken-, beperking). De **Specialisatieregel** is een projectextensie op basis van "specialisaties" in Handleiding §3.5.2b. Gebruik dit type uitsluitend voor expliciete "in afwijking van"-constructies.

Kies het type dat het **rechtsgevolg** beschrijft, niet de wetsstructuur.

## Beslisboom regeltype

```
1. Is de uitkomst uitsluitend ja of nee?
   → Beslissingsregel
2. Bevat de bepaling een rekenkundige berekening?
   2a. Begrenst of maximeert de bepaling de uitkomst?
       → Beperkingsregel  (begrenzing prevaleert)
   2b. Geen begrenzing?
       → Rekenregel
3. Wijkt de bepaling voor een deelgeval af van een hoofdregel
   ("in afwijking van" of equivalent)?
   → Specialisatieregel
4. Geen van bovenstaande: herevalueer de wetsformulering.
```

Bij twijfel 1 vs. 2: controleer het uitvoerbegrip. Beslissingsregel → Booleaanse waarde; Rekenregel → numerieke waarde of tijdsduur.

## Naamgeving

- Begin met **actieve werkwoordsvorm**: `bepalen`, `berekenen`, `vaststellen`, `beoordelen`.
- Beschrijvend voor de berekening of beslissing.
- Consistent met de begripsnamen van invoer- en uitvoerbegrippen.

Voorbeelden: `bepalen invorderbaarheid belastingaanslag`, `berekenen invorderingsrente`.

## Structuur regel-YAML

Velden (schema-afgedwongen):

| Veld | Inhoud |
|------|--------|
| `naam` | Leesbare naam (actieve werkwoordsvorm) |
| `soort` | Beslissings- / Reken- / Beperkings- / Specialisatieregel |
| `rechtsfeit-id` | begrip-id van triggerende rechtsfeit; `null` bij tussenresultaat |
| `invoer` | array van begrip-id-strings |
| `uitvoer` | array van begrip-id-strings (≥ 1; normaal 1) |
| `operators` | EN / OF / NIET / plus / min / maal / gedeeld-door / kleiner-dan / groter-dan / gelijk-aan / ten-hoogste / ten-minste |
| `formele-regel` | Volledige als-dan-structuur volgens taalpatroon |
| `toelichting` | Tracering naar artikel/lid/zinsdeel + interpretatiemotivering |
| `voorbeeldreeksen` | ≥ 2 illustratieve invoer/uitkomst-combinaties incl. ≥ 1 grensgeval |
| `tussenresultaat` | `true` bij tussenstappen in impliciete algoritmen |

## Versie en cascade

- **`vervangt-regel-id`**: bij herziening — verwijst naar de vorige versie. De vervangen regel blijft bestaan met `geldigheid-tot`-datum gezet.
- **`prioriteit`**: alleen voor Specialisatieregels mét concurrentie (meerdere op hetzelfde invoergeval). Lagere waarde = hogere prioriteit. Gaps toegestaan (1, 3, 5). Bij één Specialisatieregel of niet-Specialisatieregels: `null`. Vul niet speculatief in.
- **`gespecialiseerd-regel-id`**: verplicht bij `soort: Specialisatieregel` — verwijst naar de hoofdregel die wordt overschreven.

## Pariteit bij tenzij-constructies — projectconventie

> **Projectconventie.** De twee-regelaanpak voor tenzij-constructies is een projectoperationalisatie; de Handleiding beschrijft Specialisatieregels maar schrijft geen verplichte pariteit voor.

Wanneer de wetstekst een `tenzij`-constructie bevat met twee expliciete uitkomsten (hoofdzin én tenzij-variant), maak beide regels aan:

| Constructiedeel | Regelsoort | Vereist veld |
|----------------|-----------|--------------|
| Hoofdzin ("Als … dan A") | Rekenregel, Beperkingsregel of Beslissingsregel | — |
| Tenzij-variant ("tenzij … dan B") | Specialisatieregel | `gespecialiseerd-regel-id` → regel-id van hoofdzin |

**Besliscriterium:** is de hoofdzin een zelfstandige normatieve uitkomst (geen lege verwijzing)? Ja → beide regels aanmaken.

## Taalpatronen

### Beslissingsregel — cumulatief (EN)

```
[rechtssubject] is [uitvoerbegrip]
indien aan alle volgende voorwaarden is voldaan:
- [voorwaarde 1]
- [voorwaarde 2]
```

### Beslissingsregel — alternatief (OF)

```
[rechtssubject] is [uitvoerbegrip]
indien aan ten minste één van de volgende voorwaarden is voldaan:
- [voorwaarde A]
- [voorwaarde B]
```

### Rekenregel

```
[uitvoerbegrip] moet berekend worden als
[invoerbegrip1] [operator] [invoerbegrip2]
```

Bij meerdere stappen: elke stap als genummerd tussenresultaat (zie §Tussenresultaten).

### Beperkingsregel

**Variant A — met voorwaarde:**
```
[uitvoerbegrip] bedraagt ten hoogste/ten minste [grenswaarde of -begrip]
indien [voorwaarde]
```

**Variant B — onvoorwaardelijke begrenzing:**
```
[uitvoerbegrip] bedraagt ten hoogste/ten minste [grenswaarde of -begrip]
```

### Specialisatieregel

```
In afwijking van [naam hoofdregel]:
[uitvoerbegrip] is [specifieke waarde of begrip]
indien [specificerende voorwaarde]
```

- `[naam hoofdregel]`: letterlijke `naam`-waarde van de hoofdregel (platte tekst, geen id).
- `invoer`: voorwaardenbegrippen die het deelgeval specificeren.
- `uitvoer`: vaak hetzelfde uitvoerbegrip als hoofdregel, met andere waarde.

## Tussenresultaten

Bij impliciete algoritmen — één wetsformulering met meerdere berekeningen of beslissingen (Handleiding p. 6-7).

**Triggertest** — split bij ten minste één van:
- meer dan één rekenkundige operator in dezelfde zin;
- een invoerbegrip is zelf afgeleid (`herkomst: afgeleid`) maar bestaat nog niet als begrip;
- de formele-regel zou meer dan twee invoerregels bevatten vóór het uitvoerbegrip wordt bereikt.

**Werkwijze:**
1. Identificeer alle tussenresultaten.
2. Maak per tussenresultaat een begrip-noot (`herkomst: afgeleid`, `tussenresultaat: true`).
3. Maak per tussenresultaat een aparte afleidingsregel.
4. Verwijs in de hoofdregel naar de tussenresultaat-begrippen als `invoer`.

## Reeks-producerende rekenregels — projectconventie

> **Projectconventie.** De reeks-statustoets (peildatum-afhankelijkheid, partieel rechtsgevolg, binaire samenvattingsvraag) is een projectspecifieke uitwerking voor invorderingstijdlijnen; de Handleiding noemt dit patroon niet expliciet.

Wanneer de uitvoer een **geordende reeks** is (vervaldatums, termijnbedragen), is vrijwel altijd ook een beslissingsregel nodig die de status van elk element op een peildatum bepaalt.

Reeks-statustoets:
1. **Peildatum-afhankelijkheid:** afhankelijk van vergelijking met peildatum/extern tijdstip? → beslissingsregel `bepalen status [element] op peildatum`.
2. **Partieel rechtsgevolg:** vervallen van één element heeft zelfstandig rechtsgevolg? → rekenregel `berekenen [invorderbaar/opeisbaar] bedrag op peildatum`.
3. **Binaire samenvattingsvraag:** overkoepelende ja/nee-vraag? → bestaande beslissingsregel moet de reeks-statusregel als invoer hebben.

Maak alleen de begrippen aan die juridisch relevant zijn voor het scenario.

## RegelSpraak-correspondentie — projectconventie

> **Projectconventie.** De vertaaltabel naar RegelSpraak (ALEF) is een hulpmiddel voor de regelanalist; de Handleiding schrijft geen specifieke vertaling voor.

De taalpatronen liggen dicht bij RegelSpraak (ALEF). De jurist legt het taalpatroon vast in de regel-noot; de regelanalist vertaalt naar RegelSpraak.

| Taalpatroon | RegelSpraak-equivalent |
|-------------------|------------------------|
| `indien aan alle volgende voorwaarden is voldaan` | `Geldig als … Daarvoor geldt:` |
| `[uitvoerbegrip] moet berekend worden als` | `[uitvoerbegrip] is gelijk aan` |
| `ten hoogste` | `maximaal` |
| `ten minste` | `minimaal` |
| `indien` | `Geldig als` |
| `kleiner/groter dan [waarde]` | identiek |
| `kleiner/groter dan of gelijk aan [waarde]` | identiek |
| `niet gelijk aan [waarde]` | `ongelijk aan [waarde]` |

## Signalering en LI-context — projectconventie

> **Projectconventie.** De Leidraad-specifieke verwerkingsregels hieronder zijn projectspecifiek voor de IW 1990-annotaties; de Handleiding beschrijft geen LI-specifiek annotatiebeleid.

Bij `signalering` met "voorbeeld"/"illustratief": bronspecifieke regel voor het LI-voorbeeld; noteer dat de onderliggende norm in de wet zelf ligt en aparte annotatie vereist. Generaliseer niet binnen de LI-annotatie.

Bij `signalering` met "impliceert algemene regel": maak een expliciete keuze in `toelichting`:
- **Keuze 1 (aanbevolen):** maak de algemene regel aan als de norm grammaticaal of systematisch aantoonbaar is; gebruik het concrete geval als voorbeeldreeks.
- **Keuze 2:** beperk de regel tot het concrete voorbeeld en noteer dat generalisatie wacht op annotatie van de bronwet.

## Koppeling aan rechtsfeit

Elke afleidingsregel is gekoppeld aan het rechtsfeit dat haar triggert:

```yaml
rechtsfeit-id: BWBR0004770/art9/lid5/verstrijken-betalingstermijn-belastingaanslag
```

Koppelingspatroon: rechtsfeit "verstrijken betalingstermijn belastingaanslag" triggert regel "bepalen invorderbaarheid belastingaanslag".

## Kwaliteitseisen

1. Elke regel herleidbaar tot één artikel + lid + zinsdeel.
2. Altijd invoer- én uitvoerbegrip(pen) als begrip-id-strings.
3. `rechtsfeit-id` gevuld (of `null` bij tussenresultaat).
4. `naam` gevuld.
5. Tussenresultaten als eigen begrip + eigen regel.
6. Voorbeeldreeksen bevatten minimaal één grensgeval.
7. Taalpatroon consistent met §Taalpatronen.
