# SmartPick — Find Your Perfect Phone

№24 жоба «Смартфондар каталогы». Жоба толығымен **Python** тілінде жазылған: каталог логикасы, консоль мәзірі және веб-сервер.
Сайт үш тілде (қазақ, орыс, ағылшын), ашық және қараңғы тақырыппен жұмыс істейді.

## Файлдар

```
SmartPick/
├── smartphones.py      ← жобаның ядросы: барлық функциялар + консоль мәзірі
├── server.py           ← Python веб-сервері, smartphones.py функцияларын шақырады
├── data/phones.csv     ← 52 смартфон, 16 бренд
├── web/
│   ├── index.html      ← сайт беті (HTML, CSS, JavaScript)
│   ├── favicon.png
│   └── favicon.ico
├── docs/logo.png       ← жоба логотипі
├── run_site.bat        ← сайтты компьютерде ашу (http://localhost:8000)
├── run_console.bat     ← консоль мәзірі
├── requirements.txt    ← сыртқы кітапхана жоқ
└── render.yaml         ← Render хостингіне арналған баптау
```

## Іске қосу

| Не | Қалай |
|---|---|
| Сайт (компьютерде) | `run_site.bat` немесе `python server.py` → http://localhost:8000 |
| Консоль мәзірі | `run_console.bat` немесе `python smartphones.py` |
| Интернетте | Render: Start Command `python server.py` |

Python 3.10 немесе жаңасы керек. Қосымша кітапхана орнатудың қажеті жоқ.

## Функциялар (smartphones.py)

`load_catalog`, `save_catalog`, `read_int`, `read_text`, `validate`, `show_catalog`, `add_phone`, `search`,
`find_by_id`, `update_phone`, `delete_phone`, `cheapest`, `most_expensive`, `winner`, `compare_camera`,
`compare_phones`, `average_price`, `count_by_brand`, `show_statistics`, `search_menu`, `menu` және т.б. — барлығы 27.

Бір функцияны әртүрлі жолмен шақыру (Method Overloading баламасы):

- `add_phone()` — пернетақтадан сұрайды; `add_phone("Samsung", "A55", price=..., ...)` — бірден қосады
- `search(brand="Apple")`, `search(min_price=100000, max_price=300000)`, `search(brand="Samsung", memory=256)`
- `compare_camera(a, b)` — смартфон сөздіктерін де, ID нөмірлерін де қабылдайды (`isinstance` арқылы)
- `update_phone()` және `update_phone(5, price=199990)`; `delete_phone()` және `delete_phone(5)`
- `read_int(prompt, minimum=1, current=None)` — әдепкі параметрлер

Консоль мәзірінде `match`, циклдар, тармақталу және қателерді өңдеу (`try/except`) қолданылады.

## API (server.py)

| Сұраныс | Не істейді |
|---|---|
| `GET /api/phones` | сүзгі және сұрыптау (brand, min, max, memory, ram, battery, camera, q, sort) |
| `GET /api/stats` | статистика |
| `GET /api/compare?a=1&b=2` | екі смартфонды салыстыру |
| `POST /api/phones` | жаңа смартфон қосу |
| `POST /api/phones/update` | өзгерту |
| `POST /api/phones/delete` | өшіру |

## Render-ге жүктеу

1. Репозиторийді GitHub-қа жүктеңіз.
2. Render → New → Web Service → репозиторийді таңдаңыз.
3. Language: `Python 3`, Build Command: `pip install -r requirements.txt`, Start Command: `python server.py`, тариф: Free.

Ескерту: тегін Render-де сайт 15 минут қолданылмаса ұйықтайды, ал қосылған немесе өшірілген смартфондар қайта іске қосқанда сақталмайды.
