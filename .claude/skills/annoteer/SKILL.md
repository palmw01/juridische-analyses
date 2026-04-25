# Skill: /annoteer

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

---

## Markeren (A2a) — Handleiding §3.4.2a

### Algemene markeringsregels

- **Lidwoord altijd meenemen** in de markering (maakt volledigheidscheck mogelijk).
- **Verwijzing altijd meenemen** als die in het te markeren stukje staat (draagt bij aan betekenis en klasse).
- Markeer **precies dat stukje tekst** dat maximaal de betekenis representeert van de klasse die je wilt toekennen — dit is klasse-afhankelijk:
  - *Variabele*: neem werkwoord en voorwaarden mee (met lidwoord)
  - *Afleidingsregel*: neem werkwoorden + voorwaarden mee incl. lidwoord, verwijzing en punt
  - *Voorwaarde*: markeer bij voorkeur de gehele zin of het zinsdeel
- **Markeringen mogen overlappen**: dezelfde wetsformulering kan meerdere klassen krijgen; zet elke klasse op een aparte rij in de annotatietabel.
- **Begin bij de centrale klassen**: start met rechtsbetrekking en rechtsfeit; werk daarna naar context en randcondities.
- **Start bij de klasse die gecreëerd of afgeleid wordt**, niet bij de context.

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
---
```

Body:
- `## Wetstekst (letterlijk, peildatum [PD])` — elk lid op een nieuwe regel als `> **[nr]** [tekst]`
- `## Annotatietabel` — zie tabelformaat hieronder
- `## Delegatiestructuur` — zie tabelformaat hieronder

#### Annotatietabel-formaat

| Nr | Markering (letterlijk incl. lidwoord en verwijzingen) | JAS-klasse | Interpretatiemethode | Begrip |
|----|------------------------------------------------------|-----------|---------------------|--------|
| [doorlopend] | "[citaat]" | **[klasse]** | grammaticaal/systematisch/teleologisch | [[begrippen/[slug]]] |

- Nummerering doorlopend over alle leden.
- Overlappende markeringen: elke klasse op aparte rij, zelfde citaat mag meerdere keren voorkomen.

#### Delegatiestructuur-formaat

| Delegatiebevoegdheid | Vindplaats | Type | Invulling | Vindplaats invulling |
|---------------------|------------|------|-----------|---------------------|
| [omschrijving] | Art. [A] lid [L] [W] | Verplicht / Facultatief | [naam regeling] | Art. [Z] [regeling] |

Bij geen delegatie: schrijf exact "Geen delegatiebevoegdheden in artikel [A]."

### 2. Diagram (A2c)

Maak na de annotatietabel de `## Diagram`-sectie aan. Volg `kaders.md §Diagramregels` volledig.

Werkwijze:
1. Identificeer alle Rechtsbetrekkingen in de annotatietabel. Eén diagram per Rechtsbetrekking.
2. Per diagram: bepaal de centrale knoop (Rechtsbetrekking), voeg alle elementen toe die in de annotatietabel aan dat lid zijn gerelateerd, verbind ze met de randlabels uit de relatieschematabel.
3. Neem alleen de `classDef`-regels op voor de klassen die daadwerkelijk in het diagram voorkomen.
4. Knooplabels: `"[JAS-klasse]\n'[markering ingekort tot max. 40 tekens]'"` — inkorten bij het zelfstandig naamwoord, hulpwerkwoorden weglaten, `…` toevoegen indien afgekort.
5. Titel boven elk blok: `### Diagram [N] — lid [L]: [korte omschrijving rechtsbetrekking]`

Bij geen Rechtsbetrekking en geen Rechtsfeit in het artikel: schrijf exact `Geen centrale klasse gevonden; diagram niet van toepassing.`

### 3. Begrip-noten (lege frontmatter)

Maak per annotatierij een begrip-noot aan in `begrippen/[slug].md`. **Vul uitsluitend de frontmatter in** — definitie, voorbeelden en kenmerken blijven leeg (dat doet `/begrip`).

Begripsnaam-vuistregels (Handleiding §3.5.2a):
- Begin met **zelfstandig naamwoord** (uitzondering: afleidingsregel/rechtsfeit → actieve werkwoordsvorm)
- **Enkelvoudsvorm**, tenzij de meervoudsvorm in de wet tot andere betekenis leidt
- **Geen hoofdletters**, geen Romeinse cijfers, zo min mogelijk afkortingen
- Sluit zo nauw mogelijk aan bij de **letterlijke markering**
- Voeg wettelijke context toe als dezelfde formulering in meerdere wetten anders betekent (bijv. `verzekerde zorgtoeslag`)
- **Hergebruik** een bestaande begripsnaam als de unieke betekenis identiek is — maak géén duplicaat

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
---
```

Na aanmaken: update het `begrippen`-veld in de annotatie-noot met wiki-links naar alle aangemaakte begrip-noten.

---

## Kwaliteitseisen (niet-onderhandelbaar)

- Wetstekst altijd volledig en letterlijk citeren — nooit parafraseren.
- Peildatum altijd uit MCP (`versiedatum`), nooit de datum van vandaag.
- Structuurpositie altijd letterlijk uit `pad`-veld, nooit aangenomen.
- Begrip-noten bevatten na `/annoteer` uitsluitend frontmatter; A3-inhoud is taak van `/begrip`.
- Markering-veld bevat altijd het letterlijke citaat inclusief lidwoord.
- Delegatieketens volledig uitwerken — alle schakels ophalen via MCP.
