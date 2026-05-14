---
description: "Voert Activiteit 3a en 3b uit van de Wetsanalyse-methode: definitie, voorbeelden, kenmerken en afleidingsregels op basis van annotaties. Gebruik: /begrip [slug] | /begrip-alles art. [A] [W]"
context: fork
agent: general-purpose
---

# /begrip — Activiteit 3: begrippen en afleidingsregels

> **Conflictresolutie:** Bij tegenstrijdigheid tussen deze SKILL.md en `kaders.md` of `kaders-regels.md` zijn **de kaderdocumenten leidend**. SKILL.md geeft procesinstructies; de kaders geven de juridisch-inhoudelijke en analytische normen.

## Triggervormen

| Trigger | Wanneer gebruiken |
|---------|-------------------|
| `/begrip [slug]` | Één begrip-YAML invullen op basis van gevulde `markeringen`-lijst |
| `/begrip-alles art. [A] [W]` | Alle begrip-YAML's van een artikel achtereenvolgens verwerken |

Voert Activiteit 3a en 3b uit. Leest de door `/annoteer` aangemaakte begrip-YAML-stubs en vult de A3-inhoud in: definitie, soort, herkomst, relaties en kenmerken. Bij JAS-klasse Afleidingsregel maakt de skill tevens een regel-YAML aan in `regels/`.

**Bronbestanden zijn `.yaml`-bestanden in `begrippen/` — geen Markdown.**
**De wetstekst wordt niet opnieuw opgehaald.** De `markeringen[].tekst`-velden in de begrip-YAML zijn de enige bron.

**Lees vóór elke run eerst beide kaderdocumenten volledig in:**
- `.claude/skills/begrip/kaders.md` — begrippenkader (A3a + A6d)
- `.claude/skills/begrip/kaders-regels.md` — regelkader (A3b + A6e)

---

## Voorbereiding

0. **Idempotentiecontrole:** Controleer of `definitie`, `soort`, `herkomst` en `relaties` in `begrippen/[slug].yaml` al zijn ingevuld. Een begrip is "afgerond" als `definitie` niet leeg is, `soort` een geldige waarde heeft, `herkomst` is ingevuld, en `relaties` minstens één niet-lege lijst heeft. Als alles al is ingevuld: meld "begrip [slug] is al afgerond (definitie + soort + herkomst + relaties)" en stop — overschrijf nooit zonder expliciete bevestiging van de gebruiker.

1. **Lees de begrip-YAML** in `begrippen/[slug].yaml`. De `markeringen`-lijst bevat alle benodigde informatie.

2. **Controleer de enrichment-queue:** Lees `rapporten/enrichment-queue.json` en controleer of dit begrip daarin voorkomt. Als er een open beslissing is (d.w.z. geen `beslissing`-veld of status `te-verrijken`): stop en meld "begrip [slug] staat open in enrichment-queue — los de enrichment-beslissing eerst op". Als de beslissing is genomen: voer die uit vóórdat je de definitie opstelt.

3. **Zoek alle annotaties** die dit begrip markeren — zoek op `begrip-id` in alle annotatie-JSON's:
   ```
   grep -rl "[begrip-id]" annotaties/
   ```
   Lees elke gevonden annotatie-JSON. Verzamel per annotatie de rij uit `annotatierijen` die betrekking heeft op dit begrip: `markering`, `interpretatiemethode`, `jas-klasse`, `toelichting-klasse` en het annotatie-id. Gebruik dit om de `markeringen`-lijst te verifiëren en de top-level velden `jas-klasse` en `toelichting-klasse` in de begrip-YAML bij te werken.

4. **Controleer bestaande begrippen** in `begrippen/` op verwante begrippen voor de relaties (`is-een`, `heeft`, `leidt-tot`).

