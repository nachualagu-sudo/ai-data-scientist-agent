from fastapi import APIRouter

from api.common import http_error
from dataset_manager import DatasetError, dataset_manager
from services.analysis import build_insights

router = APIRouter(tags=["Insights"])


@router.get("/dataset-insights")
def dataset_insights():
    try:
        df, info = dataset_manager.load_current()
        return {"dataset": info.original_name, "insights": build_insights(df)}
    except DatasetError as exc:
        raise http_error(exc) from exc
