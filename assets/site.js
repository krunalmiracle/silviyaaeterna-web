/* Silviya Aeterna. Language toggle, mobile menu notes, and reveal motion.
   No network calls, no tracking, no storage beyond the language preference. */
(function () {
  "use strict";

  var root = document.documentElement;
  var KEY = "sa-lang";
  var lang = "en";

  root.classList.add("js");

  try {
    var saved = window.localStorage.getItem(KEY);
    if (saved === "bg" || saved === "en") lang = saved;
  } catch (err) {
    /* storage unavailable, English stays */
  }

  function pick(el, attr) {
    var value = el.getAttribute(attr);
    if (value !== null) el.textContent = value;
  }

  function applyText() {
    var nodes = document.querySelectorAll("[data-bg][data-en]");
    for (var i = 0; i < nodes.length; i++) {
      pick(nodes[i], lang === "bg" ? "data-bg" : "data-en");
    }
    var imgs = document.querySelectorAll("[data-alt-bg][data-alt-en]");
    for (var j = 0; j < imgs.length; j++) {
      imgs[j].setAttribute("alt", lang === "bg" ? imgs[j].getAttribute("data-alt-bg") : imgs[j].getAttribute("data-alt-en"));
    }
    var labelled = document.querySelectorAll("[data-aria-bg][data-aria-en]");
    for (var k = 0; k < labelled.length; k++) {
      labelled[k].setAttribute("aria-label", lang === "bg" ? labelled[k].getAttribute("data-aria-bg") : labelled[k].getAttribute("data-aria-en"));
    }
    var title = document.querySelector("title");
    if (title && title.getAttribute("data-bg")) {
      title.textContent = lang === "bg" ? title.getAttribute("data-bg") : title.getAttribute("data-en");
    }
  }

  function applyChrome() {
    root.setAttribute("lang", lang);
    root.setAttribute("data-lang", lang);
    var en = document.getElementById("lang-en");
    var bg = document.getElementById("lang-bg");
    if (en && bg) {
      en.setAttribute("aria-pressed", lang === "en" ? "true" : "false");
      bg.setAttribute("aria-pressed", lang === "bg" ? "true" : "false");
    }
    try {
      window.localStorage.setItem(KEY, lang);
    } catch (err) {
      /* ignore */
    }
  }

  function setLang(next) {
    lang = next;
    applyText();
    applyChrome();
  }

  /* language attribute before first paint; text after the DOM exists */
  applyChrome();

  function revealAll(items) {
    for (var i = 0; i < items.length; i++) items[i].classList.add("is-in");
  }

  document.addEventListener("DOMContentLoaded", function () {
    applyText();

    var en = document.getElementById("lang-en");
    var bg = document.getElementById("lang-bg");
    if (en) en.addEventListener("click", function () { setLang("en"); });
    if (bg) bg.addEventListener("click", function () { setLang("bg"); });

    var items = Array.prototype.slice.call(document.querySelectorAll("[data-reveal]"));
    var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var supportsObserver = "IntersectionObserver" in window;

    if (reduced || !supportsObserver) {
      revealAll(items);
      return;
    }

    var observer = new IntersectionObserver(
      function (entries) {
        for (var i = 0; i < entries.length; i++) {
          if (entries[i].isIntersecting) {
            entries[i].target.classList.add("is-in");
            observer.unobserve(entries[i].target);
          }
        }
      },
      { rootMargin: "0px 0px -6% 0px", threshold: 0.06 }
    );

    for (var i = 0; i < items.length; i++) observer.observe(items[i]);

    /* safety net: nothing stays hidden if the observer never fires */
    window.setTimeout(function () {
      for (var j = 0; j < items.length; j++) {
        if (!items[j].classList.contains("is-in")) {
          var box = items[j].getBoundingClientRect();
          if (box.top < window.innerHeight && box.bottom > 0) {
            items[j].classList.add("is-in");
            observer.unobserve(items[j]);
          }
        }
      }
    }, 2500);
  });
})();