Bij `/begrip-alles art. [A] [W]`: zoek alle begrip-YAML's waarvan een markering een `bron-annotatie-id` heeft dat begint met `[B]/art[A]`:
   ```
   grep -rl "bron-annotatie-id.*[B]/art[A]" begrippen/
   ```
   Vervang `[B]` door het BWB-id en `[A]` door het artikelnummer. Verwerk ze achtereenvolgens.

---

## Definitie opstellen (A3a) — gelaagd model

Het `definitie`-veld is een **object** met twee onderdelen:

```yaml
definitie:
  kern: "De universele betekenis — geldig voor alle bronartikelen"
  contexten:
    - markering-id: m-002
      bijdrage: verfijning          # verfijning | uitbreiding | uitzondering
      tekst: "Artikel-specifieke toevoeging..."
      toelichting: "Optionele juridische motivering"   # optioneel
```

### Kern

- Sluit zo nauw mogelijk aan bij de **letterlijke tekst** in de primaire markering (`bijdrage: primair`).
- De kern is de **wets-overstijgende** betekenis: geldig voor **alle** bronartikelen van dit begrip.
- Benoem interpretatie- en preciseringskeuzes expliciet.
- Onderbouw **altijd** de klassekeuze — ook als die overeenkomt met de letterlijke formulering.
- Geen parafrase van de wetstekst — gebruik de markering als startpunt.
- Kern bevat **geen punt** aan het einde.
- Test altijd of de kerntekst het begrip kan vervangen in een zin zonder betekenisverlies (substitutietest).
- `definitie-gebaseerd-op` bevat **uitsluitend** de markering-id's die de kern staven (primaire markeringen).

### Contexten (contextlagen)

Elk item in `contexten[]` documenteert een **artikel-specifieke inkleuring** van de kern:

| Bijdrage-type | Wanneer | Voorbeeld |
|---|---|---|
| `verfijning` | De kern blijft intact; het artikel specificeert de kern voor één context | Art. 9 lid 5 bepaalt dat de aanslag invorderbaar is in gelijke termijnen — de kern (invorderbaarheid zodra termijn verstreken) wijzigt niet |
| `uitbreiding` | Het artikel voegt een betekenisdimensie toe die buiten de kern valt | Een aanvullend artikel definieert een extra toepassingsscenario dat de kern-tekst niet dekt |
| `uitzondering` | Het artikel beperkt of sluit de kern in een specifieke context uit | Een derogatiebepaling die de hoofdregel terzijde stelt |

**Lege contexten (`contexten: []`) zijn de norm** voor begrippen die slechts uit één artikel stammen of waarbij de kern voor alle bronnen volstaat.

### Verrijkingsprotocol — nieuw artikel markeert een bestaand begrip

Wanneer een `/annoteer`-run een nieuwe markering toevoegt aan een begrip dat al een kern heeft:

1. **Analyseer** de nieuwe markering ten opzichte van `definitie.kern`.
2. **Besluit**:
   - Identieke tekst, zelfde betekenis → voeg alleen toe aan `markeringen[]`, `bijdrage: context`; geen nieuw contextitem; `contexten` blijft leeg
   - Specificeert de kern voor één wetscontext → voeg toe aan `contexten[]` met `bijdrage: verfijning`
   - Voegt nieuwe betekenisdimensie toe → voeg toe aan `contexten[]` met `bijdrage: uitbreiding`; overweeg of de kern moet worden bijgesteld
   - Beperkt of sluit de kern uit → `bijdrage: uitzondering`
   - Onverenigbaar met de kern → **signaleer homoniem-conflict** en stel splitsing voor; maak géén context-item aan
3. **Kern-update**: pas `definitie.kern` uitsluitend aan als de nieuwe bron een fundamenteler inzicht biedt dat voor **alle** bronnen geldt. Verhoog `definitie-versie` bij kernwijziging.
4. **definitie-gebaseerd-op**: bevat uitsluitend markering-ids die de kern staven — verwijder ids van markeringen die nu in `contexten` zijn opgenomen.

