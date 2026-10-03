from fastapi import APIRouter

from api.common import http_error
from dataset_manager import DatasetError, dataset_manager
from schemas import VisualizationRequest
from services.visualization import create_chart

router = APIRouter(tags=["Visualization"])


@router.post("/visualize-data")
def visualize_data(request: VisualizationRequest):
    try:
        df, info = dataset_manager.load_current()
        filename = create_chart(df, info, request)
        return {"status": "success", "dataset": info.original_name, "chart_url": f"/charts/{filename}"}
    except DatasetError as exc:
        raise http_error(exc) from exc
    except (KeyError, TypeError, ValueError) as exc:
        raise http_error(DatasetError(f"Could not create this chart: {exc}")) from exc
