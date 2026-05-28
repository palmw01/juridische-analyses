---
name: begrip-bron
description: "A3d — registreert secundaire bronnen (Leidraad, beleidsregels, MvT, jurisprudentie) bij een begrip of regel via bronnen-secundair."
context: fork
agent: general-purpose
---

# /begrip-bron — A3d secundaire bronnen

Vult `bronnen-secundair[]` in op een begrip-YAML of regel-YAML. Primaire bronnen blijven `markeringen[].bron-annotatie-id` (begrip) en `annotatie-id` (regel) — die wijzen naar de wettekst zelf via `annotaties/`. Secundaire bronnen zijn de extra ankers die de **betekenis** of **toepassing** verduidelijken.

> **Verschil met primaire bron:** primaire bronnen zijn voor traceerbaarheid van de classificatie; secundaire bronnen voor interpretatie (Handleiding §3.5.4: jurisprudentie als interpretatiebron).

## Trigger

Aangeroepen door de orchestrator of `/begrip [slug]` na `begrip-scenario` (geen eigen `/`-commando).

## Invoer

Een begrip-YAML of regel-YAML met gevulde definitie/formele regel.

## Werkwijze

1. Lees het bestand (`begrippen/[slug].yaml` of `regels/AR-….yaml`).
2. Bepaal welke secundaire bronnen relevant zijn. Beslisregel per `soort`-enum:

   | Soort | Wanneer toevoegen |
   |-------|-------------------|
   | `leidraad` | Leidraad Invordering 2008 of vergelijkbare uitvoeringsleidraad |
   | `beleidsregel` | Officieel gepubliceerd beleid (Awb art. 1:3 lid 4) |
   | `memorie-van-toelichting` | MvT bij het oorspronkelijke wetsvoorstel |
   | `jurisprudentie` | Uitspraak van een rechter die de betekenis nader uitlegt |
   | `kamerstukken` | Overige parlementaire stukken (nota's, amendementen, moties) |
   | `ander` | Restcategorie — motiveer in `toelichting` |

3. Voeg per relevante bron een entry toe aan `bronnen-secundair[]` met `soort`, `vindplaats`, optioneel `toelichting`. Voor het exacte formaat: zie `schemas/begrip.schema.json` resp. `schemas/regel.schema.json` (`bronnen-secundair`-veld) en bestaande voorbeelden in `begrippen/`.
4. Schrijf het bestand terug met `schrijf_yaml`.
5. Valideer.

### Wanneer overslaan

Als er geen secundaire bronnen relevant zijn — bv. bij een direct geclassificeerde brondefinitie die nergens nader wordt geduid — laat `bronnen-secundair[]` leeg of weg.

## Output

- `begrippen/[slug].yaml` óf `regels/AR-….yaml` met `bronnen-secundair[]` aangevuld. Schema: `schemas/begrip.schema.json` resp. `schemas/regel.schema.json`.

## Vervolg

Begrip is nu A3-compleet. De orchestrator gaat verder met de volgende begrip-stub, of (na alle begrippen) met A4b (`valideer`) per gegenereerde regel.

## Kwaliteitseisen (proces)

- Vindplaats moet uniek en herleidbaar zijn (ECLI-nummer voor jurisprudentie; paragraafnummer voor Leidraad; Kamerstuknummer voor kamerstukken).
- Toelichting beschrijft welke interpretatieve werking de bron heeft.
- Geen herhaling van wat al in `markeringen[]` of `annotatie-id` staat.
- Jurisprudentie nooit als primaire bron behandelen — zie `kaders/interpretatie.md §Jurisprudentie` en `kaders/glossarium.md` (primaire bron vs. interpretatiebron, Leidraad r. 572-580).
- **Menselijke validatie:** de relevantie en interpretatieve werking van een secundaire bron worden door een vaktechnisch jurist beoordeeld (`kaders/menselijke-validatie.md`).

Structurele vereisten (soort-enum) worden door schema afgedwongen.

## Bronnen

- Schema: `schemas/begrip.schema.json`, `schemas/regel.schema.json` (veld `bronnen-secundair[]`)
- Kaders: `kaders/interpretatie.md` (rol jurisprudentie + secundaire bronnen), `kaders/glossarium.md`, `kaders/menselijke-validatie.md`
- Canon: handleiding §3.5.4 (interpretatiebronnen); leidraad §2.4 (primaire vs secundaire bron; `leidraad.pages.md` r. 572-580)
- Projectconventies: `kaders/projectconventies.md` #20 (bronnen-secundair structuur + soort-enum)
