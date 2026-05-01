# Skill: /annoteer

> **Conflictresolutie:** Bij tegenstrijdigheid tussen deze SKILL.md en `kaders.md` is **`kaders.md` leidend**. SKILL.md geeft procesinstructies; `kaders.md` geeft de juridisch-inhoudelijke normen.

Voert Activiteit 2 uit van de Wetsanalyse-methode: markeren (A2a) en classificeren (A2b). Output is een lichte annotatie-noot per eenheid en N begrip-noten met uitsluitend gevulde frontmatter (A2-tussenproduct). Begrip-inhoud (A3) wordt later ingevuld door `/begrip`.

**Lees vóór elke annotatie-run eerst `.claude/skills/annoteer/kaders.md` volledig in.** De taxonomie (13 JAS-elementen), annotatieregels per element, en kleurcodering in dat bestand zijn bindend voor elke classificatiebeslissing in deze skill.

---

## Triggervormen

Drie flows, elk met eigen existentiecontrole en output:

| Trigger | Flow | Wanneer gebruiken |
|---------|------|-------------------|
| `/annoteer art. [A] [W]` | **A — Artikel-index** | Eerste aanraking van een artikel in een formele wet (met leden) |
| `/annoteer art. [A] lid [L] [W]` | **B — Lid-annotatie** | Annoteren van één lid van een formeel artikel |
| `/annoteer sectie [ref] [W]` | **C — Sectie-annotatie** | Bronnen zonder leden: Leidraad, beleid, beleidsregels |

Flow A maakt uitsluitend de structuurankers aan (wetstekst-noot + index-noot). Flow B voegt de inhoudelijke annotatie toe. Flow C is voor bronnen die geen leden kennen.

---

## Slug-transformatietabel

De eenheid-slug wordt deterministisch afgeleid van het MCP `pad`-veld. Verwijder tekstdelen; houd structuursymbolen en cijfers:

| MCP `pad`-segment | Transformatieregel | Slug-resultaat |
|-------------------|--------------------|----------------|
| `Artikel 9` | `art` + nummer | `art9` |
| `Artikel 2a` | `art` + nummer + letter | `art2a` |
| `Lid 1` | suffix `-` + nummer op artikel-slug | `art9-1` |
| `§ 1.1 De ontvanger` | `par` + punten → koppeltekens | `par1-1` |
| `§ 1.1.1 Inleiding` | `par` + punten → koppeltekens | `par1-1-1` |
| `Paragraaf 3` | `par` + nummer | `par3` |

Tekstdelen na het structuursymbool (zoals "De ontvanger" of "Inleiding") worden weggelaten. De slug bevat uitsluitend lowercase letters, cijfers en koppeltekens.

**Fallback voor nummerloos sectie-kopje** (geen §-nummer, geen paragraafaanduiding): slugify de volledige kopnaam — zet om naar lowercase, vervang spaties door koppeltekens, verwijder speciale tekens. Bijv. `"Algemeen"` → `algemeen`, `"Inleiding en reikwijdte"` → `inleiding-en-reikwijdte`. Bij een kopnaam die niet uniek is binnen de wet: voeg een volgnummer toe (`algemeen-2`).

---

## Voorbereiding — per flow

**Lees vóór alle flows eerst `.claude/skills/annoteer/kaders.md` volledig in.**

### Flow A — Artikel-index

> **Aanbevolen vertrekpunt (A1):** Juridische scenario's zijn de scope-afbakening voor Flow A. Als de gebruiker geen scenario's heeft geformuleerd vóór de aanroep, attendeer dan op dit hiaat — maar blokkeer de flow niet. De annotatie kan doorgaan; de scope-verantwoordelijkheid ligt bij de gebruiker (A1 valt buiten de AI-scope).

1. Controleer of wetstekst-noot bestaat: `find wetteksten/[wet]/ -name "art[A].md"`.
   - Nee → haal wetstekst op via `wettenbank_artikel` en maak aan.
   - Ja → gebruik bestaande noot; geen nieuwe MCP-aanroep.
