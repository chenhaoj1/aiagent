"""
用户相关的 Pydantic Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.user import MembershipType, UserStatus


# ========== 基础 Schema ==========
class UserBase(BaseModel):
    """用户基础 Schema"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")


class UserCreate(UserBase):
    """用户创建 Schema"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")


class UserUpdate(BaseModel):
    """用户更新 Schema"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=500, description="头像URL")
    bio: Optional[str] = Field(None, max_length=200, description="个人简介")


class UserInDB(BaseModel):
    """数据库中的用户 Schema"""
    id: int
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None

    membership_type: MembershipType
    membership_expire_at: Optional[datetime] = None

    daily_quota: int
    used_quota: int
    quota_reset_at: Optional[datetime] = None

    status: UserStatus
    is_verified: bool
    is_superuser: bool

    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserInDB):
    """用户响应 Schema（不包含敏感信息）"""
    pass


# ========== 认证相关 Schema ==========
class LoginRequest(BaseModel):
    """登录请求 Schema"""
    username: str = Field(..., description="用户名/邮箱/手机号")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """令牌响应 Schema"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterRequest(UserCreate):
    """注册请求 Schema"""
    confirm_password: str = Field(..., description="确认密码")
    code: Optional[str] = Field(None, description="验证码")


# ========== 会员相关 Schema ==========
class MembershipUpgradeRequest(BaseModel):
    """会员升级请求 Schema"""
    membership_type: MembershipType
    duration: int = Field(..., ge=1, le=12, description="购买月数")


# ========== 列表和分页 Schema ==========
class UserListResponse(BaseModel):
    """用户列表响应 Schema"""
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
