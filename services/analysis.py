from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def json_value(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if pd.isna(value):
        return None
    return value


def dataframe_preview(df: pd.DataFrame, rows: int = 10) -> list[dict[str, Any]]:
    clean = df.head(rows).copy()
    clean.columns = [str(column) for column in clean.columns]
    return [
        {str(key): json_value(value) for key, value in record.items()} for record in clean.to_dict(orient="records")
    ]


def build_summary(df: pd.DataFrame, dataset_name: str, dataset_id: str) -> dict[str, Any]:
    numeric = list(df.select_dtypes(include="number").columns.astype(str))
    categorical = list(df.select_dtypes(exclude="number").columns.astype(str))
    missing = {str(k): int(v) for k, v in df.isna().sum().items()}
    stats: dict[str, dict[str, Any]] = {}
    if numeric:
        described = df[numeric].describe().round(4)
        stats = {
            str(column): {str(k): json_value(v) for k, v in values.items()}
            for column, values in described.to_dict().items()
        }
    return {
        "dataset": dataset_name,
        "dataset_id": dataset_id,
        "rows": len(df),
        "sampled": bool(df.attrs.get("sampled", False)),
        "analysis_row_limit": df.attrs.get("analysis_row_limit", len(df)) if df.attrs.get("sampled", False) else None,
        "columns": len(df.columns),
        "column_names": [str(c) for c in df.columns],
        "data_types": {str(k): str(v) for k, v in df.dtypes.items()},
        "missing_values": missing,
        "total_missing": int(sum(missing.values())),
        "duplicates": int(df.duplicated().sum()),
        "numeric_columns": numeric,
        "categorical_columns": categorical,
        "statistics": stats,
        "preview": dataframe_preview(df),
    }


def build_insights(df: pd.DataFrame) -> list[dict[str, str]]:
    insights = [
        {"title": "Dataset size", "detail": f"{len(df):,} rows and {len(df.columns):,} columns."},
        {
            "title": "Data quality",
            "detail": (
                f"{int(df.isna().sum().sum()):,} missing cells and "
                f"{int(df.duplicated().sum()):,} duplicate rows detected."
            ),
        },
    ]
    numeric = df.select_dtypes(include="number")
    if len(numeric.columns) >= 2:
        corr = numeric.corr().abs()
        np.fill_diagonal(corr.values, np.nan)
        stacked = corr.stack()
        if not stacked.empty:
            pair = stacked.idxmax()
            value = float(stacked.max())
            insights.append(
                {
                    "title": "Strongest numeric relationship",
                    "detail": f"{pair[0]} and {pair[1]} have an absolute correlation of {value:.3f}.",
                }
            )
    categorical = df.select_dtypes(exclude="number")
    if len(categorical.columns):
        column = str(categorical.nunique(dropna=True).sort_values().index[0])
        mode = df[column].mode(dropna=True)
        if not mode.empty:
            count = int((df[column] == mode.iloc[0]).sum())
            insights.append(
                {
                    "title": f"Most common value in {column}",
                    "detail": f"{mode.iloc[0]} appears {count:,} times.",
                }
            )
    if len(numeric.columns):
        outlier_counts: dict[str, int] = {}
        for column in numeric.columns:
            series = numeric[column].dropna()
            if series.empty:
                continue
            q1, q3 = series.quantile([0.25, 0.75])
            iqr = q3 - q1
            if iqr > 0:
                outlier_counts[str(column)] = int(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum())
        if outlier_counts:
            column = max(outlier_counts, key=outlier_counts.get)
            insights.append(
                {
                    "title": "Potential outliers",
                    "detail": (
                        f"{column} has {outlier_counts[column]:,} potential IQR outliers. Review them before modelling."
                    ),
                }
            )
    return insights
