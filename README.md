# Juridische wetsanalyse — kennisgraaf voor de invorderingspraktijk

![License](https://img.shields.io/github/license/palmw01/juridische-analyses)
![Status](https://img.shields.io/badge/status-proof--of--concept-blue)
![Methodiek](https://img.shields.io/badge/methodiek-JAS%20v1.0.10-blue)
![Domein](https://img.shields.io/badge/domein-invordering%20rijksbelastingen-darkgreen)
![CI](https://img.shields.io/github/actions/workflow/status/palmw01/juridische-analyses/ci.yml?branch=main&label=CI)
[![GitHub Pages](https://img.shields.io/badge/webapp-online-blue?logo=github)](https://palmw01.github.io/juridische-analyses)

---

## Wat is dit?

Dit project is een **proof-of-concept voor AI-ondersteunde wetsanalyse** binnen het domein van de invordering van rijksbelastingen. Het laat zien hoe een groot taalmodel (Claude Code) de meest arbeidsintensieve stappen van de Wetsanalyse-methodiek kan uitvoeren: het systematisch annoteren van wettekst en het afleiden van formele begrippen en regels.

Dit PoC toont aan dat de kwaliteitsstandaarden van de BZK-Wetsanalyse-methodiek haalbaar zijn wanneer een AI de uitvoering overneemt, en dat het resultaat traceerbaar en valideerbaar genoeg is om als input voor digitale regelimplementatie te dienen.

**Geanalyseerd artikel:** art. 9 Invorderingswet 1990 (betalingstermijnen), aangevuld met §9.1 Leidraad Invordering 2008. Art. 9 IW regelt wanneer een belastingaanslag invorderbaar wordt en op welke tijdstippen de verschuldigde bedragen betaald moeten zijn. De bepaling is eenvoudig genoeg om volledig door te lopen, maar bevat voldoende lagen — hoofdregel, uitzonderingen, Leidraad-aanvulling, termijnberekening — om de methodiek serieus te testen.

**Output:** een traceerbaar kennismodel — 27 begrippen, 9 afleidingsregels, 40 gevalideerde projectbestanden — machineleesbaar als RDF/SKOS, GEXF en RegelSpraak, en direct bruikbaar voor digitale implementatie van de invorderingsregelgeving.

Aangedreven door Claude Code met een MCP-koppeling naar [wetten.overheid.nl](https://wetten.overheid.nl), gevalideerd met een Python-toolchain en gepubliceerd via GitHub Pages. De methodiek en validatiestructuur zijn model-onafhankelijk opgezet en gedocumenteerd voor hergebruik.

---

## Voor wie

| Rol | Wat biedt dit |
|-----|---------------|
| **Jurist (invordering)** | Uitgewerkte analyse van art. 9 IW / §9.1 Leidraad Invordering; elke definitie en regel is traceerbaar naar de wetstekst en van een juridische toelichting voorzien |
| **Gegevensspecialist** | Machineleesbare begrippenstelsels (RDF/SKOS), formele datamodellen (JSON Schema), meerdere exportformaten (Turtle, GEXF, GraphML) en een gedocumenteerde validatielaag met drie niveaus |
| **Regelanalist** | Afleidingsregels in RegelSpraak-oriëntatie met invoer- en uitvoerbegrippen, positieve én negatieve testgevallen, en een directe koppeling aan de annotaties waaruit ze zijn afgeleid |
| **Wetsanalist / methodiekbureau** | Werkend voorbeeld van de BZK-Wetsanalyse-methodiek met volledige JAS-classificatie, inclusief AI-audit trail |

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
| Graph-export (GEXF/GraphML) | ✅ Gereed |
| Statische webapp (GitHub Pages) | ✅ Gereed |
| **Totaal: art. 9 IW volledig doorlopen** | **✅ Proof-of-concept compleet** |
| Doorontwikkeling van het PoC | 🔜 Volgende fase |

---

## Hoe werkt de analyse?

De methodiek bestaat uit zes activiteiten (A1–A6). Claude Code ondersteunt **A2 en A3**; de overige stappen zijn een menselijke taak, uitgevoerd in multidisciplinair teamverband.

```
A1  Werkgebied bepalen          (handmatig: scope, bronnen, juridische scenario's)
     │
     ▼
A2  Markeren & classificeren    (/annoteer — Claude Code)
     │  wetstekst → JAS-annotaties in JSON
     │  elk zinsdeel krijgt een JAS-klasse + interpretatiemethode
     ▼
A3  Betekenis vastleggen        (/begrip-alles — Claude Code)
     │  annotaties → begrippen (YAML) + afleidingsregels (YAML)
     │  definities uitsluitend gebaseerd op markeringen uit A2
     ▼
A4  Valideren                   (handmatig: multidisciplinair team, concrete scenario's)
     ▼
A5  Signaleren                  (handmatig: lacunes, open normen, uitvoeringsbeleid)
     ▼
A6  Kennismodel opstellen       (handmatig: modelleringsbeslissingen en governance;
     de exports van A3 — RDF/SKOS, GEXF, RegelSpraak — zijn de invoer)
```

### Stap voor stap

**Stap 1 — Wetstekst ophalen** (`/wettenbank art. [A] [W]`)

Haalt de wetstekst op via wetten.overheid.nl (MCP), normaliseert de JSON-response en slaat die op in `bronnen/`. Extraheert tegelijk kruisreferenties (JCI URI's) naar andere artikelen en wetten. De peildatum wordt vastgelegd zodat de analyse juridisch dateerbaar is.

**Stap 2 — Annoteren** (`/annoteer art. [A] [W]` + `/annoteer art. [A] lid [L] [W]`)

Verwerkt de wetstekst naar een JAS-annotatie: elk zinsdeel wordt geclassificeerd in een van de 13 JAS-klassen (rechtssubject, rechtsobject, rechtsbetrekking, rechtsfeit, voorwaarde, etc.) en krijgt een interpretatiemethode (grammaticaal, systematisch, teleologisch, wetshistorisch). Het resultaat is een structuurdiagram (knopen + kanten) en een tabel met alle markeringen, opgeslagen in `annotaties/`.

**Stap 3 — Begrippen en regels vastleggen** (`/begrip-alles art. [A] [W]`)

Leidt uit de annotaties begrippen af: per gemarkeerd element ontstaat een YAML-bestand in `begrippen/` met definitie, soort (booleaans, datum, tijdsduur, monetair-bedrag, etc.), herkomst (direct uit wet of afgeleid), relaties naar andere begrippen en traceerbaarheid terug naar de markering. Complexere elementen leiden tot een afleidingsregel in `regels/`, uitgedrukt in RegelSpraak-oriëntatie.

**Stap 4 — Valideren** (`make validate`)

Drie validatielagen controleren het project na elke schrijfactie. Zie §[Validatielaag](#validatielaag) voor een gedetailleerde beschrijving.

**Stap 5 — Exporteren** (`make ci` of afzonderlijke targets)

Genereert alle eindproducten vanuit de YAML/JSON-bronbestanden. Zie §[Eindproducten](#eindproducten).

### Traceerbaarheid

Elk begrip en elke regel is herleidbaar via een vaste ID-keten:

```
wetstekst (art. 9 lid 1 IW)
  └─► bronbestand          bronnen/BWBR0004770/art9.json
        └─► annotatie-noot  annotaties/BWBR0004770/art9-1.json
              └─► markering  markering-id: m-001
                    └─► begrip  begrippen/invorderbaarheid-belastingaanslag.yaml  (kern + contexten)
                          └─► regel  regels/AR-BWBR0004770-art9-lid1-a.yaml
```

Elk YAML-bestand bevat het `bron-annotatie-id` en `markering-id` die de stap daarboven aanwijzen. Zo is elk eindproduct — definitie, uitkomst, regelformulering — in één klik te herleiden tot de exacte zin in de wetstekst.

---

## De kennisgraaf van dichtbij

Deze sectie toont hoe de kernbestanden eruitzien, zodat elke rol er direct mee uit de voeten kan.

### Begrip (YAML)

Een begrip beschrijft één juridisch concept. Hieronder een illustratief voorbeeld (verkorte weergave; niet-getoonde velden zoals `definitie-versie`, `definitie-gebaseerd-op`, `geldigheid-van`, `identificatiebegrip` zijn weggelaten maar wel verplicht):

```yaml
begrip-id: BWBR0004770/art9/lid1/invorderbaarheid-belastingaanslag
begripsnaam: invorderbaarheid-belastingaanslag
soort: booleaans          # uitkomst is ja/nee
jas-klasse: afleidingsregel
herkomst: afgeleid        # niet letterlijk in de wet, maar afgeleid via JAS-annotatie

definitie:
  kern: >-
    De beslissingsregel die bepaalt of een belastingaanslag invorderbaar is,
    inhoudende dat invorderbaarheid intreedt zodra zes weken zijn verstreken
    na de dagtekening van het aanslagbiljet.
  contexten:               # leeg als de kern voor alle bronnen volstaat
    - markering-id: m-002
      bijdrage: verfijning        # verfijning | uitbreiding | uitzondering
      tekst: >-
        In de context van art. 9 lid 5 treedt invorderbaarheid niet eenmalig in
        maar telkens opnieuw per betalingstermijn — de bevoegdheid herleeft N maal.

markeringen:
  - markering-id: m-001
    bron-annotatie-id: BWBR0004770/art9/lid1     # ← traceerbaar naar annotatie
    tekst: is invorderbaar
    interpretatiemethode: grammaticaal
    bijdrage: primair
    bevestigd: false
  - markering-id: m-002
    bron-annotatie-id: BWBR0004770/art9/lid5
    tekst: is invorderbaar
    interpretatiemethode: grammaticaal
    bijdrage: context             # aanvullende bron; verfijning gedocumenteerd in contexten[]
    bevestigd: false

relaties:
  is-een: []
  heeft:
    - begrip-id: BWBR0004770/art9/lid1/belastingaanslag
      kardinaliteit: '1:1'       # verplicht veld: 1:1 | 1:n | n:m
    - begrip-id: BWBR0004770/art9/lid1/zes-weken-na-dagtekening-aanslagbiljet
      kardinaliteit: '1:1'
  leidt-tot:
    - begrip-id: BWBR0004770/art9/lid1/invorderbaarheid
      relatie-soort: causaal

afleidingsregel-id: AR-BWBR0004770-art9-lid1-a   # ← koppeling naar regel
status: concept
```

Het veld `soort` bepaalt het datatype van de uitkomst (`booleaans`, `datum`, `tijdsduur`, `monetair-bedrag`, `percentage`, `tekst`, `enumeratie`, `entiteit`). Het veld `herkomst` maakt onderscheid tussen begrippen die letterlijk in de wet staan (`direct`) en begrippen die via JAS-redenering worden afgeleid (`afgeleid`). De `markeringen`-array is de enige basis voor de definitie — begrippen worden nooit rechtstreeks uit de wetstekst geformuleerd, maar altijd vanuit een annotatie.

Het veld `definitie` is een **gelaagd object**: de `kern` bevat de universele, wets-overstijgende betekenis die voor alle bronartikelen geldt; `contexten` bevat optionele artikel-specifieke inkleringen (`verfijning`, `uitbreiding` of `uitzondering`). Begrippen met slechts één bron hebben een lege `contexten: []`.

### Afleidingsregel (YAML)

Een afleidingsregel beschrijft een als-dan-redenering. Hieronder `regels/AR-BWBR0004770-art9-lid1-a.yaml` (ingekort):

```yaml
regel-id: AR-BWBR0004770-art9-lid1-a
naam: bepalen invorderbaarheid belastingaanslag
soort: Beslissingsregel    # vier typen: Beslissings-, Reken-, Specialisatie-, Beperkingsregel
prioriteit: null           # alleen bij Specialisatieregel: volgorde bij meerdere toepasselijke regels
vervangt-regel-id: null    # id van vorige versie bij herziening
geldigheid-van: '2026-01-01'

invoer:
  - BWBR0004770/art9/lid1/belastingaanslag
  - BWBR0004770/art9/lid1/dagtekening-aanslagbiljet
  - BWBR0004770/art9/lid1/zes-weken-na-dagtekening-aanslagbiljet
uitvoer:
  - BWBR0004770/art9/lid1/invorderbaarheid-belastingaanslag

formele-regel: |
  Een belastingaanslag is invorderbaar
  indien aan alle volgende voorwaarden is voldaan:
  - de belastingaanslag heeft een dagtekening van het aanslagbiljet
  - het tijdstip van beoordeling is gelegen op of na het tijdstip van
    de dagtekening van het aanslagbiljet plus zes weken

voorbeeldreeksen:
  - invoerwaarden: "aanslag IB; dagtekening: 1 jan 2026; beoordeling: 12 feb 2026"
    verwachte-uitkomst: "invorderbaar: ja"
    juridisch-juist: true
  - invoerwaarden: "aanslag IB; dagtekening: 1 jan 2026; beoordeling: 11 feb 2026"
    verwachte-uitkomst: "invorderbaar: nee"
    juridisch-juist: true
  - invoerwaarden: "navorderingsaanslag; dagtekening: 1 jan 2026; beoordeling: 12 feb 2026"
    verwachte-uitkomst: "invorderbaar: nee (o.g.v. lid 1)"
    juridisch-juist: true
```

Het veld `juridisch-juist` geeft aan of de verwachte uitkomst juridisch correct is. Een `false` waarde markeert een grensgeval of bekende interpretatievraag — nuttig voor zowel juridische review (A4) als het testen van een regelimplementatie.

### RDF/SKOS-representatie (Turtle)

Hetzelfde begrip, uitgedrukt als linked data in `kennisgraaf/begrippen.ttl`:

```turtle
@prefix skos:  <http://www.w3.org/2004/02/skos/core#> .
@prefix jas:   <http://regels.overheid.nl/jas/ontology#> .
@prefix prov:  <http://www.w3.org/ns/prov#> .
@prefix begrip: <urn:jas:begrip:> .

begrip:BWBR0004770_art9_lid1_invorderbaarheid
    a skos:Concept ;
    skos:prefLabel "invorderbaarheid"@nl ;
    skos:definition "De juridische toestand waarin een belastingaanslag verkeert zodra
                     de wettelijke betalingstermijn is verstreken"@nl ;  # ← kern
    jas:definitieContext [                     # ← contextuele verfijning voor lid 5
        jas:bijdrage "verfijning" ;
        jas:markering "m-002" ;
        jas:bron "BWBR0004770/art9/lid5" ;
        skos:note "In de context van lid 5 treedt invorderbaarheid telkens per termijn in"@nl
    ] ;
    prov:wasDerivedFrom "BWBR0004770/art9/lid1" ;    # ← bronreferentie naar annotatie
    prov:wasDerivedFrom "BWBR0004770/art9/lid5" ;
    jas:jasKlasse "rechtsbetrekking" ;
    jas:status "concept" .

begrip:BWBR0004770_art9_lid1_dagtekening-aanslagbiljet
    a skos:Concept ;
    skos:prefLabel "dagtekening-aanslagbiljet"@nl ;
    skos:definition "De op het aanslagbiljet vermelde datum die dient als referentiepunt
                     voor de berekening van de invorderingstermijn"@nl ;
    prov:wasDerivedFrom "BWBR0004770/art9/lid1" ;
    jas:leidtTot begrip:BWBR0004770_art9_lid1_zes-weken-na-dagtekening-aanslagbiljet ;
    jas:jasKlasse "tijdsaanduiding" .
```

Het predikaat `prov:wasDerivedFrom` legt de herkomst vast (W3C PROV-standaard). `skos:definition` bevat altijd de **kern** — de universele betekenis. Artikel-specifieke inkleringen staan als `jas:definitieContext`-blank-nodes met `bijdrage`, `markering` en `skos:note`. De JAS-relaties (`jas:heeft`, `jas:leidtTot`) zijn gedefinieerd in de JAS-ontologie op `regels.overheid.nl`.

> **Noot over de `jas:`-namespace:** De prefix `jas: <http://regels.overheid.nl/jas/ontology#>` is een *voorgestelde* namespace die aansluit bij de JAS-standaard van regels.overheid.nl. Er bestaat nog geen gepubliceerde ontologie op dit URI; de namespace fungeert voorlopig als stabiel anker voor eigen termen (`jasKlasse`, `definitieContext`, `bijdrage`, e.d.) totdat een formele JAS-ontologie beschikbaar komt.

---

## Validatielaag

Het project wordt op drie niveaus gevalideerd. Validatie draait automatisch bij elke commit (pre-commit hook) en bij elke push naar `main` (GitHub Actions). Het volledige rapport staat in [`rapporten/validatie-rapport.md`](./rapporten/validatie-rapport.md).

### L1 — Schema-conformiteit

**Wat:** elk JSON- en YAML-bestand in `annotaties/`, `begrippen/` en `regels/` wordt getoetst aan een JSON Schema (draft-07) in `schemas/`. Het schema legt verplichte velden, toegestane waarden en datatypes vast.

**Blokkerend:** ja — een L1-fout blokkeert de commit en laat CI mislukken.

**Voorbeeld van een L1-fout:**
```
annotaties/BWBR0004770/art9-1-lid1.json
  [L1] 'soort' is een verplicht veld maar ontbreekt
  [L1] 'status' moet een van ['concept', 'ter-review', 'gevalideerd'] zijn; gevonden: 'draft'
```

**Betrokken schema's:**

| Bestand | Valideert |
|---------|-----------|
| `schemas/annotatie-index.schema.json` | Structuurankers in `annotaties/` |
| `schemas/annotatie-lid.schema.json` | Lid-annotaties in `annotaties/` |
| `schemas/begrip.schema.json` | Begrippen in `begrippen/` |
| `schemas/regel.schema.json` | Regels in `regels/` |

### L2 — Integriteitscontrole

**Wat:** drie soorten controles, allemaal blokkerend:

1. **Referentiële integriteit** — alle verwijzingen naar andere projectbestanden worden gecontroleerd op bestaan (begrip-id's, annotatie-id's, afleidingsregel-id's, markering-id's in contexten, `vervangt-regel-id`)
2. **Status-consistentie** — `status: gevalideerd` vereist een ingevulde `definitie.kern`; `status: vervallen` vereist een niet-null `vervangen-door`
3. **Diagramintegriteit** — `kanten[].van` en `kanten[].naar` in annotatie-lid-diagrammen moeten verwijzen naar een bestaand `knopen[].id`
4. **Definitie-gebaseerd-op bijdrage** — markering-id's in `definitie-gebaseerd-op` mogen alleen `bijdrage: primair` hebben

**Blokkerend:** ja — L2-fouten blokkeren commit en CI.

**Voorbeeld van een L2-fout:**
```
begrippen/invorderbaarheid-belastingaanslag.yaml
  [L2] afleidingsregel-id 'AR-BWBR0004770-art9-lid1-a' bestaat niet in regels/
begrippen/zes-weken.yaml
  [L2] status is 'gevalideerd' maar definitie.kern is leeg — vul kern in vóór validatie
annotaties/BWBR0004770/art9-lid1.json
  [L2] diagram.kanten[2].naar: knoop-id 'X' niet gevonden in diagram.knopen
```

### L3 — Kwaliteitswaarschuwingen

**Wat:** heuristieke controles op volledigheid en kwaliteit. Niet blokkerend, maar zichtbaar in het rapport en in de webapp. Typische L3-waarschuwingen:

| Waarschuwing | Betekenis |
|---|---|
| `alle relaties leeg` | begrip heeft geen enkele relatie (`is-een`, `heeft`, `leidt-tot`) — mogelijk een geïsoleerd begrip of een ontbrekende modellering |
| `geen grensgevallen` | een afleidingsregel heeft alleen positieve testgevallen; negatieve gevallen of grensgevallen ontbreken |
| `definitie.kern leeg` | begrip is een nog niet ingevulde stub — gebruik `/begrip` om de kern te schrijven; bij `status: gevalideerd` escaleert dit naar een **L2-fout** |
| `alle markeringen onbevestigd` | alle markeringen van een begrip hebben `bevestigd: false` — A4-domeinexpert-validatie nog niet uitgevoerd |
| `prioriteit bij niet-Specialisatieregel` | `prioriteit` is ingevuld maar `soort` is geen `Specialisatieregel` — dit veld is alleen zinvol bij Specialisatieregels |
| `aanvullende markering zonder context` | een markering met `bijdrage: aanvullend` heeft geen corresponderende entry in `definitie.contexten` — overweeg een verfijning-, uitbreiding- of uitzondering-context toe te voegen |

**Huidig rapport:** 40 bestanden ✅ · 0 blokkeerfouten · 4 L3-waarschuwingen (begrippen zonder relaties: `31-december`, `afwijkend-boekjaar`, `logische-of`, `termijnbedrag`).

### Validatiepipeline

```
git commit
  └─► pre-commit hook (scripts/pre-commit)
        └─► validate_note.py --file <gewijzigde bestanden>
              L1 of L2 fout? → commit geblokkeerd
              Alleen L3?     → commit toegestaan, waarschuwing getoond

git push → main
  └─► GitHub Actions: ci.yml
        └─► make ci
              ├─► make validate   (L1 + L2 + L3, rapport in rapporten/)
              ├─► make export-rdf (RDF Turtle)
              ├─► make export-graph (GEXF + GraphML)
              └─► make check-enrichment (begrippen met meerdere bronnen)

git push → main (na ci.yml)
  └─► GitHub Actions: deploy-webapp.yml
        └─► make webapp → GitHub Pages
```

---

## Eindproducten

### Begrippenstelsel (`begrippen/*.yaml`)

Het hart van het kennismodel. 28 begrippen, elk met definitie, datatype, JAS-klasse, herkomst, relaties en volledige traceerbaarheid naar de wetstekst. Zie §[De kennisgraaf van dichtbij](#de-kennisgraaf-van-dichtbij) voor een voorbeeldbestand.

### Afleidingsregels (`regels/AR-*.yaml`)

9 formele als-dan-regels in vier typen:

| Type | Beschrijving | Voorbeeld in dit project |
|------|-------------|--------------------------|
| **Beslissingsregel** | Leidt een ja/nee-uitkomst af | *Is de belastingaanslag invorderbaar?* |
| **Rekenregel** | Berekent een waarde uit invoerwaarden | *Termijnbedrag = totaalbedrag ÷ aantal termijnen* |
| **Specialisatieregel** | Verfijnt of overschrijft een andere regel voor een deelgeval | *Lid 5: voor voorlopige aanslagen gelden andere termijnen* |
| **Beperkingsregel** | Beperkt de toepassingsruimte van een andere regel | *Terugvalregel lid 1 bij ontbreken Leidraad-grondslag* |

Elk bestand bevat invoer- en uitvoerbegrippen (als `begrip-id`), een formele-regel in RegelSpraak-oriëntatie, voorbeeldreeksen en een juridische toelichting herleidbaar naar de wettekst.

### RDF Turtle / SKOS (`kennisgraaf/begrippen.ttl`)

Het begrippenstelsel als linked data. RDF (Resource Description Framework) is de W3C-basisstandaard voor het semantisch web: alle informatie wordt uitgedrukt als drietallen (`subject – predikaat – object`) met unieke URI's. SKOS (Simple Knowledge Organization System) is het standaardvocabulaire voor begrippenstelsels, gebruikt door overheidsregisters als de Stelselcatalogus en data.overheid.nl.

Het `.ttl`-bestand is importeerbaar in triple stores (GraphDB, Apache Jena) en bevraagbaar via SPARQL. Voorbeeld:

```sparql
PREFIX skos:  <http://www.w3.org/2004/02/skos/core#>
PREFIX jas:   <http://regels.overheid.nl/jas/ontology#>
PREFIX begrip: <urn:jas:begrip:>

# Alle tijdsaanduidingen met hun definitie
SELECT ?label ?definitie WHERE {
  ?begrip jas:jasKlasse "tijdsaanduiding" ;
          skos:prefLabel ?label ;
          skos:definition ?definitie .
}
```

Uitvoeren via `make query-rdf` (past de query in `tools/sparql_query.rq` toe).

### Graafbestanden (`kennisgraaf/graph.gexf` + `graph.graphml`)

Het kennismodel als netwerkgraaf. Knopen zijn begrippen en annotaties; kanten zijn JAS-relaties (`leidt-tot`, `heeft`, `is-een`). Twee formaten:

- **GEXF** — het native formaat van [Gephi](https://gephi.org). Open `graph.gexf` in Gephi voor interactieve verkenning, community-detectie en layoutanalyse.
- **GraphML** — breed ondersteund XML-formaat, bruikbaar in yEd, Cytoscape en NetworkX.

Knoopattributen bevatten JAS-klasse, soort en status; kanten zijn gekleurd op JAS-klasse.

### Statische webapp (`webapp/index.html`)

Interactieve website in Rijkshuisstijl, automatisch gepubliceerd naar GitHub Pages bij elke push naar `main`. Gegenereerd door `python -m sitegen` vanuit de `sitegen/`-package. Bevat:

- **Begrippenlijst** — doorzoekbaar (MiniSearch) met JAS-klasse-badges, soort en status
- **Annotatiepagina's** — wetstekst, annoteerderijen, Mermaid-structuurdiagram, kruisreferenties en delegatiestructuur per artikel/lid
- **Regellijst** — formele RegelSpraak-regels met invoer/uitvoer-begrippen en testgevallen
- **Kennisgraaf** — interactieve D3.js-graaf met filter op JAS-klasse, drag, zoom en volledigscherm
- **Zoeken** — globale volledige-tekst-zoekfunctie over alle typen (MiniSearch)
- **SPARQL** — browsergebaseerde SPARQL-query-editor (Comunica) op de RDF/Turtle-export
- **Dark-mode** en responsief ontwerp (mobiel + desktop)

---

## Aan de slag

```bash
git clone git@github.com:palmw01/juridische-analyses.git
cd juridische-analyses

# Venv + dependencies + pre-commit hook in één stap
make setup

# Controleer of alles klopt
make validate

# Start een analysesessie met Claude Code in deze map
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

# Stap 5 — Exporteren
make export-graph                   # GEXF + GraphML

# Stap 6 — Webapp genereren
make webapp
open webapp/index.html

# Alles in één (zelfde als CI)
make ci
```

Bij elke commit draait automatisch de **pre-commit hook** (L1/L2-validatie).
Bij elke push naar `main` draait **GitHub Actions** (volledige validatie + alle exports + deploy webapp).

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

De W3C-basisstandaard voor het semantisch web. Alle informatie wordt uitgedrukt als **drietallen** (triples): `subject – predikaat – object`. Elk element heeft een unieke URI. Drietallen vormen samen een kennisgraaf die machineleesbaar is en over systeemgrenzen heen verbonden kan worden (linked data). In dit project wordt RDF gebruikt als exportformaat voor het begrippenstelsel en de afleidingsregels, bevraagbaar via SPARQL.

### RegelSpraak

De Nederlandse standaard voor het formeel specificeren van uitvoeringsregels in een leesbare maar machineparseerbare vorm. Ontwikkeld binnen de overheid voor regelimplementatie, onder meer gebruikt door de Belastingdienst. RegelSpraak-regels beschrijven als-dan-redenering in gestructureerde Nederlandse zinnen, waardoor juristen en IT-specialisten dezelfde specificatie kunnen lezen.

Voorbeeld van een `formele-regel` uit dit project (Beslissingsregel, art. 9 lid 1 IW):

```
Een belastingaanslag is invorderbaar
indien aan alle volgende voorwaarden is voldaan:
- de belastingaanslag heeft een dagtekening van het aanslagbiljet
- het tijdstip van beoordeling is gelegen op of na het tijdstip van
  de dagtekening van het aanslagbiljet plus zes weken
```

In dit project worden afleidingsregels in RegelSpraak-oriëntatie opgeslagen in het `formele-regel`-veld van `regels/AR-*.yaml`. Versie: RegelSpraak v2.3.0.

---

## Projectstructuur

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

rapporten/             validatierapport (gegenereerd)
scripts/               pre-commit hook (L1/L2-validatie bij commit)

sitegen/               statische webapp-generator (Python-package, `python -m sitegen`)
  cli.py               orchestratie: data laden → assets → pagina's
  html.py              HTML-primitieven (nav, breadcrumb, pagina-skelet)
  data.py              YAML/JSON-loaders voor begrippen, annotaties en regels
  mermaid.py           converter: diagram-JSON → Mermaid-flowsyntax
  assets.py            CSS/JS/icons kopiëren, data-JSON's genereren
  pages/               paginageneratoren (index, begrippen, annotaties, regels,
                       graph, search, sparql, artikel_indices)
  static/              bronassets: style.css (Rijkshuisstijl) + app.js (dark-mode)
  scripts/             esbuild-bundler voor Comunica SPARQL-engine

.build/                bouw-artefacten (niet ingecheckt)
  comunica.min.js      gebundelde Comunica SPARQL-engine (1,7 MB)

webapp/                gegenereerde statische site (niet ingecheckt; deploy via CI)

tools/                 Python-toolchain (9 scripts)
  validate_note.py     L1–L3 validatie per projectbestand
  export_rdf.py        YAML/JSON → RDF Turtle (SKOS)
  export_graph.py      begrippen + relaties → GEXF + GraphML
  check_enrichment.py  detecteert begrippen met meerdere bronartikelen
  jas_index_lib.py     gedeelde bibliotheek voor index-operaties
  query_rdf.py         SPARQL-query op gegenereerde TTL
  fetch_wettenbank.py  hulpscript: wetstekst ophalen via MCP
  extract_kruisrefs.py JCI URI-extractie uit annotaties
  queries/             SPARQL-querybestanden

.github/workflows/     CI (validatie) + deploy (GitHub Pages)
Makefile               alle build-targets
requirements.lock      pinned Python-dependencies
.claude/skills/        Claude Code skills + JAS-kaders
```

---

## Python-toolchain

| Make-target | Functie | Wanneer |
|-------------|---------|---------|
| `make setup` | venv + deps + pre-commit in één stap | Eenmalig na clone |
| `make validate` | L1 + L2 + L3 validatie, rapport in `rapporten/` | Na elke schrijfactie |
| `make export-rdf` | YAML → RDF Turtle (SKOS) | Na wijziging begrippen/regels |
| `make export-graph` | YAML/JSON → GEXF + GraphML | Na wijziging begrippen |
| `make webapp` | Genereert statische webapp in `webapp/` | Na wijzigingen |
| `make check-enrichment` | Detecteert begrippen met meerdere bronnen | Na nieuwe markeringen |
| `make query-rdf` | SPARQL-query op RDF-model | Bij analyse |
| `make test` | Testsuite uitvoeren (unit + integratie + property-based) | Na codewijzigingen |
| `make test-cov` | Testsuite met coverage-rapport (100% vereist) | Na codewijzigingen |
| `make ci` | test + validate + export-rdf + export-graph + check-enrichment | Voor push |
| `make install-hooks` | Installeert pre-commit hook | Eenmalig na clone |
| `make lock` | Installeert + pinned dependencies | Bij nieuwe deps |
| `make clean` | Verwijdert gegenereerde bestanden | Opruimen |

### Testsuite

623 tests — unit, integratie en property-based (Hypothesis) — met **100% line coverage** op alle toolchain-code (`tools/` en `sitegen/`). De suite is geschreven door Claude Code. `make test-cov` draait automatisch als eerste stap van CI; de build faalt bij minder dan 100%.

---

## Techniekstack

| Laag | Technologie |
|------|-------------|
| AI-assistent | Claude Code (Anthropic, claude-sonnet-4-6) met MCP |
| Wettenbrondata | wetten.overheid.nl via MCP-server (`wettenbank`-skill) |
| Project | Markdown + YAML (plain-text, geen Obsidian-afhankelijkheid) |
| Dataformaten | JSON (annotaties, bronnen), YAML (begrippen, regels), JSON Schema (validatie) |
| Python | 3.10+, PyYAML, jsonschema, networkx, rdflib |
| Graafvisualisatie | Graphviz (`dot`) — `sudo apt install graphviz` |
| Kennisgraaf-export | GEXF (Gephi), GraphML, RDF Turtle (SKOS), DOT (Graphviz) |
| Regelmodellering | RegelSpraak v2.3.0 |
| CI/CD | GitHub Actions — validatie op push/PR, deploy webapp op push naar main |

---

## Verantwoording

Deze werkruimte implementeert de **Wetsanalyse-methodiek** (Ministerie van BZK, 2024), gebaseerd op het **Juridisch Analyseschema (JAS) v1.0.10**, geworteld in de rechtstheorie van Wesley Newcomb Hohfeld (1913).

Alleen **A2 (markeren en classificeren)** en **A3 (betekenis vastleggen)** worden door AI ondersteund. A4 (valideren in multidisciplinair team), A5 (signaleren van lacunes) en A6 (kennismodel opstellen) zijn menselijke activiteiten buiten de scope van deze workflow.

Kaders: [JAS-taxonomie](./.claude/skills/annoteer/kaders.md) · [Begrippen](./.claude/skills/begrip/kaders.md) · [Regels](./.claude/skills/begrip/kaders-regels.md) · [BWB-mapping](./.claude/skills/wettenbank/bwb-mapping.md)
