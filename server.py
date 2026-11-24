# Смартфондар каталогы - Python веб-сервері (Python 3.10+)
# Барлық логика smartphones.py файлында: сервер тек оның функцияларын шақырып, нәтижені JSON етіп береді.
# Іске қосу:  python server.py   ->   браузерде http://localhost:8000
# Тек стандартты кітапхана қолданылады (pip қажет емес).

import json
import os
import platform
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import smartphones as sp

PORT = int(os.environ.get("PORT", 8000))  # Render өз портын осы айнымалы арқылы береді
HTML_FILE = os.path.join(sp.BASE, "web", "index.html")
lock = threading.Lock()


def num(params, key, default=0):
    try:
        return int(params.get(key, [""])[0])
    except ValueError:
        return default


def numbers(form):
    """Формадан бес сандық өрісті оқиды (бөлшек сан дөңгелектенеді)."""
    values = {}
    for key in sp.NUMBER_KEYS:
        try:
            values[key] = round(float(form.get(key, [""])[0]))
        except ValueError:
            values[key] = 0
    return values


# ---------- Сүзгі: smartphones.search() функциясын пайдаланады ----------
def filter_phones(params):
    brand = params.get("brand", [""])[0] or None
    high = num(params, "max", -1)
    result = sp.search(brand=brand, min_price=num(params, "min"),
                       max_price=None if high < 0 else high, memory=num(params, "memory"))
    text = params.get("q", [""])[0].strip().lower()
    result = [p for p in result
              if p["ram"] >= num(params, "ram") and p["battery"] >= num(params, "battery")
              and p["camera"] >= num(params, "camera") and (not text or text in sp.name(p).lower())]
    sort = params.get("sort", [""])[0]
    if "-" in sort:
        key, direction = sort.split("-", 1)
        if key in sp.NUMBER_KEYS:
            result.sort(key=lambda p: p[key], reverse=(direction == "desc"))
    return result


def stats():
    counts = sp.count_by_brand()
    return {"count": len(sp.catalog), "cheapest": sp.cheapest(), "priciest": sp.most_expensive(),
            "average": sp.average_price(), "brands": list(counts), "byBrand": counts}


def compare(a, b):
    rows = []
    for label, key, more_is_better in zip(sp.NUMBER_LABELS, sp.NUMBER_KEYS, sp.MORE_IS_BETTER):
        rows.append({"label": label, "key": key, "a": a[key], "b": b[key],
                     "winner": sp.winner(a[key], b[key], more_is_better)})
    camera_best = sp.compare_camera(a["id"], b["id"])
    return {"a": a, "b": b, "rows": rows, "diff": abs(a["price"] - b["price"]),
            "camera": {"winner": camera_best, "diff": abs(a["camera"] - b["camera"])}}


# ---------- HTTP сервер ----------
class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        params = parse_qs(url.query)
        with lock:
            if url.path in ("/", "/index.html"):
                with open(HTML_FILE, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif url.path in ("/favicon.png", "/favicon.ico"):
                with open(os.path.join(sp.BASE, "web", url.path[1:]), "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "image/png" if url.path.endswith("png") else "image/x-icon")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "max-age=86400")
                self.end_headers()
                self.wfile.write(body)
            elif url.path == "/api/info":
                self.send_json({"server": "Python", "version": platform.python_version()})
            elif url.path == "/api/phones":
                self.send_json({"items": filter_phones(params), "total": len(sp.catalog)})
            elif url.path == "/api/stats":
                self.send_json(stats())
            elif url.path == "/api/recommend":
                try:
                    items = sp.recommend(num(params, "budget", -1), params.get("priority", ["balance"])[0])
                    self.send_json({"items": items})
                except ValueError as e:
                    self.send_json({"error": str(e)}, 400)
            elif url.path == "/api/compare":
                a, b = sp.find_by_id(num(params, "a", -1)), sp.find_by_id(num(params, "b", -1))
                if a is None or b is None:
                    self.send_json({"error": "Смартфон табылмады."}, 404)
                else:
                    self.send_json(compare(a, b))
            else:
                self.send_json({"error": "Бет табылмады."}, 404)

    def do_HEAD(self):
        # Render сайттың жұмысын HEAD сұранысымен тексеруі мүмкін: денесіз 200 жауап береміз
        self.send_response(200 if urlparse(self.path).path in ("/", "/index.html") else 404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)
        with lock:
            if path == "/api/phones/delete":
                if sp.delete_phone(num(form, "id", -1)):
                    self.send_json({"ok": True})
                else:
                    self.send_json({"error": "Смартфон табылмады."}, 404)
                return
            if path not in ("/api/phones", "/api/phones/update"):
                self.send_json({"error": "Бет табылмады."}, 404)
                return
            brand = form.get("brand", [""])[0].strip()
            model = form.get("model", [""])[0].strip()
            values = numbers(form)
            problem = sp.validate(brand, model, values.values())
            if problem:
                self.send_json({"error": problem}, 400)
            elif path == "/api/phones":
                self.send_json({"ok": True, "phone": sp.add_phone(brand, model, **values)})
            elif sp.update_phone(num(form, "id", -1), brand=brand, model=model, **values):
                self.send_json({"ok": True})
            else:
                self.send_json({"error": "Смартфон табылмады."}, 404)

    def log_message(self, fmt, *args):
        pass  # консольді ластамау үшін


if __name__ == "__main__":
    sp.load_catalog()
    print(f"Python сервері іске қосылды: http://localhost:{PORT}", flush=True)
    print(f"Каталогта {len(sp.catalog)} смартфон. Тоқтату үшін Ctrl+C басыңыз.", flush=True)
    try:
        ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nСервер тоқтатылды.")
