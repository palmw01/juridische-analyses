from pathlib import Path

from sitegen.html import schrijf_html


def gen_search(out: Path, begrippen: list, annotaties: list, regels: list):
    body = f"""<h1>Zoeken</h1>
<label for="searchInput" class="sr-only">Zoekterm</label>
<input type="search" class="search-input" id="searchInput" placeholder="Zoek in begrippen, annotaties en regels...">
<div class="search-filters" id="searchFilters" role="group" aria-label="Filter op type">
  <button type="button" class="filter-chip active" data-type="all" aria-pressed="true">Alle</button>
  <button type="button" class="filter-chip" data-type="Begrip" aria-pressed="false">Begrippen</button>
  <button type="button" class="filter-chip" data-type="Annotatie" aria-pressed="false">Annotaties</button>
  <button type="button" class="filter-chip" data-type="Regel" aria-pressed="false">Regels</button>
</div>
<span id="searchStatus" class="result-status" role="status" aria-live="polite"></span>
<div id="searchResults"></div>
<script src="https://cdn.jsdelivr.net/npm/minisearch@7/dist/umd/index.min.js" integrity="sha384-9Eacb80ywplqCp0P/bR61+zYn5Pg2LmQ7T8rppdoKHcQMmXbRh1wHwRC8avUJvnz" crossorigin="anonymous"></script>
<script>
var currentFilter = 'all';
var dataReady = false;
var miniSearch = new MiniSearch({{
  fields: ['titel', 'definitie', 'wetstekst', 'formele_regel', 'toelichting'],
  storeFields: ['titel', 'url', 'type', 'jas_klasse', 'soort', 'tekst'],
  searchOptions: {{ prefix: true, fuzzy: 0.2 }}
}});
Promise.all([
  fetch('data/begrippen.json').then(function(r){{return r.json()}}),
  fetch('data/annotaties.json').then(function(r){{return r.json()}}),
  fetch('data/regels.json').then(function(r){{return r.json()}})
]).then(function(results){{
  var all = results[0].concat(results[1], results[2]);
  miniSearch.addAll(all);
  dataReady = true;
  doSearch();
}});
function escHtml(s){{return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}}
function setStatus(t){{document.getElementById('searchStatus').textContent = t || '';}}
document.querySelectorAll('#searchFilters .filter-chip').forEach(function(chip){{
  chip.addEventListener('click',function(){{
    document.querySelectorAll('#searchFilters .filter-chip').forEach(function(c){{
      c.classList.remove('active');
      c.setAttribute('aria-pressed','false');
    }});
    this.classList.add('active');
    this.setAttribute('aria-pressed','true');
    currentFilter = this.getAttribute('data-type');
    doSearch();
  }});
}});
function doSearch(){{
  var q = document.getElementById('searchInput').value.trim();
  var out = document.getElementById('searchResults');
  out.innerHTML = '';
  if(q.length < 2){{out.innerHTML='<p class="item-meta" style="padding:1rem 0">Typ minimaal 2 tekens om te zoeken</p>';setStatus('');return}}
  if(!dataReady){{out.innerHTML='<p class="item-meta" style="padding:1rem 0">Data wordt geladen... probeer opnieuw.</p>';setStatus('Index laden...');return}}
  var results = miniSearch.search(q);
  if(currentFilter !== 'all') results = results.filter(function(r){{return r.type === currentFilter}});
  if(results.length === 0){{
    out.innerHTML='<div class="no-results">Geen resultaten voor "'+escHtml(q)+'"</div>';
    setStatus('Geen resultaten voor "'+q+'"');
    return;
  }}
  var shown=Math.min(results.length,50);
  var countTxt=results.length>50?shown+' van '+results.length+' resultaten':results.length+' resultaten';
  setStatus(countTxt);
  var html='';
  results.slice(0,50).forEach(function(d){{
    var rawExcerpt = (d.tekst||'').length > 150 ? (d.tekst||'').substring(0,150)+'...' : (d.tekst||'');
    html += '<a class="search-result" href="'+escHtml(d.url)+'">'+
      '<div class="search-result-title">'+escHtml(d.titel)+'</div>'+
      '<div class="search-result-excerpt">'+escHtml(rawExcerpt)+'</div>'+
      '<div class="search-result-meta"><span>Type: '+escHtml(d.type)+'</span>'+
      (d.jas_klasse?'<span>JAS: '+escHtml(d.jas_klasse)+'</span>':'')+'</div></a>';
  }});
  out.innerHTML = html;
}}
var _st;document.getElementById('searchInput').addEventListener('input',function(){{clearTimeout(_st);_st=setTimeout(doSearch,200)}});
</script>"""
    schrijf_html(out, "search.html", "Zoeken | Belastingdienst", body, active="zoeken")
