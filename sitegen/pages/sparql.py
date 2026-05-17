import json
from pathlib import Path

from sitegen.html import schrijf_html

LOCAL_BUNDLE = "js/comunica.min.js"
ESM_CDN = "https://esm.sh/@comunica/query-sparql"

BUILTIN_QUERIES: list[tuple[str, str]] = [
    ("Aantal begrippen per JAS-klasse",
     "PREFIX jas: <http://regels.overheid.nl/jas/ontology#>\n"
     "SELECT ?klasse (COUNT(?s) AS ?aantal)\n"
     "WHERE { ?s jas:jasKlasse ?klasse . }\n"
     "GROUP BY ?klasse\n"
     "ORDER BY DESC(?aantal)"),
    ("Alle begrippen met definitie",
     "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>\n"
     "SELECT ?s ?label ?definitie\n"
     "WHERE {\n  ?s skos:prefLabel ?label .\n  ?s skos:definition ?definitie .\n}\n"
     "ORDER BY ?label"),
    ("Hi\u00ebrarchische relaties (is-een)",
     "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>\n"
     "SELECT ?smal ?label_smal ?breed ?label_breed\n"
     "WHERE {\n  ?smal skos:broader ?breed .\n"
     "  ?smal skos:prefLabel ?label_smal .\n"
     "  ?breed skos:prefLabel ?label_breed .\n}\n"
     "ORDER BY ?label_breed"),
    ("Begrippen zonder definitie",
     "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>\n"
     "SELECT ?s ?label\n"
     "WHERE {\n  ?s a skos:Concept .\n  ?s skos:prefLabel ?label .\n"
     "  FILTER NOT EXISTS { ?s skos:definition ?def }\n}"),
    ("Alle JAS-relaties (heeft / leidt-tot)",
     "PREFIX jas: <http://regels.overheid.nl/jas/ontology#>\n"
     "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>\n"
     "SELECT ?van_label ?predikaat ?naar_label\n"
     "WHERE {\n  VALUES ?predikaat { jas:heeft jas:leidtTot }\n"
     "  ?van ?predikaat ?naar .\n  ?van skos:prefLabel ?van_label .\n"
     "  ?naar skos:prefLabel ?naar_label .\n}"),
    ("Wees-begrippen (geen enkele relatie)",
     "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>\n"
     "PREFIX jas: <http://regels.overheid.nl/jas/ontology#>\n"
     "SELECT ?label\n"
     "WHERE {\n  ?s a skos:Concept .\n  ?s skos:prefLabel ?label .\n"
     "  FILTER NOT EXISTS { ?s skos:broader ?o }\n"
     "  FILTER NOT EXISTS { ?i skos:broader ?s }\n"
     "  FILTER NOT EXISTS { ?s jas:heeft ?o2 }\n"
     "  FILTER NOT EXISTS { ?i2 jas:heeft ?s }\n"
     "  FILTER NOT EXISTS { ?s jas:leidtTot ?o3 }\n"
     "  FILTER NOT EXISTS { ?i3 jas:leidtTot ?s }\n}"),
]

BUTTONS_HTML = "".join(
    f'<button type="button" class="filter-chip" data-query="{i}">'
    f'{label}</button>\n'
    for i, (label, _) in enumerate(BUILTIN_QUERIES)
)

QUERIES_JS = json.dumps([q for _, q in BUILTIN_QUERIES])


