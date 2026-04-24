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

Lees dit bestand volledig vóór enige andere actie:
- `$CLAUDE_SKILL_DIR/kaders.md` — JAS v1.0.10 taxonomie en annotatieprincipes

`$CLAUDE_SKILL_DIR/kruisverwijzingen.md` wordt geladen in Stap 6. `$CLAUDE_SKILL_DIR/rapportformat.md` wordt geladen in Stap 11.

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

Noteer uit `[BD]` alle begripsomschrijvingen die betrekking hebben op termen in artikel `[A]`. Sla deze op als `[brondefinities]` voor gebruik in Stap 10 (§3).

**Begrippen-check:** identificeer eerst alle relevante termen in de `leden[].tekst` van artikel `[A]`. Roep daarna voor elke geïdentificeerde term het begrip-protocol aan (zie `$CLAUDE_SKILL_DIR/../begrip/SKILL.md`). Dit controleert of het begrip al gedocumenteerd is in `begrippen/` en maakt of actualiseert de begrip-noot. Verwerk de termen één voor één.

**Lid-niveau controle:** tel `leden.length` in de MCP-response voor artikel `[A]`.
- Als `[L]` niet is opgegeven (volledig artikel gevraagd) EN `leden.length > 3`: stop de workflow. Meld: *"Art. [A] [W] heeft [N] leden. Specificeer een lid: `/jas art. [A] lid [N] [W]`"* en lijst alle beschikbare lidnummers op.
- Als `[L]` is opgegeven of `leden.length ≤ 3`: ga door. Bij een specifiek lid: gebruik alleen `leden[].tekst` van dat lid voor §4 en §5; gebruik de volledige artikeltekst wel als context voor §2, §3 en §9.

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

Lees `$CLAUDE_SKILL_DIR/kruisverwijzingen.md` volledig. Voer het daarin beschreven protocol uit op alle `leden[].tekst`-velden uit Stap 4. Dit levert een intern JSON-model op.

**Intern vs. extern:** records met `doel_bwbId` = `[B]` zijn intern; records met `doel_bwbId` ≠ `[B]` zijn extern. Records met `doel_artikel: null` (verwijzing naar hele wet) zijn altijd extern. Twijfelgeval: classificeer als extern.

**Parallel aanroepen (op basis van het JSON-model):**

1. `wettenbank_artikel(bwbId=[B], artikel=<nr>)` voor elk uniek intern `(doel_bwbId, doel_artikel)`-paar waarbij `doel_artikel` niet null is.
2. `wettenbank_artikel(bwbId=<doel_bwbId>, artikel=<doel_artikel>)` voor elk uniek extern paar waarbij `doel_artikel` niet null is.
3. `wettenbank_zoekterm(bwbId=[B], zoekterm="artikel [A]")` voor omgekeerde kruisreferenties. Verwerk de `artikelen`-array per treffer als kandidatenlijst. Voer daarna de §7.4-verificatieprocedure uit (zie kruisverwijzingen.md §7.4-protocol) vóór §7.4 te vullen.

Gebruik de `leden`-array (JSON) van elke response voor inhoudelijke annotatie; gebruik `bronreferentie` voor Bijlage B.

BWB-ids: IW 1990 = BWBR0004770 | UB IW = BWBR0004772 | AWR = BWBR0002320 | Awb = BWBR0005537 | Leidraad 2008 = BWBR0024096

Vervallen artikelen worden door de MCP gefilterd — gaten in nummering zijn normaal.

**§7 vullen vanuit het JSON-model:** volg de "Van JSON-model naar §7"-sectie en het §7.4-protocol in kruisverwijzingen.md. Wiki-link-notatie (`[[Art. Z wet-afkorting]]`) is verplicht in de "Verwijst naar"-kolom van §7.1, §7.2 en de "Verwijzend artikel"-kolom van §7.4.

**Kruisreferenties voor frontmatter:** sla na deduplicatie van het JSON-model alle unieke `"Art. <doel_artikel> <wet-afkorting>"`-strings op als `[kruisrefs]` — zonder `[[]]`, zonder lid. Gebruik `[kruisrefs]` in Stap 12. Bij geen kruisreferenties: lege array `[]`.

---

## Stap 7 — JAS-annotatie uitvoeren

Gebruik de definities, herkenningsvragen en taalkenmerken uit `$CLAUDE_SKILL_DIR/kaders.md`. Voer de annotatie uit op de wetstekst van lid `[L]` uit Stap 4, aangevuld met de brondefinities uit Stap 4.

