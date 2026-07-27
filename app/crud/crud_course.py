from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import CourseCategory
from app.models.course import Course, CourseLevel, CourseMode
from app.schemas.course import CourseCreate, CourseUpdate


async def get_courses(
    db: AsyncSession,
    category_id: int | None = None,
    level: CourseLevel | None = None,
    mode: CourseMode | None = None,
    search: str | None = None,
    only_active: bool = True,
) -> list[Course]:
    query = select(Course)
    if only_active:
        query = query.where(Course.status.is_(True))
    if category_id is not None:
        query = query.where(Course.category_id == category_id)
    if level is not None:
        query = query.where(Course.level == level)
    if mode is not None:
        query = query.where(Course.mode == mode)
    if search:
        query = query.where(Course.title.ilike(f"%{search}%"))
    query = query.order_by(Course.course_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_course(db: AsyncSession, course_id: int) -> Course | None:
    result = await db.execute(select(Course).where(Course.course_id == course_id))
    return result.scalar_one_or_none()


async def category_exists(db: AsyncSession, category_id: int) -> bool:
    result = await db.execute(
        select(CourseCategory.category_id).where(CourseCategory.category_id == category_id)
    )
    return result.scalar_one_or_none() is not None


async def create_course(db: AsyncSession, data: CourseCreate) -> Course:
    course = Course(**data.model_dump())
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


async def update_course(db: AsyncSession, course: Course, data: CourseUpdate) -> Course:
    # only update the fields the client actually sent
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    await db.commit()
    await db.refresh(course)
    return course


async def soft_delete_course(db: AsyncSession, course: Course) -> None:
    course.status = False
    await db.commit()
