---
description: Documenteer of actualiseer een juridisch begrip in begrippen/. Gebruik: /begrip ontvanger IW 1990 of /begrip belastingschuldige
context: fork
agent: general-purpose
---

# /begrip — Begrip documenteren (Wetsanalyse Activiteit 3)

**Term:** `$ARGUMENTS`

Een begrip is het product van **Activiteit 3** van de Wetsanalyse-methode. De bron is uitsluitend de annotatietabel uit Activiteit 2 (de JAS-annotaties in `analyses/`). Raadpleeg **nooit** de wettenbank-tools — de definitie is de letterlijk geciteerde formulering uit de annotatie.

---

## Stap 1 — Argument parsen

Parseer `$ARGUMENTS`:
- **`[TERM]`**: de juridische term (bijv. "ontvanger", "belastingschuldige")
- **`[TERM-slug]`**: term in lowercase, spaties → `-`, speciale tekens verwijderd (bijv. "ministeriële regeling" → `ministeriële-regeling`)

Bestandspad: `begrippen/[TERM-slug].md`

---

## Stap 2 — Controleer bestaand begrip

Lees `begrippen/[TERM-slug].md`.

- **Bestand bestaat en is volledig ingevuld:** vergelijk met de annotaties. Als niets veranderd is: retourneer het bestandspad zonder aanpassing. Als actualisering nodig is: ga naar Stap 4.
- **Bestand bestaat niet of is leeg:** ga naar Stap 3.

---

## Stap 3 — Extraheer uit annotaties

Zoek in alle bestanden in `analyses/` naar rijen in de annotatietabel waar de Begrip-kolom `[[begrippen/[TERM-slug]]]` bevat.

**Methode:**
```
Grep: analyses/*.md naar "begrippen/[TERM-slug]"
```

Lees elk gevonden annotatiebestand. Extraheer per treffer:

**Uit de annotatie-frontmatter:**
- `[ANNOTATIE-BESTAND]`: bestandspad (bijv. `analyses/jas-annotatie-art25lid4-IW1990-2026-04-24_14-52-40.md`)
- `[ARTIKEL]`: waarde van het `artikel`-veld
- `[WET]`: waarde van het `wet`-veld

**Uit de annotatietabel (rijen waar Begrip-kolom de term bevat):**
- `[FORMULERING]`: de letterlijk geciteerde wetsformulering (tweede kolom)
- `[JAS-KLASSE]`: de JAS-klasse (derde kolom, bijv. Rechtssubject, Rechtsobject, Voorwaarde)
- `[TOELICHTING]`: de toelichting (vierde kolom)
- `[VINDPLAATS]`: het artikel en lid waarop de annotatie betrekking heeft (uit `artikel`-frontmatter)

**Als geen enkele annotatie de term in de Begrip-kolom heeft:**
Meld dit aan de gebruiker: "De term '[TERM]' is nog niet als begrip geclassificeerd in een annotatietabel. Maak eerst een annotatie (Activiteit 2) voordat je dit begrip documenteert."
Stop hier.

---

## Stap 4 — Stel de begripsdefinitie samen

Bepaal op basis van de gevonden formuleringen:

- **`[DEFINITIE]`**: de meest specifieke en volledige wetsformulering die de inhoud van het begrip beschrijft, letterlijk geciteerd. Bij meerdere vindplaatsen: kies de begripsbepaling (definitie-artikel) als primaire bron; noem overige vindplaatsen als contextuele verschijningen.
- **`[JAS-KLASSE]`**: de dominante JAS-klasse over alle vindplaatsen (bij wisselende klassen: kies de meest specifieke).
- **`[VINDPLAATSEN]`**: lijst van alle artikelen/leden waar het begrip voorkomt in de annotatietabellen.

---

## Stap 5 — Sla het begrip op

Gebruik de datum van vandaag (`date +%Y-%m-%d`). Sla op als `begrippen/[TERM-slug].md` met de template uit `.claude/skills/begrip/template.md`.

Vul in:
- `begripsnaam`: `[TERM]`
- `jas-klasse`: `[JAS-KLASSE]`
- `definitie`: letterlijk geciteerde `[DEFINITIE]`
- `annotaties`: lijst van alle `[ANNOTATIE-BESTAND]`-paden als Obsidian-links
- `vindplaatsen`: lijst van alle `[VINDPLAATSEN]`
- `tags`: `begrip` + slugified wet-afkorting (bijv. `iw1990`)
- `aliases`: `[TERM]` en indien relevant `[TERM] [WET-AFKORTING]`

Vul de Markdown-secties in:
- **Definitie**: de letterlijk geciteerde formulering met vindplaats
- **Begripsvoorbeelden**: 2-3 stellingen (waar/niet waar) die de grens van het begrip testen, afgeleid uit de annotatie-toelichting
- **Kenmerken**: eigenschappen die volgen uit de JAS-toelichting in de annotatie
- **Relaties**: koppelingen naar andere begrippen die in dezelfde annotatierijen voorkomen
- **Annotatiebronnen**: de Obsidian-links naar alle bronnotaties

---

## Stap 6 — Commit

```
git add begrippen/[TERM-slug].md
git commit -m "begrip: [TERM] ([WET-AFKORTING])"
git push
```

---

## Stap 7 — Retourneer bestandspad

Retourneer uitsluitend `begrippen/[TERM-slug].md`.
