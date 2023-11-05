import re
from typing import Callable, Dict, Pattern

from scraper.monster_card import MonsterCard

# Bot
LANGUAGES: Dict[str, str] = {"EN": "en", "RU": "ru"}
BASE_FORMED_URL: str = "https://dnd.su/bestiary/?search="
PATTERNS: Dict[str, Pattern] = {
    "URL": re.compile(
        r"^https://dnd\.su/bestiary/\?search=(&[\w\-]+=[\w\-]+)*$"
    ),
    "ARMOR_CLASS": re.compile(r"^(\d+)(?:\s+(\d+))?$"),
}
SORTING_KEYS: Dict[str, Callable] = {
    "sort_by_danger": MonsterCard.sort_by_danger,
    "sort_by_ac": MonsterCard.sort_by_ac,
    "sort_by_title": MonsterCard.sort_by_title,
}

# Scraper
SCRAPER_SETTINGS: Dict[str, int] = {
    "SLEEP_TIME": 2,
    "MAX_PAGES": 1000,
}

SCRAPER_CONSTANTS: Dict[str, str] = {
    "ARMOR_PATTERN": r"\d+",
    "DANGER_PATTERN": r"\d+/\d+|\d+|—",
    "USER_AGENT": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    ),
    "BASE_URL": "https://dnd.su",
    "ARMOR_CLASS": "Класс Доспеха",
    "DANGER": "Опасность",
    "NEXT_PAGE_INDICATOR": ">",
}

# Keyboard
BUTTON_FACTOR: Dict[str, int] = {"columns": 3, "lines": 20}
BUTTON_TEXT: Dict[str, Dict[str, str]] = {
    "en": {
        "URL_PASTE": "Paste URL",
        "URL_FORM": "Select Monsters",
        "SKIP": "Skip",
        "SORT_BY_DANGER": "By Danger",
        "SORT_BY_AC": "By Armor Class",
        "SORT_BY_TITLE": "By Title",
    },
    "ru": {
        "URL_PASTE": "Вставить ссылку",
        "URL_FORM": "Выбрать монстров",
        "SKIP": "Пропустить",
        "SORT_BY_DANGER": "По опасности",
        "SORT_BY_AC": "По классу доспеха",
        "SORT_BY_TITLE": "По названию",
    },
}
CALLBACK_DATA: Dict[str, str] = {
    "URL_PASTE": "url_paste",
    "URL_FORM": "url_form",
    "SORT_BY_DANGER": "sort_by_danger",
    "SORT_BY_AC": "sort_by_ac",
    "SORT_BY_TITLE": "sort_by_title",
}
