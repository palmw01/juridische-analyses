# Bronindex Wetsanalyse-methodiek

Status: eerste opzet voor skillverbetering. Normatieve bronnen zijn uitsluitend:

- HANDLEIDING: `/home/willardp/Documenten/Projecten/wetsanalyse/Handleiding Wetsanalyse in de praktijk.pdf`
- LEIDRAAD: `/home/willardp/Documenten/Projecten/wetsanalyse/Leidraad voor Wetsanalyse op maat .pdf`

Geëxtraheerde tekstbestanden met pagina-ankers staan in `docs/wetsanalyse-methodiek/extracted/`.

## Uitgangspunt voor AI-gebruik

AI is een hulpmiddel voor het uitvoeren van Wetsanalyse. De AI ondersteunt het maken, controleren en verbeteren van analyseproducten, maar vervangt niet de menselijke juridische verantwoordelijkheid en niet de multidisciplinaire validatie.

Dit uitgangspunt volgt methodisch uit de nadruk op multidisciplinaire samenwerking, traceerbaarheid, controleerbaarheid en validatie in de bronnen. Het is daarnaast een projectkeuze voor de inzet van AI in deze repository.

## Kernprincipes uit de bronnen

### 1. Wetsanalyse dient uitvoeringspraktijk en andere juridische doelen

Bronpassage:

> Met Wetsanalyse kunnen we wet- en regelgeving en uitvoeringsbeleid (...) op een zodanige manier analyseren dat de resultaten bruikbaar zijn voor de inrichting van de uitvoeringspraktijk. Bijvoorbeeld voor het ontwikkelen van de informatietechnologie (IT) of het inrichten van de handmatige werkprocessen op kantoren. Wetsanalyse kan ook voor vele andere doeleinden worden ingezet, zoals voor uitvoeringstoetsen, het aanscherpen van wetgeving of behandelen van juridische casuïstiek.

Bron: LEIDRAAD p. 3; extract `leidraad.pages.md`, regels 49-56.

Skillconsequentie:

- Skills mogen niet aannemen dat de enige bestemming software-implementatie is.
- Bij elke workflow moet het doel van de analyse expliciet blijven: IT, handmatig proces, uitvoeringstoets, wetgevingsondersteuning, casuïstiek, of anders.

### 2. Traceerbaarheid is essentieel

Bronpassage:

> Daarnaast moet elke stap en elke beslissing in die vertaalslag expliciet gemaakt worden, zodat steeds te volgen is op welke wettelijke regels de beslissingen zijn gebaseerd. We noemen dat traceerbaarheid. Alleen dan kan de overheid transparant zijn over de (persoons)gegevens en regels die zij gebruikt en haar beslissingen uitleggen en verantwoorden aan burgers en bedrijven.

Bron: HANDLEIDING p. 3; extract `handleiding.pages.md`, regels 96-103.

Skillconsequentie:

- Elke skill-output moet herleidbaar zijn naar bron, annotatie, markering, begrip, regel of voorbeeldreeks.
- Skills moeten geen juridische conclusies produceren zonder expliciet bronanker.
- Reviewstappen moeten controleren op losse, niet-herleidbare conclusies.

### 3. Rechtsbeginselen sturen de kwaliteitsnorm

Bronpassages:

> Rechtmatige uitvoering: het nemen van beslissingen en gebruik van gegevens moeten rechtstreeks gebaseerd zijn op wet- en regelgeving en officieel (intern en extern gepubliceerd) uitvoeringsbeleid...

> Uitlegbare uitvoering: de genomen juridische beslissingen en gebruikte gegevens in de uitvoeringspraktijk moeten rechtstreeks gebaseerd zijn op, uitlegbaar zijn met, en traceerbaar zijn naar de primaire juridische bronnen;

> Rechtvaardige uitvoering: eventuele onvoorziene effecten bij de uitvoering van wetgeving moeten gesignaleerd worden aan de wetgever;

> Controleerbare uitvoering: transparant en navolgbaar moet zijn welke regels, gegevens en processtappen in de uitvoeringspraktijk gebruikt zijn voor juridische beslissingen.

Bron: HANDLEIDING p. 3-5; extract `handleiding.pages.md`, regels 130-140 en 152-164.

Skillconsequentie:

- De workflow moet expliciet controleren op rechtmatigheid, uitlegbaarheid, rechtvaardigheidssignalen en controleerbaarheid.
- AI mag rechtvaardigheidssignalen en beleidslacunes signaleren, maar niet zelfstandig oplossen als beleidskeuze.

### 4. Wetsanalyse is maatwerk; niet altijd zijn alle activiteiten nodig

Bronpassage:

> De hoofd- en deelactiviteiten van de Wetsanalyse kunnen volgordelijk plaatsvinden, in één of meerdere zich herhalende stappen (in iteraties) of in een afwijkende volgorde.

> De keuze is afhankelijk van de gewenste omvang en diepgang van de analyse, die weer afhankelijk is van wat met de Wetsanalyse beoogd wordt. Niet altijd hoeven alle activiteiten van de Wetsanalyse plaats te vinden.

