/* Intersection-Observer-driven fade-in for `.lb-fade-in` elements. */
(function() {
  'use strict';
  if (!('IntersectionObserver' in window)) {
    // Fallback: show everything immediately if IO unsupported.
    document.querySelectorAll('.lb-fade-in').forEach(function(el) {
      el.classList.add('lb-visible');
    });
    return;
  }
  document.addEventListener('DOMContentLoaded', function() {
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('lb-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
    document.querySelectorAll('.lb-fade-in').forEach(function(el) { observer.observe(el); });
  });
})();
