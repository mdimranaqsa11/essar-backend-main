from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user
from app.crud import crud_course, crud_enrollment, crud_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.enrollment import (
    EnrollmentAdminOut,
    EnrollmentCreate,
    EnrollmentOut,
    EnrollmentStatusUpdate,
    EnrollmentWithCourse,
)
from app.utils.response import success

router = APIRouter()


# ---------- USER: enroll into a course ----------
@router.post("", status_code=status.HTTP_201_CREATED)
async def enroll(
    data: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = await crud_course.get_course(db, data.course_id)
    if not course or not course.status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    existing = await crud_enrollment.get_user_course_enrollment(
        db, current_user.user_id, data.course_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already enrolled in this course"
        )

    enrollment = await crud_enrollment.create_enrollment(db, current_user.user_id, data.course_id)
    return success(EnrollmentOut.model_validate(enrollment), message="Enrolled successfully")


# ---------- USER: my enrolled courses ----------
@router.get("/my")
async def my_enrollments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enrollments = await crud_enrollment.get_enrollments_for_user(db, current_user.user_id)
    data = [EnrollmentWithCourse.model_validate(e) for e in enrollments]
    return success(data, message="My enrollments fetched")


# ---------- ADMIN: all enrollments ----------
@router.get("")
async def all_enrollments(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    enrollments = await crud_enrollment.get_all_enrollments(db)
    data = [EnrollmentAdminOut.model_validate(e) for e in enrollments]
    return success(data, message="All enrollments fetched")


# ---------- ADMIN: a specific user's enrolled courses ----------
@router.get("/user/{user_id}")
async def enrollments_for_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user = await crud_user.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    enrollments = await crud_enrollment.get_enrollments_for_user(db, user_id)
    data = [EnrollmentWithCourse.model_validate(e) for e in enrollments]
    return success(data, message="User's enrollments fetched")


# ---------- ADMIN: change an enrollment's status ----------
@router.patch("/{enrollment_id}/status")
async def update_enrollment_status(
    enrollment_id: int,
    data: EnrollmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    enrollment = await crud_enrollment.get_enrollment(db, enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    enrollment = await crud_enrollment.update_status(db, enrollment, data.enrollment_status)
    return success(EnrollmentOut.model_validate(enrollment), message="Enrollment status updated")


# ---------- ADMIN: cancel a user's enrollment ----------
@router.delete("/{enrollment_id}")
async def cancel_enrollment(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    enrollment = await crud_enrollment.get_enrollment(db, enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    enrollment = await crud_enrollment.cancel_enrollment(db, enrollment)
    return success(EnrollmentOut.model_validate(enrollment), message="Enrollment cancelled")
