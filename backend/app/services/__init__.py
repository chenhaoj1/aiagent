"""
服务模块
"""
# 延迟导入以避免启动时错误
try:
    from app.services.qwen_service import QwenService, qwen_service
    __all__ = [
        "QwenService",
        "qwen_service",
    ]
except ImportError:
    __all__ = []
