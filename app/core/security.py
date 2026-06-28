from datetime import UTC, datetime, timedelta

import bcrypt
from jose import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(data: dict[str, object]) -> str:
    payload: dict[str, object] = data.copy()
    expires = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["exp"] = expires
    return str(jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM))


def decode_token(token: str) -> dict[str, object]:
    return dict(jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]))
