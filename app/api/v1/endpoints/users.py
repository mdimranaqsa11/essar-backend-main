from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user
from app.crud.crud_user import get_all_users, get_user_by_email, update_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserOut, UserUpdate
from app.utils.response import success
from app.utils.upload import upload_or_none

router = APIRouter()


# ---------- ADMIN: list all users ----------
@router.get("")
async def list_users(
    role: UserRole | None = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    users = await get_all_users(db, role=role.value if role else None)
    data = [UserOut.model_validate(u) for u in users]
    return success(data, message="Users fetched")


# ---------- get own profile ----------
@router.get("/me")
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return success(UserOut.model_validate(current_user), message="Profile fetched")


# ---------- update own profile (multipart: fields + optional image file) ----------
@router.put("/me")
async def update_my_profile(
    name: str | None = Form(None),
    phone: int | None = Form(None),
    email: EmailStr | None = Form(None),
    password: str | None = Form(None),
    image: str | None = Form(None, description="Optional image URL (used if no image_file)"),
    image_file: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # if changing email, make sure it's not already taken by someone else
    if email and email != current_user.email:
        existing = await get_user_by_email(db, email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
            )

    # a file (if sent) wins over a plain URL
    image = await upload_or_none(image_file, "essar/profiles") or image

    fields = {"name": name, "phone": phone, "email": email, "password": password, "image": image}
    # ignore fields not sent (None) and empty text fields (so a blank form field never wipes data)
    provided = {k: v for k, v in fields.items() if v is not None and v != ""}

    user = await update_user(db, current_user, UserUpdate(**provided))
    return success(UserOut.model_validate(user), message="Profile updated")
