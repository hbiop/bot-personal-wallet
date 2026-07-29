from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.db_utils.base_entity import Base

# Этот блок виден только для PyCharm/линтеров, Python его игнорирует при запуске
if TYPE_CHECKING:
    from src.db.entities.account_entity import Account


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True
    )
    username: Mapped[str | None] = mapped_column(String(32))
    currency: Mapped[str] = mapped_column(String(3), server_default="RUB")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("NOW()")
    )

    accounts: Mapped[list["Account"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )