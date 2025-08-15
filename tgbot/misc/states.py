from aiogram.fsm.state import State, StatesGroup


class TestState(StatesGroup):
    test1 = State()
    test2 = State()


class StartForm(StatesGroup):
    about_user = State()
    return_to_mentor = State()

class DialogueWithMentor(StatesGroup):
    process = State()

class BuyState(StatesGroup):
    buying = State()


class BuyMentorState(StatesGroup):
    buying = State()


class AdminPanel(StatesGroup):
    gift_sub_username = State()
    ban_user_id = State()
    direct_user_id = State()
    direct_message = State()
    broadcast_message = State()
    broadcast_button = State()
