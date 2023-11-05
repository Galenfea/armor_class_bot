import unittest

from scraper.monster_card import MonsterCard


class TestMonsterCard(unittest.TestCase):

    def setUp(self) -> None:
        self.card = MonsterCard(
            "Dragon", "http://example.com/dragon", 15, "1/2"
        )

    def test_init(self):
        """
        Test the initialization of the MonsterCard object with valid parameters
        """
        self.assertEqual(self.card.title, "Dragon")
        self.assertEqual(self.card.link, "http://example.com/dragon")
        self.assertEqual(self.card.armor_class, 15)
        self.assertEqual(self.card.danger_rate, 0.5)
        self.assertEqual(self.card.language, "en")

    def test_danger_to_float(self):
        """
        Test converting the danger string to a number
        """
        self.assertEqual(self.card._MonsterCard__danger_to_float("1/2"), 0.5)
        self.assertEqual(self.card._MonsterCard__danger_to_float("1"), 1.0)
        self.assertEqual(self.card._MonsterCard__danger_to_float("—"), 0.0)
        self.assertEqual(self.card._MonsterCard__danger_to_float(None), 0.0)

    def test_set_language(self):
        """
        Test setting the language for the MonsterCard object
        """
        self.card.set_language("ru")
        self.assertEqual(self.card.language, "ru")

        with self.assertRaises(ValueError):
            self.card.set_language("unsupported_language")

    def test_repr(self):
        """
        Test the string representation of an object (__repr__ method)
        """
        self.assertEqual(
            repr(self.card), '<MonsterCard(title="Dragon", armor_class=15)>'
        )

    def test_str(self):
        """
        Test the human-readable string representation
        of an object (__str__ method)
        """
        expected_str = (
            "Name: Dragon\n"
            "URL: http://example.com/dragon\n"
            "Armor Class: 15\n"
            "Danger: 1/2"
        )
        self.assertEqual(str(self.card), expected_str)


if __name__ == "__main__":
    unittest.main()
