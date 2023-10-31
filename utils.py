import logging
from logging.config import dictConfig
from typing import Iterator, Optional, Union

from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from exceptions import EnvError
from log_config import log_config
from messages import MESSAGES
from singleton_bot import SingletonBot

dictConfig(log_config)
logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4000

bot = SingletonBot()


async def logstate(state: FSMContext, msg: str = "Current state") -> None:
    """
    Log the current state of the finite state machine context.

    Args:
        state (FSMContext): The finite state machine context.
        msg (str, optional): A custom message to include in the log.
        Default is "Current state".

    Returns:
        None
    """
    current_state = await state.get_state()
    logger.debug(f"{msg}: {current_state}")


def format_reply_markup_for_log(reply_markup):
    """
    Format for logger the provided reply markup for inline keyboard buttons

    Args:
        reply_markup: The raw reply markup.

    Returns:
        A formatted list of dictionaries, or None if reply_markup is None.
    """
    if reply_markup:
        return [
            {"text": button.text, "callback_data": button.callback_data}
            for row in reply_markup.inline_keyboard[:3]
            for button in row[:3]
        ]
    return None


def chek_token(bot_token: str) -> None:
    """
    Validate the provided bot token.

    Checks if the bot token is available. If it's not, logs a critical error
    and raises an exception.

    Args:
        bot_token (str): The token to validate.

    Returns:
        None

    Raises:
        EnvError: If the bot token is missing.
    """
    if not bot_token:
        logger.critical("Environment variable error")
        raise EnvError("Environment variable error")


async def get_current_language(state: FSMContext) -> str:
    """
    Retrieve the current language from the finite state machine context.

    Args:
        state (FSMContext): The finite state machine context.

    Returns:
        str: The current language set in the state, or "en" if not set.
    """
    await logstate(state, "Current state in get_current_language")
    data = await state.get_data()
    logger.debug(f"data in state = {list(data.keys()) if data else 'None'}")
    return data.get("current_language", "en") if data else "en"


async def get_translated_text(
    state: FSMContext, text: Union[dict, str]
) -> Optional[str]:
    """
    Get text translated to the current language from the state machine context.

    Args:
        state (FSMContext): The finite state machine context.
        text (Union[dict, str]): The text to translate. If a dictionary is
        provided, it should have language codes as keys.

    Returns:
        Optional[str]: The translated text, or None if not available.
    """
    current_language = await get_current_language(state)
    logger.debug(f"current_language = {current_language}")
    return text.get(current_language) if isinstance(text, dict) else text


async def safe_send_message(
    chat_id: int,
    text: Union[dict, str],
    state: FSMContext,
    reply_markup: Optional[
        Union[
            str,
            InlineKeyboardMarkup,
        ]
    ] = None,
) -> None:
    """
    Send a message to a chat in a safe manner by catching TelegramAPIErrors.
    If the message requires a keyboard, attach the keyboard.

    Args:
    :param chat_id: int - The ID of the chat where the message will be sent.
    :param text: str - The text of the message to be sent.

    Returns:
    None
    """
    # TODO Place logging parameters in a separate logger settings file.
    # TODO Ensure logger stability.
    logger.debug(
        "STARTED chat_id = {}, text = {}".format(
            chat_id,
            text[:10]
            if isinstance(text, str)
            else f"{list(text.keys())[0]}: {str(list(text.values())[0])[:30]}"
            if text
            else None,
        )
    )
    clean_text = await get_translated_text(state, text)
    logger.debug(f"clean_text = {clean_text[:20] if clean_text else 'None'}")
    try:
        if reply_markup:
            logger.debug(
                f"reply_markup = {format_reply_markup_for_log(reply_markup)}"
            )
            await bot.send_message(
                chat_id=chat_id,
                text=clean_text,
                disable_web_page_preview=True,
                reply_markup=reply_markup,
            )
        else:
            await bot.send_message(
                chat_id=chat_id, text=clean_text, disable_web_page_preview=True
            )
    except TelegramAPIError as error:
        logger.error(
            f"Error sending telegram message: {error},"
            f"type: {type(error).__name__}"
        )
    logger.debug("safe_send_message ENDED")


async def bag_report(chat_id: int, state: FSMContext) -> None:
    # TODO Bot administrator notification
    await safe_send_message(
        chat_id=chat_id, text=MESSAGES["SOME_ERROR"], state=state
    )


def split_message(
    text: str, max_length: int = MAX_MESSAGE_LENGTH
) -> Iterator[str]:
    """
    Split the given text into multiple substrings of a specified
    maximum length.

    Aim to split by double line breaks when possible to maintain readability.
    Return a list of substrings, each not exceeding the specified
    maximum length.

    Args:
    :param text: str - The input text to be split.
    :param max_length: int - The maximum length for each split substring.

    Returns:
    Iterator[str] - An iterator that yields each split substring.

    Examples:
    >>> list(split_message("Hello, World!", 5))
    ['Hello', ', Wor', 'ld!']
    >>> list(split_message("Hello\n\nWorld!", 5))
    ['Hello', 'World!']
    """
    while len(text) > max_length:
        split_position = text.rfind("\n\n", 0, max_length)
        if split_position == -1:
            split_position = max_length
        yield text[:split_position]
        text = text[split_position:].lstrip()
    yield text


async def form_final_url(data: dict, base_url: str) -> str:
    """
    Form the final URL by appending parameters from the FSMContext state.

    Collect data keys that start with 'url_' from the FSMContext state.
    Append these keys and their corresponding values as query parameters
    to the base_url. Return the formed final URL.

    Args:
    :param state: FSMContext - the current FSM state of the user.
    :param base_url: str - the base URL to which additional parameters
    will be appended.

    Returns:
    :return: str - the formed final URL.
    """
    additional_params = [
        value for key, value in data.items() if key.startswith("url_")
    ]
    formed_url = f'{base_url}&{"&".join(additional_params)}'
    logger.info(f"Final url is {formed_url}")
    return formed_url


async def safe_answer_callback(callback: CallbackQuery) -> None:
    """
    Safely answer a CallbackQuery by catching TelegramAPIErrors.

    Args:
    :param callback: CallbackQuery - The CallbackQuery object to be answered.

    Returns:
    None
    """
    try:
        await callback.answer()
    except TelegramAPIError as error:
        logger.error(
            f"Error sending telegram callback: {error},"
            f"type: {type(error).__name__}"
        )
