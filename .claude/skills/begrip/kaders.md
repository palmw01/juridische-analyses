# Begrippenkader — Wetsanalyse Activiteit 3a + 6d (v1.1)

> Gebaseerd op: *Handleiding Wetsanalyse in de praktijk* (v1.0, 9 feb 2023) §3.5.1–3.5.2a,
> *Leidraad voor Wetsanalyse op maat* (v1.0, 7 mrt 2023) producten #11–14, §3.8 (A6d)
> Uitgever: EBM Belastingdienst

---

## Doel van begrippen (A3a en A6d)

Begrippen zorgen voor **betekenis, duidelijkheid, traceerbaarheid en begrijpelijkheid**. Ze maken wetgeving begrijpelijk voor iedereen in de uitvoeringsorganisatie en leggen interpretatie- en preciseringskeuzes expliciet vast.

Begrippen zijn de directe bouwstenen voor (Handleiding p. 36–37, 63–64):

- **Afleidingsregels** — algoritmen die de berekeningen en beslissingen afleiden
- **Gegevensmodel (A6d)** — gestructureerd overzicht van begrippen en hun onderlinge samenhang; basis voor de gegevensbehoefte van de uitvoeringsorganisatie
- **Procesmodel (A6f)** — begrippen met JAS-klasse Rechtsfeit worden actors/events in BPMN

Het architectuurprincipe is:
```
annotatie-noot (A2) → begrip-noot (A3a) → gegevensmodel-input (A6d)
                    → regel-noot  (A3b) → regelmodel-input   (A6e)
```

Begrippen worden **nooit** rechtstreeks uit de wetstekst afgeleid. De `markering` in de begrip-frontmatter (vastgelegd in A2 via `/annoteer`) is de enige bron voor de definitie.

---

## Begripsnaam

### Algemeen

- Sluit zo nauw mogelijk aan bij de **letterlijke wetsformulering** (markering)
- Kies een nieuwe naam als de formulering niet precies genoeg is — onderbouw dit in `toelichting-klasse`
- Voeg wettelijke context toe als dezelfde formulering in meerdere wetten anders betekent (bijv. `belastingschuldige iw 1990` vs `belastingplichtige awr`)
- **Hergebruik** een bestaande begripsnaam als de unieke betekenis identiek is — maak géén duplicaat

### Vaste opbouw en consistentie

- Begin met **zelfstandig naamwoord** (uitzondering: afleidingsregel/rechtsfeit → actieve werkwoordsvorm zoals `bepalen`, `vaststellen`, `indienen`)
- Gebruik al eerder gedefinieerde begrippen in de naam — wijziging van een begrip werkt dan automatisch door
- Gebruik dezelfde soort formuleringen voor hetzelfde type betekenis (consistentie vergemakkelijkt zoekopdrachten en Dataview-queries)

### Betekenis begripsnaam

- **Enkelvoudsvorm**, tenzij meervoud in de wet tot andere betekenis leidt
- Zo min mogelijk afkortingen; bij gebruik: uitschrijven in de begripsdefinitie
- Geen Romeinse cijfers (worden verward met letters)

### Leesbaarheid begripsnaam

- Geen hoofdletters (tenzij landsnaam of eigennaam)
- Lidwoorden/voorzetsels alleen opnemen als noodzakelijk voor leesbaarheid
- Gebruik **niet** het woord "voor" (multi-interpretabel — kies `voorafgaand aan`, `bij` of `over`)
- Geen lidwoord of voorzetsel aan het begin van een begripsnaam
- Geen ontkenningen in een begripsnaam (leidt tot dubbele ontkenning in taalpatronen)
- Zo kort mogelijk — schrijf eerst volledig uit, knip daarna in

---

## Begripsdefinitie — gelaagd model (kern + contexten)

Het `definitie`-veld is een object met twee onderdelen:

```yaml
definitie:
  kern: "Universele, wets-overstijgende betekenis"
  contexten:              # [] als de kern voor alle bronnen volstaat
    - markering-id: m-002
      bijdrage: verfijning   # verfijning | uitbreiding | uitzondering
      tekst: "Artikel-specifieke toevoeging"
      toelichting: "Optionele motivering"
```

### Kern (verplicht)

- Geldig voor **alle** bronartikelen — de kern mag niet afhankelijk zijn van één specifiek artikel
- Sluit zo nauw mogelijk aan bij de literaire tekst in de primaire markering
- Moet het begrip substitueerbaar kunnen vervangen in een zin (substitutietest)
- Geen punt aan het einde
- Beschrijf essentiële kenmerken (**WAT**) én doel (**WAARVOOR**)
- Geen afleidingen, berekeningen of redeneringen — die horen in afleidingsregels
- Gebruik **niet** de begripsnaam zelf in de kern
- Gebruik wél al eerder gedefinieerde begrippen in de kern
- Benoem interpretatie- en preciseringskeuzes expliciet
- Benoem in `toelichting-klasse` als de betekenis afwijkt van de letterlijke formulering

