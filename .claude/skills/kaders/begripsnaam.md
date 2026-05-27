# Begripsnaam — vuistregels (A3a)

> **Bron:** Handleiding Wetsanalyse §3.5.2a (p. 38-41). Gebruikt door `begrip-definitie`.

---

## Algemeen

- Sluit zo nauw mogelijk aan bij de **letterlijke wetsformulering** (markering).
- Kies een nieuwe naam als de formulering niet precies genoeg is — onderbouw in `toelichting-klasse`.
- Voeg wettelijke context toe als dezelfde formulering in meerdere wetten anders betekent (bijv. `belastingschuldige iw 1990` vs `belastingplichtige awr`).
- **Hergebruik** een bestaande begripsnaam als de unieke betekenis identiek is — maak géén duplicaat. Eén begrip per unieke betekenis.

## Vaste opbouw en consistentie

- Begin met **zelfstandig naamwoord** (uitzondering: afleidingsregel/rechtsfeit → actieve werkwoordsvorm zoals `bepalen`, `vaststellen`, `indienen`).
- Gebruik al eerder gedefinieerde begrippen in de naam — wijziging werkt dan automatisch door.
- Gebruik dezelfde soort formuleringen voor hetzelfde type betekenis (consistentie vergemakkelijkt zoekopdrachten).

## Betekenis

- **Enkelvoudsvorm**, tenzij meervoud in de wet tot andere betekenis leidt.
- Zo min mogelijk afkortingen; bij gebruik: uitschrijven in de begripsdefinitie.
- Geen Romeinse cijfers (worden verward met letters).

## Leesbaarheid

- Geen hoofdletters (tenzij landsnaam of eigennaam).
- Lidwoorden/voorzetsels alleen opnemen als noodzakelijk voor leesbaarheid.
- Gebruik **niet** het woord "voor" (multi-interpretabel — kies `voorafgaand aan`, `bij` of `over`).
- Geen lidwoord of voorzetsel aan het begin van een begripsnaam.
- Geen ontkenningen in een begripsnaam (leidt tot dubbele ontkenning in taalpatronen).
- Zo kort mogelijk — schrijf eerst volledig uit, knip daarna in.

## Bestandsnaamgeving — projectconventie

- Bestandsnaam = alleen begripsnaam (`belastingaanslag.yaml`), **zonder** wet-suffix (`-iw-1990`).
- Slug: lowercase, spaties → koppelteken, bijzondere tekens weglaten.

## Scenario-specifieke valkuil — projectconventie

De begripsnaam beschrijft de **juridische rol** of het **type uitkomst**, niet de invoerwaarden uit een illustratief voorbeeld in de wet.

| Fout | Correct |
|------|---------|
| `vervaldatum-een-maand-voorbeeld-oktober` | `vervaldag-kortemaand-een-maand` |
| `belastingbedrag-2024-ib` | `belastingbedrag-ib` |
| `drempel-150-euro` | `drempel-kleine-schuld` |

**Test:** stel je voor dat de wet het voorbeeld vervangt door een ander getal of datum — blijft de naam dan kloppen? Zo niet: hernoem naar de abstracte rol.

`validate_note.py` waarschuwt op L3-niveau bij begripsnamen die een **maandnaam** (`januari…december`), een **vier-cijferig jaartal** (`19xx`/`20xx`) of het suffix **`-voorbeeld-`** bevatten.

## Homoniem vs. polyseem

Twee markeringen voor dezelfde term zijn **homoniemen** (→ twee aparte begrippen) bij ten minste twee van:

1. De juridische kernbetekenis verschilt per artikel — niet alleen de toepassingscontext.
2. De begrippen triggeren andere rechtsfeiten of leiden tot andere rechtsgevolgen.
3. Een geünificeerde definitie is niet substitueerbaar in beide bronartikelen.

Ze zijn **polyseem** (→ één verrijkt begrip met contexten) als de kern identiek is en het verschil uitsluitend de toepassingscontext betreft. Bij twijfel: substitutiebaarheidstest — formuleer een testzin met de veronderstelde kern; klopt die juridisch in beide bronartikelen, dan polyseem.

> Voorbeeld uit Handleiding: `bijdrage-inkomen` in art. 43 Zvw heeft drie verschillende betekenissen — drie homoniemen (`berekend bijdrage-inkomen`, `bijdrage-inkomen na nihilstelling`, `bijdrage-inkomen na maximumstelling`).
