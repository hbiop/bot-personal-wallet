from aiogram import Dispatcher
from src.bot.main_router import router
from src.bot.middleware.services_di_middleware import services_middleware
from src.db.db_utils.redis_initialization import storage



dispatcher = Dispatcher(storage=storage)

dispatcher.message.middleware(services_middleware)
dispatcher.callback_query.middleware(services_middleware)

dispatcher.include_router(router)