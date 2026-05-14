# Regelkader — Wetsanalyse Activiteit 3b + 6e (v1.1)

> Gebaseerd op: *Handleiding Wetsanalyse in de praktijk* (v1.0, 9 feb 2023) §3.5.2b, §3.6,
> *Leidraad voor Wetsanalyse op maat* (v1.0, 7 mrt 2023) producten #15, #19–20, §3.8 (A6e)
> Uitgever: EBM Belastingdienst

---

## Doel van afleidingsregels (A3b en A6e)

Afleidingsregels duiden en leggen vast welke **berekeningen, beslissingen, specialisaties en voorwaarden** in wetgeving zijn opgenomen. Ze zijn de bouwstenen van het regelmodel (A6e).

Beschreven in vaste taalpatronen zodat ze:
- omgezet kunnen worden naar executeerbare softwarecode zonder nadere interpretatie
- gevalideerd kunnen worden door het multidisciplinaire team (juristen, uitvoeringsdeskundigen, regelanalisten) met juridische scenario's
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

> **Noot:** De Leidraad product #15 noemt drie typen (beslissing, berekening, beperking). De Specialisatieregel is een praktijkextensie gebaseerd op de term "specialisaties" in Handleiding §3.5.2b ("berekeningen, beslissingen, **specialisaties** en voorwaarden"). Gebruik dit type uitsluitend voor expliciete "in afwijking van"-constructies in de wettekst.

Kies het type dat het **rechtsgevolg** beschrijft, niet de wetsstructuur.

### Beslisboom regeltype-classificatie

Doorloop de vragen in volgorde; de eerste die met "ja" wordt beantwoord bepaalt het type:

```
1. Is de uitkomst uitsluitend ja of nee (recht bestaat of bestaat niet)?
   → Beslissingsregel

2. Bevat de bepaling een rekenkundige berekening (optelling, deling, vermenigvuldiging)?
   2a. Begrenst of maximeert de bepaling ook de uitkomst van die berekening?
       → Beperkingsregel  (de begrenzing prevaleert boven de berekening)
   2b. Geen begrenzing?
       → Rekenregel

3. Wijkt de bepaling voor een specifiek deelgeval af van een elders vastgelegde hoofdregel
   (formule "in afwijking van" of equivalente constructie)?
   → Specialisatieregel

4. Geen van bovenstaande van toepassing: herevalueer de wetsformulering —
   controleer of er een impliciete berekening of beslissing aanwezig is.
```

Bij twijfel over 1 vs. 2: controleer het uitvoerbegrip. Een Beslissingsregel produceert een Booleaanse waarde (`waar` / `niet-waar`); een Rekenregel produceert een numerieke waarde of een tijdsduur.

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
| `## Toelichting` | Tracering naar artikel, lid, zinsdeel + interpretatiemotivering |
| `## Voorbeeldreeksen` | Minimaal 2 invoer/uitkomst-combinaties incl. ten minste 1 grensgeval |
| `vervangt-regel-id` | Optioneel — id van de vorige versie van deze regel bij herziening |

### Regelversioning: `vervangt-regel-id`

Wanneer een bestaande regel wordt herzien (nieuwe peildatum, gewijzigde formule), maak dan een nieuwe regelfile aan en verwijs met `vervangt-regel-id` naar de vervangen regel:

```yaml
vervangt-regel-id: AR-BWBR0004770-art9-lid5-b   # de vorige versie van deze regel
```

De vervangen regel blijft bestaan voor historische raadpleegbaarheid. Stel daar `geldigheid-tot` in op de dag vóór de ingangsdatum van de nieuwe regel.

### Specialisatieregel cascade: `prioriteit`

Wanneer meerdere Specialisatieregels op hetzelfde invoergeval van toepassing kunnen zijn, legt `prioriteit` de uitvoeringsvolgorde vast:

- Lagere waarde = hogere prioriteit (prioriteit 1 gaat vóór prioriteit 2)
- Bij één Specialisatieregel per situatie of bij niet-Specialisatieregels: `prioriteit: null`
- Begin bij 1 en verhoog per rang; gaps zijn toegestaan (1, 3, 5 …) zodat later regels kunnen worden ingevoegd

```yaml
soort: Specialisatieregel
prioriteit: 1   # gaat vóór andere Specialisatieregels met hogere waarde
```

Voeg `prioriteit` alleen in als er daadwerkelijk meerdere Specialisatieregels zijn die hetzelfde deelgeval kunnen betreffen — geen speculatieve invulling vooraf.

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

Gebruik variant A (met voorwaarde) als de begrenzing alleen geldt onder een bepaalde conditie. Gebruik variant B (zonder voorwaarde) als de begrenzing altijd geldt.

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

- `[naam hoofdregel]`: gebruik de letterlijke waarde van het `naam`-veld van de hoofdregel-noot (platte tekst, geen wiki-link).
- `invoer`: de voorwaardenbegrippen die het deelgeval specificeren (bijv. aanslagsoort, uitzondering).
- `uitvoer`: het begrip waarop de afwijkende waarde van toepassing is — vaak hetzelfde uitvoerbegrip als de hoofdregel, maar met een andere waarde.

