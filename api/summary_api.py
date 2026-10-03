from fastapi import APIRouter

from api.common import http_error
from dataset_manager import DatasetError, dataset_manager
from services.analysis import build_summary

router = APIRouter(tags=["Analysis"])


@router.get("/dataset-summary")
def dataset_summary():
    try:
        df, info = dataset_manager.load_current()
        return build_summary(df, info.original_name, info.dataset_id)
    except DatasetError as exc:
        raise http_error(exc) from exc


@router.get("/columns")
def dataset_columns():
    try:
        df, info = dataset_manager.load_current()
        return {
            "dataset": info.original_name,
            "columns": [str(c) for c in df.columns],
            "numeric_columns": [str(c) for c in df.select_dtypes(include="number").columns],
            "categorical_columns": [str(c) for c in df.select_dtypes(exclude="number").columns],
        }
    except DatasetError as exc:
        raise http_error(exc) from exc
