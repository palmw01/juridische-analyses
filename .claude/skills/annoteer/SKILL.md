---
description: "Voert Activiteit 2 uit van de Wetsanalyse-methode: markeren (A2a), classificeren (A2b) en structuurdiagram (A2c). Gebruik: /annoteer art. [A] [W] | /annoteer art. [A] lid [L] [W] | /annoteer sectie [ref] [W]"
context: fork
agent: general-purpose
---

# /annoteer — Activiteit 2: markeren en classificeren

> **Conflictresolutie:** Bij tegenstrijdigheid tussen deze SKILL.md en `kaders.md` is **`kaders.md` leidend**. SKILL.md geeft procesinstructies; `kaders.md` geeft de juridisch-inhoudelijke normen.

Voert Activiteit 2 uit van de Wetsanalyse-methode: markeren (A2a), classificeren (A2b) en diagram (A2c). Output zijn JSON/YAML-bestanden: één annotatie-JSON per lid, één begrip-YAML per annotatierij. Begrip-inhoud (A3) wordt later ingevuld door `/begrip`.

**Lees vóór elke annotatie-run eerst `.claude/skills/annoteer/kaders.md` volledig in.** De taxonomie (13 JAS-elementen), annotatieregels per element, en kleurcodering in dat bestand zijn bindend voor elke classificatiebeslissing in deze skill.

**Bestandsformaten:**
- Annotatie-index: `annotaties/{bwb-id}/art{N}.json` (JSON, schema: `schemas/annotatie-index.schema.json`)
- Lid-annotatie: `annotaties/{bwb-id}/art{N}-lid{L}.json` (JSON, schema: `schemas/annotatie-lid.schema.json`)
- Sectie-annotatie: `annotaties/{bwb-id}/{slug}.json` (JSON, schema: `schemas/annotatie-lid.schema.json`)
- Begrip-stub: `begrippen/{slug}.yaml` (YAML, schema: `schemas/begrip.schema.json`)

---

## Triggervormen

Drie flows, elk met eigen existentiecontrole en output:

| Trigger | Flow | Wanneer gebruiken |
|---------|------|-------------------|
| `/annoteer art. [A] [W]` | **A — Artikel-index** | Eerste aanraking van een artikel in een formele wet (met leden) |
| `/annoteer art. [A] lid [L] [W]` | **B — Lid-annotatie** | Annoteren van één lid van een formeel artikel |
| `/annoteer sectie [ref] [W]` | **C — Sectie-annotatie** | Bronnen zonder leden: Leidraad, beleid, beleidsregels |

Flow A maakt uitsluitend de structuurankers aan (index-JSON). Flow B voegt de inhoudelijke annotatie toe (lid-JSON + begrip-YAML-stubs). Flow C is voor bronnen die geen leden kennen.

---

## Slug-transformatietabel

De eenheid-slug wordt deterministisch afgeleid van het MCP `pad`-veld:

| MCP `pad`-segment | Transformatieregel | Slug-resultaat |
|-------------------|--------------------|----------------|
| `Artikel 9` | `art` + nummer | `art9` |
| `Artikel 2a` | `art` + nummer + letter | `art2a` |
| `Lid 1` | bestandsnaam `art{N}-lid{L}` | `art9-lid1.json` |
| `§ 1.1 De ontvanger` | `par` + punten → koppeltekens | `par1-1` |
| `§ 1.1.1 Inleiding` | `par` + punten → koppeltekens | `par1-1-1` |
| `Paragraaf 3` | `par` + nummer | `par3` |

Tekstdelen na het structuursymbool worden weggelaten. De slug bevat uitsluitend lowercase letters, cijfers en koppeltekens.

**Begrip-slug** (voor de `begrip-id` URI en bestandsnaam): deriveer van de begripsnaam — lowercase, spaties → koppeltekens, bijzondere tekens weglaten. Bijv. `"een belastingaanslag"` → `belastingaanslag`, `"is invorderbaar"` → `invorderbaarheid`.

**URI-formaat begrip-id:** `{bwb-id}/art{N}/lid{L}/{slug}` of `{bwb-id}/par{ref}/{slug}`.

---

## Voorbereiding — per flow

**Lees vóór alle flows eerst `.claude/skills/annoteer/kaders.md` volledig in.**

### Flow A — Artikel-index

> **Aanbevolen vertrekpunt (A1):** Als de gebruiker geen scenario's heeft geformuleerd vóór de aanroep, attendeer dan op dit hiaat — maar blokkeer de flow niet.

