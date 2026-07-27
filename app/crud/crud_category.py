from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import CourseCategory
from app.schemas.category import CategoryCreate, CategoryUpdate


async def get_categories(db: AsyncSession, only_active: bool = True) -> list[CourseCategory]:
    query = select(CourseCategory)
    if only_active:
        query = query.where(CourseCategory.status.is_(True))
    query = query.order_by(CourseCategory.category_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_category(db: AsyncSession, category_id: int) -> CourseCategory | None:
    result = await db.execute(
        select(CourseCategory).where(CourseCategory.category_id == category_id)
    )
    return result.scalar_one_or_none()


async def create_category(db: AsyncSession, data: CategoryCreate) -> CourseCategory:
    category = CourseCategory(category_name=data.category_name)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(
    db: AsyncSession, category: CourseCategory, data: CategoryUpdate
) -> CourseCategory:
    # only update the fields the client actually sent
    if data.category_name is not None:
        category.category_name = data.category_name
    if data.status is not None:
        category.status = data.status
    await db.commit()
    await db.refresh(category)
    return category


async def soft_delete_category(db: AsyncSession, category: CourseCategory) -> None:
    # we don't really delete the row, just mark status = False (safer, keeps history)
    category.status = False
    await db.commit()
