from aiogram.fsm.state import State, StatesGroup


class StepsSender(StatesGroup):
    get_message = State()
    q_button = State()
    get_text_button = State()
    confirm = State()
    get_url_button = State()
