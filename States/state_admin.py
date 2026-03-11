from aiogram.fsm.state import StatesGroup,State
class AdminFSM(StatesGroup):
    add_category=State()
    add_product=State()
    add_price=State()
    add_stock=State()
    add_category_id=State()
    add_id=State()
    choosing_category = State()
    choosing_product = State()
    up_category = State()
    up_product = State()
    up_product_id = State()
    up_price = State()
    up_stock = State()
    up_category_id = State()

