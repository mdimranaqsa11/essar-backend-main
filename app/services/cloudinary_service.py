import cloudinary
import cloudinary.uploader
import cloudinary.utils

from app.core.config import settings


def is_configured() -> bool:
    """True only when all three Cloudinary creds are present in .env."""
    return all(
        [
            settings.CLOUDINARY_CLOUD_NAME,
            settings.CLOUDINARY_API_KEY,
            settings.CLOUDINARY_API_SECRET,
        ]
    )


def _configure() -> None:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


def upload_file(
    file_bytes: bytes,
    folder: str = "essar/misc",
    resource_type: str = "auto",
    filename: str | None = None,
) -> dict:
    """Upload raw bytes to Cloudinary. `resource_type='auto'` handles images AND PDFs.

    For `raw` resources, Cloudinary won't set the correct Content-Type/extension on
    delivery unless the public_id itself ends in that extension — passing the
    original `filename` with `use_filename=True` preserves it (e.g. "notes.pdf"
    instead of a random id with no extension), so files open inline instead of
    downloading as an untyped attachment.

    This account has strict/authenticated delivery enabled for raw resources, so
    unsigned raw URLs 401 even with "Allow delivery of PDF and ZIP files" turned on.
    `sign_url` on the *upload* call doesn't affect the returned secure_url at all —
    the signed delivery URL has to be built separately via cloudinary_url(), which
    is what makes the file actually openable.

    NOTE: this is a BLOCKING network call — the endpoint runs it in a threadpool.
    """
    _configure()
    kwargs = {}
    if filename:
        kwargs.update(use_filename=True, unique_filename=True, filename=filename)
    result = cloudinary.uploader.upload(file_bytes, folder=folder, resource_type=resource_type, **kwargs)

    url = result["secure_url"]
    if resource_type == "raw":
        url, _ = cloudinary.utils.cloudinary_url(
            result["public_id"],
            resource_type="raw",
            type="upload",
            version=result["version"],
            sign_url=True,
            secure=True,
        )

    return {
        "url": url,
        "public_id": result["public_id"],
        "resource_type": result.get("resource_type"),
        "format": result.get("format"),
        "bytes": result.get("bytes"),
        "filename": filename,
    }


def delete_file(public_id: str, resource_type: str = "image") -> dict:
    _configure()
    return cloudinary.uploader.destroy(public_id, resource_type=resource_type)
