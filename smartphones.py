# Смартфондар каталогы - Python нұсқасы (Python 3.10+)
# Бұл файл - жобаның "ядросы": консоль мәзірі де, веб-сервер (server.py) де осы функцияларды қолданады.
# Іске қосу (консоль):  python smartphones.py
# Бір функция әртүрлі жолмен шақырылады: әдепкі параметрлер (None), **kwargs және isinstance арқылы тексеру.

import csv
import os

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE, "data", "phones.csv")
FIELDS = ["brand", "model", "price", "memory", "ram", "battery", "camera"]
NUMBER_KEYS = ["price", "memory", "ram", "battery", "camera"]
NUMBER_LABELS = ["Баға, ₸", "Жады, GB", "RAM, GB", "Аккумулятор, mAh", "Камера, MP"]
MORE_IS_BETTER = [False, True, True, True, True]
PROMPTS = {"price": "Баға (₸)", "memory": "Жады (GB)", "ram": "RAM (GB)",
           "battery": "Аккумулятор (mAh)", "camera": "Камера (MP)"}

# Каталог: әр смартфон сөздік (dict) ретінде сақталады
catalog = []
next_id = 1


# ---------- Деректер: CSV файлымен жұмыс ----------
def load_catalog():
    """CSV файлынан каталогты оқиды, әр смартфонға ID береді."""
    global next_id
    catalog.clear()
    next_id = 1
    with open(CSV_FILE, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter=";"):
            phone = {"id": next_id, "brand": row["brand"], "model": row["model"]}
            for key in NUMBER_KEYS:
                phone[key] = int(row[key])
            catalog.append(phone)
            next_id += 1


def save_catalog():
    """Бүкіл каталогты CSV файлына қайта жазады."""
    try:
        with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";", lineterminator="\n")
            writer.writerow(FIELDS)
            for p in catalog:
                writer.writerow([p[k] for k in FIELDS])
    except OSError as e:
        print(f"  Қате: файлға жазу мүмкін болмады - {e}")


# ---------- Енгізуді тексеру ----------
def read_int(prompt, minimum=1, current=None):
    """Бүтін сан енгізуді тексереді. current берілсе, бос Enter ескі мәнді қалдырады."""
    while True:
        text = input(prompt if current is None else f"{prompt} [{current}]: ").strip()
        if current is not None and text == "":
            return current
        try:
            n = int(text)
            if n >= minimum:
                return n
            print(f"  Қате: сан {minimum}-ден кем болмауы керек.")
        except ValueError:
            print("  Қате: сан енгізіңіз.")


def check_text(s):
    if not s:
        return "бос болмауы керек."
    if ";" in s:
        return "«;» белгісін қолдануға болмайды."
    return None


def read_text(prompt, current=None):
    """Бос емес мәтін енгізуді талап етеді. current берілсе, бос Enter ескі мәнді қалдырады."""
    while True:
        s = input(prompt if current is None else f"{prompt} [{current}]: ").strip()
        if current is not None and s == "":
            return current
        error = check_text(s)
        if error is None:
            return s
        print(f"  Қате: {error}")


def validate(brand, model, values):
    """Веб-сервер үшін: барлық өрісті бірден тексереді. Қате болмаса None қайтарады."""
    if not brand or not model:
        return "Бренд пен модельді толтырыңыз."
    if ";" in brand or ";" in model:
        return "Атауда «;» белгісі болмауы керек."
    for v in values:
        if v <= 0:
            return "Баға, жады, RAM, аккумулятор және камера оң сан болуы керек."
    return None


def capitalize(s):
    return s[:1].upper() + s[1:]


def name(p):
    return f"{p['brand']} {p['model']}"


# ---------- Каталогты шығару ----------
def show_catalog(phones=None):
    """Каталогты кесте түрінде шығарады. phones берілмесе - толық каталог."""
    if phones is None:
        phones = catalog
    if not phones:
        print("Каталог бос.")
        return
    print(f"\n{'ID':<4}{'Бренд':<9}{'Модель':<19}{'Баға, ₸':>9}{'Жады':>7}{'RAM':>5}{'mAh':>8}{'Камера':>8}")
    print("-" * 69)
    for p in phones:
        print(f"{p['id']:<4}{p['brand']:<9}{p['model']:<19}{p['price']:>9}{p['memory']:>7}"
              f"{p['ram']:>5}{p['battery']:>8}{p['camera']:>8}")