1. Controleer of bronbestand bestaat: `find bronnen/[B]/ -name "art[A].json"`.
   - Nee → voer `/wettenbank art. [A] [W]` uit om de wetstekst op te halen.
   - Ja → gebruik bestaand bronbestand; geen nieuwe MCP-aanroep.
2. Controleer of index-JSON bestaat: `find annotaties/[B]/ -name "art[A].json"`.
   - Nee → maak aan.
   - Ja → meld "index-annotatie bestaat al" en stop.
3. Noteer het `pad`-veld uit het bronbestand → structuurpositie.
4. Noteer de peildatum uit `versiedatum` in het bronbestand. Gebruik nooit de datum van vandaag.
5. Extraheer kruisreferenties uit `bronnen/[B]/art[A].kruisrefs.json`.

### Flow B — Lid-annotatie

1. Controleer of index-JSON bestaat: `find annotaties/[B]/ -name "art[A].json"`.
   - Nee → voer Flow A eerst uit.
   - Ja → ga door.
2. Controleer of lid-JSON bestaat: `find annotaties/[B]/ -name "art[A]-lid[L].json"`.
   - Nee → maak aan.
   - Ja → meld "lid-annotatie bestaat al" en stop.
3. Lees de wetstekst voor lid `[L]` uit `bronnen/[B]/art[A].json` (`leden[].tekst` waar `lid == "[L]"`).
4. Peildatum en structuurpositie overnemen uit `annotaties/[B]/art[A].json`. Gebruik nooit een datum uit een lopende MCP-sessie.

### Flow C — Sectie-annotatie

1. Leid `[slug]` af van het `pad`-veld via de slug-transformatietabel.
2. Controleer of bronbestand bestaat: `find bronnen/[B]/ -name "[slug].json"`.
   - Nee → voer `/wettenbank sectie [ref] [W]` uit.
   - Ja → gebruik bestaand bronbestand.
3. Controleer of sectie-JSON bestaat: `find annotaties/[B]/ -name "[slug].json"`.
   - Nee → maak aan.
   - Ja → meld "sectie-annotatie bestaat al" en stop.

---

## Markeren (A2a) — Handleiding §3.4.2a

### Algemene markeringsregels

- **Diagram-gedreven, niet uitputtend**: markeer alleen wetsformuleringen die deel uitmaken van een diagram van een centrale klasse of daarmee samenhangen.
- **Lidwoord altijd meenemen** in de markering.
- **Verwijzing altijd meenemen** als die in het te markeren stukje staat.
- Markeer **precies dat stukje tekst** dat maximaal de betekenis representeert van de klasse die je wilt toekennen.
- **Markeringen mogen overlappen**: dezelfde wetsformulering kan meerdere klassen krijgen; zet elke klasse op een aparte rij.
- **Begin bij de centrale klassen**: start met rechtsbetrekking en rechtsfeit.
- **Start bij de klasse die gecreëerd of afgeleid wordt**, niet bij de context.

### Klasse-specifieke markeringsregels

| JAS-klasse | Wat te markeren |
|-----------|----------------|
| Rechtssubject | Zelfstandig naamwoord voor persoon/entiteit, incl. lidwoord |
| Rechtsobject | Zelfstandig naamwoord voor het voorwerp, incl. lidwoord |
| Rechtsbetrekking | Werkwoord + hulpwerkwoord (kan, mag, is verplicht, dient te) |
| Rechtsfeit | Actieve werkwoordsvorm + tijdsverloop |
| Voorwaarde | Gehele zin of zinsdeel m.i.v. voegwoord (indien, als, tenzij, mits) |
| Afleidingsregel | Volledige als-dan constructie incl. lidwoord, werkwoorden en punt |
| Variabele | Zelfstandig naamwoord (kenmerk) + lidwoord |
| Parameter | Tariefwaarde, drempel, maximum, minimum |
| Tijdsaanduiding | Tijdstip, tijdvak, termijn |
| Plaatsaanduiding | Geografische aanduiding, jurisdictie |
| Delegatiebevoegdheid | Volledige delegatiezin incl. "bij amvb" of "bij ministeriële regeling" |
| Brondefinitie | Volledige aanhef + onderdelen van de begripsomschrijving |
| Operator | Rekenkundig teken of logisch woord (vermeerderd met, EN, OF, NIET) |

---

## Classificeren (A2b) — kaders.md

