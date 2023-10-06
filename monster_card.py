class MonsterCard:

    DANGER_RATE_STRINGS = {
        0.125: '1/8',
        0.25: '1/4',
        0.5: '1/2'
    }

    def __init__(self, title, link, armor_class, danger_rate_str):
        self.title = title
        self.link = link
        self.armor_class = int(armor_class)
        self.danger_rate = self.__danger_to_float(danger_rate_str)

    def __danger_to_float(self, danger_str):
        if danger_str == "—":
            return 0.0

        if '/' in danger_str:
            numerator, denominator = danger_str.split('/')
            return float(numerator) / float(denominator)
        return float(danger_str)

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
