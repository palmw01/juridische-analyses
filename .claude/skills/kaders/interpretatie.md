# Interpretatiemethoden

> **Bron:** Handleiding Wetsanalyse §3.5.3 (p. 44-46) — vier erkende interpretatiemethoden. Gebruikt door `annoteer-classificeer` (in `annotatierijen[].interpretatiemethode`) en `begrip-definitie` (in `markeringen[].interpretatiemethode`).

---

## De vier methoden

Het schema dwingt vier enumwaarden af: `grammaticaal`, `systematisch`, `teleologisch`, `wetshistorisch`.

| Methode | Wat | Wanneer gebruikt |
|---------|-----|------------------|
| **grammaticaal** | Taalkundige betekenis — wat staat er letterlijk? | Standaard voor de meeste markeringen; default als geen andere methode is toegepast |
| **systematisch** | Samenhang met andere bepalingen in dezelfde wet of andere wetten | Bij dubbelclassificatie, kruisreferenties, of als de betekenis volgt uit een ander artikel |
| **teleologisch** | Doel en strekking van de wet — *wat heeft de wetgever willen bereiken?* | Bij open normen, hardheidsclausules, redelijkheids-/billijkheidsbepalingen |
| **wetshistorisch** | Bedoeling wetgever uit parlementaire geschiedenis (MvT, kamerstukken) | Bij onduidelijke of bewust open formuleringen; bij twijfel die door MvT wordt opgehelderd |

## Praktijkregel

- Begin altijd grammaticaal.
- Schakel pas naar `systematisch`/`teleologisch`/`wetshistorisch` als de grammaticale betekenis ontoereikend of meerduidig is.
- **Documenteer de keuze** in `toelichting-klasse` (annotatie) of `toelichting` (begrip-context). Schrijf welke interpretatieve afweging is gemaakt.

## Jurisprudentie

Jurisprudentie is **geen primaire bron**, maar een interpretatiebron (Handleiding §3.5.4). Wanneer jurisprudentie de wetstoepassing verbreedt of beperkt:
- Vermeld de uitspraak in `bronnen-secundair` (`soort: jurisprudentie`) — zie `kaders/relaties.md` en `schemas/begrip.schema.json`.
- Geef in `toelichting-klasse` aan welke interpretatieve werking de jurisprudentie heeft.
- Voorkeur: de uitleg uit jurisprudentie wordt door de wetgever of beleidsmaker geformaliseerd in een beleidsregel of wetswijziging.
