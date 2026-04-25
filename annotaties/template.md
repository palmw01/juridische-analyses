---
type: annotatie
tags:
  - template
artikel: "Art. [A] [W]"
bwb-id: [BWB-ID]
peildatum: [YYYY-MM-DD]
structuurpositie: "[pad-veld uit MCP, bijv. Hoofdstuk X > Afdeling Y > Artikel Z]"
tags-formaat:
  - annotatie
  - wet/[wet-afkorting]   # bijv. wet/iw1990
  - art/[nummer]          # bijv. art/25
begrippen: []             # wiki-links naar begrippen/ — gevuld na /begrip-alles
---

## Wetstekst (letterlijk, peildatum [PD])

> **1** [letterlijke tekst lid 1]
> **2** [letterlijke tekst lid 2]

## Annotatietabel

| Nr | Markering (letterlijk incl. lidwoord en verwijzingen) | JAS-klasse | Interpretatiemethode | Begrip |
|----|------------------------------------------------------|-----------|---------------------|--------|
| 1  | "[citaat]" | **[klasse]** | grammaticaal | begrippen/[slug] |
| 2  | "[citaat]" | **[klasse]** | systematisch | begrippen/[slug] |

## Diagram

<!-- Één diagram per Rechtsbetrekking; bij meerdere: genummerde blokken conform kaders.md §Diagramregels -->

### Diagram 1 — lid [L]: [korte omschrijving rechtsbetrekking]

```mermaid
graph LR
    RB["rechtsbetrekking\n'[markering ingekort]'"]:::rb
    RS1["rechtssubject\n'[markering]'"]:::rs
    RO["rechtsobject\n'[markering]'"]:::ro

    RS1 -->|rechthebbende| RB
    RB -->|voorwerp| RO

    classDef rb fill:#FF0000,color:#fff
    classDef rs fill:#4472C4,color:#fff
    classDef ro fill:#70AD47,color:#fff
```

## Delegatiestructuur

| Delegatiebevoegdheid | Vindplaats | Type | Invulling | Vindplaats invulling |
|---------------------|------------|------|-----------|---------------------|
| [omschrijving] | Art. [A] lid [L] [W] | Verplicht / Facultatief | [naam regeling] | Art. [Z] [regeling] |
