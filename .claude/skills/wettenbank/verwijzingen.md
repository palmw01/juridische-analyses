# Kruisreferentie-extractieprotocol — JAS v1.0.10

Gebruik dit protocol in de Voorbereiding (dataverwerving). Voer de fasen strikt in volgorde uit. Lever het resultaat op als intern JSON-model; gebruik dit model als enige bron voor de annotatietabel (kolom Begrip) en de frontmatter-array `kruisreferenties`.

> **Veldnaming.** Alle veldnamen in het JSON-model volgen `schemas/annotatie-lid.schema.json` `kruisreferenties[]` (kebab-case: `doel-bwb-id`, `doel-artikel`, `doel-lid`, `ruwe-tekst`).

---

## JCI URI-parser

Elke JCI-link heeft de vorm `jci1.3:c:<bwbId>&<param>=<waarde>&...`.

| URI-onderdeel | Extractieregel |
|---------------|----------------|
| **bwbId** | Alles tussen `c:` en de eerste `&`; ontbreekt `&` → alles na `c:` |
| **artikel** | Waarde van `&artikel=`; ontbreekt deze parameter → `null` |
| **Negeer** | `&hoofdstuk=`, `&afdeling=`, `&paragraaf=`, `&z=`, `&g=` |

---

## Fase 1 — JCI Markdown-links (altijd eerst)

Zoek in elke `leden[].tekst` naar het patroon `[display-tekst](jci1.3:c:...)`.

**Per match:**

### 1a. Parse de URI
Pas de URI-parser toe → bwbId + artikel.

### 1b. Bepaal de wetnaam
Zoek het bwbId op in `bwb-mapping.md`. Ontbreekt het bwbId in de mapping: gebruik de display-tekst als wetnaam.

### 1c. Extraheer lidnummer(s) uit de display-tekst

Zoekpatronen (in volgorde):
1. `leden\s+(\d+)\s+(?:en|tot en met)\s+(\d+)` → maak één record per lid in het bereik
2. `(\w+)\s+lid` waarbij het eerste woord een rangnaam is → zie rangnamentabel
3. `lid\s+(\d+)` → dat cijfer
4. Geen lidpatroon gevonden → `doel-lid: null`

**Rangnamentabel:**

| Rangnaam | Ordinaal | Rangnaam | Ordinaal |
|----------|----------|----------|----------|
| eerste | 1 | twaalfde | 12 |
| tweede | 2 | dertiende | 13 |
| derde | 3 | veertiende | 14 |
| vierde | 4 | vijftiende | 15 |
| vijfde | 5 | zestiende | 16 |
| zesde | 6 | zeventiende | 17 |
| zevende | 7 | achttiende | 18 |
| achtste | 8 | negentiende | 19 |
| negende | 9 | twintigste | 20 |
| tiende | 10 | eenentwintigste | 21 |
| elfde | 11 | tweeëntwintigste | 22 |

**Meerdere rangnamen in één display-tekst** (bijv. "derde, vijfde, negende lid"): maak één record per rangnaam, elk met hetzelfde bwbId + artikel.

### 1d. Extraheer meerdere artikelen uit de display-tekst
Bevat de display-tekst "artikelen X en Y" of "artikelen X, Y en Z": maak één record per artikelnummer. De URI-bwbId en eventueel lid gelden voor elk.

### 1e. confidence
- URI bevat `&artikel=` → 1.0
- URI zonder `&artikel=` (verwijzing naar hele wet) → 0.8

---

## Fase 2 — Platte tekst (alleen passages zonder JCI-link)

Verwijder eerst alle al gematche JCI-Markdown-passages uit de tekst. Zoek daarna in de resterende tekst.

**Zoekpatroon:** `artikel\s+[0-9]+[a-z]?(?:[a-z]?(?:[,\s]+(?:en|of)\s+[0-9]+[a-z]?)*)?`

**Per match:**

1. Zoek in dezelfde zin naar een wetkwalificatie ("van de [Wet X]", "van het [Besluit Y]", "van [afkorting]"). Gevonden → gebruik BWB-mapping voor bwbId; niet gevonden → gebruik bwbId van het huidige artikel (`[B]`).
2. Zoek in dezelfde zin naar een lidaanduiding (zie Fase 1c).
3. Meerdere artikelnummers in één match → splits naar afzonderlijke records.

