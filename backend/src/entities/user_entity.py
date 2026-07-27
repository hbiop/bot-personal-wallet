from src.db_utils.base_entity import Base
from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.entities.account_entity import Account

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram ID
    username: Mapped[str | None] = mapped_column(String(32))
    currency: Mapped[str] = mapped_column(String(3), server_default="RUB")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("NOW()"))

    accounts: Mapped[list["Account"]] = relationship(back_populates="user", cascade="all, delete-orphan")



