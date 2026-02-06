"""
知识库相关的 Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ========== 知识库 Schema ==========
class KnowledgeBaseBase(BaseModel):
    """知识库基础 Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")


class KnowledgeBaseCreate(KnowledgeBaseBase):
    """知识库创建 Schema"""
    embedding_model: str = Field("text-embedding-v1", description="嵌入模型")
    chunk_size: int = Field(500, ge=100, le=2000, description="分块大小")
    chunk_overlap: int = Field(50, ge=0, le=500, description="分块重叠")
    is_public: bool = Field(False, description="是否公开")


class KnowledgeBaseUpdate(BaseModel):
    """知识库更新 Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    avatar: Optional[str] = Field(None, max_length=500, description="知识库头像")
    is_public: Optional[bool] = Field(None, description="是否公开")


class KnowledgeBaseResponse(KnowledgeBaseBase):
    """知识库响应 Schema"""
    id: int
    user_id: int
    avatar: Optional[str] = None

    embedding_model: str
    chunk_size: int
    chunk_overlap: int

    document_count: int
    total_chars: int

    is_public: bool
    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== 知识库文档 Schema ==========
class KnowledgeDocumentBase(BaseModel):
    """知识库文档基础 Schema"""
    file_name: str = Field(..., max_length=255, description="文件名")


class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    """知识库文档创建 Schema（用于上传场景，文件在表单中）"""
    pass


class KnowledgeDocumentResponse(KnowledgeDocumentBase):
    """知识库文档响应 Schema"""
    id: int
    kb_id: int

    file_url: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None

    vector_id: Optional[str] = None
    chunk_count: int
    status: str

    content: Optional[str] = None
    metadata: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== 知识库问答 Schema ==========
class KnowledgeQueryRequest(BaseModel):
    """知识库查询请求 Schema"""
    kb_id: int = Field(..., description="知识库ID")
    query: str = Field(..., min_length=1, max_length=500, description="查询问题")
    top_k: int = Field(5, ge=1, le=20, description="返回结果数量")


class KnowledgeQueryResponse(BaseModel):
    """知识库查询响应 Schema"""
    answer: str = Field(..., description="AI 生成的回答")
    sources: List[dict] = Field(default_factory=list, description="参考来源")


# ========== 列表和分页 Schema ==========
class KnowledgeBaseListResponse(BaseModel):
    """知识库列表响应 Schema"""
    items: List[KnowledgeBaseResponse]
    total: int
    page: int
    page_size: int


class KnowledgeDocumentListResponse(BaseModel):
    """知识库文档列表响应 Schema"""
    items: List[KnowledgeDocumentResponse]
    total: int
    page: int
    page_size: int
