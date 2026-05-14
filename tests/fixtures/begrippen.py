"""Factory voor minimaal-valide begrip-dicts (voor YAML-serialisatie en directe tests)."""


def maak_begrip(**overrides) -> dict:
    base = {
        "begrip-id": "BWBR0004770/art9/lid1/belastingschuldige",
        "begripsnaam": "belastingschuldige",
        "soort": "rechtssubject",
        "definitie": {
            "kern": "de persoon die de belasting verschuldigd is",
            "contexten": [],
        },
        "definitie-versie": "1.0",
        "definitie-gebaseerd-op": ["m-001"],
        "herkomst": "expliciet",
        "status": "concept",
        "jas-klasse": "rechtssubject",
        "markeringen": [
            {
                "markering-id": "m-001",
                "bijdrage": "primair",
                "bron-annotatie-id": "BWBR0004770/art9/lid1",
                "jas-klasse": "rechtssubject",
                "bevestigd": False,
            }
        ],
        "relaties": {
            "is-een": [],
            "heeft": [],
            "leidt-tot": [],
        },
        "aliases": [],
        "voorbeelden": [],
        "kenmerken": [],
    }
    base.update(overrides)
    return base
