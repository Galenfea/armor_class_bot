class MonsterCard:
    '''
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
    '''
    DANGER_RATE_STRINGS = {
        0.125: '1/8',
        0.25: '1/4',
        0.5: '1/2'
    }

    def __init__(self, title, link, armor_class, danger_rate_str):
        self.title: str = title
        self.link: str = link
        self.armor_class: int = int(armor_class)
        self.danger_rate: float = self.__danger_to_float(danger_rate_str)

    def __danger_to_float(self, danger_str: str) -> float:
        '''
        Converts the input string to a floating-point number.

        Args:
            danger_str (str): The input string to be converted.

        Returns:
            float: If the conversion is successful, the function returns a
            floating-point number.
            If conversion is not possible, it returns 0.0.
        '''
        if not danger_str or danger_str == "—":
            return 0.0
        if '/' in danger_str:
            numerator, denominator = danger_str.split('/')
            try:
                return float(numerator) / float(denominator)
            except (ValueError, ZeroDivisionError):
                return 0.0
        try:
            return float(danger_str)
        except ValueError:
            return 0.0

    def __repr__(self):
        return (f'<MonsterCard(title="{self.title}", '
                'armor_class={self.armor_class})>')

    def __str__(self):
        danger_str = MonsterCard.DANGER_RATE_STRINGS.get(
            self.danger_rate,
            f'{self.danger_rate:.0f}'
        )
        return ('Название: {}\n'
                'URL: {}\n'
                'Класс Доспеха: {}\n'
                'Опасность: {}'
                ).format(self.title,
                         self.link,
                         self.armor_class,
                         danger_str
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
