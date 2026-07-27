from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.crud import crud_category
from app.db.session import get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.utils.response import success

router = APIRouter()


# ---------- PUBLIC: anyone can view ----------
@router.get("")
async def list_categories(db: AsyncSession = Depends(get_db)):
    categories = await crud_category.get_categories(db, only_active=True)
    data = [CategoryOut.model_validate(c) for c in categories]
    return success(data, message="Categories fetched")


@router.get("/{category_id}")
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await crud_category.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return success(CategoryOut.model_validate(category), message="Category fetched")


# ---------- ADMIN ONLY: create / update / delete ----------
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    category = await crud_category.create_category(db, data)
    return success(CategoryOut.model_validate(category), message="Category created")


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    category = await crud_category.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    category = await crud_category.update_category(db, category, data)
    return success(CategoryOut.model_validate(category), message="Category updated")


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    category = await crud_category.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    await crud_category.soft_delete_category(db, category)
    return success(None, message="Category deleted")
