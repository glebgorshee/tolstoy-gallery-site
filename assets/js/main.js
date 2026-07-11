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

  /* ---- header: прозрачный над тёмным героем -> плотный при скролле ----
     На страницах с .page-head (белый фон) шапка плотная ВСЕГДА,
     иначе белый текст на белом = невидимо. */
  var header = document.getElementById('siteHeader');
  var hero = document.querySelector('.hero, .artist-hero');
  var alwaysSolid = !hero; // нет тёмного героя (page-head/обычная страница) → всегда solid
  var brandEl = document.querySelector('.brand');
  var isHome = !!document.querySelector('.hero'); // логотип в шапке прячем только на главной над героем
  function onScroll() {
    var solid;
    if (alwaysSolid) { header.classList.add('solid'); solid = true; }
    else {
      solid = window.scrollY > hero.offsetHeight - 90;   // проскроллен экран с видео
      header.classList.toggle('solid', solid);
    }
    // на главной логотип в шапке появляется только когда экран с видео проскроллен (шапка стала solid)
    if (isHome && brandEl) brandEl.classList.toggle('is-hidden', !solid);
  }
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

  /* ---- анимации ----
     Вход первого экрана — на чистом CSS (класс intro-anim + .ready),
     НЕ на GSAP: контент не должен зависеть от rAF-тикера (в фоне/headless он стопорится).
     GSAP оставляем только для параллакса — он ничего не прячет. */
  var canAnimate = window.gsap && window.ScrollTrigger && !reduce;
  if (canAnimate) gsap.registerPlugin(ScrollTrigger);

  if (!reduce) {
    // помечаем элементы первого экрана и запускаем каскад после отрисовки
    var introSel = ['.hero-logo', '.hero-sub', '.hero .btn',
                    '.ah-years', '.ah-name', '.ah-en',
                    '.ph-kicker', '.page-head h1', '.filters'];
    var intro = introSel.map(function (s) { return document.querySelector(s); }).filter(Boolean);
    intro.forEach(function (el, i) {
      el.classList.add('intro-anim');
      el.style.setProperty('--i', i);
    });
    // setTimeout, а не rAF: rAF стопорится в фоне/headless и оставил бы герой невидимым
    setTimeout(function () {
      intro.forEach(function (el) { el.classList.add('ready'); });
    }, 60);
  }

  if (canAnimate) {
    // лёгкий параллакс фоновой работы в герое (scale даёт запас, чтобы не оголялись края)
    var heroEl = document.querySelector('.hero, .artist-hero');
    var heroBg = heroEl && heroEl.querySelector('.hero-bg img, .hero-bg video, .ah-img img');
    if (heroEl && heroBg) {
      gsap.set(heroBg, { scale: 1.12 });
      gsap.fromTo(heroBg, { yPercent: -4 }, {
        yPercent: 4, ease: 'none',
        scrollTrigger: { trigger: heroEl, start: 'top top', end: 'bottom top', scrub: true }
      });
    }
  }

  /* ---- hero-видео: грузим источник под ширину экрана (desktop/mobile) ----
     autoplay-атрибута нет: src ставим из JS, поэтому мобилка НЕ качает тяжёлый desktop-файл.
     prefers-reduced-motion → видео не грузим вовсе, остаётся постер-кадр. */
  var heroVideo = document.getElementById('heroVideo');
  if (heroVideo && !reduce) {
    var hvMq = window.matchMedia('(max-width: 768px)');
    var hvLoaded = '';
    var tryPlay = function () {
      var p = heroVideo.play();
      if (p && p.catch) p.catch(function () {});   // отказ политики → попробуем ещё по событию/жесту
    };
    // добивка: любой первый жест пользователя запускает видео, если автоплей придержали
    var gestures = ['touchstart', 'pointerdown', 'click', 'scroll', 'keydown'];
    var onGesture = function () { tryPlay(); };
    gestures.forEach(function (ev) { window.addEventListener(ev, onGesture, { passive: true }); });
    heroVideo.addEventListener('playing', function () {   // заиграло → снимаем лишние слушатели
      gestures.forEach(function (ev) { window.removeEventListener(ev, onGesture, { passive: true }); });
    });
    // как только данных достаточно — стартуем, не дожидаясь полной загрузки
    heroVideo.addEventListener('loadeddata', tryPlay);
    heroVideo.addEventListener('canplay', tryPlay);
    var pickHero = function () {
      var want = hvMq.matches ? 'mobile' : 'desktop';
      if (want === hvLoaded) return;
      hvLoaded = want;
      var pos = heroVideo.getAttribute('data-poster-' + want);
      if (pos) heroVideo.poster = pos;
      heroVideo.muted = true;                 // iOS Safari: без явного mute muted-autoplay не стартует
      heroVideo.src = heroVideo.getAttribute('data-' + want);
      heroVideo.load();
      tryPlay();
    };
    pickHero();
    if (hvMq.addEventListener) hvMq.addEventListener('change', pickHero);
    else if (hvMq.addListener) hvMq.addListener(pickHero);
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
    var collEmpty = document.getElementById('collEmpty');
    var collEmptyLink = document.getElementById('collEmptyLink');
    filters.addEventListener('click', function (e) {
      var b = e.target.closest('.filter'); if (!b) return;
      filters.querySelectorAll('.filter').forEach(function (x) { x.classList.remove('active'); });
      b.classList.add('active');
      var f = b.getAttribute('data-f');
      var shown = 0;
      document.querySelectorAll('#collGrid .tile').forEach(function (t) {
        var hide = f !== 'all' && t.getAttribute('data-artist') !== f;
        t.classList.toggle('hide', hide);
        if (!hide) shown++;
      });
      // выбран художник, чьих работ ещё нет в коллекции → заглушка со ссылкой на его страницу
      if (collEmpty) {
        if (shown === 0 && f !== 'all') {
          if (collEmptyLink) collEmptyLink.href = 'artist-' + f + '.html';
          collEmpty.hidden = false;
        } else {
          collEmpty.hidden = true;
        }
      }
      if (window.ScrollTrigger) ScrollTrigger.refresh();
    });
  }

  /* ---- карусель ракурсов прямо в плитке (стрелки меняют ракурс) ---- */
  document.querySelectorAll('.tile.multi').forEach(function (tile) {
    var imgs = (tile.getAttribute('data-images') || '').split('|').filter(Boolean);
    var thumbs = (tile.getAttribute('data-thumbs') || '').split('|').filter(Boolean);
    if (imgs.length < 2) return;
    var img = tile.querySelector('.tile-img img');
    var count = tile.querySelector('.ti-count');
    var i = 0;
    function set(n) {
      i = (n + imgs.length) % imgs.length;
      img.src = thumbs[i] || imgs[i];                   // в плитке — лёгкое превью
      tile.setAttribute('data-full', imgs[i]);          // лайтбокс откроется на текущем ракурсе
      if (count) count.textContent = (i + 1) + ' / ' + imgs.length;
    }
    var prev = tile.querySelector('.ti-prev'), next = tile.querySelector('.ti-next');
    if (prev) prev.addEventListener('click', function (e) { e.stopPropagation(); set(i - 1); });
    if (next) next.addEventListener('click', function (e) { e.stopPropagation(); set(i + 1); });
  });

  /* ---- lightbox ---- */
  var tiles = [].slice.call(document.querySelectorAll('.tile[data-full]'));
  if (tiles.length) {
    var lb = document.createElement('div');
    lb.className = 'lb';
    lb.innerHTML =
      '<button class="lb-close" aria-label="Закрыть">&times;</button>' +
      '<button class="lb-nav lb-prev" aria-label="Назад">&#8249;</button>' +
      '<button class="lb-nav lb-next" aria-label="Вперёд">&#8250;</button>' +
      '<img alt=""><div class="lb-cap"><div class="lc-title"></div><div class="lc-meta"></div><a class="lc-artist"></a></div>';
    document.body.appendChild(lb);
    var lbImg = lb.querySelector('img'),
        lbT = lb.querySelector('.lc-title'),
        lbM = lb.querySelector('.lc-meta'),
        lbA = lb.querySelector('.lc-artist');

    function setArtistLink(t) {                 // ссылка «к художнику» (не на его же странице)
      var key = t.getAttribute('data-artist');
      var onOwnPage = key && location.pathname.indexOf('artist-' + key + '.html') !== -1;
      if (!key || onOwnPage) { lbA.style.display = 'none'; return; }
      var lng = document.documentElement.lang === 'en' ? 'en' : 'ru';
      var name = t.getAttribute('data-artist-' + lng) || '';
      if (!name) { lbA.style.display = 'none'; return; }
      lbA.href = 'artist-' + key + '.html';
      lbA.textContent = name + ' →';
      lbA.style.display = '';
    }
    var mode = 'works', cur = 0, angles = [], aIdx = 0, angleTile = null;

    function metaOf(t, extra) {
      var lng = document.documentElement.lang === 'en' ? 'en' : 'ru';
      var meta = t.getAttribute('data-meta-' + lng) || '';
      if (t.getAttribute('data-sold') === '1') meta += (meta ? ' · ' : '') + (lng === 'en' ? 'Sold' : 'Продано');
      if (extra) meta += (meta ? ' · ' : '') + extra;
      return meta;
    }
    function showWork(i) {                     // листаем между работами
      var visible = tiles.filter(function (t) { return !t.classList.contains('hide'); });
      if (!visible.length) return;
      cur = (i + visible.length) % visible.length;
      var t = visible[cur];
      lbImg.src = t.getAttribute('data-full');
      lbT.textContent = t.getAttribute('data-title') || '';
      lbM.textContent = metaOf(t);
      setArtistLink(t);
    }
    function showAngle(i) {                     // листаем ракурсы одной работы
      aIdx = (i + angles.length) % angles.length;
      lbImg.src = angles[aIdx];
      lbT.textContent = angleTile.getAttribute('data-title') || '';
      var lng = document.documentElement.lang === 'en' ? 'en' : 'ru';
      var label = (lng === 'en' ? 'view ' : 'ракурс ') + (aIdx + 1) + ' / ' + angles.length;
      lbM.textContent = metaOf(angleTile, label);
      setArtistLink(angleTile);
    }
    function step(d) { if (mode === 'angles') showAngle(aIdx + d); else showWork(cur + d); }
    function open(t) {
      // конфеты Julie Jaler — просмотр на белом фоне
      lb.classList.toggle('light', t.getAttribute('data-artist') === 'julie-jaler');
      var imgs = (t.getAttribute('data-images') || '').split('|').filter(Boolean);
      if (imgs.length > 1) {
        mode = 'angles'; angles = imgs; angleTile = t;
        aIdx = Math.max(0, imgs.indexOf(t.getAttribute('data-full')));
        showAngle(aIdx);
      } else {
        mode = 'works';
        var visible = tiles.filter(function (x) { return !x.classList.contains('hide'); });
        showWork(visible.indexOf(t));
      }
      lb.classList.add('open'); document.body.style.overflow = 'hidden';
    }
    function close() { lb.classList.remove('open'); document.body.style.overflow = ''; }
    tiles.forEach(function (t) {
      t.addEventListener('click', function (e) {
        if (e.target.closest('.ti-nav')) return;   // клик по стрелке — не открываем лайтбокс
        var goto = t.getAttribute('data-goto');
        if (goto) { window.location.href = goto; return; }   // визитная — сразу к художнику
        open(t);
      });
    });
    lb.querySelector('.lb-close').addEventListener('click', close);
    lb.querySelector('.lb-prev').addEventListener('click', function () { step(-1); });
    lb.querySelector('.lb-next').addEventListener('click', function () { step(1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') step(-1);
      if (e.key === 'ArrowRight') step(1);
    });
  }

  /* ---- переключение языка RU/EN (базовое) ---- */
  var langBtn = document.getElementById('langToggle');
  var lang = localStorage.getItem('agt-lang') || 'ru';
  // пересортировка списков художников по алфавиту текущего языка
  function reorderByLang(container, itemSel) {
    if (!container) return;
    var key = 'data-s' + lang; // data-sru | data-sen; у элементов без ключа (напр. «Все») → '' → в начало
    var items = [].slice.call(container.querySelectorAll(itemSel));
    items.sort(function (a, b) {
      return (a.getAttribute(key) || '').localeCompare(b.getAttribute(key) || '', lang);
    });
    items.forEach(function (el) { container.appendChild(el); });
  }
  function applyLang() {
    document.querySelectorAll('[data-ru][data-en]').forEach(function (el) {
      var val = el.getAttribute('data-' + lang);
      var tag = el.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA') el.placeholder = val;  // плейсхолдеры форм
      else el.textContent = val;
    });
    reorderByLang(document.querySelector('.artist-strip'), '.a-card');
    reorderByLang(document.querySelector('.artist-list'), '.artist-row');
    reorderByLang(document.getElementById('filters'), '.filter');
    if (langBtn) langBtn.textContent = lang === 'ru' ? 'EN' : 'RU';
    document.documentElement.lang = lang;
  }
  applyLang();
  if (langBtn) langBtn.addEventListener('click', function () {
    lang = lang === 'ru' ? 'en' : 'ru';
    localStorage.setItem('agt-lang', lang);
    applyLang();
  });

  /* ---- видео-превью: hover на десктопе, автоплей по видимости на тач-устройствах ---- */
  var gridVids = [].slice.call(document.querySelectorAll('.grid-video video'));
  gridVids.forEach(function (v) {
    v.addEventListener('mouseenter', function () { v.play().catch(function(){}); });
    v.addEventListener('mouseleave', function () { v.pause(); });
  });
  var touchDev = window.matchMedia('(hover: none)').matches;
  if (touchDev && gridVids.length && 'IntersectionObserver' in window) {
    var vio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && en.intersectionRatio >= 0.5) en.target.play().catch(function(){});
        else en.target.pause();
      });
    }, { threshold: [0, 0.5] });
    gridVids.forEach(function (v) { vio.observe(v); });
  }
})();
