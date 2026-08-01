import uuid
from decimal import Decimal, InvalidOperation
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select

from src.db.db_utils.session_maker import async_session_maker
from src.db.entities.account_entity import Account
from src.db.entities.category_entity import Category
from src.services.transaction_service import TransactionService

from aiogram import html  

router = Router(name="expense_fsm_router")


class ExpenseStates(StatesGroup):
    choosing_account = State()
    choosing_category = State()
    entering_amount = State()
    entering_description = State()


@router.message(Command("add_expense"))
async def start_expense_fsm(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id

    async with async_session_maker() as db:
        query = select(Account).where(Account.user_id == telegram_id)
        result = await db.execute(query)
        accounts = result.scalars().all()

        if not accounts:
            await message.answer("❌ У вас еще не создано ни одного счета. Введите /start")
            return

        builder = InlineKeyboardBuilder()
        for acc in accounts:
            builder.button(text=f"{acc.name} ({acc.balance} ₽)", callback_data=f"fsm_acc_{acc.id}")
        builder.adjust(1)

        await message.answer("💳 **Шаг 1 из 4:** Выберите счет для списания:", reply_markup=builder.as_markup(),
                             parse_mode="Markdown")
        await state.set_state(ExpenseStates.choosing_account)


@router.callback_query(ExpenseStates.choosing_account, F.data.startswith("fsm_acc_"))
async def process_account_choice(callback: types.CallbackQuery, state: FSMContext):
    account_id = callback.data.replace("fsm_acc_", "")
    telegram_id = callback.from_user.id

    await state.update_data(account_id=account_id)

    async with async_session_maker() as db:
        query = select(Category).where(
            (Category.type == "expense") &
            ((Category.user_id == telegram_id) | (Category.user_id.is_(None)))
        )
        result = await db.execute(query)
        categories = result.scalars().all()

        builder = InlineKeyboardBuilder()
        for cat in categories:
            builder.button(text=f"{cat.icon} {cat.name}", callback_data=f"fsm_cat_{cat.id}")
        builder.adjust(2)

        await callback.answer()
        await callback.message.edit_text("🛒 **Шаг 2 из 4:** Выберите категорию расхода:",
                                         reply_markup=builder.as_markup(), parse_mode="Markdown")
        await state.set_state(ExpenseStates.choosing_category)


@router.callback_query(ExpenseStates.choosing_category, F.data.startswith("fsm_cat_"))
async def process_category_choice(callback: types.CallbackQuery, state: FSMContext):
    category_id = int(callback.data.replace("fsm_cat_", ""))

    await state.update_data(category_id=category_id)

    await callback.answer()
    await callback.message.edit_text("💰 **Шаг 3 из 4:** Введите сумму расхода цифрами (например, `350` или `120.50`):",
                                     parse_mode="Markdown")
    await state.set_state(ExpenseStates.entering_amount)


@router.message(ExpenseStates.entering_amount, F.text)
async def process_amount_entry(message: types.Message, state: FSMContext):
    raw_amount = message.text.strip().replace(",", ".")

    try:
        amount = Decimal(raw_amount)
        if amount <= 0:
            await message.answer("❌ Сумма должна быть строго больше нуля. Попробуйте еще раз:")
            return
    except (InvalidOperation, ValueError):
        await message.answer("❌ Неверный формат числа. Введите сумму цифрами:")
        return

    await state.update_data(amount=str(amount))

    builder = InlineKeyboardBuilder()
    builder.button(text="⏩ Пропустить комментарий", callback_data="fsm_skip_desc")

    await message.answer("📝 **Шаг 4 из 4:** Напишите короткий комментарий к трате или нажмите кнопку ниже:",
                         reply_markup=builder.as_markup(), parse_mode="Markdown")
    await state.set_state(ExpenseStates.entering_description)


@router.message(ExpenseStates.entering_description, F.text)
async def process_description_entry(message: types.Message, state: FSMContext):
    await save_transaction_and_finish(state, message, message.from_user.id, description=message.text.strip())

@router.callback_query(ExpenseStates.entering_description, F.data == "fsm_skip_desc")
async def process_skip_description(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await save_transaction_and_finish(state, callback.message, callback.from_user.id, description="Внесено через FSM бота 🤖")



async def save_transaction_and_finish(state: FSMContext, message: types.Message, user_id: int, description: str | None):
    data = await state.get_data()
    saved_amount = Decimal(data['amount'])
    
    async with async_session_maker() as db:
        tx_service = TransactionService(db)
        
        await tx_service.add_expense(
            account_id=uuid.UUID(data["account_id"]),
            category_id=data["category_id"],
            amount=saved_amount,
            description=description,
        )

    await state.clear()

    safe_description = html.quote(description) if description else "Без описания"

    await message.answer(
        "✅ <b>Расход успешно зафиксирован!</b>\n\n"
        f"💰 Сумма: <b>{data['amount']} ₽</b>\n"
        f"📝 Заметка: <i>{safe_description}</i>",
        parse_mode="HTML"
    )
