from aiogram.fsm.state import State, StatesGroup

class AdminAddCar(StatesGroup):
    waiting_for_photo = State()
    waiting_for_name = State()
    waiting_for_rarity = State()
    waiting_for_price = State()
    waiting_for_description = State()