---

## Begripsnaam-vuistregels (Handleiding §3.5.2a)

- Begin met **zelfstandig naamwoord** (uitzondering: afleidingsregel/rechtsfeit → actieve werkwoordsvorm)
- **Enkelvoudsvorm**, tenzij meervoud in de wet tot andere betekenis leidt
- **Geen hoofdletters**, geen Romeinse cijfers, zo min mogelijk afkortingen
- Sluit zo nauw mogelijk aan bij de letterlijke markering
- Voeg wettelijke context toe als dezelfde formulering in meerdere wetten anders betekent
- **Hergebruik** een bestaande begripsnaam als de unieke betekenis identiek is — maak géén duplicaat

---

## Soort-systeem (8 typen)

| soort | Gebruik |
|-------|---------|
| `monetair-bedrag` | Geldbedrag (euro, cent) |
| `percentage` | Percentage of breuk |
| `tijdsduur` | Duur (weken, maanden, jaren) |
| `datum` | Kalenderdatum (ankerpunt) |
| `booleaans` | Binaire uitkomst (ja/nee, waar/niet-waar) |
| `tekst` | Vrije tekst of kwalitatieve aanduiding |
| `enumeratie` | Gesloten lijst van waarden |
| `entiteit` | Rechtspersoon, object of samengesteld gegeven |

`soort-id: true` als dit begrip dient als unieke identificatiesleutel voor een entiteit (bijv. aanslagnummer, BSN).

---

## Kenmerken en relaties (Leidraad product #14)

Leg relaties vast via de `relaties`-sectie in de YAML:
```yaml
relaties:
  is-een:
  - begrip-id: BWBR0004770/art9/lid1/belastingaanslag
  heeft:
  - begrip-id: BWBR0004770/art9/lid1/dagtekening-aanslagbiljet
    kardinaliteit: "1:1"
  leidt-tot:
  - begrip-id: BWBR0004770/art9/lid5/vervaldag-volgende-termijnen
    relatie-soort: causaal
    kardinaliteit: null
```

- `is-een`: array van `begrip-id` strings (generalisatierelatie — naar bovenliggend type)
- `heeft`: array van objecten met `begrip-id` + `kardinaliteit` (`1:1`, `1:n`, `n:m`)
- `leidt-tot`: array van objecten met `begrip-id` + `relatie-soort` (`causaal`, `procedureel`, `definitoir`) + optioneel `kardinaliteit`

**Alleen uitgaande (forward) relaties opnemen** — nooit backward links die al als forward link in een ander begrip staan.

Bij `herkomst: afgeleid` is minimaal één `leidt-tot`-relatie verplicht (of een `heeft`-relatie naar de invoerbegrippen van de afleidingsregel).

---

## Voorbeelden en kenmerken (optioneel, in begrip-YAML)

Voeg voorbeelden en kenmerken direct toe aan `begrippen/[slug].yaml`:

```yaml
voorbeelden:
  - stelling: "[concrete stelling]"
    waar: true
    toelichting: "[waarom?]"
  - stelling: "[grensgeval]"
    waar: false
    toelichting: "[waarom niet?]"

kenmerken:
  - "[eigenschap 1]"
  - "[eigenschap 2]"
```

- Minimaal **2 stellingen** (waar/niet-waar) die de grenzen van het begrip toetsen.
- Minimaal **1 grensgeval**.
- Alle stellingen zijn concreet en toetsbaar.
- Velden zijn optioneel — laat weg als nog niet ingevuld.

---

## Afleidingsregel-YAML (A3b — alleen bij JAS-klasse Afleidingsregel)

Bij JAS-klasse **afleidingsregel**: maak aanvullend een YAML aan in `regels/AR-[bwb-id]-art[N]-lid[L]-[nr].yaml`.

