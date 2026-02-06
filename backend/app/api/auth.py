"""
认证相关 API 路由
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.models.user import User, MembershipType
from app.schemas.user import (
    LoginRequest,
    TokenResponse,
    RegisterRequest,
    UserResponse,
)
from app.api.deps import get_current_active_user

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录接口

    - **username**: 用户名/邮箱/手机号
    - **password**: 密码
    """
    # 查找用户（支持用户名、邮箱、手机号登录）
    user = db.query(User).filter(
        (User.username == credentials.username) |
        (User.email == credentials.username) |
        (User.phone == credentials.username)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 验证密码
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 检查用户状态
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )

    # 生成访问令牌
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # 更新最后登录时间
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    db.commit()

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/register", response_model=TokenResponse, summary="用户注册")
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    用户注册接口

    - **username**: 用户名（必填，3-50字符）
    - **email**: 邮箱（可选）
    - **phone**: 手机号（可选）
    - **password**: 密码（必填，6-50字符）
    - **confirm_password**: 确认密码
    - **nickname**: 昵称（可选）
    - **code**: 验证码（可选）
    """
    # 验证密码
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="两次密码不一致"
        )

    # 检查用户名是否存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否存在
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )

    # 检查手机号是否存在
    if user_data.phone:
        existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册"
            )

    # 创建新用户
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=get_password_hash(user_data.password),
        nickname=user_data.nickname or user_data.username,
        membership_type=MembershipType.FREE,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 生成访问令牌
    access_token = create_access_token(
        data={"sub": str(new_user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(new_user)
    )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前登录用户信息
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout", summary="用户登出")
async def logout():
    """
    用户登出接口

    注意：JWT 是无状态的，客户端只需删除本地存储的令牌即可
    """
    return {"message": "登出成功"}
