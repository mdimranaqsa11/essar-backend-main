from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: int | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ---- client SENDS when updating own profile (all optional) ----
class UserUpdate(BaseModel):
    name: str | None = None
    phone: int | None = None
    email: EmailStr | None = None
    password: str | None = None
    image: str | None = None


class UserOut(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    phone: int | None
    role: UserRole
    image: str | None
    status: bool
    created_at: datetime

    class Config:
        from_attributes = True
