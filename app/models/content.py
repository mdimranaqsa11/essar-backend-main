from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class CourseCurriculum(Base, TimestampMixin):
    __tablename__ = "course_curriculum"

    curriculum_id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False
    )
    topic_name: Mapped[str] = mapped_column(String(255), nullable=False)
    topic_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # deleting a curriculum topic auto-deletes its study materials too (DB-level cascade)
    materials: Mapped[list["CurriculumMaterial"]] = relationship(
        "CurriculumMaterial", cascade="all, delete-orphan", lazy="selectin"
    )


class CurriculumMaterial(Base):
    """One uploaded study-material document (PDF, doc, etc.) attached to a curriculum topic."""

    __tablename__ = "curriculum_materials"

    material_id: Mapped[int] = mapped_column(primary_key=True)
    curriculum_id: Mapped[int] = mapped_column(
        ForeignKey("course_curriculum.curriculum_id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    # Cloudinary's public_id, needed to delete the actual file later
    public_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Cloudinary's resource_type ("image" or "raw"), needed to delete the actual file later
    resource_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # pdf, docx, ...
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
