# Skill: /annoteer

> **Conflictresolutie:** Bij tegenstrijdigheid tussen deze SKILL.md en `kaders.md` is **`kaders.md` leidend**. SKILL.md geeft procesinstructies; `kaders.md` geeft de juridisch-inhoudelijke normen.

**Trigger:** `/annoteer art. [A] [W]`

Voert Activiteit 2 uit van de Wetsanalyse-methode: markeren (A2a) en classificeren (A2b). Output is een lichte annotatie-noot per artikel en N begrip-noten met uitsluitend gevulde frontmatter (A2-tussenproduct). Begrip-inhoud (A3) wordt later ingevuld door `/begrip`.

**Lees vóór elke annotatie-run eerst `.claude/skills/annoteer/kaders.md` volledig in.** De taxonomie (13 JAS-elementen), annotatieregels per element, en kleurcodering in dat bestand zijn bindend voor elke classificatiebeslissing in deze skill.

---

## Voorbereiding

1. **Controleer of een annotatie al bestaat** via `find annotaties/ -name "[wet]-art[nr].md"`. Start geen nieuwe MCP-aanroepen als de wetstekst al beschikbaar is.
2. **Haal de wetstekst op** via `wettenbank_artikel` (nooit snippets of zoekresultaten als basis).
3. **Haal brondefinities op** via `wettenbank_artikel` op het begripsbepalingen-artikel van dezelfde wet (zie `bwb-mapping.md` voor artikelnummer).
4. **Noteer het `pad`-veld** letterlijk uit de MCP-response — dit is de structuurpositie. Neem dit nooit aan op basis van de artikelinhoud.
5. **Noteer de peildatum** uit `versiedatum` in de MCP-response. Gebruik nooit de datum van vandaag.
6. **Extraheer kruisreferenties** conform `.claude/skills/wettenbank/verwijzingen.md` uit **alle leden van het artikel** — ook de leden die niet in de annotatietabel worden uitgewerkt — en voeg de `kruisreferenties`-array toe aan de annotatie-frontmatter.

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

## Output

### 1. Annotatie-noot

Sla op als `annotaties/[wet]-art[nr].md` (bijv. `annotaties/iw1990-art25.md`).

```yaml
---
type: annotatie
artikel: "Art. [A] [W]"
bwb-id: [B]
peildatum: [YYYY-MM-DD uit MCP]
structuurpositie: "[pad-veld letterlijk uit MCP]"
tags:
  - annotatie
  - wet/[wet-afkorting]
  - art/[nummer]
begrippen: []
kruisreferenties: []   # gevuld conform verwijzingen.md — "Art. X [wet]"-notatie
---
```

Body:
- `## Wetstekst (letterlijk, peildatum [PD])` — elk lid op een nieuwe regel als `> **[nr]** [tekst]`
- `## Annotatietabel` — zie tabelformaat hieronder
- `## Diagram` — zie Diagram (A2c) hieronder
- `## Delegatiestructuur` — zie tabelformaat hieronder

#### Annotatietabel-formaat

| Nr | Markering (letterlijk incl. lidwoord en verwijzingen) | JAS-klasse | Interpretatiemethode | Begrip | Signalering |
|----|------------------------------------------------------|-----------|---------------------|--------|-------------|
| [doorlopend] | "[citaat]" | **[klasse]** | grammaticaal/systematisch/teleologisch | [[begrippen/[slug]]] | — |

- Nummerering doorlopend over alle leden.
- **Standaard: annoteer alle leden.** Als de scope beperkt is, documenteer dit op de eerste regel van de annotatietabel als cursieve noot: *Scope: lid [X]. Overige leden nog niet geannoteerd.*
- Overlappende markeringen: elke klasse op aparte rij, zelfde citaat mag meerdere keren voorkomen.
- **Signalering**: gebruik `—` als er geen bijzonderheden zijn. Gebruik `⚠ [toelichting]` bij meerduidigheid, spanning met andere artikelen, open normen of delegatiegaten (bijv. `⚠ meerduidig: ook uitlegbaar als voorwaarde` of `⚠ spanning met art. 4:81 Awb`).

#### Delegatiestructuur-formaat

| Delegatiebevoegdheid | Vindplaats | Type | Invulling | Vindplaats invulling |
|---------------------|------------|------|-----------|---------------------|
| [omschrijving] | Art. [A] lid [L] [W] | Verplicht / Facultatief | [naam regeling] | Art. [Z] [regeling] |

Bij geen delegatie: schrijf exact "Geen delegatiebevoegdheden in artikel [A]."

Als een gedelegeerde regeling niet opvraagbaar is via `wettenbank_artikel` (fout-respons of geen versiedatum): schrijf in de kolom Invulling: "Niet beschikbaar via wettenbank — handmatige verificatie vereist."

### 2. Diagram (A2c)

Maak na de annotatietabel de `## Diagram`-sectie aan. Volg `kaders.md §Diagramregels` volledig.

