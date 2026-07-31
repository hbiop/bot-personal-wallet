from aiogram import Dispatcher
from src.bot.main_router import router
from src.db.db_utils.redis_initialization import storage

dispatcher = Dispatcher(storage=storage)
dispatcher.include_router(router)