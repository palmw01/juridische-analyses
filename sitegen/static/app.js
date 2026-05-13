document.addEventListener('DOMContentLoaded',function(){
  var toggle=document.getElementById('darkToggle'),root=document.documentElement;
  var SVG_MOON='<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  var SVG_SUN='<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>';
  function setTheme(t){
    root.setAttribute('data-theme',t);localStorage.setItem('theme',t);
    if(toggle){
      var ic=toggle.querySelector('.dt-icon');
      if(ic)ic.innerHTML=t==='dark'?SVG_MOON:SVG_SUN;
    }
  }
  var stored=localStorage.getItem('theme');
  if(stored){setTheme(stored)}else if(window.matchMedia&&window.matchMedia('(prefers-color-scheme:dark)').matches){setTheme('dark')}else{setTheme('light')}
  if(toggle)toggle.addEventListener('click',function(){setTheme(root.getAttribute('data-theme')==='dark'?'light':'dark')});
  window.matchMedia('(prefers-color-scheme:dark)').addEventListener('change',function(e){if(!localStorage.getItem('theme'))setTheme(e.matches?'dark':'light')});
  var hamburger=document.getElementById('hamburger'),navLinks=document.querySelector('.nav-links');
  if(hamburger&&navLinks){
    function setMenu(open){
      hamburger.setAttribute('aria-expanded',String(open));
      hamburger.setAttribute('aria-label',open?'Menu sluiten':'Menu openen');
      hamburger.classList.toggle('open',open);
      navLinks.classList.toggle('open',open);
      var lbl=hamburger.querySelector('.hamburger-label');
      if(lbl)lbl.textContent=open?'Sluit':'Menu';
    }
    hamburger.addEventListener('click',function(){
      setMenu(hamburger.getAttribute('aria-expanded')!=='true');
    });
    navLinks.querySelectorAll('a').forEach(function(l){l.addEventListener('click',function(){setMenu(false)})});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&navLinks.classList.contains('open')){setMenu(false);hamburger.focus()}});
    document.addEventListener('click',function(e){if(navLinks.classList.contains('open')&&!navLinks.contains(e.target)&&!hamburger.contains(e.target)){setMenu(false)}});
  }
});
