# Markeerregels (A2a)

> **Bron:** Handleiding Wetsanalyse §3.4.2a (p. 33). Gebruikt door `annoteer-markeer`.

---

## Brongetrouwe uitgangspunten

1. **Lidwoord meenemen.** Maakt de volledigheidscheck mogelijk (is elk stukje tekst geclassificeerd?).
2. **Verwijzing meenemen.** Als een stukje brontekst een verwijzing bevat, hoort die in de markering — ze draagt bij aan de betekenis.
   - Voorbeeld: "het overeenkomstig het eerste, dan wel het tweede, lid berekende bedrag aan belasting".
3. **Markeer precies dat stukje tekst dat maximaal de betekenis representeert** van het begrip dat je uiteindelijk wilt maken. De toe te kennen klasse beïnvloedt de markeringsomvang:
   - Variabele: geen werkwoord/voorwaarden meenemen, wel het lidwoord.
   - Afleidingsregel: wél werkwoorden en voorwaarden, inclusief lidwoord, verwijzing en punt.
4. **Voorwaarde-markering: gehele zin of zinsdeel** waarin de voorwaarde omschreven wordt, inclusief voegwoord (indien, als, tenzij, mits).
5. **Werk meteen met concrete voorbeelden.** Dat maakt scherp wat je wel/niet in de markering meeneemt.
6. **Start bij de klasse die gecreëerd of afgeleid wordt** — niet bij de context. Identificeer dezelfde betekenis daarna in andere tekststukjes.
7. **Begin bij de centrale klassen** rechtsbetrekking en rechtsfeit (Handleiding p. 34); zie `diagramregels.md`.
8. **Markeringen mogen overlappen.** Dezelfde wetsformulering kan meerdere klassen krijgen (Handleiding §3.4.2b).
   - **Projectconventie:** één rij per klasse in de annotatietabel; dezelfde markering mag herhaald worden.
   - **Heuristiek temporele dubbelclassificatie:** een tijdsaanduiding die het aanvangsmoment van een termijn of het intreden van een rechtsgevolg markeert, is tegelijk een rechtsfeit ("tijdsverloop met rechtsgevolg" — zie `jas-taxonomie.md §Rechtsfeit`). Voeg in dat geval een aparte rechtsfeit-rij toe voor dezelfde wetsformulering.

## Klasse-specifieke markeringsregels

| JAS-klasse | Wat te markeren |
|-----------|----------------|
| Rechtssubject | Zelfstandig naamwoord voor persoon/entiteit incl. lidwoord |
| Rechtsobject | Zelfstandig naamwoord voor het voorwerp incl. lidwoord |
| Rechtsbetrekking | Werkwoord + hulpwerkwoord (kan, mag, is verplicht, dient te) |
| Rechtsfeit | Actieve werkwoordsvorm + tijdsverloop |
| Voorwaarde | Gehele zin of zinsdeel m.i.v. voegwoord (indien, als, tenzij, mits) |
| Afleidingsregel | Volledige als-dan-constructie incl. lidwoord, werkwoorden en punt |
| Variabele | Zelfstandig naamwoord (kenmerk) + lidwoord |
| Parameter | Tariefwaarde, drempel, maximum, minimum |
| Tijdsaanduiding | Tijdstip, tijdvak, termijn |
| Plaatsaanduiding | Geografische aanduiding, jurisdictie |
| Delegatiebevoegdheid | Volledige delegatiezin incl. "bij amvb" of "bij ministeriële regeling" |
| Brondefinitie | Volledige aanhef + onderdelen van de begripsomschrijving |
| Operator | Rekenkundig teken of logisch woord (vermeerderd met, EN, OF, NIET) |

## Volledigheidscheck (intern)

13 hoofdklassen afvinken voor elk geannoteerd lid:

```
☐ rechtssubject    ☐ rechtsobject    ☐ rechtsbetrekking
☐ rechtsfeit       ☐ voorwaarde      ☐ afleidingsregel
☐ delegatiebevoegdheid                ☐ brondefinitie
☐ variabele        ☐ parameter       ☐ operator
☐ tijdsaanduiding  ☐ plaatsaanduiding
```

Niet alle 13 hoeven aanwezig te zijn in elk lid — afvinken markeert alleen dat je elke klasse hebt overwogen. Elk gemarkeerd fragment wordt volledig geclassificeerd; geen half-ingevulde rijen.