# ---------- Смартфон қосу ----------
def add_phone(brand=None, model=None, **numbers):
    """Смартфон қосады. Параметр берілмесе - мәліметті пайдаланушыдан сұрайды
    (параметрсіз шақырсаң - пернетақтадан сұрайды, параметрмен - бірден қосады)."""
    global next_id
    if brand is None:
        brand = read_text("Бренд: ")
        model = read_text("Модель: ")
        numbers = {key: read_int(PROMPTS[key] + ": ") for key in NUMBER_KEYS}
    phone = {"id": next_id, "brand": capitalize(brand), "model": model}
    for key in NUMBER_KEYS:
        phone[key] = numbers[key]
    catalog.append(phone)
    next_id += 1
    save_catalog()
    return phone


# ---------- Іздеу ----------
def search(brand=None, min_price=0, max_price=None, memory=0):
    """Смартфондарды іздейді. Берілмеген параметр сүзгіге қатыспайды.
    search(brand="Apple"), search(min_price=1, max_price=2), search(memory=256),
    search(brand="Samsung", memory=256) - кез келген сүзгіні бірге қолдануға болады."""
    result = []
    for p in catalog:
        if brand is not None and p["brand"].lower() != brand.strip().lower():
            continue
        if p["price"] < min_price:
            continue
        if max_price is not None and p["price"] > max_price:
            continue
        if p["memory"] < memory:
            continue
        result.append(p)
    return result


def find_by_id(phone_id):
    for p in catalog:
        if p["id"] == phone_id:
            return p
    return None


# ---------- Өзгерту және жою ----------
def update_phone(phone_id=None, **changes):
    """Смартфонды өзгертеді. ID берілмесе - пайдаланушыдан сұрайды. Табылмаса False қайтарады."""
    interactive = phone_id is None
    if interactive:
        p = pick_phone("Өзгертілетін смартфон ID: ")
        print("Жаңа мәнді енгізіңіз (өзгертпеу үшін Enter басыңыз):")
        changes = {"brand": read_text("Бренд", p["brand"]), "model": read_text("Модель", p["model"])}
        for key in NUMBER_KEYS:
            changes[key] = read_int(PROMPTS[key], 1, p[key])
        phone_id = p["id"]
    p = find_by_id(phone_id)
    if p is None:
        return False
    if "brand" in changes:
        changes["brand"] = capitalize(changes["brand"])
    p.update(changes)
    save_catalog()
    if interactive:
        print(f"Өзгертілді: {name(p)}")
    return True


def delete_phone(phone_id=None):
    """Смартфонды жояды. ID берілмесе - пайдаланушыдан сұрап, растауын күтеді."""
    interactive = phone_id is None
    if interactive:
        p = pick_phone("Жойылатын смартфон ID: ")
        answer = input(f"{name(p)} жойылсын ба? (1 - иә, 0 - жоқ): ").strip().lower()
        if answer not in ("1", "иә", "ия", "y"):
            print("Жою тоқтатылды.")
            return False
        phone_id = p["id"]
    p = find_by_id(phone_id)
    if p is None:
        return False
    catalog.remove(p)
    save_catalog()
    if interactive:
        print(f"Жойылды: {name(p)}")
    return True


# ---------- Ең арзан / ең қымбат ----------
def cheapest(phones=None):
    """Ең арзан смартфонды циклмен табады. Бос тізімде None қайтарады."""
    if phones is None:
        phones = catalog
    best = None
    for p in phones:
        if best is None or p["price"] < best["price"]:
            best = p
    return best


def most_expensive(phones=None):
    """Ең қымбат смартфонды циклмен табады. Бос тізімде None қайтарады."""
    if phones is None:
        phones = catalog
    best = None
    for p in phones:
        if best is None or p["price"] > best["price"]:
            best = p
    return best