2. Controleer of index-noot bestaat: `find annotaties/[wet]/ -name "art[A].md"`.
   - Nee → maak aan.
   - Ja → meld "index-noot bestaat al" en stop.
3. Haal brondefinities op via `wettenbank_artikel` op het begripsbepalingen-artikel (zie `bwb-mapping.md`).
4. Noteer het `pad`-veld letterlijk uit MCP → structuurpositie.
5. Noteer de peildatum uit `versiedatum`. Gebruik nooit de datum van vandaag.
6. Extraheer kruisreferenties conform `verwijzingen.md` uit alle leden.

### Flow B — Lid-annotatie

1. Controleer of index-noot bestaat: `find annotaties/[wet]/ -name "art[A].md"`.
   - Nee → voer Flow A eerst uit.
   - Ja → ga door.
2. Controleer of lid-noot bestaat: `find annotaties/[wet]/ -name "art[A]-[L].md"`.
   - Nee → maak aan.
   - Ja → meld "lid-noot bestaat al" en stop.
3. Lees de wetstekst-noot `wetteksten/[wet]/art[A].md` in voor de tekst van lid [L].
4. Haal brondefinities op indien nog niet beschikbaar.
5. Peildatum en structuurpositie overnemen uit het opgeslagen frontmatter-bestand van de index-noot — lees de werkelijke waarden uit `annotaties/[wet]/art[A].md`. Gebruik nooit de versiedatum uit een lopende MCP-sessie (die kan afwijken bij een tussentijdse wetswijziging).

### Flow C — Sectie-annotatie

1. Leid slug af van het MCP `pad`-veld via de slug-transformatietabel.
2. Controleer of wetstekst-noot bestaat: `find wetteksten/[wet]/ -name "[slug].md"`.
   - Nee → haal tekst op via MCP en maak aan.
   - Ja → gebruik bestaande noot.
3. Controleer of annotatie-noot bestaat: `find annotaties/[wet]/ -name "[slug].md"`.
   - Nee → maak aan.
   - Ja → meld "annotatie-noot bestaat al" en stop.

---

## Markeren (A2a) — Handleiding §3.4.2a

### Algemene markeringsregels

- **Diagram-gedreven, niet uitputtend**: markeer alleen wetsformuleringen die deel uitmaken van een diagram van een centrale klasse of daarmee samenhangen. Vermijd "wilde weg" markeren van losse woorden zonder relatie tot een centrale klasse.
- **Lidwoord altijd meenemen** in de markering (maakt volledigheidscheck mogelijk voor geclassificeerde tekst).
- **Verwijzing altijd meenemen** als die in het te markeren stukje staat (draagt bij aan betekenis en klasse).
- Markeer **precies dat stukje tekst** dat maximaal de betekenis representeert van de klasse die je wilt toekennen — dit is klasse-afhankelijk:
  - *Variabele*: neem werkwoord en voorwaarden mee (met lidwoord)
  - *Afleidingsregel*: neem werkwoorden + voorwaarden mee incl. lidwoord, verwijzing en punt
  - *Voorwaarde*: markeer bij voorkeur de gehele zin of het zinsdeel
- **Markeringen mogen overlappen**: dezelfde wetsformulering kan meerdere klassen krijgen; zet elke klasse op een aparte rij in de annotatietabel.
- **Begin bij de centrale klassen**: start met rechtsbetrekking en rechtsfeit; werk daarna naar context en randcondities.
- **Start bij de klasse die gecreëerd of afgeleid wordt**, niet bij de context.
- **Bij twijfel over de reikwijdte van een markering**: werk meteen met een concreet voorbeeld van de betekenis die je wilt duiden — dat maakt scherper wat je wel/niet in de markering opneemt.

### Klasse-specifieke markeringsregels

