from itertools import islice
import logging
from logging.config import dictConfig

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from constantns import BUTTON_FACTOR, BUTTON_TEXT, CALLBACK_DATA
from log_config import log_config
from selector import SELECTOR

dictConfig(log_config)
logger = logging.getLogger('armor_class_bot')


def get_url_keyboard(language: str) -> InlineKeyboardMarkup:
    """
    Generate and return an inline keyboard for URL options.

    Args:
        language (str): Language code to determine the text on buttons.

    Returns:
        InlineKeyboardMarkup: A keyboard with buttons for URL options.
    """
    button_url_paste = InlineKeyboardButton(
        text=BUTTON_TEXT.get(
            language, BUTTON_TEXT['en']
            ).get('URL_PASTE', 'Unknown button'),
        callback_data=CALLBACK_DATA['URL_PASTE']
    )

    button_url_form = InlineKeyboardButton(
        text=BUTTON_TEXT.get(
            language, BUTTON_TEXT['en']
            ).get('URL_FORM', 'Unknown button'),
        callback_data=CALLBACK_DATA['URL_FORM']
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button_url_paste, button_url_form]
        ]
    )
    return keyboard


def get_selection_keyboard(
        filter_name: str,
        language: str
        ) -> InlineKeyboardMarkup:
    """
    Generate and return an inline keyboard based on the given filter name.

    Parameters:
        filter_name (str): The name of the filter for which to generate
        the keyboard.
        language (str): Language code to determine the text on buttons.

    Returns:
        InlineKeyboardMarkup: A keyboard with buttons related to the filter.
    """
    logger.debug(f'Keyboard name {filter_name}')
    logger.debug(f'Language used: {language}')
    buttons = SELECTOR.get(filter_name)
    logger.debug(f'Buttons for {filter_name}: {buttons}')
    if buttons is None:
        return InlineKeyboardMarkup(inline_keyboard=[])
    button_iter = iter(buttons.items())
    inline_keyboard = [
         [InlineKeyboardButton(
             text=text,
             callback_data=f'{filter_name}={value}'
          )
          for text, value in islice(button_iter, BUTTON_FACTOR['columns'])]
         for _ in range(BUTTON_FACTOR['lines'])
    ]
    inline_keyboard = [row for row in inline_keyboard if row]
    inline_keyboard.append(
        [InlineKeyboardButton(
            text=BUTTON_TEXT[language]['SKIP'],
            callback_data=f'{filter_name}=_'
        )]
    )

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_sorting_keyboard(language: str) -> InlineKeyboardMarkup:
    """
    Generate and return an inline keyboard for sorting options.

    Parameters:
        language (str): Language code to determine the text on buttons.

    Returns:
        InlineKeyboardMarkup: A keyboard with sorting options.
    """
    button_danger = InlineKeyboardButton(
        text=BUTTON_TEXT.get(
            language, BUTTON_TEXT['en']
            ).get('SORT_BY_DANGER', 'Unknown button'),
        callback_data=CALLBACK_DATA['SORT_BY_DANGER']
    )

    button_ac = InlineKeyboardButton(
        text=BUTTON_TEXT.get(
            language, BUTTON_TEXT['en']
            ).get('SORT_BY_AC', 'Unknown button'),
        callback_data=CALLBACK_DATA['SORT_BY_AC']
    )

    button_title = InlineKeyboardButton(
        text=BUTTON_TEXT.get(
            language, BUTTON_TEXT['en']
            ).get('SORT_BY_TITLE', 'Unknown button'),
        callback_data=CALLBACK_DATA['SORT_BY_TITLE']
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button_danger, button_ac, button_title]
        ]
    )

    return keyboard
