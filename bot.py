import asyncio
import os
import re
from typing import Match, Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from dotenv import load_dotenv

from bot_armor_class import scrap_bestiary

load_dotenv()


BOT_TOKEN = os.getenv('BOT_TOKEN')
MAX_MESSAGE_LENGTH = 4000

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


def format_monster_data(data):
    formatted = []
    for monster in data:
        monster_info = "\n".join(
            [f"{key}: {value}" for key, value in monster.items()]
        )
        formatted.append(monster_info)
    return "\n\n".join(formatted)


def split_message(text, max_length=MAX_MESSAGE_LENGTH):
    while len(text) > max_length:
        split_position = text.rfind('\n', 0, max_length)
        if split_position == -1:  # если не найден символ переноса строки
            split_position = max_length
        yield text[:split_position]
        text = text[split_position:].lstrip()
    yield text


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMSearchAC(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    get_url = State()        # Состояние ожидания ввода ссылки
    get_armor_class = State()  # Состояние ожидания ввода класс брони


# Этот хэндлер будет срабатывать на команду /start вне состояний
# и предлагать перейти к заполнению анкеты, отправив команду /fillform
@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text='Это сержант Армор, он подберёт для вас наёмников'
             ' по классу брони\n'
             'Выбор производится из отобранных вами монстров\n'
             'Чтобы начать отбор наберите команду /hire\n'
    )


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию
@dp.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Отменять нечего. Вы не начали отбор\n\n'
             'Чтобы перейти к отбору наёмников - '
             'отправьте команду /hire'
    )


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы прекратили отбор\n\n'
             'Чтобы снова перейти к отбору наёмников - '
             'отправьте команду /hire'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Этот хэндлер будет срабатывать на команду /hire
# и переводить бота в состояние ожидания ввода имени
@dp.message(Command(commands='hire'), StateFilter(default_state))
async def process_hire_command(message: Message, state: FSMContext):
    await message.answer(text='Вставьте ссылку типа '
                              'https://dnd.su/bestiary/?search=[параметры]\n'
                              'чтобы сержант Армор проверил ребят из тех, '
                              'кого вы предварителньо отобрали')
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMSearchAC.get_url)


# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ввода возраста
@dp.message(StateFilter(FSMSearchAC.get_url),
            lambda x: F.text and pattern_url.match(x.text)
            )
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенную ссылку в хранилище по ключу "name"
    await state.update_data(url=message.text)
    await message.answer(text='Отлично!\n\nА теперь введите класс брони.\n'
                         'Вы можете ввести диапазон, для этого введите '
                         'две цифры через пробел')
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
    url = data.get('url')
    formatted_data = format_monster_data(
        await scrap_bestiary(url, min_armor_class, max_armor_class)
    )
    if not formatted_data:
        await state.clear()
        await message.answer(
            text='В распоряжении сержанта Армора '
                 'оказалиcь отвратительные кадры!\n'
                 'Ни одна салага не подошла под ваш запрос.\n\n'
                 'Если хотите подобрать других, наберите /hire'
        )
    else:
        for output_part in split_message(formatted_data):
            await message.answer(text=output_part)
            await asyncio.sleep(0.5)
        await state.clear()
        # Отправляем в чат сообщение о выходе из машины состояний
        await message.answer(
            text='Сержант Армор предлагает вам этих салаг!\n\n'
                 'Если хотите подобрать других, наберите /hire'
        )
    # Отправляем в чат сообщение с предложением посмотреть свою анкету


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
                        'отправьте команду /hire'
                        )


async def main():
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
          ' или нажмите ctrl+c и подождите 20 секунд.\n'
          )
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
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
            ' или нажмите ctrl+c и подождите 20 секунд.\n'
            )
    except KeyboardInterrupt:
        print('Exit')
