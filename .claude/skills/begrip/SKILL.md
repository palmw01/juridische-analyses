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

## Definitie opstellen (A3a)

- Sluit zo nauw mogelijk aan bij de **letterlijke tekst** in `markeringen[0].tekst` (de primaire markering).
- Benoem interpretatie- en preciseringskeuzes expliciet.
- Onderbouw **altijd** de klassekeuze — ook als die overeenkomt met de letterlijke formulering.
- Geen parafrase van de wetstekst — gebruik de markering als startpunt.
- Definitie bevat **geen punt** aan het einde.
- Test altijd of de definitietekst het begrip kan vervangen in een zin zonder betekenisverlies (substitutietest).

**Bij meerdere markeringen (multi-annotatie):** de definitie is een synthese van alle markeringen. De primaire markering (`bijdrage: primair`) is leidend; aanvullende (`aanvullend`) en context-markeringen (`context`) verfijnen de definitie.

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

## Extra-bestand: voorbeelden en kenmerken

Schrijf voorbeelden en kenmerken naar `begrippen/[slug].extra.json`:
```json
{
  "begrip-id": "[B]/art[A]/lid[L]/[slug]",
  "voorbeelden": [
    { "stelling": "[concrete stelling]", "waar": true, "toelichting": "[waarom?]" },
    { "stelling": "[grensgeval]", "waar": false, "toelichting": "[waarom niet?]" }
  ],
  "kenmerken": [
    "[eigenschap 1]",
    "[eigenschap 2]"
  ]
}
```

- Minimaal **2 stellingen** (waar/niet-waar) die de grenzen van het begrip toetsen.
- Minimaal **1 grensgeval**.
- Alle stellingen zijn concreet en toetsbaar.

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

Na aanmaken: zet `afleidingsregel-id` in de begrip-YAML op de nieuwe `regel-id`.

**Tussenresultaat:** zet `tussenresultaat: true` als het begrip uitsluitend als invoer voor een andere regel dient. In dat geval: `rechtsfeit-id: null` en noteer in `toelichting` welke hoofdregel dit tussenresultaat aanroept.

---

## Bijwerken begrip-YAML

Werk na het opstellen van definitie en relaties de begrip-YAML bij:

```yaml
# Velden die /begrip invult (bestaande velden overschrijven):
soort: [kies uit 8 typen]
soort-id: false           # true als identificatiebegrip
herkomst: direct          # of afgeleid
definitie: "[definitietekst zonder punt aan het einde]"
definitie-versie: 1       # verhoog bij herziening
definitie-gebaseerd-op:   # lijst van markering-id's die de definitie staven
- m-001
aliases:
- "[bekend juridisch synoniem]"
identificatiebegrip: false # true als unieke sleutel
afleidingsregel-id: null   # of regel-id als herkomst: afgeleid
tussenresultaat: false
relaties:
  is-een: [...]
  heeft: [...]
  leidt-tot: [...]
```

Wijzig **niet**: `begrip-id`, `begripsnaam`, `jas-klasse`, `toelichting-klasse`, `markeringen`, `geldigheid-van`, `geldigheid-tot`, `status`.

`status` na invullen: laat op `concept` staan — status-wijziging is een A4-taak.

---

## Validatie en views (na elk schrijfcommando)

Na het bijwerken van de begrip-YAML:

```
cd "$CLAUDE_PROJECT_DIR" && tools/.venv/bin/python tools/validate_note.py --file begrippen/[slug].yaml
```

Bij blokkerende fouten (L1/L2): herstel en hervalideer vóór je verdergaat.

Daarna views genereren:
```
cd "$CLAUDE_PROJECT_DIR" && tools/.venv/bin/python tools/generate_views.py --type begrip --file begrippen/[slug].yaml
```

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
✅/⬜ definitie ingevuld (substitueerbaar, geen punt)
✅/⬜ relaties ingevuld (of expliciet leeg)
✅/⬜ soort-id ingevuld
✅/⬜ identificatiebegrip ingevuld
✅/⬜ aliases aanwezig (leeg is toegestaan indien geen synoniemen)
✅/⬜ extra-JSON aangemaakt met voorbeelden + kenmerken
✅/⬜ wiki-link afleidingsregel (n.v.t. indien herkomst: direct)
✅/⬜ enrichment-queue gecheckt
✅/⬜ validatie geslaagd (validate_note.py)
✅/⬜ views gegenereerd (generate_views.py)
```

Bij `/begrip-alles`: print de checklist per begrip afzonderlijk, direct nadat dat begrip is opgeslagen.
