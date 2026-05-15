# Valkuilen en best practices — /begrip

Raadpleeg dit bestand aan het begin van elke `/begrip`-run. Het bevat geleerde lessen uit eerdere runs.

---

## V1 — Naamgeving: generiek, niet scenario-specifiek

**Probleem:** De skill genereerde `vervaldatum-een-maand-voorbeeld-oktober` i.p.v. `vervaldag-kortemaand-een-maand`. De wet gebruikt een concreet voorbeeld (31 oktober) om een algemene rekenregel te illustreren; de begripsnaam beschreef het voorbeeld in plaats van de juridische rol.

**Regel:** De begripsnaam beschrijft de **juridische rol** of het **type uitkomst**, niet de invoerwaarden uit het voorbeeld.

| Fout | Correct |
|------|---------|
| `vervaldatum-een-maand-voorbeeld-oktober` | `vervaldag-kortemaand-een-maand` |
| `belastingbedrag-2024-ib` | `belastingbedrag-ib` |
| `drempel-150-euro` | `drempel-kleine-schuld` |

**Test:** Stel je voor dat de wet het voorbeeld vervangt door een ander getal of datum — blijft de naam dan nog kloppen? Zo niet: hernaam naar de abstracte rol.

---

## V2 — Operator hergebruik: check eerst bestaande begrippen

**Probleem:** De skill maakte `operator-of-betalingstermijn` aan terwijl `logische-of` al bestond. Beide vertegenwoordigen dezelfde logische OR-operator; het verschil was uitsluitend de tekstuele context.

**Regel:** Bij `jas-klasse: operator` altijd eerst zoeken op bestaande begrippen met dezelfde logische functie:

```bash
grep -rl "jas-klasse: operator" begrippen/
```

Voeg een bestaand operator-begrip toe via een `context`-markering als:
- De logische werking identiek is (EN, OF, NIET, dan-wel als OF-variant)
- Alleen de tekstuele formulering of context verschilt

Maak een **nieuw** begrip uitsluitend als de operator een eigenstandige juridische betekenis heeft die niet in bestaande begrippen past (bijv. `dan-wel` als gespecialiseerde exclusieve OR met termijnkeuze).

---

## V3 — Bijdrage `aanvullend` vereist altijd een contextregel

**Probleem:** Markering met `bijdrage: aanvullend` zonder bijbehorend item in `definitie.contexten[]` — de validator geeft hiervoor een L3-waarschuwing.

**Regel:** Kies `bijdrage: aanvullend` alleen als er een aantoonbaar nieuw definitie-facet is dat een context-item rechtvaardigt. Gebruik anders:
- `bijdrage: context` — zelfde concept, andere vindplaats, geen extra definitie-facet
- `bijdrage: primair` — meerdere primaire bronnen voor dezelfde kern

**Beslisregel:**
```
Heeft deze markering iets toe te voegen aan de kern dat nog niet gedekt is?
  Ja → aanvullend + bijbehorend contexten[]-item
  Nee → context (geen contexten[]-item nodig)
```

---

## V4 — Specialisatieregel vereist altijd een prioriteit

**Regel:** Elk begrip of regel met `soort: Specialisatieregel` moet een `prioriteit`-waarde hebben (integer ≥ 1). Lagere waarde = hogere prioriteit.

Stel prioriteit in als onderdeel van de `/begrip`-run — niet als nawerk. Gebruik `prioriteit: 1` als er geen concurrerende specialisatieregels zijn voor dezelfde toepassingssituatie.
