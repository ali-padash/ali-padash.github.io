// Light/dark toggle (remembers the visitor's choice) and spam-resistant email links.
(function () {
  var root = document.documentElement;
  var media = window.matchMedia('(prefers-color-scheme: dark)');

  function current() {
    return root.dataset.theme || (media.matches ? 'dark' : 'light');
  }

  var toggle = document.querySelector('.theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = current() === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      try { localStorage.setItem('theme', next); } catch (e) { /* storage unavailable */ }
    });
  }

  // The address is assembled here so it never appears whole in the HTML.
  document.querySelectorAll('.js-email').forEach(function (a) {
    var address = a.dataset.u + '@' + a.dataset.d;
    a.href = 'mailto:' + address;
    if (a.classList.contains('js-email-text')) a.textContent = address;
  });
})();
