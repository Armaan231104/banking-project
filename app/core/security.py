from datetime import datetime, timedelta, timezone
from uuid import uuid4
from jose import jwt, JWTError
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_token(subject: str, secret: str, algorithm: str, expires_delta: timedelta, token_type: str) -> tuple[str, str, datetime]:
    now = datetime.now(timezone.utc)
    exp = now + expires_delta
    jti = str(uuid4())
    payload = {'sub': subject, 'jti': jti, 'type': token_type, 'iat': int(now.timestamp()), 'exp': int(exp.timestamp())}
    return jwt.encode(payload, secret, algorithm=algorithm), jti, exp


def decode_token(token: str, secret: str, algorithm: str) -> dict:
    try:
        return jwt.decode(token, secret, algorithms=[algorithm])
    except JWTError as exc:
        raise ValueError('Invalid token') from exc
