---
description: Documenteer of actualiseer een juridisch begrip in begrippen/. Gebruik: /begrip [slug] of /begrip-alles art. [A] [W]
context: fork
agent: general-purpose
---

# Skill: /begrip

**Trigger:** `/begrip [slug]` of `/begrip-alles art. [A] [W]`

Voert Activiteit 3a en 3b uit van de Wetsanalyse-methode. Leest de door `/annoteer` aangemaakte begrip-noten (met gevulde frontmatter) en vult de A3-inhoud in: definitie, voorbeelden, kenmerken en relaties. Bij JAS-klasse Afleidingsregel maakt de skill tevens een regel-noot aan in `regels/`.

**De wetstekst wordt niet opnieuw opgehaald.** De annotatiefrontmatter (`markering`, `jas-klasse`, `bron`, `peildatum`, `interpretatiemethode`) is de enige bron.

**Lees vóór elke run eerst beide kaderdocumenten volledig in:**
- `.claude/skills/begrip/kaders.md` — begrippenkader (A3a + A6d): naamgeving, definitie, soort, herkomst, relaties, identificatie
- `.claude/skills/begrip/kaders-regels.md` — regelkader (A3b + A6e): typen, taalpatronen, rechtsfeit, tussenresultaten, RegelSpraaak

De kaders zijn bindend voor elke beslissing in A3a en A3b. De bestaande inline secties hieronder zijn beknopte verwijzingslagen; de kaders bevatten de gezaghebbende volledige uitwerking.

---

## Voorbereiding

1. **Lees de begrip-noot** in `begrippen/[slug].md` — de frontmatter bevat alle benodigde informatie.
2. **Zoek alle annotaties** die naar dit begrip verwijzen:
   ```
   grep -rl "begrippen/[slug]" annotaties/
   ```
   Lees elke gevonden annotatie-noot. Verzamel per annotatie de rij uit de annotatietabel die betrekking heeft op dit begrip: `markering`, `interpretatiemethode` en de artikelreferentie. Dit zijn alle markeringen die de definitie moeten voeden.
3. **Vul het `bronnen`-veld** in de frontmatter met alle gevonden artikelreferenties (als lijst). Het bestaande `bron`-veld blijft ongewijzigd.
4. **Controleer bestaande begrippen** in `begrippen/` op verwante begrippen voor relaties (is-een, heeft, leidt-tot).

Bij `/begrip-alles art. [A] [W]`: zoek alle begrip-noten waarvan het `bron`-veld verwijst naar dat artikel, en verwerk ze achtereenvolgens.

---

## Definitie opstellen (A3a)

- Sluit zo nauw mogelijk aan bij de **letterlijke markering** in het frontmatter-veld `markering`.
- Benoem interpretatie- en preciseringskeuzes expliciet.
- Als de betekenis afwijkt van de letterlijke formulering: onderbouw dit in `toelichting-klasse`.
- Geen parafrase van de wetstekst — gebruik de markering als startpunt.
- Vul altijd `soort` (datatype) en `herkomst` (direct/afgeleid) in conform begrippenkader §Eigenschappen.
- Markeer identificatiebegrippen met `[id]` in het `soort`-veld conform begrippenkader §Identificatiebegrippen.
- Vul `aliases` in met bekende juridische synoniemen (of laat leeg als er geen synoniemen bestaan).
- Leg kardinaliteit vast in de `## Relaties`-tabel (1:1 / 1:n / n:m) conform begrippenkader §Relaties en kardinaliteit.

---

## Begripsnaam-vuistregels (Handleiding §3.5.2a)

- Begin met **zelfstandig naamwoord** (uitzondering: afleidingsregel/rechtsfeit → actieve werkwoordsvorm)
- **Enkelvoudsvorm**, tenzij meervoud in de wet tot andere betekenis leidt
- **Geen hoofdletters**, geen Romeinse cijfers, zo min mogelijk afkortingen (bij gebruik: uitschrijven in definitie)
- Sluit zo nauw mogelijk aan bij de letterlijke markering
- Voeg wettelijke context toe als dezelfde formulering in meerdere wetten anders betekent
- **Hergebruik** een bestaande begripsnaam als de unieke betekenis identiek is — maak géén duplicaat

---

## Voorbeelden opstellen (Leidraad product #13)

- Minimaal **2 stellingen** (waar/niet-waar) die de grenzen van het begrip toetsen.
- Minimaal **1 grensgeval** dat de precieze afbakening demonstreert.
- Stellingen zijn concreet en toetsbaar (geen vage parafrasen).

---

## Kenmerken en relaties (Leidraad product #14)

- Leg relaties met andere begrippen vast via de velden `is-een`, `heeft`, `leidt-tot` in de frontmatter.
- Gebruik wiki-links naar betrokken begrip-noten: `[[begrippen/[slug]]]`.
- Vul ook de `## Relaties`-tabel in de body in.
- **Alleen uitgaande (forward) relaties opnemen** — nooit backward links die al als forward link in een ander begrip staan. Zie begrippenkader §Relaties en kardinaliteit.

---

## Afleidingsregel-noot (A3b — alleen bij JAS-klasse Afleidingsregel)

