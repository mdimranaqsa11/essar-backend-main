from datetime import datetime

from pydantic import BaseModel

from app.models.enrollment import EnrollmentStatus
from app.schemas.course import CourseOut
from app.schemas.user import UserOut


# ---- client SENDS when enrolling ----
class EnrollmentCreate(BaseModel):
    course_id: int


# ---- admin SENDS when changing an enrollment's status ----
class EnrollmentStatusUpdate(BaseModel):
    enrollment_status: EnrollmentStatus


# ---- basic response ----
class EnrollmentOut(BaseModel):
    enrollment_id: int
    user_id: int
    course_id: int
    enrollment_status: EnrollmentStatus
    enrolled_at: datetime
    status: bool

    class Config:
        from_attributes = True


# ---- response WITH the full course nested (for "my courses") ----
class EnrollmentWithCourse(EnrollmentOut):
    course: CourseOut | None = None


# ---- admin view: course + which user enrolled ----
class EnrollmentAdminOut(EnrollmentWithCourse):
    user: UserOut | None = None
