from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.entities.user_entity import User
from src.db.entities.account_entity import Account
from src.db.entities.category_entity import Category
from src.db.db_utils.default_categories import DEFAULT_CATEGORIES

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_accounts(self, user_id: int) -> list[Account]:
        query = select(Account).where(Account.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def register_new_user(self, user_id: int, username: str | None, currency: str) -> User:
        new_user = User(id=user_id, username=username, currency=currency)
        self.db.add(new_user)

        await self.db.flush()

        default_account = Account(
            user_id=new_user.id,
            name="💵 Наличные",
            balance=Decimal("0.00")
        )
        self.db.add(default_account)

        for cat_data in DEFAULT_CATEGORIES:
            default_category = Category(
                user_id=new_user.id,
                name=cat_data["name"],
                type=cat_data["type"],
                icon=cat_data["icon"]
            )
            self.db.add(default_category)

        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user
