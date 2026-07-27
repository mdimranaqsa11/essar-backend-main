from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.crud.crud_refresh_token import (
    create_refresh_token,
    get_active_refresh_token,
    revoke_refresh_token,
)
from app.crud.crud_user import create_user, get_user_by_email
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import RefreshRequest, Token
from app.schemas.user import UserCreate, UserOut
from app.utils.response import success

router = APIRouter()


@router.post("/register")
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = await create_user(db, user_in)
    return success(UserOut.model_validate(user), message="User registered successfully")


# NOTE: /login is the OAuth2 token endpoint. It returns the STANDARD shape
# {access_token, refresh_token, token_type} (NOT the envelope) so Swagger's
# Authorize and any OAuth2 client work out of the box. This is the one
# intentional exception.
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token = create_access_token(subject=user.email)
    refresh_token = await create_refresh_token(db, user.user_id)
    return Token(access_token=access_token, refresh_token=refresh_token)


# The app calls this silently whenever an API call gets a 401 because the
# access token (60 min) expired — it swaps a still-valid refresh token
# (30 days, see REFRESH_TOKEN_EXPIRE_DAYS) for a new pair, so the user is
# never forced back to the login screen until the refresh token itself runs out.
# Rotation: the old refresh token is revoked and a new one issued on every
# call, so a stolen-and-reused old token stops working.
@router.post("/refresh")
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_row = await get_active_refresh_token(db, payload.refresh_token)
    if token_row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user = await db.get(User, token_row.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    await revoke_refresh_token(db, token_row)

    new_access_token = create_access_token(subject=user.email)
    new_refresh_token = await create_refresh_token(db, user.user_id)
    return success(
        Token(access_token=new_access_token, refresh_token=new_refresh_token),
        message="Token refreshed",
    )


# Called on explicit user logout — revokes just this device's refresh token
# so it can no longer be used, even though it hasn't expired yet.
@router.post("/logout")
async def logout(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_row = await get_active_refresh_token(db, payload.refresh_token)
    if token_row is not None:
        await revoke_refresh_token(db, token_row)
    return success(None, message="Logged out successfully")


@router.get("/me")
async def read_current_user(current_user: User = Depends(get_current_user)):
    return success(UserOut.model_validate(current_user), message="Current user fetched")