```yaml
regel-id: AR-[bwb-id]-art[N]-lid[L]-[nr]
naam: "[leesbare naam, actieve werkwoordsvorm]"
soort: [Beslissingsregel|Rekenregel|Beperkingsregel|Specialisatieregel]
bwb-id: [B]
artikel: "[A]"
lid: "[L]"
peildatum: "[YYYY-MM-DD]"
annotatie-id: [B]/art[A]/lid[L]
rechtsfeit-id: "[begrip-id van het triggerende rechtsfeit, of null bij tussenresultaat]"
invoer:
- [begrip-id]
uitvoer:
- [begrip-id]
operators:
- [operator-naam]
formele-regel: |
  [als-dan structuur — kies taalpatroon uit kaders-regels.md]
toelichting: |
  [tracering naar specifiek lid + interpretatiemotivering]
voorbeeldreeksen:
- invoerwaarden: "[beschrijving invoerwaarden]"
  verwachte-uitkomst: "[beschrijving uitkomst]"
  juridisch-juist: true
  toelichting: "[waarom juridisch juist]"
- invoerwaarden: "[beschrijving invoerwaarden]"
  verwachte-uitkomst: "[beschrijving uitkomst]"
  juridisch-juist: false
  toelichting: "[waarom onjuist of grenswaarde]"
tussenresultaat: false
```

**Vier soorten:**
- **Beslissingsregel**: ja/nee uitkomst (recht bestaat of niet)
- **Rekenregel**: numerieke berekening (bedrag, duur, hoogte)
- **Beperkingsregel**: beperkt of maximeert een waarde of recht
- **Specialisatieregel**: specificeert een algemene regel voor een deelgeval

Kies het taalpatroon uit `kaders-regels.md §Taalpatronen` passend bij het regeltype.

Na aanmaken: koppel het begrip aan de regel via het juiste veld:
- Begrip met `jas-klasse: afleidingsregel` → zet `afleidingsregel-id: [regel-id]`
- Begrip met andere jas-klasse én `herkomst: afgeleid` → zet `uitvoer-van-regel-id: [regel-id]`

**Tussenresultaat:** zet `tussenresultaat: true` als het begrip uitsluitend als invoer voor een andere regel dient. In dat geval: `rechtsfeit-id: null` en noteer in `toelichting` welke hoofdregel dit tussenresultaat aanroept.

---

## Bijwerken begrip-YAML

Werk na het opstellen van definitie en relaties de begrip-YAML bij:

```yaml
# Velden die /begrip invult (bestaande velden overschrijven):
soort: [kies uit 8 typen]
soort-id: false           # true als identificatiebegrip
herkomst: direct          # of afgeleid
definitie:
  kern: "[definitietekst zonder punt aan het einde]"
  contexten: []           # of array van {markering-id, bijdrage, tekst, toelichting?}
definitie-versie: 1       # verhoog bij kernwijziging
definitie-gebaseerd-op:   # markering-id's die uitsluitend de KERN staven
- m-001
aliases:
- "[bekend juridisch synoniem]"
identificatiebegrip: false # true als unieke sleutel
afleidingsregel-id: null        # alleen invullen bij jas-klasse: afleidingsregel
uitvoer-van-regel-id: null      # invullen bij herkomst: afgeleid + jas-klasse ≠ afleidingsregel
tussenresultaat: false
vervangen-door: null            # niet aanraken — wordt ingesteld via A4 bij deprecatie
relaties:
  is-een: [...]
  heeft: [...]
  leidt-tot: [...]
```

**Voorbeeld met contextlaag:**
```yaml
definitie:
  kern: >-
    De juridische toestand waarin een belastingaanslag verkeert zodra de wettelijke
    betalingstermijn is verstreken
  contexten:
    - markering-id: m-002
      bijdrage: verfijning
      tekst: >-
        In de context van lid 5 treedt invorderbaarheid telkens per termijn in —
        niet eenmalig, maar op N achtereenvolgende data
      toelichting: Lid 5 is een lex-specialis ten opzichte van lid 1
definitie-versie: 2
definitie-gebaseerd-op:
- m-001
```

