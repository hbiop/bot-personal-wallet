from aiogram import BaseMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import Any, Awaitable, Callable, Dict
from aiogram.types import TelegramObject

from src.db.db_utils.session_maker import async_session_maker
from src.services.account_service import AccountService
from src.services.transaction_service import TransactionService
from src.services.user_service import UserService


class ServicesMiddleware(BaseMiddleware):
    def __init__(self, session_maker: async_sessionmaker):
        self.session_maker = session_maker

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        async with self.session_maker() as session:
            data["tx_service"] = TransactionService(session)
            data["user_service"] = UserService(session)
            data["account_service"] = AccountService(session)
            return await handler(event, data)

services_middleware = ServicesMiddleware(session_maker=async_session_maker)