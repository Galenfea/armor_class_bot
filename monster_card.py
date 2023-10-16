import logging
from logging.config import dictConfig
from typing import Optional

from log_config import log_config

dictConfig(log_config)
logger = logging.getLogger(__name__)


class MonsterCard:
    """
    This class represents a Monster Card object.

    Attributes:
    - title (str): The title of the monster.
    - link (str): URL link to the monster's information.
    - armor_class (int): The armor class of the monster.
    - danger_rate (float): The danger rate of the monster,
    represented as a float.

    Methods:
    - __init__(self, title, link, armor_class, danger_rate_str):
    Initializes a MonsterCard object.
    - __danger_to_float(self, danger_str):
    Converts a danger rate string to a float value.
    - __repr__(self): Returns a string representation of the object.
    - __str__(self): Returns a formatted string with the monster's information.

    Static Methods:
    - sort_by_title(monster): Sorts monsters by title.
    - sort_by_danger(monster): Sorts monsters by danger rate.
    - sort_by_ac(monster): Sorts monsters by armor class.
    """

    FIELDS_NAME = {
        'en': {
            'NAME': 'Name',
            'URL': 'URL',
            'ARMOR_CLASS':
            'Armor Class',
            'DANGER': 'Danger'
        },
        'ru': {
            'NAME': 'Название',
            'URL': 'URL',
            'ARMOR_CLASS': 'Класс Доспеха',
            'DANGER': 'Опасность'
            }
    }

    DANGER_RATE_STRINGS = {
        0.125: '1/8',
        0.25: '1/4',
        0.5: '1/2'
    }

    def __init__(self, title, link, armor_class, danger_rate_str):
        self.title: str = title
        self.link: str = link
        self.armor_class: Optional[int] = (
            armor_class if armor_class is not None else 0
        )
        self.danger_rate: float = self.__danger_to_float(danger_rate_str)
        self.language: str = 'en'

    def __danger_to_float(self, danger_str: str) -> float:
        """
        Convert the input string to a floating-point number.

        Args:
            danger_str (str): The input string to be converted.

        Returns:
            float: If the conversion is successful, the function returns a
            floating-point number.
            If conversion is not possible, it returns 0.0.
        """
        if not danger_str:
            return 0.0

        if '/' in danger_str:
            numerator, denominator = danger_str.split('/')
            try:
                return float(numerator) / float(denominator)
            except (ValueError, ZeroDivisionError) as error:
                logger.error(f'Danger Conversion Error - {error}')
                return 0.0

        try:
            return float(danger_str)
        except ValueError as error:
            logger.error(f'Danger Conversion Error - {error}')
            return 0.0

    def set_language(self, language: str) -> None:
        """
        Set the language for the MonsterCard object.

        Change the language attribute for the MonsterCard instance, affecting
        the language in which the monster's information will be displayed.

        Args:
            language (str): The language code to set. Supports 'en' for
            English and 'ru' for Russian.

        Returns:
            None

        Raises:
            ValueError: If the provided language code is not supported.
        """
        if language not in self.FIELDS_NAME.keys():
            logger.error(f'Unsupported language code: {language}.')
            raise ValueError(f'Unsupported language code: {language}')
        self.language = language

    def __repr__(self):
        return (f'<MonsterCard(title="{self.title}", '
                'armor_class={self.armor_class})>')

    def __str__(self):
        """
        Provide a human-readable string representation of the
        MonsterCard object.

        Generate a formatted string displaying the monster's title, URL,
        armor class, and danger rate based on the current language setting
        of the MonsterCard instance.

        Returns:
            str: A string representation of the MonsterCard object's attributes
            in a human-readable format.
        """
        danger_str = MonsterCard.DANGER_RATE_STRINGS.get(
            self.danger_rate,
            f'{self.danger_rate:.0f}'
        )
        local_field_names = self.FIELDS_NAME.get(
            self.language,
            self.FIELDS_NAME['en']
        )
        return (
            f'{local_field_names["NAME"]}: {self.title}\n'
            f'{local_field_names["URL"]}: {self.link}\n'
            f'{local_field_names["ARMOR_CLASS"]}: {self.armor_class}\n'
            f'{local_field_names["DANGER"]}: {danger_str}'
        )

    @staticmethod
    def sort_by_title(monster):
        return monster.title

    @staticmethod
    def sort_by_danger(monster):
        return monster.danger_rate

    @staticmethod
    def sort_by_ac(monster):
        return monster.armor_class