def describe(p):
    return "жоқ" if p is None else f"{name(p)} - {p['price']} ₸"


# ---------- Салыстыру ----------
def pick_phone(prompt):
    """ID бойынша смартфон таңдатады."""
    while True:
        p = find_by_id(read_int(prompt))
        if p is not None:
            return p
        print("  Қате: мұндай ID-мен смартфон жоқ.")


def winner(x, y, more_is_better=True):
    """0 - тең, 1 - бірінші жақсы, 2 - екінші жақсы."""
    if x == y:
        return 0
    return 1 if (x > y) == more_is_better else 2


def compare_camera(a, b):
    """Камерасы жақсы телефонды қайтарады (тең болса None).
    a, b - смартфон (dict) немесе оның ID-і (int) болуы мүмкін."""
    if isinstance(a, int):
        a = find_by_id(a)
    if isinstance(b, int):
        b = find_by_id(b)
    if a is None or b is None:
        return None
    w = winner(a["camera"], b["camera"])
    return None if w == 0 else (a if w == 1 else b)


def print_camera_result(a, b):
    print(f"{a['model']}: {a['camera']} MP  |  {b['model']}: {b['camera']} MP")
    best = compare_camera(a, b)
    if best is None:
        print("Камера көрсеткіштері тең.")
    else:
        print(f"Камерасы жақсы: {name(best)} (+{abs(a['camera'] - b['camera'])} MP)")


def compare_phones(a, b):
    """Екі смартфонды барлық көрсеткіш бойынша кесте етіп салыстырады."""
    print(f"\n{'':<18}{a['model']:<18}{b['model']:<18}Артық")
    print("-" * 70)
    score_a = score_b = 0
    for label, key, more_is_better in zip(NUMBER_LABELS, NUMBER_KEYS, MORE_IS_BETTER):
        x, y = a[key], b[key]
        w = winner(x, y, more_is_better)
        better = "тең" if w == 0 else (a["model"] if w == 1 else b["model"])
        if w == 1:
            score_a += 1
        elif w == 2:
            score_b += 1
        print(f"{label:<18}{x:<18}{y:<18}{better}")
    print(f"Баға айырмасы: {abs(a['price'] - b['price'])} ₸")
    print(f"Ұпай: {a['model']} {score_a} - {score_b} {b['model']}")


# ---------- Статистика ----------
def average_price(phones=None):
    """Орташа бағаны есептейді. Бос тізімде 0 қайтарады."""
    if phones is None:
        phones = catalog
    if not phones:
        return 0
    total = 0
    for p in phones:
        total += p["price"]
    return total / len(phones)


def count_by_brand():
    counts = {}
    for p in catalog:
        counts[p["brand"]] = counts.get(p["brand"], 0) + 1
    return counts


def show_statistics():
    print(f"Смартфон саны: {len(catalog)}")
    print("Ең арзан: ", describe(cheapest()))
    print("Ең қымбат:", describe(most_expensive()))
    print(f"Орташа баға: {average_price():.0f} ₸")
    parts = [f"{brand}: {n}" for brand, n in count_by_brand().items()]
    print("Бренд бойынша:", ", ".join(parts))


# ---------- Мәзір ----------
# ---------- Бюджет бойынша таңдау ----------
# priority -> қай көрсеткіштер ұпайға есептеледі ("balance" - төртеуі де)
PRIORITIES = {"camera": ("camera",), "battery": ("battery",), "memory": ("memory",),
              "ram": ("ram",), "balance": ("camera", "battery", "memory", "ram")}


def recommend(budget, priority="balance", limit=3):
    """Бюджетке сыятын ең жақсы смартфондарды қайтарады (ұпайы бойынша кему ретімен).
    Ұпай: әр көрсеткіш сүзілген смартфондар ішіндегі ең үздігіне бөлінеді (0..1), қосылады.
    Ұпай тең болса, арзаны алда тұрады. Қате берілсе ValueError шығарады."""
    if isinstance(budget, bool) or not isinstance(budget, int) or budget <= 0:
        raise ValueError("Бюджет оң бүтін сан болуы керек.")
    if priority not in PRIORITIES:
        raise ValueError("Басымдық белгісіз: " + str(priority))
    candidates = [p for p in catalog if p["price"] <= budget]
    if not candidates:
        return []
    keys = PRIORITIES[priority]
    best = {k: max(p[k] for p in candidates) for k in keys}
    candidates.sort(key=lambda p: (-sum(p[k] / best[k] for k in keys), p["price"]))
    return candidates[:limit]


