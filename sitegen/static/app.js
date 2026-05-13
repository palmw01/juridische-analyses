document.addEventListener('DOMContentLoaded',function(){
  var toggle=document.getElementById('darkToggle'),root=document.documentElement;
  function setTheme(t){
    root.setAttribute('data-theme',t);localStorage.setItem('theme',t);
    if(toggle){
      var ic=toggle.querySelector('.dt-icon');
      if(ic)ic.textContent=t==='dark'?'\u263D':'\u2600';
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
