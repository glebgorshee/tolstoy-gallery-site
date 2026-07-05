#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор статического сайта Art Gallery Tolstoy (рыба).
Читает data/catalog.json + картинки в assets/img, собирает HTML-страницы.
Запуск:  python3 build.py"""
import json, os, re, html, glob, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = 'assets/img'

# ---------- данные о художниках ----------
ARTISTS = [
    dict(slug='terenin', order=1, key='terenin',
         name_ru='Алексей Теренин', name_en='Alexey Terenin',
         years='р. 1969 · Москва / Прага',
         portrait=f'{IMG}/site/terenin-home.jpg',
         short_ru='Магический реализм: всадники, цветы и город снов на стыке культур Запада и Востока.',
         bio_ru=('Алексей Теренин родился в Москве в 1969 году. В 1993 году окончил Московский '
                 'архитектурный институт, успешно сочетая в работах образование архитектора и практику '
                 'художника. Часть детства провёл в Праге, что впитало в его творчество наследие культур '
                 'Запада и Востока. Искусствовед Алексей Вахманов определил этот стиль как магический '
                 'реализм. Первая персональная выставка — 1992, галерея «М’Арс». В 1997 году работал '
                 'художником-постановщиком балета «Каприччио» Стравинского (реж. Алексей Ратманский) на '
                 'сцене Большого театра. Живёт и работает в Праге. В России эксклюзивно представлен Арт '
                 'Галереей Толстой.')),
    dict(slug='accardi', order=2, key='accardi',
         name_ru='Анджело Аккарди', name_en='Angelo Accardi',
         years='р. 1964 · Италия',
         portrait=f'{IMG}/site/angelo-accardi1.jpg',
         short_ru='Ироничные и сюрреалистичные городские пейзажи современной жизни.',
         bio_ru=('Анджело Аккарди родился в 1964 году в городе Сапри, провинция Салерно. Учился в Академии '
                 'изящных искусств в Неаполе. В начале 1990-х основал собственную студию живописи и '
                 'скульптуры рядом с домом. Сегодня искусство Аккарди — магические композиции современной '
                 'жизни: городские пейзажи, чаще ироничные и сюрреалистичные. Художник участвовал в '
                 'многочисленных персональных и групповых выставках в Италии и по всему миру; работы — в '
                 'частных коллекциях Европы, США и Азии.')),
    dict(slug='tamburro', order=3, key='tamburro',
         name_ru='Антонио Тамбурро', name_en='Antonio Tamburro',
         years='р. 1948 · Италия',
         portrait=f'{IMG}/site/tamburo-main.jpg',
         short_ru='Фигура в движении: белое, синее, золото и охра.',
         bio_ru=('Антонио Тамбурро родился в 1948 году. Окончил Академию изящных искусств в Неаполе, затем '
                 'в Риме. Выставлялся в престижных галереях Италии, Монако, Швейцарии, Австрии, Германии и '
                 'США. В его работах преобладают оттенки белого и синего, жёлтого и охры. Акцент сделан на '
                 'фигуре в движении и на форме; композиция всегда полна динамики.')),
    dict(slug='mirogi', order=4, key='mirogi',
         name_ru='MiRoGi', name_en='Michèle Rousselot-Gilbert',
         years='р. 1957 · Франция',
         portrait=f'{IMG}/site/michele-home.jpg',
         short_ru='Скульптура женского тела: чувственность без вульгарности.',
         bio_ru=('Мишель Руссело-Жильбер (MiRoGi) родилась в 1957 году во Франции. Скульптурой занимается '
                 'с 1999 года. Самоучка с прекрасным пониманием человеческого тела (по образованию '
                 'физиотерапевт и остеопат), что дало ей уникальное видение движения в скульптуре. Она '
                 'выражает женскую чувственность в телесных формах, наполненных жизнью, работая в '
                 'эротическом стиле, но без вульгарности — показывая возможные пути женского обольщения.')),
    dict(slug='van-apple', order=5, key='van-apple',
         name_ru='Дидерик ван Эппл', name_en='Diederik van Apple',
         years='р. 1985 · Нидерланды',
         portrait=f'{IMG}/site/van-apple-art-uitnodiging-kopiya.jpg',
         short_ru='Цифровое mix-media искусство: поп-культура, комиксы, лимитированные серии.',
         bio_ru=('Дидерик ван Эппл родился и вырос в Лейдене, Нидерланды, в 1985 году. Бросил юриспруденцию '
                 'ради творчества; с 2005 года работал арт-представителем галереи в Амстердаме, ездил по '
                 'мировым выставкам и ярмаркам. Начал создавать цифровое mix-media искусство, сочетая '
                 'фантазию с художественной атмосферой мест, где жил. Первые лимитированные серии (2017) '
                 'распродавались мгновенно. Работал на Ибице. Сегодня его работы популярны в международных '
                 'галереях, среди коллекционеров и инвесторов.')),
    dict(slug='bashev', order=6, key='bashev',
         name_ru='Максим Башев', name_en='Maxim Bashev',
         years='Москва',
         portrait=f'{IMG}/site/bashev-main1.jpg',
         short_ru='Художник-гуманист: авангард, смешанная техника, фотопортрет в живописи.',
         bio_ru=('Максим Башев — художник, график, фотограф, автор коротких рассказов. Удостоен звания '
                 '«Художник-гуманист» (сертификат вице-президента Fine Arts Sotheby’s Гарри Ф. Метцнера и '
                 'галереи Aldo Castillo, Чикаго). Современный авангардист, работает в смешанной технике; '
                 'одна из главных черт его манеры — интеграция фотопортретов в живопись. Своим учителем '
                 'считает художника и философа Луиса Ортегу. Среди влияний: Веласкес, Эль Греко, Гойя, '
                 'Дали, Баския, Харинг, Дюбюффе, Раушенберг, Твомбли. Живёт и работает в Москве; работы — '
                 'в музеях и частных коллекциях России, США и Европы.'),
         is_video=True),
]
ART_BY_KEY = {a['key']: a for a in ARTISTS}

CONTACTS = dict(
    address='Новинский бульвар, 1/2, Москва',
    email1='mf@artgallerytolstoy.com', phone1='+7 (916) 999-90-06',
    email2='mb@artgallerytolstoy.com', phone2='+7 (916) 291-31-45',
    fb='https://www.facebook.com/artgallerytolstoy/',
)

# ---------- каталог работ ----------
catalog = json.load(open(os.path.join(ROOT, 'data/catalog.json'), encoding='utf-8'))

def local_work_img(artist_key, slug, remote_url):
    ext = remote_url.rsplit('.', 1)[-1] if remote_url else 'jpg'
    for e in (ext, 'jpg', 'jpeg', 'png', 'webp'):
        p = f'{IMG}/works/{artist_key}/{slug}.{e}'
        if os.path.exists(os.path.join(ROOT, p)):
            return p
    return None

def works_of(artist_key):
    out = []
    for it in catalog.get(artist_key, []):
        img = local_work_img(artist_key, it['slug'], it.get('image'))
        if not img:
            continue
        meta = it.get('meta', [])
        tech = meta[1] if len(meta) > 1 else ''
        size = meta[2] if len(meta) > 2 else ''
        sold = 'SOLD' in meta
        out.append(dict(title=it['title'], tech=tech, size=size, sold=sold, img=img,
                        artist=artist_key))
    return out

ALL_WORKS = {a['key']: works_of(a['key']) for a in ARTISTS}

def esc(s): return html.escape(s or '', quote=True)

# ---------- переиспользуемые куски ----------
def head(title, desc, active=''):
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600&family=Noto+Serif:ital,wght@0,300;0,400;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
{header(active)}
'''

def header(active=''):
    def cls(name): return ' class="active"' if name == active else ''
    return f'''<header class="site-header" id="siteHeader">
  <div class="hd-inner">
    <a class="brand" href="index.html">Art Gallery <span>Tolstoy</span></a>
    <div class="hd-right">
      <nav class="nav" id="nav">
        <a href="artists.html"{cls('artists')} data-ru="Художники" data-en="Artists">Художники</a>
        <a href="collections.html"{cls('collections')} data-ru="Коллекция" data-en="Collection">Коллекция</a>
        <a href="visit.html"{cls('visit')} data-ru="Визит" data-en="Visit">Визит</a>
      </nav>
      <button class="lang" id="langToggle" type="button">EN</button>
      <button class="burger" id="burger" aria-label="Меню"><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="mobile-menu" id="mobileMenu">
  <a href="artists.html" data-ru="Художники" data-en="Artists">Художники</a>
  <a href="collections.html" data-ru="Коллекция" data-en="Collection">Коллекция</a>
  <a href="visit.html" data-ru="Визит" data-en="Visit">Визит</a>
</div>
'''

def footer():
    c = CONTACTS
    return f'''<footer class="site-footer">
  <div class="ft-grid">
    <div>
      <div class="ft-brand">Art Gallery Tolstoy</div>
      <p class="ft-muted">Галерея современного европейского искусства.<br>Вход только по предварительной записи.</p>
    </div>
    <div>
      <div class="ft-label">Адрес</div>
      <p>{esc(c['address'])}</p>
    </div>
    <div>
      <div class="ft-label">Контакты</div>
      <p><a href="mailto:{c['email1']}">{c['email1']}</a><br><a href="tel:{c['phone1'].replace(' ','').replace('(','').replace(')','').replace('-','')}">{c['phone1']}</a></p>
      <p><a href="mailto:{c['email2']}">{c['email2']}</a><br><a href="tel:{c['phone2'].replace(' ','').replace('(','').replace(')','').replace('-','')}">{c['phone2']}</a></p>
    </div>
    <div>
      <div class="ft-label">Соцсети</div>
      <p><a href="{c['fb']}" target="_blank" rel="noopener">Facebook</a></p>
    </div>
  </div>
  <div class="ft-bottom">
    <span>© 2026 Art Gallery Tolstoy</span>
    <span class="ft-draft">рыба — черновая структура</span>
  </div>
</footer>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/gh/studio-freight/lenis@1.0.42/dist/lenis.min.js"></script>
<script src="assets/js/main.js"></script>
</body>
</html>'''

def work_tile(w, idx):
    badge = '<span class="badge">Продано</span>' if w['sold'] else ''
    meta = ' · '.join(x for x in (w['tech'], w['size']) if x)
    return f'''<figure class="tile reveal" data-index="{idx}" data-title="{esc(w['title'])}" data-meta="{esc(meta)}" data-sold="{'1' if w['sold'] else '0'}" data-full="{esc(w['img'])}">
  <div class="tile-img"><img src="{esc(w['img'])}" alt="{esc(w['title'])}" loading="lazy">{badge}</div>
  <figcaption><span class="t-title">{esc(w['title'])}</span><span class="t-meta">{esc(meta)}</span></figcaption>
</figure>'''

# ---------- главная ----------
def build_index():
    featured = []
    for key in ('accardi', 'van-apple', 'terenin', 'mirogi'):
        featured += ALL_WORKS[key][:3]
    tiles = ''.join(work_tile(w, i) for i, w in enumerate(featured))
    artist_cards = ''.join(f'''<a class="a-card reveal" href="artist-{a['slug']}.html">
      <div class="a-card-img"><img src="{esc(a['portrait'])}" alt="{esc(a['name_ru'])}" loading="lazy"></div>
      <div class="a-card-name">{esc(a['name_ru'])}</div>
      <div class="a-card-years">{esc(a['years'])}</div>
    </a>''' for a in ARTISTS)
    body = f'''
<section class="hero">
  <div class="hero-bg"><img src="{IMG}/site/new-slide3.jpg" alt=""></div>
  <div class="hero-in">
    <p class="hero-kicker" data-ru="Москва · с 2016" data-en="Moscow · since 2016">Москва · с 2016</p>
    <h1 class="hero-title">Art Gallery<br>Tolstoy</h1>
    <p class="hero-sub" data-ru="Коллекция живописи и скульптуры современных европейских художников" data-en="A collection of paintings and sculptures by modern European artists">Коллекция живописи и скульптуры современных европейских художников</p>
    <a class="btn btn-light" href="collections.html" data-ru="Смотреть коллекцию" data-en="View collection">Смотреть коллекцию</a>
  </div>
  <div class="scroll-cue"></div>
</section>

<section class="intro container">
  <p class="intro-lead reveal" data-ru="Весной 2016 года на арт-карте Москвы появилось новое место. Галерея «Толстой» представляет уникальную коллекцию картин и скульптур современных европейских художников — в тишине, вдали от суеты, для тех, кто смотрит внимательно." data-en="A new place appeared on the art map of Moscow in spring 2016. Art Gallery Tolstoy presents a unique collection of paintings and sculptures of modern European artists.">Весной 2016 года на арт-карте Москвы появилось новое место. Галерея «Толстой» представляет уникальную коллекцию картин и скульптур современных европейских художников — в тишине, вдали от суеты, для тех, кто смотрит внимательно.</p>
</section>

<section class="block container">
  <div class="block-head reveal">
    <h2 data-ru="Художники" data-en="Artists">Художники</h2>
    <a class="link-more" href="artists.html" data-ru="Все художники" data-en="All artists">Все художники →</a>
  </div>
  <div class="artist-strip">{artist_cards}</div>
</section>

<section class="block container">
  <div class="block-head reveal">
    <h2 data-ru="Избранные работы" data-en="Selected works">Избранные работы</h2>
    <a class="link-more" href="collections.html" data-ru="Вся коллекция" data-en="Full collection">Вся коллекция →</a>
  </div>
  <div class="grid">{tiles}</div>
</section>

<section class="visit-cta">
  <div class="container visit-cta-in reveal">
    <p class="vc-kicker" data-ru="Визит" data-en="Visit">Визит</p>
    <h2 data-ru="Приходите посмотреть" data-en="Come and see">Приходите посмотреть</h2>
    <p class="vc-addr">{esc(CONTACTS['address'])}</p>
    <p class="vc-note" data-ru="Доступ в галерею — по предварительной записи." data-en="Access to the gallery is by appointment only.">Доступ в галерею — по предварительной записи.</p>
    <a class="btn btn-dark" href="visit.html" data-ru="Записаться на визит" data-en="Book a visit">Записаться на визит</a>
  </div>
</section>
'''
    return head('Art Gallery Tolstoy — современное искусство в Москве',
                'Галерея современного европейского искусства в Москве. Живопись и скульптура. Вход по записи.',
                '') + body + footer()

# ---------- художники ----------
def build_artists():
    rows = ''
    for i, a in enumerate(ARTISTS):
        side = 'row-rev' if i % 2 else ''
        cnt = len(ALL_WORKS[a['key']])
        cnt_txt = f'{cnt} работ' if not a.get('is_video') else '14 видео-работ'
        rows += f'''<a class="artist-row reveal {side}" href="artist-{a['slug']}.html">
      <div class="ar-img"><img src="{esc(a['portrait'])}" alt="{esc(a['name_ru'])}" loading="lazy"></div>
      <div class="ar-txt">
        <p class="ar-years">{esc(a['years'])}</p>
        <h2 class="ar-name">{esc(a['name_ru'])}</h2>
        <p class="ar-en">{esc(a['name_en'])}</p>
        <p class="ar-short">{esc(a['short_ru'])}</p>
        <span class="ar-link">{cnt_txt} →</span>
      </div>
    </a>'''
    body = f'''
<section class="page-head container">
  <p class="ph-kicker" data-ru="Ростер галереи" data-en="Gallery roster">Ростер галереи</p>
  <h1 data-ru="Художники" data-en="Artists">Художники</h1>
</section>
<section class="container artist-list">{rows}</section>
'''
    return head('Художники — Art Gallery Tolstoy', 'Художники Арт Галереи Толстой', 'artists') + body + footer()

# ---------- страница художника ----------
def build_artist(a):
    works = ALL_WORKS[a['key']]
    tiles = ''.join(work_tile(w, i) for i, w in enumerate(works))
    if a.get('is_video'):
        vids = sorted(glob.glob(os.path.join(ROOT, f'{IMG}/works/bashev-video/*.mp4')))
        vtiles = ''
        for v in vids:
            rel = os.path.relpath(v, ROOT).replace(os.sep, '/')
            name = os.path.splitext(os.path.basename(v))[0]
            vtiles += f'''<figure class="tile reveal"><div class="tile-img"><video src="{esc(rel)}" muted loop playsinline preload="none"></video></div><figcaption><span class="t-title">{esc(name)}</span></figcaption></figure>'''
        gallery = f'<div class="grid grid-video">{vtiles}</div>' if vtiles else ''
        gallery_head = 'Видео-работы'
    else:
        gallery = f'<div class="grid">{tiles}</div>'
        gallery_head = 'Работы'
    body = f'''
<section class="artist-hero">
  <div class="ah-img"><img src="{esc(a['portrait'])}" alt="{esc(a['name_ru'])}"></div>
  <div class="ah-txt container">
    <p class="ah-years">{esc(a['years'])}</p>
    <h1 class="ah-name">{esc(a['name_ru'])}</h1>
    <p class="ah-en">{esc(a['name_en'])}</p>
  </div>
</section>
<section class="container artist-bio">
  <p class="bio reveal">{esc(a['bio_ru'])}</p>
</section>
<section class="container block">
  <div class="block-head reveal"><h2>{gallery_head}</h2></div>
  {gallery}
</section>
<section class="visit-cta">
  <div class="container visit-cta-in reveal">
    <p class="vc-kicker">Интересует работа?</p>
    <h2>Запишитесь на просмотр</h2>
    <p class="vc-note">Доступ в галерею — по предварительной записи.</p>
    <a class="btn btn-dark" href="visit.html">Связаться с галереей</a>
  </div>
</section>
'''
    return head(f'{a["name_ru"]} — Art Gallery Tolstoy', esc(a['short_ru']), 'artists') + body + footer()

# ---------- коллекция ----------
def build_collections():
    filters = '<button class="filter active" data-f="all">Все</button>'
    for a in ARTISTS:
        filters += f'<button class="filter" data-f="{a["key"]}">{esc(a["name_ru"])}</button>'
    tiles = ''
    idx = 0
    for a in ARTISTS:
        for w in ALL_WORKS[a['key']]:
            t = work_tile(w, idx)
            t = t.replace('class="tile reveal"', f'class="tile reveal" data-artist="{a["key"]}"')
            tiles += t
            idx += 1
    body = f'''
<section class="page-head container">
  <p class="ph-kicker" data-ru="Живопись и скульптура" data-en="Paintings and sculpture">Живопись и скульптура</p>
  <h1 data-ru="Коллекция" data-en="Collection">Коллекция</h1>
</section>
<section class="container">
  <div class="filters" id="filters">{filters}</div>
  <div class="grid" id="collGrid">{tiles}</div>
</section>
'''
    return head('Коллекция — Art Gallery Tolstoy', 'Коллекция работ Арт Галереи Толстой', 'collections') + body + footer()

# ---------- визит ----------
def build_visit():
    c = CONTACTS
    map_q = 'Новинский+бульвар+1/2+Москва'
    body = f'''
<section class="page-head container">
  <p class="ph-kicker" data-ru="Как добраться" data-en="Getting here">Как добраться</p>
  <h1 data-ru="Визит" data-en="Visit">Визит</h1>
</section>
<section class="container visit-grid">
  <div class="visit-info reveal">
    <div class="vi-block">
      <div class="vi-label">Адрес</div>
      <p class="vi-big">{esc(c['address'])}</p>
    </div>
    <div class="vi-block">
      <div class="vi-label">Режим</div>
      <p data-ru="Доступ в галерею — только по предварительной записи. Пожалуйста, свяжитесь с нами, чтобы договориться о визите." data-en="Access to the gallery is by appointment only. Please contact us to make an appointment.">Доступ в галерею — только по предварительной записи. Пожалуйста, свяжитесь с нами, чтобы договориться о визите.</p>
    </div>
    <div class="vi-block">
      <div class="vi-label">Контакты</div>
      <p><a href="mailto:{c['email1']}">{c['email1']}</a> · {c['phone1']}</p>
      <p><a href="mailto:{c['email2']}">{c['email2']}</a> · {c['phone2']}</p>
    </div>
    <div class="vi-block">
      <div class="vi-label">Соцсети</div>
      <p><a href="{c['fb']}" target="_blank" rel="noopener">Facebook</a></p>
    </div>
  </div>
  <form class="visit-form reveal" onsubmit="return false;">
    <div class="vf-label">Записаться на визит</div>
    <input type="text" placeholder="Имя" autocomplete="name">
    <input type="tel" placeholder="Телефон" autocomplete="tel">
    <input type="email" placeholder="E-mail" autocomplete="email">
    <textarea rows="3" placeholder="Комментарий"></textarea>
    <button class="btn btn-dark" type="submit">Отправить</button>
    <p class="vf-note">Форма-заглушка. Подключим отправку на почту при запуске.</p>
  </form>
</section>
<section class="map-wrap">
  <iframe src="https://maps.google.com/maps?q={map_q}&z=15&output=embed" loading="lazy" title="Карта"></iframe>
</section>
'''
    return head('Визит — Art Gallery Tolstoy', 'Как добраться и записаться в Арт Галерею Толстой', 'visit') + body + footer()

# ---------- запись файлов ----------
def w(path, content):
    with open(os.path.join(ROOT, path), 'w', encoding='utf-8') as f:
        f.write(content)
    print('  ', path)

print('Собираю страницы:')
w('index.html', build_index())
w('artists.html', build_artists())
for a in ARTISTS:
    w(f'artist-{a["slug"]}.html', build_artist(a))
w('collections.html', build_collections())
w('visit.html', build_visit())
print('Работ в каталоге по художникам:', {k: len(v) for k, v in ALL_WORKS.items()})
print('Готово.')
