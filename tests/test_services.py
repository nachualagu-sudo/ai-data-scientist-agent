import pandas as pd

from services.analysis import build_insights, build_summary
from services.cleaning import clean_dataframe


def sample_dataframe():
    return pd.DataFrame({"Price Value": [10.0, None, 30.0, 30.0], "Category": ["A", "B", None, None]})


def test_summary_reports_dataset_quality():
    result = build_summary(sample_dataframe(), "sample.csv", "abc")
    assert result["rows"] == 4
    assert result["columns"] == 2
    assert result["total_missing"] == 3


def test_cleaner_handles_numeric_and_text_missing_values():
    cleaned, report = clean_dataframe(sample_dataframe())
    assert cleaned.isna().sum().sum() == 0
    assert list(cleaned.columns) == ["Price_Value", "Category"]
    assert report["missing_values_before"] == 3
    assert report["missing_values_after"] == 0


def test_insights_are_generated_without_an_llm():
    insights = build_insights(sample_dataframe())
    assert len(insights) >= 2