> Elke activiteit binnen de Wetsanalyse vormt in feite een stukje gereedschap waarmee specifiek gewenste analyseresultaten behaald kunnen worden.

Bron: LEIDRAAD p. 3; extract `leidraad.pages.md`, regels 77-101.

Skillconsequentie:

- Skills moeten niet doen alsof A1-A6 altijd volledig en lineair moeten worden uitgevoerd.
- Er moet een aparte intake/op-maat skill komen die doel, aanleiding, context en benodigde activiteiten expliciteert.
- Huidige projectscope A2, A3 en A4b blijft toegestaan, maar moet als gekozen subset worden vastgelegd.

### 5. Multidisciplinair team is onderdeel van de methode

Bronpassage:

> De aanleiding, de context en het doel van de Wetsanalyse hebben ook invloed op de benodigde samenstelling van het multidisciplinaire team voor een Wetsanalyse. Bij een Wetsanalyse naar aanleiding van betekenis gerelateerde vragen over wetgeving zijn vooral verschillende soorten juristen nodig (...). Terwijl bij een analyse van wetgeving voor het ontwerpen van een nieuw uitvoeringsproces, naast de juristen ook nog deelname van procesdeskundigen (...) nodig zijn. Bij het ontwikkelen van IT via de ALEF-straat (...) zijn juist weer extra regelanalisten nodig.

Bron: LEIDRAAD p. 4; extract `leidraad.pages.md`, regels 117-129.

Skillconsequentie:

- AI mag disciplines simuleren als reviewperspectief, maar niet doen alsof daarmee het multidisciplinaire team is vervangen.
- Skills moeten aangeven welke menselijke discipline een output moet beoordelen.

### 6. Startactiviteiten horen vóór de analysekeuze

Bronpassage:

> De startactiviteiten zijn: a. Beschrijven van de aanleiding, context en doel(en) van de Wetsanalyse; b. Benoemen van de projecttypologie; c. Samenstellen van de hoofd- en deelactiviteiten; d. Samenstellen van het multidisciplinaire team.

Bron: LEIDRAAD p. 5; extract `leidraad.pages.md`, regels 177-184.

Skillconsequentie:

- Nieuwe workflow heeft een `wetsanalyse-op-maat` of intake-skill nodig.
- `/annoteer` moet bij ontbrekende A1/startinformatie niet per se blokkeren, maar wel expliciet signaleren welke startinformatie ontbreekt.

### 7. Juridische scenario’s verbinden praktijk en analyse

Bronpassage:

> Een juridisch scenario gaat over precies één te doorlopen pad van één burger of bedrijf. Bij voorkeur starten we met het scenario waarin in het meest recht toe recht aan praktijkvoorbeeld beschreven wordt, dit wordt het “happy scenario” genoemd.

> De juridische scenario’s helpen bij het aanscherpen en verduidelijken van het werkgebied, bij het bepalen van de volgorde in de analyse en bij het planmatig uitvoeren van de voorbereidende analysewerkzaamheden.

Bron: HANDLEIDING p. 19; extract `handleiding.pages.md`, regels 933-945.

Skillconsequentie:

- Skills voor annotatie en validatie moeten scenario’s als ordenings- en volledigheidsmiddel gebruiken.
- Ontbrekende scenario’s moeten als kwaliteitsrisico worden gemeld.

### 8. Activiteit 2: markeren, classificeren, diagram

Bronpassage:

> Activiteit 2 kent de volgende deelactiviteiten. a. Afbakenen van wetsformuleringen die bij elkaar horen, door middel van een markering. b. Gemarkeerde wetsformuleringen voorzien van een klasse uit het juridische analyseschema. c. Opstellen van een diagram dat de juridische structuur van gemarkeerde wetsformuleringen in onderlinge samenhang grafisch weergeeft voor een centrale klasse.

Bron: HANDLEIDING p. 31; extract `handleiding.pages.md`, regels 1511-1519.

Skillconsequentie:

- De huidige `/annoteer`-skill dekt de hoofdindeling van A2 goed.
- De skill moet sterker bronverwijzen naar de handleiding en duidelijker onderscheiden tussen bronregel, projectconventie en AI-operationele regel.

### 9. Markeringsuitgangspunten

Bronpassages:

> een lidwoord neem je mee in de markering van een stukje brontekst.

> als in een stukje brontekst een verwijzing staat, dan neem je die verwijzing ook mee in de markering.

> je markeert precies dat stukje tekst dat maximaal de betekenis representeert van het begrip die je uiteindelijk wilt maken.

> Voor de vraag welk woord of woorden je het beste kunt markeren, helpt het om meteen al met concrete voorbeelden te werken.

> Als je woorden markeert die een voorwaarde representeren, markeer dan bij voorkeur de gehele zin of het zinsdeel waarin de voorwaarden omschreven wordt.

> Doorgaans start je met het markeren van een stukje brontekst waar de klasse, die je wilt benoemen, gecreëerd of afgeleid wordt.

Bron: HANDLEIDING p. 33; extract `handleiding.pages.md`, regels 1539-1573.

Skillconsequentie:

