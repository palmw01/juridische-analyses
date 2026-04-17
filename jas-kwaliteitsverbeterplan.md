# JAS — Kwaliteitsverbeterplan

**Versie:** 1.0  
**Datum:** 2026-04-17  
**Auteurs:** AI-specialist (Claude Sonnet 4.6) × Senior jurist — Belastingdienst, Domein Inning  
**Basis:** JAS v1.0.10 (kaders.md), analyses in `analyses/INDEX.md`, brainstormsessie 2026-04-17

---

## 1. Inleiding — waarom verbeteren?

De JAS-workflow levert nu reproduceerbaar structureel goede annotaties op. Art. 9 IW 1990 is inmiddels drie keer geannoteerd; elke versie was beter dan de vorige. Maar de kwaliteitsverbetering tussen versies is op dit moment *toevallig*: er is geen systematisch mechanisme dat de volgende annotatie beter maakt dan de vorige.

Dit plan beschrijft acht voorstellen die dat veranderen — van een workflow die goed werkt naar een workflow die *structureel beter wordt*.

Het plan is opgesteld vanuit twee complementaire invalshoeken:

- **De AI-specialist** kijkt naar het systeem: modelkeuze, promptarchitectuur, agentpatronen en evaluatie.
- **De senior jurist** kijkt naar de inhoud: juridische navolgbaarheid, consistentie van begrippen, volledigheid van de interpretatie en de rol van de vakexpert als uiteindelijke kwaliteitsborging.

Beide perspectieven zijn nodig. Een technisch superieure aanpak die juridisch irrelevante output produceert is waardeloos. Een inhoudelijk correct oordeel dat niet systematisch wordt geborgd is fragiel.

---

## 2. Twee perspectieven

### 2.1 AI-specialist

De huidige JAS-skill is een **lineaire, single-agent workflow**: één model voert veertien stappen sequentieel uit. Dat is efficiënt en begrijpelijk — maar het heeft een fundamenteel zwakke plek: het model heeft geen tegenwicht. Als het een grensgevalgeval systematisch verkeerd classificeert, herhaalt het die fout elke keer.

De sterkste kwaliteitsinterventies in AI-systemen zijn niet betere modellen, maar **betere architectuur**:

- Meerdere onafhankelijke agenten die elkaars blinde vlekken zichtbaar maken
- Expliciete evaluatiestappen die verifiëren wat de productiestap heeft gedaan
- Cumulatief leergeheugen dat fouten vastlegt als precedenten voor de volgende run
- Gestructureerde feedback van domeinexperts die in de promptarchitectuur terechtkomt

Het model zelf (Claude Sonnet 4.6 → Opus 4.6 met extended thinking) is een multiplier: het vergroot bestaande kwaliteit, maar vervangt architecturele zwaktes niet.

### 2.2 Senior jurist

Juridische kwaliteit heeft twee dimensies die in gespannen verhouding staan: **juistheid** en **navolgbaarheid**. Een annotatie kan inhoudelijk correct zijn maar onnavolgbaar zijn voor een collega-jurist of een rechter. Navolgbaarheid vereist dat elke classificatiekeuze expliciet is gemotiveerd, dat alternatieve interpretaties zijn overwogen en verworpen, en dat de gehanteerde interpretatiemethode transparant is.

De huidige JAS-kaders schrijven dit voor (grammaticale, systematische en teleologische interpretatie per element), maar de **bewaking** hiervan is zwak. Er is geen mechanisme dat controleert of de motivering in de toelichting-kolom inhoudelijk sterk genoeg is.

Drie juridische kwaliteitsproblemen spelen nu al:

1. **Grensgevallen worden niet vastgelegd.** Als een element tussen Voorwaarde en Rechtsfeit kan vallen, is de gemaakte keuze niet traceerbaar voor de volgende annotatie. De volgende keer kan het anders uitvallen.
2. **Consistentie over artikelen heen is niet bewaakt.** Art. 7 en Art. 9 gebruiken allebei "belastingschuldige". Als die term in beide annotaties anders is geclassificeerd, is dat een juridisch kwaliteitsgebrek.
3. **Er is geen gevalideerde referentie.** Welk niveau van annotatie is "goed genoeg"? Zolang dat niet door een vakexpert is vastgesteld, heeft kwaliteitsverbetering geen meetlat.

