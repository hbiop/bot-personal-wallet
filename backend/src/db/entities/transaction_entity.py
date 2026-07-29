from src.db.db_utils.base_entity import Base
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, DateTime, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.entities.account_entity import Account

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("NOW()"))

    account: Mapped["Account"] = relationship(back_populates="transactions")