from datetime import datetime

from sqlalchemy import select, delete, update, values
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import session

from DB.db import Categories, Products, Orders, Customer, OrderItems


async def get_categories(session: AsyncSession):
    result = await session.execute(
        select(Categories.id, Categories.name).order_by(Categories.id)
    )
    return result.all()

async def get_products_by_category(session: AsyncSession, category_id: int):
    result=await session.execute(select(Products.id, Products.name)
                                 .where(Products.category_id == category_id)
                                 .order_by(Products.id))
    return result.all()

async def get_product_by_id(session: AsyncSession, product_id: int):
    result = await session.execute(
        select(Products).where(Products.id == product_id)
    )
    return result.scalar_one_or_none()

async def get_product_card(session: AsyncSession,product_id: int):
    result = await session.execute(
        select(Products.id, Products.name,
               Products.price,Products.stock,
               Products.category_id).where(Products.id == product_id))

    return result.one_or_none()

async def create_order_one_item(
        session: AsyncSession,
        customer_name: str,
        contact:str,
        product_id:int,
        quantity:int):
    result = await session.execute(
        select(Products).where(Products.id == product_id).with_for_update()
    )
    product = result.scalar_one_or_none()
    if not product:
        raise ValueError(f"Товар не найден")
    if quantity <= 0:
        raise ValueError(f"Количество должно быть больше 0")
    if product.stock < quantity:
        raise ValueError(f"Недостаточно товара. {product.stock}")
    product.stock -= quantity
    result = await session.execute(
        select(Customer).where(Customer.contact == contact)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        customer = Customer(name=customer_name, contact=contact)
        session.add(customer)
        await session.flush()
    order=Orders(order_at=datetime.now(), customer_id=customer.id)
    session.add(order)
    await session.flush()

    item=OrderItems(
        order_id=order.id,
        product_id=product.id,
        quantity=quantity
    )
    session.add(item)
    await session.commit()
    return order.id


async def add_category(session: AsyncSession,name:str):
    category = Categories(name=name)
    session.add(category)
    await session.commit()
    return category


async def add_products(session:AsyncSession, name:str,price:int,stock:int, category_id:int):
    product=Products(name=name, price=price, stock=stock, category_id=category_id)

    session.add(product)
    await session.commit()
    return product



async def rep_update_products(session:AsyncSession,data:dict,product_id:int,name:str,price:int,stock:int,category_id:int):
    prod=select(Products).where(Products.id == product_id)

    prod.name = name
    prod.price=price
    prod.stock=stock
    prod.category_id=category_id

    await session.commit()
    return prod

