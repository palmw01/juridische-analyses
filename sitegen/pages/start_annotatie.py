"""Genereer `start_annotatie.html` — form waarmee gebruikers een
annotatieverzoek indienen door een prefilled GitHub-issue te openen.

De pagina is volledig statisch: alle logica draait clientside. Submit
gaat via GitHub's `?title=&body=&labels=` URL-parameters; daarmee
bouwen we geen backend, maar laten we GitHub de issue-creatie afhandelen.
De gebruiker moet ingelogd zijn op GitHub. De daadwerkelijke
annotatie-run wordt in `.github/workflows/annoteer.yml` pas gestart na
goedkeuring in environment `claude-approval`.
"""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

from sitegen.html import copy_button, schrijf_html

REPO_URL = "https://github.com/palmw01/juridische-analyses"
ISSUE_LABEL = "annotatie-verzoek"
API_URL = (
    "https://api.github.com/repos/palmw01/juridische-analyses/issues"
    "?labels=annotatie-verzoek&state=all&per_page=10"
)

# (bwb_id, leesbare titel, korte naam zoals gebruikt in /annoteer-commando)
CANONIEKE_WETTEN: list[tuple[str, str, str]] = [
    ("BWBR0004770", "Invorderingswet 1990", "IW 1990"),
    ("BWBR0002320", "Algemene wet inzake rijksbelastingen", "AWR"),
    ("BWBR0005537", "Algemene wet bestuursrecht", "Awb"),
    ("BWBR0004772", "Uitvoeringsbesluit Invorderingswet 1990", "UB IW 1990"),
    ("BWBR0024096", "Leidraad Invordering 2008", "Leidraad Invordering 2008"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _wet_options_html() -> str:
    opties = [
        f'<option value="{escape(bwb, quote=True)}" '
        f'data-kortenaam="{escape(kort, quote=True)}">'
        f'{escape(titel)} ({escape(bwb)})</option>'
        for bwb, titel, kort in CANONIEKE_WETTEN
    ]
    opties.append('<option value="__custom__">Andere wet (BWB-id zelf invullen)…</option>')
    return "\n".join(opties)


def _bestaande_artikelen(indices: list, annotaties: list) -> dict[str, list[str]]:
    per_wet: dict[str, set[str]] = {}
    for bron in (*indices, *annotaties):
        bwb = bron.get("bwb_id") or ""
        artikel = str(bron.get("artikel") or "").strip()
        if not bwb or not artikel:
            continue
        per_wet.setdefault(bwb, set()).add(artikel)
    return {bwb: sorted(arts, key=lambda a: (len(a), a)) for bwb, arts in per_wet.items()}


def _datalist_html() -> str:
    # Lege datalist — wordt clientside per geselecteerde wet gevuld vanuit ARTIKELEN_PER_WET.
    return '<datalist id="artikelOpties"></datalist>'


def _uitleg_html() -> str:
    return """<details class="card" open>
  <summary class="card-title" style="cursor:pointer">Hoe werkt dit?</summary>
  <ol style="margin:0.5rem 0 0 1.25rem;padding:0">
    <li>Vul het form in (wet, artikel, lid of sectie).</li>
    <li>Klik op <strong>Open op GitHub</strong>. Je wordt naar een nieuwe issue gestuurd waarin titel, body en label al ingevuld zijn — klik daar op <em>Submit new issue</em>.</li>
    <li>De maker krijgt een melding en moet jouw verzoek <strong>goedkeuren</strong> in de Actions-tab.</li>
    <li>Na goedkeuring draait de bot <code>/annoteer …</code> en opent een PR met de annotatiebestanden.</li>
  </ol>
  <p style="margin:0.75rem 0 0;font-size:0.85rem;color:var(--text-muted)">Je hebt een GitHub-account nodig. De bot draait pas na expliciete goedkeuring — er worden geen API-tokens verbruikt zonder dat de maker akkoord geeft.</p>
</details>"""


def _form_html() -> str:
    wet_opties = _wet_options_html()
    return f"""<form id="annotatieForm" class="card" data-repo-url="{escape(REPO_URL, quote=True)}" data-label="{escape(ISSUE_LABEL, quote=True)}">
  <div class="card-title">Annotatieverzoek</div>

  <div class="form-row">
    <label for="wet">Wet</label>
    <select id="wet" name="wet" required>
      {wet_opties}
    </select>
  </div>

  <div class="form-row" id="customWetRow" hidden>
    <label for="wetCustomBwb">BWB-id</label>
    <input type="text" id="wetCustomBwb" name="wetCustomBwb" placeholder="BWBR0001234" pattern="BWBR[0-9]+" autocomplete="off">
    <label for="wetCustomKort" style="margin-top:0.5rem">Korte naam (voor het commando)</label>
    <input type="text" id="wetCustomKort" name="wetCustomKort" placeholder="bv. URIB 1990" autocomplete="off">
  </div>

  <fieldset class="form-row">
    <legend>Type annotatie</legend>
    <label><input type="radio" name="flow" value="index"> Artikel-index (Flow A)</label>
    <label><input type="radio" name="flow" value="lid" checked> Lid-annotatie (Flow B)</label>
    <label><input type="radio" name="flow" value="sectie"> Sectie-annotatie (Flow C, voor Leidraad / beleid)</label>
  </fieldset>

  <div class="form-row" id="artikelRow">
    <label for="artikel">Artikel</label>
    <input type="text" id="artikel" name="artikel" list="artikelOpties" placeholder="bv. 9" autocomplete="off">
    {_datalist_html()}
  </div>

  <div class="form-row" id="lidRow">
    <label for="lid">Lid</label>
    <input type="text" id="lid" name="lid" placeholder="bv. 1" autocomplete="off">
  </div>

  <div class="form-row" id="sectieRow" hidden>
    <label for="sectie">Sectie</label>
    <input type="text" id="sectie" name="sectie" placeholder="bv. par1-1" autocomplete="off">
  </div>

  <div class="form-row">
    <label for="aanvrager">Aanvrager (optioneel)</label>
    <input type="text" id="aanvrager" name="aanvrager" placeholder="Naam of team" autocomplete="off">
  </div>

  <div class="form-row">
    <label for="scenario">Scenario / motivatie (optioneel)</label>
    <textarea id="scenario" name="scenario" rows="3" placeholder="Korte uitleg waarom je deze annotatie nodig hebt"></textarea>
  </div>

  <p id="formError" class="error" role="alert" aria-live="polite" hidden></p>
</form>"""


def _preview_card_html() -> str:
    return f"""<div class="card">
  <div class="card-title">Preview</div>
  <p style="margin:0 0 0.5rem;font-weight:600">Issue-titel</p>
  <pre id="titlePreview" style="margin:0 0 1rem;padding:0.5rem 0.75rem;background:var(--bg-muted);border-radius:4px;white-space:pre-wrap;word-break:break-word"></pre>

  <p style="margin:0 0 0.5rem;font-weight:600">Slash-commando <span style="font-weight:400;color:var(--text-muted)">(wordt in de issue-body geplaatst)</span></p>
  <div style="display:flex;gap:0.5rem;align-items:flex-start">
    <code id="cmdInline" style="flex:1;padding:0.5rem 0.75rem;background:var(--bg-muted);border-radius:4px;font-family:var(--font-mono);font-size:0.9rem;display:block;white-space:pre-wrap;word-break:break-all"></code>
    {copy_button("#cmdInline", label="Kopieer commando")}
  </div>

  <details style="margin-top:1rem">
    <summary style="cursor:pointer;font-weight:600">Volledige issue-body bekijken</summary>
    <pre id="bodyPreview" style="margin:0.5rem 0 0;padding:0.5rem 0.75rem;background:var(--bg-muted);border-radius:4px;white-space:pre-wrap;word-break:break-word;font-size:0.85rem"></pre>
  </details>

  <div style="display:flex;gap:0.75rem;margin-top:1rem;flex-wrap:wrap">
    <a id="openIssueBtn" class="btn-primary" href="#" target="_blank" rel="noopener noreferrer" aria-disabled="true" style="text-decoration:none">
      Open op GitHub →
    </a>
    <span id="formStatus" role="status" aria-live="polite" style="font-size:0.85rem;color:var(--text-muted);align-self:center"></span>
  </div>
</div>"""


def _status_widget_html() -> str:
    return f"""<div class="card" id="recentRequestsCard">
  <div class="card-title">Recente verzoeken</div>
  <p id="recentRequestsHint" style="margin:0;font-size:0.85rem;color:var(--text-muted)">Bezig met laden…</p>
  <ul id="recentRequests" class="item-list" style="display:none"></ul>
  <p style="margin:0.75rem 0 0;font-size:0.8rem;color:var(--text-muted)">Bron: <a href="{escape(API_URL, quote=True)}" target="_blank" rel="noopener noreferrer">GitHub Issues API</a> (ongetauthenticeerd; rate limit 60/uur per IP).</p>
</div>"""


def _script_js(artikelen_per_wet_json: str, api_url: str) -> str:
    return f"""<script>
(function() {{
  var ARTIKELEN_PER_WET = {artikelen_per_wet_json};
  var KORTE_NAMEN = {{}};
  document.querySelectorAll('#wet option[data-kortenaam]').forEach(function(opt) {{
    KORTE_NAMEN[opt.value] = opt.getAttribute('data-kortenaam');
  }});

  var form = document.getElementById('annotatieForm');
  var wetSel = document.getElementById('wet');
  var customRow = document.getElementById('customWetRow');
  var customBwb = document.getElementById('wetCustomBwb');
  var customKort = document.getElementById('wetCustomKort');
  var artikelRow = document.getElementById('artikelRow');
  var artikelInput = document.getElementById('artikel');
  var artikelDatalist = document.getElementById('artikelOpties');
  var lidRow = document.getElementById('lidRow');
  var lidInput = document.getElementById('lid');
  var sectieRow = document.getElementById('sectieRow');
  var sectieInput = document.getElementById('sectie');
  var aanvragerInput = document.getElementById('aanvrager');
  var scenarioInput = document.getElementById('scenario');
  var titlePre = document.getElementById('titlePreview');
  var bodyPre = document.getElementById('bodyPreview');
  var cmdInline = document.getElementById('cmdInline');
  var openBtn = document.getElementById('openIssueBtn');
  var errorEl = document.getElementById('formError');
  var statusEl = document.getElementById('formStatus');
  var repoUrl = form.getAttribute('data-repo-url');
  var label = form.getAttribute('data-label');

  function huidigeFlow() {{
    var checked = form.querySelector('input[name="flow"]:checked');
    return checked ? checked.value : 'lid';
  }}

  function huidigeWet() {{
    var bwb = wetSel.value;
    if (bwb === '__custom__') {{
      return {{
        bwb: (customBwb.value || '').trim(),
        kort: (customKort.value || '').trim(),
        titel: (customKort.value || '').trim() || (customBwb.value || '').trim()
      }};
    }}
    var opt = wetSel.options[wetSel.selectedIndex];
    return {{
      bwb: bwb,
      kort: KORTE_NAMEN[bwb] || bwb,
      titel: opt ? opt.textContent.replace(/\\s*\\([^)]*\\)\\s*$/, '') : bwb
    }};
  }}

  function vulDatalistVoor(bwb) {{
    artikelDatalist.innerHTML = '';
    var lijst = ARTIKELEN_PER_WET[bwb] || [];
    lijst.forEach(function(a) {{
      var opt = document.createElement('option');
      opt.value = a;
      artikelDatalist.appendChild(opt);
    }});
  }}

  function bouwCommando(flow, wet) {{
    var artikel = (artikelInput.value || '').trim();
    var lid = (lidInput.value || '').trim();
    var sectie = (sectieInput.value || '').trim();
    if (flow === 'sectie') {{
      return '/annoteer sectie ' + sectie + ' ' + wet.kort;
    }}
    if (flow === 'lid') {{
      return '/annoteer art. ' + artikel + ' lid ' + lid + ' ' + wet.kort;
    }}
    return '/annoteer art. ' + artikel + ' ' + wet.kort;
  }}

  function bouwTitel(flow, wet) {{
    var artikel = (artikelInput.value || '').trim();
    var lid = (lidInput.value || '').trim();
    var sectie = (sectieInput.value || '').trim();
    if (flow === 'sectie') return '[annotatieverzoek] sectie ' + sectie + ' ' + wet.kort;
    if (flow === 'lid')    return '[annotatieverzoek] art. ' + artikel + ' lid ' + lid + ' ' + wet.kort;
    return '[annotatieverzoek] art. ' + artikel + ' ' + wet.kort;
  }}

  function bouwBody(flow, wet, commando) {{
    var artikel = (artikelInput.value || '').trim() || '—';
    var lid = (lidInput.value || '').trim() || '—';
    var sectie = (sectieInput.value || '').trim() || '—';
    var aanvrager = (aanvragerInput.value || '').trim() || '—';
    var scenario = (scenarioInput.value || '').trim() || '—';
    return [
      '## Annotatieverzoek',
      '',
      '| Veld | Waarde |',
      '|------|--------|',
      '| Wet | ' + (wet.titel || wet.bwb) + ' (`' + (wet.bwb || '?') + '`) |',
      '| Type | ' + flow + ' |',
      '| Artikel | ' + artikel + ' |',
      '| Lid | ' + lid + ' |',
      '| Sectie | ' + sectie + ' |',
      '| Aanvrager | ' + aanvrager + ' |',
      '',
      '**Commando** (wordt door de bot opgepakt):',
      '',
      '```',
      commando,
      '```',
      '',
      '**Scenario / motivatie**',
      '',
      scenario,
      '',
      '---',
      'Aangevraagd via [start_annotatie.html](https://palmw01.github.io/juridische-analyses/start_annotatie.html). De maker moet dit verzoek eerst goedkeuren in de Actions-tab voordat de bot wordt uitgevoerd.'
    ].join('\\n');
  }}

  function valideer(flow, wet) {{
    if (!wet.bwb) return 'Kies een wet of vul een BWB-id in.';
    if (wetSel.value === '__custom__' && !wet.kort) return 'Vul een korte naam in voor de wet (bv. URIB 1990).';
    if ((flow === 'index' || flow === 'lid') && !(artikelInput.value || '').trim()) return 'Vul een artikelnummer in.';
    if (flow === 'lid' && !(lidInput.value || '').trim()) return 'Vul een lidnummer in.';
    if (flow === 'sectie' && !(sectieInput.value || '').trim()) return 'Vul een sectie-referentie in (bv. par1-1).';
    return null;
  }}

  function update() {{
    customRow.hidden = wetSel.value !== '__custom__';
    var flow = huidigeFlow();
    artikelRow.hidden = flow === 'sectie';
    lidRow.hidden = flow !== 'lid';
    sectieRow.hidden = flow !== 'sectie';

    var wet = huidigeWet();
    if (wet.bwb && wetSel.value !== '__custom__') vulDatalistVoor(wet.bwb);

    var commando = bouwCommando(flow, wet);
    var titel = bouwTitel(flow, wet);
    var body = bouwBody(flow, wet, commando);

    cmdInline.textContent = commando;
    titlePre.textContent = titel;
    bodyPre.textContent = body;

    var fout = valideer(flow, wet);
    if (fout) {{
      errorEl.textContent = fout;
      errorEl.hidden = false;
      openBtn.setAttribute('aria-disabled', 'true');
      openBtn.removeAttribute('href');
      statusEl.textContent = '';
      return;
    }}
    errorEl.hidden = true;
    var url = repoUrl + '/issues/new'
      + '?title=' + encodeURIComponent(titel)
      + '&body=' + encodeURIComponent(body)
      + '&labels=' + encodeURIComponent(label);
    openBtn.setAttribute('href', url);
    openBtn.setAttribute('aria-disabled', 'false');
    statusEl.textContent = 'Klaar om in te dienen.';
  }}

  form.addEventListener('input', update);
  form.addEventListener('change', update);
  openBtn.addEventListener('click', function(e) {{
    if (openBtn.getAttribute('aria-disabled') === 'true') {{
      e.preventDefault();
    }}
  }});
  update();

  // ---- Recente verzoeken (no-backend) ----
  var hint = document.getElementById('recentRequestsHint');
  var list = document.getElementById('recentRequests');
  fetch({json.dumps(api_url)}, {{ headers: {{ 'Accept': 'application/vnd.github+json' }} }})
    .then(function(r) {{ if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }})
    .then(function(issues) {{
      issues = (issues || []).filter(function(i) {{ return !i.pull_request; }});
      if (!issues.length) {{ hint.textContent = 'Nog geen verzoeken ingediend.'; return; }}
      list.innerHTML = '';
      issues.forEach(function(i) {{
        var li = document.createElement('li');
        var a = document.createElement('a');
        a.href = i.html_url;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.className = 'item-title';
        a.textContent = '#' + i.number + ' — ' + i.title;
        var badge = document.createElement('span');
        badge.className = 'badge badge-' + (i.state === 'open' ? 'concept' : 'definitief');
        badge.textContent = i.state;
        li.appendChild(a);
        li.appendChild(document.createTextNode(' '));
        li.appendChild(badge);
        list.appendChild(li);
      }});
      hint.style.display = 'none';
      list.style.display = 'block';
    }})
    .catch(function() {{ hint.textContent = 'Kon recente verzoeken niet ophalen.'; }});
}})();
</script>"""


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def gen_start_annotatie(out: Path, indices: list, annotaties: list) -> None:
    artikelen_per_wet = _bestaande_artikelen(indices, annotaties)
    body = (
        '<h1>Annotatie starten</h1>\n'
        '<p class="subtitle">Vraag een AI-ondersteunde annotatie aan via een GitHub-issue. '
        'De maker keurt elk verzoek handmatig goed voordat er API-tokens worden verbruikt.</p>\n'
        + _uitleg_html()
        + '<div class="dash-grid" style="grid-template-columns:1fr 1fr;gap:1.5rem">\n'
        + _form_html()
        + _preview_card_html()
        + '</div>\n'
        + _status_widget_html()
    )
    extra = _script_js(json.dumps(artikelen_per_wet, ensure_ascii=False, sort_keys=True), API_URL)
    schrijf_html(
        out,
        "start_annotatie.html",
        "Annotatie starten | Belastingdienst",
        body,
        active="annotatie starten",
        extra_scripts=extra,
        description="Dien een annotatieverzoek in voor de Rechtsgraaf — opent een GitHub-issue die na goedkeuring door de maker door Claude wordt uitgevoerd.",
    )
