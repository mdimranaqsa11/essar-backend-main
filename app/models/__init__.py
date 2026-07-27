# Import every model here so Alembic autogenerate can discover them via Base.metadata.
from app.models.category import CourseCategory  # noqa: F401
from app.models.content import CourseCurriculum, CurriculumMaterial  # noqa: F401
from app.models.course import Course  # noqa: F401
from app.models.enrollment import Enrollment  # noqa: F401
from app.models.instructor import CourseInstructor, Instructor  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401
from app.models.user import User  # noqa: F401
