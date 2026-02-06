"""
知识库相关 API 路由（简化版 - 暂不含向量检索）
"""
import os
import aiofiles
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.knowledge_base import KnowledgeBase, KnowledgeDocument
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeBaseListResponse,
    KnowledgeDocumentResponse,
    KnowledgeDocumentListResponse,
    KnowledgeQueryRequest,
    KnowledgeQueryResponse,
)
from app.api.deps import get_current_active_user, check_user_quota, consume_user_quota

router = APIRouter(prefix="/knowledge-bases", tags=["知识库"])

# Milvus 向量数据库已禁用（Railway 部署不需要）
MILVUS_AVAILABLE = False

# 尝试导入通义千问服务
try:
    from app.services.qwen_service import qwen_service
    QWEN_AVAILABLE = True
except ImportError:
    QWEN_AVAILABLE = False


# ========== 知识库管理 ==========

@router.post("", response_model=KnowledgeBaseResponse, summary="创建知识库")
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建新知识库"""
    check_user_quota(current_user)

    new_kb = KnowledgeBase(
        user_id=current_user.id,
        name=kb_data.name,
        description=kb_data.description,
        embedding_model=kb_data.embedding_model,
        chunk_size=kb_data.chunk_size,
        chunk_overlap=kb_data.chunk_overlap,
        is_public=kb_data.is_public,
    )

    db.add(new_kb)
    db.commit()
    db.refresh(new_kb)

    consume_user_quota(current_user, 1)
    db.commit()

    return KnowledgeBaseResponse.model_validate(new_kb)


@router.get("", response_model=KnowledgeBaseListResponse, summary="获取知识库列表")
async def list_knowledge_bases(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的知识库列表"""
    total = db.query(KnowledgeBase).filter(
        KnowledgeBase.user_id == current_user.id
    ).count()

    items = db.query(KnowledgeBase).filter(
        KnowledgeBase.user_id == current_user.id
    ).offset((page - 1) * page_size).limit(page_size).all()

    return KnowledgeBaseListResponse(
        items=[KnowledgeBaseResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse, summary="获取知识库详情")
async def get_knowledge_base(
    kb_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取知识库详情"""
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).first()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )

    return KnowledgeBaseResponse.model_validate(kb)


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse, summary="更新知识库")
async def update_knowledge_base(
    kb_id: int,
    kb_data: KnowledgeBaseUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新知识库信息"""
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).first()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )

    update_data = kb_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(kb, field, value)

    db.commit()
    db.refresh(kb)

    return KnowledgeBaseResponse.model_validate(kb)


@router.delete("/{kb_id}", summary="删除知识库")
async def delete_knowledge_base(
    kb_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除知识库及其所有文档"""
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).first()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )

    db.delete(kb)
    db.commit()

    return {"message": "知识库已删除"}


# ========== 知识库文档管理 ==========

@router.post("/{kb_id}/documents", response_model=KnowledgeDocumentResponse, summary="上传文档")
async def upload_document(
    kb_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """上传文档到知识库"""
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).first()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )

    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".txt", ".pdf", ".doc", ".docx", ".md"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件类型"
        )

    file_content = await file.read()
    if len(file_content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制（{settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB）"
        )

    upload_dir = os.path.join(settings.UPLOAD_DIR, "kb", str(kb_id))
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_content)

    content = None
    if file_ext == ".txt":
        content = file_content.decode("utf-8")

    new_doc = KnowledgeDocument(
        kb_id=kb_id,
        file_name=file.filename,
        file_url=file_path,
        file_size=len(file_content),
        file_type=file_ext,
        content=content,
        status="completed" if content else "processing"
    )

    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    if content:
        new_doc.chunk_count = 1
        kb.document_count += 1
        kb.total_chars += len(content)
        db.commit()

    return KnowledgeDocumentResponse.model_validate(new_doc)


@router.get("/{kb_id}/documents", response_model=KnowledgeDocumentListResponse, summary="获取文档列表")
async def list_documents(
    kb_id: int,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取知识库的文档列表"""
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).first()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )

    total = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.kb_id == kb_id
    ).count()

    items = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.kb_id == kb_id
    ).offset((page - 1) * page_size).limit(page_size).all()

    return KnowledgeDocumentListResponse(
        items=[KnowledgeDocumentResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.delete("/{kb_id}/documents/{doc_id}", summary="删除文档")
async def delete_document(
    kb_id: int,
    doc_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除知识库中的文档"""
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).first()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
    )

    doc = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.id == doc_id,
        KnowledgeDocument.kb_id == kb_id
    ).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    if doc.file_url and os.path.exists(doc.file_url):
        os.remove(doc.file_url)

    db.delete(doc)
    kb.document_count -= 1
    if doc.content:
        kb.total_chars -= len(doc.content)
    db.commit()

    return {"message": "文档已删除"}


# ========== 知识库问答 ==========

@router.post("/{kb_id}/query", response_model=KnowledgeQueryResponse, summary="知识库问答")
async def query_knowledge_base(
    kb_id: int,
    query_data: KnowledgeQueryRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """使用知识库进行问答（简化版，使用通义千问直接回答）"""
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id
    ).first()

    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )

    if kb.user_id != current_user.id and not kb.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此知识库"
        )

    check_user_quota(current_user)

    try:
        if not QWEN_AVAILABLE:
            return KnowledgeQueryResponse(
                answer="通义千问服务未配置，请在 .env 中设置 QWEN_API_KEY",
                sources=[]
            )

        # 简化版：直接使用通义千问回答
        system_prompt = """你是一个专业的知识库助手。请根据用户的问题提供准确、简洁的回答。"""

        answer = await qwen_service.chat(
            prompt=query_data.query,
            system_prompt=system_prompt
        )

        consume_user_quota(current_user, 1)
        db.commit()

        return KnowledgeQueryResponse(
            answer=answer,
            sources=[]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询失败: {str(e)}"
        )
