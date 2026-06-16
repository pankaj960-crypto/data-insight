"""Report export routes."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, get_user_dataset
from app.models.dataset import Dataset
from app.models.report import Report
from app.models.user import User
from app.reports.export_service import export_csv, export_excel, export_pdf, export_word
from app.utils.file_handler import load_dataframe

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/{dataset_id}/export")
async def export_report(
    dataset: Annotated[Dataset, Depends(get_user_dataset)],
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    format: str = Query(..., pattern=r"^(pdf|excel|word|csv)$"),
    title: str = "DataInsight Report",
):
    df = load_dataframe(dataset.file_path, dataset.file_type)
    analysis = dataset.analysis_cache or {}
    insights = dataset.insights_cache or analysis.get("insights", [])

    if format == "csv":
        file_path, size = export_csv(df, user.id, dataset.name)
        report_type = "csv"
    elif format == "excel":
        file_path, size = export_excel(df, analysis, user.id, dataset.name)
        report_type = "xlsx"
    elif format == "pdf":
        file_path, size = export_pdf(df, analysis, insights, user.id, dataset.name)
        report_type = "pdf"
    elif format == "word":
        file_path, size = export_word(df, analysis, insights, user.id, dataset.name)
        report_type = "docx"
    else:
        raise HTTPException(status_code=400, detail="Invalid format")

    report = Report(
        user_id=user.id,
        dataset_id=dataset.id,
        title=title[:255],
        report_type=report_type,
        file_path=file_path,
        file_size=size,
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)

    return {"report_id": report.id, "format": format, "download_url": f"/api/v1/reports/download/{report.id}"}


@router.get("/download/{report_id}")
async def download_report(
    report_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == user.id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    media_types = {
        "pdf": "application/pdf",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "csv": "text/csv",
    }
    return FileResponse(
        report.file_path,
        media_type=media_types.get(report.report_type, "application/octet-stream"),
        filename=f"{report.title}.{report.report_type}",
    )


@router.get("")
async def list_reports(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Report).where(Report.user_id == user.id).order_by(Report.created_at.desc()).limit(50)
    )
    reports = result.scalars().all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "report_type": r.report_type,
            "dataset_id": r.dataset_id,
            "file_size": r.file_size,
            "created_at": r.created_at,
            "download_url": f"/api/v1/reports/download/{r.id}",
        }
        for r in reports
    ]
