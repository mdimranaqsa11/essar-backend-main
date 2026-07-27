from fastapi import HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool

from app.services import cloudinary_service

MAX_SIZE_MB = 10

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "bmp", "svg", "heic", "heif"}


def resource_type_for(filename: str | None) -> str:
    """Decide the Cloudinary resource_type from a filename's extension.

    Never rely on Cloudinary's resource_type='auto' for non-image files (e.g. PDFs) —
    it can misclassify them as 'image', which sends them through the image-rendering
    pipeline and breaks delivery (ERR_INVALID_RESPONSE).
    """
    extension = filename.rsplit(".", 1)[-1].lower() if filename and "." in filename else ""
    return "image" if extension in IMAGE_EXTENSIONS else "raw"


async def upload_or_none(file: UploadFile | None, folder: str) -> str | None:
    """Upload an optional file to Cloudinary and return its URL (or None if no file).

    Shared by any endpoint that lets you send a file directly (courses, profile, ...).
    Raises 503 if Cloudinary isn't configured, 413 if the file is too large.
    """
    if file is None:
        return None
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
    return result["url"]


async def upload_document(file: UploadFile, folder: str) -> dict:
    """Upload a single study-material file and return the full Cloudinary result dict.

    Unlike `upload_or_none`, this always uploads (file is required). Images use
    resource_type='image' (so Cloudinary generates thumbnails/previews correctly);
    everything else (PDF/doc/etc.) uses 'raw'.
    Raises 503 if not configured, 413 if too large.
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
            detail=f"File too large (max {MAX_SIZE_MB} MB): {file.filename}",
        )
    return await run_in_threadpool(
        cloudinary_service.upload_file, contents, folder, resource_type_for(file.filename), file.filename
    )
