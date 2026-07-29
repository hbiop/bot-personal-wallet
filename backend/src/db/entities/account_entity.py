import uuid
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.db_utils.base_entity import Base

if TYPE_CHECKING:
    from src.db.entities.transaction_entity import Transaction
    from src.db.entities.user_entity import User


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(50))
    balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), server_default="0.00"
    )

    user: Mapped["User"] = relationship(back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
