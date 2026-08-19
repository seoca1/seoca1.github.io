/* Dark mode toggle — persists to localStorage */
(function() {
  'use strict';
  document.addEventListener('DOMContentLoaded', function() {
    var btn = document.querySelector('[data-theme-toggle]');
    if (!btn) return;
    btn.addEventListener('click', function() {
      var root = document.documentElement;
      var current = root.getAttribute('data-theme');
      var isDark = current === 'dark';
      // If no explicit preference and prefers-color-scheme:dark is set, also treat as dark
      if (current === null && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        isDark = true;
      }
      var next = isDark ? 'light' : 'dark';
      if (next === 'dark') {
        root.setAttribute('data-theme', 'dark');
      } else {
        root.setAttribute('data-theme', 'light');
      }
      try { localStorage.setItem('lb-theme', next); } catch (e) {}
    });
  });
})();
