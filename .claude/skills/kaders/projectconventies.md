# Projectconventies — projectspecifieke uitwerkingen op de canon

> **Bron:** projectconventie. De Handleiding Wetsanalyse en Leidraad Wetsanalyse beschrijven de items hieronder niet (letterlijk); ze zijn projectoperationalisaties die nodig zijn voor de toolchain. Elke conventie verwijst naar de dichtstbijzijnde canon-paragraaf voor herleidbaarheid. Wijzigingen aan deze conventies vereisen een PR met motivatie.
> **Gebruikt door:** alle skills via verwijzing in de kader-bestanden.

---

## Werking

Een **projectconventie** is een keuze die expliciet aanvullend is op canon-tekst. Voorbeelden zijn: enum-waarden, vlag-velden, bestandsnaam-conventies, beslisbomen, sentinel-tekens. Ze worden in de relevante kader-bestanden inline gemarkeerd met "— projectconventie" en hier centraal verzameld voor overzicht en motivering.

| # | Conventie | Canon-anker | Rationale |
|---|-----------|-------------|-----------|
| 1 | Definitie uitsluitend uit `markeringen[].tekst` — nooit rechtstreeks uit wetstekst (`/begrip` raadpleegt wettenbank niet). | HW §3.5.2a | Traceerbaarheid: elke definitie heeft een markering die de classificatie staaft; rechtstreekse wetslezing zou de schakel A2 ↔ A3 doorbreken. |
| 2 | `soort`-enum voor begrippen (8 waarden: monetair-bedrag, percentage, tijdsduur, datum, booleaans, tekst, enumeratie, entiteit). | HW §3.5.2a (datatypering) | Canon noemt datatypes niet limitatief; de 8 waarden dekken de IW 1990/AWR-praktijk en zijn afgesproken in `schemas/begrip.schema.json`. |
| 3 | `herkomst`-enum (direct/afgeleid). | HW §3.5.2a | Canon onderscheidt observatie vs. afleiding; de twee enum-waarden zijn projectkeuze. |
| 4 | `status`-enum voor begrippen: `concept` → `ter-review` → `gevalideerd`, plus `vervallen`/`te-verrijken`. Voor voorbeeldreeksen: `concept` → `gereviseerd` → `gevalideerd`. Voor scenario's: `concept` → `gevalideerd`. | HW (statusmodel niet beschreven) | Toolchain-keuze; status sturen pre-commit en webapp-dashboard. |
| 5 | `soort-id` + `identificatiebegrip` als gekoppelde boolean-paren met identieke waarde. | HW §3.5.2a (geen) | Backwards-compat: `soort-id` is de oudere naam; `identificatiebegrip` is canoniek vanaf 2025. Het schema dwingt gelijkheid niet af; validate_note.py (L2) wel. |
| 6 | `tussenresultaat`-vlag (boolean) op begrip én regel. | HW p. 6-7 (impliciete algoritmen, geen vlag) | Maakt scheiding tussen eindresultaat-regels en intermediaire regels expliciet voor RDF-export en webapp-rendering. |
| 7 | `voorbeelden`-minItems 2 met minimaal 1 grensgeval per begrip. | HW §3.5.2a (geen aantal) | Praktijkminimum: één illustratief geval + één grensgeval dwingt afbakening af. |
| 8 | Verrijkingsprotocol: beslisboom voor `bijdrage` (primair / context / verfijning / uitbreiding / uitzondering) bij toevoegen van een markering aan een bestaand begrip. | HW §3.5.2a (kern + contexten) | Operationaliseert het canon-concept "contextuele aanvullingen" als reproduceerbare beslisroute. |
| 9 | Operator-hergebruik: bij `jas-klasse: operator` eerst zoeken naar bestaande begrippen voor hergebruik via `context`-markering. | JAS v1.0.10 (operator-element) | Voorkomt explosie van bijna-identieke operator-begrippen (`vermeerderd-met`, `verminderd-met`); behoudt RDF-graaf overzichtelijk. |
| 10 | Pariteit bij `tenzij`-constructies: hoofdzin + tenzij = altijd twee regels (hoofdregel + Specialisatieregel). | HW §3.5.2b (Specialisatieregel) | Maakt beide normatieve uitkomsten expliciet; canon laat impliciet. |
| 11 | Reeks-statustoets: bij geordende reeksen (vervaldatums, termijnbedragen) is een aanvullende beslissingsregel `bepalen status [element] op peildatum` vrijwel altijd nodig. | HW §3.6 (afleidingsregels) | Project-uitwerking voor invorderingstijdlijnen (IW 1990 art. 9, 28). Canon noemt dit patroon niet. |
| 12 | RegelSpraak-correspondentie: vertaaltabel taalpatronen → ALEF (`Geldig als`, `is gelijk aan`, `maximaal`/`minimaal`). | HW §3.6 (geen RegelSpraak-vertaling) | Hulpmiddel voor regelanalisten; niet vereist door canon. |
| 13 | LI-signaleringsregels: bij `signalering` met `"voorbeeld"`/`"illustratief"` géén generalisatie binnen de LI-annotatie. | HW (geen LI-specifiek beleid) | Project-specifiek voor IW 1990-annotaties; Leidraad Invordering 2008 is secundaire bron, niet primaire. |
| 14 | Bestandsnaamgeving begrippen: `begrippen/{slug}.yaml` zonder wet-suffix. | HW §3.5.2a (geen) | Begrip kan meerdere bronartikelen hebben; wet-suffix zou kunstmatig zijn. |
| 15 | Scenario-specifieke valkuil: vermijd maandnamen/jaartallen in begripsnamen. | HW §3.5.2a (vuistregels begripsnaam) | L3-controle in `validate_note.py`; gebruikt om "test-data-leaks" te detecteren. |
| 16 | Kleurcodering diagram-knopen (Mermaid classDef per JAS-klasse). | JAS v1.0.10 (geen vaste kleuren) | Visualisatie-keuze in `sitegen/mermaid.py`; canon laat vrij. |
| 17 | Knooplabel-formaat `[JAS-klasse]<br/>'[markering ingekort tot 40 tekens]'`. | HW §3.4.2c (diagram, geen labelregel) | Projectspecifiek voor leesbaarheid; gehandhaafd door `annoteer-diagram`. |
| 18 | Kruisreferenties-JSON-model (`{doel-bwb-id, doel-artikel, richting, confidence, ruwe-tekst}`). | JCI URI-standaard | Projectspecifieke normalisatie van JCI; canon gebruikt vrije tekst. |
| 19 | `?`-sentinel in `is-voorspelling-juist` om "juridisch oordeel nodig" te markeren. | HW §3.6.2b (geen sentinel) | Maakt onderscheid tussen geautomatiseerde gok en menselijke beoordeling expliciet; pre-push/CI-gates gebruiken dit. |
| 20 | `bronnen-secundair[]`-array per begrip én regel; soort-enum (leidraad/beleidsregel/MvT/jurisprudentie/kamerstukken/ander). | HW §3.5.4 (jurisprudentie als interpretatiebron) | Onderscheidt primaire wetstekst-anker van interpretatieve bronnen; canon onderscheidt deze, projectschema geeft enum. |
| 21 | `scenario-refs[]`-array met (scenario-id, rol)-paren; rol-enum (rechtssubject/rechtsobject/voorwaarde/uitvoer/context). | HW §3.3 (scenario's) + LW §2.4 | Koppeling A1 ↔ A3; rol-enum is project-uitwerking. |
| 22 | "Bestaansregel" (synoniem dat sporadisch in vooronderzoek opdook) is **niet** in canon — gebruik altijd **Beperkingsregel**. | HW §3.5.2b | Terminologie-stabilisatie. |
| 23 | "Drempelregel" (projectjargon) is **niet** in canon — gebruik **Beperkingsregel** of beschrijf de grenscontrole expliciet. | HW §3.5.2b | Terminologie-stabilisatie; kop in `voorbeeldreeks.md §Algoritmisch bepaalbaar` is hernoemd. |

---

## Procedure

Toevoegen of wijzigen van een projectconventie:

1. Markeer de uitspraak in het relevante kader-bestand inline met "— projectconventie" en voeg een korte rationale toe.
2. Voeg een rij toe aan de tabel hierboven met canon-anker (dichtstbijzijnde HW/LW-paragraaf, of "(geen)").
3. Werk `canon-ankers.md` bij waar relevant.
4. Bij schema-wijziging: update `schemas/<x>.schema.json` en de relevante stubs in `tools/jas_index_lib.py`.
5. Run `make ci` en `make webapp`.
