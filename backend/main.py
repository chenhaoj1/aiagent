"""
AI智能体平台 - 主入口文件
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import settings
from app.core.database import init_db
from app.api import auth, knowledge_base, video


# 配置日志
logger.remove()
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)
logger.add(
    sink=lambda msg: print(msg, end=""),
    level="INFO"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时执行
    logger.info("=" * 50)
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 50)

    # 创建必要的目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # 初始化数据库表
    try:
        init_db()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.warning(f"数据库初始化警告: {e}")

    yield

    # 关闭时执行
    logger.info("应用关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI智能体平台 - 提供AI短视频生成、知识库管理、智能客服等服务",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)


# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(knowledge_base.router, prefix=settings.API_PREFIX)
app.include_router(video.router, prefix=settings.API_PREFIX)


# 根路径
@app.get("/", tags=["根路径"])
async def root():
    """
    根路径接口
    """
    return {
        "message": f"欢迎使用 {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "api_prefix": settings.API_PREFIX
    }


# 健康检查
@app.get("/health", tags=["系统"])
async def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    全局异常处理器
    """
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "服务器内部错误",
            "detail": str(exc) if settings.DEBUG else "请联系管理员"
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
