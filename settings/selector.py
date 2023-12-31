"""
The file contains the names of options for
filtering monsters and codes for selection buttons.
"""
from typing import Dict

SIZE: Dict[str, Dict[str, str]] = {
    "ru": {
        "Крошечный": "1",
        "Маленький": "2",
        "Средний": "3",
        "Большой": "4",
        "Огромный": "5",
        "Громадный": "6",
        "Мал. или средний": "10",
        "Мал. рой крошечных": "11",
        "Сред. рой крошечных": "7",
        "Бол. рой крошечных": "8",
        "Бол. рой средних": "9",
    },
    "en": {
        "Tiny": "1",
        "Small": "2",
        "Medium": "3",
        "Large": "4",
        "Huge": "5",
        "Gargantuan": "6",
        "Small or Medium": "10",
        "Small swarm of Tiny": "11",
        "Med. swarm of Tiny": "7",
        "Large swarm of Tiny": "8",
        "Large swarm of Medium": "9",
    },
}

TYPE: Dict[str, Dict[str, str]] = {
    "ru": {
        "Аберрация": "24",
        "Великан": "25",
        "Гуманоид": "19",
        "Дракон": "21",
        "Зверь": "22",
        "Исчадие": "31",
        "Конструкт": "29",
        "Монстр": "23",
        "Небожитель": "28",
        "Нежить": "20",
        "Растение": "26",
        "Слизь": "27",
        "Фея": "32",
        "Элементаль": "30",
        "Транспорт": "33",
        "Объект": "34",
    },
    "en": {
        "Aberration": "24",
        "Giant": "25",
        "Humanoid": "19",
        "Dragon": "21",
        "Beast": "22",
        "Fiend": "31",
        "Construct": "29",
        "Monster": "23",
        "Celestial": "28",
        "Undead": "20",
        "Plant": "26",
        "Ooze": "27",
        "Fey": "32",
        "Elemental": "30",
        "Vehicle": "33",
        "Object": "34",
    },
}

ALIGNMENT: Dict[str, Dict[str, str]] = {
    "ru": {
        "Законно-добрый": "lg",
        "Нейтрально-добрый": "ng",
        "Хаотично-добрый": "cg",
        "Законно-нейтральный": "ln",
        "Нейтральный": "n",
        "Хаотично-нейтральный": "cn",
        "Законно-злой": "le",
        "Нейтрально-злой": "ne",
        "Хаотично-злой": "ce",
        "Без мировоззрения": "none",
    },
    "en": {
        "Lawful Good": "lg",
        "Neutral Good": "ng",
        "Chaotic Good": "cg",
        "Lawful Neutral": "ln",
        "Neutral": "n",
        "Chaotic Neutral": "cn",
        "Lawful Evil": "le",
        "Neutral Evil": "ne",
        "Chaotic Evil": "ce",
        "No Alignment": "none",
    },
}

DANGER: Dict[str, Dict[str, str]] = {
    "en": {
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
        "30": "43",
    }
}

ENVIRONMENT: Dict[str, Dict[str, str]] = {
    "ru": {
        "Арктика": "1",
        "Болото": "2",
        "Город": "3",
        "Горы": "4",
        "Лес": "5",
        "Луг": "6",
        "Побережье": "7",
        "Под водой": "8",
        "Подземье": "9",
        "Пустыня": "10",
        "Холмы": "11",
    },
    "en": {
        "Arctic": "1",
        "Swamp": "2",
        "Urban": "3",
        "Mountain": "4",
        "Forest": "5",
        "Grassland": "6",
        "Coast": "7",
        "Underwater": "8",
        "Underground": "9",
        "Desert": "10",
        "Hills": "11",
    },
}

SPEED: Dict[str, Dict[str, str]] = {
    "ru": {
        "ходьба": "%2B1",
        "плавание": "%2B2",
        "полёт": "%2B3",
        "лазание": "%2B4",
        "копание": "%2B5",
        "без ходьбы": "-1",
        "без плавания": "-2",
        "без полёта": "-3",
        "без лазания": "-4",
        "без копания": "-5",
    },
    "en": {
        "walking": "%2B1",
        "swimming": "%2B2",
        "flying": "%2B3",
        "climbing": "%2B4",
        "digging": "%2B5",
        "no walking": "-1",
        "no swimming": "-2",
        "no flying": "-3",
        "no climbing": "-4",
        "no digging": "-5",
    },
}


SELECTOR: Dict[str, Dict[str, Dict[str, str]]] = {
    "size": SIZE,
    "type": TYPE,
    "alignment": ALIGNMENT,
    "danger": DANGER,
    "environment": ENVIRONMENT,
    "speed": SPEED,
}
