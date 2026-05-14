# Testsuite — Ontwerp en uitgangspunten

Dit document legt de architectuur en de ontwerpbeslissingen van de testsuite vast.
Het is het eerste aanspreekpunt bij vragen over teststructuur, testlaag-keuzes en kwaliteitsdoelen.

---

## Testpiramide

De suite volgt de klassieke testpiramide (Martin Fowler / Mike Cohn).
Elke laag heeft een eigen verantwoordelijkheid en een eigen snelheidsbudget.

```
          /\
         /  \        5%   E2E
        /    \       25%  Integratie
       /      \      65%  Unit
      /        \      5%  Property-based (dwarsdoorsnijdend)
     /____________\
```

| Laag | Aandeel | Snelheidsbudget | Doel |
|------|---------|-----------------|------|
| Unit | 65% | < 1s per test | Pure functies, één check per test |
| Integratie | 25% | < 5s per test | Module-samenwerking, file I/O via `tmp_path` |
| Property-based | 5% | < 10s per test | Invarianten over grote invoerdomeinen |
| E2E | 5% | < 30s per test | Volledige pijplijn (YAML → validate → HTML/RDF) |

**Hele suite**: doelstelling < 60s op een standaard ontwikkelmachine.

---

## Kernprincipes

### 1. Fast feedback loop
Unit-tests geven binnen seconden feedback. Zij worden het vaakst gedraaid — bij elke
opgeslagen wijziging (`make test-fast`). Zwaardere lagen draaien op CI of expliciet.

### 2. Determinisme
Een test levert bij elke run exact hetzelfde resultaat, ongeacht:
- volgorde van uitvoering
- tijdstip
- bestaande bestanden op het systeem

Geen willekeurige data in tests tenzij via Hypothesis (die zaadwaarden vastlegt).