### Contextuele lagen (optioneel)

Wanneer een begrip in meerdere artikelen voorkomt, kan elk artikel de kern op een specifieke manier inkleuren. Dit legt vast zonder de kern te veranderen.

| Bijdrage-type | Juridische grondslag | Invorderingsvoorbeeld |
|---|---|---|
| `verfijning` | Lex specialis: het artikel specificeert de kern voor één toepassingscontext; de kern zelf blijft intact | Art. 9 lid 5 IW 1990: invorderbaarheid treedt *telkens* in per termijn i.p.v. eenmalig (kern: zodra betalingstermijn verstreken) |
| `uitbreiding` | Het artikel voegt een juridische dimensie toe die de kern-tekst niet dekt | Een aanvullend artikel breidt het toepassingsbereik van een begrip uit tot een nieuwe categorie belastingplichtigen |
| `uitzondering` | Derogatie: het artikel beperkt of sluit de hoofdregel uit in een specifieke situatie | Een hardheidsclausule die de standaard betalingstermijn terzijde stelt |

**Wanneer géén context-item:**
- De kern is voor alle bronnen volledig van toepassing
- Een markering heeft `bijdrage: context` en verandert de betekenis niet — voeg dan alleen de markering toe, geen contextitem
- Identieke tekst in meerdere artikelen met dezelfde juridische betekenis

**Audit-trail:** elk contextitem bevat `markering-id` waarmee de inkleuring direct herleidbaar is naar de specifieke wetstekstmarkering uit de annotatie.

---

## Concrete voorbeelden

- Stelling-formaat: `[begrip]: [stelling over concreet persoon/feit]` → `ja / nee`
- Rechtssubject voorop met fictieve naam (bijv. "Jan de Groot", "BV Acme")
- Tijdvak of tijdstip altijd benoemen
- Minimaal **2 stellingen**, waarvan minimaal **1 grensgeval** dat de precieze afbakening demonstreert
- Toelichting per stelling: waarom geldt het (niet)?
- Stellingen zijn concreet en toetsbaar — geen vage parafrasen

---

## Eigenschappen

### Soort (datatype) — VERPLICHT voor gegevensmodel

Dit veld is vereist voor A6d. Het typeert het begrip voor opname in het gegevensmodel.
Kies één waarde:

| Soort | Toelichting | Invorderingsvoorbeelden |
|-------|-------------|------------------------|
| `monetair-bedrag` | Geldbedrag in euro's | Verschuldigd belastingbedrag, invorderingsrente |
| `percentage` | Getal uitgedrukt als rate (bijv. 4.0 voor 4%) | Invorderingsrentevoet, wettelijk rentepercentage |
| `tijdsduur` | Periode in weken, maanden of jaren | Zes-weken, betalingstermijn-belastingaanslag |
| `datum` | Kalenderdatum of tijdstip | Dagtekening aanslagbiljet, invorderbaarheidsdatum |
| `booleaans` | Booleaanse waarde (ja/nee) | Invorderbaarheid, recht op uitstel |
| `tekst` | Vrije tekstwaarde | Naam belastingschuldige, adres |
| `enumeratie` | Limitatieve keuze uit vaste waardeset | Soort belastingaanslag (voorlopig/definitief/navorderings-/…) |
| `entiteit` | Rechtssubject of rechtsobject als instantie | Belastingschuldige als persoon, ontvanger |

Voeg `[id]` toe als het begrip dient als unieke sleutel — zie §Identificatiebegrippen.

> **Noot rechtssubjecten:** Personen en entiteiten (JAS-klasse: Rechtssubject) hebben `soort: entiteit`. Leg het identificatieveld (bijv. BSN, RSIN) vast als een separaat Variabele-begrip met `soort-id: true` (bijv. `soort: getal, soort-id: true` voor BSN). Verwijs vanuit het rechtssubject-begrip naar dat identificatiebegrip via `heeft`.

### Herkomst — VERPLICHT voor gegevensmodel

Dit veld is vereist voor A6d én A6e. Het onderscheidt observeerbare gegevens van berekende gegevens:

| Herkomst | Betekenis | Gevolg voor modellering |
|----------|-----------|------------------------|
| `direct` | Observeerbaar uit de werkelijke wereld; komt uit basisregistratie, aangifte of aanvraag | Bron vermelden in het `bron`-veld; input voor gegevensmodel |
| `afgeleid` | Uitvoer van een afleidingsregel; wordt berekend of beslist | Verplicht veld afhankelijk van jas-klasse: • `jas-klasse: afleidingsregel` → `afleidingsregel-id: [regel-id]` • alle andere jas-klassen → `uitvoer-van-regel-id: [regel-id]` |

