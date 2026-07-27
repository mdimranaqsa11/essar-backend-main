import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.core.config import settings


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.JWTError:
        return None


def generate_refresh_token() -> str:
    """Opaque random string (NOT a JWT) — it's looked up in the DB, never decoded."""
    return secrets.token_urlsafe(32)


def hash_refresh_token(raw_token: str) -> str:
    """We store this hash in the DB, never the raw token — same idea as password hashing,
    so a DB leak alone can't be used to log in as someone."""
    return hashlib.sha256(raw_token.encode()).hexdigest()
