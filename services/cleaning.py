from __future__ import annotations

import re

import pandas as pd


def normalized_column_names(columns) -> list[str]:
    used: set[str] = set()
    new_columns: list[str] = []
    for raw in columns:
        base = re.sub(r"[^A-Za-z0-9_]+", "_", str(raw).strip()).strip("_") or "column"
        name = base
        counter = 2
        while name.lower() in used:
            name = f"{base}_{counter}"
            counter += 1
        used.add(name.lower())
        new_columns.append(name)
    return new_columns


def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    cleaned = df.copy()
    rows_before = len(cleaned)
    duplicates_before = int(cleaned.duplicated().sum())
    missing_before = int(cleaned.isna().sum().sum())

    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    cleaned.columns = normalized_column_names(cleaned.columns)

    for column in cleaned.columns:
        series = cleaned[column]
        if pd.api.types.is_numeric_dtype(series):
            fill = series.median()
            cleaned[column] = series.fillna(0 if pd.isna(fill) else fill)
        elif pd.api.types.is_datetime64_any_dtype(series):
            mode = series.mode(dropna=True)
            cleaned[column] = series.fillna(mode.iloc[0] if not mode.empty else pd.Timestamp("1970-01-01"))
        else:
            series = series.astype("string").str.strip()
            mode = series.mode(dropna=True)
            cleaned[column] = series.fillna(mode.iloc[0] if not mode.empty else "Unknown")

    report = {
        "rows_before": int(rows_before),
        "rows_after": len(cleaned),
        "duplicates_removed": duplicates_before,
        "missing_values_before": missing_before,
        "missing_values_after": int(cleaned.isna().sum().sum()),
    }
    return cleaned, report
