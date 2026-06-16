"""Chart generation routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_user_dataset
from app.models.dataset import Dataset
from app.schemas.dataset import ChartRequest, ChartResponse
from app.services.chart_service import create_chart
from app.utils.file_handler import load_dataframe

router = APIRouter(prefix="/charts", tags=["Visualizations"])


@router.post("/{dataset_id}", response_model=ChartResponse)
async def generate_chart(
    dataset_id: int,
    request: ChartRequest,
    dataset: Annotated[Dataset, Depends(get_user_dataset)],
):
    df = load_dataframe(dataset.file_path, dataset.file_type)
    try:
        plotly_json = create_chart(df, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return ChartResponse(chart_type=request.chart_type, plotly_json=plotly_json)
