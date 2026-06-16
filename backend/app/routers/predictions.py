"""ML prediction routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_user_dataset
from app.ml.prediction_service import run_prediction
from app.models.dataset import Dataset
from app.schemas.dataset import PredictionRequest, PredictionResponse
from app.utils.file_handler import load_dataframe

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("/{dataset_id}", response_model=PredictionResponse)
async def run_model(
    request: PredictionRequest,
    dataset: Annotated[Dataset, Depends(get_user_dataset)],
):
    df = load_dataframe(dataset.file_path, dataset.file_type)
    try:
        result = run_prediction(df, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return PredictionResponse(**result)