- **Meest specifieke klasse**: tijdsaanduiding is specifieker dan variabele; plaatsaanduiding is specifieker dan parameter.
- **Interpretatiemethode expliciet benoemen** per element: grammaticaal / systematisch / teleologisch / wetshistorisch.
- **Meerduidigheid of spanning signaleren** als een element meerdere klassificaties verdient.
- **Delegatieketens volledig traceren**: wet → amvb → ministeriële regeling.
- **Alle 13 JAS-elementen intern afvinken** voor volledigheid (niet in output, wel als interne controle).

### De 13 JAS-elementen (intern afvinklijst)

```
☐ rechtssubject
☐ rechtsobject
☐ rechtsbetrekking
☐ delegatiebevoegdheid / delegatie-invulling
☐ rechtsfeit
☐ voorwaarde
☐ afleidingsregel
☐ variabele / variabelewaarde
☐ parameter / parameterwaarde
☐ operator
☐ tijdsaanduiding
☐ plaatsaanduiding
☐ brondefinitie
```

---

## Output — per flow

### Flow A — Annotatie-index JSON

Sla op als `annotaties/[B]/art[A].json`.

```json
{
  "artikel-id": "[B]/art[A]",
  "bwb-id": "[B]",
  "wet": "[citeertitel-afkorting]",
  "artikel": "[A]",
  "peildatum": "[YYYY-MM-DD uit bronbestand versiedatum]",
  "structuurpositie": "[pad-veld uit bronbestand]",
  "leden-annotaties": [],
  "kruisreferenties": ["Art. X W", "..."]
}
```

> **Read-only principe:** De index-JSON is uitsluitend structuurdrager. Vul `leden-annotaties` bij na het aanmaken van elke lid-annotatie.

### Flow B — Lid-annotatie JSON

Sla op als `annotaties/[B]/art[A]-lid[L].json`.

```json
{
  "annotatie-id": "[B]/art[A]/lid[L]",
  "bwb-id": "[B]",
  "wet": "[citeertitel-afkorting]",
  "artikel": "[A]",
  "lid": "[L]",
  "peildatum": "[YYYY-MM-DD — overnemen uit index-JSON]",
  "structuurpositie": "[structuurpositie index-JSON] > Lid [L]",
  "wetstekst": "[tekst van uitsluitend dit lid, letterlijk]",
  "annotatierijen": [
    {
      "rij-id": "r-001",
      "markering": "[citaat incl. lidwoord en verwijzingen]",
      "jas-klasse": "[klasse]",
      "interpretatiemethode": "[grammaticaal|systematisch|teleologisch|wetshistorisch]",
      "begrip-id": "[B]/art[A]/lid[L]/[slug]",
      "toelichting-klasse": "[motivering klassekeuze; meerduidigheid benoemen]",
      "signalering": null
    }
  ],
  "diagram": {
    "centrale-klasse": "[jas-klasse van de centrale knoop]",
    "knopen": [
      { "id": "RB", "jas-klasse": "rechtsbetrekking", "label": "rechtsbetrekking 'invorderbaar'", "begrip-id": null }
    ],
    "kanten": [
      { "van": "RF", "naar": "RB", "label": "triggert" }
    ]
  },
  "kruisreferenties": [],
  "delegatiestructuur": []
}
```

**kruisreferenties** — per gevonden wetsverwijzing één object:
```json
{
  "doel-bwb-id": "BWBR0002715",
  "doel-artikel": "4:6",
  "doel-lid": "1",
  "richting": "forward",
  "confidence": 0.9,
  "ruwe-tekst": "artikel 4:6, eerste lid, Awb"
}
```
`richting`: `forward` = dit lid verwijst naar het doelartikel; `backward` = doelartikel verwijst naar dit lid; `intern` = verwijzing binnen dezelfde wet. `doel-lid`, `ruwe-tekst` zijn optioneel.

**delegatiestructuur** — optioneel: alleen opnemen als het lid een delegatiebevoegdheid bevat. Bij afwezigheid: veld weglaten of `[]`.

**Annotatierijen-regels:**
- Nummerering `rij-id` begint bij `r-001` per lid-annotatie.
- Overlappende markeringen (één tekstfragment in meerdere JAS-klassen): één rij per klasse, zelfde markering mag herhalen. Noteer alternatieve klasse in `toelichting-klasse`.
- `signalering`: gebruik `null` als er geen bijzonderheden zijn; gebruik een string bij meerduidigheid, spanning of open normen.

