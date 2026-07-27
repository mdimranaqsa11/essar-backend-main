from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from starlette.concurrency import run_in_threadpool

from app.api.deps import get_current_admin
from app.models.user import User
from app.services import cloudinary_service
from app.utils.response import success
from app.utils.upload import resource_type_for

router = APIRouter()

MAX_SIZE_MB = 10


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Query("essar/misc", description="Cloudinary folder, e.g. essar/thumbnails"),
    admin: User = Depends(get_current_admin),
):
    """Upload an image or PDF to Cloudinary and get back its URL.

    Use the returned `url` as the `thumbnail` or `brochure` value when
    creating/updating a course.
    """
    if not cloudinary_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cloudinary is not configured. Set CLOUDINARY_* in your .env",
        )

    contents = await file.read()
    if len(contents) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large (max {MAX_SIZE_MB} MB)",
        )

    result = await run_in_threadpool(
        cloudinary_service.upload_file, contents, folder, resource_type_for(file.filename), file.filename
    )
    return success(result, message="File uploaded")


@router.delete("")
async def delete_file(
    public_id: str = Query(..., description="The public_id returned when the file was uploaded"),
    resource_type: str = Query("image", description="image | raw (use raw for PDFs)"),
    admin: User = Depends(get_current_admin),
):
    if not cloudinary_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cloudinary is not configured. Set CLOUDINARY_* in your .env",
        )
    result = await run_in_threadpool(cloudinary_service.delete_file, public_id, resource_type)
    return success(result, message="File deleted")
