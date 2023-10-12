import asyncio
import os
import re
from functools import partial
from typing import Match, Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message
from dotenv import load_dotenv

from keyboards import (
    get_selection_keyboard,
    get_sorting_keyboard,
    get_url_keyboard
)
from messages import (
    ARMOR_CLASS_ERROR,
    CANCEL,
    CHOICE_SORT_METHOD,
    EMPTY_LIST,
    FALSE_CANCEL,
    FINAL_WORD,
    INPUT_ERROR,
    INSERT_LINK,
    INVITE_ENTER_ARMOR_CLASS_TEXT,
    MONSTER_INPUT_INVITATION,
    PHRASE_SIZE,
    SORT_ERROR,
    WRONG_LINK
)
from monster_card import MonsterCard
from scraper import scrap_bestiary
from states import PHRASES_AND_STATES, FSMSearchAC

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')


MAX_MESSAGE_LENGTH = 4000
SORTING_KEYS = {
    'sort_by_danger': MonsterCard.sort_by_danger,
    'sort_by_ac': MonsterCard.sort_by_ac,
    'sort_by_title': MonsterCard.sort_by_title
}

BASE_FORMED_URL = 'https://dnd.su/bestiary/?search='

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = MemoryStorage()

# Создаем объекты бота и диспетчера
bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=storage)
url = ''
pattern_url = re.compile(
    r'^https://dnd\.su/bestiary/\?search=(&[\w\-]+=[\w\-]+)*$'
)
pattern_armor_class = re.compile(r'^(\d+)(?:\s+(\d+))?$')
min_armor_class = 0
max_armor_class = 0
monster_data = []


def split_message(text, max_length=MAX_MESSAGE_LENGTH):
    while len(text) > max_length:
        split_position = text.rfind('\n\n', 0, max_length)
        if split_position == -1:  # если не найден символ переноса строки
            split_position = max_length
        yield text[:split_position]
        text = text[split_position:].lstrip()
    yield text


async def form_final_url(state: FSMContext, base_url: str) -> str:
    data = await state.get_data()
    additional_params = [
        value for key, value in data.items() if key.startswith('url_')
    ]
    formed_url = f'{base_url}&{"&".join(additional_params)}'
    return formed_url


@dp.message(CommandStart(), StateFilter(default_state))
async def handle_start_command(message: Message, state: FSMContext):
    keyboard = get_url_keyboard()
    await message.answer(
        text=MONSTER_INPUT_INVITATION,
        reply_markup=keyboard
    )
    await state.set_state(FSMSearchAC.make_url_or_past)


async def generate_handlers(
        callback: CallbackQuery,
        state: FSMContext,
        keyword: str,
        new_state: State,
        text: str,
        keyboard: str
        ):
    '''Универсальный обработчик для разных состояний.
    Формирует ссылку на список монстров исходя из предпочтений пользователя.
    '''
    print('Ключевое слово', keyword)
    print(getattr(callback, 'data', None))
    await callback.answer()
    if callback.data != f'{keyword}=_':
        await state.update_data({f'url_{keyword}': callback.data})
    current_state = await state.get_state()
    print(f'Текущее состояние: {current_state}')
    await state.set_state(state=new_state)
    current_state = await state.get_state()
    print(f'Новое состояние: {current_state}')
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        reply_markup=await get_selection_keyboard(keyboard)
    )


async def dynamic_handlers_registration():
    for keyword, value in PHRASES_AND_STATES.items():
        print(f'\nРегистрация обработчика:\n'
              f'Ключ: {keyword}\nЗначение: {value}'
              )
        handler = partial(
            generate_handlers,
            keyword=keyword,
            new_state=value.state,
            text=value.phrase,
            keyboard=value.keyboard
        )
        print(f'Созданный обработчик: {handler}\n')
        dp.callback_query.register(
            handler,
            StateFilter(getattr(FSMSearchAC, f'{keyword}_selection')),
            F.data.startswith(f'{keyword}=')
        )


@dp.callback_query(StateFilter(FSMSearchAC.make_url_or_past),
                   F.data.in_(['url_paste',
                               'url_form'])
                   )
