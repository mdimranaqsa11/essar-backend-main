from datetime import datetime

from pydantic import BaseModel


# ---- client SENDS when creating an instructor ----
class InstructorCreate(BaseModel):
    name: str
    designation: str | None = None
    image: str | None = None
    bio: str | None = None


# ---- client SENDS when updating (all optional) ----
class InstructorUpdate(BaseModel):
    name: str | None = None
    designation: str | None = None
    image: str | None = None
    bio: str | None = None
    status: bool | None = None


# ---- API SENDS BACK ----
class InstructorOut(BaseModel):
    instructor_id: int
    name: str
    designation: str | None
    image: str | None
    bio: str | None
    status: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---- client SENDS when assigning an instructor to a course ----
class AssignInstructor(BaseModel):
    instructor_id: int
