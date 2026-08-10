/* Principia site behaviour. No dependencies, no build step. */
(function () {
  "use strict";

  // Mobile navigation
  var toggle = document.getElementById("nav-toggle");
  var links = document.getElementById("nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var open = links.getAttribute("data-open") === "true";
      links.setAttribute("data-open", String(!open));
      toggle.setAttribute("aria-expanded", String(!open));
    });
  }

  // The matrix scroll hint has done its job once the table has been scrolled.
  var scroller = document.getElementById("matrix-scroll");
  var hint = document.getElementById("matrix-hint");
  if (scroller && hint) {
    // On a wide screen the table fits, so the affordance would be a lie.
    if (scroller.scrollWidth <= scroller.clientWidth) hint.hidden = true;
    scroller.addEventListener("scroll", function once() {
      hint.hidden = true;
      scroller.removeEventListener("scroll", once);
    }, { passive: true });
  }

  // Screenshot lightbox. <dialog> gives us Esc and the backdrop for free.
  var dialog = document.getElementById("lightbox");
  var full = document.getElementById("lightbox-img");
  if (dialog && full && typeof dialog.showModal === "function") {
    document.querySelectorAll("[data-lightbox]").forEach(function (img) {
      img.addEventListener("click", function () {
        full.removeAttribute("srcset");
        full.src = img.getAttribute("data-lightbox");
        full.alt = img.getAttribute("alt") || "";
        dialog.showModal();
      });
    });
    dialog.querySelector(".lightbox__close").addEventListener("click", function () {
      dialog.close();
    });
    dialog.addEventListener("click", function (event) {
      if (event.target === dialog) dialog.close();
    });
  }
})();
