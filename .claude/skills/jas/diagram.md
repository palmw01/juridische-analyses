# JAS-workflow — visueel overzicht

> Beschrijvend diagram. Het uitvoeringsprotocol staat in `SKILL.md`.  
> Bij verschil tussen dit diagram en `SKILL.md` is `SKILL.md` leidend.

---

## Flowchart

```mermaid
flowchart TD
    START(["/jas aanroep"])
    START --> S1["S1 — Bestaande annotatie controleren\nINDEX.md + Glob"]
    S1 --> S1A{"Gevonden?"}
    S1A -->|"ja"| S1B["Meld aan gebruiker\nwacht op bevestiging"]
    S1B -->|"nieuwe annotatie"| S2
    S1B -->|"gebruik bestaande"| EINDE
    S1A -->|"nee"| S2

    subgraph S2_BLOK ["S2 — Dataverwerving [→ wettenbank/SKILL.md]"]
        direction LR
        S2A["wettenbank_artikel [A]"]
        S2B["wettenbank_artikel [BD]"]
    end

    S2 --> S2_BLOK
    S2_BLOK --> S2C{"Lid-niveau check\nleden > 3 zonder [L]?"}
    S2C -->|"ja"| STOP(["Stop — vraag specifiek lid"])
    S2C -->|"nee"| S2D["Kruisreferenties extraheren\nverwijzingen.md"]

    subgraph HA2 ["Hoofdactiviteit 2 — Zichtbaar maken juridische structuur"]
        direction TB
        HA2_0["Lees kaders.md (JAS v1.0.10 taxonomie)"]
        HA2A["Deelactiviteit 2a\nExtractielijst wetsformuleringen"]
        HA2B["Deelactiviteit 2b\nKlasse toekennen per formulering\nAnnotatietabel (Begrip-kolom open)"]
        HA2C["Deelactiviteit 2c\nJuridisch structuurdiagram"]
        HA2_0 --> HA2A --> HA2B --> HA2C
    end

    S2D --> HA2

    HA2 --> HA2_OUT(["OUTPUT: geclassificeerde\nwetsformuleringen"])

    subgraph HA3 ["Hoofdactiviteit 3 — Vaststellen betekenis wetgeving"]
        direction TB
        HA3A["Deelactiviteit 3a\nBegrippen maken/verrijken\n[→ begrip/begrippen-check.md]\n+ wiki-links in Begrip-kolom"]
        HA3B["Deelactiviteit 3b\nAfleidingsregels vastleggen\nin begrip-noten"]
        HA3C["Deelactiviteit 3c\nToepassingsscenario's\nin begrip-noten"]
        HA3D["Deelactiviteit 3d\nRelateren aan juridische bronnen\nin begrip-noten"]
        HA3A --> HA3B --> HA3C --> HA3D
    end

    HA2_OUT --> HA3

    HA3 --> AFR["Afsluiting\nKwaliteitscheck + rapport samenstellen\n[→ publicatie/SKILL.md]"]
    AFR --> EINDE(["Retourneer bestandspad"])
```

---

## Parallelle aanroepen

| Stap | Parallel aanroepen |
|------|--------------------|
| S2 (dataverwerving) | `wettenbank_artikel [A]` + `wettenbank_artikel [BD]` |
| Kruisreferenties | interne refs + externe refs + `wettenbank_zoekterm` omgekeerd |

## Conditionele stappen

| Stap | Conditie |
|------|----------|
| S1B | Alleen als bestaande annotatie gevonden |
| STOP | Alleen als leden > 3 zonder lid-specificatie |
| Kruisreferenties parallel | Alleen als het JSON-model referenties bevat |