| JAS-klasse | Wat te markeren |
|-----------|----------------|
| Rechtssubject | Zelfstandig naamwoord voor persoon/entiteit, incl. lidwoord |
| Rechtsobject | Zelfstandig naamwoord voor het voorwerp, incl. lidwoord |
| Rechtsbetrekking | Werkwoord + hulpwerkwoord (kan, mag, is verplicht, dient te) |
| Rechtsfeit | Actieve werkwoordsvorm + tijdsverloop (indienen, verstrijken, betekenen) |
| Voorwaarde | Gehele zin of zinsdeel m.i.v. voegwoord (indien, als, tenzij, mits) |
| Afleidingsregel | Volledige als-dan constructie incl. lidwoord, werkwoorden en punt |
| Variabele | Zelfstandig naamwoord (kenmerk) + lidwoord — géén werkwoord, géén voorwaarden |
| Parameter | Tariefwaarde, drempel, maximum, minimum |
| Tijdsaanduiding | Tijdstip, tijdvak, termijn (specifieker dan variabele — gebruik dit bij twijfel) |
| Plaatsaanduiding | Geografische aanduiding, jurisdictie (specifieker dan parameter) |
| Delegatiebevoegdheid | Volledige delegatiezin incl. "bij amvb" of "bij ministeriële regeling" |
| Brondefinitie | Volledige aanhef + onderdelen van de begripsomschrijving |
| Operator | Rekenkundig teken of logisch woord (vermeerderd met, EN, OF, NIET) |

---

## Classificeren (A2b) — kaders.md

- **Meest specifieke klasse**: tijdsaanduiding is specifieker dan variabele; plaatsaanduiding is specifieker dan parameter.
- **Interpretatiemethode expliciet benoemen** per element: grammaticaal / systematisch / teleologisch.
- **Meerduidigheid of spanning signaleren** als een element meerdere klassificaties verdient of conflicteert met andere bepalingen.
- **Delegatieketens volledig traceren**: wet → amvb → ministeriële regeling; haal alle schakels op via MCP.
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

### Flow A — Wetstekst-noot

Sla op als `wetteksten/[wet]/art[A].md`.

```yaml
---
type: wetstekst
artikel: "Art. [A] [W]"
bwb-id: [B]
peildatum: [YYYY-MM-DD uit MCP versiedatum]
structuurpositie: "[pad-veld letterlijk uit MCP]"
tags:
  - wetstekst
  - wet/[wet-afkorting]
  - art/[nummer]
bronreferentie: "[bronreferentie-veld uit MCP]"
---
```

Body: alle leden letterlijk als `> **[nr]** [tekst]`. Geen interpretatie, geen annotatie.

### Flow A — Index-noot (READ-ONLY)

Sla op als `annotaties/[wet]/art[A].md`.

```yaml
---
type: annotatie
artikel: "Art. [A] [W]"
bwb-id: [B]
peildatum: [YYYY-MM-DD uit MCP versiedatum]
structuurpositie: "[pad-veld letterlijk uit MCP]"
tags:
  - annotatie
  - wet/[wet-afkorting]
  - art/[nummer]
wetstekst: "[[wetteksten/[wet]/art[A]]]"
leden-noten: []
kruisreferenties: []
---
```

Body: uitsluitend `## Delegatiestructuur`. Geen wetstekst, geen annotatietabel, geen diagram.

> **⚠ Read-only principe — niet-onderhandelbaar**
> De index-noot is uitsluitend structuurdrager. Zij mag **nooit** bevatten:
> annotatierijen, annotatietabellen, mermaid-diagrammen, interpretaties, kwalificaties of signaleringen.
> Vervuiling ongedaan maken zodra ontdekt.
> Reden: de index-noot is het structuuranker. Vervuiling trekt ruis in bij alle querytypes die op artikelniveau filteren.

### Flow B — Lid-annotatie-noot

Sla op als `annotaties/[wet]/art[A]-[L].md`.

```yaml
---
type: annotatie
artikel: "Art. [A] lid [L] [W]"
bwb-id: [B]
peildatum: [YYYY-MM-DD — overnemen uit index-noot]
structuurpositie: "[structuurpositie index-noot] > Lid [L]"
tags:
  - annotatie
  - wet/[wet-afkorting]
  - art/[nummer]
onderdeel-van: "[[annotaties/[wet]/art[A]]]"
wetstekst: "[[wetteksten/[wet]/art[A]]]"
begrippen: []
---
```

