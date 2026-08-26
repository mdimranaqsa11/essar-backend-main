from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.user_id == user_id))
    return result.scalar_one_or_none()


async def get_all_users(db: AsyncSession, role: str | None = None) -> list[User]:
    query = select(User)
    if role is not None:
        query = query.where(User.role == role)
    query = query.order_by(User.user_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    user = User(
        name=user_in.name,
        email=user_in.email,
        phone=user_in.phone,
        password=hash_password(user_in.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()


async def update_user(db: AsyncSession, user: User, data: UserUpdate) -> User:
    if data.name is not None:
        user.name = data.name
    if data.phone is not None:
        user.phone = data.phone
    if data.email is not None:
        user.email = data.email
    if data.password is not None:
        user.password = hash_password(data.password)  # always store the hash
    if data.image is not None:
        user.image = data.image
    await db.commit()
    await db.refresh(user)
    return user
