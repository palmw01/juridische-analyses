"""Factory voor minimaal-valide regel-dicts (schema-conform)."""


def maak_regel(**overrides) -> dict:
    base = {
        "regel-id": "AR-0001",
        "naam": "Berekening betalingstermijn",
        "soort": "Rekenregel",
        "formele-regel": "betalingstermijn = 30 dagen na dagtekening aanslag",
        "toelichting": "Standaard betalingstermijn conform art. 9 IW 1990.",
        "invoer": [],
        "uitvoer": ["BWBR0004770/art9/lid1/betalingstermijn"],
        "operators": [],
        "voorbeeldreeksen": [
            {
                "invoerwaarden": "dagtekening=2024-01-01",
                "verwachte-uitkomst": "betalingstermijn=2024-01-31",
                "juridisch-juist": True,
            },
            {
                "invoerwaarden": "dagtekening=2024-01-01",
                "verwachte-uitkomst": "betalingstermijn=2024-01-15",
                "juridisch-juist": False,
                "toelichting": "Grensgeval: termijn te kort",
            },
        ],
        "tussenresultaat": False,
        "bwb-id": "BWBR0004770",
        "artikel": "9",
        "lid": "1",
        "peildatum": "2024-01-01",
        "rechtsfeit-id": None,
    }
    base.update(overrides)
    return base
