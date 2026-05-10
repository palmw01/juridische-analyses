# Webapp — Plan

## 1. Doel

Statische webapp voor het inzien, doorzoeken en visualiseren van de JAS-annotatie-vault. Gericht op juristen bij de Belastingdienst, domein Inning. De webapp vervangt Obsidian als primaire kennismodel-viewer.

## 2. Uitgangspunten

- Volledig statisch — geen backend, geen database, geen server-side runtime
- Genereerbaar met 1 commando: `make webapp`
- Deploybaar op GitHub Pages (en elke statische host)
- Werkt zonder JavaScript-errors uitschakelen
- Toegankelijk (WCAG 2.1 AA als richtlijn)

## 3. Architectuur

```
tools/generate_webapp.py  ← Python generator
  ↓ leest YAML/JSON uit vault
  ↓ output statische HTML/CSS/JS
webapp/                    ← gegenereerde site
  ├── index.html           ← dashboard
  ├── begrippen.html       ← begrippen-overzicht
  ├── begrippen/           ← detailpagina's
  ├── annotaties.html      ← annotatie-overzicht
  ├── annotaties/          ← detailpagina's
  ├── regels.html          ← regels-overzicht
  ├── regels/              ← detailpagina's
  ├── graph.html           ← force-directed graaf (D3.js)
  ├── search.html          ← full-text zoeken
  └── data/                ← JSON bestanden (graph, search-index)
```

### Waarom geen framework (Svelte/React)?

- Zero build dependencies: alleen Python + YAML-parser nodig
- Geen Node.js, npm, bundlers, etc.
- Pages wegen < 10KB — laadrijd is verwaarloosbaar
- De generator kan wél optimaler worden geschreven in Python dan in JS

## 4. Pagina's en functionaliteit

### 4.1 Dashboard (`index.html`)
- Statistieken: #begrippen, #annotaties, #regels, #JAS-klassen
- Voortgangs-indicatoren (status per begrip)
- Laatste wijzigingen (uit git log)

### 4.2 Begrippen (`begrippen.html` + `begrippen/{slug}.html`)
- **Overzicht**: alfabetische lijst met filter op JAS-klasse en soort
- **Detail**: definitie, aliases, relaties (is-een/heeft/leidt-tot met links), afleidingsregel-koppeling, markeringen, status, herkomst

### 4.3 Annotaties (`annotaties.html` + `annotaties/{id}.html`)
- **Overzicht**: per wetsartikel
- **Detail**: wetstekst, annotatierijen met markeringen, JAS-klasse per rij, gelinkte begrippen, signaleringen

### 4.4 Regels (`regels.html` + `regels/{id}.html`)
- **Overzicht**: per regeltype (Rekenregel, Beslissingsregel, etc.)
- **Detail**: formele regel (RegelSpraak), toelichting, in-/uitvoer, operators, voorbeeldreeksen, tussenresultaat-indicatie

### 4.5 Graaf (`graph.html`)
- D3.js force-directed graph
- Nodes = begrippen + regels (grootte o.b.v. aantal relaties)
- Edges = is-een/heeft/leidt-tot/invoer/uitvoer
- Kleur = JAS-klasse (uit ontologie)
- Interactief: slepen, zoomen, klikken op node → detailpagina
- Legend met JAS-klasse kleuren
- Filter op JAS-klasse

### 4.6 Zoeken (`search.html`)
- Single-page search interface
- Resultaten uit begrippen + annotaties + regels
- Zie paragraaf 5 voor specificatie

## 5. Zoekfunctionaliteit

### Eis

Full-text zoeken over alle entiteiten (begrippen, annotaties, regels), met:
- Zoeken in titel/naam
- Zoeken in definitie/wetstekst/toelichting
- Fuzzy matching (typos tolereren)
- Filter op type (begrip/annotatie/regel)
- Filter op JAS-klasse (voor begrippen)
- Sorteerbaar op relevantie
- Resultaten met uitleg waarom het matcht (welk veld)

### Implementatie

**Bibliotheek: Fuse.js of MiniSearch** (client-side, geen build step)

```javascript
// search-index.json wordt gegenereerd door generate_webapp.py
[
  {
    "type": "begrip",
    "title": "invorderbaarheid",
    "url": "/begrippen/invorderbaarheid.html",
    "text": "De juridische toestand waarin een belastingaanslag verkeert...",
    "jas_klasse": "rechtsbetrekking",
    "tags": ["invorderbaar", "betalingstermijn"]
  },
  ...
]
```

Kiesopties:

| Optie | Build step? | Index grootte | Snelheid | Typos? |
|-------|------------|---------------|----------|--------|
| **MiniSearch** | Nee | Klein (enkel JSON) | Zeer snel | Ja (startsWith) |
| **Fuse.js** | Nee | Klein | Snel | Ja (uitgebreid) |
| **Lunr.js** | Ja (index) | Middel | Zeer snel | Nee |
| **Pagefind** | Ja (WASM) | Groot | Zeer snel | Nee |

