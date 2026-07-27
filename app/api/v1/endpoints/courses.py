import json
from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.api.deps import get_current_admin
from app.crud import crud_course
from app.db.session import get_db
from app.models.course import CourseLevel, CourseMode, CourseStatus
from app.models.user import User
from app.schemas.course import CourseCreate, CourseOut, CourseUpdate
from app.services import cloudinary_service
from app.utils.response import success
from app.utils.upload import upload_document

router = APIRouter()


# ---------- helpers ----------
def _parse_features(features: str | None):
    """Accept features as a JSON array string OR a comma-separated string."""
    if features is None or features.strip() == "":
        return None
    try:
        return json.loads(features)
    except json.JSONDecodeError:
        return [f.strip() for f in features.split(",") if f.strip()]


async def _replace_asset(
    file: UploadFile | None,
    folder: str,
    old_public_id: str | None,
    old_resource_type: str | None,
) -> dict | None:
    """Upload a replacement file and delete the asset it replaces (best-effort).

    Returns the new Cloudinary result dict, or None if no file was sent (caller
    then leaves the existing thumbnail/brochure untouched).
    """
    if file is None:
        return None
    result = await upload_document(file, folder)
    if old_public_id and cloudinary_service.is_configured():
        try:
            await run_in_threadpool(
                cloudinary_service.delete_file, old_public_id, old_resource_type or "image"
            )
        except Exception:
            pass  # old asset may already be gone — new upload still succeeds
    return result


# ---------- PUBLIC: anyone can view / filter ----------
@router.get("")
async def list_courses(
    category_id: int | None = None,
    level: CourseLevel | None = None,
    mode: CourseMode | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    courses = await crud_course.get_courses(
        db, category_id=category_id, level=level, mode=mode, search=search
    )
    data = [CourseOut.model_validate(c) for c in courses]
    return success(data, message="Courses fetched")


@router.get("/{course_id}")
async def get_course(course_id: int, db: AsyncSession = Depends(get_db)):
    course = await crud_course.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return success(CourseOut.model_validate(course), message="Course fetched")


# ---------- ADMIN ONLY: create (multipart: fields + optional files) ----------
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_course(
    title: str = Form(...),
    category_id: int = Form(...),
    fee: float = Form(...),
    level: CourseLevel = Form(...),
    mode: CourseMode = Form(...),
    description: str | None = Form(None),
    duration: str | None = Form(None),
    language: str | None = Form(None),
    start_date: date | None = Form(None),
    certificate_name: str | None = Form(None),
    original_price: float | None = Form(None),
    badge: str | None = Form(None),
    course_status: CourseStatus = Form(CourseStatus.Active),
    features: str | None = Form(None, description='JSON array or comma-separated, e.g. ["Live","Certificate"]'),
    thumbnail: str | None = Form(None, description="Optional image URL (used if no thumbnail_file)"),
    brochure: str | None = Form(None, description="Optional PDF URL (used if no brochure_file)"),
    thumbnail_file: UploadFile | None = File(None),
    brochure_file: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    if not await crud_course.category_exists(db, category_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category does not exist")

    # a file (if sent) wins over a plain URL
    thumbnail_result = await upload_document(thumbnail_file, "essar/thumbnails") if thumbnail_file else None
    brochure_result = await upload_document(brochure_file, "essar/brochures") if brochure_file else None
    thumbnail = (thumbnail_result or {}).get("url") or thumbnail
    brochure = (brochure_result or {}).get("url") or brochure

    data = CourseCreate(
        title=title, category_id=category_id, fee=fee, level=level, mode=mode,
        description=description, duration=duration, language=language, start_date=start_date,
        certificate_name=certificate_name, original_price=original_price, badge=badge,
        course_status=course_status, features=_parse_features(features),
        thumbnail=thumbnail, brochure=brochure,
        thumbnail_public_id=(thumbnail_result or {}).get("public_id"),
        thumbnail_resource_type=(thumbnail_result or {}).get("resource_type"),
        brochure_public_id=(brochure_result or {}).get("public_id"),
        brochure_resource_type=(brochure_result or {}).get("resource_type"),
    )
    course = await crud_course.create_course(db, data)
    return success(CourseOut.model_validate(course), message="Course created")


# ---------- ADMIN ONLY: update (multipart: any field + optional files) ----------
@router.put("/{course_id}")
async def update_course(
    course_id: int,
    title: str | None = Form(None),
    category_id: int | None = Form(None),
    fee: float | None = Form(None),
    level: CourseLevel | None = Form(None),
    mode: CourseMode | None = Form(None),
    description: str | None = Form(None),
    duration: str | None = Form(None),
    language: str | None = Form(None),
    start_date: date | None = Form(None),
    certificate_name: str | None = Form(None),
    original_price: float | None = Form(None),
    badge: str | None = Form(None),
    course_status: CourseStatus | None = Form(None),
    status_active: bool | None = Form(None, alias="status"),
    features: str | None = Form(None),
    thumbnail: str | None = Form(None),
    brochure: str | None = Form(None),
    thumbnail_file: UploadFile | None = File(None),
    brochure_file: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    course = await crud_course.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if category_id is not None and not await crud_course.category_exists(db, category_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category does not exist")

    # a new file replaces the old one — delete the old Cloudinary asset once the new upload succeeds
    thumbnail_result = await _replace_asset(
        thumbnail_file, "essar/thumbnails", course.thumbnail_public_id, course.thumbnail_resource_type
    )
    brochure_result = await _replace_asset(
        brochure_file, "essar/brochures", course.brochure_public_id, course.brochure_resource_type
    )
    thumbnail = (thumbnail_result or {}).get("url") or thumbnail
    brochure = (brochure_result or {}).get("url") or brochure

    # only include fields the client actually sent (non-None)
    fields = {
        "title": title, "category_id": category_id, "fee": fee, "level": level, "mode": mode,
        "description": description, "duration": duration, "language": language,
        "start_date": start_date, "certificate_name": certificate_name,
        "original_price": original_price, "badge": badge, "course_status": course_status,
        "status": status_active, "thumbnail": thumbnail, "brochure": brochure,
    }
    # ignore fields not sent (None) and empty text fields (so a blank form field never wipes data)
    provided = {k: v for k, v in fields.items() if v is not None and v != ""}
    if features:
        provided["features"] = _parse_features(features)
    if thumbnail_result:
        provided["thumbnail_public_id"] = thumbnail_result.get("public_id")
        provided["thumbnail_resource_type"] = thumbnail_result.get("resource_type")
    if brochure_result:
        provided["brochure_public_id"] = brochure_result.get("public_id")
        provided["brochure_resource_type"] = brochure_result.get("resource_type")

    data = CourseUpdate(**provided)
    course = await crud_course.update_course(db, course, data)
    return success(CourseOut.model_validate(course), message="Course updated")


@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    course = await crud_course.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    await crud_course.soft_delete_course(db, course)
    return success(None, message="Course deleted")
