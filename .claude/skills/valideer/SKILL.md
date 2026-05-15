---
description: "Voert Activiteit 4b uit van de Wetsanalyse-methode: opstellen van voorbeeldreeksen voor een afleidingsregel. Gebruik: /valideer AR-[bwb-id]-art[nr]-lid[l]-[seq]"
context: fork
agent: general-purpose
---

# /valideer — Activiteit 4b: Opstellen van voorbeeldreeksen

**Lees vóór elke run eerst `.claude/skills/valideer/kaders.md` volledig in.** De testgevallenpatronen en typeafleiding in dat bestand zijn bindend.

Voert Activiteit 4b uit: genereert een gestructureerde testmatrix (voorbeeldreeks) voor een bestaande afleidingsregel. Output is één YAML-bestand in `validaties/`.

**Scope:** de skill vult de structuur en invoerwaarden in, en de verwachte uitvoer waar algoritmisch bepaalbaar. De juridische beoordeling (`is-voorspelling-juist: ja/nee`) blijft bij de gebruiker — de skill zet dit op `?`.

---

## Triggerpatroon

```
/valideer AR-[bwb-id]-art[nr]-lid[l]-[seq]
```

Voorbeeld: `/valideer AR-BWBR0004770-art9-lid1-a`

---

## Uitvoerstappen

### Stap 1 — Existentiecontroles

1. Controleer of `regels/[argument].yaml` bestaat.
   - Niet gevonden → stop met foutmelding: `Regel niet gevonden: regels/[argument].yaml`
2. Bepaal het VR-id: vervang `AR-` door `VR-` in het argument.
3. Controleer of `validaties/VR-[id].yaml` al bestaat.
   - Al aanwezig → stop met: `Voorbeeldreeks bestaat al: validaties/VR-[id].yaml — verwijder het bestand als je het opnieuw wil genereren.`

### Stap 2 — Regel en begrippen lezen

4. Lees `regels/[argument].yaml`. Extraheer:
   - `soort` (Beslissingsregel/Rekenregel/Beperkingsregel/Specialisatieregel)
   - `invoer` (lijst van begrip-ids)
   - `uitvoer` (lijst van begrip-ids)
   - `formele-regel` (voor algoritmische uitvoer)
   - `peildatum`
5. Lees voor elk begrip-id in `invoer` en `uitvoer` het bijbehorende begrip-YAML uit `begrippen/`.
   - Zoek op slug: converteer begrip-id-pad naar slug via de bestandsnamen in `begrippen/`.
   - Extraheer `soort` en `jas-klasse` per begrip (voor typeafleiding, zie kaders.md §Typeafleiding).

### Stap 3 — Kolommen genereren

6. Kies het testgevallenpatroon op basis van `soort` (zie kaders.md §Testgevallenpatronen).
7. Genereer minimaal 3 kolommen. Voor elke kolom:
   - Stel `label` in (beschrijvend, bijv. "Happy path — invorderbaar").
   - Vul `invoer` in als map `{ begrip-id: waarde }` voor alle invoer-begrippen.
   - Stel `is-invoer-juist` in (`ja` of `nee`).
   - Vul `verwachte-uitvoer` in als map `{ begrip-id: waarde }` voor alle uitvoer-begrippen.
     - Algoritmisch bepaalbaar: gebruik concrete waarde (zie kaders.md §Algoritmisch bepaalbare uitvoer).
     - Niet bepaalbaar: gebruik de meest plausibele waarde.
   - Stel `is-voorspelling-juist` in:
     - `nvt` als `is-invoer-juist: nee`
     - `?` in alle andere gevallen
   - Voeg `toelichting` toe waar nodig (grensgeval, motivatie ongeldige invoer).

### Stap 4 — Schrijven en valideren

8. Stel het YAML-bestand op met de volgende metadata:
   ```yaml
   voorbeeldreeks-id: VR-[id-deel]
   afleidingsregel-id: [volledig AR-id]
   naam: [regel-naam] — voorbeeldreeks
   status: concept
   peildatum: [peildatum uit regel]
   aangemaakt-op: [datum van vandaag, ISO-formaat]
   kolommen:
     - ...
   ```
9. Schrijf het bestand naar `validaties/VR-[id].yaml`.
10. Valideer: `tools/.venv/bin/python tools/validate_note.py --file validaties/VR-[id].yaml --schema voorbeeldreeks`
    - L1-fouten (schema): herstel direct.
    - L2-fouten (integriteit): herstel direct.
    - L3-waarschuwingen: rapporteer aan de gebruiker.

### Stap 5 — Rapportage

11. Rapporteer beknopt:
    - Pad van het aangemaakte bestand
    - Aantal kolommen en hun labels
    - Welke `is-voorspelling-juist`-velden nog `?` zijn (= vereisen gebruikersbeoordeling)
    - Eventuele L3-waarschuwingen

---

## Na de skill

De gebruiker vult de `?`-waarden in `is-voorspelling-juist` in na juridische beoordeling. Zet daarna `status: gereviseerd` en na teamvalidatie `status: gevalideerd`.
