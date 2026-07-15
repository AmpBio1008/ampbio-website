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
    panel.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { panel.classList.remove('amp-open'); });
    });
  }

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
