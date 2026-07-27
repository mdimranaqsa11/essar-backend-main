from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Instructor(Base, TimestampMixin):
    __tablename__ = "instructors"

    instructor_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    designation: Mapped[str | None] = mapped_column(String(150), nullable=True)
    image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)


class CourseInstructor(Base):
    """Join table linking courses <-> instructors (many-to-many)."""

    __tablename__ = "course_instructors"
    __table_args__ = (UniqueConstraint("course_id", "instructor_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False
    )
    instructor_id: Mapped[int] = mapped_column(
        ForeignKey("instructors.instructor_id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
