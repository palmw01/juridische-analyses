# Begrippen-check — inline gebruik vanuit JAS

> Dit protocol wordt uitgevoerd vanuit **Deelactiviteit 3a** van `/jas`.
> Input: de geclassificeerde wetsformuleringen (output Hoofdactiviteit 2).
> Het is **geen zelfstandige skill** — geen git-commit, geen push.
> De zelfstandige `/begrip`-skill staat in `begrip/SKILL.md`.

---

## Doel

Per geclassificeerde wetsformulering uit de annotatietabel: maak of actualiseer de begrip-noot in `begrippen/`, voeg de wiki-link in de Begrip-kolom van de annotatietabel in, en retourneer alle bestandspaden voor de publicatiestap.

---

## Uitvoering (per formulering, één voor één)

### Stap A — Begripsnaam bepalen

Bepaal de begripsnaam op basis van de formulering en de JAS-klasse. Gebruik de kern-term van de formulering (bijv. bij "de ontvanger" → "ontvanger"; bij "het aanslagbiljet" → "aanslagbiljet"). Sla triviale werkwoorden en voorzetsels over.

`[TERM-slug]` = begripsnaam in lowercase, spaties → `-`, speciale tekens verwijderd.  
Bestandspad: `begrippen/[TERM-slug].md`

### Stap B — Bestaande noot controleren

Roep de Read-tool aan op `begrippen/[TERM-slug].md`.

**Als het bestand bestaat:**
- Lees `begripsnaam`, `definitie`, `vindplaatsen` en `annotaties`.
- Vergelijk met de huidige formulering + JAS-klasse.
- Voeg de wiki-link naar het nieuwe rapport toe aan de `annotaties:`-lijst.
- Verrijk `definitie`, `begripsvoorbeelden`, `kenmerken` of `relaties` als de nieuwe formulering nieuwe inzichten geeft.
- Ga naar Stap D (opslaan).

**Als het bestand niet bestaat:** ga naar Stap C.

### Stap C — Definitie ophalen

Zoek in `[brondefinities]` (beschikbaar uit de Voorbereiding/dataverwerving) naar de omschrijving van de term.

Als de term niet in de begripsbepalingen staat: roep aan:
`wettenbank_zoekterm(bwbId=[B], zoekterm="[TERM]")`  
Gebruik het eerste relevante resultaat als vindplaats.

Noteer:
- `[DEFINITIE]`: letterlijk geciteerde definitie
- `[VINDPLAATS]`: artikelnummer + lid + wet (bijv. "Art. 3 lid 1 IW 1990")
- `[JAS-KLASSE]`: primaire JAS-klasse van deze formulering

### Stap D — Begrip-noot opslaan

Haal datum op via `date +%Y-%m-%d`. Sla op als `begrippen/[TERM-slug].md` conform de template in `begrip/template.md`.

Bij een **bestaande noot**: overschrijf het bestand met de bijgewerkte inhoud (bijgewerkte `annotaties:`-lijst + eventuele verrijking). Werk `datum-bijgewerkt` bij.

Bij een **nieuwe noot**: maak aan met `datum-aangemaakt` en `datum-bijgewerkt` gelijk aan vandaag.

### Stap E — Begrip-kolom invullen

Vul de `[[begrippen/[TERM-slug]]]`-wiki-link in de Begrip-kolom van de betreffende annotatierij in.

Noteer `begrippen/[TERM-slug].md` in de `[begrip-noten]`-lijst.

---

## Na verwerking van alle formuleringen

De `[begrip-noten]`-lijst bevat alle bijgewerkte of nieuw aangemaakte begrip-nootpaden. Geef deze door aan `publicatie/SKILL.md` voor de git-commit.

> **Geen commit in dit protocol.** Begrip-noten worden meegenomen in de commit van `publicatie/SKILL.md`.
