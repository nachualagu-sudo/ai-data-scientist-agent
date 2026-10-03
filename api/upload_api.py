from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from api.common import http_error
from config import ALLOWED_EXTENSIONS, MAX_UPLOAD_BYTES, MAX_UPLOAD_MB, UPLOAD_DIR
from dataset_manager import DatasetError, dataset_manager
from services.analysis import build_summary

router = APIRouter(tags=["Dataset"])


@router.post("/upload-data")
async def upload_dataset(file: Annotated[UploadFile, File()]):
    original_name = dataset_manager.safe_display_name(file.filename or "")
    if Path(original_name).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Only CSV and XLSX files are supported.")
    try:
        info = dataset_manager.create_info(original_name)
    except DatasetError as exc:
        raise http_error(exc) from exc
    target = UPLOAD_DIR / info.stored_name
    size = 0
    try:
        with target.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail=f"File is larger than {MAX_UPLOAD_MB} MB.")
                output.write(chunk)
        if size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        df = dataset_manager.read_path(target)
        if df.empty or len(df.columns) == 0:
            raise HTTPException(status_code=400, detail="Dataset has no rows or columns.")
        dataset_manager.set_current(info)
        return {"status": "success", **build_summary(df, info.original_name, info.dataset_id)}
    except HTTPException:
        target.unlink(missing_ok=True)
        raise
    except DatasetError as exc:
        target.unlink(missing_ok=True)
        raise http_error(exc) from exc
    finally:
        await file.close()
