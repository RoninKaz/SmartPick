import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

// Смартфондар каталогы - Java нұсқасы (Java 17+)
// Бұл класс - жобаның "ядросы": консоль мәзірі де, веб-сервер (SmartphoneServer) де осы әдістерді қолданады.
// Іске қосу (консоль):  javac -encoding UTF-8 *.java   ->   java SmartphoneCatalog
public class SmartphoneCatalog {

    record Phone(int id, String brand, String model, int price, int memory, int ram, int battery, int camera) {
        int get(String key) {
            return switch (key) {
                case "price" -> price;
                case "memory" -> memory;
                case "ram" -> ram;
                case "battery" -> battery;
                case "camera" -> camera;
                default -> 0;
            };
        }

        String name() {
            return brand + " " + model;
        }
    }

    static final String[] NUMBER_KEYS = {"price", "memory", "ram", "battery", "camera"};
    static final String[] NUMBER_LABELS = {"Баға, ₸", "Жады, GB", "RAM, GB", "Аккумулятор, mAh", "Камера, MP"};
    static final boolean[] MORE_IS_BETTER = {false, true, true, true, true};

    static final List<Phone> catalog = new ArrayList<>();
    static int nextId = 1;
    static final Path CSV_FILE = findBase().resolve("data").resolve("phones.csv");
    static Scanner sc;

    // ---------- Деректер: CSV файлымен жұмыс ----------
    static Path findBase() {
        // Бағдарлама java/ папкасынан да, жоба түбірінен де іске қосыла береді
        Path here = Paths.get("").toAbsolutePath();
        if (Files.exists(here.resolve("data").resolve("phones.csv"))) return here;
        return here.getParent();
    }

    static void loadCatalog() throws IOException {
        catalog.clear();
        nextId = 1;
        List<String> lines = Files.readAllLines(CSV_FILE, StandardCharsets.UTF_8);
        for (int i = 1; i < lines.size(); i++) {          // 0-жол - тақырып
            String line = lines.get(i).trim();
            if (line.isEmpty()) continue;
            String[] c = line.split(";");
            catalog.add(new Phone(nextId++, c[0], c[1], Integer.parseInt(c[2]), Integer.parseInt(c[3]),
                    Integer.parseInt(c[4]), Integer.parseInt(c[5]), Integer.parseInt(c[6])));
        }
    }

    static void saveCatalog() {
        StringBuilder sb = new StringBuilder("brand;model;price;memory;ram;battery;camera\n");
        for (Phone p : catalog)
            sb.append(String.join(";", p.brand(), p.model(), "" + p.price(), "" + p.memory(),
                    "" + p.ram(), "" + p.battery(), "" + p.camera())).append("\n");
        try {
            Files.writeString(CSV_FILE, sb.toString(), StandardCharsets.UTF_8);
        } catch (IOException e) {
            System.out.println("  Қате: файлға жазу мүмкін болмады - " + e.getMessage());
        }
    }

    // ---------- Енгізуді тексеру ----------
    static int readInt(String prompt, int min) {
        while (true) {
            System.out.print(prompt);
            try {
                int n = Integer.parseInt(sc.nextLine().trim());
                if (n >= min) return n;
                System.out.println("  Қате: сан " + min + "-ден кем болмауы керек.");
            } catch (NumberFormatException e) {
                System.out.println("  Қате: сан енгізіңіз.");
            }
        }
    }

    // Бос жол енгізілсе - ескі мән сақталады (өзгерту үшін)
    static int readInt(String prompt, int min, int current) {
        while (true) {
            System.out.print(prompt + " [" + current + "]: ");
            String s = sc.nextLine().trim();
            if (s.isEmpty()) return current;
            try {
                int n = Integer.parseInt(s);
                if (n >= min) return n;
                System.out.println("  Қате: сан " + min + "-ден кем болмауы керек.");
            } catch (NumberFormatException e) {
                System.out.println("  Қате: сан енгізіңіз.");
            }
        }
    }

    static String readText(String prompt) {
        while (true) {
            System.out.print(prompt);
            String s = sc.nextLine().trim();
            String error = checkText(s);
            if (error == null) return s;
            System.out.println("  Қате: " + error);
        }
    }

