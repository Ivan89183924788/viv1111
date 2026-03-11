from datetime import datetime

import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

engine = create_async_engine('postgresql+asyncpg://postgres:Admin@localhost:5432/sqlAlchemyTest', echo=False)
SessionMaker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase): pass


class Categories(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    products = relationship("Products", back_populates="category")


class Products(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Integer)
    stock = Column(Integer)
    category_id = Column(Integer, ForeignKey('category.id'))

    category = relationship("Categories", back_populates="products")
    order_items = relationship("OrderItems", back_populates="product")


class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    contact = Column(String)

    orders = relationship("Orders", back_populates="customer")


class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    order_at = Column(DateTime, default=datetime.now(), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'))

    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItems", back_populates="order")


class OrderItems(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)

    order = relationship("Orders", back_populates="order_items")
    product = relationship("Products", back_populates="order_items")


async def init_db(drop: bool = False) -> None:
    async with engine.begin() as conn:
        if drop:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def create_all_tables(SessionMaker) -> None:
    async with SessionMaker() as session:

        cat1 = Categories(name='Электроника')
        cat2 = Categories(name='Книги')
        cat3 = Categories(name='Одежда')
        session.add_all([cat1, cat2, cat3])
        await session.commit()
        prod1 = Products(name='Телефон', price=1000, stock=10, category_id=cat1.id)
        prod2 = Products(name='Часы', price=1500, stock=20, category_id=cat1.id)
        prod3 = Products(name='Война и мир', price=500, stock=15, category_id=cat2.id)
        prod4 = Products(name='Кросовки', price=700, stock=30, category_id=cat3.id)
        prod5 = Products(name='Носки', price=1200, stock=5, category_id=cat3.id)
        session.add_all([prod1, prod2, prod3, prod4, prod5])
        await session.commit()
        cust1 = Customer(name='Иван Иванов', contact='123456789')
        cust2 = Customer(name='Петр Петров', contact='987654321')
        cust3 = Customer(name='Сергей Сергеев', contact='456789123')
        session.add_all([cust1, cust2, cust3])
        await session.commit()
        order1 = Orders(order_at=datetime.now(), customer_id=cust1.id)
        order2 = Orders(order_at=datetime.now(), customer_id=cust2.id)
        session.add_all([order1, order2])
        await session.commit()
        oi1 = OrderItems(order_id=order1.id, product_id=prod1.id, quantity=1)
        oi2 = OrderItems(order_id=order2.id, product_id=prod3.id, quantity=2)
        session.add_all([oi1, oi2])
        await session.commit()
