# ============================================================
# CodeWhisper PR - Review Schemas
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ReviewStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReviewSettings(BaseModel):
    severity_threshold: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    categories: Optional[List[str]] = None
    max_tokens: Optional[int] = Field(None, ge=100, le=8000)
    temperature: Optional[float] = Field(None, ge=0, le=1)


class ReviewCreateRequest(BaseModel):
    repository_url: str
    pr_number: int = Field(..., gt=0)
    branch: Optional[str] = None
    settings: Optional[ReviewSettings] = None


class ReviewResponse(BaseModel):
    id: str
    user_id: str
    repository_url: str
    repository_name: str
    pr_number: int
    pr_title: Optional[str]
    pr_description: Optional[str]
    status: str
    diff_content: Optional[str]
    affected_files: Optional[List[Dict[str, Any]]]
    original_tokens: Optional[int]
    optimized_tokens: Optional[int]
    tokens_saved_percentage: Optional[float]
    optimization_time_ms: Optional[int]
    review_output: Optional[Dict[str, Any]]
    summary: Optional[str]
    issues_found: Optional[List[Dict[str, Any]]]
    model_used: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    items: List[ReviewResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class ReviewStatusResponse(BaseModel):
    review_id: str
    status: str
    progress: int = Field(..., ge=0, le=100)
    estimated_time_remaining: Optional[int] = None
    error: Optional[str] = None
