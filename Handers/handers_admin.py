from aiogram import Router, F
from aiogram.dispatcher.middlewares import data
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery, FSInputFile, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from DB.db import Products
from Keyboards.admin_keyboard import admin_keyboard, product_card
from Keyboards.keyboards import product_card_keyboard, make_row_keyboard
from Repositories.repositories import add_category, add_products,  \
     rep_update_products, get_product_card, get_products_by_category, get_categories
from States.state_admin import AdminFSM

router1 = Router()
@router1.message(Command("admin"))
async def cmd_admin(message: Message,state:FSMContext,session:AsyncSession):
    await message.answer(f"Вы попали в админ панель:\n"
                         f"выберите действия",reply_markup=admin_keyboard())
@router1.callback_query(F.data=="add_category")
async def add_cat(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
    await callback.answer("Введите название категории")
    await state.set_state(AdminFSM.add_category)

@router1.message(AdminFSM.add_category)
async def only_add_cat(message:Message,state:FSMContext,session:AsyncSession):
    category=(message.text or "").strip()
    if len(category)<3:
        await message.answer("Введи нормально")
        return
    await add_category(session,category)
    await message.answer("Категория добавлена",reply_markup=admin_keyboard())
    await state.clear()


@router1.callback_query(F.data == "add_products")
async def add_prod(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer("Введите название продукта")
    await state.set_state(AdminFSM.add_product)

@router1.message(AdminFSM.add_product)
async def add_product(message:Message,state:FSMContext,session:AsyncSession):

    name = (message.text or "").strip()
    if len(name) < 3:
        await message.answer("Введи нормально")
        return

    await state.update_data(name=name)
    await message.answer("Введите цену товара")
    await state.set_state(AdminFSM.add_price)

@router1.message(AdminFSM.add_price)
async def add_price(message:Message,state:FSMContext,session:AsyncSession):
    raw = (message.text or "").strip()
    if not raw.isdigit():
        await message.answer("Ведите цену товара")
        return
    price = int(raw)
    if price<=0:
        await message.answer(f"Цена товара должно быть больше 0")
        return
    await state.update_data(price=price)
    await message.answer("(Введите количество товара):")
    await state.set_state(AdminFSM.add_stock)

@router1.message(AdminFSM.add_stock)
async def add_stock(message:Message,state:FSMContext,session:AsyncSession):
    raw = (message.text or "").strip()
    if not raw.isdigit():
        await message.answer("Ведите количество товара")
        return
    stock = int(raw)
    if stock<=0:
        await message.answer(f"Количество товара должно быть больше 0")
        return
    await state.update_data(stock=stock)
    await message.answer("(Введите категорию товара):")
    await state.set_state(AdminFSM.add_category_id)

@router1.callback_query(F.data == "update_products")
async def update_products_list(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    products = await get_products_by_category(session)  # Реализуйте эту функцию
    if not products:
        await callback.message.answer("Нет товаров для редактирования")
        return
    for product in products:
        card = await get_product_card(session, product.id)
        await callback.message.answer(
            f"Товар: {card.name}\n"
            f"Цена: {card.price}\n"
            f"Количество: {card.stock}",
            reply_markup=product_card()
        )

@router1.callback_query(F.data == "update")
async def start_update_product(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите ID товара для изменения")
    await state.set_state(AdminFSM.update_product_id)

@router1.message(AdminFSM.update_product_id)
async def get_update_data(message: Message, state: FSMContext):
    product_id = message.text
    if not product_id.isdigit():
        await message.answer("Введите корректный ID товара")
        return
    await state.update_data(product_id=int(product_id))
    await message.answer("Введите новое название товара")
    await state.set_state(AdminFSM.update_product_name)

@router1.message(AdminFSM.update_product_name)
async def update_product_name(message: Message, state: FSMContext, session: AsyncSession):
    name = message.text.strip()
    data = await state.get_data()
    await rep_update_products(
        session=session,
        product_id=data['product_id'],
        name=name,
        price=data.get('price', 0),
        stock=data.get('stock', 0),
        category_id=data.get('category_id', 1)
    )
    await message.answer("Товар обновлён", reply_markup=admin_keyboard())
    await state.clear()

@router1.callback_query(F.data == "delete_products")
async def delete_products_list(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    products = await get_products_by_category(session)
    if not products:
        await callback.message.answer("Нет товаров для удаления")
        return
    for product in products:
        await callback.message.answer(
            f"Удалить товар: {product.name}?",
            reply_markup=admin_keyboard()




@router1.callback_query(F.data=="confirm_delete"))
async def confirm_delete_product(callback: CallbackQuery, session: AsyncSession):
    product_id = int(callback.data.split("_")[-1])
    await delete_products_list(session, product_id)
    await callback.message.edit_text("Товар удалён", reply_markup=admin_keyboard())

@router1.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery):
    await callback.message.edit_text("Удаление отменено", reply_markup=admin_keyboard())
