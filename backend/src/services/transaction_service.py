import uuid
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.transaction_repository import TransactionRepository
from src.db.entities.transaction_entity import Transaction

class TransactionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.tx_repo = TransactionRepository(db)

    async def add_expense(
        self,
        account_id: uuid.UUID,
        category_id: int,
        amount: Decimal,
        description: str | None
    ) -> Transaction:
        account = await self.tx_repo.get_account(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Указанный счет не найден."
            )

        if account.balance < amount:
            raise HTTPException(status_code=400, detail="Недостаточно средств на счете.")

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Указанный счет не найден."
        )
    transaction = await self.tx_repo.create(account_id, category_id, amount, description)

    await self.tx_repo.update_account_balance(account_id, amount)

    await self.db.commit()
    await self.db.refresh(transaction)
    return transaction