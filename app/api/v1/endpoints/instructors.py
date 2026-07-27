from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.crud import crud_course, crud_instructor
from app.db.session import get_db
from app.models.user import User
from app.schemas.instructor import (
    AssignInstructor,
    InstructorCreate,
    InstructorOut,
    InstructorUpdate,
)
from app.utils.response import success

router = APIRouter()


# ---------- PUBLIC: view instructors ----------
@router.get("/instructors")
async def list_instructors(db: AsyncSession = Depends(get_db)):
    instructors = await crud_instructor.get_instructors(db)
    data = [InstructorOut.model_validate(i) for i in instructors]
    return success(data, message="Instructors fetched")


@router.get("/instructors/{instructor_id}")
async def get_instructor(instructor_id: int, db: AsyncSession = Depends(get_db)):
    instructor = await crud_instructor.get_instructor(db, instructor_id)
    if not instructor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instructor not found")
    return success(InstructorOut.model_validate(instructor), message="Instructor fetched")


# ---------- ADMIN ONLY: create / update / delete instructor ----------
@router.post("/instructors", status_code=status.HTTP_201_CREATED)
async def create_instructor(
    data: InstructorCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    instructor = await crud_instructor.create_instructor(db, data)
    return success(InstructorOut.model_validate(instructor), message="Instructor created")


@router.put("/instructors/{instructor_id}")
async def update_instructor(
    instructor_id: int,
    data: InstructorUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    instructor = await crud_instructor.get_instructor(db, instructor_id)
    if not instructor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instructor not found")
    instructor = await crud_instructor.update_instructor(db, instructor, data)
    return success(InstructorOut.model_validate(instructor), message="Instructor updated")


@router.delete("/instructors/{instructor_id}")
async def delete_instructor(
    instructor_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    instructor = await crud_instructor.get_instructor(db, instructor_id)
    if not instructor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instructor not found")
    await crud_instructor.soft_delete_instructor(db, instructor)
    return success(None, message="Instructor deleted")


# ---------- course <-> instructor linking ----------
@router.get("/courses/{course_id}/instructors")
async def list_course_instructors(course_id: int, db: AsyncSession = Depends(get_db)):
    course = await crud_course.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    instructors = await crud_instructor.get_instructors_for_course(db, course_id)
    data = [InstructorOut.model_validate(i) for i in instructors]
    return success(data, message="Course instructors fetched")


@router.post("/courses/{course_id}/instructors", status_code=status.HTTP_201_CREATED)
async def assign_instructor(
    course_id: int,
    data: AssignInstructor,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    course = await crud_course.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    instructor = await crud_instructor.get_instructor(db, data.instructor_id)
    if not instructor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instructor not found")
    existing = await crud_instructor.get_link(db, course_id, data.instructor_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Instructor already assigned to this course"
        )
    await crud_instructor.assign_instructor(db, course_id, data.instructor_id)
    return success(None, message="Instructor assigned to course")


@router.delete("/courses/{course_id}/instructors/{instructor_id}")
async def unassign_instructor(
    course_id: int,
    instructor_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    link = await crud_instructor.get_link(db, course_id, instructor_id)
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Instructor is not assigned to this course"
        )
    await crud_instructor.unassign_instructor(db, link)
    return success(None, message="Instructor removed from course")
