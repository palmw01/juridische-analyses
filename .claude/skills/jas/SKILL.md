---
description: Voer een volledige JAS-annotatie (v1.0.10) uit op een wetsbepaling en sla het rapport op als MD-bestand. Gebruik: /jas art. 25 IW 1990 of /jas art. 36 lid 4 IW 1990
context: fork
agent: general-purpose
---

# /jas — Wetsanalyse Annotatie

**Artikel:** `$ARGUMENTS`

Uitvoeringsprotocol conform de **Wetsanalyse-methode** (Expertisecentrum BRM Belastingdienst, v1.0 2023). Hoofdactiviteiten 2 en 3.

---

## Voorbereiding — Startactiviteiten

### S1 — Bestaande annotatie controleren

Parseer `$ARGUMENTS` voor `[A]` (artikelnummer) en `[W]` (wet).

Controleer of er al een annotatie bestaat:
1. Lees `analyses/INDEX.md`.
2. Als niet gevonden: Glob `analyses/*-art[A]-*`.
3. Als gevonden: lees het rapport en meld aan de gebruiker: "Bestaande annotatie gevonden: [bestandsnaam]. Peildatum: [peildatum]. Gebruik je deze als basis of wil je een nieuwe annotatie opstellen?" **Wacht op bevestiging.**
4. Niet gevonden: ga door.

### S2 — Dataverwerving

Voer `$CLAUDE_SKILLS_DIR/wettenbank/SKILL.md` volledig uit met argument `[A] [W]`.

Resultaat beschikbaar als intern datamodel:
- `[A]`, `[W]`, `[B]`, `[L]`, `[BD]`, `[PD]`
- `wetstekst`: leden[]-array voor artikel `[A]`
- `structuurpositie`: pad-string
- `[brondefinities]`: begripsomschrijvingen uit `[BD]`
- `kruisrefs JSON-model`
- `[kruisrefs]`: array van `"Art. X W"`-strings
- `bronreferenties`: JCI-uri's

---

## Hoofdactiviteit 2 — Zichtbaar maken van de juridische structuur

Lees `$CLAUDE_SKILL_DIR/kaders.md` volledig vóór de annotatie. De kaders bevatten de JAS v1.0.10 taxonomie (13 elementen), definities, herkenningsvragen en taalkenmerken — dit is de enige autoriteit voor classificatiebeslissingen.

### Deelactiviteit 2a — Afbakenen van wetsformuleringen

Lees de letterlijke tekst van lid `[L]` woord voor woord. Maak een genummerde **extractielijst** van alle te classificeren zinsdelen en formuleringen — nog geen oordeel, alleen identificatie. Een formulering is elk afzonderlijk zinsdeel dat een juridisch element kan bevatten (werkwoord, substantief, bijwoordelijke bepaling, voegwoord met voorwaardelijke werking, etc.).

Noteer de extractielijst intern als `[extractielijst]`.

### Deelactiviteit 2b — Klasse toekennen

Loop de 13 JAS-elementen af per formulering: rechtssubject, rechtsobject, rechtsbetrekking, rechtsfeit, voorwaarde, afleidingsregel, variabele/variabelewaarde, parameter/parameterwaarde, operator, tijdsaanduiding, plaatsaanduiding/brondefinitie, delegatiebevoegdheid/delegatie-invulling.

**Annotatieprincipes:**
1. Citeer het exacte zinsdeel letterlijk.
2. Kies altijd de meest specifieke JAS-klasse: tijdsaanduiding > variabele; plaatsaanduiding > parameter.
3. Benoem per JAS-element de interpretatiemethode: grammaticaal / systematisch / teleologisch.
4. Markeer meerduidigheid of alternatieve classificaties expliciet.
5. Traceer delegatieketens volledig: wet → amvb → ministeriële regeling.

**Verificatie (interne stap):** vergelijk de annotatietabel met `[extractielijst]`. Is elk item terug te vinden als annotatierij? Zo niet: voeg toe. Noteer aanvullingen intern.

**Aanvullen Begrip-kolom (voorbereiding op Hoofdactiviteit 3):** laat de Begrip-kolom per rij open als `[[begrippen/[term]]]`-placeholder; wordt ingevuld in Deelactiviteit 3a.

**Delegatiestructuur:** na de annotatietabel: stel per delegatiebevoegdheid de volledige keten vast (wet → amvb → ministeriële regeling). Haal alle schakels op.

