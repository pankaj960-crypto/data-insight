"""Dataset and analysis Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DatasetResponse(BaseModel):
    id: int
    name: str
    original_filename: str
    file_type: str
    file_size: int
    row_count: int
    column_count: int
    data_quality_score: Optional[float]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DatasetListResponse(BaseModel):
    datasets: List[DatasetResponse]
    total: int


class AnalysisResponse(BaseModel):
    dataset_id: int
    rows: int
    columns: int
    column_names: List[str]
    dtypes: Dict[str, str]
    missing_values: Dict[str, int]
    duplicate_count: int
    statistical_summary: Dict[str, Any]
    correlation_matrix: Optional[Dict[str, Dict[str, float]]]
    insights: List[str]
    data_quality_score: float


class ChartRequest(BaseModel):
    chart_type: str = Field(..., pattern=r"^(bar|line|pie|scatter|histogram|heatmap)$")
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    color_column: Optional[str] = None
    filter_column: Optional[str] = None
    filter_value: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: str = "asc"
    limit: int = Field(default=100, ge=1, le=1000)


class ChartResponse(BaseModel):
    chart_type: str
    plotly_json: Dict[str, Any]


class CleaningPreviewRequest(BaseModel):
    operations: List[Dict[str, Any]]


class CleaningRequest(BaseModel):
    operations: List[Dict[str, Any]]
    apply: bool = True


class PredictionRequest(BaseModel):
    task_type: str = Field(..., pattern=r"^(regression|classification)$")
    target_column: str
    feature_columns: Optional[List[str]] = None
    model_type: str = Field(
        default="auto",
        description="regression: linear, random_forest | classification: logistic, random_forest",
    )


class PredictionResponse(BaseModel):
    task_type: str
    model_type: str
    target_column: str
    feature_columns: List[str]
    metrics: Dict[str, float]
    train_size: int
    test_size: int
    feature_importance: Optional[Dict[str, float]]
    message: str