Dit onderscheid is cruciaal: directe begrippen komen uit basisregistraties of aanvragen;
afgeleide begrippen worden berekend/beslist door een afleidingsregel.

### Geldigheid

- `peildatum`: de versiedatum van de wetstekst (uit MCP, nooit de datum van vandaag)
- Bij wetswijziging: maak een nieuw begrip aan met gewijzigde geldigheidsdata — pas het oude niet aan

### Status

Veld voor kwaliteitsbewaking:
- `concept` — aangemaakt maar nog niet getoetst (altijd bij aanmaken)
- `ter-review` — in bespreking
- `gevalideerd` — getoetst door het multidisciplinaire team (buiten AI-scope)

### JAS-klasse

Het `jas-klasse`-veld bevat de JAS-classificatie van het begrip, overgenomen uit de primaire annotatierij. Dit veld wordt tijdens A2 (annoteer) gezet en tijdens A3 (begrip) **niet** gewijzigd. Mogelijke waarden:

| JAS-klasse | Betekenis | Voorbeelden in invordering |
|------------|-----------|---------------------------|
| `rechtssubject` | Drager van rechten en plichten | belastingschuldige, ontvanger |
| `rechtsobject` | Voorwerp van rechtsbetrekking | belastingaanslag, voorlopige-aanslag |
| `rechtsbetrekking` | Juridische relatie | invorderbaarheid |
| `rechtsfeit` | Handeling/gebeurtenis met rechtsgevolg | dagtekening-aanslagbiljet |
| `voorwaarde` | Conditie in een als-dan-regel | dagtekening-in-vaststellingsjaar, afwijkend-boekjaar |
| `afleidingsregel` | Beslissings- of rekenregel | invorderbaarheid-belastingaanslag, terugvalregel-lid-1 |
| `operator` | Logische of rekenkundige operator | logische-of |
| `variabele` | Numerieke of tekstuele waarde | termijnbedrag, resterende-maanden-jaar |
| `tijdsaanduiding` | Datum, tijdstip of tijdsduur | 31-december, zes-weken |
| `parameter` | Vaste drempel- of referentiewaarde | — |
| `plaatsaanduiding` | Geografische aanduiding | — |
| `delegatiebevoegdheid` | Bevoegdheid tot delegatie | — |

> **Noot operators:** Begrippen met `jas-klasse: operator` krijgen altijd `soort: tekst` — de JAS-klasse beschrijft de functie, het soort het datatype (conform `jas-ontologie.yaml soort-restrictie: [tekst]`).

### Uitleg klasse

Het `toelichting-klasse`-veld bevat:
- Waarom deze JAS-klasse boven alternatieven gekozen is
- Verdieping van het type (bijv. type rechtsbetrekking: betalingsplicht; type rechtsfeit: aanvraag uitstel)
- Expliciet gesignaleerde meerduidigheid

---

## Relaties en kardinaliteit

Wiki-link arrays (`is-een`, `heeft`, `leidt-tot`) zorgen voor Obsidian Graph View-verbindingen.
Kardinaliteit staat alléén in de `## Relaties` body-tabel — niet in de YAML-arrays.
Reden: complexe YAML-objecten breken Obsidians graph-link detectie.

| Relatietype | Betekenis | Kardinaliteitsnotatie | Invorderingsvoorbeeld |
|-------------|-----------|----------------------|-----------------------|
| `is-een` | Specialisatie — dit begrip is een specifieke variant van een ander | — (subtype) | Naheffingsaanslag is-een belastingaanslag |
| `heeft 1:1` | Één-op-één compositie | Één A heeft precies één B | Belastingaanslag heeft 1:1 aanslagbiljet |
| `heeft 1:n` | Één-op-veel compositie | Één A heeft meerdere B's | Belastingschuldige heeft 1:n belastingaanslag |
| `heeft n:m` | Veel-op-veel | Meerdere A's horen bij meerdere B's | Aansprakelijkgestelde heeft n:m belastingschuld |
| `leidt-tot` | Causaal — rechtsfeit veroorzaakt rechtsgevolg | — (causaliteit) | Betalingstermijn leidt-tot invorderbaarheid |

De `## Relaties`-tabel in de body bevat altijd de kardinaliteitskolom — dit is de
input voor het entiteitrelatiediagram (A6d).

