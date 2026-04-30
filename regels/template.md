---
type: afleidingsregel
regel-id: AR-[art]-[nr]
naam: ""
soort: [Beslissingsregel | Rekenregel | Beperkingsregel | Specialisatieregel]
tags:
  - afleidingsregel
  - wet/[wet-afkorting]   # bijv. wet/iw1990
  - art/[nummer]          # bijv. art/25
afgeleid-van: ""   # wiki-link naar annotatie-noot: annotaties/[wet]/art[nr]
peildatum: [YYYY-MM-DD]
bepaalt: ""   # wiki-link naar het begrip met jas-klasse: afleidingsregel (het begrip dat deze regel uitwerkt)
rechtsfeit: ""                    # wiki-link naar het rechtsfeit dat deze regel triggert
invoer: []                        # wiki-links naar invoerbegrippen (variabelen/parameters/tijdsaanduidingen)
uitvoer: []                       # wiki-links naar uitvoerbegrippen (het afgeleide rechtsgevolg, bijv. rechtsbetrekking of variabele); normaal één element — bij meervoudig uitvoer: aparte regel-noten per uitvoerbegrip
operators: []                     # EN | OF | NIET | plus | min | maal | gedeeld-door | ten-hoogste | ten-minste
---

## Formele regel

<!-- Kies het taalpatroon passend bij soort; verwijder de overige blokken -->

<!-- BESLISSINGSREGEL (cumulatief / EN) -->
**[rechtssubject] is [uitvoerbegrip]**
indien aan alle volgende voorwaarden is voldaan:
- [voorwaarde 1]
- [voorwaarde 2]

<!-- BESLISSINGSREGEL (alternatief / OF) -->
**[rechtssubject] is [uitvoerbegrip]**
indien aan ten minste één van de volgende voorwaarden is voldaan:
- [voorwaarde A]
- [voorwaarde B]

<!-- REKENREGEL -->
**[uitvoerbegrip] moet berekend worden als**
[invoerbegrip1] [operator] [invoerbegrip2]

<!-- BEPERKINGSREGEL -->
**[uitvoerbegrip] bedraagt ten hoogste/ten minste [grenswaarde of -begrip]**
indien [voorwaarde]

<!-- SPECIALISATIEREGEL -->
**In afwijking van [naam hoofdregel]:**
[uitvoerbegrip] is [specifieke waarde of begrip]
indien [specificerende voorwaarde]

## Toelichting

[tracering naar specifiek lid + interpretatiemotivering]

## Voorbeeldreeksen

| Invoerwaarden | Verwachte uitkomst | Is voorspelling juridisch juist? |
|--------------|-------------------|---------------------------------|
| [waarden] | [uitkomst] | ja / nee |
| [grensgeval] | [uitkomst] | ja / nee |
