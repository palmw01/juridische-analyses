---
title: Juridische wetsanalyse
---

# Juridische wetsanalyse

Werkruimte voor gestructureerde wetsanalyse op het domein **invordering van rijksbelastingen**. Doel is wetgeving zo te analyseren dat de resultaten bruikbaar zijn voor de uitvoeringspraktijk: rechtmatig, uitlegbaar en controleerbaar.

## Methodiek: Wetsanalyse

Wetsanalyse is een multidisciplinaire methode voor het expliciet maken, concretiseren en vastleggen van de betekenis van wet- en regelgeving. De activiteiten worden iteratief uitgevoerd — per artikel, per lid, steeds verder verfijnd — vanuit het perspectief van de uitvoeringspraktijk.

| # | Activiteit | Omschrijving | AI |
|---|-----------|-------------|-----|
| 1 | Bepalen van het werkgebied | Scope, juridische scenario's, bronnenselectie | — |
| **2** | **Zichtbaar maken van de juridische structuur** | Markeren, classificeren (JAS), structuurdiagram | **✓** |
| **3** | **Vaststellen van de betekenis** | Begrippen, afleidingsregels, traceerbaarheid | **✓** |
| 4 | Valideren van de analyseresultaten | Toetsing met juridische scenario's en voorbeeldreeksen | — |
| 5 | Signaleren van ontbrekende beleidsregels | Interpretaties en nadere invullingen ter oplevering | — |
| 6 | Opstellen van een kennismodel | Gegevensmodel, regelmodel, procesmodel | — |

De AI-output — annotatie-noten (A2), begrip-noten (A3a) en afleidingsregel-noten (A3b) — vormt het analysemateriaal dat input is voor A4–A6. Die activiteiten vallen buiten de scope van deze werkruimte.

## Navigatie

*   **[[wetteksten/index|Wetsteksten]]**  
    *Letterlijke wetsteksten per bronregeling, objectief en MCP-afkomstig. Input voor Activiteit 2.*
*   **[[annotaties/index|Annotaties (A2)]]**  
    *Wetsartikelen voorzien van markeringen, JAS-classificaties en structuurdiagrammen.*
*   **[[begrippen/index|Begrippen (A3a)]]**  
    *Atomaire definities, kenmerken en relaties van juridische begrippen.*
*   **[[regels/index|Afleidingsregels (A3b)]]**  
    *Beslissings-, reken-, beperkings- en specialisatieregels afgeleid uit de regelgeving.*

---

## Traceerbaarheid

Rechtmatigheid vereist dat beslissingen in de uitvoeringspraktijk traceerbaar zijn naar wet- en regelgeving. De wikilink-keten in de vault maakt dit zichtbaar:

```
begrip-noot  →  annotatie-noot  →  wetstekst-noot
```

Elk begrip verwijst naar de annotatie waaruit het is afgeleid. De annotatie verwijst naar de wetstekst-noot met de letterlijke wettekst. Zo is elk analyseresultaat direct herleidbaar naar de primaire juridische bron.

---

## Obsidian Graph View

De graph is filterbaar en kleurbaar via geneste tags. Kleuren volgen de JAS-kleurcodering: blauw voor rechtssubjecten, rood voor rechtsbetrekkingen, geel voor rechtsfeiten, enzovoort.

| Filter | Resultaat |
|--------|-----------|
| `tag:#wet/iw1990` | Alles m.b.t. IW 1990 |
| `tag:#jas/rechtsbetrekking` | Alleen rechtsbetrekkingen |
| `path:begrippen/` | Alleen begrip-noten |

---

*De bronbestanden van deze kennisomgeving zijn beschikbaar op [GitHub](https://github.com/palmw01/juridische-analyses).*