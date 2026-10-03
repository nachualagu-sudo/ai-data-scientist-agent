from __future__ import annotations

from uuid import uuid4

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from config import CHART_DIR, MAX_CHART_ROWS
from dataset_manager import DatasetError, DatasetInfo
from schemas import VisualizationRequest


def _require_column(df: pd.DataFrame, column: str | None, label: str) -> str:
    if not column or column not in df.columns:
        raise DatasetError(f"Select a valid {label} column.")
    return column


def create_chart(df: pd.DataFrame, info: DatasetInfo, request: VisualizationRequest) -> str:
    sample = df.sample(MAX_CHART_ROWS, random_state=42) if len(df) > MAX_CHART_ROWS else df
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6))
    chart = request.chart_type

    if chart == "histogram":
        x = _require_column(sample, request.x_column, "numeric")
        if not pd.api.types.is_numeric_dtype(sample[x]):
            raise DatasetError("Histogram requires a numeric column.")
        sns.histplot(sample[x].dropna(), bins=30, kde=True, ax=ax, color="#2563eb")
        ax.set_title(f"Distribution of {x}")
    elif chart == "box":
        x = _require_column(sample, request.x_column, "numeric")
        if not pd.api.types.is_numeric_dtype(sample[x]):
            raise DatasetError("Box plot requires a numeric column.")
        sns.boxplot(y=sample[x], ax=ax, color="#7c3aed")
        ax.set_title(f"Outliers in {x}")
    elif chart == "scatter":
        x = _require_column(sample, request.x_column, "X-axis")
        y = _require_column(sample, request.y_column, "Y-axis")
        if not (pd.api.types.is_numeric_dtype(sample[x]) and pd.api.types.is_numeric_dtype(sample[y])):
            raise DatasetError("Scatter plot requires two numeric columns.")
        sns.scatterplot(data=sample, x=x, y=y, ax=ax, alpha=0.65, color="#0891b2")
        ax.set_title(f"{y} vs {x}")
    elif chart == "line":
        x = _require_column(sample, request.x_column, "X-axis")
        y = _require_column(sample, request.y_column, "numeric Y-axis")
        if not pd.api.types.is_numeric_dtype(sample[y]):
            raise DatasetError("Line chart Y-axis must be numeric.")
        ordered = sample[[x, y]].dropna().sort_values(x).head(2_000)
        sns.lineplot(data=ordered, x=x, y=y, ax=ax, color="#059669")
        ax.set_title(f"{y} trend by {x}")
    elif chart == "bar":
        x = _require_column(sample, request.x_column, "category")
        y = request.y_column
        if y:
            _require_column(sample, y, "numeric Y-axis")
            if not pd.api.types.is_numeric_dtype(sample[y]):
                raise DatasetError("Bar chart Y-axis must be numeric.")
            grouped = sample.groupby(x, dropna=False)[y].mean().nlargest(20).sort_values()
            grouped.plot.barh(ax=ax, color="#f59e0b")
            ax.set_xlabel(f"Average {y}")
        else:
            sample[x].astype(str).value_counts().head(20).sort_values().plot.barh(ax=ax, color="#f59e0b")
            ax.set_xlabel("Count")
        ax.set_title(f"Top values for {x}")
    elif chart == "heatmap":
        numeric = sample.select_dtypes(include="number")
        if len(numeric.columns) < 2:
            raise DatasetError("Heatmap requires at least two numeric columns.")
        numeric = numeric.iloc[:, :20]
        sns.heatmap(numeric.corr(), cmap="viridis", annot=len(numeric.columns) <= 10, fmt=".2f", ax=ax)
        ax.set_title("Correlation Heatmap")
    else:
        raise DatasetError("Unsupported chart type.")

    fig.tight_layout()
    filename = f"{info.dataset_id}_{chart}_{uuid4().hex[:10]}.png"
    fig.savefig(CHART_DIR / filename, dpi=140, bbox_inches="tight")
    plt.close(fig)
    _prune_charts()
    return filename


def _prune_charts(keep: int = 80) -> None:
    files = sorted(CHART_DIR.glob("*.png"), key=lambda path: path.stat().st_mtime, reverse=True)
    for old in files[keep:]:
        old.unlink(missing_ok=True)
