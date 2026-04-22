---
description: Voer een volledige JAS-annotatie (v1.0.10) uit op een wetsbepaling en sla het rapport op als MD-bestand. Gebruik: /jas art. 25 IW 1990 of /jas art. 36 lid 4 IW 1990
context: fork
agent: general-purpose
---

# /jas — JAS-annotatie Wetsbepaling

**Artikel:** `$ARGUMENTS`

Voer onderstaande stappen strikt in volgorde uit. Wijk niet af van de voorgeschreven formats.

---

## Stap 1 — Lees bij aanvang

Lees deze twee bestanden volledig vóór enige andere actie:
- `$CLAUDE_SKILL_DIR/kaders.md` — JAS v1.0.10 taxonomie en annotatieprincipes
- `$CLAUDE_SKILL_DIR/rapportformat.md` — §1–§11 structuur, kwaliteitseisen, pre-save checklist

---

## Stap 2 — Argument parsen

Parseer `$ARGUMENTS` en stel vast:

**Artikelnummer `[A]`**: het nummer na "art." inclusief eventuele letters (9, 25, 36, 2a). Als een specifiek lid is vermeld (bijv. "lid 3"), noteer dit als `[L]`; anders geldt `[L]` = het volledige artikel.

**Wet `[W]` en BWB-id `[B]`**:

| Invoer | [W] | [B] | [BD] begripsbepalings-artikel |
|--------|-----|-----|-------------------------------|
| IW 1990 / Invorderingswet 1990 | Invorderingswet 1990 | BWBR0004770 | 3 |
| AWR | Algemene wet inzake rijksbelastingen | BWBR0002320 | 2 |
| Awb | Algemene wet bestuursrecht | BWBR0005537 | 1:1 |
| UB IW 1990 / Uitvoeringsbesluit IW 1990 | Uitvoeringsbesluit Invorderingswet 1990 | BWBR0004772 | 1 |

Geen herkenbare wet: gebruik IW 1990 (`BWBR0004770`) als standaard en vermeld dit in het rapport.

Noteer: `[A]`, `[W]`, `[B]`, `[L]`, en het begripsbepalings-artikel `[BD]`.

---

## Stap 3 — Bestaande annotatie controleren

Controleer nu `[A]` bekend is of er al een annotatie bestaat voor dit artikel:

1. Lees `analyses/INDEX.md` om snel te zien of het artikel al behandeld is.
2. Als niet gevonden in de index: Zoek met `Glob` naar `analyses/*-art[A]-*` (vervang `[A]` met het artikelnummer uit Stap 2).
3. Als een bestaand rapport gevonden wordt:
   - Lees het rapport via de Read tool.
   - Meld aan de gebruiker: "Bestaande annotatie gevonden: [bestandsnaam]. Wetstekst geldig per [peildatum uit frontmatter]. Gebruik je deze als basis of wil je een nieuwe annotatie opstellen?"
   - **Wacht op bevestiging.** Ga alleen verder met de workflow als de gebruiker een nieuwe annotatie vraagt of als de bestaande annotatie verouderd is (andere peildatum).
4. Als geen bestaand rapport gevonden wordt: ga door met Stap 4.

---

## Stap 4 — Wetstekst ophalen en artikelen extraheren

**Parallel aanroepen via MCP:**

Roep tegelijk aan:
- `wettenbank_artikel(bwbId=[B], artikel=[A])` — te annoteren artikel
- `wettenbank_artikel(bwbId=[B], artikel=[BD])` — begripsbepalingen

De tool-resultaten zijn **JSON**. Extraheer per response de volgende velden:
- `citeertitel` — naam van de wet (bijv. `"Invorderingswet 1990"`)
- `versiedatum` — geldigheidspeildatum van de opgehaalde versie (YYYY-MM-DD); noteer als `[PD]`
- `leden` — array van objecten `{ lid: string, tekst: string }` per genummerd lid; gebruik dit voor de annotatie per lid (§4); leeg `[]` als het artikel geen genummerde leden heeft. **Bouw de volledige artikeltekst op door `leden[].tekst` in volgorde samen te voegen.**
- `pad` — hiërarchisch pad als compacte string gescheiden door ` > ` (bijv. `"Hoofdstuk II > Afdeling 1 > Artikel 9"`); gebruik dit voor structuurcontext in §2. Splits op ` > ` om de structuurketen te reconstrueren. Afwezig als het artikel geen structuurancestors heeft.
- `sectie` — artikellabel (bijv. `"Artikel 9"`); gebruik als label in §1-header
- `formaat` — `"plain"` of `"markdown"`; geeft aan of de tekst Markdown-opmaak bevat
- `bronreferentie` — JCI-uri (bijv. `"jci1.3:c:BWBR0004770&artikel=25"`); gebruik letterlijk in Bijlage B

