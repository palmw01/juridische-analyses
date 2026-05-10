# Webapp — Design document

## Kleurenpalet

### Light mode
```
Primair:     #0047A0  ── header, knoppen, links, accentborders
Accent:      #E17000  ── hover states, badges, highlights
Achtergrond: #F4F5F7  ── page background
Card-bg:     #FFFFFF  ── cards, containers
Tekst:       #1A1A1A  ── headings, body
Tekst-muted: #6B7280  ── metadata, labels
Lijn:        #E5E7EB  ── borders, dividers
Success:     #1E7E34  ── groen voor status "definitief"
Error:       #D32F2F  ── rood voor fouten/blokkades
Warning:     #E65100  ── oranje voor waarschuwingen
```

### Dark mode
```
Header:      #002D6E  ── donkerder blauw
Achtergrond: #111827  ── page background (gray-900)
Card-bg:     #1F2937  ── cards (gray-800)
Tekst:       #F3F4F6  ── headings, body (gray-100)
Tekst-muted: #9CA3AF  ── metadata (gray-400)
Lijn:        #374151  ── borders (gray-700)
```

Dark mode wordt geactiveerd via `prefers-color-scheme: dark` in een `@media`-query.
Alle kleuren worden gedefinieerd als CSS custom properties op `:root` en `[data-theme="dark"]`.

## Header (alle pagina's)

```
┌─────────────────────────────────────────────────────────┐
│ ████████████████████████████████████████████████████████ │
│ █ [logo] Belastingdienst │ Kennismodel Invordering  ██ │
│ █                        │ Dashboard │ Begrippen │ Reg█│
│ █                        │ Annotaties │ Graaf │ Zoeken █│
│ ████████████████████████████████████████████████████████ │
└─────────────────────────────────────────────────────────┘
```

