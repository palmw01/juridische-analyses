# Juridische wetsanalyse — kennisgraaf voor de invorderingspraktijk

![License](https://img.shields.io/github/license/palmw01/juridische-analyses)
![Status](https://img.shields.io/badge/status-in%20ontwikkeling-yellow)
![Methodiek](https://img.shields.io/badge/methodiek-JAS%20v1.0.10-blue)
![Domein](https://img.shields.io/badge/domein-invordering%20rijksbelastingen-darkgreen)
![CI](https://img.shields.io/github/actions/workflow/status/palmw01/juridische-analyses/ci.yml?branch=main&label=CI)

Gestructureerde wetsanalyse op **art. 9 Invorderingswet 1990** (betalingstermijnen), uitgevoerd volgens de BZK-Wetsanalyse-methodiek met het Juridisch Analyseschema (JAS v1.0.10).

De output is een **traceerbaar kennismodel**: elke definitie, elke afleidingsregel en elke relatie is herleidbaar naar een concrete markering in de wetstekst. Het model is machineleesbaar (RDF/SKOS, GEXF, RegelSpraaak) en daarmee direct bruikbaar voor digitale implementatie van de invorderingsregelgeving.

Aangedreven door Claude Code met een MCP-koppeling naar [wetten.overheid.nl](https://wetten.overheid.nl), gevalideerd met een Python-toolchain en gepubliceerd via GitHub Pages.

---

## Voor wie

| Rol | Wat biedt dit |
|-----|---------------|
| **Jurist (invordering)** | Uitgewerkte analyse van art. 9 IW / §9.1 Leidraad Invordering, traceerbaar naar de wetstekst |
| **Wetsanalist / methodiekbureau** | Werkend voorbeeld van de BZK-Wetsanalyse-methodiek met volledige JAS-classificatie |
| **Kennisengineer / IT-jurist** | Machineleesbare begrippenstelsels (RDF/SKOS) en formele afleidingsregels in RegelSpraaak-formaat |
| **Geïnteresseerde** | Proof-of-concept van AI-ondersteunde wetsanalyse met volledige audittrail |

---

## Status

| Onderdeel | Status |
|-----------|--------|
| Art. 9 lid 1 IW — annotatie | ✅ Gereed |
| Art. 9 lid 5 IW — annotatie | ✅ Gereed |
| §9.1 Leidraad Invordering — annotatie | ✅ Gereed |
| Begrippen (A3a) — 28 stuks | ✅ Gereed |
| Afleidingsregels (A3b) — 9 stuks | ✅ Gereed |
| RDF/SKOS-export | ✅ Gereed |
| Validatie (L1–L3) — 40 bestanden, 0 blokkeerfouten | ✅ Gereed |
| Enrichment-detectie | ✅ Gereed |
| Graph-export (GEXF/GraphML/PDF) | ✅ Gereed |
| Statische webapp (GitHub Pages) | ✅ Gereed |
| **Totaal: art. 9 IW volledig doorlopen** | **✅ Proof-of-concept compleet** |
| Uitbreiding naar andere artikelen | 🔜 Volgende fase |

---

## Hoe werkt de analyse?

De methodiek bestaat uit zes activiteiten (A1–A6). Claude Code ondersteunt A2 en A3; de overige stappen zijn een menselijke taak, uitgevoerd in multidisciplinair teamverband.

```
A1  Werkgebied bepalen          (handmatig: scope, bronnen, juridische scenario's)
     │
     ▼
A2  Markeren & classificeren    (/annoteer — Claude Code)
     │  wetstekst → JAS-annotaties in JSON
     │  elke zinsdeel krijgt een JAS-klasse + interpretatiemethode
     ▼
A3  Betekenis vastleggen        (/begrip-alles — Claude Code)
     │  annotaties → begrippen (YAML) + afleidingsregels (YAML)
     │  definities uitsluitend gebaseerd op markeringen uit A2
     ▼
A4  Valideren                   (handmatig: multidisciplinair team, concrete scenario's)
     ▼
A5  Signaleren                  (handmatig: lacunes, open normen, uitvoeringsbeleid)
     ▼
A6  Kennismodel opstellen       (handmatig: gegevensmodel, regelmodel, procesmodel)
```

### Stap voor stap

**Stap 1 — Wetstekst ophalen** (`/wettenbank art. [A] [W]`)

Haalt de wetstekst op via wetten.overheid.nl (MCP), normaliseert de JSON-response en slaat die op in `bronnen/`. Extraheert tegelijk kruisreferenties (JCI URI's) naar andere artikelen en wetten. De peildatum wordt vastgelegd zodat de analyse juridisch dateerbaar is.

**Stap 2 — Annoteren** (`/annoteer art. [A] [W]` + `/annoteer art. [A] lid [L] [W]`)

Verwerkt de wetstekst naar een JAS-annotatie: elk zinsdeel wordt geclassificeerd in een van de 13 JAS-klassen (rechtssubject, rechtsobject, rechtsbetrekking, rechtsfeit, voorwaarde, etc.) en krijgt een interpretatiemethode (grammaticaal, systematisch, teleologisch, wetshistorisch). Het resultaat is een structuurdiagram (knopen + kanten) en een tabel met alle markeringen, opgeslagen in `annotaties/`.

**Stap 3 — Begrippen en regels vastleggen** (`/begrip-alles art. [A] [W]`)

Leidt uit de annotaties begrippen af: per gemarkeerd element ontstaat een YAML-bestand in `begrippen/` met definitie, soort (booleaans, datum, monetair-bedrag, etc.), herkomst (direct uit wet of afgeleid), relaties naar andere begrippen en traceerbaarheid terug naar de markering. Complexere elementen leiden tot een afleidingsregel in `regels/`, uitgedrukt in RegelSpraaak-oriëntatie.

**Stap 4 — Valideren** (`make validate`)

Drie validatielagen controleren de vault na elke schrijfactie:
- L1: schema-conformiteit (JSON Schema)
- L2: integriteitscontrole (verwijzingen naar bestaande begrippen en annotaties)
- L3: kwaliteitswaarschuwingen (lege relaties, ontbrekende grensgevallen)

**Stap 5 — Exporteren** (`make ci` of afzonderlijke targets)

Genereert alle eindproducten vanuit de YAML/JSON-bronbestanden. Zie §[Eindproducten](#eindproducten) voor een toelichting per artifact.

---

## Eindproducten

### Begrippenstelsel (`begrippen/*.yaml`)

Het hart van het kennismodel. Elk bestand beschrijft één juridisch begrip met:
- een formele definitie, uitsluitend afgeleid van markeringen in de wetstekst
- het type (booleaans, datum, tijdsduur, monetair-bedrag, tekst, entiteit, etc.)
- de JAS-klasse (rechtsbetrekking, rechtsobject, variabele, etc.)
- traceerbaarheid: welke markering in welke annotatie de definitie onderbouwt
- relaties naar andere begrippen (`is-een`, `heeft`, `leidt-tot`) met kardinaliteit
- geldigheidsperiode en statusmarkering (`concept` → `ter-review` → `gevalideerd`)

### Afleidingsregels (`regels/AR-*.yaml`)

Formele als-dan-regels die beschrijven hoe juridische uitkomsten worden afgeleid. Vier typen: Beslissingsregel, Rekenregel, Specialisatieregel, Beperkingsregel. Elk bestand bevat:
- invoer- en uitvoerbegrippen (verwijzingen naar `begrippen/`)
- een formele-regel in RegelSpraaak-georiënteerde tekst
- voorbeeldreeksen met positieve én negatieve testgevallen (`juridisch-juist: true/false`)
- juridische toelichting herleidbaar naar de wettekst

### RDF Turtle / SKOS (`kennisgraaf/begrippen.ttl`)

Het begrippenstelsel uitgedrukt in **RDF** (Resource Description Framework), gemodelleerd met **SKOS** (Simple Knowledge Organization System). RDF is de W3C-webstandaard voor linked data: alles wordt beschreven als drietallen (subject – predikaat – object), waardoor begrippen verbonden kunnen worden met andere overheidsbronnen. SKOS is het daarvoor ontworpen vocabulaire voor begrippenstelsels — het biedt standaardrelaties als `skos:broader`, `skos:related` en `skos:definition`. Het `.ttl`-bestand is:
- importeerbaar in triple stores (GraphDB, Blazegraph, Apache Jena)
- SPARQL-bevraagbaar via `make query-rdf`
- uitwisselbaar met andere overheidsregisters die SKOS gebruiken (bijv. de Stelselcatalogus)

### Graafbestanden (`kennisgraaf/graph.gexf` + `graph.graphml`)

Het kennismodel als netwerkgraaf. Knopen zijn begrippen en annotaties; kanten zijn JAS-relaties (`leidt-tot`, `heeft`, `is-een`) en annotatie-verbanden. Twee formaten:
- **GEXF** — het native formaat van [Gephi](https://gephi.org), de open-source graafvisualisatietool. Open `graph.gexf` in Gephi voor interactieve verkenning, community-detectie en layoutanalyse.
- **GraphML** — breed ondersteund XML-formaat, bruikbaar in tools als yEd, Cytoscape en NetworkX.

Beide bestanden bevatten knoopattributen (JAS-klasse, soort, status) en kleurcodering op basis van JAS-klasse.

### PDF-kennisgraaf (`kennisgraaf/juridisch_kennismodel.pdf`)

Statische visualisatie van het volledige kennismodel, gegenereerd door Graphviz (`dot`). Toont alle begrippen en hun onderlinge relaties in één overzicht. Genereer of ververs met:

```bash
make pdf-graph
```

### Statische webapp (`webapp/index.html`)

Een interactieve website in Belastingdienst-huisstijl, automatisch gepubliceerd naar GitHub Pages bij elke push naar `main`. Bevat:
- doorzoekbare begrippenlijst (MiniSearch-index)
- interactieve D3-kennisgraaf met klik-navigatie en JAS-kleurcodering
- Mermaid-structuurdiagrammen per annotatie
- signaleringsoverzicht (L3-waarschuwingen) direct zichtbaar per begrip
- dark-mode

---

## Technische begrippen

### JAS — Juridisch Analyseschema

De BZK-standaard (2024) voor gestructureerde wetsanalyse, ontwikkeld door het Ministerie van Binnenlandse Zaken en Koninkrijksrelaties. Gebaseerd op de rechtstheorie van Wesley Newcomb Hohfeld (1913), die juridische relaties ontleedt in precies gedefinieerde categorieën (recht, plicht, bevoegdheid, etc.).

JAS classificeert wetselementen in **13 klassen**: rechtssubject, rechtsobject, rechtsbetrekking, rechtsfeit, voorwaarde, afleidingsregel, operator, variabele, variabelewaarde, tijdsaanduiding, plaatsaanduiding, delegatiebevoegdheid, delegatie-invulling. Elke markering in de wetstekst krijgt één klasse en één interpretatiemethode. Hierdoor wordt de redenering achter een juridische analyse expliciet en toetsbaar.

Canonieke bron: [regels.overheid.nl/standaarden/wetsanalyse/v1.0.10](https://regels.overheid.nl/standaarden/wetsanalyse/v1.0.10)

### SKOS — Simple Knowledge Organization System

De W3C-standaard voor het publiceren van begrippenstelsels (thesauri, taxonomieën, classificatieschema's) als linked data. SKOS definieert een basisvocabulaire om begrippen te beschrijven en te verbinden:

| Predicaat | Betekenis |
|-----------|-----------|
| `skos:prefLabel` | Voorkeursterm |
| `skos:definition` | Definitie |
| `skos:broader` | Bovenliggend begrip (is een soort van...) |
| `skos:related` | Gerelateerd begrip |
| `skos:inScheme` | Lidmaatschap van een begrippenstelsel |

Overheidssystemen als de [Stelselcatalogus](https://www.stelselcatalogus.nl) en [data.overheid.nl](https://data.overheid.nl) gebruiken SKOS als uitwisselingsformaat. Door het kennismodel in SKOS te publiceren, is het direct koppelbaar aan bestaande overheidsregisters.

### RDF — Resource Description Framework

De W3C-basisstandaard voor het semantisch web. Alle informatie wordt uitgedrukt als **drietallen** (triples): `subject – predikaat – object`. Elk element heeft een unieke URI. Drietallen vormen samen een **kennisgraaf** die machineleesbaar is en over systeemgrenzen heen verbonden kan worden (linked data). In dit project wordt RDF gebruikt als exportformaat voor het begrippenstelsel en de afleidingsregels, bevraagbaar via SPARQL.

### RegelSpraaak

De Nederlandse standaard voor het formeel specificeren van uitvoeringsregels in een leesbare maar machineparseerbare vorm. Ontwikkeld binnen de overheid voor regelimplementatie, onder meer gebruikt door de Belastingdienst. RegelSpraaak-regels beschrijven als-dan-redenering in gestructureerde Nederlandse zinnen, waardoor juristen en IT-specialisten dezelfde specificatie kunnen lezen.

In dit project worden afleidingsregels in RegelSpraaak-oriëntatie opgeslagen (`formele-regel`-veld in `regels/AR-*.yaml`). Versie: RegelSpraaak v2.3.0.

---

## Vault-structuur

```
bronnen/{bwb-id}/      primaire wetstekst — genormaliseerde MCP-responses (JSON)
  art{N}.json          één bestand per artikel; bevat alle leden en kruisreferenties

annotaties/{bwb-id}/   A2 — JAS-annotaties (JSON)
  art{N}.json          structuuranker per artikel (artikelindex)
  art{N}-lid{L}.json   annotatie per lid: markeringen, JAS-klassen, diagram, kruisrefs

begrippen/             A3a — begrippenstelsel (YAML)
  {slug}.yaml          definitie, soort, markeringen, relaties, geldigheid, status

regels/                A3b — afleidingsregels (YAML)
  AR-{bwb-id}-*.yaml   beslissings-, reken-, specialisatie- en beperkingsregels

schemas/               JSON Schema draft-07 (L1-validatie)
kennisgraaf/           exportartifacts
  begrippen.ttl        RDF Turtle / SKOS-begrippenstelsel
  graph.gexf           graaf voor Gephi
  graph.graphml        graaf voor yEd / Cytoscape
  juridisch_kennismodel.pdf  statische PDF-visualisatie
  model_graph.dot      Graphviz-bronbestand

views/                 gegenereerde Obsidian-views — niet handmatig bewerken
ontologie/             JAS-ontologie, SKOS-mapping, soort-systeem
rapporten/             validatierapport (gegenereerd)
scripts/               pre-commit hook (L1/L2-validatie bij commit)
tools/                 Python-toolchain (11 scripts)
.github/workflows/     CI (validatie) + deploy (GitHub Pages)
Makefile               alle build-targets
requirements.lock      pinned Python-dependencies
.claude/skills/        Claude Code skills + JAS-kaders
```

---

## Aan de slag

```bash
git clone git@github.com:palmw01/juridische-analyses.git
cd juridische-analyses

# Venv + dependencies + pre-commit hook in één stap
make setup

# Controleer of alles klopt
make validate

# Open als Obsidian-vault (vault-root = ./)
# Of start een analysesessie met Claude Code in deze map
```

### Nieuw artikel analyseren

Vervang `[A]` door het artikelnummer en `[W]` door de wetsaanduiding (bijv. `9` en `IW 1990`):

```bash
# Stap 1 — Wetstekst ophalen
/wettenbank art. [A] [W]

# Stap 2 — Annoteren (A2)
/annoteer art. [A] [W]              # structuuranker aanmaken
/annoteer art. [A] lid [L] [W]      # per lid annoteren (herhaal per lid)

# Stap 3 — Betekenis vastleggen (A3)
/begrip-alles art. [A] [W]          # begrippen + regels voor dit artikel

# Stap 4 — Valideren
make validate

# Stap 5 — Views genereren (Obsidian)
make views

# Stap 6 — Exporteren
make export-graph                   # GEXF + GraphML
make pdf-graph                      # RDF Turtle + PDF

# Stap 7 — Webapp genereren
make webapp
open webapp/index.html

# Alles in één (zelfde als CI)
make ci
```

Bij elke commit draait automatisch de **pre-commit hook** (L1/L2-validatie).  
Bij elke push naar `main` draait **GitHub Actions** (volledige validatie + alle exports + deploy webapp).

---

## Python-toolchain

| Make-target | Functie | Wanneer |
|-------------|---------|---------|
| `make setup` | venv + deps + pre-commit in één stap | Eenmalig na clone |
| `make validate` | L1 + L2 + L3 validatie, rapport in `rapporten/` | Na elke schrijfactie |
| `make views` | Genereert Obsidian-views uit YAML/JSON | Na `/annoteer` of `/begrip` |
| `make export-rdf` | YAML → RDF Turtle (SKOS) | Na wijziging begrippen/regels |
| `make export-graph` | YAML/JSON → GEXF + GraphML | Na wijziging begrippen |
| `make pdf-graph` | RDF → PDF via Graphviz (doet export-rdf eerst) | Na wijziging begrippen |
| `make webapp` | Genereert statische webapp in `webapp/` | Na wijzigingen |
| `make check-enrichment` | Detecteert begrippen met meerdere bronnen | Na nieuwe markeringen |
| `make query-rdf` | SPARQL-query op RDF-model | Bij analyse |
| `make ci` | validate + views + export-rdf + export-graph + check-enrichment | Voor push |
| `make install-hooks` | Installeert pre-commit hook | Eenmalig na clone |
| `make lock` | Installeert + pinned dependencies | Bij nieuwe deps |
| `make clean` | Verwijdert gegenereerde bestanden | Opruimen |

Graphviz is een systeemafhankelijkheid (niet via pip): `sudo apt install graphviz`

---

## Validatielagen

| Laag | Wat wordt gecontroleerd | Blokkering |
|------|------------------------|-----------|
| L1 | Schema-conformiteit — JSON Schema draft-07 | Ja — blokkeert commit en CI |
| L2 | Integriteit — verwijzingen naar bestaande begrippen en annotaties | Ja — blokkeert commit en CI |
| L3 | Kwaliteit — lege relaties, ontbrekende grensgevallen, statuswaarschuwingen | Nee — waarschuwing |

Huidig rapport: **40 bestanden ✅, 0 blokkeerfouten, 4 waarschuwingen (L3).**  
Zie [`rapporten/validatie-rapport.md`](./rapporten/validatie-rapport.md).

---

## Techniekstack

| Laag | Technologie |
|------|-------------|
| AI-assistent | Claude Code (Anthropic, claude-sonnet-4-6) met MCP |
| Wettenbrondata | wetten.overheid.nl via MCP-server (`wettenbank`-skill) |
| Vault | Obsidian (Markdown + YAML frontmatter) |
| Dataformaten | JSON (annotaties, bronnen), YAML (begrippen, regels), JSON Schema (validatie) |
| Python | 3.10+, PyYAML, jsonschema, networkx, rdflib |
| Graafvisualisatie | Graphviz (`dot`) — `sudo apt install graphviz` |
| Kennisgraaf-export | GEXF (Gephi), GraphML, RDF Turtle (SKOS), DOT (Graphviz) |
| Regelmodellering | RegelSpraaak v2.3.0 |
| CI/CD | GitHub Actions — validatie op push/PR, deploy webapp op push naar main |

---

## Verantwoording

Deze werkruimte implementeert de **Wetsanalyse-methodiek** (Ministerie van BZK, 2024), gebaseerd op het **Juridisch Analyseschema (JAS) v1.0.10**, geworteld in de rechtstheorie van Wesley Newcomb Hohfeld (1913).

Alleen **A2 (markeren en classificeren)** en **A3 (betekenis vastleggen)** worden door AI ondersteund. A4 (valideren in multidisciplinair team), A5 (signaleren van lacunes) en A6 (kennismodel opstellen) zijn menselijke activiteiten buiten de scope van deze workflow.

Kaders: [JAS-taxonomie](./.claude/skills/annoteer/kaders.md) · [Begrippen](./.claude/skills/begrip/kaders.md) · [Regels](./.claude/skills/begrip/kaders-regels.md) · [BWB-mapping](./.claude/skills/wettenbank/bwb-mapping.md)
