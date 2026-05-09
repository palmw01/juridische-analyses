---
description: "Haal wetstekst op via de wettenbank MCP en sla genormaliseerd op in bronnen/. Gebruik: /wettenbank art. 25 IW 1990"
context: fork
agent: general-purpose
---

# /wettenbank — Dataverwerving

## Triggervormen

| Trigger | Wanneer gebruiken |
|---------|-------------------|
| `/wettenbank art. [A] [W]` | Volledige wetstekst + kruisreferenties voor een artikel ophalen |
| `/wettenbank art. [A] lid [L] [W]` | Wetstekst beperkt tot één lid ophalen |

**Argument:** `$ARGUMENTS`

Voer onderstaande stappen uit. Het doel is alle wetstekst, structuurdata en kruisreferenties beschikbaar stellen als genormaliseerde JSON-bestanden in `bronnen/`.

---

## Stap 1 — Argument parsen

Parseer `$ARGUMENTS`:

- **`[A]`**: artikelnummer na "art." inclusief eventuele letters (9, 25, 36, 2a). Als een specifiek lid is vermeld (bijv. "lid 3"), noteer als `[L]`; anders `[L]` = volledig artikel.
- **`[W]`** en **`[B]`**: wet en BWB-id — raadpleeg `$CLAUDE_SKILL_DIR/bwb-mapping.md`.
- **`[BD]`**: begripsbepalings-artikel voor `[W]` — zie kolom "Begripsbepalings-art." in `bwb-mapping.md`.

Noteer: `[A]`, `[W]`, `[B]`, `[L]`, `[BD]`.

---

## Stap 2 — Wetstekst ophalen (parallel)

Roep tegelijk aan:
- `wettenbank_artikel(bwbId=[B], artikel=[A])` — te analyseren artikel
- `wettenbank_artikel(bwbId=[B], artikel=[BD])` — begripsbepalingen

Extraheer per response:
- `citeertitel` — naam van de wet
- `versiedatum` — peildatum `[PD]`
- `leden` — array `{ lid, tekst }` per genummerd lid
- `pad` — structuurpositie als `"Hoofdstuk X > Afdeling Y > Artikel Z"`
- `sectie` — artikellabel
- `formaat` — `"plain"` of `"markdown"`
- `bronreferentie` — JCI-uri

**Structuurcontext:** als `pad` afwezig is: roep `wettenbank_structuur(bwbId=[B])` aan en zoek het knooppunt voor artikel `[A]` in de `structuur`-array.

**Lid-niveau controle:** tel `leden.length` in de response voor `[A]`.
- Als `[L]` niet opgegeven EN `leden.length > 3`: stop. Meld: *"Art. [A] [W] heeft [N] leden. Specificeer een lid: `/wettenbank art. [A] lid [N] [W]`"* en lijst alle beschikbare lidnummers op.
- Anders: ga door.

Noteer uit `[BD]` alle begripsomschrijvingen voor termen in artikel `[A]` als `[brondefinities]`.

---

## Stap 3 — MCP-response opslaan

Sla de ruwe MCP-response voor artikel `[A]` op als JSON in `bronnen/[B]/art[A].json`.

Maak de map aan als die nog niet bestaat: `mkdir -p bronnen/[B]/`.

Formaat:
```json
{
  "bwb-id": "[B]",
  "artikel": "[A]",
  "opgehaald-op": "[datum van vandaag, YYYY-MM-DD]",
  "versiedatum": "[PD]",
  "citeertitel": "[citeertitel]",
  "bronreferentie": "[JCI-uri]",
  "pad": "[pad-string]",
  "leden": [{ "lid": "1", "tekst": "..." }, ...]
}
```

Als `bronnen/[B]/art[A].json` al bestaat en de versiedatum gelijk is: meld "bronbestand actueel, geen update nodig" en ga door.

---

## Stap 4 — Kruisreferenties extraheren

Lees `$CLAUDE_SKILL_DIR/verwijzingen.md` volledig. Voer het protocol uit op alle `leden[].tekst`-velden van artikel `[A]`.

**Parallel aanroepen (op basis van het JSON-model):**

1. `wettenbank_artikel(bwbId=[B], artikel=<nr>)` voor elk uniek intern `(doel_bwbId, doel_artikel)`-paar waarbij `doel_artikel` niet null is.
2. `wettenbank_artikel(bwbId=<doel_bwbId>, artikel=<doel_artikel>)` voor elk uniek extern paar waarbij `doel_artikel` niet null is.
3. `wettenbank_zoekterm(bwbId=[B], zoekterm="artikel [A]")` voor omgekeerde kruisreferenties. Voer daarna het verificatieprotocol uit (zie `verwijzingen.md` Omgekeerde kruisreferenties).

Sla na deduplicatie alle unieke kruisreferentie-records op als `bronnen/[B]/art[A].kruisrefs.json`:
```json
[
  {
    "doel-bwb-id": "...",
    "doel-artikel": "...",
    "richting": "forward|backward|intern",
    "confidence": 0.9,
    "ruwe-tekst": "..."
  }
]
```

---

## Resultaat

Retourneer als intern datamodel voor gebruik door de aanroepende skill:

```
[A], [W], [B], [L], [BD], [PD]
wetstekst artikel [A]: leden[]-array (uit bronnen/[B]/art[A].json)
structuurpositie: pad-string
brondefinities: [brondefinities]
kruisrefs JSON-model: (uit bronnen/[B]/art[A].kruisrefs.json)
bronreferentie: [JCI-uri]
```
