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

## Begripsdefinitie

- Definitie moet het begrip kunnen **vervangen in een zin** (substitueerbaar) — test dit altijd
- Geen punt aan het einde van de definitie
- Beschrijf essentiële kenmerken (**WAT**) én doel (**WAARVOOR**)
- Geen afleidingen, berekeningen of redeneringen — die horen in afleidingsregels
- Gebruik **niet** de begripsnaam zelf in de definitie
- Gebruik wél al eerder gedefinieerde begrippen in de definitie
- Benoem interpretatie- en preciseringskeuzes expliciet
- Signaleer als de betekenis afwijkt van de letterlijke formulering (A5-signaal)

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
| `getal` | Numerieke waarde incl. bedrag, percentage, aantal | Verschuldigd belastingbedrag, invorderingsrente |
| `datum` | Kalenderdatum of tijdstip | Dagtekening aanslagbiljet, invorderbaarheidsdatum |
| `waar-niet-waar` | Booleaanse waarde (ja/nee) | Invorderbaarheid, recht op uitstel |
| `tekst` | Vrije tekstwaarde | Naam belastingschuldige, adres |
| `enumeratiewaarde` | Limitatieve keuze uit vaste set waarden | Soort belastingaanslag (voorlopig/definitief/navorderings-/…) |

Voeg `[id]` toe als het begrip dient als unieke sleutel — zie §Identificatiebegrippen.

### Herkomst — VERPLICHT voor gegevensmodel

Dit veld is vereist voor A6d én A6e. Het onderscheidt observeerbare gegevens van berekende gegevens:

| Herkomst | Betekenis | Gevolg voor modellering |
|----------|-----------|------------------------|
| `direct` | Observeerbaar uit de werkelijke wereld; komt uit basisregistratie, aangifte of aanvraag | Bron vermelden in het `bron`-veld; input voor gegevensmodel |
| `afgeleid` | Uitvoer van een afleidingsregel; wordt berekend of beslist | Wiki-link naar de afleidingsregel in `afleidingsregels`-veld is verplicht |

Dit onderscheid is cruciaal: directe begrippen komen uit basisregistraties of aanvragen;
afgeleide begrippen worden berekend/beslist door een afleidingsregel.

### Geldigheid

- `peildatum`: de versiedatum van de wetstekst (uit MCP, nooit de datum van vandaag)
- Bij wetswijziging: maak een nieuw begrip aan met gewijzigde geldigheidsdata — pas het oude niet aan

### Status

Optioneel veld voor kwaliteitsbewaking:
- `gevalideerd` — getoetst in multidisciplinair team (A4)
- `concept` — aangemaakt maar nog niet getoetst
- `ter-review` — in bespreking

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

---

## Identificatiebegrippen

Markeer in het `soort`-veld aanvullend met `[id]` als een begrip dient als unieke
sleutel voor een rechtssubject of rechtsobject:

```yaml
soort: "enumeratiewaarde [id]"   # bijv. voor aanslagnummer
```

Voorbeelden in invorderingscontext:
- `sofinummer / BSN [id]` — unieke identificatie belastingschuldige
- `aanslagnummer [id]` — unieke identificatie belastingaanslag

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

---

## Invorderingscontext (IW 1990 / Leidraad Invordering)

Referentietabel voor de meest voorkomende begrippen in de invorderingssfeer:

| Begrip | Soort | Herkomst | Identificatie |
|--------|-------|----------|---------------|
| belastingschuldige | enumeratiewaarde | direct | BSN [id] |
| ontvanger | tekst | direct | — |
| belastingaanslag | enumeratiewaarde | direct | aanslagnummer [id] |
| aanslagbiljet | enumeratiewaarde | direct | — |
| dagtekening aanslagbiljet | datum | direct | — |
| betalingstermijn belastingaanslag | getal | afgeleid | — |
| invorderbaarheid | waar-niet-waar | afgeleid | — |
| invorderingsrente | getal | afgeleid | — |
| verschuldigd belastingbedrag | getal | direct | — |
| recht op uitstel van betaling | waar-niet-waar | afgeleid | — |

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