Bij JAS-klasse **Afleidingsregel**: maak aanvullend een noot aan in `regels/AR-[art]-[nr].md`.
- Vul altijd het `naam`-veld in met een leesbare naam (actieve werkwoordsvorm).
- Vul altijd het `rechtsfeit`-veld in met een wiki-link naar het triggerende rechtsfeit.
- Identificeer tussenresultaten in impliciete algoritmen en maak daarvoor eigen begrip-noten + regel-noten aan. Voeg de tag `#tussenresultaat` toe aan de tags-lijst van elke tussenresultaat-begrip-noot.
- Kies het taalpatroon uit `## Formele regel` passend bij het `soort` en verwijder de overige blokken.
- Controleer of het taalpatroon aansluit bij de RegelSpraaak-oriëntatie uit het regelkader.

**Vier soorten:**
- **Beslissingsregel**: ja/nee uitkomst (recht bestaat of niet)
- **Rekenregel**: numerieke berekening (bedrag, duur, hoogte)
- **Beperkingsregel**: beperkt of maximeert een waarde of recht
- **Specialisatieregel**: specificeert of preciseert een algemene regel voor een deelgeval

Frontmatter:
```yaml
---
type: afleidingsregel
regel-id: AR-[art]-[nr]
naam: ""            # leesbare naam, bijv. "bepalen invorderbaarheid belastingaanslag"
soort: [Beslissingsregel | Rekenregel | Beperkingsregel | Specialisatieregel]
tags:
  - afleidingsregel
  - wet/[wet-afkorting]
  - art/[nummer]
afgeleid-van: "[[annotaties/[wet]-art[nr]]]"
peildatum: [YYYY-MM-DD]
bepaalt: "[[begrippen/[slug]]]"
invoer: []
uitvoer: []
operators: []
---
```

Body:
- `## Formele regel` — als-dan structuur met invoerbegrippen en uitvoerbegrip
- `## Toelichting` — tracering naar specifiek lid + interpretatiemotivering
- `## Voorbeeldreeksen` — minimaal 2 invoer/uitkomst-combinaties (Leidraad product #20)

Na aanmaken: update het `afleidingsregels`-veld in de bijbehorende begrip-noot met een wiki-link.

---

## Output per begrip

Vul de body van `begrippen/[slug].md` volledig in:

**Definitie-blok bij één markering:**
```markdown
## Definitie

*[markering]* *(Art. [A] lid [L] [W], peildatum [PD])*

[begripsdefinitie]
```

**Definitie-blok bij meerdere markeringen (na multi-annotatie actualisatie):**
```markdown
## Definitie

Markeringen:
- *[markering 1]* *(Art. [A] lid [L] [W], peildatum [PD], [interpretatiemethode])*
- *[markering 2]* *(Art. [B] lid [M] [W], peildatum [PD], [interpretatiemethode])*

[begripsdefinitie — synthese van alle markeringen]
```

**Volledige body-structuur:**
```markdown
## Definitie

[zie bovenstaande blokken — kies passende variant]

## Voorbeelden

| Stelling | Waar? | Toelichting |
|----------|-------|-------------|
| [concrete stelling] | ja / nee | [waarom geldt het (niet)?] |
| [grensgeval] | ja / nee | [waarom geldt het (niet)?] |

## Kenmerken

- [eigenschap 1]
- [eigenschap 2]

## Relaties

| Type | Kardinaliteit | Begrip |
|------|---------------|--------|
| is een | — | [[begrippen/...]] |
| heeft | 1:1 / 1:n / n:m | [[begrippen/...]] |
| leidt tot | — | [[begrippen/...]] |
```

Update tevens de frontmatter-velden `definitie`, `is-een`, `heeft`, `leidt-tot`.

---

## Kwaliteitseisen (niet-onderhandelbaar)

- Definitie uitsluitend gebaseerd op de `markering` in de frontmatter — nooit rechtstreeks uit de wetstekst of eigen kennis.
- Definitie is substitueerbaar: test altijd of de definitietekst het begrip kan vervangen in een zin zonder betekenisverlies.
- Definitie bevat geen punt aan het einde.
- Voorbeelden bevatten altijd minimaal één grensgeval, elk met toelichting (waarom geldt het wel/niet?).
- Relaties zijn altijd wiki-links, nooit losse tekst.
- Bij JAS-klasse Afleidingsregel: regel-noot in `regels/` is verplicht.
- Regel-noten bevatten altijd voorbeeldreeksen voor validatie.
- Stel `status: concept` in op alle nieuw aangemaakte begrip-noten.

### Verplichte checklist-output na elk begrip

Print na het opslaan van elke begrip-noot de volgende checklist in de chat (vink af op basis van de daadwerkelijk ingevulde frontmatter):

```
Kennismodel-checklist — [begripsnaam]
✅/⬜ soort ingevuld
✅/⬜ herkomst ingevuld
✅/⬜ kardinaliteit in relaties-tabel
✅/⬜ [id]-markering (n.v.t. indien geen identificatiebegrip)
✅/⬜ wiki-link afleidingsregel (n.v.t. indien herkomst: direct)
✅/⬜ aliases aanwezig (leeg is toegestaan indien geen synoniemen)
✅/⬜ geldigheid-van ingevuld
✅/⬜ status: concept
```

Bij `/begrip-alles`: print de checklist per begrip afzonderlijk, direct nadat dat begrip is opgeslagen.
