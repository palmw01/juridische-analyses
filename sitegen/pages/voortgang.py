"""Voortgangsdashboard — status per artikel/lid voor A2/A3a/A3b/A3c/A3d/A4b.

Werkt op de door sitegen.data uitgepakte dicts (underscore-keys).
"""

from collections import defaultdict
from html import escape
from pathlib import Path

from sitegen.html import schrijf_html


STATUS_LEEG = "■"
STATUS_STUB = "◐"
STATUS_COMPLEET = "●"
STATUS_WAARSCHUWING = "!"


def _heeft_kern(begrip: dict) -> bool:
    return bool(str(begrip.get("definitie") or "").strip())


def _heeft_relaties(begrip: dict) -> bool:
    relaties = begrip.get("relaties") or {}
    return any(relaties.get(k) for k in ("is-een", "heeft", "leidt-tot"))


def _bouw_lid_index(begrippen, regels, voorbeeldreeksen):
    per_lid: dict[tuple, dict] = defaultdict(lambda: {
        "begrippen": [],
        "regels": [],
        "voorbeeldreeksen": [],
        "wet": "",
    })

    for b in begrippen:
        bid = b.get("id", "")
        parts = bid.split("/")
        if len(parts) < 3:
            continue
        bwb = parts[0]
        if parts[1].startswith("art") and len(parts) >= 4 and parts[2].startswith("lid"):
            artikel = parts[1][3:]
            lid = parts[2][3:]
            sleutel = (bwb, artikel, lid)
        elif parts[1].startswith("par"):
            sleutel = (bwb, parts[1], "")
        else:
            continue
        per_lid[sleutel]["begrippen"].append(b)

    for r in regels:
        sleutel = (r.get("bwb_id", ""), str(r.get("artikel", "")), str(r.get("lid", "")))
        per_lid[sleutel]["regels"].append(r)

    regel_lookup = {r.get("id"): r for r in regels}
    for vr in voorbeeldreeksen:
        ar_id = vr.get("afleidingsregel_id")
        regel = regel_lookup.get(ar_id)
        if regel:
            sleutel = (regel.get("bwb_id", ""), str(regel.get("artikel", "")), str(regel.get("lid", "")))
            per_lid[sleutel]["voorbeeldreeksen"].append(vr)

    return per_lid


def _cel(status: str, telling: int | None = None) -> str:
    klasse_map = {
        STATUS_LEEG: "cel-leeg",
        STATUS_STUB: "cel-stub",
        STATUS_COMPLEET: "cel-compleet",
        STATUS_WAARSCHUWING: "cel-waarschuwing",
    }
    klasse = klasse_map.get(status, "cel-leeg")
    label = status if telling is None else f"{status} {telling}"
    return f'<span class="voortgang-cel {klasse}">{escape(label)}</span>'


def _status_a2(annotaties, bwb, artikel, lid):
    for a in annotaties:
        if (
            a.get("bwb_id") == bwb
            and str(a.get("artikel")) == str(artikel)
            and str(a.get("lid")) == str(lid)
        ):
            if a.get("rijen"):
                return STATUS_COMPLEET
            return STATUS_STUB
    return STATUS_LEEG


def _status_a3a(begrippen):
    if not begrippen:
        return STATUS_LEEG
    afgerond = sum(1 for b in begrippen if _heeft_kern(b) and _heeft_relaties(b))
    if afgerond == 0:
        return STATUS_STUB
    if afgerond < len(begrippen):
        return STATUS_WAARSCHUWING
    return STATUS_COMPLEET


def _status_a3b(begrippen, regels):
    afl_begrippen = [b for b in begrippen if b.get("jas_klasse") == "afleidingsregel"]
    if not afl_begrippen and not regels:
        return STATUS_LEEG
    regel_ids = {r.get("id") for r in regels}
    if not afl_begrippen:
        return STATUS_COMPLEET if regel_ids else STATUS_LEEG
    afgerond = sum(1 for b in afl_begrippen if b.get("afleidingsregel-id") in regel_ids)
    if afgerond == 0:
        return STATUS_STUB
    if afgerond < len(afl_begrippen):
        return STATUS_WAARSCHUWING
    return STATUS_COMPLEET


