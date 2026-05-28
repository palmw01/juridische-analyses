---
name: wettenbank
description: "Haal wetstekst op via de wettenbank MCP en sla genormaliseerd op in bronnen/. Gebruik: /wettenbank art. 25 IW 1990"
context: fork
agent: general-purpose
---

# /wettenbank — Dataverwerving

## Trigger

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

Schrijf de ruwe MCP-response **nooit** rechtstreeks naar `bronnen/` — gebruik altijd `fetch_wettenbank.py` voor normalisatie.

Als `bronnen/[B]/art[A].json` al bestaat en de versiedatum gelijk is: meld "bronbestand actueel, geen update nodig" en ga door.

Anders: schrijf de ruwe MCP-response naar een tijdelijk bestand en roep de normalisatietool aan:

```bash
# 1. Sla ruwe response op (vervang de JSON door de werkelijke MCP-response)
echo '<ruwe-mcp-response-json>' > /tmp/mcp-art[A].json

# 2. Normaliseer en sla op in bronnen/
tools/.venv/bin/python tools/fetch_wettenbank.py \
  --input /tmp/mcp-art[A].json \
  --project-dir . \
  [--force]   # alleen toevoegen als het bestand al bestaat en overschreven mag worden

# 3. Opruimen
rm /tmp/mcp-art[A].json
```

Het script zet `bwbId` om naar `bwb-id`, voegt `opgehaald-op` toe en geeft `sectie`/`formaat` door. Het uitvoerbestand wordt automatisch geplaatst op `bronnen/[B]/art[A].json`.

---

## Stap 4 — Kruisreferenties extraheren

Lees `$CLAUDE_SKILL_DIR/verwijzingen.md` volledig. Voer het protocol uit op alle `leden[].tekst`-velden van artikel `[A]`.

**Parallel aanroepen (op basis van het JSON-model):**

1. `wettenbank_artikel(bwbId=[B], artikel=<nr>)` voor elk uniek intern `(doel-bwb-id, doel-artikel)`-paar waarbij `doel-artikel` niet null is.
2. `wettenbank_artikel(bwbId=<doel-bwb-id>, artikel=<doel-artikel>)` voor elk uniek extern paar waarbij `doel-artikel` niet null is.
3. `wettenbank_zoekterm(bwbId=[B], zoekterm="artikel [A]")` voor omgekeerde kruisreferenties. Voer daarna het verificatieprotocol uit (zie `verwijzingen.md` Omgekeerde kruisreferenties).

Sla na deduplicatie alle unieke kruisreferentie-records op als `bronnen/[B]/art[A].kruisrefs.json`. Het kruisreferentie-formaat (`doel-bwb-id`, `doel-artikel`, optioneel `doel-lid`, `richting`, `confidence`, `ruwe-tekst`) is gedefinieerd in `schemas/annotatie-lid.schema.json` onder `kruisreferenties[]` — die wordt door `annoteer-classificeer` gemigreerd naar de annotatie-lid-JSON. Bestaande `.kruisrefs.json`-bestanden in `bronnen/` volgen hetzelfde formaat.

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
