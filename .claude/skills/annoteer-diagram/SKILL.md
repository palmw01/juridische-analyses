---
name: annoteer-diagram
description: "A2c — bouwt het structuurdiagram met centrale klasse voor een geclassificeerd lid. Sluitstuk van de A2-keten."
context: fork
agent: general-purpose
---

# /annoteer-diagram — A2c structuurdiagram

Bouwt het `diagram`-object in een annotatie-lid-bestand: centrale klasse + knopen + kanten. Werkt op het resultaat van `annoteer-classificeer`.

> Lees vóór elke run: `.claude/skills/kaders/diagramregels.md`.

## Trigger

Aangeroepen door de orchestrator na `annoteer-classificeer` (geen eigen `/`-commando).

## Invoer

Annotatie-lid-bestand `annotaties/[B]/art[A]-lid[L].json` met gevulde `annotatierijen[]` (incl. `jas-klasse`).

## Werkwijze

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
7. Schrijf het bestand terug. Valideer de volledige annotatie-lid-JSON (nu schema-compleet na `annoteer-markeer` + `annoteer-classificeer` + dit diagram):
   ```
   tools/.venv/bin/python tools/validate_note.py --file annotaties/[B]/art[A]-lid[L].json
   ```

## Output

- `annotaties/[B]/art[A]-lid[L].json` — `diagram`-object ingevuld (`centrale-klasse`, `knopen[]`, `kanten[]`). Schema: `schemas/annotatie-lid.schema.json`.
- Mermaid-rendering wordt later gegenereerd door `make webapp` op basis van het JSON-diagram (zie `kaders/diagramregels.md §Voorbeeld`).

## Vervolg

Annotatie-lid is nu schema-compleet. De orchestrator gaat verder met `begrip-definitie` voor elke begrip-stub die door `annoteer-markeer` is aangemaakt.

## Kwaliteitseisen (proces)

- Knoop-id's zijn korte uppercase codes (RB, RF, RO, VW, AR, TA, …).
- Geen losse variabelen of parameters zonder verbinding met een Voorwaarde of Afleidingsregel. Een losse knoop zonder rand is een signaal dat markering/klasse heroverwogen moet worden (`kaders/diagramregels.md §Centrale klasse`).
- Verbind het diagram-centrum waar mogelijk met de rechtsbetrekking/het rechtsfeit uit het happy scenario (brugfunctie A1↔A2↔A3, `handleiding.pages.md` r. 1605-1614).
- Het schema laat één `diagram`-object per lid toe. Bij meerdere rechtsbetrekkingen: kies de meest centrale en noteer in `signalering` op de overige rechtsbetrekking-annotatierijen dat er aanvullende structuur is.
- **Menselijke validatie:** het diagram is een tussenresultaat en controlemiddel dat door vaktechnisch jurist + uitvoeringspraktijkjurist wordt beoordeeld (`kaders/menselijke-validatie.md`).

## Bronnen

- Schema: `schemas/annotatie-lid.schema.json`
- Kaders: `kaders/diagramregels.md`, `kaders/jas-taxonomie.md`, `kaders/menselijke-validatie.md`
- Canon: handleiding §3.4.2c (diagramregels; `handleiding.pages.md` r. 1592-1635, 1722-1726)
- Projectconventies: `kaders/projectconventies.md` #16 (kleurcodering), #17 (knooplabel-formaat)
