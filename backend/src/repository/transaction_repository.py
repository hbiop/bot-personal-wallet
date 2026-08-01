import uuid
from decimal import Decimal
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.entities.transaction_entity import Transaction
from src.db.entities.account_entity import Account

class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, account_id: uuid.UUID, category_id: int, amount: Decimal, description: str | None) -> Transaction:
        new_transaction = Transaction(
            account_id=account_id,
            category_id=category_id,
            amount=amount,
            description=description
        )
        self.db.add(new_transaction)
        return new_transaction

    async def update_account_balance(self, account_id: uuid.UUID, amount: Decimal) -> None:
        stmt = (
            update(Account)
            .where(Account.id == account_id)
            .values(balance=Account.balance + amount)
        )
        await self.db.execute(stmt)

    async def get_account(self, account_id: uuid.UUID) -> Account | None:
        query = select(Account).where(Account.id == account_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


