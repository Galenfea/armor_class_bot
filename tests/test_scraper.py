import logging
import unittest
from logging.config import dictConfig

from bs4 import BeautifulSoup

import tests.htmpl_sample
from exceptions.exceptions import EmptyDataError
from scraper.monster_card import MonsterCard
from scraper.scraper import (
    add_monster_in_list,
    check_if_empty,
    get_armor_class_and_danger,
    get_link,
    get_title,
    is_last_page,
    read_characteristic,
    safe_method_call,
    scrape_cards,
)
from settings.constantns import SCRAPER_CONSTANTS
from settings.log_config import log_config

dictConfig(log_config)
logger = logging.getLogger("scraper")


class TestScraperFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = tests.htmpl_sample.html

    def setUp(self):
        self.monster_data = []

    # Tests for safe_method_call
    def test_safe_method_call_valid_instance(self):
        instance = [1, 2, 3]
        expected_output = 3
        output = safe_method_call(instance, list, len)
        self.assertEqual(output, expected_output)

    def test_safe_method_call_invalid_instance(self):
        instance = "123"
        output = safe_method_call(instance, list, len)
        self.assertIsNone(output)

    # Tests for check_if_empty
    def test_check_if_empty_raise_exception(self):
        with self.assertRaises(EmptyDataError):
            check_if_empty(None, "Error")

    def test_check_if_empty_no_exception(self):
        try:
            check_if_empty("Not None", "Error")
        except EmptyDataError:
            self.fail("check_if_none() raised EmptyDataError unexpectedly!")

    # Tests for is_last_page
    def test_is_last_page_true_without_li_tags(self):
        html_content = '<div><ul class="pagination"></ul></div>'
        soup = BeautifulSoup(html_content, "html.parser")
        with self.assertRaises(
            EmptyDataError, msg="There is no li tags in pagination"
        ):
            is_last_page(soup)

    def test_is_last_page_true_with_correct_pagination(self):
        html_content = """
        <div>
            <ul class="pagination">
                <li>1</li>
                <li>2</li>
            </ul>
        </div>
        """
        soup = BeautifulSoup(html_content, "html.parser")
        self.assertTrue(is_last_page(soup))

    def test_is_last_page_false(self):
        html_content = f"""
        <div>
            <ul class="pagination">
                <li>1</li>
                <li>2</li>
                <li>{SCRAPER_CONSTANTS["NEXT_PAGE_INDICATOR"]}</li>
            </ul>
        </div>
        """
        soup = BeautifulSoup(html_content, "html.parser")
        self.assertFalse(is_last_page(soup))

    # Tests for get_title
    def test_get_title_success(self):
        soup = BeautifulSoup("<h2>Monster Name</h2>", "html.parser")
        title_tag = soup.h2
        self.assertEqual(get_title(title_tag), "Monster Name")

    def test_get_title_empty(self):
        soup = BeautifulSoup("<h2></h2>", "html.parser")
        title_tag_empty = soup.h2
        with self.assertRaises(EmptyDataError):
            get_title(title_tag_empty)

    # Tests for get_link
    def test_get_link_success(self):
        html = '<h2><a href="/monster-link"></a></h2>'
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.h2
        expected_link = SCRAPER_CONSTANTS["BASE_URL"] + "/monster-link"
        self.assertEqual(get_link(title_tag), expected_link)

    def test_get_link_empty(self):
        html = "<h2></h2>"
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.h2
        with self.assertRaises(EmptyDataError):
            get_link(title_tag)

    # Tests for read_characteristic
    def test_read_characteristic_success(self):
        html = "<li><strong>Класс Доспеха</strong>: 15</li>"
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.li
        result = read_characteristic(
            tag, tag.get_text(), "Класс Доспеха", r"\d+"
        )
        self.assertEqual(result, "15")

    def test_read_characteristic_wrong_sample(self):
        html = "<li><strong>Some other text</strong>: 15</li>"
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.li
        result = read_characteristic(
            tag, tag.get_text(), "Класс Доспеха", r"\d+"
        )
        self.assertIsNone(result)

    def test_read_characteristic_no_strong(self):
        html = "<li>15</li>"
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.li
        result = read_characteristic(
            tag, tag.get_text(), "Класс Доспеха", r"\d+"
        )
        self.assertIsNone(result)

    # Tests for get_armor_class_and_danger
    def test_get_armor_class_and_danger_success(self):
        html = """
        <div>
            <ul class="params">
                <li><strong>Класс Доспеха</strong>: 15</li>
                <li><strong>Опасность</strong>: 5/2</li>
            </ul>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        card = soup.div
        armor_class, danger = get_armor_class_and_danger(card)
        self.assertEqual(armor_class, "15")
        self.assertEqual(danger, "5/2")

    def test_get_armor_class_and_danger_missing_data(self):
        html = """
        <div>
            <ul class="params">
                <li><strong>Some other text</strong>: 15</li>
                <li><strong>Опасность</strong>: 5/2</li>
            </ul>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        card = soup.div
        armor_class, danger = get_armor_class_and_danger(card)
        self.assertIsNone(armor_class)
        self.assertEqual(danger, "5/2")

    def test_get_armor_class_and_danger_no_params(self):
        html = "<div></div>"
        soup = BeautifulSoup(html, "html.parser")
        card = soup.div
        with self.assertRaises(EmptyDataError):
            get_armor_class_and_danger(card)

    def test_get_armor_class_and_danger_no_li(self):
        html = """
        <div>
            <ul class="params"></ul>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        card = soup.div
        with self.assertRaises(EmptyDataError):
            get_armor_class_and_danger(card)

    # Tests for add_monster_in_list

    def test_add_monster_in_list_valid(self):
        add_monster_in_list(
            self.monster_data, 10, 20, "MonsterName", "link", "15", "Dangerous"
        )
        self.assertEqual(len(self.monster_data), 1)
        self.assertIsInstance(self.monster_data[0], MonsterCard)

    def test_add_monster_in_list_out_of_range(self):
        add_monster_in_list(
            self.monster_data, 10, 20, "MonsterName", "link", "25", "Dangerous"
        )
        self.assertEqual(len(self.monster_data), 0)

    def test_add_monster_in_list_invalid_armor_class(self):
        with self.assertLogs(logger, level="ERROR") as cm:
            add_monster_in_list(
                self.monster_data,
                10,
                20,
                "MonsterName",
                "link",
                "invalid",
                "Dangerous",
            )
        self.assertIn("Armor class can't be int", cm.output[0])
        self.assertEqual(len(self.monster_data), 0)

    # Tests for scrape_cards

    def test_scrape_cards_title_tag_empty(self):
        cards = [BeautifulSoup('<div class="card"></div>', "html.parser")]
        with self.assertLogs(level="ERROR") as cm:
            scrape_cards(cards, 10, 20)
        self.assertIn("title_tag is empty", cm.output[0])

    def test_scrape_cards_valid(self):
        soup = BeautifulSoup(TestScraperFunctions.html, "lxml")
        cards = soup.find_all("div", class_="card")
        result = scrape_cards(cards, 10, 20)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].title, "Барсук [Badger]")
        self.assertEqual(result[1].title, "Monster")


if __name__ == "__main__":
    unittest.main()
