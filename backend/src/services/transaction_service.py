import uuid
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped
from sqlalchemy import func, select
from datetime import datetime, timedelta
from src.custom_exeptions.account_not_found import AccountNotFoundError
from src.custom_exeptions.insufficient_funds import InsufficientFundsError
from src.db.entities.account_entity import Account
from src.db.entities.category_entity import Category
from src.repository.transaction_repository import TransactionRepository
from src.db.entities.transaction_entity import Transaction

class TransactionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.tx_repo = TransactionRepository(db)

    async def check_balance(self, account_id: uuid.UUID) -> Decimal | None:
        account = await self.tx_repo.get_account(account_id)

        if not account:
            return None

        return account.balance

    async def add_expense(
        self,
        account_id: uuid.UUID,
        category_id: int,
        amount: Decimal,
        description: str | None
    ) -> Transaction:
        account = await self.tx_repo.get_account(account_id)
        if not account:
            raise AccountNotFoundError("Счёт не найден.")
        if account.balance < amount:
            raise InsufficientFundsError("Недостаточно средств.")

        transaction = await self.tx_repo.create(
            account_id=account_id,
            category_id=category_id,
            amount=amount,
            description=description
        )

        await self.tx_repo.update_account_balance(account_id, -amount)

        await self.db.commit()
        await self.db.refresh(transaction)

        return transaction


    async def add_income(
            self, account_id: uuid.UUID, category_id: int, amount: Decimal, description: str | None
    ) -> Transaction:
        account = await self.tx_repo.get_account(account_id)
        if not account:
            raise AccountNotFoundError("Счёт не найден.")

        transaction = await self.tx_repo.create(account_id, category_id, amount, description)

        await self.tx_repo.update_account_balance(account_id, amount)

        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def get_monthly_statistics(self, user_id: int, tx_type: str = "expense") -> list[tuple[str, float]]:
        """
        Получает агрегированные данные: Название категории и Сумма транзакций.
        Фильтрует по user_id (через accounts), типу категории и за последние 30 дней.
        """
        start_date = datetime.now() - timedelta(days=30)

        query = (
            select(Category.name, func.sum(Transaction.amount))
            .join(Transaction, Transaction.category_id == Category.id)
            .join(Account, Transaction.account_id == Account.id)
            .where(
                Account.user_id == user_id,
                Category.type == tx_type,
                Transaction.created_at >= start_date
            )
            .group_by(Category.name)
        )

        result = await self.db.execute(query)
        return [(row[0], float(row[1])) for row in result.all()]