def _status_a3c(begrippen):
    if not begrippen:
        return STATUS_LEEG
    kandidaten = [b for b in begrippen if b.get("jas_klasse") in ("rechtsbetrekking", "rechtsfeit")]
    if not kandidaten:
        return STATUS_LEEG
    gevuld = sum(1 for b in kandidaten if b.get("scenario_refs"))
    if gevuld == 0:
        return STATUS_STUB
    if gevuld < len(kandidaten):
        return STATUS_WAARSCHUWING
    return STATUS_COMPLEET


def _status_a3d(begrippen):
    if not begrippen:
        return STATUS_LEEG
    gevuld = sum(1 for b in begrippen if b.get("bronnen_secundair"))
    if gevuld == 0:
        return STATUS_LEEG
    if gevuld < len(begrippen):
        return STATUS_WAARSCHUWING
    return STATUS_COMPLEET


def _status_a4b(regels, voorbeeldreeksen):
    if not regels:
        return STATUS_LEEG
    vr_voor_ar = {vr.get("afleidingsregel_id") for vr in voorbeeldreeksen}
    afgerond = sum(1 for r in regels if r.get("id") in vr_voor_ar)
    if afgerond == 0:
        return STATUS_STUB
    if afgerond < len(regels):
        return STATUS_WAARSCHUWING
    open_q = sum(
        1
        for vr in voorbeeldreeksen
        for k in (vr.get("kolommen") or [])
        if k.get("is_voorspelling_juist") == "?"
    )
    if open_q > 0:
        return STATUS_WAARSCHUWING
    return STATUS_COMPLEET


