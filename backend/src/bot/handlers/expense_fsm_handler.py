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
from src.services.account_service import AccountService
from src.services.transaction_service import TransactionService

from aiogram import html  

router = Router(name="expense_fsm_router")


class TransactionStates(StatesGroup):
    choosing_account = State()
    choosing_category = State()
    entering_amount = State()
    entering_description = State()


@router.message(Command("add_income"))
async def start_income_fsm(message: types.Message, state: FSMContext, account_service: AccountService):
    await state.set_data({"transaction_type": "income"}) # Запомнили тип
    await _start_transaction_flow(message, state, account_service)

# Расход
@router.message(Command("add_expense"))
async def start_expense_fsm(message: types.Message, state: FSMContext, account_service: AccountService):
    await state.set_data({"transaction_type": "expense"}) # Запомнили тип
    await _start_transaction_flow(message, state, account_service)


async def _start_transaction_flow(message: types.Message, state: FSMContext, account_service: AccountService):
    accounts = await account_service.get_all_accounts_by_user_id(user_id=message.from_user.id)
    if not accounts:
        await message.answer("❌ У вас еще не создано ни одного счета.")
        return

    builder = InlineKeyboardBuilder()
    for acc in accounts:
        builder.button(text=f"{acc.name} ({acc.balance} ₽)", callback_data=f"fsm_acc_{acc.id}")
    builder.adjust(1)

    await message.answer("Шаг 1 из 4: Выберите счет:", reply_markup=builder.as_markup())
    await state.set_state(TransactionStates.choosing_account)

@router.callback_query(TransactionStates.choosing_account, F.data.startswith("fsm_acc_"))
async def process_account_choice(callback: types.CallbackQuery, state: FSMContext):
    account_id = callback.data.replace("fsm_acc_", "")
    telegram_id = callback.from_user.id
    fsm_data = await state.get_data()
    tx_type = fsm_data.get("transaction_type")

    await state.update_data(account_id=account_id)

    async with async_session_maker() as db:
        query = select(Category).where(
            (Category.type == tx_type) &
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
        await state.update_data(account_id=account_id, transaction_type=tx_type)
        await state.set_state(TransactionStates.choosing_category)


@router.callback_query(TransactionStates.choosing_category, F.data.startswith("fsm_cat_"))
async def process_category_choice(callback: types.CallbackQuery, state: FSMContext):
    category_id = int(callback.data.replace("fsm_cat_", ""))

    await state.update_data(category_id=category_id)

    await callback.answer()
    await callback.message.edit_text("💰 **Шаг 3 из 4:** Введите сумму расхода цифрами (например, `350` или `120.50`):",
                                     parse_mode="Markdown")
    await state.set_state(TransactionStates.entering_amount)


from decimal import Decimal, InvalidOperation
import uuid


@router.message(TransactionStates.entering_amount, F.text)
async def process_amount_entry(
        message: types.Message,
        state: FSMContext,
        tx_service: TransactionService  # Имя зависимости должно совпадать с тем, что в DI Middleware
):
    raw_amount = message.text.strip().replace(",", ".")
    try:
        amount = Decimal(raw_amount)
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше нуля:")
            return

        data = await state.get_data()

        if data.get("transaction_type") == "expense":
            account_id = uuid.UUID(data["account_id"])
            balance = await tx_service.check_balance(account_id)

            if balance is None:
                await message.answer("❌ Счет не найден.")
                return

            if balance < amount:
                await message.answer(f"❌ Недостаточно средств! Баланс: {balance} ₽. Введите другую сумму:")
                return

    except (InvalidOperation, ValueError):
        await message.answer("❌ Введите сумму цифрами:")
        return

    await state.update_data(amount=str(amount))

    builder = InlineKeyboardBuilder()
    builder.button(text="⏩ Пропустить комментарий", callback_data="fsm_skip_desc")

    await message.answer(
        "📝 **Шаг 4 из 4:** Напишите короткий комментарий к трате или нажмите кнопку ниже:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await state.set_state(TransactionStates.entering_description)


@router.message(TransactionStates.entering_description, F.text)
async def process_description_entry(message: types.Message, state: FSMContext):
    await save_transaction_and_finish(state, message, message.from_user.id, description=message.text.strip())

@router.callback_query(TransactionStates.entering_description, F.data == "fsm_skip_desc")
async def process_skip_description(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await save_transaction_and_finish(state, callback.message, callback.from_user.id, description="Внесено через FSM бота 🤖")


async def save_transaction_and_finish(state: FSMContext, message: types.Message, tx_service: TransactionService,
                                      description: str | None):
    data = await state.get_data()
    tx_type = data["transaction_type"]

    if tx_type == "expense":
        await tx_service.add_expense(
            account_id=uuid.UUID(data["account_id"]),
            category_id=int(data["category_id"]),
            amount=Decimal(data['amount']),
            description=description,
        )
        text = "✅ Расход успешно добавлен!"
    else:
        await tx_service.add_income(
            account_id=uuid.UUID(data["account_id"]),
            category_id=int(data["category_id"]),
            amount=Decimal(data['amount']),
            description=description,
        )
        text = "✅ Доход успешно добавлен!"

    await state.clear()
    await message.answer(text)
