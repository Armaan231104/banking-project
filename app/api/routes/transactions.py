from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.transaction import DepositRequest, WithdrawRequest, TransferRequest, TransactionOut
from app.services import transaction_service

router = APIRouter(prefix='/transactions', tags=['transactions'])


def _to_out(tx):
    return TransactionOut(id=tx.id, type=tx.type.value, amount=float(tx.amount), currency=tx.currency, flagged_fraud=tx.flagged_fraud)


@router.post('/deposit', response_model=TransactionOut)
def deposit(payload: DepositRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tx = transaction_service.deposit(db, user.id, payload.account_id, payload.amount, payload.currency, payload.idempotency_key, payload.description, request.client.host if request.client else None, request.headers.get('user-agent'))
    return _to_out(tx)


@router.post('/withdraw', response_model=TransactionOut)
def withdraw(payload: WithdrawRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tx = transaction_service.withdraw(db, user.id, payload.account_id, payload.amount, payload.currency, payload.idempotency_key, payload.description, request.client.host if request.client else None, request.headers.get('user-agent'))
    return _to_out(tx)


@router.post('/transfer', response_model=TransactionOut)
def transfer(payload: TransferRequest, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tx = transaction_service.transfer(db, user.id, payload.source_account_id, payload.destination_account_id, payload.amount, payload.currency, payload.idempotency_key, payload.description, request.client.host if request.client else None, request.headers.get('user-agent'))
    return _to_out(tx)


@router.get('/{account_id}', response_model=list[TransactionOut])
def history(account_id: str, page: int = 1, size: int = 20, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    txs = transaction_service.history(db, user.id, account_id, page, size)
    return [_to_out(tx) for tx in txs]