---

## 3. Acht verbetervoorstellen

---

### Voorstel 1 — Grensgevallen-bibliotheek

**Kern:** een apart bestand `grensgevallen.md` dat moeilijke classificatiebeslissingen vastlegt als precedenten, meegestuurd bij elke nieuwe annotatie als few-shot geheugen.

**AI-specialist:**  
Large language models leren niet tussen sessies. Elke annotatie begint opnieuw. De grensgevallen-bibliotheek lost dit op door moeilijke beslissingen *expliciet* in de prompt te zetten als geconditioneerde voorbeelden:

```
Eerder vastgesteld precedent:
  Formulering: "is invorderbaar overeenkomstig de bepalingen die gelden voor die belastingaanslag"
  Overwogen: Rechtsbetrekking (vestiging juridische status) vs. Afleidingsregel (beslisregel)
  Beslissing: Afleidingsregel — want het rechtsgevolg (termijn) wordt *afgeleid* van een andere bepaling, 
              niet zelfstandig gevestigd.
  Methode: systematisch (samenhang met de termijnbepalingen in lid 1 t/m 4)
```

Dit is geen fine-tuning en vereist geen modeltraining — het werkt puur via de prompt.

**Senior jurist:**  
Dit is analoog aan vaste uitlegregels in de rechtspraktijk: een uitleg die eenmaal expliciet is gemotiveerd, werkt door in latere interpretaties van hetzelfde begrip. Juristen noemen dit ook wel "interne systematiek". Door dit te formaliseren wordt de JAS-workflow juridisch coherenter over de tijd.

**Verwachte winst:**  
- Minder inconsistente classificaties bij vergelijkbare formuleringen
- Grensgevallen worden zichtbaar als juridische meerduidigheidspunten — ook informatief voor de jurist

**Bestand:** nieuw bestand `grensgevallen.md` in `.claude/skills/jas/`; stap 1 van de skill laadt dit bestand mee.

---

### Voorstel 2 — Human-in-the-loop feedback

**Kern:** de jurist die een annotatie valideert markeert bijstellingen gestructureerd; die worden als gecorrigeerde voorbeelden teruggevoerd in de kaders of grensgevallen-bibliotheek.

**AI-specialist:**  
Dit is de meest directe feedbackloop mogelijk zonder model-fine-tuning. Een jurist die zegt "deze formulering is een Rechtsfeit, niet een Voorwaarde, omdat…" levert een goud-waardige correctie. Die correctie moet niet verloren gaan in een e-mail — ze moet in `grensgevallen.md` terechtkomen.

Concreet: voeg een sectie toe aan elk rapport:

```markdown
## §12 Validatienotities (in te vullen door vakexpert)

| Nr | Originele classificatie | Bijgesteld naar | Motivering |
|----|------------------------|-----------------|------------|
| ... | ... | ... | ... |
```

Een aparte `/jas-review`-skill verwerkt deze notities naar `grensgevallen.md`.

**Senior jurist:**  
Dit formaliseert iets wat nu informeel of helemaal niet gebeurt: de terugkoppeling van de vakexpert naar het systeem. In een kwaliteitssysteem voor juridische producten is peer review geen optionele stap — het is de kern. Dit voorstel maakt die stap structureel.

**Verwachte winst:**  
- Elke gevalideerde annotatie maakt het systeem beter voor de volgende
- Opbouw van een inhoudelijke kennisbasis die de Belastingdienst toebehoort, niet het AI-model

---

### Voorstel 3 — Golden dataset en regressietesten

**Kern:** een door vakexperts gevalideerde annotatie (kandidaat: Art. 9 v3 na review) fungeert als referentie; elke verandering in kaders, skill of model wordt hierop getoetst.

**AI-specialist:**  
Software heeft unit tests. De JAS-skill heeft die niet. Dat betekent dat een wijziging in `kaders.md` of een modelupgrade ongemerkt de kwaliteit kan verlagen — en dat wordt pas ontdekt wanneer een jurist de output bekijkt.

Een "golden run" lost dit op: voer de annotatie opnieuw uit op het referentie-artikel, vergelijk de output met de gevalideerde versie. Wat is er anders? Is het beter of slechter?