---

## Tussenresultaten in impliciete algoritmen

Wetgeving bevat soms **impliciete algoritmen**: één wetsformulering bevat meerdere berekeningen of beslissingen (Handleiding p. 6–7). Elke tussenberekening of -beslissing moet als **eigen begrip** worden benoemd en als **eigen afleidingsregel** worden vastgelegd.

### Heuristische triggertest

Split in tussenresultaten als aan **ten minste één** van de volgende criteria is voldaan:
- De wetsformulering bevat meer dan één rekenkundige operator (bijv. optelling én deling in dezelfde zin).
- Een invoerbegrip van de afleidingsregel is zelf afgeleid (herkomst: afgeleid) maar bestaat nog niet als begrip-noot.
- De Formele regel zou meer dan twee regels invoer bevatten voordat het uitvoerbegrip wordt bereikt.

### Werkwijze

1. Identificeer alle tussenresultaten in de formule — dit zijn variabelen die niet rechtstreeks observeerbaar zijn uit de werkelijke wereld maar berekend moeten worden
2. Maak voor elk tussenresultaat een begrip-noot aan (`herkomst: afgeleid`) en voeg de tag `#tussenresultaat` toe aan de `tags`-lijst
3. Maak voor elk tussenresultaat een aparte afleidingsregel aan
4. Verwijs in de hoofdregel naar de tussenresultaat-begrippen als `invoer`

De tag `#tussenresultaat` maakt afgeleide tussenberekeningen filterbaar in Obsidian Graph View en Dataview.

### Voorbeeld (invorderingsrente art. 28 IW 1990)

| Stap | Tussenresultaat | Soort regel |
|------|----------------|-------------|
| 1 | `berekeningsgrondslag invorderingsrente` (afgeleid) | Rekenregel |
| 2 | `rentepercentage per dag` (afgeleid van parameter) | Rekenregel |
| Hoofdregel | `berekenen invorderingsrente` | Rekenregel (gebruikt stap 1 + 2 als invoer) |

---

## Reeks-producerende rekenregels

Een rekenregel produceert soms niet één waarde maar een **geordende reeks** van waarden (vervaldatums, termijnbedragen, staffelwaarden). Bij zo'n reeks ontbreekt vrijwel altijd een bijbehorende beslissingsregel die de **status van elk element op een gegeven tijdstip** bepaalt.

### Heuristische triggertest

Controleer na het opstellen van een rekenregel of de uitvoer een reeks is:

```
Is het uitvoerbegrip een verzameling van gelijksoortige waarden
(bijv. N vervaldatums, N termijnbedragen)?
→ ja: voer de reeks-statustoets uit (zie hieronder)
→ nee: geen aanvullende actie vereist
```

### Reeks-statustoets

Doorloop de volgende vragen:

1. **Peildatum-afhankelijkheid**: is de status van een element in de reeks afhankelijk van een vergelijking met een peildatum of ander extern tijdstip?
   - ja → er is een beslissingsregel nodig: `bepalen status [element] op peildatum`
2. **Partieel rechtsgevolg**: heeft het vervallen van één element een zelfstandig rechtsgevolg (bijv. invorderbaarheid van dat deel, opeisbaarheid van dat termijnbedrag)?
   - ja → maak ook een rekenregel aan: `berekenen [invorderbaar/opeisbaar] bedrag op peildatum`
3. **Binaire samenvattingsvraag**: is er ook een overkoepelende ja/nee-vraag ("is de aanslag al invorderbaar?") die volgt uit de reeksstatus?
   - ja → de bestaande beslissingsregel voor het overkoepelende begrip moet verwijzen naar de reeks-statusregel als invoer

### Begrippen die bij een reeks-statusregel horen

| Begrip | JAS-klasse | soort | Toelichting |
|--------|-----------|-------|-------------|
| `[element]-reeks` | variabele | lijst | de berekende reeks zelf (uitvoer van de rekenregel) |
| `status-[element]-op-peildatum` | afleidingsregel | waar-niet-waar | is dit element vervallen/opeisbaar op de peildatum? |
| `aantal-vervallen-[elementen]-op-peildatum` | variabele | getal | tussenresultaat: hoeveel elementen zijn al vervallen? |
| `[invorderbaar/opeisbaar]-bedrag-op-peildatum` | afleidingsregel | getal | partieel rechtsgevolg (indien van toepassing) |

Maak alleen de begrippen aan die juridisch relevant zijn voor het scenario; niet alle vier zijn altijd nodig.

### Voorbeeld (art. 9 lid 5 IW 1990)

| Rekenregel (aanwezig) | Ontbrekende beslissingsregel |
|-----------------------|------------------------------|
| `berekenen vervaldag eerste termijn` (AR-9-5c) | `bepalen status termijn op peildatum`: vervaldag-termijn ≤ peildatum → termijn vervallen |
| `berekenen vervaldag volgende termijnen` (AR-9-5d) | `berekenen invorderbaar bedrag op peildatum`: N vervallen termijnen × termijnbedrag |