- Deze regels horen in `annoteer/kaders.md` als PDF-gebaseerde normen.
- AI-review moet expliciet controleren op: lidwoorden, verwijzingen, te kleine markeringen, voorwaarden en startpunt bij gecreëerde/afgeleide klasse.

### 10. Diagrammen verbinden A1, A2 en A3

Bronpassage:

> Diagrammen helpen bij: (...) het verband leggen en - houden (‘brugfunctie’) tussen een juridisch scenario enerzijds en de gemarkeerde en geclassificeerde wetsformuleringen anderzijds (...).

> Een diagram verbindt dus activiteit 1 (juridische scenario) met activiteit 2 (markeren en classificeren van wetsformulering) en met de voorbereiding van activiteit 3 (inhoudelijke betekenis en relaties).

Bron: HANDLEIDING p. 33-34; extract `handleiding.pages.md`, regels 1587-1594 en 1633-1638.

Skillconsequentie:

- Diagrammen zijn niet alleen visualisatie maar controlemiddel.
- De annotatieskill moet diagrammen gebruiken als volledigheids- en samenhangstoets.

### 11. Activiteit 3: begrippen, afleidingsregels, scenario’s, bronrelaties

Bronpassage:

> Activiteit 3 kent de volgende deelactiviteiten. a. Maken van begrippen (...) b. Maken van afleidingsregels (...) c. Aanvullen van de in activiteit 1 opgestelde juridische scenario’s en uitbreiden van de scenario’s. d. Relateren van de begrippen en regels aan de juridische bronnen.

Bron: HANDLEIDING p. 37; extract `handleiding.pages.md`, regels 1753-1765.

Skillconsequentie:

- De huidige `/begrip`-skill dekt A3a en A3b, maar mist A3c als expliciete terugkoppeling naar scenario’s.
- Bronrelatie A3d moet als harde traceerbaarheidscheck blijven.

### 12. Begrippen expliciteren betekenis en zijn bouwstenen

Bronpassages:

> Voor iedere formulering (...) die in activiteit 2 is geclassificeerd, worden begrippen gemaakt met begripsnamen, definities, kenmerken en de onderlinge relaties tussen de begrippen.

> De begrippen zorgen voor betekenis, duidelijkheid, traceerbaarheid en begrijpelijkheid.

> Begrippen maken de inhoudelijke betekenis van geclassificeerde wetsformuleringen expliciet en precies. Begrippen vormen de bouwstenen voor afleidingsregels (...). Begrippen vormen de bouwstenen voor gegevensmodellen (...). Begrippen ondersteunen een eenduidige communicatie (...). Begrippen kunnen worden geïllustreerd en getoetst met concrete voorbeelden.

Bron: HANDLEIDING p. 36-38; extract `handleiding.pages.md`, regels 1737-1744 en 1819-1828.

Skillconsequentie:

- Begrippen moeten altijd vanuit A2-classificaties ontstaan.
- Voorbeelden horen bij begripsvorming, niet alleen bij regels/validaties.
- Skills moeten begripsvoorbeelden als toetsmiddel serieuzer verwerken.

### 13. Gelijke woorden kunnen verschillende begrippen zijn; verschillende woorden kunnen één begrip zijn

Bronpassage:

> Een begrip wordt hergebruikt voor elke formulering in de wetgeving die dezelfde unieke betekenis heeft. (...) Maar soms gebruikt de wetgever verschillende woorden om hetzelfde te duiden. (...) Andersom kan een op het oog gelijke formulering in de wetgeving, een verschillende betekenis hebben.

Bron: HANDLEIDING p. 38; extract `handleiding.pages.md`, regels 1830-1853.

Skillconsequentie:

- De bestaande homoniem/polyseem-regels in `begrip/SKILL.md` zijn methodisch goed geplaatst, maar moeten brongetrouw worden herleid en mogelijk eenvoudiger worden geformuleerd.
- AI-review moet zoeken naar te brede hergebruikte begrippen én onnodig gesplitste begrippen.

### 14. Concrete voorbeelden toetsen en verduidelijken begrippen

Bronpassage:

> Om de betekenis van begrippen te expliciteren, discussie over de betekenis te faciliteren en de begrippen te valideren (zie activiteit 4) maken we concrete voorbeelden bij de begrippen.

Bron: HANDLEIDING p. 50; extract `handleiding.pages.md`, regels 2601-2605.

Skillconsequentie:

- Voorbeelden zijn niet alleen output van `/valideer`; ze horen ook bij begripsanalyse.
- Een toekomstige skill-splitsing kan `wetsanalyse-voorbeelden` of een A4-reviewprotocol bevatten.

## Open punten voor vervolgaudit

Deze bronindex is een eerste basis. Nog uit te werken:

- volledige passages over activiteit 4, 5 en 6;
- volledige productentabel uit LEIDRAAD hoofdstuk 4;
- disciplines en rollen uit LEIDRAAD hoofdstuk 2/3;
- exacte status van JAS-taxonomie: welke onderdelen zijn expliciet PDF-gebaseerd en welke zijn projectconventie of externe methodiek;
- vergelijking van alle bestaande skillregels met deze bronindex.
