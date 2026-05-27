---
description: "A3d — registreert secundaire bronnen (Leidraad, beleidsregels, MvT, jurisprudentie) bij een begrip of regel via bronnen-secundair."
context: fork
agent: general-purpose
---

# /begrip-bron — A3d secundaire bronnen

Vult `bronnen-secundair[]` in op een begrip-YAML of regel-YAML. Primaire bronnen blijven `markeringen[].bron-annotatie-id` (begrip) en `annotatie-id` (regel) — die wijzen naar de wettekst zelf via `annotaties/`. Secundaire bronnen zijn de extra ankers die de **betekenis** of **toepassing** verduidelijken.

> **Verschil met primaire bron:** primaire bronnen zijn voor traceerbaarheid van de classificatie; secundaire bronnen voor interpretatie (Handleiding §3.5.4: jurisprudentie als interpretatiebron).

## Invoer

Een begrip-YAML of regel-YAML met gevulde definitie/formele regel.

## Bron-soorten (schema-enum)

| Soort | Wanneer toevoegen |
|-------|-------------------|
| `leidraad` | Leidraad Invordering 2008 of vergelijkbare uitvoeringsleidraad |
| `beleidsregel` | Officieel gepubliceerd beleid (Awb art. 1:3 lid 4) |
| `memorie-van-toelichting` | MvT bij het oorspronkelijke wetsvoorstel |
| `jurisprudentie` | Uitspraak van een rechter die de betekenis nader uitlegt |
| `kamerstukken` | Overige parlementaire stukken (nota's, amendementen, moties) |
| `ander` | Restcategorie — motiveer in `toelichting` |

## Stappen

1. Lees het bestand (`begrippen/[slug].yaml` of `regels/AR-….yaml`).
2. Identificeer welke secundaire bronnen relevant zijn. Beslisregel:
   - Is er een Leidraad-passage die de toepassing nader regelt? → `leidraad`.
   - Is er gepubliceerd beleid? → `beleidsregel`.
   - Is er jurisprudentie die de wetstoepassing verbreedt of beperkt? → `jurisprudentie` + interpretatieve werking in `toelichting`.
   - Wordt het begrip in de MvT toegelicht op een manier die de wettekst verduidelijkt? → `memorie-van-toelichting`.
3. Voeg per relevante bron een entry toe:
   ```yaml
   bronnen-secundair:
   - soort: leidraad
     vindplaats: "Leidraad Invordering 2008, §9.5"
     toelichting: "Beleidsmatige invulling van het verschuiven van de vervaldag van termijnen in kortemaanden."
   - soort: jurisprudentie
     vindplaats: "HR 2 oktober 2020, ECLI:NL:HR:2020:1559"
     toelichting: "Bevestigt dat de zes-wekentermijn ingaat op de dagtekening van het aanslagbiljet, niet op de datum van ontvangst."
   ```
4. Schrijf het bestand terug.
5. Valideer.

## Wanneer overslaan

Als er geen secundaire bronnen relevant zijn — bv. bij een direct geclassificeerde brondefinitie die nergens nader wordt geduid — laat `bronnen-secundair[]` leeg of weg.

## Kwaliteitseisen

- Vindplaats moet uniek en herleidbaar zijn (ECLI-nummer voor jurisprudentie; paragraafnummer voor Leidraad; Kamerstuknummer voor kamerstukken).
- Toelichting beschrijft welke interpretatieve werking de bron heeft.
- Geen herhaling van wat al in `markeringen[]` of `annotatie-id` staat.
- Jurisprudentie nooit als primaire bron behandelen — zie `kaders/interpretatie.md §Jurisprudentie`.