**Diagram-regels:**
- Construeer diagram als JSON (knopen + kanten) — Mermaid wordt gegenereerd door `generate_views.py`.
- Centrale knoop: kies conform `kaders.md §Centrale klasse` (1. Rechtsbetrekking → 2. Rechtsfeit → 3. Afleidingsregel → 4. Voorwaarde).
- Knoop-id's: korte uppercase codes (RB, RF, RO, VW, AR, TA, …).
- Label-tekst: `"[jas-klasse] '[markering ingekort tot max. 40 tekens]'"`.
- `begrip-id` in knoop: vul in als de knoop direct overeenkomt met een begrip-slug; anders `null`.

Na aanmaken: voeg `"[B]/art[A]/lid[L]"` toe aan `leden-annotaties` in de index-JSON. Lijst altijd gesorteerd op oplopend lidnummer.

### Flow C — Sectie-annotatie JSON

Sla op als `annotaties/[B]/[slug].json`. Gebruikt hetzelfde formaat als lid-annotatie, maar:
- `annotatie-id`: `"[B]/[slug]"`
- `lid`: `""` (leeg)
- Geen apart index-JSON-bestand voor sectie-bronnen.

### Begrip-stubs (YAML) — alle flows

Maak per annotatierij een begrip-YAML aan in `begrippen/[slug].yaml`. **Vul uitsluitend de kernvelden in** — definitie en relaties blijven leeg (dat doet `/begrip`).

**Begripsnaam-vuistregels:** zie `/begrip` §Begripsnaam-vuistregels — dat is de canonieke bron. Enige regel die al tijdens `/annoteer` geldt: **hergebruik** een bestaande begripsnaam als de unieke betekenis identiek is.

YAML-formaat per begrip-stub:
```yaml
begrip-id: [B]/art[A]/lid[L]/[slug]
begripsnaam: [slug]
aliases: []
soort: ""
soort-id: false
jas-klasse: [klasse]      # JAS-classificatie uit annotatierij; bepaalt kleur codering in kennisgraaf
toelichting-klasse: ""    # juridische motivering van JAS-klassekeuze
herkomst: direct          # afgeleid bij JAS-klasse: afleidingsregel
status: concept
definitie:
  kern: ""
  contexten: []
definitie-versie: 1
definitie-gebaseerd-op:
- m-001
markeringen:
- markering-id: m-001
  bron-annotatie-id: [B]/art[A]/lid[L]
  tekst: "[letterlijk geciteerd incl. lidwoord en verwijzingen]"
  interpretatiemethode: [grammaticaal|systematisch|teleologisch|wetshistorisch]
  bijdrage: primair
  bevestigd: false
  bevestigd-op: null
geldigheid-van: "[YYYY-MM-DD uit bronbestand versiedatum]"
geldigheid-tot: null
vervangen-door: null
relaties:
  is-een: []
  heeft: []
  leidt-tot: []
identificatiebegrip: false
afleidingsregel-id: null
tussenresultaat: false
```

**Hergebruik van een bestaand begrip:** als de begripsnaam al bestaat in `begrippen/`, voeg een tweede markering toe aan de bestaande YAML (`markering-id: m-002`, `bijdrage: context` tenzij de nieuwe bron een sterkere claim heeft). Meld dit als hergebruikte begrip in de hergebruiksrapportage. Voeg het begrip toe aan `rapporten/enrichment-queue.json` als de nieuwe markering afwijkt van de bestaande definitie.

> **Valkuil — herkomst bij JAS-klasse afleidingsregel**
> Bij JAS-klasse `afleidingsregel`: zet `herkomst: afgeleid`. Bij alle andere klassen: zet `herkomst: direct`.

---

## Delegatiestructuur (alle flows)

Vul `delegatiestructuur` in de annotatie-JSON als een array van objecten:
```json
[
  {
    "omschrijving": "[bevoegdheidsomschrijving]",
    "vindplaats": "Art. [A] lid [L] [W]",
    "type": "Verplicht|Facultatief",
    "invulling": "[naam regeling of null]",
    "vindplaats-invulling": "[artikel regeling of null]"
  }
]
```
Bij geen delegatie: gebruik `[]`.

Als een gedelegeerde regeling niet opvraagbaar is via MCP: stel `"invulling": "Niet beschikbaar via wettenbank — handmatige verificatie vereist"`.

---

## Validatie en views (na elk schrijfcommando)

Na het aanmaken of bijwerken van annotatie-JSON én begrip-YAML bestanden:

