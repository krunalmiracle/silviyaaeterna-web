/* Local preferences only. No tracking, external calls or content-dependent motion. */
(function () {
  'use strict';
  const root = document.documentElement;
  const menu = document.querySelector('.nav-more');
  let language = 'en';
  try {
    const saved = localStorage.getItem('sa-lang');
    if (saved === 'en' || saved === 'bg') language = saved;
  } catch (_) { /* Private browsing can deny storage. */ }

  function closeMenu(restoreFocus) {
    if (!menu || !menu.open) return;
    menu.open = false;
    if (restoreFocus) menu.querySelector('summary').focus();
  }
  function setLanguage(next) {
    language = next;
    root.lang = next;
    root.dataset.lang = next;
    document.querySelectorAll('[data-en][data-bg]').forEach(node => {
      node.textContent = node.dataset[next];
    });
    document.querySelectorAll('[data-alt-en][data-alt-bg]').forEach(node => {
      node.alt = node.getAttribute('data-alt-' + next);
    });
    document.querySelectorAll('[data-aria-en][data-aria-bg]').forEach(node => {
      node.setAttribute('aria-label', node.getAttribute('data-aria-' + next));
    });
    ['en', 'bg'].forEach(lang => {
      document.getElementById('lang-' + lang).setAttribute('aria-pressed', String(lang === next));
    });
    try { localStorage.setItem('sa-lang', next); } catch (_) { /* Nonessential. */ }
  }
  ['en', 'bg'].forEach(lang => {
    document.getElementById('lang-' + lang).addEventListener('click', () => setLanguage(lang));
  });
  setLanguage(language);

  if (menu) {
    menu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => closeMenu(false)));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') closeMenu(true);
    });
    document.addEventListener('click', event => {
      if (!menu.contains(event.target)) closeMenu(false);
    });
  }

  const links = [...document.querySelectorAll('[data-theme]')];
  function selectTheme(id, moveFocus) {
    const selected = links.find(link => link.dataset.theme === id);
    if (!selected) return;
    links.forEach(link => {
      if (link === selected) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
    const topic = document.getElementById(id);
    topic.querySelector('details').open = true;
    if (moveFocus) topic.focus({ preventScroll: true });
  }
  links.forEach(link => link.addEventListener('click', () => selectTheme(link.dataset.theme, true)));
  window.addEventListener('hashchange', () => selectTheme(location.hash.slice(1), false));
  selectTheme(location.hash.slice(1), false);
})();
