from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_sorting_keyboard() -> InlineKeyboardMarkup:
    # Создаем объекты инлайн-кнопок
    button_danger = InlineKeyboardButton(
        text='По рейтингу опасности',
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
            [button_danger],
            [button_ac],
            [button_title]
        ]
    )

    return keyboard
