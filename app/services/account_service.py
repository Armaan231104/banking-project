from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.aws import upload_and_sign
from app.db.models.account import Account
from app.db.models.transaction import Transaction
from app.services.audit_service import log_event


def create_account(db: Session, user_id: int, currency: str, ip: str | None, user_agent: str | None):
    account = Account(owner_id=user_id, account_id=f'ACCT-{uuid4().hex[:16]}', currency=currency.upper(), balance=0)
    db.add(account)
    db.flush()
    log_event(db, 'account_create', 'account', account.account_id, user_id, ip, user_agent)
    db.commit()
    return account


def get_owned_account(db: Session, user_id: int, public_id: str) -> Account:
    account = db.query(Account).filter_by(account_id=public_id).first()
    if not account:
        raise HTTPException(status_code=404, detail='Account not found')
    if account.owner_id != user_id:
        raise HTTPException(status_code=403, detail='Forbidden')
    return account


def export_statement(db: Session, account: Account, user_id: int, ip: str | None, user_agent: str | None) -> str:
    txs = db.query(Transaction).filter((Transaction.source_account_id == account.id) | (Transaction.destination_account_id == account.id)).order_by(Transaction.created_at.desc()).all()
    rows = ['id,type,amount,currency,created_at'] + [f'{t.id},{t.type.value},{t.amount},{t.currency},{t.created_at.isoformat()}' for t in txs]
    settings = get_settings()
    key = f"{settings.s3_prefix}/{account.account_id}.csv"
    try:
        url = upload_and_sign(key, '\n'.join(rows))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    log_event(db, 'statement_export', 'account', account.account_id, user_id, ip, user_agent)
    db.commit()
    return url
