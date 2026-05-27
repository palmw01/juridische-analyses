---
description: "A2b — wijst jas-klasse, interpretatiemethode en toelichting toe aan markeringen. Volgt op annoteer-markeer."
context: fork
agent: general-purpose
---

# /annoteer-classificeer — A2b classificeren

Vult `jas-klasse`, `interpretatiemethode`, `toelichting-klasse` en eventueel `signalering` in voor elke rij in een bestaand annotatie-lid-bestand.

> Lees vóór elke run: `.claude/skills/kaders/jas-taxonomie.md` en `.claude/skills/kaders/interpretatie.md`.

## Invoer

Annotatie-lid-bestand `annotaties/[B]/art[A]-lid[L].json` (of sectie-variant) waarvan de markeringen zijn ingevuld door `annoteer-markeer` maar de klasse-velden nog leeg of placeholder zijn.

## Stappen

1. Lees het annotatie-lid-bestand.
2. Voor elke rij in `annotatierijen[]`:
   1. Kies de **meest specifieke jas-klasse** (zie `kaders/jas-taxonomie.md` voor de 16 enumwaarden + herkenningsvragen).
      - Tijdsaanduiding > variabele; plaatsaanduiding > parameter.
      - Bij overlap met meerdere markeringen op dezelfde tekst: één rij per klasse.
   2. Bepaal `interpretatiemethode` (`grammaticaal` / `systematisch` / `teleologisch` / `wetshistorisch`).
      - Default `grammaticaal`. Andere methode alleen bij expliciete reden — documenteer in `toelichting-klasse`.
   3. Vul `toelichting-klasse` met:
      - Waarom deze JAS-klasse boven alternatieven gekozen is.
      - Verdieping van het type (bijv. type rechtsbetrekking).
      - Expliciet gesignaleerde meerduidigheid (indien van toepassing).
   4. Vul `signalering` als de markering een spanning of open norm bevat (bijv. dubbelclassificatie, ontbrekende delegatie-invulling). Anders `null`.
3. **Delegatiebevoegdheid:** als een rij `jas-klasse: delegatiebevoegdheid` heeft, voeg een entry toe aan `delegatiestructuur[]`:
   - `omschrijving`, `vindplaats`, `type` (Verplicht/Facultatief — zie `kaders/jas-taxonomie.md §Delegatiebevoegdheid`).
   - `invulling` en `vindplaats-invulling` als de gedelegeerde regeling beschikbaar is; anders `null` of "Niet beschikbaar via wettenbank — handmatige verificatie vereist".
4. **Kruisreferenties:** als een markering een verwijzing bevat naar een ander artikel, voeg een entry toe aan `kruisreferenties[]` (forward).
5. Schrijf het bestand terug met `schrijf_json`.
6. Valideer.

## Volledigheidscheck (intern)

Vink af welke van de 13 hoofdklassen je hebt overwogen voor dit lid (zie `kaders/markeerregels.md §Volledigheidscheck`). Niet alle 13 hoeven aanwezig.

## Vervolg

Roep daarna `annoteer-diagram` aan om het structuurdiagram te bouwen.

## Kwaliteitseisen

- `jas-klasse` moet één van de 16 enumwaarden zijn (schema-afgedwongen).
- `toelichting-klasse` is geen lege string — minimaal de klassemotivering.
- Meerduidigheid expliciet signaleren via `signalering`.
- Delegatieketens volledig uitwerken (wet → amvb → ministeriële regeling).
