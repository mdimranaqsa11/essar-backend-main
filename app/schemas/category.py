from datetime import datetime

from pydantic import BaseModel


# ---- what the client SENDS when creating a category ----
class CategoryCreate(BaseModel):
    category_name: str


# ---- what the client SENDS when updating (both fields optional) ----
class CategoryUpdate(BaseModel):
    category_name: str | None = None
    status: bool | None = None


# ---- what the API SENDS BACK ----
class CategoryOut(BaseModel):
    category_id: int
    category_name: str
    status: bool
    created_at: datetime

    class Config:
        from_attributes = True
