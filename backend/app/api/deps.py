"""
API 依赖项
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserStatus
from app.schemas.user import UserInDB

# OAuth2 密码模式（令牌 URL）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    获取当前登录用户

    Args:
        db: 数据库会话
        token: JWT 令牌

    Returns:
        User: 当前用户对象

    Raises:
        HTTPException: 认证失败
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 解码令牌
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    # 检查用户状态
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前激活用户

    Args:
        current_user: 当前用户

    Returns:
        User: 当前激活用户

    Raises:
        HTTPException: 用户未激活
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户未激活"
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前超级管理员

    Args:
        current_user: 当前用户

    Returns:
        User: 当前超级管理员

    Raises:
        HTTPException: 权限不足
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    return current_user


def check_user_quota(user: User, quota_amount: int = 1) -> bool:
    """
    检查用户配额

    Args:
        user: 用户对象
        quota_amount: 需要的配额数量

    Returns:
        bool: 是否有足够配额

    Raises:
        HTTPException: 配额不足
    """
    if not user.has_quota():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"配额不足，请升级会员或明天再试。今日已用：{user.used_quota}/{user.daily_quota if user.daily_quota > 0 else '无限'}"
        )
    return True


def consume_user_quota(user: User, quota_amount: int = 1) -> bool:
    """
    消耗用户配额

    Args:
        user: 用户对象
        quota_amount: 需要消耗的配额数量

    Returns:
        bool: 是否成功消耗
    """
    return user.consume_quota(quota_amount)