    static String readText(String prompt, String current) {
        while (true) {
            System.out.print(prompt + " [" + current + "]: ");
            String s = sc.nextLine().trim();
            if (s.isEmpty()) return current;
            String error = checkText(s);
            if (error == null) return s;
            System.out.println("  Қате: " + error);
        }
    }

    static String checkText(String s) {
        if (s.isEmpty()) return "бос болмауы керек.";
        if (s.contains(";")) return "«;» белгісін қолдануға болмайды.";
        return null;
    }

    // Веб-сервер үшін: барлық өрісті бірден тексереді. Қате болмаса null қайтарады.
    static String validate(String brand, String model, int[] values) {
        if (brand.isEmpty() || model.isEmpty()) return "Бренд пен модельді толтырыңыз.";
        if (brand.contains(";") || model.contains(";")) return "Атауда «;» белгісі болмауы керек.";
        for (int v : values)
            if (v <= 0) return "Баға, жады, RAM, аккумулятор және камера оң сан болуы керек.";
        return null;
    }

    static String capitalize(String s) {
        return s.isEmpty() ? s : Character.toUpperCase(s.charAt(0)) + s.substring(1);
    }

    // ---------- Каталогты шығару (Method Overloading: 2 нұсқа) ----------
    static void showCatalog() {
        showCatalog(catalog);
    }

    static void showCatalog(List<Phone> phones) {
        if (phones.isEmpty()) {
            System.out.println("Каталог бос.");
            return;
        }
        System.out.printf("%n%-4s%-9s%-19s%9s%7s%5s%8s%8s%n", "ID", "Бренд", "Модель", "Баға, ₸", "Жады", "RAM", "mAh", "Камера");
        System.out.println("-".repeat(69));
        for (Phone p : phones)
            System.out.printf("%-4d%-9s%-19s%9d%7d%5d%8d%8d%n", p.id(), p.brand(), p.model(),
                    p.price(), p.memory(), p.ram(), p.battery(), p.camera());
    }

    // ---------- Смартфон қосу (Method Overloading: 3 нұсқа) ----------
    static Phone addPhone(Phone p) {
        catalog.add(p);
        saveCatalog();
        return p;
    }

    static Phone addPhone(String brand, String model, int price, int memory, int ram, int battery, int camera) {
        return addPhone(new Phone(nextId++, capitalize(brand), model, price, memory, ram, battery, camera));
    }

    static Phone addPhone() {
        String brand = readText("Бренд: ");
        String model = readText("Модель: ");
        int price = readInt("Баға (₸): ", 1);
        int memory = readInt("Жады (GB): ", 1);
        int ram = readInt("RAM (GB): ", 1);
        int battery = readInt("Аккумулятор (mAh): ", 1);
        int camera = readInt("Камера (MP): ", 1);
        Phone p = addPhone(brand, model, price, memory, ram, battery, camera);
        System.out.println("Қосылды: " + p.name() + " (ID " + p.id() + ")");
        return p;
    }

    // ---------- Іздеу (Method Overloading: 3 нұсқа) ----------
    static List<Phone> search(String brand) {
        List<Phone> result = new ArrayList<>();
        for (Phone p : catalog)
            if (p.brand().equalsIgnoreCase(brand.trim())) result.add(p);
        return result;
    }

    static List<Phone> search(int minPrice, int maxPrice) {
        List<Phone> result = new ArrayList<>();
        for (Phone p : catalog)
            if (p.price() >= minPrice && p.price() <= maxPrice) result.add(p);
        return result;
    }

    static List<Phone> search(String brand, int minMemory) {
        List<Phone> result = new ArrayList<>();
        for (Phone p : search(brand))
            if (p.memory() >= minMemory) result.add(p);
        return result;
    }

    static List<Phone> searchByMemory(int minMemory) {
        List<Phone> result = new ArrayList<>();
        for (Phone p : catalog)
            if (p.memory() >= minMemory) result.add(p);
        return result;
    }

    static Phone findById(int id) {
        for (Phone p : catalog)
            if (p.id() == id) return p;
        return null;
    }

    // ---------- Өзгерту және жою (Method Overloading: 2 нұсқадан) ----------
    static boolean updatePhone(int id, String brand, String model, int price, int memory, int ram, int battery, int camera) {
        for (int i = 0; i < catalog.size(); i++) {
            if (catalog.get(i).id() == id) {
                catalog.set(i, new Phone(id, capitalize(brand), model, price, memory, ram, battery, camera));
                saveCatalog();
                return true;
            }
        }
        return false;
    }

