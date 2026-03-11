import asyncio
from unicodedata import category

from DB.db import SessionMaker
from Repositories.repositories import get_categories, get_products_by_category, get_product_card, get_product_by_id


async def test_database():
    async with SessionMaker() as session:
        categories=await get_categories(session)
        print(categories)
        first_category_id=categories[2][0]
        products=await get_products_by_category(session, first_category_id)
        print(products)
        prod=await get_product_by_id(session, first_category_id)
        first_category_id = categories[0][0]

        prod = products[1][0]
        print(prod)
        product=products[0][0]
        prod=await get_product_card(session, product)
        print(prod)
if __name__ == '__main__':
    asyncio.run(test_database())