# Regelkader — Wetsanalyse Activiteit 3b + 6e (v1.1)

> Gebaseerd op: *Handleiding Wetsanalyse in de praktijk* (v1.0, 9 feb 2023) §3.5.2b, §3.6,
> *Leidraad voor Wetsanalyse op maat* (v1.0, 7 mrt 2023) producten #15, #19–20, §3.8 (A6e)
> Uitgever: EBM Belastingdienst

---

## Doel van afleidingsregels (A3b en A6e)

Afleidingsregels duiden en leggen vast welke **berekeningen, beslissingen, specialisaties en voorwaarden** in wetgeving zijn opgenomen. Ze zijn de bouwstenen van het regelmodel (A6e).

Beschreven in vaste taalpatronen zodat ze:
- omgezet kunnen worden naar executeerbare softwarecode zonder nadere interpretatie
- gevalideerd kunnen worden door het multidisciplinaire team (juristen, uitvoeringsdeskundigen, regelanalisten) met juridische scenario's (A4)
- direct gekoppeld zijn aan de rechtsgevolgen per rechtsfeit uit het juridische scenario

Het architectuurprincipe is:
```
annotatie-noot (A2) → begrip-noot (A3a) [JAS-klasse: Afleidingsregel]
                    → regel-noot  (A3b) → regelmodel-input (A6e)
```

Regel-noten worden **alleen** aangemaakt bij begrip-noten met JAS-klasse `Afleidingsregel`.

---

## De vier typen afleidingsregels

| Type | Uitkomst | Typisch taalpatroon | A6e: regelmodel |
|------|----------|---------------------|-----------------|
| **Beslissingsregel** | Ja/nee — recht bestaat of niet | "[rechtssubject] is [uitvoerbegrip] indien …" | Conditietak |
| **Rekenregel** | Numerieke waarde | "[uitvoerbegrip] moet berekend worden als [invoer] [operator] [invoer]" | Rekenformule |
| **Beperkingsregel** | Beperking of maximering van een waarde of recht | "[uitvoerbegrip] bedraagt ten hoogste/ten minste [grens]" | Begrenzing |
| **Specialisatieregel** | Deelgeval ten opzichte van een hoofdregel | "In afwijking van [naam hoofdregel]: … indien …" | Subtype-tak |

Kies het type dat het **rechtsgevolg** beschrijft, niet de wetsstructuur.

---

## Naamgeving afleidingsregel

- Begin met **actieve werkwoordsvorm**: `bepalen`, `berekenen`, `vaststellen`, `beoordelen`
- Beschrijvend voor de berekening of beslissing (wat wordt er bepaald?)
- Consistent met de begripsnamen van invoer- en uitvoerbegrippen
- Gebruik het leesbare `naam`-frontmatter-veld voor Obsidian Graph View en Dataview

Voorbeelden:
- `bepalen invorderbaarheid belastingaanslag`
- `berekenen invorderingsrente`
- `vaststellen betalingstermijn belastingaanslag`
- `beoordelen recht op uitstel van betaling`

---

## Structuur van een afleidingsregel

Een regel-noot bevat de volgende elementen:

| Veld | Inhoud |
|------|--------|
| `naam` | Leesbare naam (actieve werkwoordsvorm + omschrijving) |
| `soort` | Beslissingsregel / Rekenregel / Beperkingsregel / Specialisatieregel |
| `rechtsfeit` | Wiki-link naar het rechtsfeit (JAS-klasse: Rechtsfeit) dat deze regel triggert |
| `invoer` | Wiki-links naar invoerbegrippen (variabelen, parameters) |
| `uitvoer` | Wiki-link naar uitvoerbegrip (het afgeleide begrip) |
| `operators` | EN / OF / NIET / plus / min / maal / gedeeld-door / kleiner-dan / groter-dan / gelijk-aan / ten-hoogste / ten-minste |
| `## Formele regel` | Volledige als-dan structuur conform taalpatroon per type |
| `## Toelichting` | Tracering naar artikel, lid, zinsdeel + interpretatiemotivering + A5-signaal |
| `## Voorbeeldreeksen` | Minimaal 2 invoer/uitkomst-combinaties incl. ten minste 1 grensgeval |

