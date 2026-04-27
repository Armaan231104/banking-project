import enum
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class LedgerEntryType(str, enum.Enum):
    debit = 'debit'
    credit = 'credit'


class LedgerEntry(Base):
    __tablename__ = 'ledger_entries'

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey('transactions.id'), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), index=True)
    entry_type: Mapped[LedgerEntryType] = mapped_column(Enum(LedgerEntryType))
    amount: Mapped[float] = mapped_column(Numeric(14, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
