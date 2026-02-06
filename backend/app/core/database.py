"""
数据库连接配置
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# 直接使用 SQLite，绕过配置文件
DATABASE_URL = "sqlite:///./ai_agent_platform.db"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    用于 FastAPI 依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis():
    """
    获取 Redis 连接
    """
    return None  # 暂时禁用 Redis


def init_db() -> None:
    """
    初始化数据库表
    """
    Base.metadata.create_all(bind=engine)