- Donkerblauwe balk (#0047A0 light / #002D6E dark), 56px hoog
- Links: Belastingdienst-logo + "Kennismodel Invordering" (wit, semi-transparant)
- Rechts: navigatie-links + dark mode toggle (☀/🌙 icoon), actieve pagina heeft witte underline

---

## Dashboard

```
┌─────────────────────────────────────────────────────────┐
│ Kennismodel Invordering                                 │
│ Artikel 9 Invorderingswet 1990 · JAS v1.0.10            │
│                                                          │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                    │
│ │  28  │ │   3  │ │   9  │ │   5  │                    │
│ │Begrippen│Annotaties│ Regels │JAS-klassen│             │
│ └──────┘ └──────┘ └──────┘ └──────┘                    │
│                                                          │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│ │ Voortgang    │  │ JAS-klassen  │  │ Kwaliteit    │   │
│ │──────────────│  │──────────────│  │──────────────│   │
│ │ concept  ▓░░░│  │ rechtsobject 6│  │ Met defin. 28│  │
│ │ definitief░░│  │ tijdsaand. 4 │  │ Zonder rel. 3│   │
│ │              │  │ voorwaarde 3 │  │              │   │
│ └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ 📄 Laatste wijzigingen                             │  │
│ │───────────────────────────────────────────────────│  │
│ │ • feat: statische webapp in ...   10 min geleden  │  │
│ │ • fix: VENV auto-detect in M...   2 uur geleden   │  │
│ │ • docs: docstrings/skos-mapp...   3 uur geleden   │  │
│ └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Begrippen — overzicht

```
┌─────────────────────────────────────────────────────────┐
│ Begrippen (28)                                [+ filter]│
│                                                          │
│ [  🔍  Filter begrippen...                     ]        │
│                                                          │
│ JAS-klasse: [Alle ▼]  Status: [Alle ▼]                 │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ ○ invorderbaarheid          rechtsbetrekking  ●●●  │ │
│ │   ⏱ Herkomst: afgeleid · Status: concept            │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │ ○ belastingaanslag          rechtsobject      ●●●  │ │
│ │   ⏱ Herkomst: direct · Status: concept              │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │ ○ vervaldag eerste termijn  afleidingsregel   ●●●  │ │
│ │   ⏱ Herkomst: afgeleid · Status: concept            │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ [items 1-20 van 28]                    < 1 2 >          │
└─────────────────────────────────────────────────────────┘
```

Elke rij is klikbaar → navigeert naar detailpagina.
JAS-klasse badge heeft de juiste kleur uit het palet.
Drie puntjes rechts is context-menu (snel naar relaties).

---

## Begrip — detail

```
┌─────────────────────────────────┬───────────────────────┐
│ Begrip                         │ Relaties               │
│                                 │                        │
│ invorderbaarheid                │ Is een                 │
│ [rechtsbetrekking] [concept]    │   (geen)               │
│                                 │                        │
│ ┌───────────────────────────┐  │ Heeft                  │
│ │ Definitie                 │  │  ○ belastingaanslag    │
│ │───────────────────────────│  │  ○ voorlopige aanslag  │
│ │ De juridische toestand    │  │                        │
│ │ waarin een belasting-     │  │ Leidt tot              │
│ │ aanslag verkeert zodra de │  │   (geen)               │
│ │ wettelijke betalingster-  │  │                        │
│ │ mijn is verstreken...     │  │ Afleidingsregel        │
│ └───────────────────────────┘  │  ○ AR-BWBR0004770...   │
│                                 │                        │
│ Kenmerken                       └───────────────────────┘
│  ID: BWBR0004770/art9/lid1/...
│  Soort: booleaans
│  Herkomst: afgeleid
│  Aliases: invorderbaar
│  Geldig vanaf: 2026-01-01
│  Tussenresultaat: nee
│
│ Markeringen
│  ┌─────────────────────────────────────────────────────┐
│  │ m-001  "is invorderbaar"        grammaticaal primair│
│  │        bron: art. 9 lid 1 IW 1990                  │
│  │ m-002  "is invorderbaar"        grammaticaal context│
│  │        bron: art. 9 lid 5 IW 1990                  │
│  └─────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────┘
```

Layout: twee column op desktop (>900px), één column op mobile.
Linkerkolom: definitie + kenmerken.
Rechterkolom: relaties (incl. verwijzingen naar andere begrippen).

---

## Annotatie — detail

```
┌─────────────────────────────────────────────────────────┐
│ IW 1990 art. 9, lid 1                                   │
│ Hoofdstuk II > Artikel 9 > Lid 1 · BWBR0004770          │
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ "Een belastingaanslag is invorderbaar zes weken na │  │
│ │  de dagtekening van het aanslagbiljet."            │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ Annotatierijen                                           │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Markering                     JAS-klasse    Begrip  │ │
│ │─────────────────────────────────────────────────────│ │
│ │ "Een belastingaanslag"        rechtsobject  belas.. │ │
│ │ "is invorderbaar"             rechtsbetr.  invord.. │ │
│ │ "zes weken na de dagtekening" voorwaarde    zes-we..│ │
│ │ "zes weken"                   tijdsaand.    zes-we..│ │
│ │ "de dagtekening van het       tijdsaand.    dagtek..│ │
│ │  aanslagbiljet"                                     │ │
│ │ "aanslagbiljet"               rechtsobject  dagtek..│ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ Signaleringen                                            │
│ ⚠ rechtssubjecten niet expliciet benoemd in lid 1       │
└─────────────────────────────────────────────────────────┘
```

Opvallend: de tabel met annotatierijen heeft duidelijke kolommen en is sorteerbaar.
JAS-klasse badges hebben de juiste kleur.
Begrippen zijn klikbare links.

---

## Regel — detail

```
┌─────────────────────────────────────────────────────────┐
│ Afleidingsregel                                          │
│ berekenen vervaldag eerste termijn voorlopige aanslag    │
│ [Rekenregel]  AR-BWBR0004770-art9-lid5-c                │
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Formele regel                                      │  │
│ │───────────────────────────────────────────────────│  │
│ │ vervaldag-eerste-termijn moet berekend worden als  │  │
│ │ dagtekening-aanslagbiljet plus één kalendermaand   │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐│
│ │ Invoer       │  │ Uitvoer      │  │ Operators       ││
│ │──────────────│  │──────────────│  │─────────────────││
│ │ dagtekening  │  │ vervaldag    │  │ plus            ││
│ │ een-maand-na │  │ eerste-term.│  │                 ││
│ └──────────────┘  └──────────────┘  └─────────────────┘│
│                                                          │
│ Toelichting                                              │
│ Herleidbaar tot art. 9 lid 5 IW 1990...                 │
│                                                          │
│ Voorbeeldreeksen                                         │
│ ✅ Invoer: dagtekening 15 maart 2026                    │
│    Uitvoer: 15 april 2026                               │
│ ✅ Invoer: dagtekening 1 september 2026                 │
│    Uitvoer: 1 oktober 2026                              │
│ ❌ Invoer: dagtekening 31 januari 2026                  │
│    Uitvoer: 31 februari 2026 (bestaat niet)            │
└─────────────────────────────────────────────────────────┘
```

Formele regel in grijze quote-box met oranje linkerborder.
Voorbeeldreeksen: groene border voor juist, rode voor onjuist.

---

## Graaf

```
┌─────────────────────────────────────────────────────────┐
│ Kennisgraaf                              Legenda        │
│                                          ─────────      │
│   [Alle ▼] JAS-klasse filter             ■ rechtsobject │
│                                          ■ voorwaarde   │
│       ○────○                             ■ rechtsbetr.  │
│      /      \                            ■ tijdsaand.   │
│  ○──○        ○──○                       ■ afleidingsr. │
│      \      /                            ■ variabele    │
│       ○────○                             ■ operator     │
│                                          ─────────      │
│       ○────○                             28 nodes       │
│      /      \                            42 edges       │
│  ○──○        ○──○                                       │
│      \      /
│       ○────○
│                                          [  zoom: █░░  ]
│
│ 🔍 [hover: node-naam]  [click: → detailpagina]
└─────────────────────────────────────────────────────────┘
```

- D3.js force-directed layout
- Nodes: begrippen + regels (verschillende vormen: cirkel=begrip, ruit=regel)
- Nodes kleur-gecodeerd op JAS-klasse
- Node-grootte o.b.v. graad (aantal verbindingen)
- Edges: is-een, heeft, leidt-tot, invoer, uitvoer
- Legend rechtsonder (fixed bij scroll)
- Filter dropdown voor JAS-klasse (filtert nodes in/uit)
- Zoom + pan met muis/trackpad
- Hover toont tooltip met naam
- Click op node navigeert naar detailpagina

---

## Zoeken

```
┌─────────────────────────────────────────────────────────┐
│ Zoeken                                                   │
│                                                          │
│ [  🔍  Zoek in begrippen, annotaties en regels...   ]   │
│                                                          │
│ Type: [Alle] [Begrip] [Annotatie] [Regel]               │
│ JAS-klasse: [Alle ▼]                                    │
│                                                          │
│ ─── Resultaten (6) ─────────────────────────────────── │
│                                                          │
│ 📄 invorderbaarheid                           Begrip    │
│    De juridische toestand waarin een belastingaanslag    │
│    verkeert zodra de wettelijke betalingstermijn is      │
│    verstreken...
│    Match: definitie                                      │
│                                                          │
│ 📄 IW 1990 art. 9, lid 1                     Annotatie  │
│    Een belastingaanslag is invorderbaar zes weken na     │
│    Match: wetstekst                                       │
│                                                          │
│ 📄 berekenen vervaldag                       Regel       │
│    vervaldag-eerste-termijn moet berekend worden als     │
│    Match: formele-regel                                   │
└─────────────────────────────────────────────────────────┘
```

- MiniSearch voor fuzzy full-text search
- Filters bovenaan (type, JAS-klasse)
- Resultaten: type-icoon, titel, excerpt met highlight, match-veld
- Max 50 resultaten, gesorteerd op relevantie
- Debounce op input (300ms)
- Toetsenbord-navigatie (pijltjes om door resultaten te gaan)

---

## Responsive (mobile-first)

| Schermbreedte | Layout |
|:---|---|
| <480px | Mobile: minimalistisch, volledige breedte, header alleen icoon, zoekbalk inline |
| 480-768px | Tablet-small: header met tekst, 1-column |
| 768-1024px | Tablet: 2-column grid voor overzichten, normale margins |
| >1024px | Desktop: full layout, sidebar nav voor detailpagina's (optioneel) |

**Mobile-first principe:**
- Base styles = mobile (< 480px)
- `@media (min-width: 480px)` = tablet-small
- `@media (min-width: 768px)` = tablet
- `@media (min-width: 1024px)` = desktop
- Geen `max-width` breakpoints (behalve uitzonderingen)
- Alle containers `width: 100%; max-width: 1200px; margin: 0 auto; padding: 1rem`
- Grid: `grid-template-columns: 1fr` base → `repeat(auto-fill, minmax(280px, 1fr))` op 768px

---

## Interacties

| Element | Hover | Click | Animate |
|---------|-------|-------|---------|
| Navigatie-link | underline | → page | 200ms ease |
| Card | shadow(0,4,12) | nvt | 200ms ease |
| Begrip/regel rij | bg #F0F4FF | → detail | 150ms ease |
| JAS-badge | scale(1.05) | filter | 150ms ease |
| Graph node | scale(1.3) + tooltip | → detail | 200ms ease |
| Zoekresultaat | bg #F0F4FF | → detail | 150ms ease |
| Filter-chip | bg verandering | toggle | 200ms ease |

---

## Bestandsstructuur (output)

```
webapp/
├── index.html
├── 404.html                    ← redirect naar index
├── css/
│   └── style.css               ← alle styling (10-15KB)
├── js/
│   └── app.js                  ← MiniSearch + interacties
├── data/
│   ├── search-index.json       ← alle data voor zoeken
│   └── graph-data.json         ← nodes + edges voor D3
├── begrippen.html              ← overzicht
├── begrippen/
│   ├── invorderbaarheid.html
│   ├── belastingaanslag.html
│   └── ... (28 pagina's)
├── annotaties.html
├── annotaties/
│   ├── BWBR0004770-art9-lid1.html
│   ├── BWBR0004770-art9-lid5.html
│   └── BWBR0024096-par9-1.html
├── regels.html
├── regels/
│   ├── AR-BWBR0004770-art9-lid5-c.html
│   └── ... (9 pagina's)
└── graph.html
```

- Geen externe CSS frameworks (Bootstrap/Tailwind)
- D3.js geladen van CDN (`https://d3js.org/d3.v7.min.js`)
- MiniSearch geladen van CDN of inline
- Geen andere CDN-afhankelijkheden
- Alle HTML semantic (<nav>, <main>, <article>, <section>)