**7a — Extractie (interne stap, niet in output):**
Lees de letterlijke tekst van lid `[L]` woord voor woord. Maak een genummerde lijst van alle te classificeren zinsdelen en formuleringen — nog geen oordeel, alleen identificatie. Noteer deze lijst intern als `[extractielijst]`. Een formulering is elk afzonderlijk zinsdeel dat een juridisch element kan bevatten (werkwoord, substantief, bijwoordelijke bepaling, voegwoord met voorwaardelijke werking, etc.).

**Interne annotatiestap (niet opnemen in rapportoutput):** loop de 13 JAS-elementen af en bepaal per element of het aanwezig is in het lid: rechtssubject, rechtsobject, rechtsbetrekking, rechtsfeit, voorwaarde, afleidingsregel, variabele/variabelewaarde, parameter/parameterwaarde, operator, tijdsaanduiding, plaatsaanduiding, delegatiebevoegdheid/delegatie-invulling, brondefinitie. Noteer per aanwezig element de vindplaats.

**Annotatieprincipes:**
1. Citeer het exacte zinsdeel letterlijk bij elk geclassificeerd element.
2. Kies altijd de meest specifieke JAS-klasse: tijdsaanduiding > variabele; plaatsaanduiding > parameter.
3. Benoem per JAS-element de interpretatiemethode: grammaticaal / systematisch / teleologisch.
4. Markeer meerduidigheid of alternatieve classificaties expliciet in de toelichting.
5. Traceer delegatieketens volledig: wet → amvb → ministeriële regeling; haal alle schakels op.

**Structuur van de annotatietabel:** maak één subsectie voor lid `[L]`. Nummer de annotaties doorlopend. Gebruik als kolomnamen: Nr | Formulering (letterlijk geciteerd) | JAS-element | Toelichting.

**Inhoud van de Toelichting-kolom:**
1. Interpretatiemethode (grammaticaal / systematisch / teleologisch)
2. Reden voor keuze van deze JAS-klasse boven alternatieven
3. Meerduidigheid of alternatieve classificatie (indien van toepassing)

**7d — Verificatie (interne stap, niet in output):**
Vergelijk de annotatietabel met `[extractielijst]` uit 7a. Is elk item uit de extractielijst terug te vinden als een annotatierij? Zo niet: voeg de ontbrekende rij alsnog toe aan de tabel vóór verdere verwerking. Noteer het aantal toegevoegde rijen als `[7d-aanvullingen]`; bij 0 aanvullingen: ga direct door.

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

## Stap 10 — Rapportopbouw (§2, §3, §6, §9–§11)

Gebruik uitsluitend de in Stappen 4–9 vergaarde wetstekst en annotaties als grondslag. Geen nieuwe MCP-aanroepen in deze stap.

**§2 Structuurdiagram:**
Gebruik het `pad`-veld uit Stap 4 als structuurpositie (blokcitaat, letterlijk overgenomen). Breng daarna de interne relaties tussen de leden in kaart op basis van de in Stap 7 geclassificeerde JAS-elementen: welk lid is de hoofdregel, welke leden zijn uitzonderingen of nadere invullingen. Gebruik een boomstructuur met ├── en └── vertakkingen. Bij een enkel lid: schrijf de standaardmelding uit rapportformat.md.

**§3 Brondefinities:**
Genereer de vierkolomstabel (Term | Definitie | Vindplaats | Reikwijdte) op basis van `[brondefinities]` uit Stap 4. Citeer definities letterlijk. Bij geen relevante brondefinities: gebruik de standaardmelding uit rapportformat.md.

**§6 Termijnen en tijdsaanduidingen:**
Genereer de tabel op basis van alle tijdsaanduidingen die in Stap 7 als JAS-element zijn geclassificeerd. Vermeld per termijn: naam, duur/datum, aanvang, einde en rechtsgevolg bij overschrijding. Bij geen termijnen: gebruik de standaardmelding uit rapportformat.md.

**§9 Juridische analyse:**
- §9.1 Grammaticale interpretatie — op basis van de letterlijke wetstekst uit §1; benoem de gewone betekenis van sleuteltermen.
- §9.2 Systematische interpretatie — op basis van de kruisreferenties uit §7 (inclusief §7.3); verwijs altijd naar concrete artikelnummers.
- §9.3 Teleologische interpretatie — op basis van wetsstructuur en wetsgeschiedenis; markeer MvT-verwijzingen altijd als "Verificatie vereist" tenzij de vindplaats (Kamerstukken II [jaar], [nr.], nr. [ondernr.], p. [X]) zeker is. Fabriceer geen MvT-verwijzingen.
- §9.4 Spanning en meerduidigheid — gebruik uitsluitend §1–§7 als grondslag; bij geen spanningsvelden: gebruik de standaardmelding uit rapportformat.md.

