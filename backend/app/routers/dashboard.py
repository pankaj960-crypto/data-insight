"""Dashboard aggregation routes."""

from typing import Annotated, Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.dataset import Dataset
from app.models.report import Report
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
async def get_dashboard(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Dict[str, Any]:
    ds_result = await db.execute(
        select(Dataset)
        .where(Dataset.user_id == user.id, Dataset.status == "active")
        .order_by(Dataset.created_at.desc())
    )
    datasets = ds_result.scalars().all()

    reports_result = await db.execute(
        select(Report).where(Report.user_id == user.id).order_by(Report.created_at.desc()).limit(5)
    )
    reports = reports_result.scalars().all()

    total_rows = sum(d.row_count for d in datasets)
    avg_quality = (
        sum(d.data_quality_score or 0 for d in datasets) / len(datasets) if datasets else 0
    )

    kpis = [
        {"label": "Total Datasets", "value": len(datasets), "change": "+0%", "trend": "up"},
        {"label": "Total Rows", "value": f"{total_rows:,}", "change": "", "trend": "up"},
        {"label": "Avg Quality Score", "value": f"{avg_quality:.1f}", "change": "", "trend": "up"},
        {
            "label": "Reports Generated",
            "value": len(reports),
            "change": "",
            "trend": "neutral",
        },
    ]

    recommendations: List[str] = []
    for d in datasets[:3]:
        if d.insights_cache:
            recommendations.extend(d.insights_cache[:2])
    recommendations = list(dict.fromkeys(recommendations))[:6]

    return {
        "kpis": kpis,
        "recent_uploads": [
            {
                "id": d.id,
                "name": d.name,
                "rows": d.row_count,
                "columns": d.column_count,
                "quality_score": d.data_quality_score,
                "created_at": d.created_at.isoformat(),
            }
            for d in datasets[:5]
        ],
        "recent_reports": [
            {
                "id": r.id,
                "title": r.title,
                "type": r.report_type,
                "created_at": r.created_at.isoformat(),
            }
            for r in reports
        ],
        "ai_recommendations": recommendations or [
            "Upload a dataset to get started with AI-powered insights",
            "Try asking the AI assistant to summarize your data",
        ],
        "stats": {
            "total_datasets": len(datasets),
            "total_rows": total_rows,
            "total_storage": sum(d.file_size for d in datasets),
        },
    }
