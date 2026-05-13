from sitegen.html import schrijf_html


def gen_search(out: Path, begrippen: list, annotaties: list, regels: list):
    body = f"""<h1>Zoeken</h1>
<label for="searchInput" class="sr-only">Zoekterm</label>
<input type="text" class="search-input" id="searchInput" placeholder="Zoek in begrippen, annotaties en regels..." autofocus>
<div class="search-filters" id="searchFilters">
  <span class="filter-chip active" data-type="all">Alle</span>
  <span class="filter-chip" data-type="Begrip">Begrippen</span>
  <span class="filter-chip" data-type="Annotatie">Annotaties</span>
  <span class="filter-chip" data-type="Regel">Regels</span>
</div>
<div id="searchResults"></div>
<script src="https://cdn.jsdelivr.net/npm/minisearch@7/dist/umd/index.min.js"></script>
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
}});
function escHtml(s){{return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}}
document.querySelectorAll('.filter-chip').forEach(function(chip){{
  chip.addEventListener('click',function(){{
    document.querySelectorAll('.filter-chip').forEach(function(c){{c.classList.remove('active')}});
    this.classList.add('active');
    currentFilter = this.getAttribute('data-type');
    doSearch();
  }});
}});
function doSearch(){{
  var q = document.getElementById('searchInput').value.trim();
  var out = document.getElementById('searchResults');
  out.innerHTML = '';
  if(q.length < 2){{out.innerHTML='<p class="item-meta" style="padding:1rem 0">Typ minimaal 2 tekens om te zoeken</p>';return}}
  if(!dataReady){{out.innerHTML='<p class="item-meta" style="padding:1rem 0">Data wordt geladen... probeer opnieuw.</p>';return}}
  var results = miniSearch.search(q);
  if(currentFilter !== 'all') results = results.filter(function(r){{return r.type === currentFilter}});
  if(results.length === 0){{out.innerHTML='<div class="no-results">Geen resultaten voor "'+escHtml(q)+'"</div>';return}}
  out.innerHTML = '<div style="font-size:0.85rem;color:var(--text-muted);margin-bottom:0.5rem">'+results.length+' resultaten</div>';
  var html='';
  results.slice(0,50).forEach(function(d){{
    var rawExcerpt = (d.tekst||'').length > 150 ? (d.tekst||'').substring(0,150)+'...' : (d.tekst||'');
    html += '<a class="search-result" href="'+escHtml(d.url)+'">'+
      '<div class="search-result-title">'+escHtml(d.titel)+'</div>'+
      '<div class="search-result-excerpt">'+escHtml(rawExcerpt)+'</div>'+
      '<div class="search-result-meta"><span>Type: '+escHtml(d.type)+'</span>'+
      (d.jas_klasse?'<span>JAS: '+escHtml(d.jas_klasse)+'</span>':'')+'</div></a>';
  }});
  out.innerHTML += html;
}}
var _st;document.getElementById('searchInput').addEventListener('input',function(){{clearTimeout(_st);_st=setTimeout(doSearch,200)}});
</script>"""
    schrijf_html(out, "search.html", "Zoeken | Belastingdienst", body, active="zoeken")
