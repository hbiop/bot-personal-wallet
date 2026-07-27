from src.db_utils.base_entity import Base
import uuid
from decimal import Decimal
from sqlalchemy import BigInteger, ForeignKey, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.entities.user_entity import User
from src.entities.transaction_entity import Transaction

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(50))
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0.00")

    user: Mapped["User"] = relationship(back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account", cascade="all, delete-orphan")
