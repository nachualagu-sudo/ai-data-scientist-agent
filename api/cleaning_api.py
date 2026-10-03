from fastapi import APIRouter
from fastapi.responses import FileResponse

from api.common import http_error
from config import UPLOAD_DIR
from dataset_manager import DatasetError, dataset_manager
from services.cleaning import clean_dataframe

router = APIRouter(tags=["Cleaning"])


@router.post("/clean-data")
def clean_data():
    try:
        df, current = dataset_manager.load_current()
        cleaned, report = clean_dataframe(df)
        name = current.original_name
        if not name.lower().startswith("cleaned_"):
            name = f"Cleaned_{name}"
        source_name = current.source_stored_name or current.stored_name
        info = dataset_manager.create_info(
            name, is_cleaned=True, source_stored_name=source_name,
            sampled_source=bool(df.attrs.get("sampled", False)),
        )
        target = UPLOAD_DIR / info.stored_name
        dataset_manager.save_dataframe(cleaned, target)
        dataset_manager.set_current(info)
        return {
            "status": "Dataset cleaned successfully",
            "original_dataset": current.original_name,
            "cleaned_dataset": info.original_name,
            "cleaned_dataset_id": info.dataset_id,
            "current_dataset_updated": True,
            "sampled": bool(df.attrs.get("sampled", False)),
            **report,
        }
    except DatasetError as exc:
        raise http_error(exc) from exc


@router.get("/download-current-dataset")
def download_current_dataset():
    try:
        info = dataset_manager.get_current_info()
        return FileResponse(
            dataset_manager.get_current_path(),
            filename=info.original_name,
            media_type="application/octet-stream",
        )
    except DatasetError as exc:
        raise http_error(exc) from exc
