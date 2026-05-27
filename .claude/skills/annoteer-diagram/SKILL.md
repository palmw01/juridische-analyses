---
description: "A2c — bouwt het structuurdiagram met centrale klasse voor een geclassificeerd lid. Sluitstuk van de A2-keten."
context: fork
agent: general-purpose
---

# /annoteer-diagram — A2c structuurdiagram

Bouwt het `diagram`-object in een annotatie-lid-bestand: centrale klasse + knopen + kanten. Werkt op het resultaat van `annoteer-classificeer`.

> Lees vóór elke run: `.claude/skills/kaders/diagramregels.md`.

## Invoer

Annotatie-lid-bestand `annotaties/[B]/art[A]-lid[L].json` met gevulde `annotatierijen[]` (incl. `jas-klasse`).

## Stappen

1. Lees het annotatie-lid-bestand.
2. **Bepaal de centrale klasse** volgens prioriteit (zie `kaders/diagramregels.md`):
   1. Rechtsbetrekking
   2. Rechtsfeit
   3. Afleidingsregel
   4. Voorwaarde
   - Als alle vier ontbreken: schrijf geen `diagram`-veld en stop. Meld in de output: `Geen centrale klasse gevonden; diagram niet van toepassing.`
3. **Construeer knopen** voor:
   - de centrale klasse (id zoals `RB`, `RF`, `AR`, `VW`);
   - alle rechtssubjecten die rechthebbend of plichthebbend zijn (id `RS1`, `RS2`, …);
   - rechtsobject(en);
   - aanwezige voorwaarden, rechtsfeiten, afleidingsregels, delegatiebevoegdheden;
   - variabelen/parameters **alleen** als onderdeel van een voorwaarde of afleidingsregel in hetzelfde diagram.
4. **Construeer kanten** met de standaard randlabels (tabel in `kaders/diagramregels.md`).
5. **Knooplabel-formaat**:
   ```
   [JAS-klasse]<br/>'[markering ingekort tot max. 40 tekens, eindig op zelfstandig naamwoord, "…" indien afgekort]'
   ```
6. **Begrip-id per knoop**: vul `begrip-id` in als de knoop direct overeenkomt met een bestaand begrip; anders `null`.
7. Schrijf het bestand terug. Valideer de volledige annotatie-lid-JSON (nu schema-compleet na `annoteer-markeer` + `annoteer-classificeer` + dit diagram): `tools/.venv/bin/python tools/validate_note.py --file annotaties/[B]/art[A]-lid[L].json`.

## Voorbeeld

Zie `kaders/diagramregels.md` §Voorbeeld voor een complete Mermaid-uitvoer (gegenereerd door `make webapp` op basis van het JSON-diagram).

## Kwaliteitseisen

- De knoop-id's zijn korte uppercase codes (RB, RF, RO, VW, AR, TA, …).
- Geen losse variabelen of parameters zonder verbinding met een Voorwaarde of Afleidingsregel.
- Bij meerdere rechtsbetrekkingen: meerdere genummerde diagrammen toevoegen aan een `diagrammen[]`-veld (alternatief: schrijf het hoofd-diagram en noteer in `signalering` op de annotatierij dat er een extra diagram is).
