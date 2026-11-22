import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;

// Смартфондар каталогы - Java веб-сервері (Java 17+)
// Барлық логика SmartphoneCatalog класында: сервер тек оның әдістерін шақырып, нәтижені JSON етіп береді.
// Іске қосу:  javac -encoding UTF-8 *.java  ->  java SmartphoneServer  ->  http://localhost:8080
public class SmartphoneServer {

    static final int PORT = 8080;
    static final Path HTML_FILE = SmartphoneCatalog.findBase().resolve("web").resolve("index.html");

    // ---------- Сүзгі: SmartphoneCatalog-тағы search() нұсқаларын біріктіреді ----------
    static List<SmartphoneCatalog.Phone> filter(Map<String, String> q) {
        List<SmartphoneCatalog.Phone> result = new ArrayList<>(SmartphoneCatalog.catalog);
        String brand = q.getOrDefault("brand", "");
        int memory = num(q, "memory", 0);
        if (!brand.isEmpty() && memory > 0) result.retainAll(SmartphoneCatalog.search(brand, memory));
        else if (!brand.isEmpty()) result.retainAll(SmartphoneCatalog.search(brand));
        else if (memory > 0) result.retainAll(SmartphoneCatalog.searchByMemory(memory));
        int low = num(q, "min", 0), high = num(q, "max", Integer.MAX_VALUE);
        if (low > 0 || high < Integer.MAX_VALUE) result.retainAll(SmartphoneCatalog.search(low, high));

        String text = q.getOrDefault("q", "").trim().toLowerCase();
        int ram = num(q, "ram", 0), battery = num(q, "battery", 0), camera = num(q, "camera", 0);
        result.removeIf(p -> p.ram() < ram || p.battery() < battery || p.camera() < camera
                || (!text.isEmpty() && !p.name().toLowerCase().contains(text)));

        String sort = q.getOrDefault("sort", "");
        if (sort.contains("-")) {
            String key = sort.substring(0, sort.indexOf('-'));
            Comparator<SmartphoneCatalog.Phone> cmp = Comparator.comparingInt(p -> p.get(key));
            if (sort.endsWith("desc")) cmp = cmp.reversed();
            result.sort(cmp);
        }
        return result;
    }

    // ---------- Формадан смартфон деректерін оқу ----------
    static int[] numbers(Map<String, String> f) {
        int[] v = new int[SmartphoneCatalog.NUMBER_KEYS.length];
        for (int i = 0; i < v.length; i++) {
            try {
                v[i] = (int) Math.round(Double.parseDouble(f.getOrDefault(SmartphoneCatalog.NUMBER_KEYS[i], "")));
            } catch (NumberFormatException e) {
                v[i] = 0;
            }
        }
        return v;
    }

    // ---------- JSON ----------
    static String str(String s) {
        return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
    }

    static String json(SmartphoneCatalog.Phone p) {
        if (p == null) return "null";
        return "{\"id\":" + p.id() + ",\"brand\":" + str(p.brand()) + ",\"model\":" + str(p.model())
                + ",\"price\":" + p.price() + ",\"memory\":" + p.memory() + ",\"ram\":" + p.ram()
                + ",\"battery\":" + p.battery() + ",\"camera\":" + p.camera() + "}";
    }

    static String json(List<SmartphoneCatalog.Phone> phones) {
        StringJoiner j = new StringJoiner(",", "[", "]");
        for (SmartphoneCatalog.Phone p : phones) j.add(json(p));
        return j.toString();
    }

    static String stats() {
        StringJoiner brands = new StringJoiner(",", "[", "]");
        StringJoiner counts = new StringJoiner(",", "{", "}");
        for (Map.Entry<String, Integer> e : SmartphoneCatalog.countByBrand().entrySet()) {
            brands.add(str(e.getKey()));
            counts.add(str(e.getKey()) + ":" + e.getValue());
        }
        return "{\"count\":" + SmartphoneCatalog.catalog.size()
                + ",\"cheapest\":" + json(SmartphoneCatalog.cheapest())
                + ",\"priciest\":" + json(SmartphoneCatalog.mostExpensive())
                + ",\"average\":" + SmartphoneCatalog.averagePrice()
                + ",\"brands\":" + brands + ",\"byBrand\":" + counts + "}";
    }

    static String compare(SmartphoneCatalog.Phone a, SmartphoneCatalog.Phone b) {
        StringJoiner rows = new StringJoiner(",", "[", "]");
        for (int i = 0; i < SmartphoneCatalog.NUMBER_KEYS.length; i++) {
            String key = SmartphoneCatalog.NUMBER_KEYS[i];
            int w = SmartphoneCatalog.winner(a.get(key), b.get(key), SmartphoneCatalog.MORE_IS_BETTER[i]);
            rows.add("{\"label\":" + str(SmartphoneCatalog.NUMBER_LABELS[i]) + ",\"key\":" + str(key)
                    + ",\"a\":" + a.get(key) + ",\"b\":" + b.get(key) + ",\"winner\":" + w + "}");
        }
        SmartphoneCatalog.Phone cam = SmartphoneCatalog.compareCamera(a.id(), b.id());
        return "{\"a\":" + json(a) + ",\"b\":" + json(b) + ",\"rows\":" + rows
                + ",\"diff\":" + Math.abs(a.price() - b.price())
                + ",\"camera\":{\"winner\":" + json(cam) + ",\"diff\":" + Math.abs(a.camera() - b.camera()) + "}}";
    }

