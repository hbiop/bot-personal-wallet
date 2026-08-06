from aiogram.exceptions import TelegramNetworkError
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, InputMediaPhoto
from src.services.transaction_service import TransactionService
from src.bot.utils.generate_charts import generate_pie_chart

# Minimal valid 1×1 PNG — avoids URLInputFile (extra HTTP fetch before upload).
_PLACEHOLDER_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _png_input_file(data: bytes) -> BufferedInputFile:
    return BufferedInputFile(file=bytes(data), filename="stats.png")


def _is_valid_png(data: bytes) -> bool:
    return len(data) >= 8 and data[:8] == b"\x89PNG\r\n\x1a\n"

class StatsCallback(CallbackData, prefix="stats_view"):
    type: str


def get_stats_keyboard(current_type: str) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    expense_text = "🔴 Расходы (Активно)" if current_type == "expense" else "Расходы"
    builder.button(text=expense_text, callback_data=StatsCallback(type="expense"))

    income_text = "🟢 Доходы (Активно)" if current_type == "income" else "Доходы"
    builder.button(text=income_text, callback_data=StatsCallback(type="income"))

    builder.adjust(2)
    return builder.as_markup()


router = Router()


@router.message(Command("stats"))
async def show_statistics_command(message: types.Message, tx_service: TransactionService):
    await _send_or_edit_stats(message, tx_service, user_id=message.from_user.id, tx_type="expense")


@router.callback_query(StatsCallback.filter())
async def change_stats_type_callback(
        callback: types.CallbackQuery,
        callback_data: StatsCallback,
        tx_service: TransactionService
):
    await callback.answer()
    await _send_or_edit_stats(
        callback.message,
        tx_service,
        user_id=callback.from_user.id,
        tx_type=callback_data.type,
        is_callback=True
    )


async def _send_or_edit_stats(
    message: types.Message,
    tx_service: TransactionService,
    user_id: int,
    tx_type: str,
    is_callback: bool = False,
):
    stats_data = await tx_service.get_monthly_statistics(user_id=user_id, tx_type=tx_type)
    title_type = "расходов" if tx_type == "expense" else "доходов"
    caption = f"📊 **Статистика {title_type} за 30 дней:**\n\n"

    photo_bytes = _PLACEHOLDER_PNG

    if not stats_data:
        caption += "_Нет данных для построения графика_"
    else:
        for category, amount in stats_data:
            caption += f"🔹 {category}: **{amount:,.2f} ₽**\n"
        chart_bytes = generate_pie_chart(stats_data, title=f"Статистика {title_type}")
        if chart_bytes is not None and _is_valid_png(chart_bytes):
            photo_bytes = chart_bytes
        else:
            caption += "\n⚠️ Не удалось построить график."

    reply_markup = get_stats_keyboard(current_type=tx_type)

    if not is_callback:
        await _answer_stats_photo(message, photo_bytes, caption, reply_markup)
    else:
        await _edit_stats_photo(message, photo_bytes, caption, reply_markup)


async def _answer_stats_photo(
    message: types.Message,
    photo_bytes: bytes,
    caption: str,
    reply_markup: types.InlineKeyboardMarkup,
) -> None:
    for attempt in range(2):
        try:
            await message.answer_photo(
                photo=_png_input_file(photo_bytes),
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="Markdown",
            )
            return
        except TelegramNetworkError:
            if attempt == 0:
                continue
    await message.answer(
        caption,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def _edit_stats_photo(
    message: types.Message,
    photo_bytes: bytes,
    caption: str,
    reply_markup: types.InlineKeyboardMarkup,
) -> None:
    for attempt in range(2):
        try:
            await message.edit_media(
                media=InputMediaPhoto(
                    media=_png_input_file(photo_bytes),
                    caption=caption,
                    parse_mode="Markdown",
                ),
                reply_markup=reply_markup,
            )
            return
        except TelegramNetworkError:
            if attempt == 0:
                continue
    await message.edit_caption(
        caption=caption,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
