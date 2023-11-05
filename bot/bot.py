import asyncio
import logging
from functools import partial
from logging.config import dictConfig
from typing import List, Match, Optional

from aiogram import Dispatcher, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message

from bot.exception_routes import exception_router
from bot.keyboards import (
    get_language_keyboard,
    get_selection_keyboard,
    get_sorting_keyboard,
    get_url_keyboard,
)
from bot.singleton_bot import SingletonBot
from bot.states import FSMSearchAC, PHRASES_AND_STATES
from bot.utils import (
    bag_report,
    form_final_url,
    get_current_language,
    logstate,
    safe_answer_callback,
    safe_send_message,
    split_message,
)
from exceptions.exceptions import EmptyDataError, EnvError
from scraper.monster_card import MonsterCard
from scraper.scraper import scrape_bestiary
from settings.constantns import (
    BASE_FORMED_URL,
    CALLBACK_DATA,
    LANGUAGES,
    PATTERNS,
    SORTING_KEYS,
)
from settings.log_config import log_config
from settings.messages import MESSAGE_TEXT_ERROR, MESSAGES

dictConfig(log_config)
logger = logging.getLogger(__name__)

storage = MemoryStorage()
logger.debug("Before SingletonBot instance creation")
bot = SingletonBot()
logger.debug("After SingletonBot instance creation\n\n")
dp = Dispatcher(storage=storage)
router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def handle_start_command(message: Message, state: FSMContext):
    keyboard = get_language_keyboard()
    chat_id = message.chat.id
    logger.debug(f"chat_id = {chat_id}, keyboard = {keyboard}")
    current_state = await state.get_state()
    logger.debug(f"State: {current_state}")
    await safe_send_message(
        chat_id=chat_id,
        text=MESSAGES.get("CHOOSE_USER_LANGUAGE", MESSAGE_TEXT_ERROR),
        state=state,
        reply_markup=keyboard,
    )
    await state.set_state(FSMSearchAC.choose_language)


@router.callback_query(StateFilter(FSMSearchAC.choose_language))
async def choose_language(callback: CallbackQuery, state: FSMContext) -> None:
    await logstate(state, "State in choose_language")
    await safe_answer_callback(callback)
    await state.update_data({"current_language": callback.data})
    try:
        language: str = callback.data or LANGUAGES["EN"]
        keyboard = get_url_keyboard(language)

        chat_id = callback.message.chat.id  # type: ignore # In try block
        logger.debug(f"chat_id = {chat_id}, keyboard = {keyboard}")
        await safe_send_message(
            chat_id=chat_id,
            text=MESSAGES.get("MONSTER_INPUT_INVITATION", MESSAGE_TEXT_ERROR),
            state=state,
            reply_markup=keyboard,
        )
    except AttributeError as error:
        logger.error(f"Probably message eror: {error}")
    await state.set_state(FSMSearchAC.make_url_or_past)


async def generate_handlers(
    callback: CallbackQuery,
    state: FSMContext,
    keyword: str,
    new_state: State,
    text_key: str,
    keyboard: str,
) -> None:
    """
    Handle the incoming callback query, update the user's state in the
    finite state machine, and send a message featuring a new keyboard layout.

    Arguments:
    :param callback: CallbackQuery - the callback query object from aiogram
    :param state: FSMContext - the user's state context from aiogram
    :param keyword: str - the keyword for processing and saving data
    :param new_state: State - the new state the user should transition to
    :param text: str - the text message to be sent to the user
    :param keyboard: str - the name of the keyboard to be used for creating
    the reply_markup

    Returns:
    None
    """
    try:
        curretnt_language = await get_current_language(state)

        logger.debug(f"Keyword {keyword}")
        logger.debug(getattr(callback, "data", None))

        await safe_answer_callback(callback)
        if callback.data != f"{keyword}=_":
            logger.debug({f"url_{keyword}": callback.data})
            await state.update_data({f"url_{keyword}": callback.data})
        logger.debug("Current state?")
        await logstate(state, "Current state in generate_handlers")

        await state.set_state(state=new_state)
        await logstate(state, "New state after set_state in generate_handlers")
        logger.debug(
            "Before safe send message\n"
            f"chat_id {callback.message.chat.id}"  # type: ignore
            "Text_key: {text_key}, state: {state}"
        )
        await safe_send_message(
            chat_id=callback.message.chat.id,  # type: ignore # In try block
            text=MESSAGES.get(text_key, MESSAGE_TEXT_ERROR),
            state=state,
            reply_markup=get_selection_keyboard(keyboard, curretnt_language),
        )
        logger.debug("After safe send message")
    except (AttributeError, ValueError) as error:
        logger.error(f"Error while processing callback: {error}")
    except (TimeoutError, ConnectionError) as error:
        logger.critical(f"Network-related error: {error}")
    except TypeError as error:
        logger.error(f"Message Error: {error}")


async def dynamic_handlers_registration() -> None:
    """
    Dynamically register handlers for different states and phrases based
    on the contents of the PHRASES_AND_STATES dictionary.

    Iterate through the PHRASES_AND_STATES dictionary to generate and
    register a handler for each keyword-value pair. Partially apply each
    handler with the values from the dictionary, including the new state,
    text, and keyboard to be used.

    Register the handler to handle callback queries that match the
    StateFilter and data prefix for the keyword.

    Note:
    - This function assumes that PHRASES_AND_STATES, logger, dp, FSMSearchAC,
    and generate_handlers are all defined in the current namespace.
    - The generate_handlers function should accept the keyword, new_state,
    text and keyboard as keyword arguments.

    Arguments:
    None

    Returns:
    None
    """
    try:
        for keyword, value in PHRASES_AND_STATES.items():
            handler = partial(
                generate_handlers,
                keyword=keyword,
                new_state=value.state,
                text_key=value.phrase_key,
                keyboard=value.keyboard,
            )
            logger.debug(
                f"Created handler: {bool(handler)}\n"
                f"Keyword: {keyword}, Keyboard: {value.keyboard}"
            )
            router.callback_query.register(
                handler,
                StateFilter(getattr(FSMSearchAC, f"{keyword}_selection")),
                F.data.startswith(f"{keyword}="),
            )
            logger.debug(
                f"router registered: {keyword}_selection\n"
                f"F.data start {keyword}="
            )
    except NameError as error:
        logger.error(f"NameError: {error}")
    except AttributeError as error:
        logger.error(f"AttributeError: {error}")
    except TypeError as error:
        logger.error(f"TypeError: {error}")


