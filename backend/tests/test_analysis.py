"""Tests for analysis service."""

import pandas as pd
import pytest

from app.services.analysis_service import analyze_dataframe, compute_data_quality_score, generate_insights


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "product": ["A", "B", "A", "C", "B"],
        "sales": [100, 200, 150, 50, 300],
        "category": ["Electronics", "Home", "Electronics", "Home", "Home"],
        "rating": [4.5, 3.8, None, 4.0, 4.9],
    })


def test_analyze_dataframe(sample_df):
    result = analyze_dataframe(sample_df)
    assert result["rows"] == 5
    assert result["columns"] == 4
    assert "product" in result["column_names"]
    assert result["duplicate_count"] >= 0
    assert 0 <= result["data_quality_score"] <= 100


def test_quality_score(sample_df):
    score = compute_data_quality_score(sample_df)
    assert 0 <= score <= 100


def test_generate_insights(sample_df):
    insights = generate_insights(sample_df)
    assert len(insights) > 0
    assert isinstance(insights[0], str)
