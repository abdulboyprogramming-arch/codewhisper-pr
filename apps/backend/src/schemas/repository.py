# ============================================================
# CodeWhisper PR - Repository Schemas
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RepositoryCreate(BaseModel):
    url: str
    name: str = Field(..., min_length=1, max_length=200)
    full_name: str = Field(..., min_length=1, max_length=300)
    default_branch: Optional[str] = "main"
    is_private: bool = False


class RepositoryResponse(BaseModel):
    id: str
    user_id: str
    url: str
    name: str
    full_name: str
    default_branch: Optional[str]
    is_private: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
