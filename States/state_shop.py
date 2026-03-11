from aiogram.fsm.state import StatesGroup, State


class ShopFSM(StatesGroup):
    choosing_category = State()
    choosing_product = State()
    entering_qty = State()
    entering_name = State()
    entering_contact = State()