### Deelactiviteit 2c — Juridisch structuurdiagram opstellen

Gebruik de structuurpositie (uit `pad`-veld, letterlijk) als positiebepaling. Breng de interne relaties tussen de leden in kaart: welk lid is de hoofdregel, welke zijn uitzonderingen of nadere invullingen. Gebruik een boomstructuur met ├── en └── vertakkingen.

Bij één lid: schrijf "Artikel [A] heeft één lid; geen interne structuurverhouding."

**OUTPUT Hoofdactiviteit 2:** geclassificeerde wetsformuleringen (annotatietabel) → dit is de INPUT voor Hoofdactiviteit 3.

---

## Hoofdactiviteit 3 — Vaststellen van de betekenis van wetgeving

### Deelactiviteit 3a — Begrippen maken of verrijken

Lees `$CLAUDE_SKILLS_DIR/begrip/begrippen-check.md` volledig en voer het daarin beschreven protocol uit.

Input: elke geclassificeerde wetsformulering uit de annotatietabel (output Deelactiviteit 2b).

Per formulering:
- Bepaal de begripsnaam op basis van de formulering + JAS-klasse.
- Controleer `begrippen/[term].md`: bestaat het al?
  - **Bestaand begrip:** voeg de nieuwe annotatie toe aan de `annotaties:`-lijst; verrijk definitie, voorbeelden, kenmerken of relaties op basis van deze formulering.
  - **Nieuw begrip:** maak aan conform de template in `begrip/template.md`.
- Vul de `[[begrippen/[term]]]`-wiki-link in de Begrip-kolom van de annotatietabel in.

### Deelactiviteit 3b — Afleidingsregels vastleggen

Op basis van de als Afleidingsregel geclassificeerde formuleringen:

**Beslisregels:** stel per beslisregel de voorwaardenstructuur op (EN/OF/NIET), de uitvoervariabele en de vindplaats.

**Rekenregels:** stel per rekenregel de formule op met invoervariabelen, uitvoervariabele en vindplaats. Geef een cijfervoorbeeld als de rekenregel niet-triviaal is.

**Parameters:** noteer alle vaste waarden (tarieven, termijnen, percentages, drempelbedragen).

Leg deze vast in de relevante begrip-noten (als Kenmerken of in de Definitie-sectie).

### Deelactiviteit 3c — Toepassingsscenario's beschrijven

Beschrijf op basis van de annotatie:
- **Hoofdscenario:** standaard toepassing van het artikel (wie doet wat, wanneer, met welk rechtsgevolg).
- **Varianten:** relevante afwijkende situaties die uit de leden of delegatiestructuur volgen.

Leg deze vast als Begripsvoorbeelden in de relevante begrip-noten.

### Deelactiviteit 3d — Relateren aan juridische bronnen

Gebruik het kruisrefs JSON-model (uit de Voorbereiding):
- Interne verwijzingen (zelfde wet): voeg toe als Relaties in de relevante begrip-noten.
- Externe verwijzingen (andere wetten): voeg toe als Relaties.
- Omgekeerde kruisreferenties: voeg toe als context in begrip-noten waar relevant.

---

## Afsluiting — Publicatie

### Kwaliteitscheck vóór opslaan

Doorloop vóór publicatie:
- [ ] §1: wetstekst letterlijk geciteerd, peildatum uit MCP
- [ ] §2.1: structuurpositie letterlijk uit `pad`-veld — nooit afgeleid
- [ ] §2.2: alle 13 JAS-elementen beoordeeld per formulering; Begrip-kolom ingevuld
- [ ] §2.2: delegatieketens volledig (alle schakels opgehaald)
- [ ] §2.3: structuurdiagram aanwezig (of standaardmelding)
- [ ] Begrip-noten: elke geclassificeerde formulering heeft een begrip-noot
- [ ] Begrip-noten: `annotaties:`-lijst bijgewerkt met link naar dit rapport
- [ ] Bestandsnaam conform schema

Lees `$CLAUDE_SKILL_DIR/rapport.md` voor de rapportstructuur en kwaliteitseisen.

### Publicatie

Stel het rapport samen conform `$CLAUDE_SKILL_DIR/rapport.md`. Voer daarna `$CLAUDE_SKILLS_DIR/publicatie/SKILL.md` volledig uit.

Retourneer het bestandspad van het opgeslagen rapport.
