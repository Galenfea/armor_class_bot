"""
The module contains a set of states, messages corresponding to them,
and the order of transition from one state to another.
"""
from typing import Optional

from aiogram.fsm.state import State, StatesGroup


class MessageAndState:
    def __init__(self, phrase_key: str, state: State, keyboard: Optional[str]):
        self.phrase_key: str = phrase_key
        self.state: State = state
        self.keyboard: Optional[str] = keyboard


class FSMSearchAC(StatesGroup):
    choose_language = State()
    make_url_or_past = State()
    get_url = State()
    get_armor_class = State()
    sort_results = State()
    print_results = State()
    size_selection = State()
    type_selection = State()
    alignment_selection = State()
    danger_selection = State()
    environment_selection = State()
    speed_selection = State()


PHRASES_AND_STATES = {
    "size": MessageAndState(
        phrase_key="PHRASE_TYPE",
        state=FSMSearchAC.type_selection,
        keyboard="type",
    ),
    "type": MessageAndState(
        phrase_key="PHRASE_ALIGNMENT",
        state=FSMSearchAC.alignment_selection,
        keyboard="alignment",
    ),
    "alignment": MessageAndState(
        phrase_key="PHRASE_DANGER",
        state=FSMSearchAC.danger_selection,
        keyboard="danger",
    ),
    "danger": MessageAndState(
        phrase_key="PHRASE_ENVIRONMENT",
        state=FSMSearchAC.environment_selection,
        keyboard="environment",
    ),
    "environment": MessageAndState(
        phrase_key="PHRASE_SPEED",
        state=FSMSearchAC.speed_selection,
        keyboard="speed",
    ),
    "speed": MessageAndState(
        phrase_key="INVITE_ENTER_ARMOR_CLASS_TEXT",
        state=FSMSearchAC.get_armor_class,
        keyboard=None,
    ),
}
