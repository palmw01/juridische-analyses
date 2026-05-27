# Relaties tussen begrippen — projectconventie

> **Bron:** Handleiding Wetsanalyse §3.5.2 (dat begrippen onderlinge relaties hebben) + projectconventie voor structuur/kardinaliteit (georiënteerd op A6d, buiten scope). Gebruikt door `begrip-definitie`.

---

## Structuur

Leg relaties vast in het `relaties`-object van de begrip-YAML:

```yaml
relaties:
  is-een:
  - BWBR0004770/art9/lid1/belastingaanslag       # array van begrip-id-strings
  heeft:
  - begrip-id: BWBR0004770/art9/lid1/aanslagbiljet
    kardinaliteit: "1:1"                          # 1:1 | 1:n | n:m (verplicht)
  leidt-tot:
  - begrip-id: BWBR0004770/art9/lid5/invorderbaarheid
    relatie-soort: causaal                        # causaal | procedureel | definitoir
    kardinaliteit: null                           # optioneel
```

## Drie relatietypes

| Type | Betekenis | Kardinaliteit | Voorbeeld |
|------|-----------|---------------|-----------|
| `is-een` | Specialisatie (subtype) — dit begrip is een specifieke variant | n.v.t. | naheffingsaanslag is-een belastingaanslag |
| `heeft` | Compositie | `1:1`, `1:n` of `n:m` (verplicht) | belastingaanslag heeft 1:1 aanslagbiljet |
| `leidt-tot` | Causaal/procedureel/definitoir verband | optioneel | betalingstermijn leidt-tot invorderbaarheid |

## Forward-only

**Alleen uitgaande relaties opnemen.** Neem geen backward link op die al als forward link in een ander begrip staat.

Voorbeeld: als `belastingaanslag` `heeft 1:1 dagtekening-aanslagbiljet` bevat, dan neemt `dagtekening-aanslagbiljet` **geen** `heeft belastingaanslag` op. De graaf-export inverteert backward zo nodig zelf.

## Verplicht bij afgeleide begrippen

Bij `herkomst: afgeleid` is minimaal één `leidt-tot`-relatie verplicht (of een `heeft`-relatie naar de invoerbegrippen van de afleidingsregel) — anders staat het afgeleide begrip los van de regelketen.

## L3-waarschuwing

`validate_note.py` geeft een L3-waarschuwing als alle drie relatie-arrays leeg zijn (`is-een`, `heeft`, `leidt-tot`). Lege relaties zijn toegestaan maar wijzen vaak op een onvolledig begrip.
