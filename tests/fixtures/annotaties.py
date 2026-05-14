"""Factory voor minimaal-valide annotatie-dicts (JSON-formaat)."""


def maak_annotatie(**overrides) -> dict:
    base = {
        "annotatie-id": "BWBR0004770/art9/lid1",
        "bwb-id": "BWBR0004770",
        "wet": "Invorderingswet 1990",
        "artikel": "9",
        "lid": "1",
        "peildatum": "2024-01-01",
        "wetstekst": "De belastingaanslag moet worden betaald binnen dertig dagen.",
        "annotatierijen": [
            {
                "rij-id": "r1",
                "markering": "belastingschuldige",
                "jas-klasse": "rechtssubject",
                "begrip-id": "BWBR0004770/art9/lid1/belastingschuldige",
                "interpretatiemethode": "grammaticaal",
            }
        ],
        "diagram": {
            "knopen": [{"id": "k1", "label": "belastingschuldige", "jas-klasse": "rechtssubject"}],
            "kanten": [],
        },
    }
    base.update(overrides)
    return base
