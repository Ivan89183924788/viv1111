import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile

from DB.db import init_db, create_all_tables, SessionMaker
from DB.middleware_db import DBSessionMiddleware
from Handers.handers_admin import router1
# from Handers.handers_shop import router


logging.basicConfig(level=logging.DEBUG)
TOKEN = "8508651402:AAEBS6MSDYnz5VYpY3yTWdVzV1G9AmdkHvg"
dp = Dispatcher()
# Command handler
@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer_photo(FSInputFile('img/11.jpg'),
                               caption="Вы попали в магазин выберите команду /shop")
# Run the bot
async def main() -> None:
#     await init_db(drop=False)
#     await create_all_tables(SessionMaker)
    dp.update.middleware(DBSessionMiddleware())
    # dp.include_router(router)
    dp.include_router(router1)
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)




if __name__ == "__main__":
    asyncio.run(main())
