# JAS-workflow — visueel overzicht

> Beschrijvend diagram. Het uitvoeringsprotocol staat in `PROTOCOL.md`.  
> Bij verschil tussen dit diagram en `PROTOCOL.md` is `PROTOCOL.md` leidend.

---

## Flowchart

```mermaid
flowchart TD
    START(["/jas aanroep"])
    START --> S1["Stap 1 — kaders.md lezen"]
    S1 --> S2["Stap 2 — Argument parsen\n[A] [W] [B] [L] [BD]"]
    S2 --> S3{"Stap 3 — Bestaande annotatie?"}

    S3 -->|"gevonden"| S3A["Meld aan gebruiker\nwacht op bevestiging"]
    S3A -->|"nieuwe annotatie gewenst"| S4
    S3A -->|"gebruik bestaande"| EINDE
    S3 -->|"niet gevonden"| S4

    subgraph S4_BLOK ["Stap 4 — Wetstekst ophalen (parallel)"]
        direction LR
        S4A["wettenbank_artikel [A]"]
        S4B["wettenbank_artikel [BD]"]
    end

    S4 --> S4_BLOK
    S4_BLOK --> S4C{"Lid-niveau check\nleden > 3 zonder [L]?"}
    S4C -->|"ja"| STOP(["Stop — vraag specifiek lid"])
    S4C -->|"nee"| S4D["begrippen-protocol.md\nuitvoeren per term"]

    S4D --> S5{"Stap 5 — [W] = IW 1990?"}
    S5 -->|"nee"| S6

    subgraph S5_BLOK ["Stap 5 — Leidraad + art. 1 IW (parallel)"]
        direction LR
        S5A["wettenbank_artikel\nart. 1 IW 1990"]
        S5B["wettenbank_artikel\nLeidraad [A]"]
    end

    S5 -->|"ja"| S5_BLOK
    S5_BLOK --> S6

    subgraph S6_BLOK ["Stap 6 — Kruisreferenties (parallel)"]
        direction LR
        S6A["intern:\nwettenbank_artikel per ref"]
        S6B["extern:\nwettenbank_artikel per ref"]
        S6C["omgekeerd:\nwettenbank_zoekterm"]
    end

    S6["Stap 6 — kruisverwijzingen.md lezen"] --> S6_BLOK
    S6_BLOK --> S7

    subgraph S7_BLOK ["Stap 7 — JAS-annotatie"]
        S7A["7a: Extractielijst opstellen"]
        S7B["Annotatietabel per lid"]
        S7C["7d: Verificatie vs extractielijst"]
        S7A --> S7B --> S7C
    end

    S7 --> S7_BLOK
    S7_BLOK --> S8["Stap 8 — Afleidingsregels\nen rekenstructuur"]

    S8 --> S9{"Stap 9 — [W] = IW 1990?"}
    S9 -->|"ja"| S9A["Awb-toepasselijkheidscheck\n(art. 1 lid 2 IW 1990)"]
    S9A --> S10
    S9 -->|"nee"| S10

    S10["Stap 10 — Rapportopbouw\n§2 §3 §6 §9–§11"]
    S10 --> S11["Stap 11 — Kwaliteitscheck\nrapportformat.md + checklist"]
    S11 --> S12["Stap 12 — Frontmatter\ntimestamp + rapport opslaan"]
    S12 --> S13["Stap 13 — INDEX.md bijwerken"]
    S13 --> S13B["Stap 13b — Hub-note\n⚠️ VERPLICHT"]
    S13B --> S14["Stap 14 — git commit + push"]
    S14 --> EINDE(["Stap 15 — Retourneer bestandspad"])
```

---

## Leeswijzer parallelle aanroepen

| Stap | Parallel aanroepen |
|------|--------------------|
| 4 | `wettenbank_artikel [A]` + `wettenbank_artikel [BD]` |
| 5 | `wettenbank_artikel art. 1 IW 1990` + `wettenbank_artikel Leidraad [A]` |
| 6 | interne refs + externe refs + `wettenbank_zoekterm` omgekeerd |

## Conditionele stappen

| Stap | Conditie |
|------|----------|
| 5 | Alleen als `[W]` = IW 1990 of UB IW 1990 |
| 9 | Alleen als `[W]` = IW 1990 |
| §7.3 (rapport) | Alleen als `[W]` = IW 1990 |
| §8 (rapport) | Alleen als `[W]` = IW 1990 of UB IW 1990 |

## Sub-bestanden

| Bestand | Geladen in stap |
|---------|----------------|
| `../shared/bwb-mapping.md` | Stap 2 |
| `kaders.md` | Stap 1 |
| `begrippen-protocol.md` | Stap 4 |
| `../begrip/template.md` | Via begrippen-protocol (stap 4) |
| `kruisverwijzingen.md` | Stap 6 |
| `rapportformat.md` | Stap 11 |
