from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.models.account import Account
from app.db.session import get_db
from app.schemas.account import AccountCreate, AccountOut, StatementExportResponse
from app.services import account_service

router = APIRouter(prefix='/accounts', tags=['accounts'])


@router.post('/', response_model=AccountOut)
def create_account(payload: AccountCreate, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    account = account_service.create_account(db, user.id, payload.currency, request.client.host if request.client else None, request.headers.get('user-agent'))
    return AccountOut(account_id=account.account_id, balance=float(account.balance), currency=account.currency)


@router.get('/', response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    accounts = db.query(Account).filter_by(owner_id=user.id).all()
    return [AccountOut(account_id=a.account_id, balance=float(a.balance), currency=a.currency) for a in accounts]


@router.get('/{account_id}', response_model=AccountOut)
def get_account(account_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    account = account_service.get_owned_account(db, user.id, account_id)
    return AccountOut(account_id=account.account_id, balance=float(account.balance), currency=account.currency)


@router.post('/{account_id}/statements/export', response_model=StatementExportResponse)
def export_statement(account_id: str, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    account = account_service.get_owned_account(db, user.id, account_id)
    url = account_service.export_statement(db, account, user.id, request.client.host if request.client else None, request.headers.get('user-agent'))
    return StatementExportResponse(download_url=url)
