from itertools import islice

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from selector import SELECTOR

BUTTON_FACTOR = {
    'size': 3
}


def get_url_keyboard() -> InlineKeyboardMarkup:
    button_url_paste = InlineKeyboardButton(
        text='Вставить ссылку',
        callback_data='url_paste'
    )

    button_url_form = InlineKeyboardButton(
        text='Выбрать монстров',
        callback_data='url_form'
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button_url_paste, button_url_form]
        ]
    )
    return keyboard


async def get_selection_keyboard(filter_name: str) -> InlineKeyboardMarkup:
    buttons = SELECTOR.get(filter_name)
    if buttons is None:
        return InlineKeyboardMarkup(inline_keyboard=[])
    button_iter = iter(buttons.items())
    inline_keyboard = [
         [InlineKeyboardButton(
             text=text,
             callback_data=f'{filter_name}:{value}'
          )
          for text, value in islice(button_iter, BUTTON_FACTOR[filter_name])]
         for _ in range(10)
    ]
    inline_keyboard = [row for row in inline_keyboard if row]

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_sorting_keyboard() -> InlineKeyboardMarkup:
    # Создаем объекты инлайн-кнопок
    button_danger = InlineKeyboardButton(
        text='По опасности',
        callback_data='sort_by_danger'
    )

    button_ac = InlineKeyboardButton(
        text='По классу доспеха',
        callback_data='sort_by_ac'
    )

    button_title = InlineKeyboardButton(
        text='По названию',
        callback_data='sort_by_title'
    )

    # Создаем объект инлайн-клавиатуры
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button_danger, button_ac, button_title]
        ]
    )

    return keyboard
