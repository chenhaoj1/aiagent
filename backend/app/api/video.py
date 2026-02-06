"""
AI 视频生成相关 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from loguru import logger

from app.core.database import get_db
from app.models.user import User
from app.models.video import VideoGenerationTask, VideoTemplate, VideoGenerationStatus
from app.schemas.video import (
    VideoTaskCreate,
    VideoTaskResponse,
    VideoTaskListResponse,
    VideoTemplateCreate,
    VideoTemplateUpdate,
    VideoTemplateResponse,
    VideoTemplateListResponse,
    MessageResponse,
)
from app.api.deps import get_current_active_user, get_current_superuser, check_user_quota, consume_user_quota
from app.services.wanxiang_service import wanxiang_service

router = APIRouter(prefix="/video", tags=["AI视频"])


# ========== 视频生成任务 ==========

@router.post("/generate", response_model=VideoTaskResponse, summary="创建视频生成任务")
async def create_video_task(
    task_data: VideoTaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建 AI 视频生成任务

    - **prompt**: 提示词/文案（必填）
    - **video_style**: 视频风格（可选）
    - **video_duration**: 视频时长（秒）
    - **aspect_ratio**: 宽高比（16:9, 9:16, 1:1）
    - **template_id**: 模板ID（可选）
    """
    # 检查配额
    check_user_quota(current_user)

    # 验证模板
    if task_data.template_id:
        template = db.query(VideoTemplate).filter(
            VideoTemplate.id == task_data.template_id,
            VideoTemplate.is_active == True
        ).first()
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模板不存在或已下架"
            )

    # 创建任务
    new_task = VideoGenerationTask(
        user_id=current_user.id,
        prompt=task_data.prompt,
        video_style=task_data.video_style,
        video_duration=task_data.video_duration,
        aspect_ratio=task_data.aspect_ratio,
        template_id=task_data.template_id,
        status=VideoGenerationStatus.PENDING.value,
        progress=0,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # 消耗配额
    consume_user_quota(current_user, 1)
    db.commit()

    # 后台处理任务
    background_tasks.add_task(process_video_task, new_task.id, db)

    return VideoTaskResponse.model_validate(new_task)


async def process_video_task(task_id: int, db: Session):
    """
    后台处理视频生成任务
    使用通义万相 API 生成真实视频
    """
    task = db.query(VideoGenerationTask).filter(VideoGenerationTask.id == task_id).first()
    if not task:
        return

    try:
        # 更新状态为处理中
        task.status = VideoGenerationStatus.PROCESSING.value
        task.progress = 10
        db.commit()

        # 映射宽高比到通义万相尺寸
        size_map = {
            "16:9": "1920*1080",
            "9:16": "1080*1920",
            "1:1": "1080*1080"
        }
        size = size_map.get(task.aspect_ratio, "1920*1080")

        # 映射时长 (通义万相只支持 5/10 秒)
        duration = 5 if task.video_duration <= 5 else 10

        # 创建视频生成任务
        logger.info(f"创建视频生成任务: {task.prompt}")
        result = await wanxiang_service.create_video_task(
            prompt=task.prompt,
            size=size,
            duration=duration,
            watermark=False
        )

        task.provider_task_id = result.get("task_id")
        task.progress = 30
        db.commit()

        # 等待视频生成完成
        logger.info(f"等待视频生成完成: {task.provider_task_id}")
        video_url = await wanxiang_service.wait_for_completion(
            task_id=task.provider_task_id,
            check_interval=15,
            max_wait=300  # 最多等待5分钟
        )

        if video_url:
            # 生成成功
            task.status = VideoGenerationStatus.COMPLETED.value
            task.progress = 100
            task.video_url = video_url
            task.thumbnail_url = video_url.replace(".mp4", ".jpg")  # 通义万相不提供缩略图，使用占位
            task.video_duration_actual = duration
            task.completed_at = datetime.utcnow()
            logger.info(f"视频生成成功: {video_url}")
        else:
            # 生成失败
            task.status = VideoGenerationStatus.FAILED.value
            task.error_message = "视频生成超时或失败"
            logger.error(f"视频生成失败: {task.provider_task_id}")

        db.commit()

    except Exception as e:
        logger.error(f"处理视频任务异常: {e}")
        task.status = VideoGenerationStatus.FAILED.value
        task.error_message = str(e)
        db.commit()


@router.get("/tasks", response_model=VideoTaskListResponse, summary="获取视频任务列表")
async def list_video_tasks(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的视频生成任务列表

    - **page**: 页码
    - **page_size**: 每页数量
    - **status**: 状态筛选
    """
    # 构建查询
    query = db.query(VideoGenerationTask).filter(
        VideoGenerationTask.user_id == current_user.id
    )

    if status:
        query = query.filter(VideoGenerationTask.status == status)

    # 查询总数
    total = query.count()

    # 查询列表
    items = query.order_by(
        VideoGenerationTask.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    return VideoTaskListResponse(
        items=[VideoTaskResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/tasks/{task_id}", response_model=VideoTaskResponse, summary="获取任务详情")
async def get_video_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取视频生成任务详情
    """
    task = db.query(VideoGenerationTask).filter(
        VideoGenerationTask.id == task_id,
        VideoGenerationTask.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )

    return VideoTaskResponse.model_validate(task)


@router.delete("/tasks/{task_id}", response_model=MessageResponse, summary="删除任务")
async def delete_video_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除视频生成任务
    """
    task = db.query(VideoGenerationTask).filter(
        VideoGenerationTask.id == task_id,
        VideoGenerationTask.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )

    db.delete(task)
    db.commit()

    return MessageResponse(message="任务已删除")


# ========== 视频模板管理 ==========

@router.get("/templates", response_model=VideoTemplateListResponse, summary="获取视频模板列表")
async def list_video_templates(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    is_featured: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    获取视频模板列表

    - **page**: 页码
    - **page_size**: 每页数量
    - **category**: 分类筛选
    - **is_featured**: 是否精选
    """
    # 构建查询
    query = db.query(VideoTemplate).filter(
        VideoTemplate.is_active == True
    )

    if category:
        query = query.filter(VideoTemplate.category == category)

    if is_featured is not None:
        query = query.filter(VideoTemplate.is_featured == is_featured)

    # 查询总数
    total = query.count()

    # 查询列表
    items = query.order_by(
        VideoTemplate.is_featured.desc(),
        VideoTemplate.usage_count.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    return VideoTemplateListResponse(
        items=[VideoTemplateResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/templates/{template_id}", response_model=VideoTemplateResponse, summary="获取模板详情")
async def get_video_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """
    获取视频模板详情
    """
    template = db.query(VideoTemplate).filter(
        VideoTemplate.id == template_id,
        VideoTemplate.is_active == True
    ).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在或已下架"
        )

    return VideoTemplateResponse.model_validate(template)


@router.post("/templates", response_model=VideoTemplateResponse, summary="创建视频模板")
async def create_video_template(
    template_data: VideoTemplateCreate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    创建视频模板（仅管理员）
    """
    new_template = VideoTemplate(**template_data.model_dump())
    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return VideoTemplateResponse.model_validate(new_template)


@router.put("/templates/{template_id}", response_model=VideoTemplateResponse, summary="更新视频模板")
async def update_video_template(
    template_id: int,
    template_data: VideoTemplateUpdate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    更新视频模板（仅管理员）
    """
    template = db.query(VideoTemplate).filter(
        VideoTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在"
        )

    # 更新字段
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)

    return VideoTemplateResponse.model_validate(template)


@router.delete("/templates/{template_id}", response_model=MessageResponse, summary="删除视频模板")
async def delete_video_template(
    template_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    删除视频模板（仅管理员）
    """
    template = db.query(VideoTemplate).filter(
        VideoTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模板不存在"
        )

    db.delete(template)
    db.commit()

    return MessageResponse(message="模板已删除")


# ========== AI 文案生成辅助接口 ==========

@router.post("/generate-script", summary="AI 生成视频脚本")
async def generate_video_script(
    prompt: str,
    style: Optional[str] = None,
    duration: Optional[int] = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    使用 AI 生成视频脚本/文案

    - **prompt**: 主题或关键词
    - **style**: 风格（如：幽默、专业、情感等）
    - **duration**: 视频时长（秒）
    """
    # 检查配额
    check_user_quota(current_user)

    from app.services.qwen_service import qwen_service

    system_prompt = f"""你是一个专业的视频脚本创作助手。
请根据用户提供的主题，创作一个约 {duration} 秒的视频脚本。

脚本格式要求：
1. 开场钩子（吸引注意力的前3秒）
2. 主要内容
3. 结尾号召

风格要求：{style or "自然、有趣、有吸引力"}

请直接输出脚本内容，不要有额外的解释。"""

    try:
        script = await qwen_service.chat(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8
        )

        # 消耗配额
        consume_user_quota(current_user, 1)
        db.commit()

        return {"script": script}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"脚本生成失败: {str(e)}"
        )
