from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.user_repository import UserRepository
from src.db.entities.user_entity import User


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def handle_user_start(self, user_id: int, username: str | None) -> tuple[User, bool]:

        user = await self.user_repo.get_by_id(user_id)

        if not user:
            user = await self.user_repo.register_new_user(
                user_id=user_id,
                username=username,
                currency="RUB"
            )
            return user, True

        return user, False
