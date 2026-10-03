"""Safe, centralized dataset state and file loading."""

from __future__ import annotations

import json
import re
import zipfile
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from uuid import uuid4

import pandas as pd

from config import (
    ALLOWED_EXTENSIONS,
    MAX_ANALYSIS_ROWS,
    MAX_COLUMNS,
    MAX_EXCEL_EXPANDED_BYTES,
    STATE_FILE,
    UPLOAD_DIR,
)


class DatasetError(Exception):
    """A user-facing dataset error."""


@dataclass(frozen=True)
class DatasetInfo:
    dataset_id: str
    original_name: str
    stored_name: str
    uploaded_at: str
    is_cleaned: bool = False
    source_stored_name: str | None = None
    sampled_source: bool = False


class DatasetManager:
    def __init__(self) -> None:
        self._lock = RLock()

    @staticmethod
    def safe_display_name(name: str) -> str:
        base = Path(name or "dataset").name
        safe = re.sub(r"[^A-Za-z0-9._ -]", "_", base).strip(" .")
        return safe[:120] or "dataset.csv"

    def create_info(
        self, original_name: str, *, is_cleaned: bool = False,
        source_stored_name: str | None = None, sampled_source: bool = False
    ) -> DatasetInfo:
        display_name = self.safe_display_name(original_name)
        extension = Path(display_name).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise DatasetError("Only CSV and XLSX files are supported.")
        dataset_id = uuid4().hex
        return DatasetInfo(
            dataset_id=dataset_id,
            original_name=display_name,
            stored_name=f"{dataset_id}{extension}",
            uploaded_at=datetime.now(UTC).isoformat(),
            is_cleaned=is_cleaned,
            source_stored_name=source_stored_name,
            sampled_source=sampled_source,
        )

    def set_current(self, info: DatasetInfo) -> None:
        target = UPLOAD_DIR / info.stored_name
        if not target.is_file():
            raise DatasetError("Dataset file was not found.")
        temp = STATE_FILE.with_suffix(".tmp")
        with self._lock:
            temp.write_text(json.dumps(asdict(info), indent=2), encoding="utf-8")
            temp.replace(STATE_FILE)
            keep = {info.stored_name, info.source_stored_name}
            for old in UPLOAD_DIR.iterdir():
                if old.is_file() and old.name not in keep:
                    old.unlink(missing_ok=True)

    def get_current_info(self) -> DatasetInfo:
        with self._lock:
            if not STATE_FILE.is_file():
                raise DatasetError("No dataset is selected. Upload a CSV or XLSX file first.")
            try:
                payload = json.loads(STATE_FILE.read_text(encoding="utf-8"))
                info = DatasetInfo(**payload)
            except (OSError, json.JSONDecodeError, TypeError) as exc:
                raise DatasetError("Dataset state is invalid. Upload the dataset again.") from exc
        if Path(info.stored_name).name != info.stored_name or (
            info.source_stored_name and Path(info.source_stored_name).name != info.source_stored_name
        ):
            raise DatasetError("Dataset state contains an invalid file path.")
        if not (UPLOAD_DIR / info.stored_name).is_file():
            raise DatasetError("The selected dataset file is missing. Upload it again.")
        return info

    def get_current_path(self) -> Path:
        return UPLOAD_DIR / self.get_current_info().stored_name

    @staticmethod
    def read_path(path: Path) -> pd.DataFrame:
        suffix = path.suffix.lower()
        try:
            if suffix == ".csv":
                header = pd.read_csv(path, nrows=0)
                if len(header.columns) > MAX_COLUMNS:
                    raise DatasetError(f"Dataset has more than {MAX_COLUMNS} columns; reduce columns and retry.")
                df = pd.read_csv(path, nrows=MAX_ANALYSIS_ROWS + 1, low_memory=False)
                truncated = len(df) > MAX_ANALYSIS_ROWS
                df = df.iloc[:MAX_ANALYSIS_ROWS].copy()
                df.columns = [str(column) for column in df.columns]
                df.attrs["sampled"] = truncated
                return df
            if suffix == ".xlsx":
                with zipfile.ZipFile(path) as workbook:
                    expanded_size = sum(member.file_size for member in workbook.infolist())
                    if expanded_size > MAX_EXCEL_EXPANDED_BYTES:
                        raise DatasetError("Excel workbook expands beyond the safe processing limit.")
                header = pd.read_excel(path, engine="openpyxl", nrows=0)
                if len(header.columns) > MAX_COLUMNS:
                    raise DatasetError(f"Dataset has more than {MAX_COLUMNS} columns; reduce columns and retry.")
                df = pd.read_excel(path, engine="openpyxl", nrows=MAX_ANALYSIS_ROWS + 1)
                truncated = len(df) > MAX_ANALYSIS_ROWS
                df = df.iloc[:MAX_ANALYSIS_ROWS].copy()
                df.columns = [str(column) for column in df.columns]
                df.attrs["sampled"] = truncated
                return df
        except DatasetError:
            raise
        except (UnicodeDecodeError, pd.errors.ParserError, ValueError, OSError, zipfile.BadZipFile) as exc:
            raise DatasetError(f"Could not read the dataset: {exc}") from exc
        raise DatasetError("Only CSV and XLSX files are supported.")

    def load_current(self) -> tuple[pd.DataFrame, DatasetInfo]:
        info = self.get_current_info()
        df = self.read_path(UPLOAD_DIR / info.stored_name)
        if info.sampled_source:
            df.attrs["sampled"] = True
            df.attrs["analysis_row_limit"] = MAX_ANALYSIS_ROWS
        return df, info

    def load_for_training(self) -> tuple[pd.DataFrame, DatasetInfo]:
        info = self.get_current_info()
        if info.is_cleaned and info.source_stored_name:
            raw = UPLOAD_DIR / info.source_stored_name
            if not raw.is_file():
                raise DatasetError("Original dataset is missing. Upload it again before training.")
            from services.cleaning import normalized_column_names

            df = self.read_path(raw)
            df.columns = normalized_column_names(df.columns)
            return df, info
        return self.read_path(UPLOAD_DIR / info.stored_name), info

    @staticmethod
    def save_dataframe(df: pd.DataFrame, path: Path) -> None:
        # Spreadsheet applications may execute cells beginning with formula markers.
        safe = df.copy()
        for column in safe.select_dtypes(exclude="number").columns:
            safe[column] = safe[column].map(
                lambda value: "'" + value if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@"))
                else value
            )
        if path.suffix.lower() == ".xlsx":
            safe.to_excel(path, index=False, engine="openpyxl")
        else:
            safe.to_csv(path, index=False)


dataset_manager = DatasetManager()


def load_current_dataset() -> tuple[pd.DataFrame, str]:
    """Compatibility helper for older modules."""
    df, info = dataset_manager.load_current()
    return df, info.original_name