De vergelijking hoeft niet geautomatiseerd te zijn — zelfs een handmatige vergelijking van de annotatie-tabel door een jurist is al waardevol.

**Senior jurist:**  
Dit is hetzelfde als de toetsing aan "vaste jurisprudentie": als een nieuw systeem andere uitkomsten geeft dan een gevestigd, betrouwbaar precedent, is dat een signaal dat nader onderzoek vereist. De golden dataset geeft de JAS-workflow een juridisch ankerpunt.

**Verwachte winst:**  
- Regressiebewaking bij modelupgrades (Sonnet → Opus → toekomstige versies)
- Bewaking bij kaders-updates (v1.0.10 → v1.1.0)
- Objectieve maatstaf voor "is deze annotatie beter dan de vorige?"

---

### Voorstel 4 — Gesplitste annotatiestap

**Kern:** stap 7 (JAS-annotatie) opsplitsen in vier expliciete micro-stappen: extractie → classificatie → redenering → verificatie.

**AI-specialist:**  
Stap 7 is verreweg de zwaarste stap in de workflow: het model moet tegelijk alle formuleringen identificeren, elk element classificeren, de redenering formuleren én de toelichting schrijven. Dat is te veel voor één aandachtsspan.

Door de stap op te splitsen geef je het model per taak volledige aandacht:

1. **Extractie** — identificeer alle formuleringen die geclassificeerd moeten worden; geen oordeel
2. **Classificatie** — ken per formulering het meest specifieke JAS-element toe; geen motivering
3. **Redenering** — schrijf de toelichting: methode, argumentatie, alternatieve classificaties
4. **Verificatie** — controleer: is elk lid volledig behandeld? Is er een formulering overgeslagen?

Dit verkleint de kans op missers (overgeslagen formuleringen, te brede classificaties) aanzienlijk.

**Senior jurist:**  
Dit spiegelt de werkwijze van een grondige jurist: eerst markeren, dan labelen, dan motiveren, dan nalopen. Door het model te dwingen in die volgorde te werken, is het eindresultaat navolgbaarder en minder rommelig.

**Verwachte winst:**  
- Minder gemiste formuleringen (nu soms overgeslagen bij complexe leden met veel bijzinnen)
- Betere motivering in de toelichting-kolom (redenering krijgt eigen aandacht)
- Verificatiestap vangt gevallen op die de extractie heeft gemist

---

### Voorstel 5 — Extended thinking op de annotatiestap

**Kern:** Claude Opus 4.6 met extended thinking inzetten voor stap 7 (annotatie) en stap 9 (juridische analyse); de zichtbare redenering verhoogt de navolgbaarheid.

**AI-specialist:**  
Extended thinking laat het model expliciet redeneren vóórdat het een antwoord geeft. Voor grensgevallen ("is dit een Voorwaarde of een Rechtsfeit?") is dat cruciaal: het model werkt de opties door in plaats van de meest voor de hand liggende classificatie te kiezen. De thinking-trace is voor de jurist leesbaar en geeft inzicht in hoe de AI tot zijn keuze is gekomen.

Praktisch: alleen stap 7 en stap 9 hoeven op Opus + thinking te draaien. De rest (ophalen, formatteren, opslaan) kan op Sonnet blijven — dit begrenst de kosten.

**Senior jurist:**  
Voor juridische interpretatie geldt: de *motivering* is minstens zo belangrijk als de conclusie. Een rechter die zijn vonnis niet motiveert, levert geen rechtsbedeling. Een JAS-annotatie die niet uitlegt *waarom* een element als Afleidingsregel is geclassificeerd in plaats van een Voorwaarde, heeft dezelfde tekortkoming. Extended thinking adresseert dit direct.

**Verwachte winst:**  
- Hogere kwaliteit bij complexe, meerduidigheid-rijke artikelen
- Transparante redenering die door de jurist kan worden beoordeeld en bijgesteld
- Beter gebruik van de drie interpretatiemethoden (grammaticaal, systematisch, teleologisch)

---

### Voorstel 6 — Strategische modelkeuze per stap

