/* ============================================================
   Ampbio — Home behaviours
   Ported from the DCLogic class in Ampbio Home.dc.html
   ============================================================ */
(function () {
  'use strict';

  var root = document.getElementById('amp-root');
  if (!root) return;

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- mobile menu toggle ---- */
  var burger = document.getElementById('amp-burger');
  var panel = document.getElementById('amp-mobile-panel');
  if (burger && panel) {
    burger.addEventListener('click', function () {
      panel.classList.toggle('amp-open');
    });
    /* Delegated, so links injected later by the browse menu close the drawer
       too. The Products row and the branch rows only expand a submenu, so
       they must leave the drawer open. */
    panel.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a');
      if (!a || !panel.contains(a)) return;
      if (a.classList.contains('amp-mm-m') || a.classList.contains('amp-mm-toggle')) return;
      panel.classList.remove('amp-open');
    });
  }

  /* ---- Virongy browse menu ------------------------------------------
     The panel is ~41 KB of markup and is identical on every page, so it is
     not inlined: it is fetched from menu.html the first time someone opens
     the menu, and the browser caches it for the rest of the site. If the
     fetch fails nothing breaks - "Products" is still an ordinary link. */
  (function () {
    var mount = root.querySelector('.amp-mm-mount');
    var drawerLink = root.querySelector('.amp-mm-m');
    if (!mount && !drawerLink) return;

    var pending = null;

    /* menu.html sits next to app.js at the site root, but product pages live
       in virongy/ - so resolve it against this script's own URL rather than
       against the page. The ?v=<hash> is carried over so the fragment can
       never be served from cache against a newer stylesheet. */
    var menuURL = (function () {
      var s = document.currentScript ||
              document.querySelector('script[src*="app.js"]');
      var src = (s && s.src) || 'app.js';
      var m = /[?&]v=([0-9a-f]+)/.exec(src);
      try {
        return new URL('menu.html' + (m ? '?v=' + m[1] : ''), src).href;
      } catch (e) {
        return 'menu.html';
      }
    })();

    function load() {
      if (pending) return pending;
      pending = fetch(menuURL, { credentials: 'same-origin' })
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          return r.text();
        })
        .catch(function () { pending = null; return null; });
      return pending;
    }

    /* desktop: mount on first hover or keyboard focus */
    if (mount) {
      var wrap = mount.parentNode;
      var fill = function () {
        load().then(function (html) {
          if (!html || mount.firstChild) return;
          mount.innerHTML = html;
          mount.removeAttribute('hidden');
          bindToggles(mount, false);
        });
      };
      wrap.addEventListener('mouseenter', fill);
      wrap.addEventListener('focusin', fill);
    }

    /* drawer: build an accordion under the Products row */
    if (drawerLink) {
      var box = document.createElement('div');
      box.className = 'amp-mm-mobile';
      drawerLink.parentNode.insertBefore(box, drawerLink.nextSibling);
      var opened = false;
      drawerLink.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();           // do not let the drawer close itself
        if (!opened) {
          opened = true;
          load().then(function (html) {
            if (!html) { window.location.href = 'products.html'; return; }
            box.innerHTML = html;
            bindToggles(box, true);
          });
        } else {
          box.style.display = box.style.display === 'none' ? '' : 'none';
        }
      });
    }

    /* branch rows open their panel; on desktop CSS :hover already does it,
       so there a click should simply not jump to "#". */
    function bindToggles(scope, accordion) {
      scope.querySelectorAll('.amp-mm-toggle').forEach(function (a) {
        a.addEventListener('click', function (e) {
          e.preventDefault();
          if (!accordion) return;
          var li = a.parentNode;
          var open = li.classList.toggle('amp-open');
          a.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
      });
    }
  })();

  /* ---- scroll hint: smooth-scroll past the hero ---- */
  var hint = document.getElementById('amp-scroll-hint');
  function scrollDown() {
    var h = document.querySelector('.amp-hero');
    var y = h ? h.getBoundingClientRect().bottom + window.scrollY - 68 : window.innerHeight;
    window.scrollTo({ top: y, behavior: 'smooth' });
  }
  if (hint) {
    hint.addEventListener('click', scrollDown);
    hint.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); scrollDown(); }
    });
  }

  /* ---- hero video: force muted autoplay + hard loop ---- */
  var video = document.getElementById('amp-hero-video');
  if (video) {
    video.muted = true;
    video.loop = true;
    video.setAttribute('muted', '');
    video.play().catch(function () {});
    video.addEventListener('ended', function () { video.currentTime = 0; video.play().catch(function () {}); });
  }

  /* ---- header shadow on scroll ---- */
  var header = root.querySelector('header');
  function onScroll() {
    if (!header) return;
    if (window.scrollY > 20) header.classList.add('amp-scrolled');
    else header.classList.remove('amp-scrolled');
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (reduce) return;

  /* ---- reveal each SECTION as a whole block when it scrolls into view ---- */
  var sections = Array.prototype.slice.call(root.querySelectorAll('section, footer'));
  sections.forEach(function (sec) {
    if (sec.classList.contains('amp-hero')) return; // hero stays visible

    var promo = sec.querySelector('.amp-promo');
    if (promo) {
      // reveal the two promo cards individually with a stagger
      Array.prototype.slice.call(promo.children).forEach(function (card, i) {
        card.classList.add('amp-reveal');
        card.dataset.ampDelay = String(i * 200);
      });
      return;
    }

    var journey = sec.querySelector('.amp-journey');
    if (journey) {
      sec.classList.add('amp-reveal'); // eyebrow + heading fade with the block
      Array.prototype.slice.call(journey.children).forEach(function (step, i) {
        step.classList.add('amp-reveal');
        step.dataset.ampDelay = String(150 + i * 130);
      });
      return;
    }

    sec.classList.add('amp-reveal');
  });

  function reveal(el) {
    if (el.dataset.ampDelay) el.style.animationDelay = el.dataset.ampDelay + 'ms';
    el.classList.add('amp-in');
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { reveal(e.target); io.unobserve(e.target); }
    });
  }, { threshold: 0.14, rootMargin: '0px 0px -12% 0px' });

  root.querySelectorAll('.amp-reveal').forEach(function (el) { io.observe(el); });

  // immediate reveal for sections already in view on load
  requestAnimationFrame(function () {
    root.querySelectorAll('.amp-reveal:not(.amp-in)').forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.top < window.innerHeight * 0.85 && r.bottom > 0) { reveal(el); io.unobserve(el); }
    });
  });

  // safety net: never leave content hidden
  setTimeout(function () {
    root.querySelectorAll('.amp-reveal:not(.amp-in)').forEach(reveal);
  }, 5000);
})();
