from aiogram import Router
from src.bot.handlers.common import router as common_router

router = Router()
router.include_router(common_router)