// Activeert elementen met data-copy-target — klikt: tekst van target naar clipboard.
// Schrijfwijze in HTML:
//   <span id="regel-id">AR-...-1</span>
//   <button type="button" class="copy-btn" data-copy-target="#regel-id" aria-label="ID kopiëren">📋</button>
// Of: data-copy-text="letterlijk te kopiëren tekst"

(function () {
  function flash(btn, ok) {
    var orig = btn.getAttribute('data-orig-label') || btn.getAttribute('aria-label') || '';
    if (!btn.getAttribute('data-orig-label')) btn.setAttribute('data-orig-label', orig);
    btn.classList.add(ok ? 'copy-ok' : 'copy-err');
    btn.setAttribute('aria-label', ok ? 'Gekopieerd' : 'Kopiëren mislukt');
    var sr = btn.querySelector('.copy-status');
    if (sr) sr.textContent = ok ? 'Gekopieerd' : 'Mislukt';
    setTimeout(function () {
      btn.classList.remove('copy-ok', 'copy-err');
      btn.setAttribute('aria-label', orig);
      if (sr) sr.textContent = '';
    }, 1500);
  }

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('aria-hidden', 'true');
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }

  function copy(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).then(function () { return true; }, function () { return fallbackCopy(text); });
    }
    return Promise.resolve(fallbackCopy(text));
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-copy-target],[data-copy-text]');
    if (!btn) return;
    var text = btn.getAttribute('data-copy-text');
    if (!text) {
      var sel = btn.getAttribute('data-copy-target');
      var target = sel ? document.querySelector(sel) : null;
      if (target) {
        text = target.value !== undefined ? target.value : target.textContent;
      }
    }
    if (!text) return;
    copy(String(text).trim()).then(function (ok) { flash(btn, ok); });
  });
})();
