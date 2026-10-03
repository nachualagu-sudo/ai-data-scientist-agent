"""Application configuration kept in one place."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("APP_DATA_DIR", BASE_DIR / "data")).resolve()
UPLOAD_DIR = DATA_DIR / "uploads"
CHART_DIR = DATA_DIR / "charts"
MODEL_DIR = DATA_DIR / "models"
STATE_FILE = DATA_DIR / "current_dataset.json"

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "200"))
if not 1 <= MAX_UPLOAD_MB <= 250:
    raise RuntimeError("MAX_UPLOAD_MB must be between 1 and 250.")
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
MAX_EXCEL_EXPANDED_BYTES = 500 * 1024 * 1024
MAX_ANALYSIS_ROWS = int(os.getenv("MAX_ANALYSIS_ROWS", "50000"))
MAX_COLUMNS = int(os.getenv("MAX_COLUMNS", "100"))
if not 100 <= MAX_ANALYSIS_ROWS <= 200_000 or not 2 <= MAX_COLUMNS <= 200:
    raise RuntimeError("MAX_ANALYSIS_ROWS or MAX_COLUMNS is outside the supported range.")
ALLOWED_EXTENSIONS = {".csv", ".xlsx"}
MAX_PREVIEW_ROWS = 20
MAX_CHART_ROWS = 10_000
MAX_TRAIN_ROWS = int(os.getenv("MAX_TRAIN_ROWS", "50_000"))
if not 100 <= MAX_TRAIN_ROWS <= MAX_ANALYSIS_ROWS:
    raise RuntimeError("MAX_TRAIN_ROWS must be between 100 and MAX_ANALYSIS_ROWS.")
APP_USERNAME = os.getenv("APP_USERNAME", "").strip()
APP_PASSWORD = os.getenv("APP_PASSWORD", "")
APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
if APP_ENV not in {"development", "production"}:
    raise RuntimeError("APP_ENV must be development or production.")
if bool(APP_USERNAME) != bool(APP_PASSWORD):
    raise RuntimeError("Set both APP_USERNAME and APP_PASSWORD, or leave both empty for local development.")
if APP_PASSWORD and len(APP_PASSWORD) < 12:
    raise RuntimeError("APP_PASSWORD must contain at least 12 characters.")
if APP_ENV == "production" and not (APP_USERNAME and APP_PASSWORD):
    raise RuntimeError("Production requires APP_USERNAME and APP_PASSWORD.")

for directory in (DATA_DIR, UPLOAD_DIR, CHART_DIR, MODEL_DIR):
    directory.mkdir(parents=True, exist_ok=True)