**Kern:** niet alle 14 stappen vereisen hetzelfde model; differentieer op kwaliteit/kosten-verhouding per stap.

**AI-specialist:**

| Stap | Taak | Aanbevolen model | Reden |
|------|------|-----------------|-------|
| 1–3 | Kaders laden, parsen, INDEX controleren | Sonnet | Gestructureerde instructies, geen interpretatie |
| 4–6 | Wetstekst + kruisverwijzingen ophalen | Sonnet | Feitelijke extractie, MCP-aanroepen |
| 7 | JAS-annotatie | **Opus + thinking** | Complexe classificatie, juridische redenering |
| 8 | Rekenstructuur | Opus | Formele logica, formule-afleiding |
| 9 | Awb-check | Sonnet | Gestructureerde beslisboom |
| 10 | Kwaliteitschecklist | Sonnet | Verificatie, geen interpretatie |
| 11–14 | Opslaan, INDEX bijwerken, commit | Sonnet | Bestandsbeheer, geen interpretatie |

**Senior jurist:**  
Niet elke stap vraagt hetzelfde niveau van juridisch redeneren. De aansluitingscheck op de Awb (stap 9) is een gestructureerde beslisboom — daar is een snel model voldoende. De eigenlijke annotatie (stap 7) is het hart van de analyse — daar mag het beste gereedschap voor worden ingezet.

**Verwachte winst:**  
- Betere kwaliteit op de stappen die er het meest toe doen
- Beheersbare kosten door Sonnet op de routinestappen
- Geen kwaliteitsverlies op extractie en formattering

---

### Voorstel 7 — Cross-artikel consistentie

**Kern:** een periodieke agent die alle analyses in `INDEX.md` scant op inconsistente classificaties van hetzelfde begrip.

**AI-specialist:**  
Nu worden artikelen onafhankelijk geannoteerd. Maar de Invorderingswet heeft ~70 artikelen die allemaal dezelfde begrippen gebruiken: "belastingaanslag", "belastingschuldige", "ontvanger". Als Art. 7 "belastingschuldige" als Rechtssubject classificeert en Art. 9 lid 3 dat als Rechtsobject, is dat een kwaliteitsgebrek — maar het valt nu niet op.

Een `/jas-consistentie`-skill loopt periodiek over alle analyses, extraheert de classificaties per begrip en rapporteert afwijkingen:

```
Begrip: "belastingschuldige"
  Art. 7 lid 1: Rechtssubject ✓
  Art. 9 lid 11: Rechtssubject ✓
  Art. 9 lid 3: Rechtsobject ← AFWIJKING (verwacht: Rechtssubject)
```

**Senior jurist:**  
Begrippenconsistentie is in de rechtspraktijk geen nice-to-have — het is fundamenteel. Als een wet "belastingschuldige" altijd als drager van een plicht behandelt en een annotatie plotseling "belastingschuldige" als voorwerp van een rechtsbetrekking aanmerkt, is dat een interpretatieverschil dat uitleg vereist. De cross-artikel check dwingt dit zichtbaar te maken.

**Verwachte winst:**  
- Systematisch bewaken van de juridische begrippencohesie over de hele annotatiebasis
- Automatisch signaal bij terminologische inconsistenties
- Sterker fundament voor het feitmodel en het CGM dat op de analyses wordt gebouwd

---

### Voorstel 8 — Parallelle annotators + judge

**Kern:** twee onafhankelijke agents annoteren hetzelfde artikel, een derde agent ("judge") beoordeelt beide annotaties en construeert de beste gecombineerde versie; afwijkingen worden als meerduidigheidssignalen gerapporteerd.

**AI-specialist:**  
Dit is het "mixture-of-agents" of "debate"-patroon. De opzet:

```
Agent A: annoteert Art. X met alleen wetstekst (grammaticale focus)
Agent B: annoteert Art. X met wetstekst + Leidraad + Memorie van Toelichting (teleologische focus)
Agent C (judge): ontvangt beide outputs + wetstekst
  → Accepteert waar A en B het eens zijn
  → Beargumenteert de juiste keuze waar ze afwijken
  → Markeert onoplosbare afwijkingen als meerduidigheidspunten
```