---

## Taalpatronen per type

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

Bij meerdere stappen: elke stap als genummerd tussenresultaat (→ zie §Tussenresultaten).

### Beperkingsregel

```
[uitvoerbegrip] bedraagt ten hoogste/ten minste [grenswaarde of -begrip]
indien [voorwaarde]
```

### Specialisatieregel

```
In afwijking van [naam hoofdregel]:
[uitvoerbegrip] is [specifieke waarde of begrip]
indien [specificerende voorwaarde]
```

---

## Tussenresultaten in impliciete algoritmen

Wetgeving bevat soms **impliciete algoritmen**: één wetsformulering bevat meerdere berekeningen of beslissingen (Handleiding p. 6–7). Elke tussenberekening of -beslissing moet als **eigen begrip** worden benoemd en als **eigen afleidingsregel** worden vastgelegd.

### Werkwijze

1. Identificeer alle tussenresultaten in de formule — dit zijn variabelen die niet rechtstreeks observeerbaar zijn uit de werkelijke wereld maar berekend moeten worden
2. Maak voor elk tussenresultaat een begrip-noot aan (`herkomst: afgeleid`)
3. Maak voor elk tussenresultaat een aparte afleidingsregel aan
4. Verwijs in de hoofdregel naar de tussenresultaat-begrippen als `invoer`

### Voorbeeld (invorderingsrente art. 28 IW 1990)

| Stap | Tussenresultaat | Soort regel |
|------|----------------|-------------|
| 1 | `berekeningsgrondslag invorderingsrente` (afgeleid) | Rekenregel |
| 2 | `rentepercentage per dag` (afgeleid van parameter) | Rekenregel |
| Hoofdregel | `berekenen invorderingsrente` | Rekenregel (gebruikt stap 1 + 2 als invoer) |

---

## Invoer- en uitvoerbegrippen

- **Invoer**: wiki-links naar begrip-noten die als variabele of parameter dienen (JAS-klasse: Variabele, Parameter, Tijdsaanduiding)
- **Uitvoer**: één wiki-link naar het afgeleide begrip-noot (JAS-klasse: Afleidingsregel)
- Het uitvoerbegrip heeft `herkomst: afgeleid` en een wiki-link in het `afleidingsregels`-veld terug naar deze regel-noot
- Nooit losse tekst — altijd wiki-links naar begrip-noten

---

## Koppeling aan rechtsfeit en juridisch scenario

Elke afleidingsregel is gekoppeld aan het **rechtsfeit** dat haar triggert (Handleiding p. 50–51):

```yaml
rechtsfeit: "[[begrippen/verstrijken-betalingstermijn-belastingaanslag]]"
```

Dit maakt de regel bruikbaar als input voor het **procesmodel (A6f)**: het rechtsfeit is de event in het BPMN-procesmodel, de afleidingsregel de uitvoering ervan.

Koppelingspatroon:
- Rechtsfeit: `verstrijken betalingstermijn belastingaanslag`
- Triggert: `bepalen invorderbaarheid belastingaanslag`

---

## Voorbeeldreeksen (validatie A4)

Minimaal 2 reeksen; bij meerdere voorwaarden minimaal 1 reeks per tak.

| Invoerwaarden | Verwachte uitkomst | Is voorspelling juridisch juist? |
|--------------|-------------------|----------------------------------|
| [concrete invoerwaarden] | [verwachte uitkomst] | ja / nee + toelichting bij nee |

Test altijd:
- **Normale gevallen** — standaardsituatie
- **Grensgevallen** — precies op de grens van een voorwaarde
- **Randgevallen** — uitzonderingssituaties (andere leden, afwijkende aanslagsoorten)

---

## RegelSpraaak-oriëntatie (Belastingdienst ALEF)

