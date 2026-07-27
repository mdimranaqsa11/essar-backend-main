import enum

from sqlalchemy import (
    JSON,
    Date,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class CourseLevel(str, enum.Enum):
    Beginner = "Beginner"
    Intermediate = "Intermediate"
    Advanced = "Advanced"


class CourseMode(str, enum.Enum):
    Online = "Online"
    Offline = "Offline"
    Hybrid = "Hybrid"


class CourseStatus(str, enum.Enum):
    Active = "Active"
    Inactive = "Inactive"
    Upcoming = "Upcoming"


class Course(Base, TimestampMixin):
    __tablename__ = "courses"

    course_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("course_categories.category_id"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumbnail: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Cloudinary bookkeeping so a replaced thumbnail/brochure can delete the old file
    thumbnail_public_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    thumbnail_resource_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    duration: Mapped[str | None] = mapped_column(String(100), nullable=True)
    level: Mapped[CourseLevel] = mapped_column(Enum(CourseLevel), nullable=False)
    language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mode: Mapped[CourseMode] = mapped_column(Enum(CourseMode), nullable=False)
    start_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    certificate_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    students_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rating: Mapped[float] = mapped_column(Numeric(2, 1), default=0.0, nullable=False)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # `fee` is the selling price; `original_price` is the higher MRP (for showing a strikethrough + discount %)
    original_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    # a small highlight chip on the card, e.g. "Bestseller", "New", "Trending"
    badge: Mapped[str | None] = mapped_column(String(50), nullable=True)
    brochure: Mapped[str | None] = mapped_column(String(255), nullable=True)
    brochure_public_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    brochure_resource_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    features: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    course_status: Mapped[CourseStatus] = mapped_column(
        Enum(CourseStatus), default=CourseStatus.Active, nullable=False
    )
