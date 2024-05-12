from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    choice_topic = State()
    username = State()
    answer = State()
    wait = State()