Wijzig **niet**: `begrip-id`, `begripsnaam`, `jas-klasse`, `toelichting-klasse`, `markeringen`, `geldigheid-van`, `geldigheid-tot`, `status`, `vervangen-door`.

> **markeringen-velden**: `bevestigd: false` (default bij aanmaken — wordt ingesteld op `true` zodra een domeinexpert de markering juridisch heeft gevalideerd); `bevestigd-op` bevat de validatiedatum (ISO-8601). Beide velden worden **niet** door de AI gevuld — ze zijn A4-input.

> **markeringen-velden**: `bevestigd: false` (default bij aanmaken — wordt ingesteld op `true` zodra een domeinexpert de markering juridisch heeft gevalideerd); `bevestigd-op` bevat de validatiedatum (ISO-8601). Beide velden worden **niet** door de AI gevuld — ze zijn A4-input.

`status` na invullen: laat op `concept` staan — status-wijziging is een A4-taak.

---

## Validatie en views (na elk schrijfcommando)

Na het bijwerken van de begrip-YAML:

```
cd "$CLAUDE_PROJECT_DIR" && tools/.venv/bin/python tools/validate_note.py --file begrippen/[slug].yaml
```

Bij blokkerende fouten (L1/L2): herstel en hervalideer vóór je verdergaat.

Bij aanmaken van een regel-YAML: valideer ook de regel:
```
cd "$CLAUDE_PROJECT_DIR" && tools/.venv/bin/python tools/validate_note.py --file regels/AR-[...].yaml
```

---

## Kwaliteitseisen (niet-onderhandelbaar)

- Definitie uitsluitend gebaseerd op `markeringen[].tekst` — nooit rechtstreeks uit de wetstekst of eigen kennis.
- Definitie is substitueerbaar: test altijd of de definitietekst het begrip kan vervangen.
- Definitie bevat geen punt aan het einde.
- Voorbeelden bevatten altijd minimaal één grensgeval, elk met toelichting.
- Bij JAS-klasse Afleidingsregel: regel-YAML in `regels/` is verplicht.
- Regel-YAML's bevatten altijd voorbeeldreeksen: minimaal 1 positief + 1 negatief of grenswaarde voorbeeld.
- `geldigheid-van` altijd gelijk aan de `versiedatum` uit de annotatie (`peildatum`-veld in de markering).

### Verplichte checklist-output na elk begrip

```
Kennismodel-checklist — [begripsnaam]
✅/⬜ soort ingevuld
✅/⬜ herkomst ingevuld
✅/⬜ definitie.kern ingevuld (substitueerbaar, geen punt)
✅/⬜ definitie.contexten[] ingevuld (of expliciet leeg — lege array is correct)
✅/⬜ definitie-gebaseerd-op bevat uitsluitend kern-markeringen
✅/⬜ verrijkingsprotocol doorlopen (bij meerdere markeringen)
✅/⬜ relaties ingevuld (of expliciet leeg)
✅/⬜ soort-id ingevuld
✅/⬜ identificatiebegrip ingevuld
✅/⬜ aliases aanwezig (leeg is toegestaan indien geen synoniemen)
✅/⬜ voorbeelden + kenmerken ingevuld in begrip-YAML (optioneel)
✅/⬜ afleidingsregel-id ingevuld (alleen bij jas-klasse: afleidingsregel)
✅/⬜ uitvoer-van-regel-id ingevuld (bij herkomst: afgeleid + jas-klasse ≠ afleidingsregel)
✅/⬜ enrichment-queue gecheckt
✅/⬜ validatie geslaagd (validate_note.py)
```

Bij `/begrip-alles`: print de checklist per begrip afzonderlijk, direct nadat dat begrip is opgeslagen.