async def handle_url_buttons(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    chat_id = callback.message.chat.id
    if callback.data == 'url_paste':
        await bot.send_message(
            chat_id=chat_id,
            text=INSERT_LINK
        )
        await state.set_state(FSMSearchAC.get_url)
    if callback.data == 'url_form':
        keyboard = await get_selection_keyboard('size')
        await bot.send_message(
            chat_id=chat_id,
            text=PHRASE_SIZE,
            reply_markup=keyboard)
        print('CALLBACK DATA = ', callback.data)
        current_state = await state.get_state()
        print(f'Текущее состояние: {current_state}')
        await state.set_state(FSMSearchAC.size_selection)
        current_state = await state.get_state()
        print(f'Новое состояние: {current_state}')


@dp.message(Command(commands='cancel'), StateFilter(default_state))
async def handle_cancel_in_default_state(message: Message):
    await message.answer(
        text=FALSE_CANCEL
    )


@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def handle_cancel_in_state(message: Message, state: FSMContext):
    await message.answer(
        text=CANCEL
    )
    await state.clear()


@dp.message(StateFilter(FSMSearchAC.get_url),
            lambda x: F.text and pattern_url.match(x.text)
            )
async def handle_url(message: Message, state: FSMContext):
    await state.update_data(url=message.text)
    await message.answer(text=INVITE_ENTER_ARMOR_CLASS_TEXT)
    await state.set_state(FSMSearchAC.get_armor_class)


@dp.message(StateFilter(FSMSearchAC.get_url))
async def warning_not_url(message: Message):
    await message.answer(
        text=WRONG_LINK
    )


@dp.message(StateFilter(FSMSearchAC.get_armor_class),
            lambda x: F.text and pattern_armor_class.match(x.text)
            )
async def handle_armor_class(message: Message, state: FSMContext):
    matches: Optional[Match] = pattern_armor_class.match(message.text)
    if matches:
        min_armor_class = int(matches.group(1))
        max_armor_class = (int(matches.group(2))
                           if matches.group(2) else min_armor_class)
    data = await state.get_data()
    formed_url = await form_final_url(state, BASE_FORMED_URL)
    url = data.get('url') or formed_url
    print('Ссылка', url)
    monsters: list[MonsterCard] = await scrap_bestiary(url,
                                                       min_armor_class,
                                                       max_armor_class
                                                       )
    if not monsters:
        await state.clear()
        await bot.send_message(
            chat_id=message.chat.id,
            text=EMPTY_LIST
        )
        return None
    await state.set_data({'monsters': monsters})
    await state.set_state(FSMSearchAC.sort_results)
    keyboard = get_sorting_keyboard()
    await bot.send_message(message.chat.id, CHOICE_SORT_METHOD,
                           reply_markup=keyboard
                           )


@dp.callback_query(StateFilter(FSMSearchAC.sort_results),
                   F.data.in_(['sort_by_danger',
                               'sort_by_ac',
                               'sort_by_title'])
                   )
async def handle_sort_buttons_(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    sort_key = callback.data
    chat_id = callback.message.chat.id
    if sort_key not in SORTING_KEYS:
        await bot.send_message(
            chat_id=chat_id,
            text=(SORT_ERROR)
        )
        return
    monsters = data.get('monsters')
    monsters.sort(key=SORTING_KEYS[sort_key])
    formatted_monsters = '\n\n'.join([str(monster) for monster in monsters])
    for output_part in split_message(formatted_monsters):
        await bot.send_message(
            chat_id=chat_id,
            text=output_part
        )
        await asyncio.sleep(0.5)
    await state.clear()
    await bot.send_message(
        chat_id=chat_id,
        text=FINAL_WORD
    )


@dp.message(StateFilter(FSMSearchAC.get_armor_class))
async def warning_not_age(message: Message):
    await message.answer(
        text=ARMOR_CLASS_ERROR
    )


@dp.message(StateFilter(default_state))
async def handle_input_in_default_state(message: Message):
    await message.reply(text=INPUT_ERROR)


async def main():
    await dynamic_handlers_registration()
    print(
          '\n ДЕМО-версия телеграм бота.\n'
          ' Для полноценного и стабильного релиза\n'
          ' требуется платный интернет хостинг.\n'
          ' Демоверсия использует в качестве хостинга ваш компьютер.\n'
          '\n ВНИМАНИЕ: не закрывайте программу, пока не закончите работу.\n'
          ' Бот не работает без запущенной программы.\n'
          '\n Название телеграм бота: Monster Armor Class\n'
          '\n Имя бота для поиска: @monster_armor_class_bot\n'
          '\n Для остановки бота закройте программу\n'
          ' или нажмите ctrl+c.\n'
          )
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('До свидания!')
