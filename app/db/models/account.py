from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, CheckConstraint, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class Account(Base):
    __tablename__ = 'accounts'
    __table_args__ = (CheckConstraint('balance >= 0', name='ck_accounts_balance_non_negative'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    account_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    balance: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default='USD')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
