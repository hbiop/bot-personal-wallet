from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, InputMediaPhoto
from src.services.transaction_service import TransactionService
from src.bot.utils.generate_charts import generate_pie_chart

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

    photo_file: types.InputFile | types.URLInputFile

    if not stats_data:
        caption += "_Нет данных для построения графика_"
        photo_file = types.URLInputFile("https://via.placeholder.com/300?text=No+data")
    else:
        for category, amount in stats_data:
            caption += f"🔹 {category}: **{amount:,.2f} ₽**\n"
        chart_buffer = generate_pie_chart(stats_data, title=f"Статистика {title_type}")

        # Гарантированно перематываем буфер в начало
        if chart_buffer:
            chart_buffer.seek(0)
            data = chart_buffer.read()
        else:
            data = b""

        if data and len(data) > 0:
            photo_file = BufferedInputFile(data, filename="stats.png")
        else:
            # Если график не получился — заглушка вместо пустого файла
            caption += "\n⚠️ Не удалось построить график."
            photo_file = types.URLInputFile("https://via.placeholder.com/300?text=Chart+error")

    reply_markup = get_stats_keyboard(current_type=tx_type)

    if not is_callback:
        await message.answer_photo(
            photo=photo_file,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
    else:
        media = InputMediaPhoto(
            media=photo_file,
            caption=caption,
            parse_mode="Markdown",
        )
        await message.edit_media(
            media=media,
            reply_markup=reply_markup,
        )
