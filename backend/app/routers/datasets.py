"""Dataset upload and management routes."""

import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, get_user_dataset
from app.models.dataset import Dataset
from app.models.user import User
from app.schemas.dataset import AnalysisResponse, DatasetListResponse, DatasetResponse
from app.services.analysis_service import get_analysis_response
from app.utils.file_handler import delete_file, load_dataframe, save_upload_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.post("/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: Annotated[UploadFile, File(...)],
    name: Annotated[str, Form()] = "",
    user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    file_path, file_type, file_size = await save_upload_file(file, user.id)
    display_name = name.strip() or (file.filename or "Untitled Dataset")

    try:
        df = load_dataframe(file_path, file_type)
        analysis, quality, insights = get_analysis_response(0, df)
    except HTTPException:
        delete_file(file_path)
        raise
    except Exception as e:
        delete_file(file_path)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e

    dataset = Dataset(
        user_id=user.id,
        name=display_name[:255],
        original_filename=file.filename or "unknown",
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        row_count=len(df),
        column_count=len(df.columns),
        analysis_cache=analysis,
        insights_cache=insights,
        data_quality_score=quality,
    )
    db.add(dataset)
    await db.flush()
    await db.refresh(dataset)

    analysis["dataset_id"] = dataset.id
    dataset.analysis_cache = analysis
    await db.flush()

    logger.info("Dataset uploaded: id=%s user=%s", dataset.id, user.id)
    return dataset


@router.get("", response_model=DatasetListResponse)
async def list_datasets(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 50,
):
    count_result = await db.execute(
        select(func.count()).select_from(Dataset).where(Dataset.user_id == user.id, Dataset.status == "active")
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(Dataset)
        .where(Dataset.user_id == user.id, Dataset.status == "active")
        .order_by(Dataset.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    datasets = result.scalars().all()
    return DatasetListResponse(datasets=datasets, total=total)


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset: Annotated[Dataset, Depends(get_user_dataset)]):
    return dataset


@router.get("/{dataset_id}/analysis", response_model=AnalysisResponse)
async def get_analysis(
    dataset: Annotated[Dataset, Depends(get_user_dataset)],
    db: Annotated[AsyncSession, Depends(get_db)],
    refresh: bool = False,
):
    if dataset.analysis_cache and not refresh:
        cache = dataset.analysis_cache
        return AnalysisResponse(
            dataset_id=dataset.id,
            rows=cache.get("rows", dataset.row_count),
            columns=cache.get("columns", dataset.column_count),
            column_names=cache.get("column_names", []),
            dtypes=cache.get("dtypes", {}),
            missing_values=cache.get("missing_values", {}),
            duplicate_count=cache.get("duplicate_count", 0),
            statistical_summary=cache.get("statistical_summary", {}),
            correlation_matrix=cache.get("correlation_matrix"),
            insights=cache.get("insights", dataset.insights_cache or []),
            data_quality_score=cache.get("data_quality_score", dataset.data_quality_score or 0),
        )

    df = load_dataframe(dataset.file_path, dataset.file_type)
    analysis, quality, insights = get_analysis_response(dataset.id, df)
    dataset.analysis_cache = analysis
    dataset.insights_cache = insights
    dataset.data_quality_score = quality
    dataset.row_count = analysis["rows"]
    dataset.column_count = analysis["columns"]
    await db.flush()
    return AnalysisResponse(**analysis)


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset: Annotated[Dataset, Depends(get_user_dataset)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    delete_file(dataset.file_path)
    dataset.status = "deleted"
    await db.flush()


@router.get("/{dataset_id}/preview")
async def preview_dataset(
    dataset: Annotated[Dataset, Depends(get_user_dataset)],
    rows: int = 20,
):
    df = load_dataframe(dataset.file_path, dataset.file_type)
    preview = df.head(min(rows, 100)).fillna("").astype(str)
    return {"columns": df.columns.tolist(), "data": preview.to_dict(orient="records"), "total_rows": len(df)}