> **Brugfunctie:** het diagram verbindt het juridisch scenario (A1) met de gemarkeerde wetsformuleringen (A2) en bereidt de betekenisgeving (A3) voor. Vertrekpunt is altijd de centrale klasse die bij de eerste relevante gebeurtenis uit het scenario hoort.

Werkwijze:
1. Identificeer alle Rechtsbetrekkingen in de annotatietabel. Eén diagram per Rechtsbetrekking.
2. Per diagram: bepaal de centrale knoop (Rechtsbetrekking), voeg alle elementen toe die in de annotatietabel aan dat lid zijn gerelateerd, verbind ze met de randlabels uit de relatieschematabel.
3. Neem alleen de `classDef`-regels op voor de klassen die daadwerkelijk in het diagram voorkomen.
4. Knooplabels: `"[JAS-klasse]<br/>'[markering ingekort tot max. 40 tekens]'"` — inkorten bij het zelfstandig naamwoord, hulpwerkwoorden weglaten, `…` toevoegen indien afgekort.
5. Titel boven elk blok: `### Diagram [N] — lid [L]: [korte omschrijving rechtsbetrekking]`

Bij afwezigheid van Rechtsbetrekking én Rechtsfeit: gebruik Afleidingsregel of Voorwaarde als centrale klasse als het artikel primair een berekening, beslissing of conditie beschrijft (conform `kaders.md §Centrale klasse`). Alleen als alle vier ontbreken: schrijf exact `Geen centrale klasse gevonden; diagram niet van toepassing.`

### 3. Begrip-noten (lege frontmatter)

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
interpretatiemethode: [grammaticaal | systematisch | teleologisch]
toelichting-klasse: "[waarom deze klasse boven alternatieven; meerduidigheid benoemen]"
definitie: ""
soort: ""           # getal | datum | waar-niet-waar | tekst | enumeratiewaarde [| id]
herkomst: ""        # direct | afgeleid
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

Na aanmaken: update het `begrippen`-veld in de annotatie-noot met wiki-links naar alle aangemaakte begrip-noten.

---

## Kwaliteitseisen (niet-onderhandelbaar)

- Wetstekst altijd volledig en letterlijk citeren — nooit parafraseren.
- Peildatum altijd uit MCP (`versiedatum`), nooit de datum van vandaag.
- Structuurpositie altijd letterlijk uit `pad`-veld, nooit aangenomen.
- Begrip-noten bevatten na `/annoteer` uitsluitend frontmatter; A3-inhoud is taak van `/begrip`.
- Markering-veld bevat altijd het letterlijke citaat inclusief lidwoord.
- Delegatieketens volledig uitwerken — alle schakels ophalen via MCP.

---

## Verplichte checklist-output na elke annotatie-run

Print na het opslaan van de annotatie-noot en begrip-noten de volgende checklist in de chat:

```
Annotatie-checklist — Art. [A] [W]
✅/⬜ wetstekst volledig en letterlijk geciteerd
✅/⬜ peildatum uit MCP (versiedatum), niet van vandaag
✅/⬜ structuurpositie letterlijk uit pad-veld
✅/⬜ alle leden geannoteerd (of scope gedocumenteerd als cursieve noot in annotatietabel)
✅/⬜ alle 13 JAS-elementen intern afgevinkt
✅/⬜ kruisreferenties gevuld (of "geen kruisreferenties" indien van toepassing)
✅/⬜ delegatiestructuur uitgewerkt (of "geen delegatiebevoegdheden")
✅/⬜ diagram aangemaakt (of reden ontbreken vermeld)
✅/⬜ begrip-noten aangemaakt per annotatierij
✅/⬜ begrippen-veld bijgewerkt in annotatie-noot
```

---

## Hergebruiksrapportage

Print aan het einde van elke annotatie-run een overzicht van hergebruikte begrippen — begrip-noten die al bestonden vóór deze run en nu een extra markering hebben gekregen:

**Hergebruikte begrippen (definitie mogelijk bijstellen):**
- `[[begrippen/[slug]]]` — primaire bron: [bron-veld]; nieuw ook geannoteerd in Art. [A] [W]

**Voer `/begrip [slug]` niet automatisch uit vanuit deze skill.** `/begrip` start een aparte agent-context en kan niet worden gechaind vanuit `/annoteer`. Rapporteer de hergebruikte begrippen als actievelijst; de gebruiker roept daarna handmatig `/begrip [slug]` aan voor elk gerapporteerd begrip.

Na het bijstellen van een begrip (via handmatige `/begrip`-aanroep): controleer via het `afleidingsregels`-veld of afhankelijke regel-noten in `regels/` nog kloppen — met name of invoer/uitvoer-begrippen en het taalpatroon nog overeenkomen met de bijgestelde definitie.

Als er geen hergebruikte begrippen zijn: schrijf exact "Geen hergebruikte begrippen."
