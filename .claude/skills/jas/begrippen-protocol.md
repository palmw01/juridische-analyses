# Begrippen-protocol — inline gebruik vanuit JAS

> Dit protocol wordt uitgevoerd vanuit **Stap 4** van het JAS-annotatieprotocol.
> Het is **geen zelfstandige skill** — geen git-commit, geen push.
> De zelfstandige `/begrip`-skill staat in `begrip/SKILL.md`.

---

## Doel

Controleer voor elke relevante term in de annotatie of een begrip-noot bestaat in `begrippen/`. Maak of actualiseer de noot zo nodig. Retourneer het bestandspad voor gebruik in §3 van het rapport.

---

## Uitvoering (per term, één voor één)

### Stap A — Term identificeren

Bepaal welke termen in `leden[].tekst` van artikel `[A]` juridisch relevant zijn: rechtssubjecten, rechtsobjecten, gedefinieerde begrippen uit het begripsbepalings-artikel. Sla triviale werkwoorden en voorzetsels over.

### Stap B — Slug bepalen

`[TERM-slug]` = term in lowercase, spaties → `-`, speciale tekens verwijderd.  
Bestandspad: `begrippen/[TERM-slug].md`

### Stap C — Bestaande noot controleren

Roep de Read-tool aan op `begrippen/[TERM-slug].md`.

**Als het bestand bestaat:**
- Vergelijk `definitie` en `vindplaats` met de beschikbare wetstekst uit Stap 4.
- Als niets veranderd is: noteer het pad en ga door naar de volgende term.
- Als actualisering nodig is (nieuwe vindplaats, betere definitie): ga naar Stap E.

**Als het bestand niet bestaat:** ga naar Stap D.

### Stap D — Definitie ophalen

De begripsbepalingen zijn al beschikbaar uit Stap 4 (`[brondefinities]`). Zoek daarin de omschrijving van de term.

Als de term niet in het begripsbepalings-artikel staat: roep aan:
`wettenbank_zoekterm(bwbId=[B], zoekterm="[TERM]")`  
Gebruik het eerste relevante resultaat als vindplaats.

Noteer:
- `[DEFINITIE]`: letterlijk geciteerde definitie
- `[VINDPLAATS]`: artikelnummer + lid + wet (bijv. "Art. 3 lid 1 IW 1990")
- `[JAS-ELEMENT]`: primair JAS-element (Rechtssubject / Rechtsobject / Brondefinitie / etc.)

### Stap E — Begrip-noot opslaan

Sla op als `begrippen/[TERM-slug].md`. Datum via `date +%Y-%m-%d`. Gebruik de template uit `.claude/skills/begrip/template.md`.

### Stap F — Retourneer pad

Noteer `begrippen/[TERM-slug].md` voor gebruik in §3 van het rapport.

---

## Na verwerking van alle termen

Sla alle begrip-paden op als `[begrip-noten]`. Gebruik deze in de `[brondefinities]`-verwerking van Stap 10 (§3).

> **Geen commit.** De begrip-noten worden opgeslagen maar niet gecommit in dit protocol. De commit voor begrip-noten valt buiten de JAS-workflow.
