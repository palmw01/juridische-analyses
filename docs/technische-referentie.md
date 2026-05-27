# Technische referentie

Deze pagina beschrijft de projectstructuur, Make-targets, toolchain en testsuite.

## Projectstructuur

```text
bronnen/{bwb-id}/      primaire wetstekst als genormaliseerde JSON
annotaties/{bwb-id}/   A2 JAS-annotaties per artikel en lid
begrippen/             A3a begrippenstelsel als YAML
regels/                A3b afleidingsregels als YAML
validaties/            A4b voorbeeldreeksen als YAML
schemas/               JSON Schema draft-07
kennisgraaf/           RDF/SKOS, GEXF en GraphML exports
rapporten/             validatierapporten en runrapporten
scripts/               pre-commit en pre-push hooks
sitegen/               statische webapp-generator
tools/                 validatie-, export- en hulpscripts
tests/                 unit-, integratie-, property- en e2e-tests
webapp/                gegenereerde statische site
```

## Make-targets

| Target | Functie |
|---|---|
| `make setup` | Maakt venv, installeert dependencies en hooks |
| `make validate` | Draait L1-L3 validatie |
| `make export-rdf` | Genereert RDF Turtle / SKOS |
| `make export-graph` | Genereert GEXF en GraphML |
| `make webapp` | Genereert de statische webapp |
| `make check-enrichment` | Detecteert begrippen met meerdere bronnen |
| `make query-rdf` | Voert SPARQL-query uit op RDF-export |
| `make test` | Draait standaard tests zonder e2e |
| `make test-fast` | Draait unit-tests en stopt bij eerste fout |
| `make test-cov` | Draait tests met coverage-rapport |
| `make test-e2e` | Draait e2e-tests apart |
| `make lint` | Draait ruff over `sitegen/` en `tools/` |
| `make lint-fix` | Draait ruff met automatische fixes |
| `make ci` | Draait test, validatie, exports en enrichment-check |
| `make clean` | Verwijdert gegenereerde bestanden |

## Python-toolchain

| Script | Functie |
|---|---|
| `tools/validate_note.py` | L1-L3 validatie van projectbestanden |
| `tools/export_rdf.py` | YAML/JSON naar RDF Turtle |
| `tools/export_graph.py` | Begrippen en relaties naar GEXF/GraphML |
| `tools/check_enrichment.py` | Detectie van begrippen met meerdere bronnen |
| `tools/jas_index_lib.py` | Gedeelde I/O-helpers en JAS-indexfuncties |
| `tools/genereer_run_rapport.py` | Per-run Markdownrapporten |
| `tools/query_rdf.py` | SPARQL-query op gegenereerde TTL |
| `tools/fetch_wettenbank.py` | Wetstekst ophalen via MCP |
| `tools/extract_kruisrefs.py` | JCI URI-extractie uit annotaties |

## Sitegenerator

`sitegen/` genereert de statische webapp vanuit de bronbestanden.

Belangrijke onderdelen:

| Pad | Functie |
|---|---|
| `sitegen/cli.py` | Orchestratie van dataloading, assets en pagina's |
| `sitegen/data.py` | YAML/JSON-loaders |
| `sitegen/html.py` | HTML-primitieven |
| `sitegen/mermaid.py` | Diagram-JSON naar Mermaid |
| `sitegen/assets.py` | CSS/JS/icons en data-assets |
| `sitegen/pages/` | Paginageneratoren |
| `sitegen/static/` | Bronassets voor de webapp |

## Testsuite

De tests staan in `tests/` en zijn geconfigureerd via `pyproject.toml`.

| Map | Inhoud |
|---|---|
| `tests/unit/` | Unit-tests per tool |
| `tests/integration/` | Integratietests voor sitegen en pipeline |
| `tests/property/` | Property-based tests via Hypothesis |
| `tests/e2e/` | End-to-end tests via subprocess |
| `tests/fixtures/` | Testdata en factories |

Coverage is ingesteld op `fail_under = 100` voor `tools/` en `sitegen/`.

## Techniekstack

| Laag | Technologie |
|---|---|
| AI-assistent | Claude Code met MCP |
| Wettenbrondata | wetten.overheid.nl via MCP-server |
| Projectdata | Markdown, YAML en JSON |
| Validatie | JSON Schema, Python |
| Python | 3.11, PyYAML, jsonschema, networkx, rdflib |
| Kennisgraaf | RDF Turtle, SKOS, GEXF, GraphML |
| Webapp | Statische HTML/CSS/JS |
| CI/CD | GitHub Actions |
