// Shared client-side filter voor lijstpagina's (begrippen, regels, annotaties, kwaliteit).
// Configuratie via data-attributen op het input-element:
//   data-list="#itemList"           CSS-selector voor de lijst-container
//   data-source="data/foo.json"     URL naar JSON-array met records die een veld "id" hebben
//   data-fields="titel,definitie"   komma-gescheiden velden om te indexeren
//   data-status="#filterStatus"     selector van de aria-live status-span (optioneel)
//   data-empty="#filterEmpty"       selector van de empty-state container (optioneel)
//   data-inline="json"              JSON-array direct in het script-tag (bypass fetch)
//
// Vereist: MiniSearch globaal geladen.

(function () {
  function init(input) {
    if (!input || input.dataset.filterInit) return;
    input.dataset.filterInit = '1';

    var listSel = input.getAttribute('data-list');
    var list = listSel ? document.querySelector(listSel) : null;
    if (!list) return;

    var source = input.getAttribute('data-source');
    var fields = (input.getAttribute('data-fields') || 'titel').split(',').map(function (s) { return s.trim(); });
    var statusEl = input.getAttribute('data-status') ? document.querySelector(input.getAttribute('data-status')) : null;
    var emptyEl = input.getAttribute('data-empty') ? document.querySelector(input.getAttribute('data-empty')) : null;
    var inlineId = input.getAttribute('data-inline');

    var ready = false;
    var items = Array.from(list.querySelectorAll('[data-id]'));
    var total = items.length;
    var ms = new MiniSearch({ fields: fields, storeFields: ['id'], searchOptions: { prefix: true, fuzzy: 0.2 } });

    function setStatus(text) {
      if (statusEl) statusEl.textContent = text;
    }

    function setEmpty(visible, message) {
      if (!emptyEl) return;
      emptyEl.classList.toggle('is-visible', !!visible);
      if (visible && message) {
        var titleEl = emptyEl.querySelector('.empty-state-title');
        if (titleEl) titleEl.textContent = message;
      }
    }

    function applyFilter() {
      var q = input.value.trim();
      if (!q || !ready) {
        items.forEach(function (li) { li.style.display = ''; });
        setStatus(ready ? total + ' resultaten' : 'Index laden...');
        setEmpty(false);
        return;
      }
      var matches = new Set(ms.search(q).map(function (r) { return r.id; }));
      var shown = 0;
      items.forEach(function (li) {
        var visible = matches.has(li.getAttribute('data-id'));
        li.style.display = visible ? '' : 'none';
        if (visible) shown++;
      });
      if (shown === 0) {
        setStatus('Geen resultaten voor "' + q + '"');
        setEmpty(true, 'Geen resultaten voor "' + q + '"');
      } else {
        setStatus(shown + ' van ' + total + ' resultaten');
        setEmpty(false);
      }
    }

    function loadAndIndex(data) {
      ms.addAll(data);
      ready = true;
      input.removeAttribute('aria-busy');
      applyFilter();
    }

    input.setAttribute('aria-busy', 'true');
    setStatus('Index laden...');

    if (inlineId) {
      var script = document.getElementById(inlineId);
      try { loadAndIndex(JSON.parse(script.textContent)); }
      catch (e) { setStatus('Fout bij laden index.'); }
    } else if (source) {
      fetch(source).then(function (r) { return r.json(); }).then(loadAndIndex).catch(function () {
        setStatus('Fout bij laden index.');
        input.removeAttribute('aria-busy');
      });
    }

    var t;
    input.addEventListener('input', function () {
      clearTimeout(t);
      t = setTimeout(applyFilter, 180);
    });
  }

  function boot() {
    document.querySelectorAll('input[data-list][data-fields]').forEach(init);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
