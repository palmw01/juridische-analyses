---
name: wa-data
description: "Haal wetstekst op via de wettenbank MCP en extraheer kruisreferenties. Gebruik bijv. 'Haal art. 25 IW 1990 op' of 'Zoek verwijzingen in art. 9 IW 1990'."
---

# wa-data — Dataverwerving

Deze skill helpt bij het ophalen van wetsteksten en het extraheren van kruisreferenties met behulp van de Wettenbank MCP tools.

## Werkwijze

### 1. Artikel ophalen
Gebruik `mcp_wettenbank_wettenbank_artikel` om de tekst van een artikel of specifiek lid op te halen.
Raadpleeg [bwb-mapping.md](references/bwb-mapping.md) voor de juiste BWB-id's en begripsbepalingen-artikelen.

### 2. Kruisreferenties extraheren
Extraheer kruisreferenties conform het protocol in [verwijzingen.md](references/verwijzingen.md).
- Voer parallelle aanroepen uit voor gevonden interne en externe verwijzingen.
- Gebruik `mcp_wettenbank_wettenbank_zoekterm` voor omgekeerde kruisreferenties (waar wordt dit artikel aangehaald?).

### 3. Begripsdefinities
Haal ook het begripsbepalingen-artikel op (zie bwb-mapping.md) om relevante definities in context te hebben.