**Structuurcontext:** gebruik het `pad`-veld (string) voor §1 (structuurpositie in de header) en §2 (Structuurdiagram). **Neem nooit een hoofdstuk- of afdelingstitel aan op basis van de artikelinhoud.** Als `pad` afwezig is: roep `wettenbank_structuur(bwbId=[B])` aan en zoek in de `structuur`-array het knooppunt op dat overeenkomt met artikel `[A]`; gebruik de ancestor-knooppunten als structuurpositie. Geeft ook dat geen resultaat: noteer "Structuurpositie niet beschikbaar" in §2.

Noteer uit `[BD]` alle begripsomschrijvingen die betrekking hebben op termen in artikel `[A]`.

**Gebruik altijd de `artikel`-parameter — nooit de volledige wet ophalen.**

---

## Stap 5 — Art. 1 IW 1990 + Leidraad ophalen (conditioneel)

**Alleen als `[W]` = Invorderingswet 1990 of Uitvoeringsbesluit IW 1990:**

Roep parallel aan:
- `wettenbank_artikel(bwbId="BWBR0004770", artikel="1")` — tenzij `[A]` = 1 (dan al beschikbaar uit Stap 4). Gebruik de `leden`-array (JSON) en noteer de letterlijke tekst van art. 1 lid 2 IW 1990 (de Awb-uitsluitingsclausule) uit het lid-object met `lid: "2"`.
- `wettenbank_artikel(bwbId="BWBR0024096", artikel=[A])` — het Leidraad-artikel met hetzelfde nummer als het te annoteren artikel. Gebruik de `leden`-array (JSON). De Leidraad is een beleidsregel (type: beleidsregel), geen wet, maar verplichte bron voor §8 van het rapport. Als het `fout`-veld aanwezig is (artikel niet gevonden): roep aansluitend `wettenbank_zoekterm(bwbId="BWBR0024096", zoekterm="artikel [A]")` aan en gebruik het eerste trefferresultaat als Leidraad-bron voor §8. Als ook dat geen resultaat oplevert: noteer dit en sla §8 over.

**Nooit:** `BWBR0004800` (Leidraad invordering 1990, verlopen per 2005-07-12).

**Als `[W]` ≠ IW 1990 en ≠ UB IW:** sla Stap 5 over.

---

## Stap 6 — Kruisreferenties extraheren

Scan de in Stap 4 verkregen artikeltekst op expliciete verwijzingen. Neem uitsluitend verwijzingen op die **letterlijk in de tekst staan** als "artikel X", "artikel X, lid Y", "artikel X, onderdeel Y". Geen verwijzingen toevoegen op basis van eigen kennis.

Maak twee lijsten:
- **Intern**: verwijzingen naar artikelen binnen dezelfde wet `[W]`
- **Extern**: verwijzingen naar artikelen in andere wetten

**Parallel aanroepen:**

1. Roep `wettenbank_artikel(bwbId=[B], artikel=<nr>)` aan voor elk **intern** gerefereerd artikel.
2. Roep `wettenbank_artikel(bwbId=<id>, artikel=<nr>)` aan voor elk **extern** gerefereerd artikel.
3. Roep `wettenbank_zoekterm(bwbId=[B], zoekterm="artikel [A]")` aan om **omgekeerde kruisreferenties** te vinden: artikelen binnen dezelfde wet die verwijzen naar art. `[A]`. Verwerk de `artikelen`-array uit de response: noteer per treffer het artikelnummer en het aantal treffers. Dit levert de lijst van articles die afhankelijk zijn van of verwijzen naar art. `[A]`.

Alle drie de groepen aanroepen parallel uitvoeren.

Gebruik de `leden`-array (JSON) van elke response voor inhoudelijke annotatie; gebruik `bronreferentie` voor Bijlage B.

BWB-ids: IW 1990 = BWBR0004770 | UB IW = BWBR0004772 | AWR = BWBR0002320 | Awb = BWBR0005537 | Leidraad 2008 = BWBR0024096

Vervallen artikelen worden door de MCP gefilterd — gaten in nummering zijn normaal.

**Wiki-links voor Obsidian:** schrijf in de kolom "Verwijst naar" van §7.1, §7.2 en in de kolom "Verwijzend artikel" van §7.4 elk artikel als wiki-link: `[[Art. Z IW 1990]]`, `[[Art. Z Awb]]`, etc. Gebruik de korte wet-afkorting (IW 1990, Awb, AWR, LI 2008), niet de volledige wetnaam.

