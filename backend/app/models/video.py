"""
AI 视频生成模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class VideoGenerationStatus(str, enum.Enum):
    """视频生成状态"""
    PENDING = "pending"          # 等待处理
    PROCESSING = "processing"    # 处理中
    COMPLETED = "completed"      # 完成
    FAILED = "failed"            # 失败


class VideoGenerationTask(Base):
    """AI 视频生成任务表"""

    __tablename__ = "video_generation_tasks"

    id = Column(Integer, primary_key=True, index=True, comment="任务ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")

    # 输入信息
    prompt = Column(Text, nullable=False, comment="提示词/文案")
    video_style = Column(String(50), nullable=True, comment="视频风格")
    video_duration = Column(Integer, default=30, comment="视频时长（秒）")
    aspect_ratio = Column(String(20), default="16:9", comment="宽高比：16:9, 9:16, 1:1")

    # 模板配置
    template_id = Column(Integer, ForeignKey("video_templates.id", ondelete="SET NULL"), nullable=True, comment="模板ID")
    config = Column(JSON, nullable=True, comment="生成配置（JSON）")

    # 输出信息
    video_url = Column(String(500), nullable=True, comment="视频URL")
    thumbnail_url = Column(String(500), nullable=True, comment="缩略图URL")
    video_duration_actual = Column(Integer, nullable=True, comment="实际视频时长（秒）")
    video_size = Column(Integer, nullable=True, comment="视频大小（字节）")

    # 状态信息
    status = Column(
        String(20),
        default=VideoGenerationStatus.PENDING.value,
        comment="任务状态"
    )
    progress = Column(Integer, default=0, comment="处理进度（0-100）")
    error_message = Column(Text, nullable=True, comment="错误信息")

    # 第三方服务信息
    provider_task_id = Column(String(100), nullable=True, comment="第三方服务任务ID")
    provider = Column(String(50), default="jianying", comment="服务提供商：jianying/heygen/custom")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")

    # 关系
    # user = relationship("User", back_populates="video_tasks")
    # template = relationship("VideoTemplate", back_populates="tasks")

    def __repr__(self):
        return f"<VideoGenerationTask(id={self.id}, status={self.status})>"


class VideoTemplate(Base):
    """视频模板表"""

    __tablename__ = "video_templates"

    id = Column(Integer, primary_key=True, index=True, comment="模板ID")

    # 基本信息
    name = Column(String(100), nullable=False, comment="模板名称")
    description = Column(Text, nullable=True, comment="模板描述")
    category = Column(String(50), nullable=False, comment="模板分类")
    tags = Column(String(200), nullable=True, comment="标签（逗号分隔）")

    # 预览信息
    preview_url = Column(String(500), nullable=True, comment="预览视频URL")
    thumbnail_url = Column(String(500), nullable=True, comment="缩略图URL")

    # 模板配置
    style_config = Column(JSON, nullable=True, comment="风格配置（JSON）")
    default_duration = Column(Integer, default=30, comment="默认时长（秒）")

    # 使用统计
    usage_count = Column(Integer, default=0, comment="使用次数")
    rating = Column(Float, default=0, comment="评分（0-5）")

    # 状态
    is_active = Column(Integer, default=1, comment="是否激活")
    is_featured = Column(Integer, default=0, comment="是否精选")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    # tasks = relationship("VideoGenerationTask", back_populates="template")

    def __repr__(self):
        return f"<VideoTemplate(id={self.id}, name={self.name})>"
