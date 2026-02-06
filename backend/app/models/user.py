"""
用户模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MembershipType(str, enum.Enum):
    """会员类型"""
    FREE = "free"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class UserStatus(str, enum.Enum):
    """用户状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class User(Base):
    """用户表"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=True, comment="邮箱")
    phone = Column(String(20), unique=True, index=True, nullable=True, comment="手机号")
    hashed_password = Column(String(200), nullable=False, comment="哈希密码")

    # 用户信息
    nickname = Column(String(50), nullable=True, comment="昵称")
    avatar = Column(String(500), nullable=True, comment="头像URL")
    bio = Column(String(200), nullable=True, comment="个人简介")

    # 会员信息
    membership_type = Column(
        Enum(MembershipType),
        default=MembershipType.FREE,
        nullable=False,
        comment="会员类型"
    )
    membership_expire_at = Column(DateTime, nullable=True, comment="会员过期时间")

    # 配额信息
    daily_quota = Column(Integer, default=5, nullable=False, comment="每日配额")
    used_quota = Column(Integer, default=0, nullable=False, comment="已使用配额")
    quota_reset_at = Column(DateTime, nullable=True, comment="配额重置时间")

    # 用户状态
    status = Column(
        Enum(UserStatus),
        default=UserStatus.ACTIVE,
        nullable=False,
        comment="用户状态"
    )
    is_verified = Column(Boolean, default=False, comment="是否已验证")
    is_superuser = Column(Boolean, default=False, comment="是否超级管理员")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")

    # 关系
    # knowledge_bases = relationship("KnowledgeBase", back_populates="owner", cascade="all, delete-orphan")
    # creations = relationship("Creation", back_populates="user", cascade="all, delete-orphan")
    # orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

    @property
    def is_active(self) -> bool:
        """用户是否激活"""
        return self.status == UserStatus.ACTIVE

    @property
    def is_premium(self) -> bool:
        """是否是付费会员"""
        return self.membership_type != MembershipType.FREE

    def can_use_feature(self, feature: str) -> bool:
        """检查用户是否可以使用某个功能"""
        from app.core.config import settings

        membership_config = settings.MEMBERSHIP_CONFIG.get(self.membership_type.value, {})
        available_features = membership_config.get("features", [])

        if "all_features" in available_features:
            return True

        return feature in available_features

    def has_quota(self) -> bool:
        """检查用户是否有配额"""
        # 无限配额
        if self.daily_quota < 0:
            return True

        # 检查是否需要重置配额
        if self.quota_reset_at and self.quota_reset_at < datetime.utcnow():
            self.used_quota = 0
            self.quota_reset_at = None

        return self.used_quota < self.daily_quota

    def consume_quota(self, amount: int = 1) -> bool:
        """消耗配额"""
        if not self.has_quota():
            return False

        self.used_quota += amount
        return True

    def reset_daily_quota(self):
        """重置每日配额"""
        self.used_quota = 0
        self.quota_reset_at = datetime.utcnow()
