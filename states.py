"""
The module contains a set of states, messages corresponding to them,
and the order of transition from one state to another.
"""

from collections import namedtuple

from aiogram.fsm.state import State, StatesGroup

from messages import (
    INVITE_ENTER_ARMOR_CLASS_TEXT,
    PHRASE_TYPE,
    PHRASE_ALIGNMENT,
    PHRASE_DANGER,
    PHRASE_ENVIRONMENT,
    PHRASE_SPEED
)


class FSMSearchAC(StatesGroup):
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


Phrase_and_state = namedtuple(
    'Phrase_and_state',
    ['phrase', 'state', 'keyboard']
    )

PHRASES_AND_STATES = {
    'size': Phrase_and_state(
        phrase=PHRASE_TYPE,
        state=FSMSearchAC.type_selection,
        keyboard='type'
    ),
    'type': Phrase_and_state(
        phrase=PHRASE_ALIGNMENT,
        state=FSMSearchAC.alignment_selection,
        keyboard='alignment'
    ),
    'alignment': Phrase_and_state(
        phrase=PHRASE_DANGER,
        state=FSMSearchAC.danger_selection,
        keyboard='danger'
    ),
    'danger': Phrase_and_state(
        phrase=PHRASE_ENVIRONMENT,
        state=FSMSearchAC.environment_selection,
        keyboard='environment'
    ),
    'environment': Phrase_and_state(
        phrase=PHRASE_SPEED,
        state=FSMSearchAC.speed_selection,
        keyboard='speed'
    ),
    'speed': Phrase_and_state(
        phrase=INVITE_ENTER_ARMOR_CLASS_TEXT,
        state=FSMSearchAC.get_armor_class,
        keyboard=None
    )
}