De taalpatronen in dit kader zijn intentioneel dicht bij de **RegelSpraaak-syntax** gehouden (Leidraad p. 8–9: "bij voorkeur één op de Nederlandse taal gebaseerde specificatieomgeving zoals ALEF").

Correspondentietabel:

| Kader-taalpatroon | RegelSpraaak-equivalent |
|-------------------|------------------------|
| `indien aan alle volgende voorwaarden is voldaan` | `Geldig als … Daarvoor geldt:` |
| `[uitvoerbegrip] moet berekend worden als` | `[uitvoerbegrip] is gelijk aan` |
| `ten hoogste` | `maximaal` |
| `ten minste` | `minimaal` |
| `indien` | `Geldig als` |
| `in afwijking van` | `In afwijking van` (identiek) |

**Rolverdeling**: De jurist legt het taalpatroon vast in de regel-noot; de regelanalist (Leidraad, disciplinetabel) zet dit om naar RegelSpraaak. Dit kader beschrijft de **juridische laag** — de regelanalist vertaalt naar de IT-laag.

---

## Kennismodel-geschiktheid (A6e — niet-onderhandelbaar)

Een regel-noot is pas **kennismodel-gereed** als aan alle volgende eisen is voldaan:

1. `naam`-veld gevuld met leesbare naam (actieve werkwoordsvorm)
2. `rechtsfeit`-veld gevuld met wiki-link naar het triggerende rechtsfeit
3. Alle invoerbegrippen zijn wiki-links naar begrip-noten
4. Uitvoerbegrip is een wiki-link naar een begrip-noot
5. Tussenresultaten zijn als eigen begrip + eigen afleidingsregel uitgewerkt
6. Voorbeeldreeksen bevatten minimaal één grensgeval
7. A5-signaal vermeld als uitvoeringsbeleid vereist is maar ontbreekt

---

## Invorderingscontext (IW 1990)

Referentietabel voor de meest voorkomende afleidingsregels in de invorderingssfeer:

| Naam | Type | Rechtsfeit | Invoer | Uitvoer |
|------|------|-----------|--------|---------|
| bepalen invorderbaarheid belastingaanslag | Beslissingsregel | verstrijken betalingstermijn belastingaanslag | belastingaanslag, dagtekening aanslagbiljet, betalingstermijn belastingaanslag | invorderbaarheid |
| vaststellen betalingstermijn belastingaanslag | Specialisatieregel | vaststellen belastingaanslag | soort belastingaanslag | betalingstermijn belastingaanslag |
| berekenen invorderingsrente | Rekenregel | verstrijken betalingstermijn | berekeningsgrondslag invorderingsrente, rentepercentage per dag, duur | invorderingsrente |
| beoordelen recht op uitstel van betaling | Beslissingsregel | aanvraag uitstel van betaling | betalingsonmacht, zekerheid | recht op uitstel van betaling |

---

## Kwaliteitseisen (niet-onderhandelbaar)

1. Elke regel is herleidbaar tot één artikel + lid + zinsdeel
2. Geen regel zonder invoer- én uitvoerbegrip(pen) — altijd wiki-links
3. `rechtsfeit`-veld is altijd gevuld
4. `naam`-veld is altijd gevuld
5. Tussenresultaten zijn als eigen begrip + eigen regel uitgewerkt
6. Voorbeeldreeksen bevatten altijd minimaal één grensgeval
7. Taalpatroon is voor niet-juristen begrijpelijk en consistent met §Taalpatronen
8. A5-signaal opnemen bij ontbrekend uitvoeringsbeleid

---

## Referenties

- **Handleiding Wetsanalyse in de praktijk** (v1.0, 9 feb 2023), §3.5.2b, §3.6, p. 6–7, 50–51, 63–64
- **Leidraad voor Wetsanalyse op maat** (v1.0, 7 mrt 2023), producten #15, #19–20, §3.8, p. 8–9
- **JAS v1.0.10:** https://regels.overheid.nl/standaarden/wetsanalyse/v1.0.10
- **RegelSpraaak / ALEF:** Belastingdienst interne documentatie
