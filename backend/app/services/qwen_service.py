"""
通义千问 AI 服务（简化版）
"""
import json
from typing import Optional, List, Dict, Any
import httpx
from loguru import logger

from app.core.config import settings


class QwenService:
    """通义千问服务类"""

    def __init__(self):
        self.api_key = settings.QWEN_API_KEY
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.model = settings.QWEN_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _make_request(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """发起 API 请求"""
        if not self.api_key:
            raise ValueError("通义千问 API Key 未配置，请在 .env 文件中设置 QWEN_API_KEY")

        payload = {
            "model": kwargs.get("model", self.model),
            "input": {
                "messages": messages
            },
            "parameters": {
                "result_format": kwargs.get("result_format", "message"),
                "stream": stream,
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "max_tokens": kwargs.get("max_tokens", 2000),
            }
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"通义千问 API 请求失败: {e}")
                raise

    async def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """对话生成"""
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        if history:
            messages.extend(history)

        messages.append({
            "role": "user",
            "content": prompt
        })

        response = await self._make_request(messages, **kwargs)

        if "output" in response and "choices" in response["output"]:
            return response["output"]["choices"][0]["message"]["content"]
        else:
            logger.error(f"通义千问响应格式错误: {response}")
            raise ValueError("AI 服务响应格式错误")


# 全局服务实例
qwen_service = QwenService()
