from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.core.config import get_settings
from app.db.models.account import Account
from app.db.models.transaction import Transaction, TransactionType
from app.db.models.ledger_entry import LedgerEntry, LedgerEntryType
from app.services.audit_service import log_event


def _existing_by_idempotency(db: Session, key: str | None):
    if not key:
        return None
    return db.query(Transaction).filter_by(idempotency_key=key).first()


def deposit(db: Session, user_id: int, account_id: str, amount: float, currency: str, idem: str | None, description: str | None, ip: str | None, user_agent: str | None):
    existing = _existing_by_idempotency(db, idem)
    if existing:
        return existing
    acct = db.execute(select(Account).where(Account.account_id == account_id).with_for_update()).scalar_one_or_none()
    if not acct or acct.owner_id != user_id:
        raise HTTPException(status_code=404, detail='Account not found')
    if acct.currency != currency:
        raise HTTPException(status_code=400, detail='Currency mismatch')
    acct.balance = float(acct.balance) + amount
    flagged = amount >= get_settings().fraud_threshold
    tx = Transaction(type=TransactionType.deposit, destination_account_id=acct.id, amount=amount, currency=currency, idempotency_key=idem, flagged_fraud=flagged, description=description)
    db.add(tx)
    db.flush()
    db.add(LedgerEntry(transaction_id=tx.id, account_id=acct.id, entry_type=LedgerEntryType.credit, amount=amount))
    log_event(db, 'deposit', 'transaction', str(tx.id), user_id, ip, user_agent)
    db.commit()
    return tx


def withdraw(db: Session, user_id: int, account_id: str, amount: float, currency: str, idem: str | None, description: str | None, ip: str | None, user_agent: str | None):
    existing = _existing_by_idempotency(db, idem)
    if existing:
        return existing
    acct = db.execute(select(Account).where(Account.account_id == account_id).with_for_update()).scalar_one_or_none()
    if not acct or acct.owner_id != user_id:
        raise HTTPException(status_code=404, detail='Account not found')
    if acct.currency != currency:
        raise HTTPException(status_code=400, detail='Currency mismatch')
    if float(acct.balance) < amount:
        raise HTTPException(status_code=400, detail='Insufficient funds')
    acct.balance = float(acct.balance) - amount
    flagged = amount >= get_settings().fraud_threshold
    tx = Transaction(type=TransactionType.withdrawal, source_account_id=acct.id, amount=amount, currency=currency, idempotency_key=idem, flagged_fraud=flagged, description=description)
    db.add(tx)
    db.flush()
    db.add(LedgerEntry(transaction_id=tx.id, account_id=acct.id, entry_type=LedgerEntryType.debit, amount=amount))
    log_event(db, 'withdraw', 'transaction', str(tx.id), user_id, ip, user_agent)
    db.commit()
    return tx


def transfer(db: Session, user_id: int, source_id: str, dest_id: str, amount: float, currency: str, idem: str | None, description: str | None, ip: str | None, user_agent: str | None):
    existing = _existing_by_idempotency(db, idem)
    if existing:
        return existing
    src = db.execute(select(Account).where(Account.account_id == source_id).with_for_update()).scalar_one_or_none()
    dst = db.execute(select(Account).where(Account.account_id == dest_id).with_for_update()).scalar_one_or_none()
    if not src or src.owner_id != user_id:
        raise HTTPException(status_code=404, detail='Source account not found')
    if not dst:
        raise HTTPException(status_code=404, detail='Destination account not found')
    if src.currency != currency or dst.currency != currency:
        raise HTTPException(status_code=400, detail='Currency mismatch')
    if float(src.balance) < amount:
        raise HTTPException(status_code=400, detail='Insufficient funds')
    src.balance = float(src.balance) - amount
    dst.balance = float(dst.balance) + amount
    flagged = amount >= get_settings().fraud_threshold
    tx = Transaction(type=TransactionType.transfer, source_account_id=src.id, destination_account_id=dst.id, amount=amount, currency=currency, idempotency_key=idem, flagged_fraud=flagged, description=description)
    db.add(tx)
    db.flush()
    db.add(LedgerEntry(transaction_id=tx.id, account_id=src.id, entry_type=LedgerEntryType.debit, amount=amount))
    db.add(LedgerEntry(transaction_id=tx.id, account_id=dst.id, entry_type=LedgerEntryType.credit, amount=amount))
    log_event(db, 'transfer', 'transaction', str(tx.id), user_id, ip, user_agent)
    db.commit()
    return tx


def history(db: Session, user_id: int, account_id: str, page: int, size: int):
    account = db.query(Account).filter_by(account_id=account_id).first()
    if not account or account.owner_id != user_id:
        raise HTTPException(status_code=404, detail='Account not found')
    q = db.query(Transaction).filter(or_(Transaction.source_account_id == account.id, Transaction.destination_account_id == account.id)).order_by(Transaction.created_at.desc())
    return q.offset((page - 1) * size).limit(size).all()
