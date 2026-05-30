from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
def admin_keyboard():
    kb=InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Добавить категорию",callback_data="add_category"))
    kb.row(InlineKeyboardButton(text="Добавить товар",callback_data="add_products"),
           InlineKeyboardButton(text="Изменить товар", callback_data="update_products"),
           InlineKeyboardButton(text="Удалить товар", callback_data="delete_products"))
    InlineKeyboardButton(text="Да", callback_data="confirm_delete"),
    InlineKeyboardButton(text="Нет", callback_data="cancel_delete")
    return kb.as_markup()

def product_card():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Изменить", callback_data="update"))
    kb.row(InlineKeyboardButton(text="Удалить", callback_data="delete"))
    kb.row(InlineKeyboardButton(text="Назад", callback_data="back_products"),
           InlineKeyboardButton(text="Главное меню", callback_data="menu"))
    return kb.as_markup()
