from collections import namedtuple

from aiogram.fsm.state import State, StatesGroup


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMSearchAC(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    make_url_or_past = State()
    get_url = State()        # Состояние ожидания ввода ссылки
    get_armor_class = State()  # Состояние ожидания ввода класс брони
    sort_results = State()
    print_results = State()
    size_selection = State()
    type_selection = State()
    alignment_selection = State()
    danger_selection = State()
    # source_selection = State()
    environment_selection = State()
    speed_selection = State()
    languages_selection = State()


PHRASE_TYPE = 'Выберите тип монстра'
PHRASE_ALIGNMENT = 'Выберите мировоозрение монстра'
PHRASE_DANGER = 'Выберите рейтинг опасности монстра'
# PHRASE_SOURCE = 'Выберите книгу, в которой будете искать монстра'
PHRASE_ENVIRONMENT = 'Выберите среду, в которой живёт монстр'
PHRASE_SPEED = 'Выберите скорость монстра'
PHRASE_LANGUAGES = 'Выберите язык монстра'
INVITE_ENTER_ARMOR_CLASS_TEXT = (
    'Отлично!\n\nА теперь введите класс брони.\n'
    'Вы можете ввести диапазон, для этого введите '
    'две цифры через пробел'
)


Phrase_and_state = namedtuple(
    'Phrase_and_state',
    ['phrase', 'state', 'keyboard']
    )

PHRASES_AND_STATES = {
    'size': Phrase_and_state(
        phrase=PHRASE_TYPE,
        state=FSMSearchAC.type_selection,
        keyboard='type'
    ),
    'type': Phrase_and_state(
        phrase=PHRASE_ALIGNMENT,
        state=FSMSearchAC.alignment_selection,
        keyboard='alignment'
    ),
    'alignment': Phrase_and_state(
        phrase=PHRASE_DANGER,
        state=FSMSearchAC.danger_selection,
        keyboard='danger'
    ),
    'danger': Phrase_and_state(
        phrase=PHRASE_ENVIRONMENT,
        state=FSMSearchAC.environment_selection,
        keyboard='environment'
    ),
    #     'source': Phrase_and_state(
    #         phrase=PHRASE_ENVIRONMENT,
    #         state=FSMSearchAC.environment_selection,
    #         keyboard='environment'
    #     ),
    'environment': Phrase_and_state(
        phrase=PHRASE_SPEED,
        state=FSMSearchAC.speed_selection,
        keyboard='speed'
    ),
    'speed': Phrase_and_state(
        phrase=INVITE_ENTER_ARMOR_CLASS_TEXT,
        state=FSMSearchAC.get_armor_class,
        keyboard=None
    )
}

# https://dnd.su/bestiary/?search=&size=10
# https://dnd.su/bestiary/?search=&size=1%7C2%7C3%7C4

DELIMITER = '%7C'

SIZE = {
    'Крошечный': '1',
    'Маленький': '2',
    'Средний': '3',
    'Большой': '4',
    'Огрмоный': '5',
    'Громадный': '6',
    'Маленький или средний': '10',
    'Маленький рой крошечных': '11',
    'Средний рой крошечных': '7',
    'Большой рой крошечных': '8',
    'Большой рой средних': '9'
}

# https://dnd.su/bestiary/?search=&type=24
TYPE = {
    'Аберрация': '24',
    'Великан': '25',
    'Гуманоид': '19',
    'Дракон': '21',
    'Зверь': '22',
    'Исчадие': '31',
    'Конструкт': '29',
    'Монстр': '23',
    'Небожитель': '28',
    'Нежить': '20',
    'Растение': '26',
    'Слизь': '27',
    'Фея': '32',
    'Элементаль': '30',
    'Транспорт': '33',
    'Объект': '34'

}

# https://dnd.su/bestiary/?search=&alignment=lg
ALIGNMENT = {
    'Законно-добрый': 'lg',
    'Нейтрально-добрый': 'ng',
    'Хаотично-добрый': 'cg',
    'Законно-нейтральный': 'ln',
    'Нейтральный': 'n',
    'Хаотично-нейтральный': 'cn',
    'Законно-злой': 'le',
    'Нейтрально-злой': 'ne',
    'Хаотично-злой': 'ce',
    'Без мировоззрения': 'none'
}


DANGER = {
    "0": "10",
    "1/8": "11",
    "1/4": "12",
    "1/2": "13",
    "1": "14",
    "2": "15",
    "3": "16",
    "4": "17",
    "5": "18",
    "6": "19",
    "7": "20",
    "8": "21",
    "9": "22",
    "10": "23",
    "11": "24",
    "12": "25",
    "13": "26",
    "14": "27",
    "15": "28",
    "16": "29",
    "17": "30",
    "18": "31",
    "19": "32",
    "20": "33",
    "21": "34",
    "22": "35",
    "23": "36",
    "24": "37",
    "25": "38",
    "26": "39",
    "27": "40",
    "28": "41",
    "29": "42",
    "30": "43"
}


SOURCE = {
    "Dungeon master's guide": "101",
    "Monster manual": "103",
    "Acquisition Incorporated": "115",
    "Bigby Presents: Glory of the Giants": "198",
    "Eberron: Rising from the Last War": "119",
    "Explorer's Guide to Wildemount": "116",
    "Fizban's Treasury of Dragons": "152",
    "Guildmasters' guide to Ravnica": "112",
    "Spelljammer: Adventures in Space": "160",
    "Mordenkainen Presents: Monsters of the Multiverse": "158",
    "Mordenkainen's Tome of Foes": "113",
    "Mythic Odysseys of Theros": "121",
    "Tasha's Cauldron of Everything": "117",
    "Van Richten's Guide to Ravenloft": "125",
    "Volo's guide to monsters": "111",
    "Xanathar's Guide to Everything": "109",
    "Baldur's Gate: Descent Into Avernus": "126",
    "Candlekeep Mysteries": "122",
    "Critical Role: Call of the Netherdeep": "159",
    "Curse of Strahd": "124",
    "Dragonlance: Shadow of the Dragon Queen": "183",
    "Ghosts of Saltmarsh": "128",
    "Hoard of the Dragon Queen": "105",
    "Icewind Dale: Rime of the Frostmaiden": "120",
    "Journeys through the Radiant Citadel": "171",
    "Out of the Abyss": "129",
    "Princes of the Apocalypse": "107",
    "Phandelver and Below: The Shattered Obelisk": "202",
    "Storm King's Thunder": "132",
    "Strixhaven: A Curriculum of Chaos": "155",
    "Tales from the Yawning Portal": "133",
    "The Rise of Tiamat": "106",
    "The Wild Beyond The Witchlight: A Feywild Adventure": "151",
    "Tomb of Annihilation": "114",
    "Waterdeep: Dragon Heist": "134",
    "Waterdeep: Dungeon of the Mad Mage": "135",
    "Essentials Kit: Divine Contention": "127",
    "Essentials Kit: Dragon of Icespire peak": "157",
    "Essentials Kit: Sleeping Dragon's Wake": "131",
    "Essentials Kit: Storm Lord's Wrath": "167",
    "Giants of the Star Forge": "197",
    "Hunt for the Thessalhydra": "123",
    "Infernal Machine Rebuild": "161",
    "The Lost Dungeon of Rickedness: Big Rick Energy": "130",
    "Lost Mine of Phandelver": "110",
    "Honor among Thieves": "191",
    "Misplaced Monsters: Volume One": "194",
    "Monstrous Compendium Vol 1: Spelljammer Creatures": "187",
    "Monstrous Compendium Vol 2: Dragonlance Creatures": "188",
    "Monstrous Compendium Vol 3: Minecraft Creatures": "199",
    "The Vecna Dossier": "174",
    "Adventurers League": "169"
}


ENVIRONMENT = {
    'Арктика': '1',
    'Болото': '2',
    'Город': '3',
    'Горы': '4',
    'Лес': '5',
    'Луг': '6',
    'Побережье': '7',
    'Под водой': '8',
    'Подземье': '9',
    'Пустыня': '10',
    'Холмы': '11'
}

SPEED = {
    'ходьба': '%2B1',
    'плавание': '%2B2',
    'полёт': '%2B3',
    'лазание': '%2B4',
    'копание': '%2B5',
    'без ходьбы': '-1',
    'без плавания': '-2',
    'без полёта': '-3',
    'без лазания': '-4',
    'без копания': '-5'
}

LANGUAGES = {
    'Общий': '12',
    'Телепатия': '29',
    'Все': '30',
    'Любой': '75',
    'Великаний': '18',
    'Гномий': '13',
    'Гоблинский': '19',
    'Дварфский': '14',
    'Драконий': '20',
    'Орочий': '17',
    'Полуросликов': '15',
    'Эльфийский': '16',
    'Бездны': '21',
    'Глубинная речь': '22',
    'Инфернальный': '23',
    'Небесный': '24',
    'Первичный': '25',
    'Подземный': '26',
    'Сильван': '27',
    'Ауран': '28',
    'Акван': '33',
    'Терран': '34',
    'Игнан': '35',
    'Воровской жаргон': '55',
    'Друидический': '45',
    'Гитский': '31',
    'Гноллий': '36',
    'Модронский': '39',
    'Сахуагинский': '41',
    'Тэйский': '57',
    'Мерфолк': '62',
    'Леонинский': '67',
    'Ведалкен': '79',
    'Язык Локсодонов': '78',
    'Язык Минотавров': '77',
    'Доварский': '72',
    'Бохти': '61',
    'Зиксвет': '69',
    'Йикариа': '65',
    'Крауль': '74',
    'Крутик': '63',
    'Куори': '64',
    'Отиджский': '40',
    'Тлетлахтолли': '70',
    'Три-кринский': '44',
    'Троглодитский': '46',
    'Слаадский': '42',
    'Умбрал': '76',
    'Язык Аартуков': '71',
    'Язык Бурых увальней': '47',
    'Язык Вегепигмеев': '58',
    'Язык Воргов': '49',
    'Язык Гигантских лосей': '51',
    'Язык Гигантских орлов': '52',
    'Язык Гигантских сов': '50',
    'Язык Глубинных воронов': '68',
    'Язык Греллов': '37',
    'Язык Грунгов': '59',
    'Язык Икситксачитлов': '66',
    'Язык Йети': '48',
    'Язык Жаболюдов': '32',
    'Язык Крюкастых ужасов': '38',
    'Язык Ледяных жаб': '56',
    'Язык Мерцающих псов': '53',
    'Язык Полярных волков': '54',
    'Язык Сфинксов': '43',
    'Язык Тлинкалли': '60',
    'Язык Хадози': '73',
    'Соламнийский': '80',
    'Наречие кендеров': '81'
}

SELECTOR = {
    'size': SIZE,
    'type': TYPE,
    'alignment': ALIGNMENT,
    'danger': DANGER,
    # 'source': SOURCE,
    'environment': ENVIRONMENT,
    'speed': SPEED,
    # 'languages': LANGUAGES
}
