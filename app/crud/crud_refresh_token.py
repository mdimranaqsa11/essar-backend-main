from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import generate_refresh_token, hash_refresh_token
from app.models.refresh_token import RefreshToken


async def create_refresh_token(db: AsyncSession, user_id: int) -> str:
    """Creates a row in the DB (hash only) and returns the RAW token — the raw
    value is only ever handed to the client, never stored or logged."""
    raw_token = generate_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    db.add(
        RefreshToken(
            user_id=user_id,
            token_hash=hash_refresh_token(raw_token),
            expires_at=expires_at,
        )
    )
    await db.commit()
    return raw_token


async def get_active_refresh_token(db: AsyncSession, raw_token: str) -> RefreshToken | None:
    """Returns the row only if it's not revoked and not expired."""
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(raw_token),
            RefreshToken.status.is_(True),
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    return result.scalar_one_or_none()


async def revoke_refresh_token(db: AsyncSession, token_row: RefreshToken) -> None:
    token_row.status = False
    await db.commit()
