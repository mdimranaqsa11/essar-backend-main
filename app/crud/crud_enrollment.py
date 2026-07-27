from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enrollment import Enrollment, EnrollmentStatus


async def get_enrollment(db: AsyncSession, enrollment_id: int) -> Enrollment | None:
    result = await db.execute(
        select(Enrollment).where(Enrollment.enrollment_id == enrollment_id)
    )
    return result.scalar_one_or_none()


async def get_user_course_enrollment(
    db: AsyncSession, user_id: int, course_id: int
) -> Enrollment | None:
    result = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == user_id, Enrollment.course_id == course_id
        )
    )
    return result.scalar_one_or_none()


async def get_enrollments_for_user(db: AsyncSession, user_id: int) -> list[Enrollment]:
    result = await db.execute(
        select(Enrollment)
        .where(Enrollment.user_id == user_id)
        .order_by(Enrollment.enrollment_id.desc())
    )
    return list(result.scalars().all())


async def get_all_enrollments(db: AsyncSession) -> list[Enrollment]:
    result = await db.execute(select(Enrollment).order_by(Enrollment.enrollment_id.desc()))
    return list(result.scalars().all())


async def create_enrollment(db: AsyncSession, user_id: int, course_id: int) -> Enrollment:
    # no payment yet, so we mark them Enrolled right away
    enrollment = Enrollment(
        user_id=user_id, course_id=course_id, enrollment_status=EnrollmentStatus.Enrolled
    )
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


async def update_status(
    db: AsyncSession, enrollment: Enrollment, new_status: EnrollmentStatus
) -> Enrollment:
    enrollment.enrollment_status = new_status
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


async def cancel_enrollment(db: AsyncSession, enrollment: Enrollment) -> Enrollment:
    """Admin cancels a user's enrollment: mark cancelled AND turn off `status` (soft-delete)."""
    enrollment.enrollment_status = EnrollmentStatus.Cancelled
    enrollment.status = False
    await db.commit()
    await db.refresh(enrollment)
    return enrollment
