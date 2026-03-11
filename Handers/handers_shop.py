import types

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from DB.db import Products

from Keyboards.keyboards import make_row_keyboard, product_card_keyboard, nav_keyboard_only
from Repositories.repositories import get_categories, get_products_by_category, get_product_by_id, get_product_card, \
    create_order_one_item
from States.state_shop import ShopFSM

router=Router()

# кнопка вход в магазин
@router.message(Command("shop"))
async def cmd_food(message: Message,state:FSMContext,session:AsyncSession):
    cat=await get_categories(session)
    if not cat:
        await message.answer("Категорий нет")
        return
    await message.answer_photo(FSInputFile('img/un.png'),
                               caption="Выбери категорию",
                               reply_markup=make_row_keyboard(cat,"cat"))
    await state.update_data(cat=cat)
    await state.set_state(ShopFSM.choosing_category)

    # кнопка меню
@router.callback_query(F.data=='menu')
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
    await state.set_state(ShopFSM.choosing_category)

# выбираем категорию
@router.callback_query(ShopFSM.choosing_category,F.data.startswith("cat:"))
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
    await state.set_state(ShopFSM.choosing_product)

# выбираем продукт
@router.callback_query(ShopFSM.choosing_product, F.data.startswith("products:"))
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
     caption=text),reply_markup=product_card_keyboard()
)
    await state.update_data(
        prod_id=prod_id,
        name=name,
        price=price,
        stock=stock,
        category_id=category_id
    )

    # кнопка назад
@router.callback_query(F.data=='back_products')
async def on_menu(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
    await callback.answer()
    data=await state.get_data()
    category_id=data.get("category_id")

    if not category_id:
        categories=await get_categories(session)
        if not categories:
            await callback.answer("Категорий нет")
            return
        kb = make_row_keyboard(categories, "cat", None, False)
        await callback.message.edit_media(media=InputMediaPhoto
        (media=FSInputFile("img/11.jpg"),
         caption="Выбери Категорию"), reply_markup=kb)
        await state.set_state(ShopFSM.choosing_category)
        return
    products=await get_products_by_category(session,int(category_id))
    print(products)

    if products:
        await callback.message.answer("Товаров нет",show_alert=True)
        return
    kb = make_row_keyboard(products, "products", None, True)
    await callback.message.edit_media(media=InputMediaPhoto
    (media=FSInputFile("img/11.jpg"),
     caption="Выбери Товар"), reply_markup=kb)
    await state.set_state(ShopFSM.choosing_product)

# выбрали заказ покупаем
@router.callback_query(F.data=='buy')
async def on_buy(callback:CallbackQuery,state:FSMContext,session:AsyncSession):
    await callback.answer()
    data=await state.get_data()
    if not data.get("prod_id"):
        await callback.answer("Выбери товар",show_alert=True)
        return
    text=(f"{data['name']}\n"
          f"Цена: {data['price']}\n"
          f"Остаток: {data['stock']}\n"
          f"введи количество числом:")
    await callback.message.edit_media(media=InputMediaPhoto
    (media=FSInputFile("img/11.jpg"),
     caption=text), reply_markup=nav_keyboard_only(add_back="back_products",add_menu=True))
    await state.set_state(ShopFSM.entering_qty)

    # выбираем количество
@router.message(ShopFSM.entering_qty)
async def on_qty(message:Message,state:FSMContext,session:AsyncSession):
    raw=(message.text or "").strip()
    if not raw.isdigit():
        await message.answer("введи число")
        return
    qty=int(raw)
    if qty<=0:
        await message.answer("число должно быть больше 0")
        return
    data = await state.get_data()
    stock=int(data["stock"])
    if qty>stock:
        await message.answer(f"В наличии только {stock}. Введи меньше")
        return
    await state.update_data(qty=qty)
    await message.answer("Введи имя")
    await state.set_state(ShopFSM.entering_name)

    # добавляем имя
@router.message(ShopFSM.entering_name)
async def on_name(message:Message,state:FSMContext,session:AsyncSession):
    name=(message.text or "").strip()
    if len(name)<2:
        await message.answer(f"Имя слишком короткое.Введи еще раз",show_alert=True)
        return
    await state.update_data(customer_name=name)
    await message.answer("Введи контакт (телефон/ник):")
    await state.set_state(ShopFSM.entering_contact)

# добавляем контакт
@router.message(ShopFSM.entering_contact)
async def on_contact(message:Message,state:FSMContext,session:AsyncSession):
    contact=(message.text or "").strip()
    if len(contact)<3:
        await message.answer(f"Контакт слишком короткий.Введи еще раз")
        return
    data = await state.get_data()
    try:
        order_id=await create_order_one_item(
            session=session,
            customer_name=data["customer_name"],
            contact=contact,
            product_id=int(data["prod_id"]),
            quantity=int(data["qty"])
        )
    except ValueError as e:
        await message.answer(f"{e}")
        return
    total=int(data["qty"])*int(data["price"])
    await message.answer(
        "Заказ создан \n"
        f"Номер заказа: {order_id}\n"
        f"Товар: {data["name"]}\n"
        f"Количество: {data["qty"]}\n"
        f"Итого: {total}\n"
    )
    await state.clear()

# закрыть
@router.message(Command("cancel"))
async def cmd_cancel(message:Message,state:FSMContext):
    await state.clear()
    await message.answer("Отмена")


# Сделать админку:
# Реализовать вход в бота под админом
# Создать клавиатуру для админа(Добавить категории,Добавить товар и тд)
# Добавить возможность редактировать категории,товары и тд