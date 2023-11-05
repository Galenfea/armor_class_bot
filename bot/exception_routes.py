import logging
from logging.config import dictConfig

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message

from bot.singleton_bot import SingletonBot
from bot.states import FSMSearchAC
from bot.utils import safe_send_message
from settings.log_config import log_config
from settings.messages import MESSAGE_TEXT_ERROR, MESSAGES

dictConfig(log_config)
logger = logging.getLogger(__name__)

bot = SingletonBot()
exception_router = Router()


@exception_router.message(
    Command(commands="cancel"), StateFilter(default_state)
)
async def handle_cancel_in_default_state(
    message: Message, state: FSMContext
) -> None:
    """
    Handles the '/cancel' command when the user is in the default state.

    This function sends a message informing the user that the cancel command
    is not applicable in the default state.

    Arguments:
    :param message: Message - the incoming message object from aiogram

    Returns:
    None
    """
    chat_id = message.chat.id
    await safe_send_message(
        chat_id=chat_id,
        text=MESSAGES.get("FALSE_CANCEL", MESSAGE_TEXT_ERROR),
        state=state,
    )


@exception_router.message(
    Command(commands="cancel"), ~StateFilter(default_state)
)
async def handle_cancel_in_state(message: Message, state: FSMContext):
    """
    Handles the '/cancel' command when the user is in a non-default state.

    This function sends a message to inform the user that their current
    operation has been canceled. It also clears the user's state in the
    FSM context.

    Arguments:
    :param message: Message - the incoming aiogram Message object
    :param state: FSMContext - the current FSM state of the user

    Returns:
    None
    """
    chat_id = message.chat.id
    await safe_send_message(
        chat_id=chat_id,
        text=MESSAGES.get("CANCEL", MESSAGE_TEXT_ERROR),
        state=state,
    )
    await state.clear()


@exception_router.message(StateFilter(FSMSearchAC.get_url))
async def warning_not_url(message: Message, state: FSMContext):
    """
    Sends a warning message if the user's input is not a valid URL.

    This function is triggered when the state machine is in the
    FSMSearchAC.get_url state and the user's input does not match
    a valid URL pattern. It sends a warning message to the user
    indicating that the input is not a valid URL.

    Arguments:
    :param message: Message - the message object that contains the
    user's text.

    Returns:
    None
    """
    chat_id = message.chat.id
    await safe_send_message(
        chat_id=chat_id,
        text=MESSAGES.get("WRONG_LINK", MESSAGE_TEXT_ERROR),
        state=state,
    )


@exception_router.message(StateFilter(FSMSearchAC.get_armor_class))
async def warning_not_armor_class(message: Message, state: FSMContext):
    """
    Sends a warning message if the armor class input is invalid.
    This function assumes that the bot is in the state expecting an armor
    class value.

    Arguments:
    message (Message): The incoming message object from aiogram.

    Returns:
    None
    """
    chat_id = message.chat.id
    await safe_send_message(
        chat_id=chat_id,
        text=MESSAGES.get("ARMOR_CLASS_ERROR", MESSAGE_TEXT_ERROR),
        state=state,
    )


@exception_router.message(StateFilter(default_state))
async def handle_input_in_default_state(message: Message, state: FSMContext):
    """
    Handles any input while the bot is in the default state and sends
    an error message.

    Arguments:
    message (Message): The incoming message object from aiogram.

    Returns:
    None
    """
    chat_id = message.chat.id
    await safe_send_message(
        chat_id=chat_id,
        text=MESSAGES.get("INPUT_ERROR", MESSAGE_TEXT_ERROR),
        state=state,
    )