Body:
- `## Wetstekst lid [L] (letterlijk)` — tekst van uitsluitend dit lid als `> **[L]** [tekst]`
- `## Annotatietabel` — zie tabelformaat hieronder
- `## Diagram` — zie Diagram (A2c) hieronder

Na aanmaken: voeg `"[[annotaties/[wet]/art[A]-[L]]]"` toe aan `leden-noten` in de index-noot. Lijst altijd gesorteerd op oplopend lidnummer.

#### Annotatietabel-formaat

| Nr | Markering (letterlijk incl. lidwoord en verwijzingen) | JAS-klasse | Interpretatiemethode | Begrip | Signalering |
|----|------------------------------------------------------|-----------|---------------------|--------|-------------|
| [doorlopend vanaf 1] | "[citaat]" | **[klasse]** | grammaticaal/systematisch/teleologisch/wetshistorisch | [[begrippen/[slug]]] | — |

- Nummerering begint bij 1 per lid-noot.
- **Overlappende markeringen** (één tekstfragment past in meerdere JAS-klassen): gebruik altijd **aparte rijen** — één rij per klasse, zelfde citaat mag meerdere keren voorkomen. Kies per rij de klasse die die specifieke functie het best beschrijft. Vermeld de alternatieve klasse in de Signalering-kolom van de primaire rij: `⚠ alternatief: [klasse]`.
- **Meerduidigheid binnen één klasse** (twijfel welke van twee klassen de juiste is): kies de meest specifieke klasse (zie kaders.md §Annotatieprincipe 3). Verantwoord de keuze in de Signalering-kolom: `⚠ overwogen: [alternatief], gekozen: [klasse] omdat [reden]`.
- **Signalering**: gebruik `—` als er geen bijzonderheden zijn. Gebruik `⚠ [toelichting]` bij meerduidigheid, spanning met andere artikelen, open normen of delegatiegaten.

### Flow C — Wetstekst-noot (sectie)

Sla op als `wetteksten/[wet]/[slug].md`. Identiek aan Flow A-wetstekst-noot, maar met sectie-slug en sectiestructuurpositie.

### Flow C — Directe annotatie-noot (sectie)

Sla op als `annotaties/[wet]/[slug].md`.

```yaml
---
type: annotatie
artikel: "[ref zoals in bron, bijv. § 1.1 LI 2008]"
bwb-id: [B]
peildatum: [YYYY-MM-DD uit MCP]
structuurpositie: "[pad-veld letterlijk uit MCP]"
tags:
  - annotatie
  - wet/[wet-afkorting]
begrippen: []
wetstekst: "[[wetteksten/[wet]/[slug]]]"
kruisreferenties: []
---
```

Body: `## Wetstekst [ref] (letterlijk)`, `## Annotatietabel`, `## Diagram`, `## Delegatiestructuur`.

Geen `onderdeel-van` (geen index-noot voor sectie-bronnen). Geen `leden-noten`.

### Begrip-noten (lege frontmatter) — alle flows

Maak per annotatierij een begrip-noot aan in `begrippen/[slug].md`. **Vul uitsluitend de frontmatter in** — definitie, voorbeelden en kenmerken blijven leeg (dat doet `/begrip`).

Begripsnaam-vuistregels: zie `/begrip` §Begripsnaam-vuistregels (Handleiding §3.5.2a) — dat is de canonieke bron. Enige regel die al tijdens `/annoteer` geldt: **hergebruik** een bestaande begripsnaam als de unieke betekenis identiek is — maak géén duplicaat.

Frontmatter per begrip-noot (body leeg):
```yaml
---
type: begrip
begripsnaam: [slug]
jas-klasse: [JAS-element]
tags:
  - begrip
  - jas/[klasse-slug]
  - wet/[wet-afkorting]
  - art/[nummer]
markering: "[letterlijk geciteerd incl. lidwoord en verwijzingen]"
bron: "Art. [A] lid [L] [W]"
bronnen: []
peildatum: [YYYY-MM-DD uit MCP]
interpretatiemethode: [grammaticaal | systematisch | teleologisch | wetshistorisch]
toelichting-klasse: "[waarom deze klasse boven alternatieven; meerduidigheid benoemen]"
definitie: ""
soort: ""
herkomst: ""
aliases: []
is-een: []
heeft: []
leidt-tot: []
afleidingsregels: []
geldigheid-van: [YYYY-MM-DD uit MCP versiedatum]
geldigheid-tot: ""
status: concept
---
```

