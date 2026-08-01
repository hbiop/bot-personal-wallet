from aiogram import Router
from src.bot.handlers.common import router as common_router
from src.bot.handlers.expense_fsm_handler import router as expense_router
from src.bot.handlers.statistics import router as stats_router

router = Router()
router.include_router(common_router)
router.include_router(expense_router)
router.include_router(stats_router)