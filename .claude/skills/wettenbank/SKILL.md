---
description: Haal wetstekst op via de wettenbank MCP en extraheer kruisreferenties. Gebruik: /wettenbank art. 25 IW 1990
context: fork
agent: general-purpose
---

# /wettenbank — Dataverwerving

**Argument:** `$ARGUMENTS`

Voer onderstaande stappen uit. Het doel is alle wetstekst, structuurdata en kruisreferenties beschikbaar te stellen voor de analyse-skills.

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

**Structuurcontext:** als `pad` afwezig is in de response voor `[A]`: roep `wettenbank_structuur(bwbId=[B])` aan en zoek het knooppunt voor artikel `[A]` in de `structuur`-array. Geeft ook dat geen resultaat: noteer "Structuurpositie niet beschikbaar".

**Lid-niveau controle:** tel `leden.length` in de response voor `[A]`.
- Als `[L]` niet opgegeven EN `leden.length > 3`: stop. Meld: *"Art. [A] [W] heeft [N] leden. Specificeer een lid: `/jas art. [A] lid [N] [W]`"* en lijst alle beschikbare lidnummers op.
- Anders: ga door.

Noteer uit `[BD]` alle begripsomschrijvingen voor termen in artikel `[A]` als `[brondefinities]`.

---

## Stap 3 — Kruisreferenties extraheren

Lees `$CLAUDE_SKILL_DIR/verwijzingen.md` volledig. Voer het protocol uit op alle `leden[].tekst`-velden van artikel `[A]`.

**Parallel aanroepen (op basis van het JSON-model):**

1. `wettenbank_artikel(bwbId=[B], artikel=<nr>)` voor elk uniek intern `(doel_bwbId, doel_artikel)`-paar waarbij `doel_artikel` niet null is.
2. `wettenbank_artikel(bwbId=<doel_bwbId>, artikel=<doel_artikel>)` voor elk uniek extern paar waarbij `doel_artikel` niet null is.
3. `wettenbank_zoekterm(bwbId=[B], zoekterm="artikel [A]")` voor omgekeerde kruisreferenties. Voer daarna het verificatieprotocol uit (zie `verwijzingen.md` Omgekeerde kruisreferenties).

Sla na deduplicatie alle unieke `"Art. <doel_artikel> <wet-afkorting>"`-strings op als `[kruisrefs]` (lege array bij geen kruisreferenties).

---

## Resultaat

Retourneer als intern datamodel voor gebruik door de aanroepende skill:

```
[A], [W], [B], [L], [BD], [PD]
wetstekst artikel [A]: leden[]-array
structuurpositie: pad-string
brondefinities: [brondefinities]
kruisrefs JSON-model: [...]
[kruisrefs]: ["Art. X W", ...]
bronreferenties: { artikel: jci-uri, ... }
```
