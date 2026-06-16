"""Tests for AI assistant."""

import pandas as pd

from app.services.ai_assistant import process_chat_message


def test_summarize():
    df = pd.DataFrame({"sales": [10, 20, 30], "product": ["A", "B", "C"]})
    reply, suggestions = process_chat_message("Summarize this dataset", df, quality_score=95.0)
    assert "Rows" in reply
    assert len(suggestions) > 0


def test_anomalies():
    df = pd.DataFrame({"value": [1, 2, 3, 100, 4, 5]})
    reply, _ = process_chat_message("Find anomalies", df)
    assert "outlier" in reply.lower() or "anomaly" in reply.lower()
