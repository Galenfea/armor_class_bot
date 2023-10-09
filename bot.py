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

from bot_armor_class import scrap_bestiary
from monster_card import MonsterCard
from keyboards import get_sorting_keyboard, get_url_keyboard
from keyboards import get_selection_keyboard
from selector import PHRASES_AND_STATES, FSMSearchAC

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')


MAX_MESSAGE_LENGTH = 4000
SORTING_KEYS = {
    "sort_by_danger": MonsterCard.sort_by_danger,
    "sort_by_ac": MonsterCard.sort_by_ac,
    "sort_by_title": MonsterCard.sort_by_title
}

BASE_FORMED_URL = 'https://dnd.su/bestiary/?search='
INVITE_ENTER_ARMOR_CLASS_TEXT = (
    'Отлично!\n\nА теперь введите класс брони.\n'
    'Вы можете ввести диапазон, для этого введите '
    'две цифры через пробел'
)


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


# Этот хэндлер будет срабатывать на команду /start вне состояний
# и предлагать перейти выбору монстров
@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, state: FSMContext):
    keyboard = get_url_keyboard()
    await message.answer(
        text='Это сержант Армор, он подберёт для вас наёмников'
             ' по классу брони\n'
             'Выбор производится из отобранных вами монстров\n'
             'Выберите монстров или вставьте ссылку на отобранных:\n',
             reply_markup=keyboard
    )
    await state.set_state(FSMSearchAC.make_url_or_past)


async def generic_process_handler(
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
            generic_process_handler,
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
async def handling_url_buttons_(callback: CallbackQuery, state: FSMContext):
    await callback.answer(f'Вы выбрали {callback.data}')
    chat_id = callback.message.chat.id
    if callback.data == 'url_paste':
        await bot.send_message(
            chat_id=chat_id,
            text='Вставьте ссылку типа '
                 'https://dnd.su/bestiary/?search=[параметры]\n'
                 'чтобы сержант Армор проверил ребят из тех, '
                 'кого вы предварителньо отобрали')
        await state.set_state(FSMSearchAC.get_url)
    if callback.data == 'url_form':
        keyboard = await get_selection_keyboard('size')
        await bot.send_message(
            chat_id=chat_id,
            text='Выберите размер монстра:',
            reply_markup=keyboard)
        print('CALLBACK DATA = ', callback.data)
        current_state = await state.get_state()
        print(f'Текущее состояние: {current_state}')
        await state.set_state(FSMSearchAC.size_selection)
        current_state = await state.get_state()
        print(f'Новое состояние: {current_state}')


# @dp.callback_query(
#         StateFilter(FSMSearchAC.size_selection),
#         F.data.startswith('size=')
# )
# async def process_size_sent(callback: CallbackQuery, state: FSMContext):
#     print(callback.data)
#     await state.update_data({'formed_url_size': callback.data})
#     # data = await state.get_data()
#     # formed_url: str = BASE_FORMED_URL + '&' + data.get('formed_url_size')
#     # print('Сформированная ссылка = ', formed_url)
#     # await state.update_data({'formed_url': formed_url})
#     await state.set_state(PHRASES_AND_STATES['size'].state)
#     await bot.send_message(
#             chat_id=callback.message.chat.id,
#             text=PHRASES_AND_STATES['size'].phrase
#     )


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию
@dp.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Отменять нечего. Вы не начали отбор\n\n'
             'Чтобы перейти к отбору наёмников - '
             'отправьте команду /start'
    )


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы прекратили отбор\n\n'
             'Чтобы снова перейти к отбору наёмников - '
             'отправьте команду /start'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


@dp.message(StateFilter(FSMSearchAC.get_url),
            lambda x: F.text and pattern_url.match(x.text)
            )
async def process_name_sent(message: Message, state: FSMContext):
    await state.update_data(url=message.text)
    await message.answer(text=INVITE_ENTER_ARMOR_CLASS_TEXT)
    # Устанавливаем состояние ожидания ввода класса брони
    await state.set_state(FSMSearchAC.get_armor_class)