> **⚠ Valkuil — JAS-klasse ≠ entiteitstype**
> Het `type`-veld is altijd `begrip` — ook als de `jas-klasse` `afleidingsregel` is.
> De `jas-klasse` beschrijft de juridische functie; `type` beschrijft het entiteitstype in de vault.
> Tags bij JAS-klasse afleidingsregel: `[begrip, jas/afleidingsregel, wet/..., art/...]`
> — **nooit** `[afleidingsregel, ...]` (dat is het patroon voor regel-noten in `regels/`).

Na aanmaken: update het `begrippen`-veld in de annotatie-noot (lid-noot of sectie-noot) met wikilinks naar alle aangemaakte begrip-noten.

### Diagram (A2c)

Maak na de annotatietabel de `## Diagram`-sectie aan. Volg `kaders.md §Diagramregels` volledig.

> **Brugfunctie:** het diagram verbindt het juridisch scenario (A1) met de gemarkeerde wetsformuleringen (A2) en bereidt de betekenisgeving (A3) voor. Vertrekpunt is altijd de centrale klasse die bij de eerste relevante gebeurtenis uit het scenario hoort.

Werkwijze:
1. Identificeer alle Rechtsbetrekkingen in de annotatietabel. Eén diagram per Rechtsbetrekking.
2. Per diagram: bepaal de centrale knoop (Rechtsbetrekking), voeg alle elementen toe die in de annotatietabel aan dit lid zijn gerelateerd, verbind ze met de randlabels uit de relatieschematabel.
3. Neem alleen de `classDef`-regels op voor de klassen die daadwerkelijk in het diagram voorkomen.
4. Knooplabels: `"[JAS-klasse]<br/>'[markering ingekort tot max. 40 tekens]'"` — inkorten bij het zelfstandig naamwoord, hulpwerkwoorden weglaten, `…` toevoegen indien afgekort.
5. Titel boven elk blok: `### Diagram [N] — lid [L]: [korte omschrijving rechtsbetrekking]`

Kies de centrale klasse conform de prioriteitsvolgorde in `kaders.md §Centrale klasse` (1. Rechtsbetrekking → 2. Rechtsfeit → 3. Afleidingsregel → 4. Voorwaarde). Alleen als alle vier ontbreken: schrijf exact `Geen centrale klasse gevonden; diagram niet van toepassing.`

#### Delegatiestructuur-formaat

| Delegatiebevoegdheid | Vindplaats | Type | Invulling | Vindplaats invulling |
|---------------------|------------|------|-----------|---------------------|
| [omschrijving] | Art. [A] lid [L] [W] | Verplicht / Facultatief | [naam regeling] | Art. [Z] [regeling] |

Bij geen delegatie: schrijf exact "Geen delegatiebevoegdheden in artikel [A]."

Als een gedelegeerde regeling niet opvraagbaar is via `wettenbank_artikel`: schrijf in kolom Invulling "Niet beschikbaar via wettenbank — handmatige verificatie vereist."

---

## Kwaliteitseisen (niet-onderhandelbaar)

- Wetstekst altijd volledig en letterlijk citeren — nooit parafraseren.
- Peildatum altijd uit MCP (`versiedatum`), nooit de datum van vandaag.
- Structuurpositie altijd letterlijk uit `pad`-veld, nooit aangenomen.
- Begrip-noten bevatten na `/annoteer` uitsluitend frontmatter; A3-inhoud is taak van `/begrip`.
- Markering-veld bevat altijd het letterlijke citaat inclusief lidwoord.
- Delegatieketens volledig uitwerken — alle schakels ophalen via MCP.
- **Index-noot is uitsluitend structuurdrager** — nooit annotatierijen, diagrammen of interpretaties. Vervuiling ongedaan maken zodra ontdekt.
- Regelbestanden (`regels/AR-*.md`): `afgeleid-van` verwijst naar de lid-noot of sectie-annotatie-noot, nooit naar de index-noot.

