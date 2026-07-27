from datetime import date, datetime
from typing import Any

from pydantic import BaseModel

from app.models.course import CourseLevel, CourseMode, CourseStatus


# ---- what the client SENDS when creating a course ----
class CourseCreate(BaseModel):
    title: str
    category_id: int
    fee: float
    level: CourseLevel
    mode: CourseMode
    description: str | None = None
    thumbnail: str | None = None
    thumbnail_public_id: str | None = None
    thumbnail_resource_type: str | None = None
    duration: str | None = None
    language: str | None = None
    start_date: date | None = None
    certificate_name: str | None = None
    brochure: str | None = None
    brochure_public_id: str | None = None
    brochure_resource_type: str | None = None
    features: Any | None = None
    original_price: float | None = None
    badge: str | None = None
    course_status: CourseStatus = CourseStatus.Active


# ---- what the client SENDS when updating (all optional) ----
class CourseUpdate(BaseModel):
    title: str | None = None
    category_id: int | None = None
    fee: float | None = None
    level: CourseLevel | None = None
    mode: CourseMode | None = None
    description: str | None = None
    thumbnail: str | None = None
    thumbnail_public_id: str | None = None
    thumbnail_resource_type: str | None = None
    duration: str | None = None
    language: str | None = None
    start_date: date | None = None
    certificate_name: str | None = None
    brochure: str | None = None
    brochure_public_id: str | None = None
    brochure_resource_type: str | None = None
    features: Any | None = None
    original_price: float | None = None
    badge: str | None = None
    course_status: CourseStatus | None = None
    status: bool | None = None


# ---- what the API SENDS BACK ----
class CourseOut(BaseModel):
    course_id: int
    title: str
    category_id: int
    description: str | None
    thumbnail: str | None
    fee: float
    duration: str | None
    level: CourseLevel
    language: str | None
    mode: CourseMode
    start_date: date | None
    certificate_name: str | None
    students_count: int
    rating: float
    total_reviews: int
    original_price: float | None
    badge: str | None
    brochure: str | None
    features: Any | None
    course_status: CourseStatus
    status: bool
    created_at: datetime

    class Config:
        from_attributes = True
