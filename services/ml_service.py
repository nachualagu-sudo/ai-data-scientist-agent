from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from config import MAX_TRAIN_ROWS, MODEL_DIR
from dataset_manager import DatasetError, DatasetInfo, dataset_manager
from schemas import TrainRequest

ARTIFACT_PATH = MODEL_DIR / "current_model.joblib"
METADATA_PATH = MODEL_DIR / "current_model.json"


def _infer_task(y: pd.Series) -> str:
    unique = y.nunique(dropna=True)
    if not pd.api.types.is_numeric_dtype(y) or unique <= min(20, max(2, int(len(y) * 0.05))):
        return "classification"
    return "regression"


def _prepare_features(df: pd.DataFrame, target: str) -> tuple[pd.DataFrame, list[str]]:
    X = df.drop(columns=[target]).copy()
    excluded: list[str] = []
    for column in list(X.columns):
        unique = X[column].nunique(dropna=True)
        if unique == 0 or (not pd.api.types.is_numeric_dtype(X[column]) and unique > min(200, len(X) * 0.5)):
            excluded.append(str(column))
            X = X.drop(columns=[column])
    if X.empty:
        raise DatasetError("No usable feature columns remain after validation.")
    return X, excluded


def train_model(df: pd.DataFrame, info: DatasetInfo, request: TrainRequest) -> dict[str, Any]:
    target = request.target_column
    if target not in df.columns:
        raise DatasetError("Selected target column does not exist.")
    # Duplicate examples must not appear in both train and test sets.
    # When the user cleaned the dataset, the manager supplies the raw source
    # so imputers are fitted exclusively on the training fold.
    working = df.drop_duplicates().dropna(subset=[target]).copy()
    if len(working) < 20:
        raise DatasetError("At least 20 rows with a target value are required for training.")
    if working[target].nunique(dropna=True) < 2:
        raise DatasetError("Target column must contain at least two different values.")
    if len(working) > MAX_TRAIN_ROWS:
        working = working.sample(MAX_TRAIN_ROWS, random_state=42)

    y = working[target]
    inferred_task = _infer_task(y)
    task = inferred_task if request.task_type == "auto" else request.task_type
    if task == "regression" and not pd.api.types.is_numeric_dtype(y):
        raise DatasetError("Regression requires a numeric target column.")
    if task == "classification" and inferred_task == "regression":
        raise DatasetError(
            "Classification requires a target with discrete classes. "
            "The selected target contains continuous numeric values; choose Regression or Auto detect."
        )
    if task == "classification" and y.nunique() > 50:
        raise DatasetError("Classification supports at most 50 target classes. Choose a suitable target.")
    X, excluded = _prepare_features(working, target)
    numeric = list(X.select_dtypes(include="number").columns)
    categorical = [column for column in X.columns if column not in numeric]

    transformers = []
    if numeric:
        transformers.append(
            (
                "numeric",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric,
            )
        )
    if categorical:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore", min_frequency=2)),
                    ]
                ),
                categorical,
            )
        )
    preprocessor = ColumnTransformer(transformers, remainder="drop")

    requested_model = request.model_type
    if requested_model == "auto":
        requested_model = "random_forest"
    if task == "regression":
        if requested_model not in {"linear", "random_forest"}:
            raise DatasetError("Choose Linear or Random Forest for regression.")
        estimator = (
            LinearRegression()
            if requested_model == "linear"
            else RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=1, max_depth=18)
        )
    else:
        if requested_model == "linear":
            requested_model = "logistic"
        if requested_model not in {"logistic", "random_forest"}:
            raise DatasetError("Choose Logistic or Random Forest for classification.")
        if requested_model == "logistic":
            estimator = LogisticRegression(max_iter=1_000, class_weight="balanced")
        else:
            estimator = RandomForestClassifier(
                n_estimators=100, random_state=42, n_jobs=1, class_weight="balanced", max_depth=18
            )

    stratify = None
    if task == "classification" and y.value_counts().min() >= 2:
        stratify = y
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=request.test_size, random_state=42, stratify=stratify
        )
        pipeline = Pipeline([("preprocessor", preprocessor), ("model", estimator)])
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)
    except (TypeError, ValueError) as exc:
        raise DatasetError(f"Model training failed: {exc}") from exc

    if task == "regression":
        metrics = {
            "mae": round(float(mean_absolute_error(y_test, predictions)), 4),
            "rmse": round(float(mean_squared_error(y_test, predictions) ** 0.5), 4),
            "r2": round(float(r2_score(y_test, predictions)), 4),
        }
    else:
        metrics = {
            "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
            "f1_weighted": round(float(f1_score(y_test, predictions, average="weighted", zero_division=0)), 4),
        }

    examples: dict[str, Any] = {}
    for column in X.columns:
        series = X[column].dropna()
        if series.empty:
            examples[str(column)] = None
        elif column in numeric:
            examples[str(column)] = float(series.median())
        else:
            examples[str(column)] = str(series.mode().iloc[0])
    metadata = {
        "dataset_id": info.dataset_id,
        "dataset": info.original_name,
        "target": target,
        "task_type": task,
        "model_type": requested_model,
        "feature_columns": [str(c) for c in X.columns],
        "numeric_features": [str(c) for c in numeric],
        "categorical_features": [str(c) for c in categorical],
        "excluded_columns": excluded,
        "example_values": examples,
        "metrics": metrics,
        "training_rows": len(X_train),
        "testing_rows": len(X_test),
        "trained_at": datetime.now(UTC).isoformat(),
    }
    temp_artifact = ARTIFACT_PATH.with_suffix(".tmp")
    joblib.dump({"pipeline": pipeline, "metadata": metadata}, temp_artifact)
    temp_artifact.replace(ARTIFACT_PATH)
    temp_metadata = METADATA_PATH.with_suffix(".tmp")
    temp_metadata.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    temp_metadata.replace(METADATA_PATH)
    return metadata


def get_model_metadata() -> dict[str, Any]:
    if not METADATA_PATH.is_file() or not ARTIFACT_PATH.is_file():
        raise DatasetError("No trained model is available. Train a model first.")
    try:
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DatasetError("Saved model metadata is invalid. Train the model again.") from exc
    if metadata.get("dataset_id") != dataset_manager.get_current_info().dataset_id:
        raise DatasetError("The dataset changed since training. Train a new model before predicting.")
    return metadata


def predict(features: dict[str, Any]) -> dict[str, Any]:
    metadata = get_model_metadata()
    missing = [column for column in metadata["feature_columns"] if column not in features]
    if missing:
        raise DatasetError(f"Missing prediction fields: {', '.join(missing)}")
    row = {column: features[column] for column in metadata["feature_columns"]}
    for column in metadata["numeric_features"]:
        try:
            row[column] = float(row[column])
        except (TypeError, ValueError) as exc:
            raise DatasetError(f"{column} must be a number.") from exc
    artifact = joblib.load(ARTIFACT_PATH)
    pipeline = artifact["pipeline"]
    result = pipeline.predict(pd.DataFrame([row]))[0]
    if isinstance(result, np.generic):
        result = result.item()
    response: dict[str, Any] = {"prediction": result, "target": metadata["target"], "task_type": metadata["task_type"]}
    if metadata["task_type"] == "classification" and hasattr(pipeline, "predict_proba"):
        probabilities = pipeline.predict_proba(pd.DataFrame([row]))[0]
        classes = pipeline.classes_
        response["probabilities"] = {
            str(label): round(float(prob), 5) for label, prob in zip(classes, probabilities, strict=True)
        }
    return response
