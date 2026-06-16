"""Admin panel schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.dataset import DatasetResponse


class UserAdminResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    dataset_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminStats(BaseModel):
    total_users: int
    active_users: int
    total_datasets: int
    total_reports: int
    total_storage_bytes: int
    recent_uploads: List[DatasetResponse]
