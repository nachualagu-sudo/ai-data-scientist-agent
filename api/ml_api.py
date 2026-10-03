from fastapi import APIRouter

from api.common import http_error
from dataset_manager import DatasetError, dataset_manager
from schemas import PredictRequest, SalesFeatures, TrainRequest
from services.ml_service import get_model_metadata, predict, train_model

router = APIRouter(tags=["Machine Learning"])


@router.post("/train-model")
def train(request: TrainRequest):
    try:
        df, info = dataset_manager.load_for_training()
        return {"status": "success", **train_model(df, info, request)}
    except DatasetError as exc:
        raise http_error(exc) from exc


@router.get("/model-info")
def model_info():
    try:
        return get_model_metadata()
    except DatasetError as exc:
        raise http_error(exc) from exc


@router.post("/predict")
def make_prediction(request: PredictRequest):
    try:
        return {"status": "success", **predict(request.features)}
    except DatasetError as exc:
        raise http_error(exc) from exc


@router.post("/predict-sales")
def predict_sales(features: SalesFeatures):
    """Backward-compatible educational sales estimate with strict inputs."""
    net_price = features.price * (1 - features.discount / 100)
    estimate = net_price * features.quantity
    return {
        "status": "success",
        "prediction": round(estimate, 2),
        "note": "Formula-based legacy demo. Use /train-model and /predict for dataset-trained ML.",
    }
