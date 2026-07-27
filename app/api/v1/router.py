from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    categories,
    contents,
    courses,
    enrollments,
    instructors,
    uploads,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
# contents + instructors define full paths (e.g. /courses/{id}/curriculum), so no prefix here
api_router.include_router(contents.router, tags=["curriculum"])
api_router.include_router(instructors.router, tags=["instructors"])
api_router.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
