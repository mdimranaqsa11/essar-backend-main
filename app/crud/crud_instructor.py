from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.instructor import CourseInstructor, Instructor
from app.schemas.instructor import InstructorCreate, InstructorUpdate


async def get_instructors(db: AsyncSession, only_active: bool = True) -> list[Instructor]:
    query = select(Instructor)
    if only_active:
        query = query.where(Instructor.status.is_(True))
    query = query.order_by(Instructor.instructor_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_instructor(db: AsyncSession, instructor_id: int) -> Instructor | None:
    result = await db.execute(
        select(Instructor).where(Instructor.instructor_id == instructor_id)
    )
    return result.scalar_one_or_none()


async def create_instructor(db: AsyncSession, data: InstructorCreate) -> Instructor:
    instructor = Instructor(**data.model_dump())
    db.add(instructor)
    await db.commit()
    await db.refresh(instructor)
    return instructor


async def update_instructor(
    db: AsyncSession, instructor: Instructor, data: InstructorUpdate
) -> Instructor:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(instructor, field, value)
    await db.commit()
    await db.refresh(instructor)
    return instructor


async def soft_delete_instructor(db: AsyncSession, instructor: Instructor) -> None:
    instructor.status = False
    await db.commit()


# ---- course <-> instructor linking (join table) ----
async def get_link(db: AsyncSession, course_id: int, instructor_id: int) -> CourseInstructor | None:
    result = await db.execute(
        select(CourseInstructor).where(
            CourseInstructor.course_id == course_id,
            CourseInstructor.instructor_id == instructor_id,
        )
    )
    return result.scalar_one_or_none()


async def assign_instructor(db: AsyncSession, course_id: int, instructor_id: int) -> CourseInstructor:
    link = CourseInstructor(course_id=course_id, instructor_id=instructor_id)
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


async def get_instructors_for_course(db: AsyncSession, course_id: int) -> list[Instructor]:
    result = await db.execute(
        select(Instructor)
        .join(CourseInstructor, CourseInstructor.instructor_id == Instructor.instructor_id)
        .where(CourseInstructor.course_id == course_id)
        .order_by(Instructor.instructor_id)
    )
    return list(result.scalars().all())


async def unassign_instructor(db: AsyncSession, link: CourseInstructor) -> None:
    await db.delete(link)
    await db.commit()
