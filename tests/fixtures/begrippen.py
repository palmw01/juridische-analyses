"""Factory voor minimaal-valide begrip-dicts (schema-conform + voor directe unit-tests)."""


def maak_begrip(**overrides) -> dict:
    base = {
        "begrip-id": "BWBR0004770/art9/lid1/belastingschuldige",
        "begripsnaam": "belastingschuldige",
        "soort": "entiteit",
        "definitie": {
            "kern": "de persoon die de belasting verschuldigd is",
            "contexten": [],
        },
        "definitie-versie": 1,
        "definitie-gebaseerd-op": ["m-001"],
        "herkomst": "direct",
        "status": "concept",
        "jas-klasse": "rechtssubject",
        "toelichting-klasse": "Drager van rechten en plichten in de invorderingsrelatie",
        "identificatiebegrip": False,
        "geldigheid-van": "2024-01-01",
        "markeringen": [
            {
                "markering-id": "m-001",
                "bijdrage": "primair",
                "bron-annotatie-id": "BWBR0004770/art9/lid1",
                "tekst": "de persoon die de belasting verschuldigd is",
                "interpretatiemethode": "grammaticaal",
                "bevestigd": False,
            }
        ],
        "relaties": {
            "is-een": [],
            "heeft": [],
            "leidt-tot": [],
        },
        "aliases": [],
        "voorbeelden": [
            {"stelling": "Jan is belastingschuldige", "waar": True, "toelichting": "happy"},
            {"stelling": "De BV is belastingschuldige", "waar": True, "toelichting": "grensgeval"},
        ],
        "kenmerken": [],
    }
    base.update(overrides)
    return base