**§10 Lacunes en ontbrekend beleid:**
Identificeer op basis van §9 en §5 eventuele lacunes. Bij geen lacunes: gebruik de standaardmelding uit rapportformat.md.

**§11 Conclusie:**
- §11.1 Kernbevindingen: minimaal 3, maximaal 5 genummerde bevindingen (structuur per bevinding: vetgedrukte titel, *Vindplaats:*, *Betekenis:*).
- §11.2 Onzekerheden en voorbehouden: benoem resterende onzekerheden; altijd vermelden als teleologische interpretaties niet geverifieerd zijn.

---

## Stap 11 — Kwaliteitscheck

Lees `$CLAUDE_SKILL_DIR/rapportformat.md` volledig. Doorloop daarna de pre-save checklist volledig vóór opslaan. Alle punten moeten afgevinkt zijn of voorzien van een expliciete toelichting waarom een punt niet van toepassing is.

---

## Stap 12 — Frontmatter bepalen, timestamp ophalen en rapport opslaan

**Frontmatter-uitbreidingen bepalen (vóór opslaan):**

1. **tags** (zie rapportformat.md voor invulregels):
   - Altijd: `jas-annotatie`
   - Wet-tag: `[W]` → lowercase afkorting: IW 1990 → `iw1990`; AWR → `awr`; Awb → `awb`; LI 2008 → `li2008`; UB IW 1990 → `ubiw1990`
   - Artikel-tag: `art` + artikelnummer, `.` en `:` → `-`: art. 9 → `art9`; art. 4:86 → `art4-86`; art. 24.4 → `art24-4`; gecombineerd "9.1 en 9.5" → `art9-1` + `art9-5`
2. **aliases**: `"Art. [A] [wet-afkorting] ([datum])"` — bijv. `"Art. 9 lid 1 IW 1990 (2026-04-21)"`
3. **kruisreferenties**: gebruik de `[kruisrefs]`-lijst uit Stap 6 (lege array `[]` bij geen kruisreferenties)

Sla `[hub-pad]` op voor Stap 13b: `wetsartikelen/[wet-mapnaam]/art-[nummer].md`

**`[wet-mapnaam]` — exacte mapnamen (geen spaties, geen punten):**

| Wet | Mapnaam |
|-----|---------|
| Invorderingswet 1990 | `IW1990` |
| Algemene wet bestuursrecht | `Awb` |
| Algemene wet inzake rijksbelastingen | `AWR` |
| Leidraad Invordering 2008 | `LI2008` |
| Uitvoeringsbesluit IW 1990 | `UBIW1990` |

**`[nummer]`** = artikelnummer met `.` en `:` vervangen door `-`: art. 9 → `art-9`; art. 4:86 → `art-4-86`; gecombineerd "9.1 en 9.5" → `art-9-1en9-5`.

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

## Stap 13 — INDEX.md bijwerken

Voeg het nieuwe rapport toe aan `analyses/INDEX.md` onder de juiste wet:
- Gebruik het format: `- [Art. [A] (versie X)](./jas-annotatie-...) (YYYY-MM-DD)`
- Als de wet nog niet in de index staat: voeg een nieuwe kop `## [Wet]` toe.
- Update de regel `*Laatste update: YYYY-MM-DD*` onderaan het bestand.

---

## Stap 13b — Hub-note aanmaken ⚠️ VERPLICHT — nooit overslaan

Roep de Read-tool aan op `[hub-pad]` (bepaald in Stap 12). **Deze stap mag niet worden overgeslagen.** De pre-save checklist (rapportformat.md) blokkeert de commit als de hub-note ontbreekt.

**Als de Read-tool een fout geeft (bestand bestaat niet):** maak het aan met onderstaande structuur. Vul `[A]`, `[wet-afkorting]`, `[volledige wetnaam (BWB-id)]`, `[wet-afkorting-lowercase]` en `[nummer]` in met de waarden uit Stap 2 en 12. Noteer het pad als `[hub-nieuw]` = true voor Stap 14.

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

## Stap 14 — Commit en push

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

Gebruik exact het opgeslagen bestandspad uit Stap 12 voor de `git add`.

---

## Stap 15 — Retourneer bestandspad

Retourneer uitsluitend het opgeslagen bestandspad.