```
cd "$CLAUDE_PROJECT_DIR" && tools/.venv/bin/python tools/validate_note.py --file annotaties/[B]/art[A]-lid[L].json
```

Bij blokkerende fouten (L1/L2): herstel en hervalideer vóór je verdergaat. L3-waarschuwingen rapporteren aan de gebruiker maar blokkeren niet.

---

## Kwaliteitseisen (niet-onderhandelbaar)

- Wetstekst altijd volledig en letterlijk citeren — nooit parafraseren.
- Peildatum altijd uit het bronbestand (`versiedatum`), nooit de datum van vandaag.
- Structuurpositie altijd letterlijk uit het `pad`-veld in het bronbestand.
- Begrip-stubs bevatten na `/annoteer` een lege kern (`definitie: {kern: "", contexten: []}`); A3-inhoud is taak van `/begrip`.
- `markering.tekst` bevat altijd het letterlijke citaat inclusief lidwoord.
- `begrip-id` URI is deterministisch: `{bwb-id}/art{N}/lid{L}/{slug}`.
- Index-JSON is uitsluitend structuurdrager — nooit annotatierijen of diagrammen.
- Delegatieketens volledig uitwerken — alle schakels ophalen via MCP.

---

## Verplichte checklist-output na elke annotatie-run

Print na het opslaan:

**Flow A:**
```
Artikel-index-checklist — Art. [A] [W]
✅/⬜ index-JSON aangemaakt in annotaties/[B]/art[A].json
✅/⬜ peildatum uit bronbestand (versiedatum)
✅/⬜ structuurpositie letterlijk uit pad-veld
✅/⬜ kruisreferenties gevuld vanuit bronnen/[B]/art[A].kruisrefs.json
✅/⬜ delegatiestructuur beschreven (optioneel — alleen bij delegatiebevoegdheden)
✅/⬜ validatie geslaagd (validate_note.py)
```

**Flow B:**
```
Lid-annotatie-checklist — Art. [A] lid [L] [W]
✅/⬜ lid-JSON aangemaakt in annotaties/[B]/art[A]-lid[L].json
✅/⬜ wetstekst lid [L] volledig en letterlijk geciteerd
✅/⬜ alle 13 JAS-elementen intern afgevinkt
✅/⬜ diagram aangemaakt (centrale-klasse + knopen + kanten; weglaten alleen als geen van de 4 centrale JAS-klassen aanwezig is)
✅/⬜ begrip-YAML-stubs aangemaakt per annotatierij
✅/⬜ leden-annotaties bijgewerkt in index-JSON (pad-notatie: "BWBR0004770/art9/lid1")
✅/⬜ validatie geslaagd (validate_note.py)
```

**Flow C:**
```
Sectie-annotatie-checklist — [ref] [W]
✅/⬜ sectie-JSON aangemaakt in annotaties/[B]/[slug].json
✅/⬜ wetstekst sectie volledig en letterlijk geciteerd
✅/⬜ alle 13 JAS-elementen intern afgevinkt
✅/⬜ annotatierijen ingevuld
✅/⬜ diagram aangemaakt
✅/⬜ delegatiestructuur beschreven (optioneel — alleen bij delegatiebevoegdheden)
✅/⬜ begrip-YAML-stubs aangemaakt per annotatierij
✅/⬜ validatie geslaagd (validate_note.py)
✅/⬜ views gegenereerd (generate_views.py)
```

---

## Hergebruiksrapportage

Print aan het einde van elke annotatie-run:

**Hergebruikte begrippen (definitie mogelijk bijstellen):**
- `begrippen/[slug].yaml` — primaire bron: [bron-annotatie-id]; nieuw ook geannoteerd in Art. [A] lid [L] [W]

**Voer `/begrip [slug]` niet automatisch uit vanuit deze skill.** Rapporteer als actievelijst.

Als er geen hergebruikte begrippen zijn: schrijf exact "Geen hergebruikte begrippen."

### Soort-consistentiecheck bij hergebruik (verplicht)

| soort in bestaand begrip | Signaal in nieuwe context | Actie |
|--------------------------|--------------------------|-------|
| `booleaans` | het begrip werkt in de nieuwe context per element (bijv. per termijn) | ⚠ signaleer in `toelichting-klasse`: "hergebruikt begrip is binair; in deze context werkt het per [element] — overweeg nieuw begrip" |
| Elk soort | het soort is passend | — |

Noteer de uitkomst in `toelichting-klasse` van de annotatierij.
