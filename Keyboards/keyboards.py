from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def make_row_keyboard(items, prefix,add_back:str |None=None,add_menu:bool = True):
    kb = InlineKeyboardBuilder()
    if not items:
        return kb.as_markup()
    for item_id, name in items:
        kb.button(text=name, callback_data=f"{prefix}:{item_id}")
    count = len(items)
    if count <= 2:
        width = count
    elif count <= 6:
        width = 2
    else:
        width = 3
    kb.adjust(width)
    nav_row=[]
    if add_back:
        nav_row.append(InlineKeyboardButton(text='Назад', callback_data=add_back))
    if add_menu:
        nav_row.append(InlineKeyboardButton(text="Главное меню", callback_data='menu'))
    if nav_row:
        kb.row(*nav_row)
    return kb.as_markup()

def product_card_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Заказать", callback_data="buy"))
    kb.row(InlineKeyboardButton(text="Назад", callback_data="back_products"),
           InlineKeyboardButton(text="Главное меню", callback_data="menu"))
    return kb.as_markup()

def nav_keyboard_only(add_back:str |None, add_menu:bool = True):
    kb = InlineKeyboardBuilder()
    row=[]
    if add_back:
        row.append(InlineKeyboardButton(text='Назад', callback_data=add_back))
    if add_menu:
        row.append(InlineKeyboardButton(text="Главное меню", callback_data='menu'))
    if row:
        kb.row(*row)
    return kb.as_markup()
