"""
AI 视频生成相关的 Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.models.video import VideoGenerationStatus


# ========== 视频生成任务 Schema ==========
class VideoTaskBase(BaseModel):
    """视频生成任务基础 Schema"""
    prompt: str = Field(..., min_length=1, max_length=2000, description="提示词/文案")
    video_style: Optional[str] = Field(None, max_length=50, description="视频风格")
    video_duration: int = Field(30, ge=5, le=300, description="视频时长（秒）")
    aspect_ratio: str = Field("16:9", pattern=r"^(16:9|9:16|1:1)$", description="宽高比")


class VideoTaskCreate(VideoTaskBase):
    """视频生成任务创建 Schema"""
    template_id: Optional[int] = Field(None, description="模板ID")


class VideoTaskResponse(VideoTaskBase):
    """视频生成任务响应 Schema"""
    id: int
    user_id: int

    template_id: Optional[int] = None

    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_duration_actual: Optional[int] = None
    video_size: Optional[int] = None

    status: VideoGenerationStatus
    progress: int
    error_message: Optional[str] = None

    provider_task_id: Optional[str] = None
    provider: str

    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ========== 视频模板 Schema ==========
class VideoTemplateBase(BaseModel):
    """视频模板基础 Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    category: str = Field(..., max_length=50, description="模板分类")
    tags: Optional[str] = Field(None, max_length=200, description="标签（逗号分隔）")


class VideoTemplateCreate(VideoTemplateBase):
    """视频模板创建 Schema"""
    preview_url: Optional[str] = Field(None, max_length=500, description="预览视频URL")
    thumbnail_url: Optional[str] = Field(None, max_length=500, description="缩略图URL")
    style_config: Optional[dict] = Field(None, description="风格配置")
    default_duration: int = Field(30, ge=5, le=300, description="默认时长")
    is_featured: bool = Field(False, description="是否精选")


class VideoTemplateUpdate(BaseModel):
    """视频模板更新 Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    category: Optional[str] = Field(None, max_length=50, description="模板分类")
    tags: Optional[str] = Field(None, max_length=200, description="标签")
    preview_url: Optional[str] = Field(None, max_length=500, description="预览视频URL")
    thumbnail_url: Optional[str] = Field(None, max_length=500, description="缩略图URL")
    style_config: Optional[dict] = Field(None, description="风格配置")
    default_duration: Optional[int] = Field(None, ge=5, le=300, description="默认时长")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_featured: Optional[bool] = Field(None, description="是否精选")


class VideoTemplateResponse(VideoTemplateBase):
    """视频模板响应 Schema"""
    id: int

    preview_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    style_config: Optional[dict] = None
    default_duration: int

    usage_count: int
    rating: float

    is_active: bool
    is_featured: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== 列表和分页 Schema ==========
class VideoTaskListResponse(BaseModel):
    """视频任务列表响应 Schema"""
    items: List[VideoTaskResponse]
    total: int
    page: int
    page_size: int


class VideoTemplateListResponse(BaseModel):
    """视频模板列表响应 Schema"""
    items: List[VideoTemplateResponse]
    total: int
    page: int
    page_size: int


# ========== 通用响应 Schema ==========
class MessageResponse(BaseModel):
    """通用消息响应 Schema"""
    message: str
    code: int = 200
