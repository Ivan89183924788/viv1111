from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from DB.db import SessionMaker


class DBSessionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler:Callable[[TelegramObject,Dict[str,Any]],Awaitable[Any]],
            event:TelegramObject,
            data:Dict[str,Any]

    )->Any:
        async with SessionMaker() as session:
            data["session"] = session
            return await handler(event, data)