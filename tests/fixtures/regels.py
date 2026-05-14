"""Factory voor minimaal-valide regel-dicts."""


def maak_regel(**overrides) -> dict:
    base = {
        "regel-id": "BWBR0004770/art9/lid1/r001",
        "naam": "Berekening betalingstermijn",
        "soort": "Afleidingsregel",
        "formele-regel": "betalingstermijn = 30 dagen na dagtekening aanslag",
        "toelichting": "Standaard betalingstermijn conform art. 9 IW 1990.",
        "invoer": [],
        "uitvoer": [],
        "operators": [],
        "voorbeeldreeksen": [
            {
                "invoerwaarden": {"dagtekening": "2024-01-01"},
                "verwachte-uitkomst": {"betalingstermijn": "2024-01-31"},
                "juridisch-juist": True,
            },
            {
                "invoerwaarden": {"dagtekening": "2024-01-01"},
                "verwachte-uitkomst": {"betalingstermijn": "2024-01-15"},
                "juridisch-juist": False,
                "toelichting": "Grensgeval: termijn te kort",
            },
        ],
        "tussenresultaat": False,
        "bwb-id": "BWBR0004770",
        "artikel": "9",
        "lid": "1",
    }
    base.update(overrides)
    return base
