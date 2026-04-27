import enum
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Numeric, Boolean, CheckConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class TransactionType(str, enum.Enum):
    deposit = 'deposit'
    withdrawal = 'withdrawal'
    transfer = 'transfer'


class Transaction(Base):
    __tablename__ = 'transactions'
    __table_args__ = (CheckConstraint('amount > 0', name='ck_transactions_amount_positive'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType))
    source_account_id: Mapped[int | None] = mapped_column(ForeignKey('accounts.id'), nullable=True)
    destination_account_id: Mapped[int | None] = mapped_column(ForeignKey('accounts.id'), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3))
    idempotency_key: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    flagged_fraud: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