**Aanbeveling: MiniSearch** — modern, klein (6KB), geen build step, goede standaard matching, werkt met een simpele JSON array.

### Pagina-indeling zoeken

```
┌──────────────────────────────────────┐
│ [zoekveld]                              │
│                                       │
│ Filters: [Alle] [Begrippen] [Regels] │
│ JAS-klasse: [▼]                      │
│                                       │
│ ─── Resultaten (12) ─────────────────│
│                                       │
│ invorderbaarheid              Begrip  │
│    De juridische toestand waarin...   │
│    Match in: definitie               │
│                                       │
│ vervaldag eerste termijn       Regel  │
│    **vervaldag-eerste-termijn** moet  │
│    Match in: formele-regel           │
└──────────────────────────────────────┘
```

## 6. Design

### Look & feel

- **Rijksoverheid/Belastingdienst DNA, maar modern**
  - Primaire kleur: `#0047A0` (Rijksoverheid blauw)
  - Accentkleur: `#E17000` (oranje voor acties/highlights)
  - Neutraal: `#f5f5f5` achtergrond, `#fff` cards
  - Tekst: `#1a1a1a` primair, `#666` secundair
  - Groen (`#1E7E34`) voor success/gereed
  - Rood (`#D32F2F`) voor fouten/blokkades

- **Typografie**: System font stack (geen externe fonts nodig)
  - `Inter` via Google Fonts optioneel (moderner)
  - Of `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
  - Headings: 700 weight, body: 400

- **Layout**: 
  - Vaste header met navigatie + zoekbalk (altijd zichtbaar)
  - Twee-column layout voor detailpagina's (nav links | content)
  - Cards voor entiteiten
  - Responsive (mobile-first grid)

### Moderne elementen
- Subtiele schaduwen (`box-shadow: 0 1px 3px rgba(0,0,0,0.08)`)
- Border-radius: 8px
- Soepele hover transitions (200ms ease)
- Goede whitespace (1.5-2rem padding)
- Laad-animatie voor graph (skeleton of fade-in)
- Dark mode via `prefers-color-scheme` (CSS custom properties)

### Graph styling
- D3 v7 met forceSimulation
- Nodes: 8-16px radius (o.b.v. connecties)
- Labels: anti-aliased, wit achtergrond-vignet voor leesbaarheid
- Hover: scale(1.3) + tooltip met volledige naam
- Click: navigate naar detailpagina
- Legend: vaste overlay rechtsonder met JAS-klassen

### Kleuren per JAS-klasse (uit jas-ontologie.yaml)
| Klasse | Kleur | Hex |
|--------|-------|-----|
| rechtssubject | Blauw | #4472C4 |
| rechtsobject | Groen | #70AD47 |
| rechtsbetrekking | Rood | #FF0000 |
| rechtsfeit | Geel | #FFC000 |
| voorwaarde | Paars | #7030A0 |
| afleidingsregel | Lichtblauw | #00B0F0 |
| variabele | Lichtgroen | #92D050 |
| tijdsaanduiding | Oranje | #F4B942 |
| operator | Grijs | #808080 |

## 7. GitHub Pages deployment

### Workflow

```yaml
# .github/workflows/deploy-webapp.yml
name: Deploy webapp

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
          cache-dependency-path: requirements.lock
      - run: pip install -r requirements.lock
      - run: python tools/generate_webapp.py --out webapp
      - uses: actions/upload-pages-artifact@v3
        with:
          path: webapp/

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/deploy-pages@v4
```

### Vereisten

1. GitHub repo Settings → Pages → Source: **GitHub Actions**
2. Domein: `palmw01.github.io/juridische-analyses/` (default)
3. Eventueel: eigen domein configureren

## 8. Fasen

| Fase | Wat | Resultaat |
|------|-----|-----------|
| **0** | Plan + design op papier | Dit document + wireframes |
| **1** | HTML/CSS template (statisch, hardcoded) | Getoond en goedgekeurd design |
| **2** | Python generator: data inladen + template vullen | `make webapp` werkt |
| **3** | Search (MiniSearch) + Graph (D3) + detailpagina's | Volledige webapp |
| **4** | GitHub Actions deploy + cleanup | Live op GitHub Pages |
| **5** | Fine-tuning: dark mode, responsive, animaties | Polijsten |

## 9. Open vragen

1. Moet de webapp ook de PDF-graaf embedden of linken?
2. Moet er een "wijzigingen-logboek" op het dashboard?
3. Dark mode gewenst?
4. Eigen domein of GitHub Pages default?
5. Moet de graaf ook regels tonen of alleen begrippen?
   → Alle entiteiten
