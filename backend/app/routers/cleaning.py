"""Data cleaning routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_user_dataset
from app.models.dataset import Dataset
from app.schemas.dataset import CleaningPreviewRequest, CleaningRequest
from app.services.analysis_service import get_analysis_response
from app.services.cleaning_service import apply_operations, preview_cleaning
from app.utils.file_handler import load_dataframe

router = APIRouter(prefix="/cleaning", tags=["Data Cleaning"])


@router.post("/{dataset_id}/preview")
async def preview_clean(
    request: CleaningPreviewRequest,
    dataset: Annotated[Dataset, Depends(get_user_dataset)],
):
    df = load_dataframe(dataset.file_path, dataset.file_type)
    return preview_cleaning(df, request.operations)


@router.post("/{dataset_id}/apply")
async def apply_clean(
    request: CleaningRequest,
    dataset: Annotated[Dataset, Depends(get_user_dataset)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    df = load_dataframe(dataset.file_path, dataset.file_type)
    cleaned = apply_operations(df, request.operations)

    if request.apply:
        cleaned.to_csv(dataset.file_path, index=False)
        dataset.file_type = "csv"
        analysis, quality, insights = get_analysis_response(dataset.id, cleaned)
        dataset.analysis_cache = analysis
        dataset.insights_cache = insights
        dataset.data_quality_score = quality
        dataset.row_count = len(cleaned)
        dataset.column_count = len(cleaned.columns)
        await db.flush()

    return {
        "applied": request.apply,
        "rows": len(cleaned),
        "columns": len(cleaned.columns),
        "preview": cleaned.head(10).fillna("").astype(str).to_dict(orient="records"),
    }
