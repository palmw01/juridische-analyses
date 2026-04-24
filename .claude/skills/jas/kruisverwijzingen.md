# Kruisreferentie-extractieprotocol — JAS v1.0.10

Gebruik dit protocol in Stap 6. Voer de fasen strikt in volgorde uit. Lever het resultaat op als intern JSON-model; gebruik dit model als enige bron voor §7 en de frontmatter-array `kruisreferenties`.

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
Zoek het bwbId op in de BWB-mapping (SKILL.md Stap 2). Ontbreekt het bwbId in de mapping: gebruik de display-tekst als wetnaam.

### 1c. Extraheer lidnummer(s) uit de display-tekst

Zoekpatronen (in volgorde):
1. `leden\s+(\d+)\s+(?:en|tot en met)\s+(\d+)` → maak één record per lid in het bereik
2. `(\w+)\s+lid` waarbij het eerste woord een rangnaam is → zie rangnamentabel
3. `lid\s+(\d+)` → dat cijfer
4. Geen lidpatroon gevonden → `doel_lid: null`

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

Gebruik `(bron_bwbId, bron_artikel, bron_lid, doel_bwbId, doel_artikel, doel_lid)` als unieke sleutel. Duplicaten — bijv. hetzelfde artikel dat in twee opeenvolgende leden wordt aangehaald — bewaar als één record. Noteer in `ruwe_tekst` het eerste voorkomen.

---

## Edge cases

| Situatie | Aanpak |
|----------|--------|
| `&artikel=` ontbreekt in URI | `doel_artikel: null`, `doel_lid: null`, confidence 0.8 |
| Meerdere lids in display-tekst, één URI | Eén record per lid (zelfde bwbId + artikel) |
| Meerdere artikelen in display-tekst | Eén record per artikel |
| Dezelfde combinatie al gezien | Één record bewaren (deduplicatie) |
| Artikel verwijst naar zichzelf | Opnemen als interne verwijzing met toelichting "zelfverwijzing" |

---

## JSON-schema per record

```json
{
  "bron_bwbId": "BWBR0004770",
  "bron_artikel": "28",
  "bron_lid": "3",
  "doel_bwbId": "BWBR0004770",
  "doel_wet": "Invorderingswet 1990",
  "doel_artikel": "25",
  "doel_lid": "3",
  "ruwe_tekst": "artikel 25, derde lid",
  "confidence": 1.0
}
```

`doel_lid` is een string (ordinaal als getal: "3", "5") of `null`.

---

## Van JSON-model naar §7

Groepeer records op `doel_bwbId`:
- `doel_bwbId` = `bron_bwbId` → **§7.1 Interne verwijzingen**
- `doel_bwbId` ≠ `bron_bwbId` → **§7.2 Externe verwijzingen**

Schrijf in de "Verwijst naar"-kolom altijd de wiki-link-notatie: `[[Art. Z wet-afkorting]]`.

Bij `confidence < 0.8`: voeg in de "Relevantie"-kolom toe: *(verificatie aanbevolen)*.

De `kruisreferenties`-array in de frontmatter bevat de unieke waarden van `"Art. <doel_artikel> <wet-afkorting>"` — zonder wiki-brackets, zonder lid.

---

## §7.4-protocol — Omgekeerde kruisreferenties

De `wettenbank_zoekterm`-resultaten zijn een ruwe kandidatenlijst. Voer de onderstaande stappen verplicht uit voordat §7.4 wordt geschreven.

### Stap A — Filter valse treffers (andere wet)

De zoekterm `"artikel [A]"` matcht ook passages als "artikel [A] van de [andere wet]" die binnen [B] voorkomen. Per kandidaatartikel:

1. Roep `wettenbank_artikel(bwbId=[B], artikel=<nr>)` aan voor elk kandidaatartikel dat nog niet is opgehaald in Stap 6.
2. Controleer in de retourneertekst of de passage `"artikel [A]"` gevolgd wordt door een wetnaam of wetsafkorting van een **andere wet** dan [B]. Zo ja → **valse treffer**, uitsluiten van §7.4.

*Voorbeeld van valse treffer:* art. 7a IW 1990 bevat "artikel 25 van de Algemene wet inkomensafhankelijke regelingen" — de "25" verwijst naar de AWIR, niet naar IW 1990.

### Stap B — Classificeer per lid

Zoek in de retourneertekst naar de specifieke lidaanduiding van het geannoteerde lid `[L]`. Gebruik de rangnamentabel uit Fase 1c.

| Wat je vindt in de tekst | Classificatie |
|--------------------------|---------------|
| Expliciete verwijzing naar lid [L] (bijv. "artikel [A], vierde lid" of een bereik dat lid [L] omsluit zoals "derde **tot en met** vijfde") | **Directe omgekeerde kruisreferentie** — opnemen |
| Verwijzing naar art. [A] zonder specifiek lid (bijv. "het bepaalde in artikel [A]") | **Algemene omgekeerde kruisreferentie** — opnemen met *(verwijst naar art. [A] in het geheel)* in de Relevantie-kolom |
| Verwijzing naar art. [A] met een ander lid dan [L] | **Niet-relevant** — uitsluiten van §7.4 |

### Stap C — Beschrijving in de Relevantie-kolom

De Relevantie-kolom beschrijft de **werkelijke inhoud** van het verwijzende artikel, niet de verwijzing zelf. Gebruik het `pad`-veld van de MCP-response voor de afdeling/context. Benoem expliciet wat het artikel regelt (bijv. "uitsluiting verrekening gedurende uitstel", "overeenkomstige toepassing uitstelregime op aansprakelijk gestelden").

### Stap D — Substantieel belang

Controleer na classificatie of het verwijzende artikel lid [L] **opneemt in een opsomming of juist uitsluit**. Dit heeft rechtstreekse gevolgen voor de uitvoering van het geannoteerde lid (bijv. of invorderingsrente loopt of een vrijstelling geldt). Noteer een dergelijk bevinding als substantieel punt voor §9 (spanning/meerduidigheid) of §10 (lacunes).