**confidence:**
- Expliciete wetnaam in de zin → 0.9
- Geen wetkwalificatie → 0.7

---

## Deduplicatie

Gebruik `(bron-bwb-id, bron-artikel, bron-lid, doel-bwb-id, doel-artikel, doel-lid)` als unieke sleutel. Duplicaten — bijv. hetzelfde artikel dat in twee opeenvolgende leden wordt aangehaald — bewaar als één record. Noteer in `ruwe-tekst` het eerste voorkomen.

---

## Edge cases

| Situatie | Aanpak |
|----------|--------|
| `&artikel=` ontbreekt in URI | `doel-artikel: null`, `doel-lid: null`, confidence 0.8 |
| Meerdere lids in display-tekst, één URI | Eén record per lid (zelfde bwbId + artikel) |
| Meerdere artikelen in display-tekst | Eén record per artikel |
| Dezelfde combinatie al gezien | Één record bewaren (deduplicatie) |
| Artikel verwijst naar zichzelf | Opnemen als interne verwijzing met toelichting "zelfverwijzing" |

---

## JSON-schema per record

```json
{
  "bron-bwb-id": "BWBR0004770",
  "bron-artikel": "28",
  "bron-lid": "3",
  "doel-bwb-id": "BWBR0004770",
  "doel-wet": "Invorderingswet 1990",
  "doel-artikel": "25",
  "doel-lid": "3",
  "ruwe-tekst": "artikel 25, derde lid",
  "confidence": 1.0
}
```

`doel-lid` is een string (ordinaal als getal: "3", "5") of `null`.

---

## Van JSON-model naar kruisreferenties-kolom en frontmatter

Groepeer records op `doel-bwb-id`:
- `doel-bwb-id` = `bron-bwb-id` → **interne verwijzing**
- `doel-bwb-id` ≠ `bron-bwb-id` → **externe verwijzing**

Bij `confidence < 0.8`: markeer met *(verificatie aanbevolen)*.

De `kruisreferenties`-array in de frontmatter bevat de unieke waarden van `"Art. <doel-artikel> <wet-afkorting>"` — zonder wiki-brackets, zonder lid.

---

## Omgekeerde kruisreferenties — verificatieprotocol

De `wettenbank_zoekterm`-resultaten zijn een ruwe kandidatenlijst. Voer de onderstaande stappen verplicht uit.

### Stap A — Filter valse treffers (andere wet)

De zoekterm `"artikel [A]"` matcht ook passages als "artikel [A] van de [andere wet]" die binnen [B] voorkomen. Per kandidaatartikel:

1. Roep `wettenbank_artikel(bwbId=[B], artikel=<nr>)` aan voor elk kandidaatartikel dat nog niet is opgehaald.
2. Controleer in de retourneertekst of de passage `"artikel [A]"` gevolgd wordt door een wetnaam of wetsafkorting van een **andere wet** dan [B]. Zo ja → **valse treffer**, uitsluiten.

### Stap B — Classificeer per lid

Zoek in de retourneertekst naar de specifieke lidaanduiding van het geannoteerde lid `[L]`. Gebruik de rangnamentabel.

| Wat je vindt in de tekst | Classificatie |
|--------------------------|---------------|
| Expliciete verwijzing naar lid [L] | **Directe omgekeerde kruisreferentie** — opnemen |
| Verwijzing naar art. [A] zonder specifiek lid | **Algemene omgekeerde kruisreferentie** — opnemen met *(verwijst naar art. [A] in het geheel)* |
| Verwijzing naar art. [A] met een ander lid dan [L] | **Niet-relevant** — uitsluiten |

### Stap C — Beschrijving

Beschrijf de **werkelijke inhoud** van het verwijzende artikel, niet de verwijzing zelf. Gebruik het `pad`-veld van de MCP-response voor context.

### Stap D — Substantieel belang

Controleer of het verwijzende artikel lid [L] **opneemt in een opsomming of juist uitsluit**. Noteer dit als relevant punt voor de toelichting-kolom van de annotatietabel.