De echte waarde zit in de afwijkingen: die markeren niet alleen modelonzekerheid, maar ook juridische meerduidigheid. "Twee AI's zijn het hier niet eens" is een signaal dat de wet zelf niet eenduidig is — waardevolle informatie voor de jurist.

**Senior jurist:**  
Juristen werken ook met meerdere opiniën. Een opinie die geen enkele twijfel erkent, wordt in de rechtspraktijk met argwaan bekeken. Het debate-patroon formaliseert dit: het systeem is niet langer een autoriteit die één antwoord geeft, maar een instrument dat de ruimte van interpretaties verkent en expliciet maakt waar die ruimte breed is.

**Verwachte winst:**  
- Hogere kwaliteit bij meerduidigheid-rijke formuleringen
- Automatische identificatie van de moeilijkste juridische vragen in een artikel
- Inzicht in de "interpretatiebandbreedte" van een wet — ook voor juristen ongeacht de AI-kwaliteit

**Kanttekening:** dit patroon is pas effectief als de golden dataset (voorstel 3) bestaat. Zonder referentie is er geen manier om te beoordelen of de judge-output beter is dan een enkelvoudige annotatie.

---

## 4. Prioriteringsmatrix

### Assen

- **Juridische waarde** — in welke mate verbetert dit de inhoudelijke juridische kwaliteit van het rapport?
- **Technische inspanning** — hoeveel werk is nodig in de skill, kaders.md of tooling?

### Matrix

```
                    Lage inspanning          Hoge inspanning
                  ┌─────────────────────┬─────────────────────┐
  Hoge juridische │  1. Grensgevallen    │  8. Parallelle      │
  waarde          │  2. Human-in-loop   │     annotators      │
                  │  5. Extended think  │  7. Cross-artikel   │
                  │  3. Golden dataset* │     consistentie    │
                  ├─────────────────────┼─────────────────────┤
  Lagere          │  4. Gesplitste stap │  (niet van toepas-  │
  juridische      │  6. Modelkeuze/stap │   sing in dit plan) │
  waarde          │                     │                     │
                  └─────────────────────┴─────────────────────┘
* Golden dataset heeft lage technische inspanning maar vereist jurist-tijd
```

### Aanbevolen volgorde

| Prioriteit | Voorstel | Reden |
|-----------|---------|-------|
| **1** | Grensgevallen-bibliotheek | Morgen te starten, cumulatief effect, lage kosten |
| **2** | Human-in-the-loop feedback | Formaliseert review die nu informeel is; maakt 1 effectiever |
| **3** | Golden dataset | Vereist jurist-sessie; ontgrendelt meting van alle andere verbeteringen |
| **4** | Gesplitste annotatiestap | Skill-refactor zonder externe afhankelijkheden |
| **5** | Extended thinking | Één parameterkeuze; directe kwaliteitswinst op stap 7 |
| **6** | Strategische modelkeuze | Verfijning van 5; hogere ROI na golden dataset meetbaar is |
| **7** | Cross-artikel consistentie | Waardevoller naarmate INDEX groeit (nu 8 analyses; beter bij 20+) |
| **8** | Parallelle annotators | Meest indrukwekkend maar ook meest complex; pas na gouden dataset |

---

## 5. Implementatieplan

### Voorstel 1 — Grensgevallen-bibliotheek

**Doel:** een cumulatief few-shot geheugen dat moeilijke classificaties vastlegt en bij elke nieuwe annotatie wordt meegeladen.

**Aanpak:**
1. Maak `.claude/skills/jas/grensgevallen.md` aan met frontmatter en lege template
2. Documenteer de eerste 3–5 grensgevallen uit de bestaande analyses (bijv. Art. 9 lid 3 nr. 12: Afleidingsregel vs. Rechtsbetrekking)
3. Voeg aan stap 1 van SKILL.md toe: lees ook `grensgevallen.md` in
4. Voeg aan stap 10 (kwaliteitschecklist) toe: "Zijn er grensgevallen in deze annotatie die aan grensgevallen.md moeten worden toegevoegd?"

**Afhankelijkheden:** geen externe afhankelijkheden

**Doorlooptijd:** 1–2 uur (aanmaken bestand + 5 initiële grensgevallen documenteren)

