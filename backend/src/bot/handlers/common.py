from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.db.db_utils.session_maker import async_session_maker
from src.services.user_service import UserService

router = Router(name="start_router")


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username

    async with async_session_maker() as db:
        user_service = UserService(db)
        user, is_new = await user_service.handle_user_start(telegram_id, username)

    if is_new:
        welcome_text = (
            f"👋 ✨ **Добро пожаловать в Личный Кошелёк, {message.from_user.first_name}!**\n\n"
            f"Я создал для вас стартовый счёт *«💵 Наличные»* и базовые категории трат."
        )
    else:
        welcome_text = f"👋 Рады видеть вас снова, {message.from_user.first_name}! С возвращением в кошелёк."

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📱 Открыть Кошелёк", web_app=types.WebAppInfo(url="https://domain.com"))]
        ]
    )

    await message.answer(text=welcome_text, reply_markup=keyboard, parse_mode="Markdown")
