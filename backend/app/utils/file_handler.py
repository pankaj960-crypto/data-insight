"""Secure file upload and dataset loading utilities."""

import json
import os
import re
import uuid
from pathlib import Path
from typing import Tuple

import pandas as pd
from fastapi import HTTPException, UploadFile, status

from app.config import get_settings

settings = get_settings()

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".json"}
ALLOWED_MIME = {
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/json",
    "text/plain",
}


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    name = re.sub(r"[^\w.\-]", "_", name)
    return name[:255] if name else "upload.dat"


def validate_upload(file: UploadFile, content: bytes) -> str:
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")

    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.max_upload_size_mb}MB",
        )

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    return ext


async def save_upload_file(file: UploadFile, user_id: int) -> Tuple[str, str, int]:
    content = await file.read()
    ext = validate_upload(file, content)

    user_dir = Path(settings.upload_dir) / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    safe_name = sanitize_filename(file.filename or "data")
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    file_path = user_dir / unique_name

    with open(file_path, "wb") as f:
        f.write(content)

    return str(file_path), ext.lstrip("."), len(content)


def load_dataframe(file_path: str, file_type: str) -> pd.DataFrame:
    path = Path(file_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset file not found")

    try:
        if file_type == "csv":
            df = pd.read_csv(file_path)
        elif file_type in ("xlsx", "excel"):
            df = pd.read_excel(file_path)
        elif file_type == "json":
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.json_normalize(data)
            else:
                raise ValueError("JSON must be array or object")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse file: {str(e)[:200]}",
        ) from e

    if df.empty:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dataset contains no rows")

    return df


def delete_file(file_path: str) -> None:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass
