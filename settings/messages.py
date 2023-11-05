"""
The module contains all the texts of messages
sent to the user, which are used both in the
main module and in the "states" module.
"""
from typing import Dict, Union

MESSAGE_TEXT_ERROR: str = "Message text error"

MESSAGES: Dict[str, Union[str, Dict[str, str]]] = {
    "CHOOSE_USER_LANGUAGE": "Choose language        | Выберите язык",
    "PHRASE_SIZE": {
        "en": "Choose the size of the monster",
        "ru": "Выберите размер монстра",
    },
    "PHRASE_TYPE": {
        "en": "Choose the type of the monster",
        "ru": "Выберите тип монстра",
    },
    "PHRASE_ALIGNMENT": {
        "en": "Choose the alignment of the monster",
        "ru": "Выберите мировоозрение монстра",
    },
    "PHRASE_DANGER": {
        "en": "Choose the danger rating of the monster",
        "ru": "Выберите рейтинг опасности монстра",
    },
    "PHRASE_ENVIRONMENT": {
        "en": "Choose the environment the monster lives in",
        "ru": "Выберите среду, в которой живёт монстр",
    },
    "PHRASE_SPEED": {
        "en": "Choose the speed of the monster",
        "ru": "Выберите скорость монстра",
    },
    "INVITE_ENTER_ARMOR_CLASS_TEXT": {
        "en": (
            "Great!\n\nNow enter the armor class.\n"
            "You can enter a range, just put two numbers separated by a "
            "space"
        ),
        "ru": (
            "Отлично!\n\nА теперь введите класс брони.\n"
            "Вы можете ввести диапазон, для этого введите "
            "две цифры через пробел"
        ),
    },
    "MONSTER_INPUT_INVITATION": {
        "en": (
            "This is Sergeant Armor, he'll pick mercenaries for you "
            "based on armor class\n"
            "The selection is made from the monsters you have pre-selected\n"
            "Choose monsters or insert a link to the selected ones:\n"
        ),
        "ru": (
            "Это сержант Армор, он подберёт для вас наёмников по классу "
            "брони\n"
            "Выбор производится из отобранных вами монстров\n"
            "Выберите монстров или вставьте ссылку на отобранных:\n"
        ),
    },
    "INSERT_LINK": {
        "en": (
            "Insert a link like "
            "https://dnd.su/bestiary/?search=\n"
            "so that Sergeant Armor can check the guys you have pre-selected"
        ),
        "ru": (
            "Вставьте ссылку типа "
            "https://dnd.su/bestiary/?search=\n"
            "чтобы сержант Армор проверил ребят из тех, "
            "кого вы предварительно отобрали"
        ),
    },
    "FALSE_CANCEL": {
        "en": (
            "Nothing to cancel. You have not started the selection\n\n"
            "To proceed to selecting mercenaries, send the command /start"
        ),
        "ru": (
            "Отменять нечего. Вы не начали отбор\n\n"
            "Чтобы перейти к отбору наёмников - отправьте команду /start"
        ),
    },
    "CANCEL": {
        "en": (
            "You have stopped the selection\n\n"
            "To start selecting mercenaries again, send the command /start"
        ),
        "ru": (
            "Вы прекратили отбор\n\n"
            "Чтобы снова перейти к отбору наёмников - отправьте команду /start"
        ),
    },
    "WRONG_LINK": {
        "en": (
            "What you sent does not look like the correct link\n\n"
            "Please enter a link like "
            "https://dnd.su/bestiary/?search=&size=1&type=2\n\n"
            "If you want to cancel the selection of mercenaries, "
            "send the command /cancel"
        ),
        "ru": (
            "То, что вы отправили не похоже на нужную ссылку\n\n"
            "Пожалуйста, введите ссылку вида "
            "https://dnd.su/bestiary/?search=&size=1&type=2\n\n"
            "Если вы хотите прервать подбор наёмников - отправьте"
            "команду /cancel"
        ),
    },
    "EMPTY_LIST": {
        "en": (
            "Sergeant Armor has got some really bad picks!\n"
            "No one fit your criteria.\n\n"
            "If you want to pick others, type /start"
        ),
        "ru": (
            "В распоряжении сержанта Армора оказалиcь отвратительные кадры!\n"
            "Ни одна салага не подошла под ваш запрос.\n\n"
            "Если хотите подобрать других, наберите /start"
        ),
    },
    "CHOICE_SORT_METHOD": {
        "en": "Choose the sorting method:",
        "ru": "Выберите способ сортировки:",
    },
    "SORT_ERROR": {
        "en": "An error occurred during sorting. Please try again.",
        "ru": "Произошла ошибка при сортировке. Пожалуйста, попробуйте снова.",
    },
    "FINAL_WORD": {
        "en": (
            "Sergeant Armor offers you these grunts!\n\n"
            "If you want to pick others, type /start"
        ),
        "ru": (
            "Сержант Армор предлагает вам этих салаг!\n\n"
            "Если хотите подобрать других, наберите /start"
        ),
    },
    "ARMOR_CLASS_ERROR": {
        "en": (
            "You have incorrectly entered the armor class\n\n"
            "Please try again\n\n"
            "If you want to stop filling out the form, send the "
            "command /cancel"
        ),
        "ru": (
            "Вы некорректно ввели класс брони\n\n"
            "Попробуйте еще раз\n\n"
            "Если вы хотите прервать заполнение формы - отправьте "
            "команду /cancel"
        ),
    },
    "INPUT_ERROR": {
        "en": (
            "Sorry, Sergeant Armor is not very smart"
            " and does not understand you\n"
            "To go back to selecting mercenaries, send the command /start"
        ),
        "ru": (
            "Извините, сержант Армор не очень умён"
            " и не понимает вас\n"
            "Чтобы снова перейти к отбору наёмников - "
            "отправьте команду /start"
        ),
    },
    "SOME_ERROR": {
        "en": (
            "Something went wrong. Work has been interrupted.\n"
            "The Sergeant has already reported to the command (bot admin)."
        ),
        "ru": (
            "Что-то пошло не так. Работа прервана.\n"
            "Сержант уже должился командованию (администратору бота)."
        ),
    },
}
