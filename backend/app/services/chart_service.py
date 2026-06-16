"""Plotly chart generation service."""

import json
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.schemas.dataset import ChartRequest


def _apply_filters(df: pd.DataFrame, req: ChartRequest) -> pd.DataFrame:
    result = df.copy()
    if req.filter_column and req.filter_value and req.filter_column in result.columns:
        result = result[result[req.filter_column].astype(str) == str(req.filter_value)]
    if req.sort_by and req.sort_by in result.columns:
        ascending = req.sort_order.lower() != "desc"
        result = result.sort_values(req.sort_by, ascending=ascending)
    return result.head(req.limit)


def create_chart(df: pd.DataFrame, req: ChartRequest) -> Dict[str, Any]:
    data = _apply_filters(df, req)
    chart_type = req.chart_type

    if chart_type == "bar":
        if not req.x_column or not req.y_column:
            raise ValueError("Bar chart requires x_column and y_column")
        fig = px.bar(data, x=req.x_column, y=req.y_column, color=req.color_column)
    elif chart_type == "line":
        if not req.x_column or not req.y_column:
            raise ValueError("Line chart requires x_column and y_column")
        fig = px.line(data, x=req.x_column, y=req.y_column, color=req.color_column)
    elif chart_type == "pie":
        if not req.x_column:
            raise ValueError("Pie chart requires x_column (labels)")
        values = req.y_column if req.y_column and req.y_column in data.columns else None
        fig = px.pie(data, names=req.x_column, values=values)
    elif chart_type == "scatter":
        if not req.x_column or not req.y_column:
            raise ValueError("Scatter plot requires x_column and y_column")
        fig = px.scatter(data, x=req.x_column, y=req.y_column, color=req.color_column)
    elif chart_type == "histogram":
        col = req.x_column or req.y_column
        if not col:
            raise ValueError("Histogram requires x_column")
        fig = px.histogram(data, x=col, color=req.color_column)
    elif chart_type == "heatmap":
        numeric = data.select_dtypes(include=[np.number])
        if numeric.shape[1] < 2:
            raise ValueError("Heatmap requires at least 2 numeric columns")
        corr = numeric.corr()
        fig = go.Figure(
            data=go.Heatmap(
                z=corr.values,
                x=corr.columns.tolist(),
                y=corr.columns.tolist(),
                colorscale="RdBu",
            )
        )
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=40, b=40),
    )
    # to_json() produces JSON-safe primitives; to_dict() leaves numpy arrays that break API responses
    return json.loads(fig.to_json())
