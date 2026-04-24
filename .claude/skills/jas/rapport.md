# JAS-annotatie — Rapportformat

Het rapport bevat uitsluitend metadata, wetstekst en de annotatie (Hoofdactiviteit 2). Begrippen, afleidingsregels, toepassingsscenario's en kruisreferenties leven in begrip-noten buiten het rapport.

---

## Frontmatter (YAML)

```yaml
---
type: jas-annotatie
artikel: [volledige artikelreferentie, bijv. "Art. 25 IW 1990"]
wet: [volledige wetnaam (BWB-id)]
datum: [YYYY-MM-DD]
timestamp: [YYYY-MM-DD_HH-MM-SS]
peildatum: [peildatum uit MCP]
analist: Belastingdienst — Domein Inning
jas-versie: 1.0.10
tags:
  - jas-annotatie
  - [wet-afkorting-lowercase]
  - art[nummer]
aliases:
  - "[Art. [A] [wet-afkorting] ([datum])]"
kruisreferenties: []
---
```

**Invulregels:**
- **tags[1]:** IW 1990 → `iw1990`; AWR → `awr`; Awb → `awb`; UB IW 1990 → `ubiw1990`
- **tags[2]:** artikelnummer zonder spaties; `.` en `:` → `-`: art. 9 → `art9`; art. 4:86 → `art4-86`
- **kruisreferenties:** `[kruisrefs]`-array uit de dataverwerving; lege array bij geen

---

## Rapportheader

```
# JAS-annotatie: [Volledige artikelreferentie]

**Analysedatum:** [DATUM]
**Peildatum wetstekst:** [PD] ([wet])
**Analist:** Belastingdienst — Domein Inning
**JAS-versie:** 1.0.10
```

---

## §1 Wetstekst (letterlijk, geldig per [PD])

Citeer de volledige, letterlijke tekst van artikel `[A]`. Elk lid op een nieuwe regel met vetgedrukt lidnummer (`> **1** ...`). Geen parafrase, geen samenvatting.

---

## §2 Zichtbaar maken van de juridische structuur

### §2.1 Structuurpositie

Vermeld de structuurpositie van het artikel, **letterlijk overgenomen uit het `pad`-veld van de MCP-response**:

> **Structuurpositie:** Hoofdstuk X > Afdeling Y > Artikel Z

Nooit een hoofdstuk- of afdelingstitel aannemen op basis van de artikelinhoud.

### §2.2 Markeringen en klassen per lid

Schrijf boven de tabel exact deze leeswijzer:

> **Leeswijzer toelichting-kolom:** Vermeldt (1) toegepaste interpretatiemethode, (2) reden voor JAS-klasse boven alternatieven, (3) meerduidigheid of alternatieve classificatie.

Maak per lid een subsectie. Nummer annotaties doorlopend over alle leden.

```
#### Lid 1 — [korte omschrijving van dit lid]

| Nr | Formulering (letterlijk geciteerd) | JAS-element | Toelichting | Begrip |
|----|-----------------------------------|-------------|-------------|--------|
| 1  | "[citaat]" | **[JAS-klasse]** | [methode + motivering] | [[begrippen/[term]]] |
| 2  | "[citaat]" | **[JAS-klasse]** | [methode + motivering] | [[begrippen/[term]]] |

#### Lid 2 — [korte omschrijving]

| Nr | Formulering (letterlijk geciteerd) | JAS-element | Toelichting | Begrip |
|----|-----------------------------------|-------------|-------------|--------|
| [doorlopend] | "[citaat]" | **[JAS-klasse]** | [toelichting] | [[begrippen/[term]]] |
```

Na het laatste lid: voeg toe:

```
#### Delegatiestructuur

| Delegatiebevoegdheid | Vindplaats | Type | Delegatie-invulling | Vindplaats invulling |
|---------------------|------------|------|---------------------|---------------------|
| [omschrijving] | Art. [A] lid Y | Verplicht / Facultatief | [naam regeling] | Art. Z [regeling] |
```

Bij geen delegatie: schrijf exact "Geen delegatiebevoegdheden in artikel [A]."

### §2.3 Juridisch structuurdiagram

Structuurpositie (letterlijk uit `pad`-veld) gevolgd door de interne relatiestructuur:

```
Structuurpositie: [pad]

Art. [A] [W]
├── Lid 1: [omschrijving — hoofdregel / uitzondering / etc.]
│   └── [nadere invulling]
└── Lid N: [omschrijving]
```

Bij één lid: "Artikel [A] heeft één lid; geen interne structuurverhouding."

---

## Bijlage — Geraadpleegde bronnen

| Bron | BWB-id | Peildatum (uit MCP) | JCI-uri (uit MCP) |
|------|--------|---------------------|-------------------|
| [Wetnaam [W]] | [B] | [PD] | [jci1.3:c:[B]&artikel=[A]] |
| [Eventuele externe wetten uit kruisreferenties] | [BWB-id] | [peildatum] | [jci1.3:c:...&artikel=X] |
| kaders.md | — | [DATUM] | — |

---

## Kwaliteitseisen (niet-onderhandelbaar)

- **Nooit parafraseren.** Wetstekst altijd letterlijk en volledig citeren in §1 en §2.2.
- **Wetstekst lezen voor elke claim.** Snippets zijn nooit voldoende grondslag.
- **Meest specifieke JAS-klasse.** Tijdsaanduiding boven variabele; plaatsaanduiding boven parameter.
- **Alle 13 JAS-elementen intern afgevinkt** (interne stap, niet in output).
- **Kruisreferenties alleen uit de tekst.** Uitsluitend letterlijk staande verwijzingen.
- **Delegatieketens volledig.** Wet → amvb → ministeriële regeling; alle schakels ophalen.
- **Interpretatiemethode per element.** Grammaticaal / systematisch / teleologisch in elke Toelichting-cel.
- **Begrip-kolom ingevuld.** Elke annotatierij heeft een `[[begrippen/[term]]]`-wiki-link.
- **Peildatum uit MCP.** Nooit de datum van vandaag gebruiken.
- **Altijd opslaan.** Rapport als MD-bestand in `analyses/` conform bestandsnaamschema.
- **Hub-note verplicht.** Vóór commit: controleer of hub-note bestaat.