**Meetcriterium:** bij de eerstvolgende annotatie van een nieuw artikel worden vergelijkbare formuleringen consistent geclassificeerd met die in de grensgevallen-bibliotheek

---

### Voorstel 2 — Human-in-the-loop feedback

**Doel:** een gestructureerd terugkoppelingsmechanisme waarmee jurist-bijstellingen de skill verbeteren.

**Aanpak:**
1. Voeg aan `rapportformat.md` sectie §12 toe: "Validatienotities" met tabel (Nr | Originele classificatie | Bijgesteld naar | Motivering)
2. Schrijf `/jas-review`-skill (nieuw bestand `.claude/skills/jas-review/SKILL.md`):
   - Leest §12 van een opgegeven rapport
   - Verrijkt `grensgevallen.md` met de gecorrigeerde classificaties
   - Stelt voor of `kaders.md` aanpassing nodig is
3. Documenteer het reviewproces in `README.md`

**Afhankelijkheden:** voorstel 1 (grensgevallen-bibliotheek) moet bestaan

**Doorlooptijd:** 2–3 uur (format + skill)

**Meetcriterium:** na twee reviewronden zijn de bijgestelde classificaties niet meer te zien in nieuwe annotaties van vergelijkbare formuleringen

---

### Voorstel 3 — Golden dataset

**Doel:** een door een vakexpert gevalideerde annotatie als kwaliteitsreferentie voor alle toekomstige verbeteringen.

**Aanpak:**
1. Selecteer Art. 9 v3 als kandidaat (meest volwassen versie)
2. Plan een reviewsessie met een senior jurist (2–3 uur): doorlopen §4 (annotatie per lid) en §9 (juridische analyse)
3. Documenteer bijstellingen via het §12-mechanisme (voorstel 2)
4. Sla het gevalideerde rapport op als `analyses/jas-referentie-art9-IW1990.md` met status-flag `gevalideerd: ja`
5. Voeg regressie-instructie toe aan README: "Voer bij elke kaders-update of modelupgrade /jas op Art. 9 IW 1990 uit en vergelijk §4 met de referentie"

**Afhankelijkheden:** voorstel 2 (reviewformat)

**Doorlooptijd:** 1 uur voorbereiding + jurist-sessie + 1 uur verwerking

**Meetcriterium:** referentie-rapport is aanwezig en goedgekeurd; volgende JAS-versie wordt hieraan getoetst voor release

---

### Voorstel 4 — Gesplitste annotatiestap

**Doel:** stap 7 van de skill opsplitsen in vier micro-stappen om de kwaliteit van de annotatie te verhogen door gerichte aandacht per deeltaak.

**Aanpak:**
1. Refactor stap 7 in `SKILL.md`:
   - **7a — Extractie:** lijst alle te classificeren formuleringen per lid, zonder oordeel
   - **7b — Classificatie:** ken per formulering het meest specifieke JAS-element toe
   - **7c — Redenering:** schrijf per element de toelichting (methode, argumentatie, alternatieven)
   - **7d — Verificatie:** controleer elk lid op volledigheid; markeer eventuele missers
2. Test de refactored skill op Art. 25 IW 1990 (onbekend artikel)
3. Vergelijk output met een enkelvoudige stap 7 op hetzelfde artikel

**Afhankelijkheden:** voorstel 3 (voor de vergelijking) is nuttig maar niet vereist

**Doorlooptijd:** 3–4 uur (skill-refactor + test)

**Meetcriterium:** het aantal geclassificeerde formuleringen per lid wijkt niet af van een handmatige telling van de zinsdelen in de wetstekst (< 5% missers)

---

### Voorstel 5 — Extended thinking op stap 7

**Doel:** Claude Opus 4.6 met extended thinking inzetten voor de annotatiestap om de kwaliteit van grensgevalclassificaties te verhogen.

**Aanpak:**
1. Pas SKILL.md aan: stap 7 en stap 9 expliciet aanmerken als "gebruik Opus + extended thinking"
2. Test op een grensgevalgeval uit de grensgevallen-bibliotheek (voorstel 1): geeft het model de juiste classificatie én een sterkere motivering?
3. Vergelijk de thinking-trace met de huidige toelichting-kolom: is de redenering rijker?

