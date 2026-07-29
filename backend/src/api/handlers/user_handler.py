from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db_utils.session_maker import get_db
from src.repository.user_repository import UserRepository
from src.api.schemas.user_schemas import UserCreate, UserResponse

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)

    existing_user = await user_repo.get_by_id(user_data.id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Пользователь с Telegram ID {user_data.id} уже зарегистрирован."
        )

    new_user = await user_repo.register_new_user(
        user_id=user_data.id,
        username=user_data.username,
        currency=user_data.currency
    )

    return new_user