---

## Verplichte checklist-output na elke annotatie-run

Print na het opslaan de volgende checklist in de chat:

**Flow A:**
```
Artikel-index-checklist — Art. [A] [W]
✅/⬜ wetstekst-noot aangemaakt in wetteksten/[wet]/art[A].md
✅/⬜ index-noot aangemaakt in annotaties/[wet]/art[A].md (leeg behalve delegatiestructuur)
✅/⬜ peildatum uit MCP (versiedatum)
✅/⬜ structuurpositie letterlijk uit pad-veld
✅/⬜ kruisreferenties gevuld
✅/⬜ delegatiestructuur uitgewerkt (of "geen delegatiebevoegdheden")
```

**Flow B:**
```
Lid-annotatie-checklist — Art. [A] lid [L] [W]
✅/⬜ lid-noot aangemaakt in annotaties/[wet]/art[A]-[L].md
✅/⬜ wetstekst lid [L] volledig en letterlijk geciteerd
✅/⬜ alle 13 JAS-elementen intern afgevinkt
✅/⬜ diagram aangemaakt (of reden ontbreken vermeld)
✅/⬜ begrip-noten aangemaakt per annotatierij
✅/⬜ begrippen-veld bijgewerkt in lid-noot
✅/⬜ leden-noten-veld bijgewerkt in index-noot (gesorteerd)
```

**Flow C:**
```
Sectie-annotatie-checklist — [ref] [W]
✅/⬜ wetstekst-noot aangemaakt in wetteksten/[wet]/[slug].md
✅/⬜ annotatie-noot aangemaakt in annotaties/[wet]/[slug].md
✅/⬜ wetstekst sectie volledig en letterlijk geciteerd
✅/⬜ alle 13 JAS-elementen intern afgevinkt
✅/⬜ annotatietabel ingevuld
✅/⬜ diagram aangemaakt (of reden ontbreken vermeld)
✅/⬜ delegatiestructuur beschreven (of "geen delegatiebevoegdheden")
✅/⬜ begrip-noten aangemaakt per annotatierij
✅/⬜ begrippen-veld bijgewerkt in annotatie-noot
```

---

## Hergebruiksrapportage

Print aan het einde van elke annotatie-run een overzicht van hergebruikte begrippen — begrip-noten die al bestonden vóór deze run en nu een extra markering hebben gekregen:

**Hergebruikte begrippen (definitie mogelijk bijstellen):**
- `[[begrippen/[slug]]]` — primaire bron: [bron-veld]; nieuw ook geannoteerd in Art. [A] lid [L] [W]

**Voer `/begrip [slug]` niet automatisch uit vanuit deze skill.** Rapporteer de hergebruikte begrippen als actievelijst; de gebruiker roept daarna handmatig `/begrip [slug]` aan.

Na het bijstellen van een begrip: controleer via het `afleidingsregels`-veld of afhankelijke regel-noten in `regels/` nog kloppen.

Als er geen hergebruikte begrippen zijn: schrijf exact "Geen hergebruikte begrippen."

### Soort-consistentiecheck bij hergebruik (verplicht)

Controleer bij elk hergebruikt begrip of het `soort`-veld nog semantisch passend is in de nieuwe context:

| soort in bestaand begrip | Signaal in nieuwe context | Actie |
|--------------------------|--------------------------|-------|
| `waar-niet-waar` | het begrip werkt in de nieuwe context per element (bijv. per termijn, per deelbedrag) | ⚠ signaleer in annotatietabel: "hergebruikt begrip is binair; in deze context werkt het per [element] — overweeg nieuw begrip" |
| `getal` | de nieuwe context vereist een binaire uitkomst | ⚠ signaleer idem |
| Elk soort | het soort is passend — geen actie | — |

Noteer de uitkomst van deze check in de Signalering-kolom van de annotatierij, ook als er geen probleem is (`soort passend`). Dit maakt de keuze traceerbaar voor A4-validatie.
