"""
应用配置文件
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    APP_NAME: str = "AI智能体平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库配置
    # Render 平台会自动提供 DATABASE_URL (PostgreSQL)
    # 本地开发使用 SQLite
    DATABASE_URL: str = "sqlite:///./ai_agent_platform.db"
    DATABASE_ECHO: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 检测是否在 Render 环境中
        if os.getenv("RENDER"):
            # Render 会自动提供 DATABASE_URL
            pass
        else:
            # 本地开发使用 SQLite
            if not self.DATABASE_URL.startswith("postgresql"):
                self.DATABASE_URL = "sqlite:///./ai_agent_platform.db"

    # 临时禁用 lru_cache 以便重新加载配置
    # @lru_cache()

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # 通义千问配置
    QWEN_API_KEY: str = ""
    QWEN_MODEL: str = "qwen-turbo"

    # 通义万相视频生成配置
    DASHSCOPE_API_KEY: str = ""

    # 向量数据库配置 (Milvus)
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION_NAME: str = "knowledge_base"

    # 文件存储配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: set = {
        ".txt", ".pdf", ".doc", ".docx",
        ".jpg", ".jpeg", ".png", ".gif",
        ".mp4", ".avi", ".mov",
        ".mp3", ".wav"
    }

    # 对象存储配置 (阿里云OSS / 腾讯云COS)
    OSS_ENDPOINT: Optional[str] = None
    OSS_ACCESS_KEY_ID: Optional[str] = None
    OSS_ACCESS_KEY_SECRET: Optional[str] = None
    OSS_BUCKET_NAME: Optional[str] = None

    # 剪映 API 配置
    JIANying_API_KEY: Optional[str] = None
    JIANying_API_URL: str = "https://api.jianying.com"

    # CORS 配置
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # Vercel 前端域名 (部署后需要更新)
        "https://*.vercel.app",
    ]

    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # 会员配置
    MEMBERSHIP_CONFIG: dict = {
        "free": {
            "daily_quota": 5,
            "features": ["basic_ai_text", "basic_kb_query"]
        },
        "standard": {
            "daily_quota": 100,
            "features": ["all_ai_text", "ai_video", "ai_image", "kb_manage"]
        },
        "professional": {
            "daily_quota": -1,  # 无限
            "features": ["all_features", "priority", "dedicated_support"]
        }
    }

    class Config:
        env_file = ".env"
        case_sensitive = True


# @lru_cache()  # 禁用缓存以便重新加载
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