---

## Invoer- en uitvoerbegrippen

- **Invoer**: wiki-links naar begrip-noten die als variabele of parameter dienen (JAS-klasse: Variabele, Parameter, Tijdsaanduiding)
- **Uitvoer**: in het `uitvoer`-veld een lijst met wiki-links naar de uitvoerbegrippen. Normaal één element. Bij meervoudig uitvoer (zeldzaam, bijv. een regel die zowel een rechtsbetrekking als een tijdsaanduiding bepaalt): maak aparte regel-noten per uitvoerbegrip in plaats van meerdere elementen in één `uitvoer`-lijst.
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

## Voorbeeldreeksen

Minimaal 2 reeksen. Aanvullende eisen:
- Bij meerdere conditionele takken (EN/OF-voorwaarden): minimaal **1 reeks per tak**.
- Bij Specialisatieregels: altijd een reeks voor het deelgeval **én** een reeks die laat zien dat de hoofdregel voor het deelgeval niet geldt. Gebruik het volgende tabelformaat om het onderscheid zichtbaar te maken:

  | Scenario | Deelgeval van toepassing? | Uitkomst deelgeval | Uitkomst hoofdregel |
  |----------|--------------------------|-------------------|---------------------|
  | [normaal geval — deelgeval niet van toepassing] | nee | n.v.t. | [uitkomst hoofdregel] |
  | [deelgeval — specificerende voorwaarde vervuld] | ja | [uitkomst deelgeval] | [afwijkend van hoofdregel] |
- Bij Beperkingsregels: altijd een reeks voor precies op de grenswaarde en een reeks waarbij de grenswaarde wordt overschreden.

| Invoerwaarden | Verwachte uitkomst | Is voorspelling juridisch juist? |
|--------------|-------------------|----------------------------------|
| [concrete invoerwaarden] | [verwachte uitkomst] | ja / nee + toelichting bij nee |

Test altijd:
- **Normale gevallen** — standaardsituatie
- **Grensgevallen** — precies op de grens van een voorwaarde
- **Randgevallen** — uitzonderingssituaties (andere leden, afwijkende aanslagsoorten)

---

## RegelSpraak-oriëntatie (Belastingdienst ALEF)

De taalpatronen in dit kader zijn intentioneel dicht bij de **RegelSpraak-syntax** gehouden (Leidraad p. 8–9: "bij voorkeur één op de Nederlandse taal gebaseerde specificatieomgeving zoals ALEF").

Correspondentietabel:

| Kader-taalpatroon | RegelSpraak-equivalent |
|-------------------|------------------------|
| `indien aan alle volgende voorwaarden is voldaan` | `Geldig als … Daarvoor geldt:` |
| `[uitvoerbegrip] moet berekend worden als` | `[uitvoerbegrip] is gelijk aan` |
| `ten hoogste` | `maximaal` |
| `ten minste` | `minimaal` |
| `indien` | `Geldig als` |
| `in afwijking van` | `In afwijking van` (identiek) |
| `kleiner dan [waarde]` | `kleiner dan [waarde]` (identiek) |
| `groter dan [waarde]` | `groter dan [waarde]` (identiek) |
| `kleiner dan of gelijk aan [waarde]` | `kleiner dan of gelijk aan [waarde]` (identiek) |
| `groter dan of gelijk aan [waarde]` | `groter dan of gelijk aan [waarde]` (identiek) |
| `niet gelijk aan [waarde]` | `ongelijk aan [waarde]` |

**Rolverdeling**: De jurist legt het taalpatroon vast in de regel-noot; de regelanalist (Leidraad, disciplinetabel) zet dit om naar RegelSpraak. Dit kader beschrijft de **juridische laag** — de regelanalist vertaalt naar de IT-laag.

---

## Kennismodel-geschiktheid (A6e — niet-onderhandelbaar)

Een regel-noot is pas **kennismodel-gereed** als aan alle volgende eisen is voldaan:

1. `naam`-veld gevuld met leesbare naam (actieve werkwoordsvorm)
2. `rechtsfeit`-veld gevuld met wiki-link naar het triggerende rechtsfeit
3. Alle invoerbegrippen zijn wiki-links naar begrip-noten
4. Uitvoerbegrip is een wiki-link naar een begrip-noot
5. Tussenresultaten zijn als eigen begrip + eigen afleidingsregel uitgewerkt
6. Voorbeeldreeksen bevatten minimaal één grensgeval

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

---

## Referenties

- **Handleiding Wetsanalyse in de praktijk** (v1.0, 9 feb 2023), §3.5.2b, §3.6, p. 6–7, 50–51, 63–64
- **Leidraad voor Wetsanalyse op maat** (v1.0, 7 mrt 2023), producten #15, #19–20, §3.8, p. 8–9
- **JAS v1.0.10:** https://regels.overheid.nl/standaarden/wetsanalyse/v1.0.10
- **RegelSpraak / ALEF:** Belastingdienst interne documentatie