**Alleen uitgaande (forward) relaties opnemen.** De relaties-tabel en de frontmatter-velden `is-een`, `heeft` en `leidt-tot` bevatten uitsluitend relaties die *vanuit dit begrip* lopen — consistent met de voorbeelden in de Handleiding (§3.5.2), die relaties altijd beschrijven vanuit het perspectief van het begrip dat wordt uitgewerkt. Neem geen backward link op die al als forward link in een ander begrip is vastgelegd: Obsidian pikt alle wiki-links in het bestand op als uitgaande kanten in de Graph View, waardoor een onjuiste backward link een extra, verkeerd gerichte kant trekt. Voorbeeld: als `belastingaanslag` al `heeft 1:1 dagtekening-aanslagbiljet` bevat, dan neemt `dagtekening-aanslagbiljet` **geen** `heeft belastingaanslag` op.

---

## Identificatiebegrippen

Markeer in het `soort`-veld aanvullend met `[id]` als een begrip dient als unieke
sleutel voor een rechtssubject of rechtsobject:

```yaml
soort: enumeratie
soort-id: true       # bijv. voor aanslagnummer
```

Voorbeelden in invorderingscontext:
- `sofinummer / BSN` — `soort: getal, soort-id: true`
- `aanslagnummer` — `soort: enumeratie, soort-id: true`

Dit veld is input voor het gegevensmodel (A6d: "identificaties die nodig zijn om een gegeven uniek te maken").

---

## Hergebruik en homonimie

- **Eén begrip per unieke betekenis** — controleer bestaande begrippen vóór aanmaken
- Dezelfde formulering met een andere betekenis = apart begrip (homoniem); voeg wettelijke context toe in de naam
- Bij gewijzigde betekenis na jurisprudentie of wetswijziging: nieuw begrip met gewijzigde geldigheidsdata — pas het oude niet aan
- `aliases`-veld voor juridische synoniemen (bijv. `[invorderbaar]` als alias voor `invorderbaarheid`) — Obsidian herkent deze als alternatieve doorzoekbare namen

---

## Kennismodel-geschiktheid (A6d — niet-onderhandelbaar)

Een begrip-noot is pas **kennismodel-gereed** als aan alle volgende eisen is voldaan:

1. `soort` (datatype) is ingevuld
2. `herkomst` (direct of afgeleid) is ingevuld
3. Kardinaliteit van elke relatie is vermeld in de `## Relaties`-tabel
4. Identificatiebegrippen zijn gemarkeerd als `[id]` in het `soort`-veld
5. Afgeleide begrippen hebben een wiki-link naar de afleidingsregel in het `afleidingsregels`-veld
6. `aliases`-veld gevuld met bekende synoniemen (of leeg als geen synoniemen bestaan)
7. `geldigheid-van` is ingevuld (= peildatum bij aanmaken)
8. `status` is ingevuld (`concept` bij aanmaken)

---

## Invorderingscontext (IW 1990 / Leidraad Invordering)

Referentietabel voor de meest voorkomende begrippen in de invorderingssfeer:

| Begrip | Soort | Herkomst | Identificatie |
|--------|-------|----------|---------------|
| belastingschuldige | entiteit | direct | BSN (soort-id: true) |
| ontvanger | entiteit | direct | — |
| belastingaanslag | enumeratie | direct | aanslagnummer (soort-id: true) |
| aanslagbiljet | enumeratie | direct | — |
| dagtekening aanslagbiljet | datum | direct | — |
| betalingstermijn belastingaanslag | tijdsduur | afgeleid | — |
| invorderbaarheid | booleaans | afgeleid | — |
| invorderingsrente | monetair-bedrag | afgeleid | — |
| verschuldigd belastingbedrag | monetair-bedrag | direct | — |
| recht op uitstel van betaling | booleaans | afgeleid | — |

---

## Kwaliteitseisen (niet-onderhandelbaar)

1. Definitie vervangt het begrip substitueerbaar in een zin — test dit altijd
2. Definitie bevat geen afleidingen of berekeningen
3. Minimaal één grensgeval bij de voorbeelden
4. Relaties zijn altijd wiki-links; kardinaliteit staat in de `## Relaties`-tabel
5. `soort` en `herkomst` zijn altijd ingevuld
6. Afgeleide begrippen hebben altijd een wiki-link naar de afleidingsregel
7. Definitie uitsluitend gebaseerd op `markering` in frontmatter — nooit uit eigen kennis of rechtstreeks uit de wetstekst
8. `aliases`-veld aanwezig (ook als leeg)

---

## Referenties

- **Handleiding Wetsanalyse in de praktijk** (v1.0, 9 feb 2023), §3.5.1–3.5.2a, p. 36–37, 47–50, 63–64
- **Leidraad voor Wetsanalyse op maat** (v1.0, 7 mrt 2023), producten #11–14, §3.8
- **JAS v1.0.10:** https://regels.overheid.nl/standaarden/wetsanalyse/v1.0.10
- **NL-SBB begrippenkader:** https://docs.geostandaarden.nl/nl-sbb/nl-sbb/
