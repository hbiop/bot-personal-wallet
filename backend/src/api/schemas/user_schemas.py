from pydantic import BaseModel, Field
from datetime import datetime

class UserCreate(BaseModel):
    id: int = Field(..., description="Telegram ID пользователя")
    username: str | None = Field(None, max_length=32, description="Юзернейм в Telegram")
    currency: str = Field(default="RUB", max_length=3, description="Базовая валюта")

class UserResponse(BaseModel):
    id: int
    username: str | None
    currency: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
