from pathlib import Path

import pandas as pd
import pytest

from dataset_manager import DatasetError, DatasetInfo
from schemas import TrainRequest
from services import ml_service


def test_regression_training_and_prediction(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(ml_service, "ARTIFACT_PATH", tmp_path / "model.joblib")
    monkeypatch.setattr(ml_service, "METADATA_PATH", tmp_path / "model.json")
    rows = 60
    df = pd.DataFrame(
        {
            "carat": [0.2 + i / 100 for i in range(rows)],
            "cut": ["Ideal" if i % 2 else "Good" for i in range(rows)],
        }
    )
    df["price"] = df["carat"] * 5000 + [i % 5 for i in range(rows)]
    info = DatasetInfo("id", "diamonds.csv", "id.csv", "now")
    monkeypatch.setattr(ml_service.dataset_manager, "get_current_info", lambda: info)
    result = ml_service.train_model(df, info, TrainRequest(target_column="price", model_type="linear"))
    assert result["task_type"] == "regression"
    prediction = ml_service.predict({"carat": 0.5, "cut": "Ideal"})
    assert isinstance(prediction["prediction"], float)


def test_continuous_target_rejects_classification():
    rows = 60
    df = pd.DataFrame(
        {
            "feature": range(rows),
            "price": [100.25 + index * 2.5 for index in range(rows)],
        }
    )
    info = DatasetInfo("id", "continuous.csv", "id.csv", "now")

    with pytest.raises(DatasetError, match="choose Regression or Auto detect"):
        ml_service.train_model(
            df,
            info,
            TrainRequest(target_column="price", task_type="classification"),
        )
