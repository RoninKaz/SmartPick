# Автоматты тесттер. Іске қосу:  python -m unittest -v test_smartphones
# Тесттер нақты data/phones.csv файлына тиіспейді: әр тест уақытша көшірмемен жұмыс істейді.

import os
import shutil
import tempfile
import unittest
from unittest import mock

import smartphones as sp
import server


class CatalogTestCase(unittest.TestCase):
    """Әр тестке дейін каталогты уақытша CSV көшірмесінен жүктейді."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        copy = os.path.join(self.tmp, "phones.csv")
        shutil.copy(os.path.join(sp.BASE, "data", "phones.csv"), copy)
        patcher = mock.patch.object(sp, "CSV_FILE", copy)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(shutil.rmtree, self.tmp, True)
        sp.load_catalog()


class TestSearch(CatalogTestCase):
    # Тест 1: іздеу
    def test_load_has_52_phones(self):
        self.assertEqual(len(sp.catalog), 52)

    def test_search_by_brand_ignores_case(self):
        result = sp.search(brand="aPPle")
        self.assertTrue(result)
        self.assertTrue(all(p["brand"] == "Apple" for p in result))

    def test_search_by_price_range(self):
        result = sp.search(min_price=100000, max_price=200000)
        self.assertTrue(result)
        self.assertTrue(all(100000 <= p["price"] <= 200000 for p in result))

    def test_search_combined_filters(self):
        result = sp.search(brand="Samsung", memory=256)
        self.assertTrue(all(p["brand"] == "Samsung" and p["memory"] >= 256 for p in result))

    def test_search_nothing_found(self):
        self.assertEqual(sp.search(brand="Nokia"), [])
        self.assertEqual(sp.search(max_price=1), [])


class TestCameraCompare(CatalogTestCase):
    # Тест 2: камераны салыстыру (ID және сөздік қабылдайды)
    def test_better_camera_wins_by_id_and_by_dict(self):
        lo = sp.add_phone("Test", "Lo", price=100000, memory=128, ram=8, battery=5000, camera=48)
        hi = sp.add_phone("Test", "Hi", price=100000, memory=128, ram=8, battery=5000, camera=200)
        self.assertEqual(sp.compare_camera(lo["id"], hi["id"]), hi)
        self.assertEqual(sp.compare_camera(hi, lo), hi)

    def test_equal_camera_returns_none(self):
        a = sp.add_phone("Test", "A", price=1, memory=1, ram=1, battery=1, camera=50)
        b = sp.add_phone("Test", "B", price=1, memory=1, ram=1, battery=1, camera=50)
        self.assertIsNone(sp.compare_camera(a, b))

    def test_unknown_id_returns_none(self):
        self.assertIsNone(sp.compare_camera(1, 99999))

    def test_winner_direction(self):
        self.assertEqual(sp.winner(10, 20, more_is_better=True), 2)
        self.assertEqual(sp.winner(10, 20, more_is_better=False), 1)  # арзаны жақсы
        self.assertEqual(sp.winner(5, 5), 0)


class TestEditing(CatalogTestCase):
    # Тест 3: қосу, өзгерту, өшіру және файлға сақтау
    def test_add_update_delete_cycle_is_saved(self):
        phone = sp.add_phone("xiaomi", "Test X", price=99000, memory=128, ram=6, battery=5000, camera=50)
        self.assertEqual(phone["brand"], "Xiaomi")  # бас әріпке айналады
        self.assertEqual(len(sp.catalog), 53)

        self.assertTrue(sp.update_phone(phone["id"], price=89000))
        self.assertEqual(sp.find_by_id(phone["id"])["price"], 89000)

        sp.load_catalog()  # файлдан қайта оқимыз: өзгеріс сақталған болуы керек
        self.assertEqual(len(sp.catalog), 53)
        self.assertEqual(sp.catalog[-1]["price"], 89000)

        self.assertTrue(sp.delete_phone(sp.catalog[-1]["id"]))
        self.assertEqual(len(sp.catalog), 52)

    def test_missing_id_returns_false(self):
        self.assertFalse(sp.update_phone(99999, price=1))
        self.assertFalse(sp.delete_phone(99999))

    def test_real_csv_is_not_touched(self):
        real = os.path.join(sp.BASE, "data", "phones.csv")
        self.assertNotEqual(os.path.abspath(sp.CSV_FILE), os.path.abspath(real))


class TestValidation(unittest.TestCase):
    # Тест 4: қате енгізуді тексеру
    def test_empty_names(self):
        self.assertIsNotNone(sp.validate("", "Model", [1, 1, 1, 1, 1]))
        self.assertIsNotNone(sp.validate("Brand", "", [1, 1, 1, 1, 1]))

    def test_semicolon_is_forbidden(self):
        self.assertIsNotNone(sp.validate("Br;and", "Model", [1, 1, 1, 1, 1]))

    def test_non_positive_numbers(self):
        self.assertIsNotNone(sp.validate("A", "B", [100, 0, 8, 5000, 50]))
        self.assertIsNotNone(sp.validate("A", "B", [100, 128, -1, 5000, 50]))

    def test_valid_input(self):
        self.assertIsNone(sp.validate("A", "B", [100, 128, 8, 5000, 50]))

    def test_read_int_retries_until_valid(self):
        with mock.patch("builtins.input", side_effect=["abc", "-3", "0", "7"]), \
                mock.patch("builtins.print"):
            self.assertEqual(sp.read_int("x: "), 7)

    def test_read_int_keeps_current_on_empty_enter(self):
        with mock.patch("builtins.input", return_value=""):
            self.assertEqual(sp.read_int("x", 1, 42), 42)


class TestRecommend(CatalogTestCase):
    # Тест 5: бюджет бойынша таңдау
    def test_everything_fits_the_budget(self):
        for priority in sp.PRIORITIES:
            result = sp.recommend(200000, priority)
            self.assertLessEqual(len(result), 3)
            self.assertTrue(result)
            self.assertTrue(all(p["price"] <= 200000 for p in result))

    def test_camera_priority_puts_best_camera_first(self):
        result = sp.recommend(250000, "camera")
        best = max(p["camera"] for p in sp.catalog if p["price"] <= 250000)
        self.assertEqual(result[0]["camera"], best)

    def test_tie_goes_to_cheaper_phone(self):
        result = sp.recommend(250000, "memory")
        same = [p for p in result if p["memory"] == result[0]["memory"]]
        self.assertEqual([p["price"] for p in same], sorted(p["price"] for p in same))

    def test_too_small_budget_gives_empty_list(self):
        self.assertEqual(sp.recommend(1000), [])

    def test_limit_parameter(self):
        self.assertEqual(len(sp.recommend(10_000_000, "balance", limit=5)), 5)

    def test_bad_arguments_raise(self):
        for bad in (0, -1, "100", 1.5, True, None):
            with self.assertRaises(ValueError):
                sp.recommend(bad)
        with self.assertRaises(ValueError):
            sp.recommend(100000, "speed")


class TestServerHelpers(CatalogTestCase):
    # Тест 6: веб-сервер функциялары (желісіз)
    def test_filter_by_brand_and_sort(self):
        result = server.filter_phones({"brand": ["Samsung"], "sort": ["price-asc"]})
        prices = [p["price"] for p in result]
        self.assertTrue(result)
        self.assertEqual(prices, sorted(prices))

    def test_filter_by_text(self):
        result = server.filter_phones({"q": ["galaxy"]})
        self.assertTrue(all("galaxy" in sp.name(p).lower() for p in result))

    def test_stats(self):
        st = server.stats()
        self.assertEqual(st["count"], 52)
        self.assertLessEqual(st["cheapest"]["price"], st["priciest"]["price"])

    def test_compare_structure(self):
        result = server.compare(sp.find_by_id(1), sp.find_by_id(2))
        self.assertEqual(len(result["rows"]), 5)
        self.assertIn("camera", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