**Afhankelijkheden:** voorstel 1 (om te testen op bekende grensgevallen)

**Doorlooptijd:** 1–2 uur (skill-aanpassing + test)

**Meetcriterium:** bij drie bekende grensgevallen uit grensgevallen.md: classified Opus+thinking minstens 2/3 correct vs. Sonnet (handmatig beoordeeld door jurist)

---

### Voorstel 6 — Strategische modelkeuze per stap

**Doel:** differentieer modelkeuze per stap op kwaliteit/kosten-verhouding; Opus voor interpretatie, Sonnet voor extractie en formattering.

**Aanpak:**
1. Annoteer alle 14 stappen in SKILL.md met een aanbevolen model (zie tabel in §3.6)
2. Implementeer de selectie (via Claude Code's model-parameter of omgevingsvariabele)
3. Meet kosten per run vóór en na de differentiatie

**Afhankelijkheden:** voorstel 5 (want Opus op stap 7 is de kern van de differentiatie)

**Doorlooptijd:** 2–3 uur

**Meetcriterium:** kosten per volledige annotatie dalen met ≥ 30% t.o.v. volledig Opus, zonder kwaliteitsverlies op stap 7 (getoetst aan golden dataset)

---

### Voorstel 7 — Cross-artikel consistentie

**Doel:** automatisch bewaken van terminologische consistentie over alle annotaties in INDEX.md.

**Aanpak:**
1. Schrijf `/jas-consistentie`-skill (nieuw bestand):
   - Leest alle rapporten in `analyses/`
   - Extraheert alle classificaties per begrip (kolom "Formulering" in §4-tabellen)
   - Rapporteert begrippen die in verschillende artikelen anders zijn geclassificeerd
2. Voeg uitvoering toe aan README als aanbevolen kwartaalcheck
3. Eerste run: identificeer bestaande inconsistenties; verwerk ze via voorstel 2

**Afhankelijkheden:** minimaal 10 annotaties in INDEX.md voor zinvolle resultaten

**Doorlooptijd:** 4–6 uur (skill-bouw + eerste run)

**Meetcriterium:** geen enkele term met meer dan één JAS-klasse in de INDEX zonder expliciete redenering in grensgevallen.md

---

### Voorstel 8 — Parallelle annotators + judge

**Doel:** twee onafhankelijke annotaties + een judge-agent die de beste versie construeert en meerduidigheidspunten rapporteert.

**Aanpak:**
1. Maak `/jas-debate`-skill met drie agenten:
   - **Agent A:** annoteert met alleen wetstekst (grammaticale invalshoek)
   - **Agent B:** annoteert met wetstekst + Leidraad + eventuele MvT (teleologische invalshoek)
   - **Agent C (judge):** ontvangt A + B + wetstekst; accepteert consensus, beargumenteert keuze bij divergentie, markeert onoplosbare afwijkingen als §9.4-meerduidigheidspunten
2. Test op Art. 25 IW 1990 (uitstel van betaling — complex, veel leden)
3. Vergelijk met gouden Art. 9-annotatie: is de judge-output beter?

**Afhankelijkheden:** voorstel 3 (golden dataset) is vereist voor evaluatie; voorstel 5 (Opus) is aanbevolen voor agent A en B

**Doorlooptijd:** 6–8 uur (skill-bouw + test + evaluatie)

**Meetcriterium:** judge-output scoort beter op de golden dataset dan enkelvoudige annotatie (door jurist beoordeeld); divergentie-punten correleren met de spanningspunten in §9.4 van de referentie-annotatie

---

## Bijlage — Samenvatting roadmap

| Kwartaal | Voorstellen | Resultaat |
|---------|------------|-----------|
| Q2 2026 | 1, 2 | Grensgevallen-bibliotheek actief; reviewproces geformaliseerd |
| Q2 2026 | 3 | Golden dataset beschikbaar; kwaliteitsmeting mogelijk |
| Q3 2026 | 4, 5, 6 | Verbeterde annotatie-architectuur; Opus + thinking op kern |
| Q3 2026 | 7 | Cross-artikel consistentie bewaakt |
| Q4 2026 | 8 | Debate-patroon operationeel; meerduidigheidsrapportage live |
