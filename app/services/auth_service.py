from datetime import timedelta
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.redis_client import get_redis
from app.core.security import hash_password, verify_password, create_token, decode_token
from app.db.models.user import User
from app.db.models.refresh_token import RefreshToken
from app.services.audit_service import log_event


def register(db: Session, email: str, full_name: str, password: str, request: Request):
    if db.query(User).filter_by(email=email).first():
        raise HTTPException(status_code=409, detail='Email already exists')
    user = User(email=email, full_name=full_name, password_hash=hash_password(password))
    db.add(user)
    db.flush()
    log_event(db, 'register', 'user', str(user.id), user.id, request.client.host if request.client else None, request.headers.get('user-agent'))
    db.commit()
    return user


def login(db: Session, email: str, password: str, request: Request):
    ip = request.client.host if request.client else 'unknown'
    redis = get_redis()
    settings = get_settings()
    key = f'login:{ip}'
    count = redis.incr(key)
    if count == 1:
        redis.expire(key, 60)
    if count > settings.login_rate_limit_per_minute:
        raise HTTPException(status_code=429, detail='Rate limit exceeded')
    user = db.query(User).filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        log_event(db, 'login_failed', 'auth', user_id=user.id if user else None, ip=ip, user_agent=request.headers.get('user-agent'))
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    access, _, _ = create_token(str(user.id), settings.jwt_secret, settings.jwt_algorithm, timedelta(minutes=settings.access_token_minutes), 'access')
    refresh, jti, exp = create_token(str(user.id), settings.jwt_secret, settings.jwt_algorithm, timedelta(days=settings.refresh_token_days), 'refresh')
    db.add(RefreshToken(user_id=user.id, token_jti=jti, expires_at=exp))
    log_event(db, 'login_success', 'auth', user_id=user.id, ip=ip, user_agent=request.headers.get('user-agent'))
    db.commit()
    return {'access_token': access, 'refresh_token': refresh}


def refresh(db: Session, refresh_token: str, request: Request):
    settings = get_settings()
    payload = decode_token(refresh_token, settings.jwt_secret, settings.jwt_algorithm)
    if payload.get('type') != 'refresh':
        raise HTTPException(status_code=401, detail='Invalid token type')
    row = db.query(RefreshToken).filter_by(token_jti=payload['jti']).first()
    if not row or row.revoked:
        raise HTTPException(status_code=401, detail='Refresh token revoked or reused')
    row.revoked = True
    access, _, _ = create_token(payload['sub'], settings.jwt_secret, settings.jwt_algorithm, timedelta(minutes=settings.access_token_minutes), 'access')
    new_refresh, new_jti, exp = create_token(payload['sub'], settings.jwt_secret, settings.jwt_algorithm, timedelta(days=settings.refresh_token_days), 'refresh')
    row.replaced_by_jti = new_jti
    db.add(RefreshToken(user_id=int(payload['sub']), token_jti=new_jti, expires_at=exp))
    log_event(db, 'refresh', 'auth', user_id=int(payload['sub']), ip=request.client.host if request.client else None, user_agent=request.headers.get('user-agent'))
    db.commit()
    return {'access_token': access, 'refresh_token': new_refresh}


def logout(db: Session, refresh_token: str, request: Request):
    settings = get_settings()
    payload = decode_token(refresh_token, settings.jwt_secret, settings.jwt_algorithm)
    row = db.query(RefreshToken).filter_by(token_jti=payload.get('jti')).first()
    if row:
        row.revoked = True
        log_event(db, 'logout', 'auth', user_id=row.user_id, ip=request.client.host if request.client else None, user_agent=request.headers.get('user-agent'))
        db.commit()
