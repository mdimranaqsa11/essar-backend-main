from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.api.deps import get_current_admin
from app.crud import crud_course, crud_curriculum
from app.db.session import get_db
from app.models.user import User
from app.schemas.content import CurriculumCreate, CurriculumOut, CurriculumUpdate, MaterialOut
from app.services import cloudinary_service
from app.utils.response import success
from app.utils.upload import upload_document

router = APIRouter()

MAX_MATERIALS_PER_UPLOAD = 10


# ---------- PUBLIC: view a course's curriculum (materials included) ----------
@router.get("/courses/{course_id}/curriculum")
async def list_curriculum(course_id: int, db: AsyncSession = Depends(get_db)):
    course = await crud_course.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    items = await crud_curriculum.get_curriculum_by_course(db, course_id)
    data = [CurriculumOut.model_validate(i) for i in items]
    return success(data, message="Curriculum fetched")


# ---------- ADMIN ONLY: add a topic to a course ----------
@router.post("/courses/{course_id}/curriculum", status_code=status.HTTP_201_CREATED)
async def add_curriculum(
    course_id: int,
    data: CurriculumCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    course = await crud_course.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    item = await crud_curriculum.create_curriculum(db, course_id, data)
    return success(CurriculumOut.model_validate(item), message="Curriculum topic added")


# ---------- ADMIN ONLY: update / delete a single topic ----------
@router.put("/curriculum/{curriculum_id}")
async def update_curriculum(
    curriculum_id: int,
    data: CurriculumUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    item = await crud_curriculum.get_curriculum_item(db, curriculum_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curriculum topic not found")
    item = await crud_curriculum.update_curriculum(db, item, data)
    return success(CurriculumOut.model_validate(item), message="Curriculum topic updated")


@router.delete("/curriculum/{curriculum_id}")
async def delete_curriculum(
    curriculum_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    item = await crud_curriculum.get_curriculum_item(db, curriculum_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curriculum topic not found")

    # delete every attached material's real file from Cloudinary first (best-effort)
    if cloudinary_service.is_configured():
        for material in item.materials:
            if material.public_id:
                try:
                    await run_in_threadpool(
                        cloudinary_service.delete_file,
                        material.public_id,
                        material.resource_type or "raw",
                    )
                except Exception:
                    pass  # DB cleanup still proceeds even if a Cloudinary file was already gone

    # materials belong to this topic only — remove their DB rows too, not just the files
    await crud_curriculum.delete_all_materials_for_curriculum(db, curriculum_id)
    await crud_curriculum.soft_delete_curriculum(db, item)
    return success(None, message="Curriculum topic deleted")


# ---------- ADMIN ONLY: upload study materials (multiple files) for a topic ----------
@router.post("/curriculum/{curriculum_id}/materials", status_code=status.HTTP_201_CREATED)
async def upload_materials(
    curriculum_id: int,
    files: list[UploadFile] = File(..., description=f"Up to {MAX_MATERIALS_PER_UPLOAD} documents"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    item = await crud_curriculum.get_curriculum_item(db, curriculum_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curriculum topic not found")
    if len(files) > MAX_MATERIALS_PER_UPLOAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Max {MAX_MATERIALS_PER_UPLOAD} files per upload",
        )

    created = []
    for f in files:
        result = await upload_document(f, "essar/materials")
        material = await crud_curriculum.add_material(
            db,
            curriculum_id=curriculum_id,
            title=f.filename or "document",
            url=result["url"],
            public_id=result["public_id"],
            file_type=(f.filename.rsplit(".", 1)[-1].lower() if f.filename and "." in f.filename else None),
            resource_type=result.get("resource_type"),
        )
        created.append(MaterialOut.model_validate(material))

    return success(created, message=f"{len(created)} material(s) uploaded")


# ---------- ADMIN ONLY: remove one study material (DB row + Cloudinary file) ----------
@router.delete("/materials/{material_id}")
async def delete_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    material = await crud_curriculum.get_material(db, material_id)
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")

    if material.public_id and cloudinary_service.is_configured():
        try:
            await run_in_threadpool(
                cloudinary_service.delete_file,
                material.public_id,
                material.resource_type or "raw",
            )
        except Exception:
            pass  # DB row is still removed even if the Cloudinary file was already gone

    await crud_curriculum.delete_material(db, material)
    return success(None, message="Material deleted")