def gen_sparql(out: Path):
    body = f"""<h1>SPARQL-query</h1>
<p class="subtitle">Bevraag het kennismodel met SPARQL. Data wordt geladen uit <code>data/begrippen.ttl</code>. Draai <code>make export-rdf</code> als het bestand ontbreekt.</p>

<div class="card">
  <div class="card-title">Voorbeeldqueries</div>
  <div class="search-filters" style="margin-bottom:0">
    {BUTTONS_HTML}
  </div>
</div>

<div class="card">
  <div class="card-title">
    <label for="queryInput">Query</label>
    <button type="button" class="copy-btn" data-copy-target="#queryInput" aria-label="Query kopiëren" title="Query kopiëren">
      <svg class="copy-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
      <span class="copy-status" aria-hidden="true"></span>
    </button>
  </div>
  <textarea id="queryInput" class="search-input" style="min-height:160px;font-family:var(--font-mono);font-size:0.85rem;padding:0.75rem 1rem;resize:vertical;line-height:1.5" placeholder="SELECT ?s ?p ?o WHERE {{ ?s ?p ?o }} LIMIT 10" aria-describedby="queryHint"></textarea>
  <span id="queryHint" class="sr-only">Tip: Ctrl+Enter voert de query uit.</span>
  <div style="display:flex;gap:0.75rem;flex-wrap:wrap;align-items:center">
    <button id="runBtn" class="btn-primary" type="button">&#9654; Uitvoeren</button>
    <button id="stopBtn" class="btn-secondary" type="button" style="display:none">&#9632; Stop</button>
    <span id="sparqlStatus" role="status" aria-live="polite" style="font-size:0.85rem;color:var(--text-muted)"></span>
  </div>
</div>

<div id="sparqlResults" style="display:none">
  <div class="card">
    <div class="card-title">Resultaten <span id="resultCount" style="font-weight:400;text-transform:none;letter-spacing:0"></span></div>
    <div class="table-scroll">
      <table class="ann-table" id="resultTable">
        <thead id="resultHead"></thead>
        <tbody id="resultBody"></tbody>
      </table>
    </div>
  </div>
</div>

<div id="sparqlError" style="display:none">
  <div class="card" style="border-left-color:var(--error)">
    <div class="card-title">Fout</div>
    <p id="errorText" style="color:var(--error);font-family:var(--font-mono);font-size:0.85rem"></p>
  </div>
</div>

<div id="sparqlLoading" style="display:none">
  <div class="card" style="text-align:center;padding:2rem">
    <p style="color:var(--text-muted)">Bezig met laden...</p>
  </div>
</div>

<div id="sparqlNoRdf" style="display:none">
  <div class="card" style="border-left-color:var(--warning)">
    <div class="card-title">Geen RDF-data</div>
    <p>Het bestand <code>data/begrippen.ttl</code> is niet gevonden. Draai eerst <code>make export-rdf</code> in de projectroot.</p>
  </div>
</div>

<script src="{LOCAL_BUNDLE}"></script>
<script>
var QUERIES = {QUERIES_JS};
var cancelled = false;
var engineLoading = false;

document.querySelectorAll('[data-query]').forEach(function(btn){{
  btn.addEventListener('click',function(){{
    var idx = parseInt(this.getAttribute('data-query'));
    document.getElementById('queryInput').value = QUERIES[idx];
    document.getElementById('queryInput').focus();
  }});
}});

function escHtml(s){{
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

function formatTerm(term){{
  if(!term) return '<em class="item-meta">\u2014</em>';
  var t = term.termType;
  var v = term.value;
  if(t === 'NamedNode'||t==='IRI') return '<code>'+escHtml(v)+'</code>';
  if(t === 'Literal') return '"'+escHtml(v)+'"'+(term.language?'@'+term.language:'');
  if(t === 'BlankNode') return '<em>_:'+escHtml(v)+'</em>';
  return escHtml(v);
}}

function hideStop() {{
  document.getElementById('stopBtn').style.display = 'none';
  document.getElementById('runBtn').style.display = 'inline-flex';
}}

async function getEngine() {{
  if (typeof Comunica !== 'undefined' && Comunica.QueryEngine) {{
    return new Comunica.QueryEngine();
  }}
  var mod = await import("{ESM_CDN}");
  return new mod.QueryEngine();
}}

document.getElementById('stopBtn').addEventListener('click', function() {{
  cancelled = true;
  if (engineLoading) {{
    document.getElementById('sparqlStatus').textContent = 'Stoppen na laden engine...';
  }} else {{
    document.getElementById('sparqlLoading').style.display = 'none';
    hideStop();
    document.getElementById('sparqlStatus').textContent = 'Gestopt';
  }}
}});

document.getElementById('runBtn').addEventListener('click', async function(){{
  var q = document.getElementById('queryInput').value.trim();
  if(!q) return;
  cancelled = false;
  var statusEl = document.getElementById('sparqlStatus');
  var resultsDiv = document.getElementById('sparqlResults');
  var errorDiv = document.getElementById('sparqlError');
  var loading = document.getElementById('sparqlLoading');
  var noRdf = document.getElementById('sparqlNoRdf');
  var headEl = document.getElementById('resultHead');
  var bodyEl = document.getElementById('resultBody');
  var countEl = document.getElementById('resultCount');
  resultsDiv.style.display = 'none';
  errorDiv.style.display = 'none';
  noRdf.style.display = 'none';
  loading.style.display = 'block';
  document.getElementById('stopBtn').style.display = 'inline-flex';
  document.getElementById('runBtn').style.display = 'none';
  statusEl.textContent = 'Engine laden...';

  var engine;
  try {{
    engineLoading = true;
    engine = await getEngine();
    engineLoading = false;
  }} catch(e) {{
    engineLoading = false;
    loading.style.display = 'none';
    hideStop();
    errorDiv.style.display = 'block';
    document.getElementById('errorText').textContent = 'Kon SPARQL-engine niet laden.\\n\\n' + (e&&e.message||String(e));
    statusEl.textContent = 'Fout bij laden engine';
    return;
  }}
  if(cancelled) {{ hideStop(); loading.style.display = 'none'; statusEl.textContent = 'Gestopt'; return; }}

  var ttlUrl = new URL('data/begrippen.ttl', window.location.href).href;
  statusEl.textContent = 'Query uitvoeren...';
  engine.queryBindings(q, {{
    sources: [ttlUrl]
  }}).then(function(bindingsStream){{
    return bindingsStream.toArray();
  }}).then(function(bindings){{
    if(cancelled) return;
    loading.style.display = 'none';
    if(bindings.length === 0){{
      headEl.innerHTML = '';
      bodyEl.innerHTML = '';
      countEl.textContent = '(0 resultaten)';
      resultsDiv.style.display = 'block';
      statusEl.textContent = 'Klaar (0 resultaten)';
      return;
    }}
    var vars = Array.from(bindings[0].keys());
    headEl.innerHTML = '<tr>' + vars.map(function(v){{return '<th>'+escHtml(v.value||v)+'</th>'}}).join('') + '</tr>';
    bodyEl.innerHTML = bindings.map(function(b){{
      return '<tr>' + vars.map(function(v){{
        var term = b.get(v);
        return '<td style="font-size:0.82rem;font-family:var(--font-mono);max-width:350px;overflow-wrap:break-word;word-break:break-word">'+formatTerm(term)+'</td>';
      }}).join('') + '</tr>';
    }}).join('');
    countEl.textContent = '('+bindings.length+' resultaten)';
    resultsDiv.style.display = 'block';
    statusEl.textContent = 'Klaar ('+bindings.length+' resultaten)';
  }}, function(err){{
    if(cancelled) return;
    loading.style.display = 'none';
    if(err && err.message && err.message.indexOf('404') >= 0 &&
        err.message.indexOf('begrippen.ttl') >= 0){{
      noRdf.style.display = 'block';
      statusEl.textContent = 'RDF niet gevonden';
    }} else {{
      errorDiv.style.display = 'block';
      document.getElementById('errorText').textContent = (err&&err.message)||String(err);
      statusEl.textContent = 'Fout';
    }}
  }}).catch(function(err){{
    if(cancelled) return;
    loading.style.display = 'none';
    errorDiv.style.display = 'block';
    document.getElementById('errorText').textContent = 'Onverwachte fout:\\n\\n' + (err&&err.message||String(err));
    statusEl.textContent = 'Fout';
  }}).then(function(){{
    hideStop();
  }});
}});

document.getElementById('queryInput').addEventListener('keydown',function(e){{
  if(e.key === 'Enter' && (e.ctrlKey || e.metaKey)){{
    e.preventDefault();
    document.getElementById('runBtn').click();
  }}
}});
</script>"""
    schrijf_html(out, "sparql.html", "SPARQL-query | Belastingdienst", body, active="sparql")
