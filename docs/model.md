# Kennismodel

Deze pagina beschrijft wat er in het kennismodel zit, hoe de bestanden samenhangen en welke standaarden worden gebruikt.

## Traceerbaarheidsketen

Elk begrip en elke regel is herleidbaar via een vaste ID-keten:

```text
wetstekst
  -> bronnen/{bwb-id}/art{N}.json
    -> annotaties/{bwb-id}/art{N}-lid{L}.json
      -> markering-id
        -> begrippen/{slug}.yaml
          -> regels/AR-{bwb-id}-*.yaml
            -> validaties/VR-{bwb-id}-*.yaml
```

YAML-bestanden bevatten verwijzingen zoals `bron-annotatie-id`, `markering-id` en `afleidingsregel-id`. Daardoor is de juridische herkomst van definities, relaties, regels en voorbeeldreeksen controleerbaar.

## Begrippen

Een begrip beschrijft een juridisch concept met definitie, datatype, JAS-klasse, herkomst, relaties en status.

| Veld | Functie |
|---|---|
| `begrip-id` | Stabiele identificatie binnen de kennisgraaf |
| `begripsnaam` | Leesbare naam / slug |
| `soort` | Datatype: `booleaans`, `datum`, `tekst` of `entiteit` |
| `jas-klasse` | JAS-classificatie van het begrip |
| `herkomst` | `direct` uit wetstekst of `afgeleid` via analyse |
| `definitie.kern` | Algemene betekenis van het begrip |
| `definitie.contexten` | Artikel- of brongebonden verfijningen |
| `markeringen` | Annotaties waarop de definitie is gebaseerd |
| `relaties` | `is-een`, `heeft` en `leidt-tot`-relaties |
| `afleidingsregel-id` | Koppeling naar een regel, indien van toepassing |

Verkort voorbeeld:

```yaml
begrip-id: BWBR0004770/art9/lid1/invorderbaarheid-belastingaanslag
begripsnaam: invorderbaarheid-belastingaanslag
soort: booleaans
jas-klasse: afleidingsregel
herkomst: afgeleid

definitie:
  kern: >-
    De beslissingsregel die bepaalt of een belastingaanslag invorderbaar is.
  contexten: []

markeringen:
  - markering-id: m-001
    bron-annotatie-id: BWBR0004770/art9/lid1
    tekst: is invorderbaar
    interpretatiemethode: grammaticaal
    bijdrage: primair

afleidingsregel-id: AR-BWBR0004770-art9-lid1-a
status: concept
```

## Afleidingsregels

Een afleidingsregel beschrijft een als-dan-redenering met invoerbegrippen, uitvoerbegrippen en een formele regel in RegelSpraak-oriëntatie.

| Type | Beschrijving |
|---|---|
| Beslissingsregel | Leidt een ja/nee-uitkomst af |
| Rekenregel | Berekent een waarde uit invoerwaarden |
| Specialisatieregel | Verfijnt of overschrijft een andere regel voor een deelgeval |
| Beperkingsregel | Beperkt de toepassingsruimte van een andere regel |

Verkort voorbeeld:

```yaml
regel-id: AR-BWBR0004770-art9-lid1-a
naam: bepalen invorderbaarheid belastingaanslag
soort: Beslissingsregel

invoer:
  - BWBR0004770/art9/lid1/belastingaanslag
  - BWBR0004770/art9/lid1/dagtekening-aanslagbiljet
uitvoer:
  - BWBR0004770/art9/lid1/invorderbaarheid-belastingaanslag

formele-regel: |
  Een belastingaanslag is invorderbaar
  indien aan alle volgende voorwaarden is voldaan:
  - de belastingaanslag heeft een dagtekening van het aanslagbiljet
  - het tijdstip van beoordeling is gelegen op of na de dagtekening plus zes weken
```

## Voorbeeldreeksen

Voorbeeldreeksen in `validaties/` zijn A4b-testmatrices voor afleidingsregels. Ze bevatten per kolom een testgeval met invoerwaarden, verwachte uitvoer en het oordeelveld `is-voorspelling-juist`.

Het oordeelveld blijft `?` totdat een juridisch expert de voorspelling beoordeelt. Bij ongeldige invoer staat het op `nvt`.

| Testsoort | Doel |
|---|---|
| Happy path | Normaal geval waarin de regel moet gelden |
| Grensgeval | Juridisch of temporeel kantelpunt |
| Negatief geval | Situatie waarin de uitkomst niet volgt |

## Standaarden

### JAS

JAS staat voor Juridisch Analyseschema — de classificatiebasis binnen de Wetsanalyse-methodiek. Wetselementen worden ingedeeld in juridische klassen, zodat de redenering achter een analyse expliciet en controleerbaar wordt.

| Klasse | Betekenis |
|---|---|
| rechtssubject | Actor of drager van rechten en plichten |
| rechtsobject | Object waarop een rechtsbetrekking ziet |
| rechtsbetrekking | Juridische verhouding: recht, plicht of bevoegdheid |
| rechtsfeit | Feit dat juridisch gevolg heeft |
| voorwaarde | Voorwaarde voor toepasselijkheid of gevolg |
| afleidingsregel | Regel die een uitkomst afleidt |
| tijdsaanduiding | Datum, termijn of tijdstip |
| operator | Logische of grammaticale operator |

Canonieke bron: [regels.overheid.nl/standaarden/wetsanalyse/v1.0.10](https://regels.overheid.nl/standaarden/wetsanalyse/v1.0.10)

### RegelSpraak

RegelSpraak is een Nederlandse standaard voor het formeel specificeren van uitvoeringsregels in leesbare, gestructureerde taal. Regels staan in RegelSpraak-oriëntatie in het veld `formele-regel` van `regels/AR-*.yaml`.

Het doel is dat juristen en regelanalisten dezelfde specificatie kunnen lezen, bespreken en valideren.

### RDF en SKOS

`kennisgraaf/begrippen.ttl` publiceert het begrippenstelsel als linked data via RDF (Resource Description Framework) en SKOS (Simple Knowledge Organization System).

| Prefix | Functie |
|---|---|
| `skos:` | Labels, definities en begrippenstructuur |
| `prov:` | Herkomstverwijzingen |
| `jas:` | Projectnamespace voor JAS-specifieke eigenschappen |
| `begrip:` | URI-basis voor begrippen |

Voorbeeldquery:

```sparql
PREFIX skos:  <http://www.w3.org/2004/02/skos/core#>
PREFIX jas:   <http://regels.overheid.nl/jas/ontology#>

SELECT ?label ?definitie WHERE {
  ?begrip jas:jasKlasse "tijdsaanduiding" ;
          skos:prefLabel ?label ;
          skos:definition ?definitie .
}
```

Uitvoeren via `make query-rdf` (query uit `tools/sparql_query.rq`).

### GEXF en GraphML

De relatiegraaf staat in twee formaten voor visualisatie en analyse:

| Bestand | Gebruik |
|---|---|
| `kennisgraaf/graph.gexf` | Gephi |
| `kennisgraaf/graph.graphml` | yEd, Cytoscape, NetworkX |

Knopen zijn begrippen en annotaties. Kanten zijn JAS-relaties: `heeft`, `is-een` en `leidt-tot`.