### 3. Isolatie
Tests delen geen toestand. Elke test die het bestandssysteem nodig heeft, gebruikt
`tmp_path` (pytest's ingebouwde tijdelijke map). Geen globale fixtures met side-effects.

### 4. Traceerbaarheid — elke check heeft twee tests
Voor elke validator-check (L1, L2, L3) in `validate_note.py` bestaan twee tests:
- **Happy path**: geldige invoer → geen fout/waarschuwing
- **Failure path**: precies de foute invoer → exact de verwachte foutstring

Dit maakt regrессies onmiddellijk zichtbaar en documenteert het verwachte gedrag.

### 5. Fixtures als factory-functies, niet als vaste dicts
Fixtures zijn functies die een valide basisobject maken en gerichte aanpassingen
accepteren via `**overrides`. Dit voorkomt test-code-duplicatie en maakt afwijkingen
expliciet leesbaar:

```python
# Duidelijk: dit test precies één afwijking
maak_begrip(**{"definitie-gebaseerd-op": ["m-ontbreekt"]})
```

### 6. Snapshots voor gegenereerde output
HTML- en RDF-output worden niet handmatig geverifieerd maar vergeleken met opgeslagen
referentiebestanden (syrupy). Wijzigingen in gegenereerde output zijn altijd zichtbaar
als diff in de PR. Snapshot-bestanden worden gecommit en leven in `tests/snapshots/`.

---

## Laagoverzicht

### Laag 1 — Unit (`tests/unit/`)

Test één functie in isolatie. Geen bestandssysteem, geen netwerk.

| Bestand | Wat wordt getest |
|---------|-----------------|
| `test_validate_schema.py` | L1: JSON-schema validatie per veldtype (happy + failure) |
| `test_validate_integrity.py` | L2: cross-referentie checks (begrip-id, regel-id, markering-id) |
| `test_validate_quality.py` | L3: kwaliteitswaarschuwingen (onbevestigde markeringen, lege relaties, etc.) |
| `test_config.py` | `slugify`, `_text_color_for_bg` |
| `test_mermaid.py` | `diagram_to_mermaid` — syntaxcorrectheid van output |
| `test_rdf.py` | `turtle_literal`, `begrip_to_triples` |
| `test_jas_index.py` | `haal_kern`, `haal_contexten` |

### Laag 2 — Integratie (`tests/integration/`)

Test samenwerking van meerdere modules via het echte bestandssysteem (tmp_path).

| Bestand | Wat wordt getest |
|---------|-----------------|
| `test_data_loading.py` | `laad_begrippen`, `laad_regels`, `laad_annotaties` — YAML/JSON → dict |
| `test_validator_pipeline.py` | Volledige validator-pipeline per bestandstype (begrip, regel, annotatie) |
| `test_sitegen.py` | sitegen-data-laag → HTML-generatie (met snapshot-asserties) |

### Laag 3 — Property-based (`tests/property/`)

Test invarianten die voor alle (of zeer veel) invoerwaarden moeten gelden.
Draait met [Hypothesis](https://hypothesis.readthedocs.io/).

| Eigenschap | Functie | Invariant |
|------------|---------|-----------|
| Idempotentie | `slugify` | `slugify(slugify(x)) == slugify(x)` |
| Tekenset | `slugify` | Output bevat alleen `[a-z0-9-]` |
| Determinisme | `_text_color_for_bg` | Zelfde kleur → altijd zelfde tekstkleur |
| Veilige escaping | `turtle_literal` | Output bevat geen ongescapete aanhalingstekens |
| Schema-roundtrip | YAML-serialisatie | Begrip-dict → YAML → laad → dict: sleutelwaarden stabiel |

### Laag 4 — E2E (`tests/e2e/`)

Test de volledige pijplijn als black box via `subprocess`. Draait traag; alleen in CI
en bij expliciete aanroep (`make test-e2e`).

| Test | Scenario |
|------|---------|
| `test_make_validate_slaagt` | Valide fixture-project → exit code 0, geen L1/L2 |
| `test_make_validate_detecteert_l1` | YAML met schemafout → exit code 1, L1-fout in output |
| `test_make_webapp_genereert_html` | Fixture-project → `make webapp` → HTML-bestanden aanwezig |

---

## Fixture-architectuur

```
tests/
├── conftest.py            # project_root (tmp_path), gedeelde helpers
└── fixtures/
    ├── begrippen.py       # maak_begrip(**overrides) → dict
    ├── regels.py          # maak_regel(**overrides) → dict
    └── annotaties.py      # maak_annotatie(**overrides) → dict
```

**`project_root`-fixture** (`conftest.py`):
Bouwt een minimaal geldig project-skelet in `tmp_path`:
- `begrippen/`, `regels/`, `annotaties/`, `schemas/` mappen aanwezig
- Echte schema-bestanden gekopieerd vanuit de projectwortel
- Geen data-bestanden (tests schrijven zelf wat ze nodig hebben)

---

## Coverage-strategie

| Module | Doel | Prioritering |
|--------|------|-------------|
| `tools/validate_note.py` | ≥ 95% | Kritiek — core business logic |
| `sitegen/config.py` | ≥ 90% | Regrессie-gevoelig (slugify) |
| `sitegen/data.py` | ≥ 80% | Data-laag, integratie |
| `tools/rdf_export.py` | ≥ 80% | Complexe transformatie |
| `sitegen/html.py` | ≥ 70% | HTML-generatie |
| `sitegen/pages/` | ≥ 65% | Snapshots vangen regressies |
| **Overall** | **≥ 65%** | Afgedwongen via `--fail-under=65` |

Coverage is een **vangnet**, geen doel op zich. Een hoge coverage zonder zinvolle
assertions geeft een vals veiligheidsgevoel. Elke test moet een concrete claim maken.

---

## Technologiestapel

| Pakket | Versie | Rol |
|--------|--------|-----|
| `pytest` | ≥ 8.0 | Test-runner, fixtures, parametrize |
| `pytest-cov` | ≥ 5.0 | Coverage-meting en -rapportage |
| `hypothesis` | ≥ 6.100 | Property-based testing |
| `syrupy` | ≥ 4.6 | Snapshot-testing voor HTML/RDF |
| `pytest-xdist` | ≥ 3.5 | Parallelle uitvoering (`-n auto`) |

---

## Makefile-commando's

| Commando | Wat het doet |
|----------|-------------|
| `make test` | Volledige suite (unit + integratie + property) |
| `make test-fast` | Alleen unit-tests, stop bij eerste fout (`-x`) |
| `make test-cov` | Suite + coverage-rapport in terminal |
| `make test-e2e` | Inclusief E2E-tests (traag, apart targeten) |

---

## Wanneer welke laag uitbreiden?

| Situatie | Laag |
|----------|------|
| Nieuwe validator-check (L1/L2/L3) | Unit: happy + failure path |
| Nieuw YAML-veld in schema | Unit (schema), Integratie (data loading) |
| Nieuw gegenereerd HTML-blok | Snapshot (integratie) |
| Nieuwe transformatiefunctie (pure) | Unit + eventueel property |
| Nieuw Makefile-doel in pijplijn | E2E |
| Bug gevonden en gefixt | Eerst: regressietest die de bug reproduceert; dan: fix |

---

## Bekende beperkingen en risico's

| Risico | Mitigatie |
|--------|-----------|
| Snapshots verouderen bij legitieme wijzigingen | `pytest --snapshot-update` + diff reviewen in PR |
| E2E-tests vertragen CI | `make test` sluit E2E uit; `make test-e2e` separaat |
| `validate_note.py` heeft geen schone publieke API | Refactor nodig: `validate_begrip(data, project_root) -> (errors, warnings)` extracten vóór Sprint 2 |
| Hypothesis vindt niet-reproduceerbare fouten | Zaadwaarde vastleggen met `@settings(deriving=seed(42))` bij flaky cases |