def recommend_menu():
    """Бюджет пен басымдықты сұрап, 3 үздік смартфонды шығарады."""
    budget = read_int("Бюджет (₸): ")
    print("1.Камера  2.Аккумулятор  3.Жады  4.RAM  5.Тепе-тең")
    kind = read_int("Басымдық: ", 1)
    priority = ["camera", "battery", "memory", "ram", "balance"][kind - 1] if kind <= 5 else "balance"
    result = recommend(budget, priority)
    if not result:
        print(f"{budget} ₸ бюджетке сыятын смартфон жоқ.")
        return
    print(f"Бюджетке сай үздік {len(result)} смартфон:")
    show_catalog(result)


def search_menu():
    """Іздеу түрін таңдатып, нәтижені шығарады."""
    print("\n1.Бренд бойынша  2.Баға бойынша  3.Жады бойынша  4.Бренд + жады")
    kind = read_int("Іздеу түрі: ", 0)
    match kind:
        case 1:
            result = search(brand=read_text("Бренд: "))
        case 2:
            low = read_int("Ең төменгі баға: ", 0)
            high = read_int("Ең жоғарғы баға: ", low)
            result = search(min_price=low, max_price=high)
        case 3:
            result = search(memory=read_int("Жады (GB, ең аз): "))
        case 4:
            brand = read_text("Бренд: ")
            result = search(brand=brand, memory=read_int("Жады (GB, ең аз): "))
        case _:
            print("  Қате: 1-4 аралығында таңдаңыз.")
            return
    print(f"Табылды: {len(result)}" if result else "Ештеңе табылмады.")
    show_catalog(result)


def menu():
    """Негізгі мәзір: пайдаланушы бірнеше әрекетті қайталап орындай алады."""
    while True:
        print(f"\n===== СМАРТФОНДАР КАТАЛОГЫ ({len(catalog)} смартфон) =====")
        print("1.Смартфон қосу      2.Іздеу             3.Камераны салыстыру\n"
              "4.Екі смартфонды салыстыру              5.Ең арзан / ең қымбат\n"
              "6.Статистика         7.Каталогты шығару  8.Өзгерту\n"
              "9.Жою               10.Бюджет бойынша таңдау   0.Шығу")
        choice = read_int("Таңдау: ", 0)
        match choice:
            case 0:
                print("Сау болыңыз!")
                break
            case 1:
                p = add_phone()
                print(f"Қосылды: {name(p)} (ID {p['id']})")
            case 2:
                search_menu()
            case 3 | 4:
                if len(catalog) < 2:
                    print("Салыстыру үшін кемінде 2 смартфон керек.")
                    continue
                show_catalog()
                a = pick_phone("Бірінші смартфон ID: ")
                b = pick_phone("Екінші смартфон ID: ")
                if choice == 3:
                    print_camera_result(a, b)
                else:
                    compare_phones(a, b)
            case 5:
                print("Ең арзан: ", describe(cheapest()))
                print("Ең қымбат:", describe(most_expensive()))
            case 6:
                show_statistics()
            case 7:
                show_catalog()
            case 8 | 9:
                if not catalog:
                    print("Каталог бос.")
                    continue
                show_catalog()
                if choice == 8:
                    update_phone()
                else:
                    delete_phone()
            case 10:
                recommend_menu()
            case _:
                print("  Қате: мәзірде мұндай пункт жоқ.")


if __name__ == "__main__":
    try:
        load_catalog()
    except OSError:
        print(f"Қате: {CSV_FILE} файлын оқу мүмкін болмады.")
    else:
        try:
            menu()
        except (EOFError, KeyboardInterrupt):
            print("\nСау болыңыз!")