    static void updatePhone() {
        Phone p = pickPhone("Өзгертілетін смартфон ID: ");
        System.out.println("Жаңа мәнді енгізіңіз (өзгертпеу үшін Enter басыңыз):");
        String brand = readText("Бренд", p.brand());
        String model = readText("Модель", p.model());
        int price = readInt("Баға (₸)", 1, p.price());
        int memory = readInt("Жады (GB)", 1, p.memory());
        int ram = readInt("RAM (GB)", 1, p.ram());
        int battery = readInt("Аккумулятор (mAh)", 1, p.battery());
        int camera = readInt("Камера (MP)", 1, p.camera());
        updatePhone(p.id(), brand, model, price, memory, ram, battery, camera);
        System.out.println("Өзгертілді: " + capitalize(brand) + " " + model);
    }

    static boolean deletePhone(int id) {
        Phone p = findById(id);
        if (p == null) return false;
        catalog.remove(p);
        saveCatalog();
        return true;
    }

    static void deletePhone() {
        Phone p = pickPhone("Жойылатын смартфон ID: ");
        System.out.print(p.name() + " жойылсын ба? (1 - иә, 0 - жоқ): ");
        String answer = sc.nextLine().trim().toLowerCase();
        if (answer.equals("1") || answer.equals("иә") || answer.equals("ия") || answer.equals("y")) {
            deletePhone(p.id());
            System.out.println("Жойылды: " + p.name());
        } else {
            System.out.println("Жою тоқтатылды.");
        }
    }

    // ---------- Ең арзан / ең қымбат ----------
    static Phone cheapest() {
        Phone best = null;
        for (Phone p : catalog)
            if (best == null || p.price() < best.price()) best = p;
        return best;
    }

    static Phone mostExpensive() {
        Phone best = null;
        for (Phone p : catalog)
            if (best == null || p.price() > best.price()) best = p;
        return best;
    }

    static String describe(Phone p) {
        return p == null ? "жоқ" : p.name() + " - " + p.price() + " ₸";
    }

    // ---------- Салыстыру ----------
    static Phone pickPhone(String prompt) {
        while (true) {
            Phone p = findById(readInt(prompt, 1));
            if (p != null) return p;
            System.out.println("  Қате: мұндай ID-мен смартфон жоқ.");
        }
    }

    // 0 - тең, 1 - бірінші жақсы, 2 - екінші жақсы
    static int winner(int x, int y, boolean moreIsBetter) {
        if (x == y) return 0;
        return (x > y) == moreIsBetter ? 1 : 2;
    }

    // Камерасы жақсы телефонды қайтарады, тең болса - null (Method Overloading: 2 нұсқа)
    static Phone compareCamera(Phone a, Phone b) {
        int w = winner(a.camera(), b.camera(), true);
        return w == 0 ? null : (w == 1 ? a : b);
    }

    static Phone compareCamera(int idA, int idB) {
        Phone a = findById(idA), b = findById(idB);
        if (a == null || b == null) return null;
        return compareCamera(a, b);
    }

    static void printCameraResult(Phone a, Phone b) {
        System.out.println(a.model() + ": " + a.camera() + " MP  |  " + b.model() + ": " + b.camera() + " MP");
        Phone best = compareCamera(a, b);
        if (best == null) System.out.println("Камера көрсеткіштері тең.");
        else System.out.println("Камерасы жақсы: " + best.name()
                + " (+" + Math.abs(a.camera() - b.camera()) + " MP)");
    }

    static void comparePhones(Phone a, Phone b) {
        System.out.printf("%n%-18s%-18s%-18s%s%n", "", a.model(), b.model(), "Артық");
        System.out.println("-".repeat(70));
        int scoreA = 0, scoreB = 0;
        for (int i = 0; i < NUMBER_KEYS.length; i++) {
            int x = a.get(NUMBER_KEYS[i]), y = b.get(NUMBER_KEYS[i]);
            int w = winner(x, y, MORE_IS_BETTER[i]);
            String better = w == 0 ? "тең" : (w == 1 ? a.model() : b.model());
            if (w == 1) scoreA++;
            if (w == 2) scoreB++;
            System.out.printf("%-18s%-18d%-18d%s%n", NUMBER_LABELS[i], x, y, better);
        }
        System.out.println("Баға айырмасы: " + Math.abs(a.price() - b.price()) + " ₸");
        System.out.println("Ұпай: " + a.model() + " " + scoreA + " - " + scoreB + " " + b.model());
    }

