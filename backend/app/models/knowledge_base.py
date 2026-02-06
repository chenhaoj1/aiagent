"""
知识库模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class KnowledgeBase(Base):
    """知识库表"""

    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True, comment="知识库ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")

    # 基本信息
    name = Column(String(100), nullable=False, comment="知识库名称")
    description = Column(Text, nullable=True, comment="知识库描述")
    avatar = Column(String(500), nullable=True, comment="知识库头像")

    # 配置
    embedding_model = Column(String(50), default="text-embedding-v1", comment="嵌入模型")
    chunk_size = Column(Integer, default=500, comment="分块大小")
    chunk_overlap = Column(Integer, default=50, comment="分块重叠")

    # 统计
    document_count = Column(Integer, default=0, comment="文档数量")
    total_chars = Column(Integer, default=0, comment="总字符数")

    # 状态
    is_public = Column(Boolean, default=False, comment="是否公开")
    is_active = Column(Boolean, default=True, comment="是否激活")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    # owner = relationship("User", back_populates="knowledge_bases")
    # documents = relationship("KnowledgeDocument", back_populates="knowledge_base", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, name={self.name})>"


class KnowledgeDocument(Base):
    """知识库文档表"""

    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True, comment="文档ID")
    kb_id = Column(Integer, ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False, comment="知识库ID")

    # 文件信息
    file_name = Column(String(255), nullable=False, comment="文件名")
    file_url = Column(String(500), nullable=True, comment="文件URL")
    file_size = Column(Integer, nullable=True, comment="文件大小（字节）")
    file_type = Column(String(50), nullable=True, comment="文件类型")

    # 处理信息
    vector_id = Column(String(100), nullable=True, comment="向量ID（Milvus）")
    chunk_count = Column(Integer, default=0, comment="分块数量")
    status = Column(String(20), default="processing", comment="处理状态：processing/completed/failed")

    # 文本内容（用于搜索）
    content = Column(Text, nullable=True, comment="提取的文本内容")
    doc_metadata = Column(Text, nullable=True, comment="元数据（JSON）")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    # knowledge_base = relationship("KnowledgeBase", back_populates="documents")

    def __repr__(self):
        return f"<KnowledgeDocument(id={self.id}, file_name={self.file_name})>"
