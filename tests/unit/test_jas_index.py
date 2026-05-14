from jas_index_lib import haal_kern, haal_contexten


# ---------- haal_kern ----------

def test_haal_kern_dict_met_kern():
    assert haal_kern({"kern": "de belastingplichtige"}) == "de belastingplichtige"


def test_haal_kern_dict_zonder_kern():
    assert haal_kern({}) == ""


def test_haal_kern_dict_kern_none():
    assert haal_kern({"kern": None}) == ""


def test_haal_kern_legacy_string():
    assert haal_kern("legacy definitie") == "legacy definitie"


def test_haal_kern_none():
    assert haal_kern(None) == ""


def test_haal_kern_stript_whitespace():
    assert haal_kern({"kern": "  spaties  "}) == "spaties"


def test_haal_kern_lege_string():
    assert haal_kern("") == ""


# ---------- haal_contexten ----------

def test_haal_contexten_dict_met_contexten():
    ctx = [{"markering-id": "m-001", "tekst": "in het kader van art. 9"}]
    assert haal_contexten({"kern": "x", "contexten": ctx}) == ctx


def test_haal_contexten_dict_zonder_contexten():
    assert haal_contexten({"kern": "x"}) == []


def test_haal_contexten_contexten_none():
    assert haal_contexten({"kern": "x", "contexten": None}) == []


def test_haal_contexten_legacy_string():
    assert haal_contexten("legacy") == []


def test_haal_contexten_none():
    assert haal_contexten(None) == []


def test_haal_contexten_lege_lijst():
    assert haal_contexten({"contexten": []}) == []


def test_haal_contexten_geeft_kopie():
    ctx = [{"markering-id": "m-001"}]
    result = haal_contexten({"contexten": ctx})
    result.append({"markering-id": "m-002"})
    assert len(haal_contexten({"contexten": ctx})) == 1
