"""
Pydantic Schemas
"""
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserResponse,
    LoginRequest,
    TokenResponse,
    RegisterRequest,
    MembershipUpgradeRequest,
    UserListResponse,
)
from app.schemas.knowledge_base import (
    KnowledgeBaseBase,
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeDocumentBase,
    KnowledgeDocumentCreate,
    KnowledgeDocumentResponse,
    KnowledgeQueryRequest,
    KnowledgeQueryResponse,
    KnowledgeBaseListResponse,
    KnowledgeDocumentListResponse,
)
from app.schemas.video import (
    VideoTaskBase,
    VideoTaskCreate,
    VideoTaskResponse,
    VideoTemplateBase,
    VideoTemplateCreate,
    VideoTemplateUpdate,
    VideoTemplateResponse,
    VideoTaskListResponse,
    VideoTemplateListResponse,
    MessageResponse,
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "LoginRequest",
    "TokenResponse",
    "RegisterRequest",
    "MembershipUpgradeRequest",
    "UserListResponse",
    # Knowledge Base
    "KnowledgeBaseBase",
    "KnowledgeBaseCreate",
    "KnowledgeBaseUpdate",
    "KnowledgeBaseResponse",
    "KnowledgeDocumentBase",
    "KnowledgeDocumentCreate",
    "KnowledgeDocumentResponse",
    "KnowledgeQueryRequest",
    "KnowledgeQueryResponse",
    "KnowledgeBaseListResponse",
    "KnowledgeDocumentListResponse",
    # Video
    "VideoTaskBase",
    "VideoTaskCreate",
    "VideoTaskResponse",
    "VideoTemplateBase",
    "VideoTemplateCreate",
    "VideoTemplateUpdate",
    "VideoTemplateResponse",
    "VideoTaskListResponse",
    "VideoTemplateListResponse",
    "MessageResponse",
]