**Kruisreferenties voor frontmatter:** sla na het invullen van §7.1, §7.2 en §7.4 alle referentie-strings op als `[kruisrefs]` — een lijst van strings zónder `[[]]`, bijv. `["Art. 2 IW 1990", "Art. 1 IW 1990", "Art. 4:86 Awb"]`. Gebruik `[kruisrefs]` in Stap 11 voor het frontmatter-veld `kruisreferenties`. Bij geen kruisreferenties: lege array `[]`.

---

## Stap 7 — JAS-annotatie uitvoeren

Gebruik de definities, herkenningsvragen en taalkenmerken uit `$CLAUDE_SKILL_DIR/kaders.md`. Voer de annotatie uit op de wetstekst van artikel `[A]` uit Stap 4, aangevuld met de brondefinities uit Stap 4.

**Interne annotatiestap (niet opnemen in rapportoutput):** loop de 13 JAS-elementen af en bepaal per element of het aanwezig is in het artikel: rechtssubject, rechtsobject, rechtsbetrekking, rechtsfeit, voorwaarde, afleidingsregel, variabele/variabelewaarde, parameter/parameterwaarde, operator, tijdsaanduiding, plaatsaanduiding, delegatiebevoegdheid/delegatie-invulling, brondefinitie. Noteer per aanwezig element de vindplaats in het artikel.

**Annotatieprincipes:**
1. Citeer het exacte zinsdeel letterlijk bij elk geclassificeerd element.
2. Kies altijd de meest specifieke JAS-klasse: tijdsaanduiding > variabele; plaatsaanduiding > parameter.
3. Benoem per JAS-element de interpretatiemethode: grammaticaal / systematisch / teleologisch.
4. Markeer meerduidigheid of alternatieve classificaties expliciet in de toelichting.
5. Traceer delegatieketens volledig: wet → amvb → ministeriële regeling; haal alle schakels op.

**Structuur van de annotatietabel:** maak één subsectie per lid van het artikel. Nummer de annotaties doorlopend over alle leden. Gebruik als kolomnamen: Nr | Formulering (letterlijk geciteerd) | JAS-element | Toelichting.

**Inhoud van de Toelichting-kolom:**
1. Interpretatiemethode (grammaticaal / systematisch / teleologisch)
2. Reden voor keuze van deze JAS-klasse boven alternatieven
3. Meerduidigheid of alternatieve classificatie (indien van toepassing)

---

## Stap 8 — Afleidingsregels en rekenstructuur uitwerken

Op basis van de in Stap 7 geclassificeerde afleidingsregels:

**Beslisregels:** stel per beslisregel de voorwaardenstructuur op (EN/OF/NIET), de uitvoervariabele (ja/nee) en de vindplaats.

**Rekenregels:** stel per rekenregel de formule op met invoervariabelen, uitvoervariabele en vindplaats. Geef een cijfervoorbeeld als de rekenregel niet-triviaal is.

**Parameters:** noteer alle vaste waarden die voor alle rechtssubjecten gelijk zijn (tarieven, termijnen, percentages, drempelbedragen).

---

## Stap 9 — Awb-toepasselijkheidscheck (conditioneel)

**Alleen als `[W]` = IW 1990:** stel per gevonden Awb-artikel (Stap 6, extern) vast of de betreffende Awb-titel van toepassing is op grond van art. 1 lid 2 IW 1990 (Stap 5). Citeer art. 1 lid 2 letterlijk. Vermeld per Awb-titel: van toepassing / uitgesloten / geen expliciete uitzondering met reden.

**Als `[W]` ≠ IW 1990:** sla Stap 9 over.

---

## Stap 10 — Kwaliteitscheck

Doorloop de pre-save checklist in `$CLAUDE_SKILL_DIR/rapportformat.md` volledig vóór opslaan. Alle punten moeten afgevinkt zijn of voorzien van een expliciete toelichting waarom een punt niet van toepassing is.

---

## Stap 11 — Frontmatter bepalen, timestamp ophalen en rapport opslaan

**Frontmatter-uitbreidingen bepalen (vóór opslaan):**

1. **tags** (zie rapportformat.md voor invulregels):
   - Altijd: `jas-annotatie`
   - Wet-tag: `[W]` → lowercase afkorting: IW 1990 → `iw1990`; AWR → `awr`; Awb → `awb`; LI 2008 → `li2008`; UB IW 1990 → `ubiw1990`
   - Artikel-tag: `art` + artikelnummer, `.` en `:` → `-`: art. 9 → `art9`; art. 4:86 → `art4-86`; art. 24.4 → `art24-4`; gecombineerd "9.1 en 9.5" → `art9-1` + `art9-5`
