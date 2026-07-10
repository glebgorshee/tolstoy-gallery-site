#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор статического сайта Art Gallery Tolstoy (рыба).
Читает data/catalog.json + картинки в assets/img, собирает HTML-страницы.
Запуск:  python3 build.py"""
import json, os, re, html, glob, shutil, time

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = 'assets/img'
VER = str(int(time.time()))  # версия для сброса кеша CSS/JS при каждой пересборке

# ---------- данные о художниках ----------
ARTISTS = [
    dict(slug='kiko', order=1, key='kiko',
         name_ru='KIKO', name_en='KIKO',
         years='Франция',
         portrait=f'{IMG}/site/kiko-portrait.jpg', hero_pos='center 15%',
         short_ru='Экспрессивные портреты из цветных росчерков — на грани абстракции и фигуратива.',
         bio_ru=('KIKO — современный художник, работающий в экспрессивной манере: многослойные цветные '
                 'росчерки и мазки складываются в портреты и образы на грани абстракции и фигуратива. '
                 '[Черновая справка — биографию уточним у художника.]')),
    dict(slug='julie-jaler', order=2, key='julie-jaler',
         name_ru='Джули Жалер', name_en='Julie Jaler',
         years='Франция',
         portrait=f'{IMG}/site/julie-portrait.jpg', hero_pos='center 12%',
         short_ru='Гиперреалистичные скульптуры-конфеты из смолы в мотивах люксовых домов.',
         bio_ru=('Джули Жалер (Julie Jaler) — французская художница-скульптор из Парижа. Создаёт '
                 'гиперреалистичные скульптуры-конфеты из смолы, оборачивая их в мотивы люксовых домов — '
                 'переосмысление роскоши, поп-арта и объекта желания. Каждая работа существует в нескольких '
                 'ракурсах. [Черновая справка — биографию уточним у художницы.]')),
    dict(slug='accardi', order=2, key='accardi',
         name_ru='Анджело Аккарди', name_en='Angelo Accardi',
         years='Италия',
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
         years='Италия',
         portrait=f'{IMG}/site/tamburo-main.jpg',
         short_ru='Фигура в движении: белое, синее, золото и охра.',
         bio_ru=('Антонио Тамбурро родился в 1948 году. Окончил Академию изящных искусств в Неаполе, затем '
                 'в Риме. Выставлялся в престижных галереях Италии, Монако, Швейцарии, Австрии, Германии и '
                 'США. В его работах преобладают оттенки белого и синего, жёлтого и охры. Акцент сделан на '
                 'фигуре в движении и на форме; композиция всегда полна динамики.')),
    dict(slug='van-apple', order=5, key='van-apple',
         name_ru='Ван Эппл', name_en='Van Apple',
         years='Нидерланды',
         portrait=f'{IMG}/site/van-apple-art-uitnodiging-kopiya.jpg', hero_pos='center top',
         short_ru='Цифровое mix-media искусство: поп-культура, комиксы, лимитированные серии.',
         bio_ru=('Дидерик ван Эппл родился и вырос в Лейдене, Нидерланды, в 1985 году. Бросил юриспруденцию '
                 'ради творчества; с 2005 года работал арт-представителем галереи в Амстердаме, ездил по '
                 'мировым выставкам и ярмаркам. Начал создавать цифровое mix-media искусство, сочетая '
                 'фантазию с художественной атмосферой мест, где жил. Первые лимитированные серии (2017) '
                 'распродавались мгновенно. Работал на Ибице. Сегодня его работы популярны в международных '
                 'галереях, среди коллекционеров и инвесторов.')),
    dict(slug='bashev', order=6, key='bashev',
         name_ru='Максим Башев', name_en='Maxim Bashev',
         years='Россия',
         portrait=f'{IMG}/site/bashev-portrait.jpg', hero_pos='center 20%',
         short_ru='Художник-гуманист: авангард, смешанная техника, фотопортрет в живописи.',
         bio_ru=('Максим Башев — художник, график, фотограф, автор коротких рассказов. Удостоен звания '
                 '«Художник-гуманист» (сертификат вице-президента Fine Arts Sotheby’s Гарри Ф. Метцнера и '
                 'галереи Aldo Castillo, Чикаго). Современный авангардист, работает в смешанной технике; '
                 'одна из главных черт его манеры — интеграция фотопортретов в живопись. Своим учителем '
                 'считает художника и философа Луиса Ортегу. Среди влияний: Веласкес, Эль Греко, Гойя, '
                 'Дали, Баския, Харинг, Дюбюффе, Раушенберг, Твомбли. Живёт и работает в Москве; работы — '
                 'в музеях и частных коллекциях России, США и Европы.'),
         is_video=True),
    dict(slug='mauro-paparella', order=7, key='mauro-paparella',
         name_ru='Мауро Папарелла', name_en='Mauro Paparella',
         years='Италия',
         portrait=f'{IMG}/site/mauro-portrait.jpg', hero_pos='center 40%',
         short_ru='Живопись на стыке с цифровыми медиа: идентичность, душа, современное общество.',
         bio_ru=('Мауро Папарелла — итальянский современный художник (р. 1985). Соединяет живопись и '
                 'цифровые медиа, работая на стыке фигуративного и абстрактного. Его инновационный язык '
                 'сочетает живописную традицию с элементами дизайна и мультимедиа; в основе работ — темы '
                 'поиска идентичности, души человека и размышления о современном обществе. Выставлялся в '
                 'галереях Италии и за рубежом.')),
    dict(slug='raphael-vanderhaegen', order=8, key='raphael-vanderhaegen',
         name_ru='Рафаэль Вандерхаген', name_en='Raphaël Vanderhaegen',
         years='Нидерланды',
         portrait=f'{IMG}/site/raphael-portrait.jpg', hero_pos='center 55%',
         short_ru='Личная история и преодоление прошлого как источник стиля.',
         bio_ru=('Рафаэль Вандерхаген — художник (р. 1991). В своём творчестве он опирается на собственное '
                 'прошлое: пережив непростые обстоятельства, он сумел оставить их позади, сосредоточившись '
                 'на своей страсти. Именно этот опыт и его преодоление сформировали художественный стиль '
                 'Рафаэля.')),
    dict(slug='jf-piecourt', order=9, key='jf-piecourt',
         name_ru='Жан-Франсуа Пьекур', name_en='Jean-François Piécourt',
         years='Франция',
         portrait=f'{IMG}/site/piecourt-portrait.jpg', hero_pos='center 25%',
         short_ru='Французский скульптор на стыке искусства и дизайна.',
         bio_ru=('Жан-Франсуа Пьекур — французский скульптор, работающий на стыке искусства и дизайна: '
                 'создаёт объекты-скульптуры, соединяя пластику формы с предметным дизайном. '
                 '[Черновая справка — подробности уточним у художника.]')),
    dict(slug='naor', order=10, key='naor',
         name_ru='NAOR', name_en='NAOR',
         years='Франция',
         portrait=f'{IMG}/site/naor-portrait.jpg', hero_pos='center center', logo=True,
         short_ru='Поп-арт-скульптуры из смолы: символы люксовых брендов и ирония над консюмеризмом.',
         bio_ru=('NAOR — французский художник из Лиона (р. 1988). Его стиль соединяет энергию поп-арта с '
                 'элегантностью ар-деко. Создаёт скульптуры-фигурки из смолы и металла, вплетая символы '
                 'люксовых домов — как оммаж и одновременно ирония над культурой потребления. В его '
                 'работах — баланс между нежностью и агрессией.')),
    dict(slug='dan-faco', order=11, key='dan-faco',
         name_ru='Дэн Фако', name_en='Dan Faco',
         years='Италия',
         portrait=f'{IMG}/site/danfaco-portrait.jpg', hero_pos='center 22%',
         short_ru='Поп-арт и экшн-пейнтинг: смола, фактуры, символы поп-культуры как эмоциональные карты.',
         bio_ru=('Дэн Фако (Даниэла Факоэтти) — итальянская художница из Бергамо, соединяющая визуальную '
                 'мощь поп-арта с жестовой энергией экшн-пейнтинга. Училась в художественной школе Мандзу '
                 'в Бергамо и Школе комикса при Кастелло Сфорцеско в Милане. Работает в акриле, аэрографии '
                 'и смоле, добавляя фактурные элементы — перья, монеты, природные объекты, — превращая '
                 'символы поп-культуры и повседневности в насыщенные, чувственные эмоциональные карты. '
                 'Выставлялась в Милане, Риме, Париже, Праге, Москве, Берлине и др.; в 2025 вошла в '
                 'Ежегодник итальянских художников.')),
    dict(slug='milena-b', order=12, key='milena-b',
         name_ru='Милена Б. Арт', name_en='Milena B. Art',
         years='Италия',
         portrait=f'{IMG}/site/milena-portrait.jpg', hero_pos='center 20%',
         short_ru='Поп-арт со стрит-настроением: иконы кино, музыки и поп-культуры.',
         bio_ru=('Милена Б. — итальянская поп-художница из Милана (родилась в Ро в 1972 году). Училась '
                 'графике и рекламе, работала арт-директором в рекламных агентствах, а затем превратила '
                 'своё увлечение в искусство. Первая коллекция, посвящённая иконам кино и музыки, была '
                 'показана в 2011 году с успехом и привела к сотрудничеству с галереями в Италии и '
                 'Бразилии. Её работы — с сильным поп-импактом и стрит-настроением, населённые иконами '
                 'поп-культуры: от героев Disney и Looney Tunes до современных героинь.')),
    dict(slug='dmitry-dyu', order=13, key='dmitry-dyu',
         name_ru='Дмитрий Дью', name_en='Dmitry DYU',
         years='Россия',
         portrait=f'{IMG}/site/dyu-portrait.jpg', hero_pos='center 38%',
         short_ru='Дизайнерские арт-игрушки Dyu Toys: каждая фигура — дух-оболочка, оживающая через владельца.',
         bio_ru=('Дмитрий Дью — художник и создатель Dyu Toys. Каждая фигура — дух-оболочка, оживающий '
                 'через своего владельца. Это лимитированные объекты, где философия, эстетика и ручная '
                 'работа превращают коллекцию в живое искусство.')),
    dict(slug='le-marquis', order=14, key='le-marquis',
         name_ru='Ле Маркиз', name_en='Le Marquis',
         years='Франция',
         portrait=f'{IMG}/site/lemarquis-portrait.jpg', hero_pos='center 25%',
         short_ru='Скульптуры-фигурки героев детства, переосмысленные с юмором и в духе люкс-брендов.',
         bio_ru=('Ле Маркиз (Le Marquis) — французский художник, «создатель эмоций»: лепит скульптуры-фигурки героев '
                 'детства, переосмысленные с юмором и в духе люксовых брендов. Знакомые персонажи в новом, '
                 'ироничном и рекламном ключе.')),
    dict(slug='leo-steph', order=15, key='leo-steph',
         name_ru='Лео и Стеф', name_en='Leo & Steph',
         years='Франция',
         portrait=f'{IMG}/site/leosteph-portrait.jpg', hero_pos='center 30%',
         short_ru='Дуэт, создатели персонажа Kid Cup: яркий и позитивный поп-арт в живописи и скульптуре.',
         bio_ru=('Лео и Стеф (Leo & Steph) — арт-дуэт, создатели культового персонажа Kid Cup. Их поп-арт — яркий и '
                 'позитивный — живёт в живописи и скульптуре: уникальные вещи, лимитированные серии и '
                 'работы на заказ. Дуэт выставляется на международных ярмарках, включая Art Basel Miami.')),
]
# ключи сортировки по фамилии (для обоих языков). Базовый порядок в DOM — по RU,
# на EN список пересортировывается в JS (порядки не совпадают).
# сортировка по ОТОБРАЖАЕМОМУ имени (Имя Фамилия) — чтобы список читался по алфавиту
SORT_KEYS = {
    'accardi':    ('анджело',  'angelo'),      # Анджело Аккарди
    'tamburro':   ('антонио',  'antonio'),     # Антонио Тамбурро
    'julie-jaler':('джули',    'julie'),       # Джули Жалер
    'van-apple':  ('ван эппл', 'van apple'),   # van Apple (имя Diederik убрано)
    'kiko':       ('кико',     'kiko'),        # KIKO
    'mauro-paparella':('мауро','mauro'),       # Мауро Папарелла
    'bashev':     ('максим',   'maxim'),       # Максим Башев
    'naor':       ('наор',     'naor'),        # NAOR
    'dan-faco':   ('дэн',      'dan'),         # Дэн Фако
    'milena-b':   ('милена',   'milena'),      # Милена Б.
    'dmitry-dyu': ('дмитрий',  'dmitry'),      # Dmitry DYU
    'le-marquis': ('ле маркиз','le marquis'),  # Le Marquis
    'leo-steph':  ('лео',      'leo'),         # Leo & Steph
    'raphael-vanderhaegen':('рафаэль','raphael'),  # Рафаэль Вандерхаген
    'jf-piecourt':('жан-франсуа','jean-francois'),  # Жан-Франсуа Пьекур
}
for a in ARTISTS:
    a['sort_ru'], a['sort_en'] = SORT_KEYS[a['key']]
ARTISTS.sort(key=lambda a: a['sort_ru'])   # базовый порядок — русский алфавит
ART_BY_KEY = {a['key']: a for a in ARTISTS}

# ---------- английские версии текстов художников ----------
EN = {
 'kiko': dict(
    years='France',
    short='Expressive portraits built from colored scribbles — between abstraction and figuration.',
    bio=('KIKO is a contemporary artist working in an expressive manner: layered colored scribbles and '
         'strokes come together into portraits and images on the edge of abstraction and figuration. '
         '[Draft note — biography to be confirmed with the artist.]')),
 'julie-jaler': dict(
    years='France',
    short='Hyperrealistic resin candy sculptures wrapped in the motifs of luxury houses.',
    bio=('Julie Jaler is a French sculptor-artist based in Paris. She creates hyperrealistic candy '
         'sculptures in resin, wrapping them in the motifs of luxury houses — a reimagining of luxury, '
         'pop art and the object of desire. Each work exists in several viewing angles. '
         '[Draft note — biography to be confirmed with the artist.]')),
 'accardi': dict(
    years='Italy',
    short='Ironic, surreal cityscapes of modern life.',
    bio=('Angelo Accardi was born in 1964 in Sapri, province of Salerno. He studied at the Academy of '
         'Fine Arts in Naples. In the early 1990s he founded his own painting and sculpture studio near '
         'his home. Today Accardi’s art is a magical composition of modern life: cityscapes, often ironic '
         'and surreal. He has taken part in numerous solo and group exhibitions in Italy and around the '
         'world; his works are in private collections across Europe, the USA and Asia.')),
 'tamburro': dict(
    years='Italy',
    short='The figure in motion: white, blue, gold and ochre.',
    bio=('Antonio Tamburro was born in 1948. He graduated from the Academy of Fine Arts in Naples, then '
         'in Rome. He has exhibited in prestigious galleries in Italy, Monaco, Switzerland, Austria, '
         'Germany and the USA. His work is dominated by shades of white and blue, yellow and ochre. The '
         'emphasis is on the figure in motion and on form; the composition is always full of dynamism.')),
 'van-apple': dict(
    years='Netherlands',
    short='Digital mix-media art: pop culture, comics, limited editions.',
    bio=('Diederik van Apple was born and raised in Leiden, the Netherlands, in 1985. He gave up law for '
         'art; from 2005 he worked as a gallery art representative in Amsterdam, travelling the world’s '
         'exhibitions and fairs. He began creating digital mix-media art, combining fantasy with the '
         'artistic atmosphere of the places he lived. His first limited series (2017) sold out instantly. '
         'He worked in Ibiza. Today his works are popular in international galleries, among collectors and '
         'investors.')),
 'bashev': dict(
    years='Russia',
    short='Humanist artist: avant-garde, mixed media, photo-portraits in painting.',
    bio=('Maxim Bashev is an artist, graphic artist, photographer and author of short stories. He was '
         'awarded the title “Humanist Artist” (certificate from Sotheby’s Vice President of Fine Arts '
         'Garry F. Metzner and the Aldo Castillo Gallery, Chicago). A contemporary avant-garde artist '
         'working in mixed media; one of the main features of his manner is the integration of '
         'photo-portraits into painting. He considers the artist and philosopher Luis Ortega his teacher. '
         'Among his influences: Velázquez, El Greco, Goya, Dalí, Basquiat, Haring, Dubuffet, Rauschenberg, '
         'Twombly. He lives and works in Moscow; his works are in museums and private collections in '
         'Russia, the USA and Europe.')),
 'mauro-paparella': dict(
    years='Italy',
    short='Painting meets digital media: identity, the soul, contemporary society.',
    bio=('Mauro Paparella is an Italian contemporary artist (b. 1985). He merges painting with digital '
         'media, working between the figurative and the abstract. His innovative language combines '
         'painterly tradition with elements of design and multimedia; at the core of his work are themes '
         'of identity, the human soul and reflections on contemporary society. He has exhibited in '
         'galleries in Italy and abroad.')),
 'raphael-vanderhaegen': dict(
    years='Netherlands',
    short='A personal story and overcoming the past as the source of his style.',
    bio=('Raphaël Vanderhaegen is an artist (b. 1991). His work draws on his own past: having gone '
         'through difficult circumstances, he found a way to leave them behind by focusing on his '
         'passion. It is this experience — and overcoming it — that shaped Raphaël’s artistic style.')),
 'jf-piecourt': dict(
    years='France',
    short='French sculptor at the intersection of art and design.',
    bio=('Jean-François Piécourt is a French sculptor working at the intersection of art and design: '
         'he creates sculptural objects that merge the plasticity of form with product design. '
         '[Draft note — details to be confirmed with the artist.]')),
 'naor': dict(
    years='France',
    short='Resin pop-art figurines: luxury-brand symbols and a wink at consumerism.',
    bio=('NAOR is a French artist from Lyon (b. 1988). His style blends the energy of pop art with the '
         'elegance of art deco. He creates resin and metal figurine-sculptures woven with the symbols of '
         'luxury houses — at once an homage to and a critique of consumer culture. His work balances '
         'tenderness and aggression.')),
 'dan-faco': dict(
    years='Italy',
    short='Pop Art meets action painting: resin, materials, pop-culture symbols as emotional maps.',
    bio=('Dan Faco (Daniela Facoetti) is a Bergamo-based Italian artist who blends the visual power of '
         'Pop Art with the gestural energy of action painting. Trained at the Manzù Art School in Bergamo '
         'and the School of Comics at the Castello Sforzesco in Milan, she works across acrylics, airbrush '
         'and resin, adding material elements — feathers, coins, natural objects — that turn symbols of '
         'pop culture and everyday life into intense, sensorial emotional maps. She has exhibited in '
         'Milan, Rome, Paris, Prague, Moscow, Berlin and beyond, and was included in the 2025 Italian '
         'Artists Yearbook.')),
 'milena-b': dict(
    years='Italy',
    short='Pop art with a street edge: icons of cinema, music and pop culture.',
    bio=('Milena B. is an Italian pop artist based in Milan (born in Rho in 1972). After studying '
         'graphics and advertising and working as an art director in advertising agencies, she turned '
         'her passion into art. Her first collection — dedicated to icons of cinema and music — was '
         'exhibited in 2011 to acclaim, leading to collaborations with galleries in Italy and Brazil. '
         'Her work has a strong pop impact with a street edge, populated by icons of pop culture — from '
         'Disney and Looney Tunes characters to modern heroines.')),
 'dmitry-dyu': dict(
    years='Russia',
    short='Designer art toys, Dyu Toys: each figure a spirit-shell that comes alive through its owner.',
    bio=('Dmitry DYU is an artist and the creator of Dyu Toys. Each figure is a spirit-shell that comes '
         'alive through its owner — limited-edition objects where philosophy, aesthetics and handcraft '
         'turn the collection into living art.')),
 'le-marquis': dict(
    years='France',
    short='Figurines of childhood characters, reimagined with humour and a luxury-brand twist.',
    bio=('Le Marquis is a French artist — a “creator of emotions” who sculpts figurines of childhood '
         'characters, reimagined with humour and a luxury-brand twist. Familiar icons reinterpreted in a '
         'playful, advertising key.')),
 'leo-steph': dict(
    years='France',
    short='A duo, creators of the Kid Cup character: colorful, positive pop art in painting and sculpture.',
    bio=('Leo & Steph are an artist duo, creators of the iconic Kid Cup character. Their pop art — '
         'colorful and positive — lives in paintings and sculptures: unique pieces, limited editions and '
         'custom works. The duo shows at international fairs including Art Basel Miami.')),
}
for a in ARTISTS:
    e = EN[a['key']]
    a['years_en'], a['short_en'], a['bio_en'] = e['years'], e['short'], e['bio']

# логотип-вордмарк для шапки (инлайн SVG, fill наследует currentColor)
LOGO_SVG = open(os.path.join(ROOT, 'assets/img/site/logo.svg'), encoding='utf-8').read().strip()

CONTACTS = dict(
    address='Новинский бульвар, 1/2, Москва',
    email1='mf@artgallerytolstoy.com', phone1='+7 (916) 999-90-06',
    email2='mb@artgallerytolstoy.com', phone2='+7 (916) 291-31-45',
    fb='https://www.facebook.com/artgallerytolstoy/',
)

# ---------- каталог работ ----------
catalog = json.load(open(os.path.join(ROOT, 'data/catalog.json'), encoding='utf-8'))

# Новые работы (наполнение 2026) — единый источник с поддержкой мультиракурса.
# Формат: { "<key>": [ {slug, title, tech_ru, tech_en, size, sold, imgs:[имена файлов]} ] }
# imgs — имена файлов внутри assets/img/works/<key>/. Несколько файлов = карусель ракурсов.
_ARTWORKS_PATH = os.path.join(ROOT, 'data/artworks.json')
artworks_data = json.load(open(_ARTWORKS_PATH, encoding='utf-8')) if os.path.exists(_ARTWORKS_PATH) else {}

def local_work_img(artist_key, slug, remote_url):
    ext = remote_url.rsplit('.', 1)[-1] if remote_url else 'jpg'
    for e in (ext, 'jpg', 'jpeg', 'png', 'webp'):
        p = f'{IMG}/works/{artist_key}/{slug}.{e}'
        if os.path.exists(os.path.join(ROOT, p)):
            return p
    return None

def kiko_works():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, f'{IMG}/works/kiko/*.jpg'))):
        rel = os.path.relpath(p, ROOT).replace(os.sep, '/')
        out.append(dict(title='', tech_ru='Акрил, смешанная техника', tech_en='Acrylic, mixed media',
                        size='', sold=False, imgs=[rel], artist='kiko'))
    return out

# у сплошных конфет обложкой встал «зад» — ставим кадр с надписью бренда первым (0-based индекс)
JULIE_FRONT = {'coco-blanc': 1, 'coco-noir': 2, 'hermes-1': 1, 'herm-s-ii': 1}

def julie_works():
    data = json.load(open(os.path.join(ROOT, 'data/julie_works.json'), encoding='utf-8'))
    out = []
    for w in data:
        imgs = [i for i in w['imgs'] if os.path.exists(os.path.join(ROOT, i))]
        if not imgs:
            continue
        fi = JULIE_FRONT.get(w['slug'])
        if fi is not None and fi < len(imgs):
            imgs = [imgs[fi]] + imgs[:fi] + imgs[fi + 1:]   # фронт — первым
        out.append(dict(title=w['title'], tech_ru='Смола', tech_en='Resin', size=w.get('size', ''),
                        sold=False, imgs=imgs, artist='julie-jaler'))
    return out

def artworks_of(artist_key):
    """Новые работы из data/artworks.json. Несколько файлов в imgs → мультиракурс-карусель (как у Julie)."""
    out = []
    for w in artworks_data.get(artist_key, []):
        imgs = []
        for fn in w.get('imgs', []):
            p = f'{IMG}/works/{artist_key}/{fn}'
            if os.path.exists(os.path.join(ROOT, p)):
                imgs.append(p)
        if not imgs:
            continue
        out.append(dict(title=w.get('title', ''), tech_ru=w.get('tech_ru') or '', tech_en=w.get('tech_en') or '',
                        size=w.get('size') or '', sold=w.get('sold', False), imgs=imgs, artist=artist_key))
    return out

# переводы техник из старого каталога (EN → RU). Серийные названия работ
# van Apple (K.O. Bunny, Fashion Monkey и т.п.) — имена собственные, не переводятся.
TECH_RU = {
    'Oil, Acrylic, Ink Painting':   'Масло, акрил, тушь',
    'Oil Acrylic and Ink Painting': 'Масло, акрил, тушь',
    'Mixed Technique On Canvas':    'Холст, смешанная техника',
    'Etched Metal':                 'Металл, травление',
}

def works_of(artist_key):
    if artist_key == 'kiko':
        base = kiko_works()
    elif artist_key == 'julie-jaler':
        base = julie_works()
    else:
        base = []
        for it in catalog.get(artist_key, []):
            img = local_work_img(artist_key, it['slug'], it.get('image'))
            if not img:
                continue
            meta = it.get('meta', [])
            tech = meta[1] if len(meta) > 1 else ''
            size = meta[2] if len(meta) > 2 else ''
            sold = 'SOLD' in meta
            base.append(dict(title=it['title'], tech_ru=TECH_RU.get(tech, tech), tech_en=tech,
                            size=size, sold=sold, imgs=[img], artist=artist_key))
    # Новые работы (artworks.json) доливаются ко всем художникам единообразно
    return base + artworks_of(artist_key)

ALL_WORKS = {a['key']: works_of(a['key']) for a in ARTISTS}

def esc(s): return html.escape(s or '', quote=True)

# ---------- производные: миниатюры плиток и постеры видео ----------
# Плитки грузят лёгкие превью (~800px), полноразмер — только в лайтбоксе.
# Постер видео = кадр из ролика: без него <video preload="none"> стоит пустым квадратом.
THUMBS = f'{IMG}/thumbs'
import subprocess

def _fresh(dst, src):
    return os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src)

def thumb_path(rel):
    """assets/img/<x>.jpg -> assets/img/thumbs/<x>.jpg (если миниатюра есть, иначе оригинал)"""
    if not rel or not rel.startswith(IMG + '/'):
        return rel
    t = f'{THUMBS}/' + os.path.splitext(rel[len(IMG) + 1:])[0] + '.jpg'
    return t if os.path.exists(os.path.join(ROOT, t)) else rel

def poster_path(video_rel):
    stem = os.path.splitext(os.path.basename(video_rel))[0]
    vdir = os.path.basename(os.path.dirname(video_rel))
    p = f'{THUMBS}/posters/{vdir}/{stem}.jpg'
    return p if os.path.exists(os.path.join(ROOT, p)) else ''

def make_derivatives():
    made = 0
    # миниатюры: работы (кроме *-video) + портреты/картинки site
    srcs = [p for p in glob.glob(os.path.join(ROOT, IMG, 'works', '*', '*'))
            if os.path.splitext(p)[1].lower() in ('.jpg', '.jpeg', '.png')
            and '-video' not in os.path.basename(os.path.dirname(p))]
    srcs += [p for p in glob.glob(os.path.join(ROOT, IMG, 'site', '*'))
             if os.path.splitext(p)[1].lower() in ('.jpg', '.jpeg')]
    for src in srcs:
        rel = os.path.relpath(src, ROOT).replace(os.sep, '/')
        dst = os.path.join(ROOT, THUMBS, os.path.splitext(rel[len(IMG) + 1:])[0] + '.jpg')
        if _fresh(dst, src):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        # magick: лучше жмёт + progressive (перцептивно быстрее); sips — запасной
        r = subprocess.run(['magick', src, '-auto-orient', '-resize', '800x800>',
                            '-strip', '-interlace', 'Plane', '-quality', '76', dst],
                           capture_output=True)
        if r.returncode != 0:
            subprocess.run(['sips', '-Z', '800', '-s', 'format', 'jpeg',
                            '-s', 'formatOptions', '76', src, '--out', dst],
                           capture_output=True)
        made += 1
    # постеры видео (ffmpeg): кадр с 0.5 сек, ширина 640
    for src in glob.glob(os.path.join(ROOT, IMG, 'works', '*-video', '*.mp4')):
        vdir = os.path.basename(os.path.dirname(src))
        stem = os.path.splitext(os.path.basename(src))[0]
        dst = os.path.join(ROOT, THUMBS, 'posters', vdir, f'{stem}.jpg')
        if _fresh(dst, src):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        r = subprocess.run(['ffmpeg', '-y', '-ss', '0.5', '-i', src, '-frames:v', '1',
                            '-vf', 'scale=480:-2', '-q:v', '6', dst], capture_output=True)
        if r.returncode != 0:  # ролик короче 0.5с — берём первый кадр
            subprocess.run(['ffmpeg', '-y', '-i', src, '-frames:v', '1',
                            '-vf', 'scale=480:-2', '-q:v', '6', dst], capture_output=True)
        made += 1
    if made:
        print(f'Производные обновлены: {made}')

make_derivatives()

# ---------- переиспользуемые куски ----------
def head(title, desc, active='', home=False):
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
<link rel="stylesheet" href="assets/css/style.css?v={VER}">
</head>
<body>
{header(active, home)}
'''

def header(active='', home=False):
    def cls(name): return ' class="active"' if name == active else ''
    brand_cls = 'brand is-hidden' if home else 'brand'   # на главной логотип скрыт изначально, без мелькания до JS
    return f'''<header class="site-header" id="siteHeader">
  <div class="hd-inner">
    <div class="hd-top">
      <button class="burger" id="burger" aria-label="Меню"><span></span><span></span></button>
      <a class="{brand_cls}" href="index.html" aria-label="Art Gallery Tolstoy">{LOGO_SVG}</a>
      <button class="lang" id="langToggle" type="button">EN</button>
    </div>
    <nav class="nav" id="nav">
      <a href="artists.html"{cls('artists')} data-ru="Художники" data-en="Artists">Художники</a>
      <a href="collections.html"{cls('collections')} data-ru="Коллекция" data-en="Collection">Коллекция</a>
      <a href="contacts.html"{cls('contacts')} data-ru="Контакты" data-en="Contacts">Контакты</a>
    </nav>
  </div>
</header>
<div class="mobile-menu" id="mobileMenu">
  <a href="artists.html" data-ru="Художники" data-en="Artists">Художники</a>
  <a href="collections.html" data-ru="Коллекция" data-en="Collection">Коллекция</a>
  <a href="contacts.html" data-ru="Контакты" data-en="Contacts">Контакты</a>
</div>
'''

def footer():
    c = CONTACTS
    return f'''<footer class="site-footer">
  <div class="ft-grid">
    <div>
      <div class="ft-brand">Art Gallery Tolstoy</div>
      <p class="ft-muted" data-ru="Галерея современного европейского искусства." data-en="A gallery of contemporary European art.">Галерея современного европейского искусства.</p>
    </div>
    <div>
      <div class="ft-label" data-ru="Адрес" data-en="Address">Адрес</div>
      <p data-ru="{esc(c['address'])}" data-en="Novinsky Blvd, 1/2, Moscow">{esc(c['address'])}</p>
    </div>
    <div>
      <div class="ft-label" data-ru="Контакты" data-en="Contacts">Контакты</div>
      <p><a href="mailto:{c['email1']}">{c['email1']}</a><br><a href="tel:{c['phone1'].replace(' ','').replace('(','').replace(')','').replace('-','')}">{c['phone1']}</a></p>
      <p><a href="mailto:{c['email2']}">{c['email2']}</a><br><a href="tel:{c['phone2'].replace(' ','').replace('(','').replace(')','').replace('-','')}">{c['phone2']}</a></p>
    </div>
    <div>
      <div class="ft-label" data-ru="Соцсети" data-en="Social">Соцсети</div>
      <p><a href="{c['fb']}" target="_blank" rel="noopener">Facebook</a></p>
    </div>
  </div>
  <div class="ft-bottom">
    <span>© 2026 Art Gallery Tolstoy</span>
  </div>
</footer>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/gh/studio-freight/lenis@1.0.42/dist/lenis.min.js"></script>
<script src="assets/js/main.js?v={VER}"></script>
</body>
</html>'''

def work_tile(w, idx=0):
    imgs = w.get('imgs') or [w.get('img')]
    cover = imgs[0]
    multi = len(imgs) > 1
    tech_ru = w.get('tech_ru', w.get('tech', ''))
    tech_en = w.get('tech_en', w.get('tech', ''))
    # единицы измерения — каждой версии свои: RU «см», EN «cm»
    size = w['size'] or ''
    size_ru = re.sub(r'\bcm\b', 'см', size)
    size_en = re.sub(r'\bсм\b', 'cm', size)
    meta_ru = ' · '.join(x for x in (tech_ru, size_ru) if x)
    meta_en = ' · '.join(x for x in (tech_en, size_en) if x)
    badge = '<span class="badge" data-ru="Продано" data-en="Sold">Продано</span>' if w['sold'] else ''
    title_html = f'<span class="t-title">{esc(w["title"])}</span>' if w['title'] else ''
    candy = ' candy' if w.get('artist') == 'julie-jaler' else ''
    nav = ''
    if multi:
        nav = ('<button class="ti-nav ti-prev" aria-label="Предыдущий ракурс">‹</button>'
               '<button class="ti-nav ti-next" aria-label="Следующий ракурс">›</button>'
               f'<span class="ti-count">1 / {len(imgs)}</span>')
    thumbs = [thumb_path(i) for i in imgs]
    return f'''<figure class="tile reveal{' multi' if multi else ''}{candy}" data-artist="{esc(w.get('artist',''))}" data-title="{esc(w['title'])}" data-meta-ru="{esc(meta_ru)}" data-meta-en="{esc(meta_en)}" data-sold="{'1' if w['sold'] else '0'}" data-images="{esc('|'.join(imgs))}" data-thumbs="{esc('|'.join(thumbs))}" data-full="{esc(cover)}">
  <div class="tile-img"><img src="{esc(thumbs[0])}" alt="{esc(w['title'])}" loading="lazy" decoding="async">{badge}{nav}</div>
  <figcaption>{title_html}<span class="t-meta" data-ru="{esc(meta_ru)}" data-en="{esc(meta_en)}">{esc(meta_ru)}</span></figcaption>
</figure>'''

# ---------- главная ----------
def build_index():
    featured = []
    for key in ('julie-jaler', 'accardi', 'van-apple', 'kiko'):
        featured += ALL_WORKS[key][:3]
    tiles = ''.join(work_tile(w, i) for i, w in enumerate(featured))
    artist_cards = ''.join(f'''<a class="a-card reveal" href="artist-{a['slug']}.html" data-sru="{esc(a['sort_ru'])}" data-sen="{esc(a['sort_en'])}">
      <div class="a-card-img{' logo' if a.get('logo') else ''}"><img src="{esc(thumb_path(a['portrait']))}" alt="{esc(a['name_ru'])}" loading="lazy" decoding="async"></div>
      <div class="a-card-name" data-ru="{esc(a['name_ru'])}" data-en="{esc(a['name_en'])}">{esc(a['name_ru'])}</div>
      {f'<div class="a-card-years" data-ru="{esc(a["years"])}" data-en="{esc(a["years_en"])}">{esc(a["years"])}</div>' if a['years'] else ''}
    </a>''' for a in ARTISTS)
    body = f'''
<section class="hero">
  <div class="hero-bg">
    <video class="hero-video" id="heroVideo" muted loop playsinline autoplay preload="auto"
           poster="{IMG}/site/hero-poster.jpg"
           data-desktop="assets/video/hero-desktop.mp4" data-mobile="assets/video/hero-mobile.mp4"
           data-poster-desktop="{IMG}/site/hero-poster.jpg" data-poster-mobile="{IMG}/site/hero-poster-mobile.jpg"></video>
  </div>
  <div class="hero-in">
    <h1 class="hero-logo">{LOGO_SVG}</h1>
    <p class="hero-sub" data-ru="Коллекция живописи и скульптуры современных европейских художников" data-en="A collection of paintings and sculptures by modern European artists">Коллекция живописи и скульптуры современных европейских художников</p>
    <a class="btn btn-glass" href="collections.html" data-ru="Смотреть работы" data-en="Artworks">Смотреть работы</a>
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
    <p class="vc-kicker" data-ru="Контакты" data-en="Contacts">Контакты</p>
    <h2 data-ru="Приходите посмотреть" data-en="Come and see">Приходите посмотреть</h2>
    <p class="vc-addr">{esc(CONTACTS['address'])}</p>
    <a class="btn btn-dark" href="contacts.html" data-ru="Контакты" data-en="Contacts">Контакты</a>
  </div>
</section>
'''
    return head('Art Gallery Tolstoy — современное искусство в Москве',
                'Галерея современного европейского искусства в Москве. Живопись и скульптура.',
                '', home=True) + body + footer()

# ---------- художники ----------
def build_artists():
    rows = ''
    for a in ARTISTS:
        cnt = len(ALL_WORKS[a['key']])
        vcnt = len(artist_videos(a['key']))
        def _ru(n, one, few, many):
            if n % 10 == 1 and n % 100 != 11: return one
            if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14: return few
            return many
        w_ru = f'{cnt} {_ru(cnt, "работа", "работы", "работ")}'
        w_en = f'{cnt} work{"s" if cnt != 1 else ""}'
        v_ru = f'{vcnt} видео'
        v_en = f'{vcnt} video{"s" if vcnt != 1 else ""}'
        if cnt and vcnt:
            cnt_txt, cnt_en = f'{w_ru} · {v_ru}', f'{w_en} · {v_en}'
        elif vcnt:
            cnt_txt, cnt_en = v_ru, v_en
        elif cnt:
            cnt_txt, cnt_en = w_ru, w_en
        else:
            cnt_txt, cnt_en = 'Скоро', 'Coming soon'
        rows += f'''<a class="artist-row reveal" href="artist-{a['slug']}.html" data-sru="{esc(a['sort_ru'])}" data-sen="{esc(a['sort_en'])}">
      <div class="ar-img{' logo' if a.get('logo') else ''}"><img src="{esc(thumb_path(a['portrait']))}" alt="{esc(a['name_ru'])}" loading="lazy" decoding="async"></div>
      <div class="ar-txt">
        {f'<p class="ar-years" data-ru="{esc(a["years"])}" data-en="{esc(a["years_en"])}">{esc(a["years"])}</p>' if a['years'] else ''}
        <h2 class="ar-name" data-ru="{esc(a['name_ru'])}" data-en="{esc(a['name_en'])}">{esc(a['name_ru'])}</h2>
        <p class="ar-en" data-ru="{esc(a['name_en'])}" data-en="{esc(a['name_ru'])}">{esc(a['name_en'])}</p>
        <p class="ar-short" data-ru="{esc(a['short_ru'])}" data-en="{esc(a['short_en'])}">{esc(a['short_ru'])}</p>
        <span class="ar-link" data-ru="{cnt_txt} →" data-en="{cnt_en} →">{cnt_txt} →</span>
      </div>
    </a>'''
    body = f'''
<section class="page-head container">
  <h1 data-ru="Художники / Скульпторы" data-en="Artists / Sculptors">Художники / Скульпторы</h1>
</section>
<section class="container artist-list">{rows}</section>
'''
    return head('Художники — Art Gallery Tolstoy', 'Художники и скульпторы Арт Галереи Толстой', 'artists') + body + footer()

# ---------- страница художника ----------
VIDEO_TITLES = {'x-ray-suitcase': 'X-Ray — Suitcase', 'x-ray-birkin': 'X-Ray — Birkin'}

def artist_videos(key):
    return sorted(glob.glob(os.path.join(ROOT, f'{IMG}/works/{key}-video/*.mp4')))

def build_artist(a):
    works = ALL_WORKS[a['key']]
    tiles = ''.join(work_tile(w, i) for i, w in enumerate(works))
    vids = artist_videos(a['key'])
    vtiles = ''
    for v in vids:
        rel = os.path.relpath(v, ROOT).replace(os.sep, '/')
        stem = os.path.splitext(os.path.basename(v))[0]
        name = VIDEO_TITLES.get(stem, stem.replace('-', ' ').title())
        poster = poster_path(rel)
        pattr = f' poster="{esc(poster)}"' if poster else ''
        vtiles += f'''<figure class="tile reveal"><div class="tile-img"><video src="{esc(rel)}"{pattr} muted loop playsinline preload="none"></video></div><figcaption><span class="t-title">{esc(name)}</span></figcaption></figure>'''
    video_block = ''
    if vtiles:
        vh_ru, vh_en = 'Видео-работы', 'Video works'
        video_block = f'''
<section class="container block">
  <div class="block-head reveal"><h2 data-ru="{vh_ru}" data-en="{vh_en}">{vh_ru}</h2></div>
  <div class="grid grid-video">{vtiles}</div>
</section>'''
    if works:
        gallery = f'<div class="grid">{tiles}</div>'
        gh_ru, gh_en = 'Работы', 'Works'
    elif vids:
        gallery = ''   # только видео — блок «Работы» не показываем
        gh_ru, gh_en = '', ''
    else:
        gallery = ('<p class="works-soon reveal" data-ru="Работы этого художника скоро появятся." '
                   'data-en="Works by this artist are coming soon.">Работы этого художника скоро появятся.</p>')
        gh_ru, gh_en = 'Работы', 'Works'
    body = f'''
<section class="artist-hero">
  <div class="ah-img{' logo' if a.get('logo') else ''}"><img src="{esc(a['portrait'])}" alt="{esc(a['name_ru'])}" style="object-position:{a.get('hero_pos','center center')}"></div>
  <div class="ah-txt container">
    <h1 class="ah-name" data-ru="{esc(a['name_ru'])}" data-en="{esc(a['name_en'])}">{esc(a['name_ru'])}</h1>
  </div>
</section>
<section class="container artist-bio">
  <p class="bio reveal" data-ru="{esc(a['bio_ru'])}" data-en="{esc(a['bio_en'])}">{esc(a['bio_ru'])}</p>
</section>
{f'''<section class="container block">
  <div class="block-head reveal"><h2 data-ru="{gh_ru}" data-en="{gh_en}">{gh_ru}</h2></div>
  {gallery}
</section>''' if gallery else ''}{video_block}
'''
    return head(f'{a["name_ru"]} — Art Gallery Tolstoy', esc(a['short_ru']), 'artists') + body + footer()

# ---------- коллекция ----------
def build_collections():
    filters = '<button class="filter active" data-f="all" data-ru="Все" data-en="All">Все</button>'
    for a in ARTISTS:
        # показываем ВСЕХ художников в фильтре, даже без работ (работы ещё в процессе).
        # клик по «пустому» покажет заглушку со ссылкой на страницу художника (см. main.js)
        filters += (f'<button class="filter" data-f="{a["key"]}" data-sru="{esc(a["sort_ru"])}" data-sen="{esc(a["sort_en"])}" '
                    f'data-ru="{esc(a["name_ru"])}" data-en="{esc(a["name_en"])}">{esc(a["name_ru"])}</button>')
    tiles = ''
    for a in ARTISTS:
        for w in ALL_WORKS[a['key']]:
            tiles += work_tile(w)   # data-artist проставляется внутри work_tile
    body = f'''
<section class="page-head container">
  <p class="ph-kicker" data-ru="Живопись и скульптура" data-en="Paintings and sculpture">Живопись и скульптура</p>
  <h1 data-ru="Коллекция" data-en="Collection">Коллекция</h1>
</section>
<section class="container">
  <div class="filters" id="filters">{filters}</div>
  <div class="grid" id="collGrid">{tiles}</div>
  <div class="works-soon coll-empty" id="collEmpty" hidden>
    <span data-ru="Работы этого художника скоро появятся." data-en="Works by this artist are coming soon.">Работы этого художника скоро появятся.</span>
    <a class="link-more" id="collEmptyLink" href="#" data-ru="Открыть страницу художника →" data-en="Open the artist page →">Открыть страницу художника →</a>
  </div>
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
  <h1 data-ru="Контакты" data-en="Contacts">Контакты</h1>
</section>
<section class="container visit-contact">
  <div class="visit-info reveal">
    <div class="vi-block">
      <div class="vi-label" data-ru="Адрес" data-en="Address">Адрес</div>
      <p class="vi-big" data-ru="{esc(c['address'])}" data-en="Novinsky Blvd, 1/2, Moscow">{esc(c['address'])}</p>
    </div>
    <div class="vi-block">
      <div class="vi-label" data-ru="Контакты" data-en="Contacts">Контакты</div>
      <p><a href="mailto:{c['email1']}">{c['email1']}</a> · {c['phone1']}</p>
      <p><a href="mailto:{c['email2']}">{c['email2']}</a> · {c['phone2']}</p>
    </div>
    <div class="vi-block">
      <div class="vi-label" data-ru="Соцсети" data-en="Social">Соцсети</div>
      <p><a href="{c['fb']}" target="_blank" rel="noopener">Facebook</a></p>
    </div>
  </div>
</section>
<section class="map-wrap">
  <iframe src="https://maps.google.com/maps?q={map_q}&z=15&output=embed" loading="lazy" title="Карта"></iframe>
</section>
'''
    return head('Контакты — Art Gallery Tolstoy', 'Контакты и адрес Арт Галереи Толстой', 'contacts') + body + footer()

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
w('contacts.html', build_visit())
print('Работ в каталоге по художникам:', {k: len(v) for k, v in ALL_WORKS.items()})
print('Готово.')
