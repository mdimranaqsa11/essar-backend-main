from datetime import datetime

from pydantic import BaseModel


# ---- client SENDS when adding a topic to a course ----
class CurriculumCreate(BaseModel):
    topic_name: str
    topic_order: int


# ---- client SENDS when updating (all optional) ----
class CurriculumUpdate(BaseModel):
    topic_name: str | None = None
    topic_order: int | None = None
    status: bool | None = None


# ---- one study-material document ----
class MaterialOut(BaseModel):
    material_id: int
    curriculum_id: int
    title: str
    url: str
    file_type: str | None
    resource_type: str | None
    created_at: datetime

    class Config:
        from_attributes = True


# ---- API SENDS BACK ----
class CurriculumOut(BaseModel):
    curriculum_id: int
    course_id: int
    topic_name: str
    topic_order: int
    status: bool
    created_at: datetime
    materials: list[MaterialOut] = []

    class Config:
        from_attributes = True
