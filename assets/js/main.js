/* Art Gallery Tolstoy — рыба. Прогрессивное улучшение: без JS контент виден. */
document.documentElement.classList.add('js');

(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var touch = window.matchMedia('(pointer: coarse)').matches;

  /* ---- Lenis плавный скролл (выкл. на touch и reduced-motion) ---- */
  if (window.Lenis && !reduce && !touch) {
    var lenis = new Lenis({ duration: 1.1, smoothWheel: true });
    function raf(t) { lenis.raf(t); requestAnimationFrame(raf); }
    requestAnimationFrame(raf);
    if (window.ScrollTrigger) lenis.on('scroll', ScrollTrigger.update);
  }

  /* ---- header: прозрачный над героем -> плотный при скролле ---- */
  var header = document.getElementById('siteHeader');
  var hero = document.querySelector('.hero, .artist-hero, .page-head');
  function onScroll() {
    var threshold = hero ? hero.offsetHeight - 90 : 60;
    if (window.scrollY > threshold) header.classList.add('solid');
    else header.classList.remove('solid');
  }
  // страницы без тёмного героя (page-head на белом) — сразу плотный header
  if (hero && hero.classList.contains('page-head')) header.classList.add('solid');
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---- мобильное меню ---- */
  var burger = document.getElementById('burger');
  var menu = document.getElementById('mobileMenu');
  if (burger) burger.addEventListener('click', function () {
    burger.classList.toggle('open');
    menu.classList.toggle('open');
    document.body.style.overflow = menu.classList.contains('open') ? 'hidden' : '';
    header.classList.add('solid');
  });

  /* ---- анимации: вход героя, параллакс, каскадный reveal ---- */
  var canAnimate = window.gsap && window.ScrollTrigger && !reduce;
  if (canAnimate) gsap.registerPlugin(ScrollTrigger);

  if (canAnimate) {
    // вход шапки
    gsap.from('#siteHeader .hd-inner', { y: -22, autoAlpha: 0, duration: .7, ease: 'power2.out', clearProps: 'all' });

    // каскадный вход первого экрана (герой / шапка страницы)
    var introSel = ['.hero-kicker', '.hero-title', '.hero-sub', '.hero .btn',
                    '.ah-years', '.ah-name', '.ah-en',
                    '.ph-kicker', '.page-head h1', '.filters'];
    var intro = introSel.map(function (s) { return document.querySelector(s); }).filter(Boolean);
    if (intro.length) {
      gsap.from(intro, {
        y: 34, autoAlpha: 0, duration: .9, ease: 'power3.out',
        stagger: .12, delay: .15, clearProps: 'all'
      });
    }

    // лёгкий параллакс фоновой работы в герое (scale даёт запас, чтобы не оголялись края)
    var heroEl = document.querySelector('.hero, .artist-hero');
    var heroBg = heroEl && heroEl.querySelector('.hero-bg img, .ah-img img');
    if (heroEl && heroBg) {
      gsap.set(heroBg, { scale: 1.12 });
      gsap.fromTo(heroBg, { yPercent: -4 }, {
        yPercent: 4, ease: 'none',
        scrollTrigger: { trigger: heroEl, start: 'top top', end: 'bottom top', scrub: true }
      });
    }
  }

  /* ---- reveal при скролле: IntersectionObserver + каскад внутри пачки ----
     Нарочно НЕ на ScrollTrigger: показ контента не должен зависеть от rAF,
     а IO не боится сдвигов layout от lazy-картинок. */
  var reveals = [].slice.call(document.querySelectorAll('.reveal'));
  if (reduce || !('IntersectionObserver' in window)) {
    reveals.forEach(function (el) { el.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      var i = 0;
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target;
        el.style.transitionDelay = Math.min(i * 70, 420) + 'ms'; // ступенька 70мс, потолок 420
        el.classList.add('in');
        el.addEventListener('transitionend', function te() {
          el.style.transitionDelay = '';
          el.removeEventListener('transitionend', te);
        });
        io.unobserve(el);
        i++;
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    reveals.forEach(function (el) { io.observe(el); });
  }

  /* ---- фильтр коллекции ---- */
  var filters = document.getElementById('filters');
  if (filters) {
    filters.addEventListener('click', function (e) {
      var b = e.target.closest('.filter'); if (!b) return;
      filters.querySelectorAll('.filter').forEach(function (x) { x.classList.remove('active'); });
      b.classList.add('active');
      var f = b.getAttribute('data-f');
      document.querySelectorAll('#collGrid .tile').forEach(function (t) {
        t.classList.toggle('hide', f !== 'all' && t.getAttribute('data-artist') !== f);
      });
      if (window.ScrollTrigger) ScrollTrigger.refresh();
    });
  }

  /* ---- lightbox ---- */
  var tiles = [].slice.call(document.querySelectorAll('.tile[data-full]'));
  if (tiles.length) {
    var lb = document.createElement('div');
    lb.className = 'lb';
    lb.innerHTML =
      '<button class="lb-close" aria-label="Закрыть">&times;</button>' +
      '<button class="lb-nav lb-prev" aria-label="Назад">&#8249;</button>' +
      '<button class="lb-nav lb-next" aria-label="Вперёд">&#8250;</button>' +
      '<img alt=""><div class="lb-cap"><div class="lc-title"></div><div class="lc-meta"></div></div>';
    document.body.appendChild(lb);
    var lbImg = lb.querySelector('img'),
        lbT = lb.querySelector('.lc-title'),
        lbM = lb.querySelector('.lc-meta');
    var cur = 0;
    function show(i) {
      var visible = tiles.filter(function (t) { return !t.classList.contains('hide'); });
      if (!visible.length) return;
      cur = (i + visible.length) % visible.length;
      var t = visible[cur];
      lbImg.src = t.getAttribute('data-full');
      lbT.textContent = t.getAttribute('data-title') || '';
      var meta = t.getAttribute('data-meta') || '';
      if (t.getAttribute('data-sold') === '1') meta += (meta ? ' · ' : '') + 'Продано';
      lbM.textContent = meta;
      lb._visible = visible;
    }
    function open(t) {
      var visible = tiles.filter(function (x) { return !x.classList.contains('hide'); });
      show(visible.indexOf(t));
      lb.classList.add('open'); document.body.style.overflow = 'hidden';
    }
    function close() { lb.classList.remove('open'); document.body.style.overflow = ''; }
    tiles.forEach(function (t) {
      t.addEventListener('click', function () { open(t); });
    });
    lb.querySelector('.lb-close').addEventListener('click', close);
    lb.querySelector('.lb-prev').addEventListener('click', function () { show(cur - 1); });
    lb.querySelector('.lb-next').addEventListener('click', function () { show(cur + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(cur - 1);
      if (e.key === 'ArrowRight') show(cur + 1);
    });
  }

  /* ---- переключение языка RU/EN (базовое) ---- */
  var langBtn = document.getElementById('langToggle');
  var lang = localStorage.getItem('agt-lang') || 'ru';
  function applyLang() {
    document.querySelectorAll('[data-ru][data-en]').forEach(function (el) {
      el.textContent = el.getAttribute('data-' + lang);
    });
    if (langBtn) langBtn.textContent = lang === 'ru' ? 'EN' : 'RU';
    document.documentElement.lang = lang;
  }
  applyLang();
  if (langBtn) langBtn.addEventListener('click', function () {
    lang = lang === 'ru' ? 'en' : 'ru';
    localStorage.setItem('agt-lang', lang);
    applyLang();
  });

  /* ---- видео-превью Башева: play при наведении ---- */
  document.querySelectorAll('.grid-video video').forEach(function (v) {
    v.addEventListener('mouseenter', function () { v.play().catch(function(){}); });
    v.addEventListener('mouseleave', function () { v.pause(); });
  });
})();