@router.callback_query(
    StateFilter(FSMSearchAC.make_url_or_past),
    F.data.in_(["url_paste", "url_form"]),
)
async def handle_url_buttons(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    Handles clicks on the 'url_paste' and 'url_form' buttons
    in the bot interface. Serves as the entry point into the
    chain of dynamically created handlers through the 'url_form'
    branch. In this case, generates a keyboard to select the size
    of the monster.

    Arguments:
    :param callback: CallbackQuery - the aiogram callback query object
    :param state: FSMContext - the current FSM state of the user

    Returns:
    None
    """
    try:
        await safe_answer_callback(callback)
        chat_id = callback.message.chat.id  # type: ignore # In try block
        if callback.data == "url_paste":
            await safe_send_message(
                chat_id=chat_id,
                text=MESSAGES.get("INSERT_LINK", MESSAGE_TEXT_ERROR),
                state=state,
            )
            await state.set_state(FSMSearchAC.get_url)
        if callback.data == "url_form":
            keyboard = get_selection_keyboard(
                "size", await get_current_language(state)
            )
            await safe_send_message(
                chat_id=chat_id,
                text=MESSAGES.get("PHRASE_SIZE", MESSAGE_TEXT_ERROR),
                state=state,
                reply_markup=keyboard,
            )
            logger.debug(f"CALLBACK DATA = {callback.data}")
            current_state = await state.get_state()
            logger.debug(f"Curent state: {current_state}")
            await state.set_state(FSMSearchAC.size_selection)
            new_state = await state.get_state()
            logger.debug(f"New state: {new_state}")
    except TimeoutError as error:
        logger.critical(f"Network error: {error}")
    except AttributeError as error:
        logger.error(f"Attribute error: {error}")
    except KeyError as error:
        logger.error(f"Key error: {error}")


@router.message(
    StateFilter(FSMSearchAC.get_url),
    lambda x: F.text and PATTERNS["URL"].match(x.text),
)
async def handle_url(message: Message, state: FSMContext):
    """
    Handles a valid URL input from the user.

    This function triggers when the user is in the `FSMSearchAC.get_url` state
    and sends a message that matches the URL pattern. It updates the FSM state
    with the provided URL and then asks the user to enter the armor class,
    transitioning to the `FSMSearchAC.get_armor_class` state.

    Arguments:
    :param message: Message - The message object containing the user's text.
    :param state: FSMContext - The current FSM state of the user.

    Returns:
    None
    """
    await state.update_data(url=message.text)
    chat_id = message.chat.id
    await safe_send_message(
        chat_id=chat_id,
        text=MESSAGES.get("INVITE_ENTER_ARMOR_CLASS_TEXT", MESSAGE_TEXT_ERROR),
        state=state,
    )
    await state.set_state(FSMSearchAC.get_armor_class)


@router.message(
    StateFilter(FSMSearchAC.get_armor_class),
    lambda x: F.text and PATTERNS["ARMOR_CLASS"].match(x.text),
)
async def handle_armor_class(message: Message, state: FSMContext):
    """
    Handles the user's input for armor class and proceeds to scrape for
    monster cards.

    This function is triggered when the state machine is in the
    FSMSearchAC.get_armor_class
    state and the user's input matches the valid armor class pattern.
    It scrapes the bestiary website using the URL and filters the monster
    cards based on the armor class range specified.

    Arguments:
    :param message: Message - the message object that contains the user's text.
    :param state: FSMContext - the current FSM state of the user.

    Returns:
    None

    Exceptions:
    The function expects the pattern to be matched already and therefore does
    not catch ValueError exceptions related to conversion to integers.
    """
    if message.text:
        message_text = message.text
    else:
        message_text = ""
        min_armor_class: int = 0
        max_armor_class: int = 30
        logger.error(
            "Wrong min max armor_class pattern in filter %s", message.text
        )

    matches: Optional[Match] = PATTERNS["ARMOR_CLASS"].match(message_text)
    if matches:
        min_armor_class = int(matches.group(1))
        max_armor_class = (
            int(matches.group(2)) if matches.group(2) else min_armor_class
        )
    data = await state.get_data()
    if not data:
        logger.critical("Empty data")
        await bag_report(chat_id=message.chat.id, state=state)
    formed_url = await form_final_url(data, BASE_FORMED_URL)
    url = data.get("url", formed_url)  # Attention
    logger.debug("Link to be used: {url}")
    monsters: List[MonsterCard]
    try:
        monsters = await scrape_bestiary(url, min_armor_class, max_armor_class)
    except Exception as error:
        logger.error(f"Scraping failed: {error}")
        monsters = []

    if not monsters:
        await safe_send_message(
            chat_id=message.chat.id,
            text=MESSAGES.get("EMPTY_LIST", MESSAGE_TEXT_ERROR),
            state=state,
        )
        await state.clear()
        return None
    await state.update_data({"monsters": monsters})
    await state.set_state(FSMSearchAC.sort_results)
    keyboard = get_sorting_keyboard(await get_current_language(state))
    await safe_send_message(
        chat_id=message.chat.id,
        text=MESSAGES.get("CHOICE_SORT_METHOD", MESSAGE_TEXT_ERROR),
        state=state,
        reply_markup=keyboard,
    )


@router.callback_query(
    StateFilter(FSMSearchAC.sort_results),
    F.data.in_(
        [
            CALLBACK_DATA["SORT_BY_DANGER"],
            CALLBACK_DATA["SORT_BY_AC"],
            CALLBACK_DATA["SORT_BY_TITLE"],
        ]
    ),
)
async def handle_sort_buttons(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    Handle sort buttons after a sorting criterion is selected.

    1. Respond to the callback query.
    2. Retrieve the current state data.
    3. Validate the sorting key.
    4. Sort the list of monsters based on the selected key.
    5. Send the sorted list of monsters to the user.
    6. Clear the state.

    Arguments:
    :param callback: CallbackQuery - the aiogram callback query object
    :param state: FSMContext - the current FSM state of the user

    Returns:
    None
    """
    await safe_answer_callback(callback)
    try:
        data = await state.get_data()
        chat_id = callback.message.chat.id  # type: ignore # In try block
    except EmptyDataError as error:
        logger.error(f"state is None: {error}")
    except AttributeError as error:
        logger.error(f"message is None: {error}")
    current_language = await get_current_language(state)
    sort_key = callback.data
    if sort_key not in SORTING_KEYS:
        await safe_send_message(
            chat_id=chat_id,
            text=MESSAGES.get("SORT_ERROR", MESSAGE_TEXT_ERROR),
            state=state,
        )
        return
    monsters: List[MonsterCard] = data.get("monsters", [])
    logger.debug(f"Is there monsters? {bool(monsters)}")
    if not monsters:
        logger.critical("No monsters in data")
    monsters.sort(key=SORTING_KEYS[sort_key])
    # Formats a list of monster objects into a string,
    # setting each monster's language.
    formatted_monsters = "\n\n".join(
        [
            str((lambda m: m.set_language(current_language) or m)(monster))
            for monster in monsters
        ]
    )
    for output_part in split_message(formatted_monsters):
        await safe_send_message(chat_id=chat_id, text=output_part, state=state)
        await asyncio.sleep(0.5)
    await safe_send_message(
        chat_id=chat_id,
        text=MESSAGES.get("FINAL_WORD", MESSAGE_TEXT_ERROR),
        state=state,
    )
    await state.clear()


async def register_routers() -> None:
    """
    Register main and exception routers to the dispatcher.

    This function includes the main router to the dispatcher and the exception
    router to the main router. It also logs the state of the routers and the
    dispatcher.

    Note: Assumes that `dp`, `router`, and `exception_router` are already
    initialized.

    No Args:

    Returns:
        None
    """
    logger.debug("Start register_routers()")
    dp.include_router(router)
    logger.debug(f"dp.include_router({router})")
    router.include_router(exception_router)
    logger.debug(f"router.include_router({exception_router})")
    logger.debug("Subrouters: %s", router.sub_routers)
    logger.debug(
        "Exception_router: %s", exception_router.resolve_used_update_types()
    )
    logger.debug("Router: %s", router.resolve_used_update_types())
    logger.debug("Dispatcher: %s", dp.resolve_used_update_types())


async def run_bot():
    """
    The main function that starts the bot's operation.

    Actions:
        1. Logs that the program has started.
        2. Registers dynamic handlers.
        3. Starts message polling.
    """
    logger.info("The program has started")
    try:
        await dynamic_handlers_registration()
        logger.debug("Registration of dynamic handlers completed.")
        await register_routers()
        logger.debug("Routers registered")
        logger.debug("Bot = %s", bot)
        logger.debug("Bot = %s", dp)
        print(
            "\n DEMO version of the Telegram bot.\n"
            " For a full and stable release,\n"
            " a paid internet hosting is required.\n"
            " The demo version uses your computer as the hosting.\n"
            "\n WARNING: Do not close the program until you finish working.\n"
            " The bot doesn't work without the program running.\n"
            "\n Telegram bot name: Monster Armor Class\n"
            "\n Bot name for search: @monster_armor_class_bot\n"
            "\n To stop the bot, close the program\n"
            " or press ctrl+c.\n"
        )
        await dp.start_polling(bot)
        logger.debug("Polling started")
    except (TelegramAPIError, EnvError) as error:
        logger.critical(f"Telegram API error: {error}")
