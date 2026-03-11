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



@router1.message(AdminFSM.add_category_id)
async def stock(message:Message,state:FSMContext,session:AsyncSession):
    category_id = (message.text or "").strip()
    if not category_id.isdigit():
        await message.answer("Ведите категорию товара")
        return
    category_id = int(category_id)
    if category_id<=0:
        await message.answer(f"Категория товара должно быть больше 0")
        return
    await state.update_data(category_id=category_id)
    data = await state.get_data()
    try:
        product = await add_products(
            session=session,
            name=str(data["name"]),
            price=int(data["price"]),
            stock=int(data["stock"]),
            category_id=int(data["category_id"]))
    except ValueError as e:
        await message.answer(f"{e}")
    await add_products(session,name=str(data["name"]),price=int(data["price"]),stock=int(data["stock"]),category_id=int(data["category_id"]))
    await message.answer("Продукт добавлен", reply_markup=admin_keyboard())
    await state.clear()





    # изменить продукты

@router1.callback_query(F.data=='update_products')
async def on_menu(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
    await callback.answer()
    categories = await get_categories(session)
    kb=make_row_keyboard(categories,"cat",None,False)
    if not categories:
        await callback.answer("Категорий нет")
        return
    data=await state.get_data()
    ui_msg_id=data.get("ui_msg_id")
    media=InputMediaPhoto(media=FSInputFile('img/11.jpg'),caption="Выбери Категорию")
    if ui_msg_id:
        await callback.bot.edit_message_media(
            chat_id=callback.message.chat.id,
            message_id=ui_msg_id,
            media=media,
            reply_markup=kb
        )
        await state.clear()
        await state.update_data(ui_msg_id=ui_msg_id)
    else:
        msg=await callback.message.edit_media(
            media=media,
            reply_markup=kb
        )
        await state.clear()
        await state.update_data(ui_msg_id=msg.message_id)
    await state.set_state(AdminFSM.up_category)

# выбираем категорию
@router1.callback_query(AdminFSM.up_category,F.data.startswith("cat:"))
async def on_category(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
    await callback.answer()
    category_id=int(callback.data.split(":")[1])
    products=await get_products_by_category(session,category_id)
    if not products:
        await callback.answer("Продуктов нет")
        return
    data=await state.get_data()
    ui_msg_id = data.get("ui_msg_id")

    await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile("img/11.jpg")),
                                          reply_markup=make_row_keyboard(products,"products",None,True))
    await state.update_data(category_id=category_id, products=None)
    await state.set_state(AdminFSM.up_product)

# выбираем продукт
@router1.callback_query(AdminFSM.up_product, F.data.startswith("products:"))
async def on_product(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    product_id = int(callback.data.split(":")[1])
    card = await get_product_card(session, product_id)
    if not card:
        await callback.answer("Товара нет",show_alert=True)
        return
    prod_id,name,price,stock,category_id=card
    text=(f"Наименование:{name} \n"
         f"Цена:{price} \n"
         f"Кол-во:{stock} \n"
         f"Введи количество числом: ")
    data = await state.get_data()

    await state.update_data(prod_id=data)
    await callback.message.edit_media(media=InputMediaPhoto
    (media=FSInputFile("img/11.jpg"),
     caption=text),reply_markup=product_card()
)
    await state.update_data(
        prod_id=prod_id,
        name=name,
        price=price,
        stock=stock,
        category_id=category_id
    )

# @router.callback_query(F.data=='menu')
# async def on_menu(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
#     await callback.answer()
#     categories = await get_categories(session)
#     kb=make_row_keyboard(categories,"cat",None,False)
#     if not categories:
#         await callback.answer("Категорий нет")
#         return
#     data=await state.get_data()

@router1.callback_query(F.data == "update")
async def add_prod(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer("Введите номер изменяемого продукта")
    update = await state.get_data()

    await state.set_state(AdminFSM.up_product)



@router1.message(AdminFSM.up_product)
async def add_product(message:Message,state:FSMContext,session:AsyncSession):

    name = (message.text or "").strip()
    if len(name) < 3:
        await message.answer("Введи нормально")
        return

    await state.update_data(name=name)
    await message.answer("Введите цену товара")
    await state.set_state(AdminFSM.up_price)

@router1.message(AdminFSM.up_price)
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
    await state.set_state(AdminFSM.up_stock)

@router1.message(AdminFSM.up_stock)
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
    await state.set_state(AdminFSM.up_category_id)



@router1.message(AdminFSM.up_category_id)
async def stock(message:Message,state:FSMContext,session:AsyncSession):
    category_id = (message.text or "").strip()
    if not category_id.isdigit():
        await message.answer("Ведите категорию товара")
        return
    category_id = int(category_id)
    if category_id<=0:
        await message.answer(f"Категория товара должно быть больше 0")
        return
    await state.update_data(category_id=category_id)
    data = await state.get_data()
    try:
        product = await rep_update_products(
            session=session,

            name=str(data["name"]),
            price=int(data["price"]),
            stock=int(data["stock"]),
            category_id=int(data["category_id"]))
    except ValueError as e:
        await message.answer(f"{e}")
    await rep_update_products(session,name=str(data["name"]),price=int(data["price"]),stock=int(data["stock"]),category_id=int(data["category_id"]))
    await message.answer("Продукт добавлен", reply_markup=admin_keyboard())
    await state.clear()