# Этот хэндлер будет срабатывать, если во время ввода ссылки
# будет введено что-то некорректное
@dp.message(StateFilter(FSMSearchAC.get_url))
async def warning_not_url(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на нужную ссылку\n\n'
             'Пожалуйста, введите ссылку вида'
             ' https://dnd.su/bestiary/?search=&size=1&type=2\n\n'
             'Если вы хотите прервать подбор наёмников - '
             'отправьте команду /cancel'
    )


@dp.message(StateFilter(FSMSearchAC.get_armor_class),
            lambda x: F.text and pattern_armor_class.match(x.text)
            )
async def process_wish_news_press(message: Message, state: FSMContext):
    matches: Optional[Match] = pattern_armor_class.match(message.text)
    if matches:
        min_armor_class = int(matches.group(1))
        max_armor_class = (int(matches.group(2))
                           if matches.group(2) else min_armor_class)
    data = await state.get_data()
    formed_url = await form_final_url(state, BASE_FORMED_URL)
    url = data.get('url') or formed_url
    print('Какая ссылка получена в итоге = ', url)
    monsters: list[MonsterCard] = await scrap_bestiary(url,
                                                       min_armor_class,
                                                       max_armor_class
                                                       )
    await state.set_data({'monsters': monsters})
    await state.set_state(FSMSearchAC.sort_results)
    keyboard = get_sorting_keyboard()
    await bot.send_message(message.chat.id, "Выберите способ сортировки:",
                           reply_markup=keyboard
                           )


@dp.callback_query(StateFilter(FSMSearchAC.sort_results),
                   F.data.in_(['sort_by_danger',
                               'sort_by_ac',
                               'sort_by_title'])
                   )
async def handling_sort_buttons_(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    sort_key = callback.data
    chat_id = callback.message.chat.id
    if sort_key not in SORTING_KEYS:
        await bot.send_message(
            chat_id=chat_id,
            text=('Произошла ошибка при сортировке. '
                  'Пожалуйста, попробуйте снова.')
        )
        return
    monsters = data.get('monsters')
    monsters.sort(key=SORTING_KEYS[sort_key])
    formatted_monsters = '\n\n'.join([str(monster) for monster in monsters])
    if not formatted_monsters:
        await state.clear()
        await bot.send_message(
            chat_id=chat_id,
            text='В распоряжении сержанта Армора '
                 'оказалиcь отвратительные кадры!\n'
                 'Ни одна салага не подошла под ваш запрос.\n\n'
                 'Если хотите подобрать других, наберите /start'
        )
    else:
        for output_part in split_message(formatted_monsters):
            await bot.send_message(
                chat_id=chat_id,
                text=output_part
            )
            await asyncio.sleep(0.5)
        await state.clear()
        # Отправляем в чат сообщение о выходе из машины состояний
        await bot.send_message(
            chat_id=chat_id,
            text='Сержант Армор предлагает вам этих салаг!\n\n'
                 'Если хотите подобрать других, наберите /start'
        )


# Этот хэндлер будет срабатывать, если во время ввода класс брони
# будет введено что-то некорректное
@dp.message(StateFilter(FSMSearchAC.get_armor_class))
async def warning_not_age(message: Message):
    await message.answer(
        text='Вы некорректно ввели класс брони\n\n'
             'Попробуйте еще раз\n\nЕсли вы хотите прервать '
             'заполнение анкеты - отправьте команду /cancel'
    )


# Этот хэндлер будет срабатывать на любые сообщения, кроме тех
# для которых есть отдельные хэндлеры, вне состояний
@dp.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply(text='Извините, сержант Армор не очень умён'
                        ' и не понимает вас\n'
                        'Чтобы снова перейти к отбору наёмников - '
                        'отправьте команду /start'
                        )


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
