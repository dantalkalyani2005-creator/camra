from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.auth import get_current_user
from app.services.deidentification.sanitizer import sanitize_text
from app.services.ocr.tesseract import extract_text_from_image
from app.services.ocr.pdf import extract_text_from_pdf


router = APIRouter(prefix="/upload", tags=["Report Upload"])

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def _extension(filename: str) -> str:
    filename = filename.lower()

    for extension in ALLOWED_EXTENSIONS:
        if filename.endswith(extension):
            return extension

    return ""


@router.post("")
async def upload_report(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided",
        )

    extension = _extension(file.filename)

    if not extension:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Allowed: PDF, JPG, JPEG, PNG, WEBP",
        )

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 10 MB",
        )

    # --------------------------------------------------------
    # 1. Extract the complete document as one string
    # --------------------------------------------------------

    try:
        if extension == ".pdf":
            raw_text = extract_text_from_pdf(file_content)
        else:
            raw_text = extract_text_from_image(file_content)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document extraction failed: {exc}",
        )

    if not raw_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No readable text could be extracted from the report",
        )

    # --------------------------------------------------------
    # 2. Sanitize the complete extracted string
    # --------------------------------------------------------

    try:
        report_text = sanitize_text(raw_text)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"De-identification failed: {exc}",
        )

    if not report_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No usable text remained after de-identification",
        )

    # --------------------------------------------------------
    # 3. Return the complete sanitized report as one string
    # --------------------------------------------------------

    return {
        "message": "Report processed successfully",
        "report": {
            "report_name": file.filename,
            "patient_data": {},
            "report_data": {
                "report_text": report_text,
            },
        },
    }