    // ---------- Көмекші әдістер ----------
    static int num(Map<String, String> q, String key, int def) {
        try {
            return Integer.parseInt(q.getOrDefault(key, "").trim());
        } catch (NumberFormatException e) {
            return def;
        }
    }

    static Map<String, String> parse(String query) {
        Map<String, String> map = new HashMap<>();
        if (query == null || query.isEmpty()) return map;
        for (String pair : query.split("&")) {
            int eq = pair.indexOf('=');
            String k = eq < 0 ? pair : pair.substring(0, eq);
            String v = eq < 0 ? "" : pair.substring(eq + 1);
            map.put(URLDecoder.decode(k, StandardCharsets.UTF_8), URLDecoder.decode(v, StandardCharsets.UTF_8).trim());
        }
        return map;
    }

    static void send(HttpExchange ex, int status, String type, byte[] body) throws IOException {
        ex.getResponseHeaders().set("Content-Type", type + "; charset=utf-8");
        ex.sendResponseHeaders(status, body.length);
        try (OutputStream os = ex.getResponseBody()) {
            os.write(body);
        }
    }

    static void reply(HttpExchange ex, int status, String body) throws IOException {
        send(ex, status, "application/json", body.getBytes(StandardCharsets.UTF_8));
    }

    static void error(HttpExchange ex, int status, String message) throws IOException {
        reply(ex, status, "{\"error\":" + str(message) + "}");
    }

    // ---------- HTTP сұрауларды өңдеу ----------
    static synchronized void handle(HttpExchange ex) throws IOException {
        String path = ex.getRequestURI().getPath();
        Map<String, String> q = parse(ex.getRequestURI().getRawQuery());
        try {
            if (ex.getRequestMethod().equals("POST")) {
                Map<String, String> f = parse(new String(ex.getRequestBody().readAllBytes(), StandardCharsets.UTF_8));
                handlePost(ex, path, f);
                return;
            }
            switch (path) {
                case "/", "/index.html" -> send(ex, 200, "text/html", Files.readAllBytes(HTML_FILE));
                case "/favicon.png", "/favicon.ico" -> {
                    byte[] icon = Files.readAllBytes(HTML_FILE.resolveSibling(path.substring(1)));
                    ex.getResponseHeaders().set("Content-Type", path.endsWith("png") ? "image/png" : "image/x-icon");
                    ex.getResponseHeaders().set("Cache-Control", "max-age=86400");
                    ex.sendResponseHeaders(200, icon.length);
                    try (OutputStream os = ex.getResponseBody()) {
                        os.write(icon);
                    }
                }
                case "/api/info" -> reply(ex, 200, "{\"server\":\"Java\",\"version\":" + str(System.getProperty("java.version")) + "}");
                case "/api/phones" -> reply(ex, 200, "{\"items\":" + json(filter(q)) + ",\"total\":" + SmartphoneCatalog.catalog.size() + "}");
                case "/api/stats" -> reply(ex, 200, stats());
                case "/api/compare" -> {
                    SmartphoneCatalog.Phone a = SmartphoneCatalog.findById(num(q, "a", -1));
                    SmartphoneCatalog.Phone b = SmartphoneCatalog.findById(num(q, "b", -1));
                    if (a == null || b == null) error(ex, 404, "Смартфон табылмады.");
                    else reply(ex, 200, compare(a, b));
                }
                default -> error(ex, 404, "Бет табылмады.");
            }
        } catch (Exception e) {
            error(ex, 500, "Сервер қатесі: " + e.getMessage());
        }
    }

    static void handlePost(HttpExchange ex, String path, Map<String, String> f) throws IOException {
        switch (path) {
            case "/api/phones/delete" -> {
                if (SmartphoneCatalog.deletePhone(num(f, "id", -1))) reply(ex, 200, "{\"ok\":true}");
                else error(ex, 404, "Смартфон табылмады.");
            }
            case "/api/phones", "/api/phones/update" -> {
                String brand = f.getOrDefault("brand", ""), model = f.getOrDefault("model", "");
                int[] v = numbers(f);
                String problem = SmartphoneCatalog.validate(brand, model, v);
                if (problem != null) {
                    error(ex, 400, problem);
                } else if (path.equals("/api/phones")) {
                    SmartphoneCatalog.Phone p = SmartphoneCatalog.addPhone(brand, model, v[0], v[1], v[2], v[3], v[4]);
                    reply(ex, 200, "{\"ok\":true,\"phone\":" + json(p) + "}");
                } else if (SmartphoneCatalog.updatePhone(num(f, "id", -1), brand, model, v[0], v[1], v[2], v[3], v[4])) {
                    reply(ex, 200, "{\"ok\":true}");
                } else {
                    error(ex, 404, "Смартфон табылмады.");
                }
            }
            default -> error(ex, 404, "Бет табылмады.");
        }
    }

    public static void main(String[] args) throws IOException {
        SmartphoneCatalog.loadCatalog();
        HttpServer server = HttpServer.create(new InetSocketAddress("localhost", PORT), 0);
        server.createContext("/", SmartphoneServer::handle);
        server.start();
        System.out.println("Java сервері іске қосылды: http://localhost:" + PORT);
        System.out.println("Каталогта " + SmartphoneCatalog.catalog.size() + " смартфон. Тоқтату үшін Ctrl+C басыңыз.");
    }
}