def gen_voortgang(
    out: Path,
    annotaties: list[dict],
    begrippen: list[dict],
    regels: list[dict],
    voorbeeldreeksen: list[dict],
) -> None:
    per_lid = _bouw_lid_index(begrippen, regels, voorbeeldreeksen)

    # Voeg leden uit annotaties toe
    for a in annotaties:
        bwb = a.get("bwb_id", "")
        artikel = str(a.get("artikel", ""))
        lid = str(a.get("lid", ""))
        sleutel = (bwb, artikel, lid)
        if sleutel not in per_lid:
            per_lid[sleutel]
        per_lid[sleutel]["wet"] = per_lid[sleutel].get("wet") or a.get("wet", "")

    rijen = []
    totalen = {
        "leden": 0, "a2_compleet": 0, "a3a_compleet": 0, "a3b_compleet": 0,
        "a4b_compleet": 0, "open_q": 0, "onbevestigd": 0,
    }
    for (bwb, artikel, lid), groep in sorted(per_lid.items()):
        bs = groep["begrippen"]
        rs = groep["regels"]
        vrs = groep["voorbeeldreeksen"]
        a2 = _status_a2(annotaties, bwb, artikel, lid)
        a3a = _status_a3a(bs)
        a3b = _status_a3b(bs, rs)
        a3c = _status_a3c(bs)
        a3d = _status_a3d(bs)
        a4b = _status_a4b(rs, vrs)
        totalen["leden"] += 1
        if a2 == STATUS_COMPLEET:
            totalen["a2_compleet"] += 1
        if a3a == STATUS_COMPLEET:
            totalen["a3a_compleet"] += 1
        if a3b in (STATUS_COMPLEET, STATUS_LEEG):
            totalen["a3b_compleet"] += 1
        if a4b in (STATUS_COMPLEET, STATUS_LEEG):
            totalen["a4b_compleet"] += 1
        totalen["open_q"] += sum(
            1 for vr in vrs for k in (vr.get("kolommen") or [])
            if k.get("is_voorspelling_juist") == "?"
        )
        totalen["onbevestigd"] += sum(
            1 for b in bs for m in (b.get("markeringen") or [])
            if not m.get("bevestigd")
        )
        wet = groep.get("wet") or next(
            (a.get("wet", "") for a in annotaties if a.get("bwb_id") == bwb),
            bwb,
        )
        rijen.append({
            "bwb": bwb, "artikel": artikel, "lid": lid, "wet": wet,
            "a2": a2, "a3a": a3a, "a3b": a3b, "a3c": a3c, "a3d": a3d, "a4b": a4b,
            "n_begrippen": len(bs), "n_regels": len(rs), "n_vr": len(vrs),
        })

    tabel_rijen = ""
    for r in rijen:
        wet = escape(r["wet"] or r["bwb"])
        artikel = escape(r["artikel"])
        lid = escape(r["lid"]) if r["lid"] else ""
        if r["lid"] and r["artikel"]:
            link = f'annotaties/{r["bwb"]}/art{r["artikel"]}-lid{r["lid"]}.html'
            vindplaats = f'art. {artikel} lid {lid}'
        elif r["artikel"]:
            link = f'annotaties/{r["bwb"]}/{r["artikel"]}.html'
            vindplaats = f'§ {artikel}'
        else:
            link = ""
            vindplaats = r["bwb"]
        link_html = f'<a href="{escape(link)}">{vindplaats}</a>' if link else vindplaats
        tabel_rijen += (
            f'<tr>'
            f'<td>{wet}</td>'
            f'<td>{link_html}</td>'
            f'<td>{_cel(r["a2"])}</td>'
            f'<td>{_cel(r["a3a"], r["n_begrippen"])}</td>'
            f'<td>{_cel(r["a3b"], r["n_regels"])}</td>'
            f'<td>{_cel(r["a3c"])}</td>'
            f'<td>{_cel(r["a3d"])}</td>'
            f'<td>{_cel(r["a4b"], r["n_vr"])}</td>'
            f'</tr>\n'
        )

    body = f"""<h1>Voortgangsdashboard</h1>
<p class="lead">Status per artikel/lid voor de activiteiten A2 (annotatie), A3a (definitie), A3b (regel), A3c (scenario), A3d (secundaire bronnen) en A4b (voorbeeldreeks).</p>

<section class="voortgang-totalen">
  <div class="kpi"><span class="kpi-label">Leden</span><span class="kpi-waarde">{totalen['leden']}</span></div>
  <div class="kpi"><span class="kpi-label">A2 compleet</span><span class="kpi-waarde">{totalen['a2_compleet']}/{totalen['leden']}</span></div>
  <div class="kpi"><span class="kpi-label">A3a compleet</span><span class="kpi-waarde">{totalen['a3a_compleet']}/{totalen['leden']}</span></div>
  <div class="kpi"><span class="kpi-label">A4b compleet</span><span class="kpi-waarde">{totalen['a4b_compleet']}/{totalen['leden']}</span></div>
  <div class="kpi"><span class="kpi-label">Openstaande ?</span><span class="kpi-waarde">{totalen['open_q']}</span></div>
  <div class="kpi"><span class="kpi-label">Onbevestigde markeringen</span><span class="kpi-waarde">{totalen['onbevestigd']}</span></div>
</section>

<table class="voortgang-tabel">
  <thead>
    <tr>
      <th>Wet</th>
      <th>Vindplaats</th>
      <th>A2</th>
      <th>A3a</th>
      <th>A3b</th>
      <th>A3c</th>
      <th>A3d</th>
      <th>A4b</th>
    </tr>
  </thead>
  <tbody>
    {tabel_rijen}
  </tbody>
</table>

<aside class="voortgang-legenda">
  <h2>Legenda</h2>
  <ul>
    <li>{_cel(STATUS_LEEG)} geen data of niet van toepassing</li>
    <li>{_cel(STATUS_STUB)} bestand bestaat, nog niet afgerond</li>
    <li>{_cel(STATUS_COMPLEET)} afgerond</li>
    <li>{_cel(STATUS_WAARSCHUWING)} afgerond met openstaande punten of L3-meldingen</li>
  </ul>
</aside>
"""

    schrijf_html(out, "voortgang.html", "Voortgang | Belastingdienst", body, active="voortgang")
