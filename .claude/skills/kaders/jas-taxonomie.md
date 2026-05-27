# JAS-taxonomie — 16 elementen

> **Bron:** JAS v1.0.10 (https://regels.overheid.nl/standaarden/wetsanalyse/v1.0.10) + Handleiding Wetsanalyse §3.4 (p. 31-35). Gebruikt door `annoteer-classificeer`, `annoteer-diagram`, `begrip-definitie`.
> **Status enums:** identiek aan `schemas/annotatie-lid.schema.json` en `schemas/begrip.schema.json` (`jas-klasse`-enum). De schema's zijn canoniek; deze tekst geeft de betekenis en herkenningsvragen.

---

## Boomstructuur

```
rechtssubject
rechtsobject
rechtsbetrekking
delegatiebevoegdheid
  └── delegatie-invulling
rechtsfeit
voorwaarde
  └── afleidingsregel
        ├── operator
        ├── variabele
        │     ├── variabelewaarde
        │     ├── tijdsaanduiding
        │     └── plaatsaanduiding
        └── parameter
              └── parameterwaarde
brondefinitie
```

13 hoofdklassen + 3 sub-elementen (`delegatie-invulling`, `variabelewaarde`, `parameterwaarde`) = 16 enumwaarden. De interne afvinklijst gebruikt de 13 hoofdklassen.

---

## Elementen

### 1. Rechtssubject

- **Definitie:** drager van rechten en plichten; natuurlijke of rechtspersoon.
- **Herkenningsvraag:** *Wie* heeft het recht / de plicht? *Van wie* is een rechtsobject?
- **Taalkenmerken:** zelfstandig naamwoord voor persoon/entiteit; voornaamwoord (hij, iemand, een ieder, degene).
- **Invordering:** belastingschuldige (art. 3 IW 1990), ontvanger, aansprakelijkgestelde, schuldeiser, Staat.

### 2. Rechtsobject

- **Definitie:** voorwerp van rechtsbetrekking of rechtsfeit; fysiek of niet-fysiek.
- **Herkenningsvraag:** *Wat* is het voorwerp van een recht of plicht?
- **Taalkenmerken:** zelfstandig naamwoord voor het onderwerp; aanwijzend voornaamwoord (dat, hetgeen, welke).
- **Invordering:** belastingaanslag, dwangbevel, beslag, vordering, vermogensbestanddeel.

### 3. Rechtsbetrekking

- **Definitie:** juridische relatie tussen twee rechtssubjecten — één rechthebbend, één plichthebbend.
- **Herkenningsvraag:** *Hoe verhouden* twee rechtssubjecten zich tot elkaar?
- **Taalkenmerken:** werkwoord + hulpwerkwoord (kan verzoeken, mag, is verplicht, heeft recht op, heeft aanspraak op).
- **Invordering:** betalingsplicht (art. 7 IW 1990), aanmaning, dwangbevel, uitstel, kwijtschelding.

### 4. Rechtsfeit

- **Definitie:** handeling, gebeurtenis of tijdsverloop met rechtsgevolg dat een rechtsbetrekking creëert, wijzigt of beëindigt.
- **Herkenningsvraag:** *Wat is de gebeurtenis* die gevolg heeft voor de rechtsbetrekking?
- **Taalkenmerken:** actieve werkwoordsvorm (indienen bezwaar, betekenen dwangbevel, verstrijken termijn).
- **Invordering:** dagtekening aanslag, verstrijken betalingstermijn, betekening dwangbevel.

### 5. Voorwaarde

- **Definitie:** conditie voor het intreden van een rechtsgevolg; enkelvoudig of samengesteld (EN/OF/NIET).
- **Herkenningsvraag:** *Welke eisen* worden gesteld? *Onder welke omstandigheden* geldt het rechtsgevolg?
- **Taalkenmerken:** voegwoorden (indien, als, tenzij, mits, met dien verstande dat); bijwoorden (schriftelijk, elektronisch).
- **Invordering:** voorwaarden uitstel (art. 25 IW 1990), kwijtscheldingscriteria (art. 26 IW 1990).

### 6. Afleidingsregel

- **Definitie:** regel die nieuwe feiten of waarden creëert op basis van bestaande feiten of waarden. Vier typen — zie `regeltypen.md`.
- **Herkenningsvraag:** *Hoe wordt* een variabele berekend of afgeleid?
- **Taalkenmerken:** is verminderd met, bedraagt vermeerderd met, wordt gesteld op, berekend naar.
- **Invordering:** berekening invorderingsrente (art. 28 IW 1990), vaststelling openstaand bedrag.

### 7. Variabele / Variabelewaarde

- **Variabele:** specifiek kenmerk/eigenschap van een rechtssubject, rechtsobject, rechtsbetrekking of rechtsfeit.
- **Variabelewaarde:** de concrete waarde — (1) getal/datum, (2) tekst, (3) enumeratiewaarde, (4) booleaanse waarde.
- **Herkenningsvraag:** *Welk bedrag, welke duur, welke hoogte* hoort bij dit object of feit?
- **Invordering:** verschuldigd belastingbedrag, betalingstermijn, datum aanslag, inkomen.

### 8. Parameter / Parameterwaarde

- **Parameter:** constante waarde over een periode, gelijk voor alle instanties.
- **Parameterwaarde:** de concrete waarde voor die periode.
- **Herkenningsvraag:** is dit een waarde die over een periode *voor iedereen gelijk* is?
- **Taalkenmerken:** tarieven, (drempel)bedragen, maxima, minima.
- **Invordering:** invorderingsrentevoet (art. 29 IW 1990), wettelijk rentepercentage.

### 9. Operator

- **Definitie:** woord of teken voor een rekenkundige bewerking, samengestelde voorwaarde, gelijkstelling of vergelijking.
- **Typen:** (a) rekenkundig (+, −, ×, ÷); (b) vergelijking (groter dan, gelijk aan); (c) logisch (EN, OF, NIET).
- **Taalkenmerken:** vermeerderd met, verminderd met, ten minste, niet.
- **Hergebruik-regel (projectconventie):** zoek bij `jas-klasse: operator` altijd eerst naar bestaande operator-begrippen (`grep -rl "jas-klasse: operator" begrippen/`). Voeg een bestaand begrip toe via een `context`-markering wanneer de logische werking identiek is; alleen een eigenstandige juridische betekenis rechtvaardigt een nieuw operator-begrip.

### 10. Tijdsaanduiding

- **Definitie:** tijdstip of tijdvak; geldigheid van een rechtsbetrekking, tijdsverloop met rechtsgevolg, peildatum.
- **Herkenningsvraag:** *Wanneer? Vanaf / tot welk moment?*
- **Taalkenmerken:** concrete datum, periodewoorden (jaar, maand, week, dag).
- **Invordering:** betalingstermijn 6 weken (art. 9), aanvang invorderingsrente, verjaring.

### 11. Plaatsaanduiding

- **Definitie:** plaats of gebied waarvoor de wetgeving geldt of die bepalend is voor de context.
- **Herkenningsvraag:** *Waar* (voor welk gebied) geldt de regel (niet)?
- **Invordering:** fiscale woonplaats, vestigingsplaats, grensoverschrijdende invordering.

### 12. Delegatiebevoegdheid / Delegatie-invulling

- **Delegatiebevoegdheid:** bevoegdheid om regels nader uit te werken in lagere regelgeving.
- **Delegatie-invulling:** de daadwerkelijke gedelegeerde regeling.
- **Scope:** uitsluitend delegatie strikt sensu — mandaat en attributie vallen buiten dit JAS-element.
- **Type-beslisregel:** *Verplicht* = passieve werkwoordsvorm zonder "kunnen" ("worden regels gesteld bij amvb"). *Facultatief* = "kan/kunnen" in de delegatiezin ("kan bij amvb worden bepaald"). Bij twijfel: kan de gemachtigde wetgever géén nadere regels stellen zonder de wet te schenden? Ja → facultatief.
- **Invordering:** art. 73 IW 1990 → UBIB 1990.

### 13. Brondefinitie

- **Definitie:** begripsomschrijving expliciet in de wetgeving opgenomen.
- **Herkenningsvraag:** is deze term *uitdrukkelijk omschreven* in de wettekst zelf?
- **Taalkenmerken:** artikel met aanhef + onderdelen ("In deze wet wordt verstaan onder:").
- **Invordering:** art. 3 IW 1990 (belastingschuldige, ontvanger), art. 1 AWR.

---

## Annotatieprincipes (Handleiding §3.4 + §3.5.3)

1. **Lees de wetstekst altijd eerst.** Snippets zijn nooit voldoende grondslag.
2. **Citeer precies.** Koppel elk element aan exact artikel + lid + zinsdeel.
3. **Kies de meest specifieke klasse.** Tijdsaanduiding > variabele; plaatsaanduiding > parameter.
4. **Interpretatiemethode expliciet.** Zie `interpretatie.md` voor de vier methoden.
5. **Meerduidigheid signaleren.** Benoem als een element conflicteert of dubbelzinnig is.
6. **Delegatieketens traceren.** Volledige keten (wet → amvb → ministeriële regeling).

> **Noot (operator-soort):** begrippen met `jas-klasse: operator` krijgen altijd `soort: tekst` — de JAS-klasse beschrijft de functie, het soort het datatype.

> **Noot (rechtssubject-identificatie):** rechtssubjecten hebben `soort: entiteit`. Het identificatieveld (BSN, RSIN) wordt als separaat Variabele-begrip met `soort-id: true` vastgelegd; verwijs daarheen via `heeft`.