2. **aliases**: `"Art. [A] [wet-afkorting] ([datum])"` — bijv. `"Art. 9 lid 1 IW 1990 (2026-04-21)"`
3. **kruisreferenties**: gebruik de `[kruisrefs]`-lijst uit Stap 7 (lege array `[]` bij geen kruisreferenties)

Sla `[hub-pad]` op voor Stap 12b: `wetsartikelen/[wet-afkorting]/art-[nummer].md` waarbij `[nummer]` = artikelnummer met `.` en `:` vervangen door `-` (art. 9 → `art-9`; art. 4:86 → `art-4-86`; gecombineerd "9.1 en 9.5" → `art-9-1en9-5`).

---

Haal de timestamp op via `date +%Y-%m-%d_%H-%M-%S`. Sla het rapport op als:

```
analyses/jas-annotatie-art[A]-[afkorting wet]-[TIMESTAMP].md
```

Voorbeelden:
- `analyses/jas-annotatie-art25-IW1990-2026-04-02_14-30-00.md`
- `analyses/jas-annotatie-art36lid4-IW1990-2026-04-02_14-30-00.md`

Regels voor de bestandsnaam: geen spaties; "art. " → "art"; "lid " → "lid"; IW 1990 → "IW1990"; AWR → "AWR"; Awb → "Awb"; UB IW 1990 → "UBIW1990".

Genereer het rapport conform de structuur in `$CLAUDE_SKILL_DIR/rapportformat.md`. De sectienummers en koppen zijn exact en mogen niet worden gewijzigd.

---

## Stap 12 — INDEX.md bijwerken

Voeg het nieuwe rapport toe aan `analyses/INDEX.md` onder de juiste wet:
- Gebruik het format: `- [Art. [A] (versie X)](./jas-annotatie-...) (YYYY-MM-DD)`
- Als de wet nog niet in de index staat: voeg een nieuwe kop `## [Wet]` toe.
- Update de regel `*Laatste update: YYYY-MM-DD*` onderaan het bestand.

---

## Stap 12b — Hub-note aanmaken

Controleer of `[hub-pad]` (bepaald in Stap 11) al bestaat via de Read-tool.

**Als het bestand niet bestaat:** maak het aan met onderstaande structuur. Vul `[A]`, `[wet-afkorting]`, `[volledige wetnaam (BWB-id)]`, `[wet-afkorting-lowercase]` en `[nummer]` in met de waarden uit Stap 2 en 11. Noteer het pad als `[hub-nieuw]` = true voor Stap 13.

```markdown
---
type: wetsartikel-hub
artikel: Art. [A] [wet-afkorting]
wet: [volledige wetnaam (BWB-id)]
aliases:
  - "Art. [A] [wet-afkorting]"
tags:
  - wetsartikel
  - [wet-afkorting-lowercase]
  - art[nummer]
---

# Art. [A] — [volledige wetnaam]

## Alle annotaties

\`\`\`dataview
TABLE datum AS "Analysedatum", peildatum AS "Peildatum", jas-versie AS "JAS"
FROM "analyses"
WHERE type = "jas-annotatie" AND contains(artikel, "Art. [A]") AND contains(wet, "[deel van wetnaam]")
SORT datum DESC
\`\`\`

## Annotaties die naar dit artikel verwijzen

\`\`\`dataview
TABLE artikel, datum AS "Analysedatum"
FROM "analyses"
WHERE type = "jas-annotatie" AND contains(kruisreferenties, "Art. [A] [wet-afkorting]")
SORT datum DESC
\`\`\`
```

**Als het bestand al bestaat:** geen actie. Noteer `[hub-nieuw]` = false.

---

## Stap 13 — Commit en push

Voer in de projectroot uit:

```
git add analyses/jas-annotatie-art[A]-[afkorting wet]-[TIMESTAMP].md analyses/INDEX.md
git commit -m "jas: annotatie art. [A] [W] ([PD])"
git push
```

Als `[hub-nieuw]` = true: voeg de hub-note toe aan de `git add` vóór de commit:

```
git add analyses/jas-annotatie-art[A]-[afkorting wet]-[TIMESTAMP].md analyses/INDEX.md [hub-pad]
git commit -m "jas: annotatie art. [A] [W] ([PD])"
git push
```

Gebruik exact het opgeslagen bestandspad uit Stap 11 voor de `git add`.

---

## Stap 14 — Retourneer bestandspad

Retourneer uitsluitend het opgeslagen bestandspad.
