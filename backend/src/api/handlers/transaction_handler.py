from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db_utils.session_maker import get_db
from src.api.schemas.transaction_schemas import TransactionCreate, TransactionResponse
from src.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/v1/transactions", tags=["Transactions"])


@router.post(
    "/expense",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить новый расход"
)
async def create_expense(
        payload: TransactionCreate,
        db: AsyncSession = Depends(get_db)
):
    tx_service = TransactionService(db)

    new_expense = await tx_service.add_expense(
        account_id=payload.account_id,
        category_id=payload.category_id,
        amount=payload.amount,
        description=payload.description
    )

    return new_expense
