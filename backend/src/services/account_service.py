import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.entities.account_entity import Account
from src.repository.transaction_repository import TransactionRepository
from src.repository.user_repository import UserRepository


class AccountService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_all_accounts_by_user_id(self, user_id: int) -> list[Account]:
        account = await self.user_repo.get_all_accounts(user_id)
        return account