    // ---------- Статистика ----------
    static double averagePrice() {
        if (catalog.isEmpty()) return 0;
        long total = 0;
        for (Phone p : catalog) total += p.price();
        return (double) total / catalog.size();
    }

    static Map<String, Integer> countByBrand() {
        Map<String, Integer> counts = new LinkedHashMap<>();
        for (Phone p : catalog) counts.merge(p.brand(), 1, Integer::sum);
        return counts;
    }

    static void showStatistics() {
        System.out.println("Смартфон саны: " + catalog.size());
        System.out.println("Ең арзан:  " + describe(cheapest()));
        System.out.println("Ең қымбат: " + describe(mostExpensive()));
        System.out.printf("Орташа баға: %.0f ₸%n", averagePrice());
        StringJoiner parts = new StringJoiner(", ");
        for (Map.Entry<String, Integer> e : countByBrand().entrySet()) parts.add(e.getKey() + ": " + e.getValue());
        System.out.println("Бренд бойынша: " + parts);
    }

    // ---------- Мәзір ----------
    static void searchMenu() {
        System.out.println("\n1.Бренд бойынша  2.Баға бойынша  3.Жады бойынша  4.Бренд + жады");
        int kind = readInt("Іздеу түрі: ", 0);
        List<Phone> result;
        switch (kind) {
            case 1 -> result = search(readText("Бренд: "));
            case 2 -> {
                int low = readInt("Ең төменгі баға: ", 0);
                int high = readInt("Ең жоғарғы баға: ", low);
                result = search(low, high);
            }
            case 3 -> result = searchByMemory(readInt("Жады (GB, ең аз): ", 1));
            case 4 -> {
                String brand = readText("Бренд: ");
                result = search(brand, readInt("Жады (GB, ең аз): ", 1));
            }
            default -> {
                System.out.println("  Қате: 1-4 аралығында таңдаңыз.");
                return;
            }
        }
        System.out.println(result.isEmpty() ? "Ештеңе табылмады." : "Табылды: " + result.size());
        showCatalog(result);
    }

    public static void main(String[] args) {
        sc = new Scanner(System.in, StandardCharsets.UTF_8);
        try {
            loadCatalog();
        } catch (IOException e) {
            System.out.println("Қате: " + CSV_FILE + " файлын оқу мүмкін болмады.");
            return;
        }
        boolean running = true;
        while (running) {
            System.out.println("\n===== СМАРТФОНДАР КАТАЛОГЫ (" + catalog.size() + " смартфон) =====");
            System.out.println("1.Смартфон қосу      2.Іздеу             3.Камераны салыстыру\n"
                    + "4.Екі смартфонды салыстыру              5.Ең арзан / ең қымбат\n"
                    + "6.Статистика         7.Каталогты шығару  8.Өзгерту\n"
                    + "9.Жою                0.Шығу");
            int choice = readInt("Таңдау: ", 0);
            switch (choice) {
                case 0 -> {
                    System.out.println("Сау болыңыз!");
                    running = false;
                }
                case 1 -> addPhone();
                case 2 -> searchMenu();
                case 3, 4 -> {
                    if (catalog.size() < 2) {
                        System.out.println("Салыстыру үшін кемінде 2 смартфон керек.");
                    } else {
                        showCatalog();
                        Phone a = pickPhone("Бірінші смартфон ID: ");
                        Phone b = pickPhone("Екінші смартфон ID: ");
                        if (choice == 3) printCameraResult(a, b);
                        else comparePhones(a, b);
                    }
                }
                case 5 -> {
                    System.out.println("Ең арзан:  " + describe(cheapest()));
                    System.out.println("Ең қымбат: " + describe(mostExpensive()));
                }
                case 6 -> showStatistics();
                case 7 -> showCatalog();
                case 8, 9 -> {
                    if (catalog.isEmpty()) {
                        System.out.println("Каталог бос.");
                    } else {
                        showCatalog();
                        if (choice == 8) updatePhone();
                        else deletePhone();
                    }
                }
                default -> System.out.println("  Қате: мәзірде мұндай пункт жоқ.");
            }
        }
    }
}
