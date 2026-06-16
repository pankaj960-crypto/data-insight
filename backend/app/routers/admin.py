"""Admin panel routes."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.dataset import Dataset
from app.models.report import Report
from app.models.user import User
from app.schemas.admin import AdminStats, UserAdminResponse
from app.schemas.dataset import DatasetResponse
from app.utils.file_handler import delete_file

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    users_count = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
    active_count = (
        await db.execute(select(func.count()).select_from(User).where(User.is_active == True))
    ).scalar() or 0
    datasets_count = (
        await db.execute(select(func.count()).select_from(Dataset).where(Dataset.status == "active"))
    ).scalar() or 0
    reports_count = (await db.execute(select(func.count()).select_from(Report))).scalar() or 0
    storage = (
        await db.execute(
            select(func.coalesce(func.sum(Dataset.file_size), 0)).where(Dataset.status == "active")
        )
    ).scalar() or 0

    recent = await db.execute(
        select(Dataset).where(Dataset.status == "active").order_by(Dataset.created_at.desc()).limit(10)
    )
    recent_uploads = recent.scalars().all()

    return AdminStats(
        total_users=users_count,
        active_users=active_count,
        total_datasets=datasets_count,
        total_reports=reports_count,
        total_storage_bytes=int(storage),
        recent_uploads=recent_uploads,
    )


@router.get("/users", response_model=List[UserAdminResponse])
async def list_users(
    admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    response = []
    for u in users:
        ds_count = (
            await db.execute(
                select(func.count()).select_from(Dataset).where(Dataset.user_id == u.id, Dataset.status == "active")
            )
        ).scalar() or 0
        response.append(
            UserAdminResponse(
                id=u.id,
                email=u.email,
                username=u.username,
                full_name=u.full_name,
                is_active=u.is_active,
                is_admin=u.is_admin,
                dataset_count=ds_count,
                created_at=u.created_at,
            )
        )
    return response


@router.delete("/datasets/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_dataset(
    dataset_id: int,
    admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    delete_file(dataset.file_path)
    dataset.status = "deleted"
    await db.flush()


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_report(
    report_id: int,
    admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    delete_file(report.file_path)
    await db.delete(report)
    await db.flush()
