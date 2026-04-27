from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest, TokenResponse, LogoutRequest
from app.services import auth_service

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register')
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    user = auth_service.register(db, payload.email, payload.full_name, payload.password, request)
    return {'id': user.id, 'email': user.email}


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    return auth_service.login(db, payload.email, payload.password, request)


@router.post('/refresh', response_model=TokenResponse)
def refresh(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    return auth_service.refresh(db, payload.refresh_token, request)


@router.post('/logout')
def logout(payload: LogoutRequest, request: Request, db: Session = Depends(get_db)):
    auth_service.logout(db, payload.refresh_token, request)
    return {'status': 'ok'}
