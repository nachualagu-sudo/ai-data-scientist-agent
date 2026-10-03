import base64
from io import BytesIO

from fastapi.testclient import TestClient

import dataset_manager as manager_module
import FastAPI_Main_Server as server
from api import cleaning_api, upload_api
from services import ml_service


def test_large_dataset_is_labelled_and_cleaning_keeps_raw_source(tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    monkeypatch.setattr(manager_module, "UPLOAD_DIR", uploads)
    monkeypatch.setattr(manager_module, "STATE_FILE", tmp_path / "current.json")
    monkeypatch.setattr(upload_api, "UPLOAD_DIR", uploads)
    monkeypatch.setattr(cleaning_api, "UPLOAD_DIR", uploads)
    monkeypatch.setattr(manager_module, "MAX_ANALYSIS_ROWS", 100)
    monkeypatch.setattr(ml_service, "ARTIFACT_PATH", tmp_path / "model.joblib")
    monkeypatch.setattr(ml_service, "METADATA_PATH", tmp_path / "model.json")
    rows = "Feature Value,target\n" + "".join(f"{i},{i * 2}\n" for i in range(130))
    with TestClient(server.app) as client:
        response = client.post("/upload-data", files={"file": ("large.csv", BytesIO(rows.encode()), "text/csv")})
        assert response.status_code == 200
        assert response.json()["rows"] == 100
        assert response.json()["sampled"] is True
        raw_name = manager_module.dataset_manager.get_current_info().stored_name
        cleaned = client.post("/clean-data")
        assert cleaned.status_code == 200
        assert cleaned.json()["sampled"] is True
        assert (uploads / raw_name).exists()
        assert client.get("/dataset-summary").json()["analysis_row_limit"] == 100
        raw_for_training, _ = manager_module.dataset_manager.load_for_training()
        assert raw_for_training["Feature_Value"].iloc[-1] == 99
        assert manager_module.dataset_manager.get_current_info().source_stored_name == raw_name
        trained = client.post("/train-model", json={"target_column": "target", "model_type": "linear"})
        assert trained.status_code == 200
        assert trained.json()["feature_columns"] == ["Feature_Value"]
        again = client.post("/upload-data", files={"file": ("new.csv", BytesIO(rows.encode()), "text/csv")})
        assert again.status_code == 200
        assert not (uploads / raw_name).exists()
        assert client.get("/model-info").status_code == 400


def test_production_rejects_unauthorized_and_cross_origin_requests(monkeypatch):
    monkeypatch.setattr(server, "APP_ENV", "production")
    monkeypatch.setattr(server, "APP_USERNAME", "teacher")
    monkeypatch.setattr(server, "APP_PASSWORD", "an-example-secret")
    credentials = base64.b64encode(b"teacher:an-example-secret").decode("ascii")
    with TestClient(server.app) as client:
        unauthenticated = client.get("/")
        assert unauthenticated.status_code == 401
        assert unauthenticated.headers["cache-control"] == "no-store"
        cross_origin = client.post(
            "/clean-data", headers={"Authorization": f"Basic {credentials}", "Origin": "https://evil.example"}
        )
        assert cross_origin.status_code == 403
        allowed = client.post(
            "/clean-data", headers={"Authorization": f"Basic {credentials}", "Origin": "http://testserver"}
        )
        assert allowed.status_code == 400  # Authentication and origin checks passed; no dataset was uploaded.


def test_upload_above_old_25mb_limit(tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    monkeypatch.setattr(manager_module, "UPLOAD_DIR", uploads)
    monkeypatch.setattr(manager_module, "STATE_FILE", tmp_path / "current.json")
    monkeypatch.setattr(upload_api, "UPLOAD_DIR", uploads)
    # Valid CSV followed by empty lines. The transport still sends more than 25 MiB.
    content = b"value,target\n1,2\n3,4\n" + (b"\n" * (26 * 1024 * 1024))
    with TestClient(server.app) as client:
        response = client.post("/upload-data", files={"file": ("above25.csv", BytesIO(content), "text/csv")})
        assert response.status_code == 200
        assert response.json()["rows"] == 2
