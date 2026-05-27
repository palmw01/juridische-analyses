# Begripsdefinitie — gelaagd model (A3a)

> **Bron:** Handleiding Wetsanalyse §3.5.2a (p. 40-43). Gebruikt door `begrip-definitie`.

---

## Doel

Begrippen zorgen voor **betekenis, duidelijkheid, traceerbaarheid en begrijpelijkheid**. Definities maken interpretatie- en preciseringskeuzes expliciet vastlegbaar. Begrippen worden **nooit** rechtstreeks uit de wetstekst afgeleid — uitsluitend uit de `markeringen[].tekst`-velden in de begrip-YAML (door `/annoteer` vastgelegd).

## Structuur — kern + contexten

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

## Kern — eisen

- Geldig voor **alle** bronartikelen — niet afhankelijk van één specifiek artikel.
- Sluit zo nauw mogelijk aan bij de letterlijke tekst in de primaire markering (`bijdrage: primair`).
- **Substitutietest:** moet het begrip vervangen kunnen vervangen in een zin zonder betekenisverlies.
- **Geen punt** aan het einde (voorkomt dubbele punt bij substitutie).
- Beschrijf **WAT** het is (essentiële kenmerken) én **WAARVOOR** (doel).
- Geen afleidingen, berekeningen of redeneringen — die horen in afleidingsregels.
- Gebruik **niet** de begripsnaam zelf in de kern.
- Gebruik wél al eerder gedefinieerde begrippen in de kern (onderhoud werkt automatisch door).
- Benoem interpretatie- en preciseringskeuzes expliciet in `toelichting-klasse`.

`definitie-gebaseerd-op` bevat uitsluitend de markering-id's die de **kern** staven (primaire markeringen).

## Contexten — wanneer

| Bijdrage-type | Wanneer | Voorbeeld |
|---|---|---|
| `verfijning` | Kern blijft intact; artikel specificeert de kern voor één toepassingscontext (lex specialis) | Art. 9 lid 5 IW 1990: invorderbaarheid treedt *telkens* in per termijn i.p.v. eenmalig (kern: zodra betalingstermijn verstreken) |
| `uitbreiding` | Artikel voegt betekenisdimensie toe die buiten de kern valt | Aanvullend artikel breidt toepassingsbereik uit tot nieuwe categorie |
| `uitzondering` | Artikel beperkt of sluit de kern uit in een specifieke context (derogatie) | Hardheidsclausule die hoofdregel terzijde stelt |

**Lege contexten (`contexten: []`)** zijn de norm bij begrippen die uit één artikel stammen of waarbij de kern voor alle bronnen volstaat.

## Verrijkingsprotocol — nieuwe markering op bestaand begrip — projectconventie

> **Projectconventie.** De beslisboom hieronder is een projectoperationalisatie van het gelaagde definitiemodel; de Handleiding schrijft dit stappenplan niet letterlijk voor.

Wanneer `/annoteer` een markering toevoegt aan een begrip dat al een kern heeft:

1. **Analyseer** de nieuwe markering t.o.v. `definitie.kern`.
2. **Besluit:**
   - Identieke tekst, zelfde betekenis → voeg alleen toe aan `markeringen[]` met `bijdrage: context`; geen contextitem; `contexten` blijft leeg.
   - Specificeert de kern voor één wetscontext → voeg toe aan `contexten[]` met `bijdrage: verfijning`.
   - Voegt nieuwe betekenisdimensie toe → `contexten[]` met `bijdrage: uitbreiding`; overweeg kern-bijstelling.
   - Beperkt of sluit kern uit → `bijdrage: uitzondering`.
   - Onverenigbaar met kern → **signaleer homoniem-conflict** en stel splitsing voor; geen contextitem.
3. **Kern-update:** alleen bij fundamenteler inzicht dat voor alle bronnen geldt. Verhoog `definitie-versie`.
4. **`definitie-gebaseerd-op`** bevat uitsluitend kern-markeringen — verwijder ids die in `contexten` zijn opgenomen.

## Concrete voorbeelden

- Stelling-formaat: `[begrip]: [stelling over concreet persoon/feit]` → `ja / nee`.
- Rechtssubject voorop met fictieve naam (bijv. "Jan de Groot", "BV Acme").
- Tijdvak of tijdstip altijd benoemen.
- Minimaal 2 stellingen, waarvan **minstens 1 grensgeval** dat de afbakening demonstreert.
- Toelichting per stelling: waarom geldt het (niet)?
- Stellingen zijn concreet en toetsbaar — geen vage parafrasen.

## Eigenschappen — soort en herkomst — projectconventie

> **Projectconventie.** De soort- en herkomst-taxonomieën zijn projectoperationalisaties van het Handleiding §3.5.2a-begrippenkader; de canonieke enumwaarden staan in `schemas/begrip.schema.json`.

**Soort** (datatype, verplicht):

| Soort | Toelichting |
|-------|-------------|
| `monetair-bedrag` | Geldbedrag in euro's |
| `percentage` | Getal als rate (4.0 voor 4%) |
| `tijdsduur` | Periode in weken/maanden/jaren |
| `datum` | Kalenderdatum of tijdstip |
| `booleaans` | Ja/nee |
| `tekst` | Vrije tekstwaarde |
| `enumeratie` | Limitatieve keuze uit vaste set |
| `entiteit` | Rechtssubject of rechtsobject als instantie |

**Herkomst** (verplicht):

| Herkomst | Betekenis |
|----------|-----------|
| `direct` | Observeerbaar uit basisregistratie, aangifte of aanvraag |
| `afgeleid` | Uitvoer van een afleidingsregel; verwijst via `afleidingsregel-id` (bij JAS-klasse afleidingsregel) of `uitvoer-van-regel-id` (overige klassen) |

**Identificatie (projectconventie):** `soort-id: true` (én `identificatiebegrip: true`) als het begrip dient als unieke sleutel voor een entiteit (BSN, aanslagnummer). Beide velden hebben altijd dezelfde booleanwaarde.

## Kwaliteitseisen

1. Definitie substitueerbaar — test altijd.
2. Geen afleidingen of berekeningen in definitie.
3. Minimaal één grensgeval bij de voorbeelden.
4. Definitie uitsluitend gebaseerd op `markeringen[].tekst` — nooit uit eigen kennis of rechtstreeks uit de wetstekst.
5. Afgeleide begrippen verwijzen naar hun regel via `afleidingsregel-id` of `uitvoer-van-regel-id`.
