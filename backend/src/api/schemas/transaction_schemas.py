import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class TransactionCreate(BaseModel):
    account_id: uuid.UUID = Field(
        ...,
        description="ID счета (UUID), с которого списываются деньги"
    )
    category_id: int = Field(
        ...,
        ge=1,
        description="ID категории расхода из базы данных"
    )
    amount: Decimal = Field(
        ...,
        description="Сумма расхода (должна быть строго положительной)"
    )
    description: str | None = Field(
        default=None,
        max_length=250,
        description="Комментарий к трате (необязательно, макс. 250 символов)"
    )

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("Сумма транзакции должна быть строго больше нуля.")

        return value.quantize(Decimal("0.01"))


class TransactionResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Уникальный UUID созданной транзакции")
    account_id: uuid.UUID
    category_id: int
    amount: Decimal
    description: str | None
    created_at: datetime = Field(..., description="Точное время создания транзакции")

    model_config = {
        "from_attributes": True
    }
