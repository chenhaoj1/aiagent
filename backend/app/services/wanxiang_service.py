"""
通义万相视频生成服务
https://help.aliyun.com/zh/model-studio/text-to-video-api-reference
"""
import os
import asyncio
import aiohttp
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from loguru import logger

from app.core.config import settings


class WanxiangVideoService:
    """通义万相视频生成服务"""

    def __init__(self):
        # 北京地域
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"
        self.api_key = settings.DASHSCOPE_API_KEY or os.getenv("DASHSCOPE_API_KEY", "")

        if not self.api_key:
            logger.warning("未配置 DASHSCOPE_API_KEY，视频生成将使用模拟模式")

    async def create_video_task(
        self,
        prompt: str,
        model: str = "wan2.5-t2v-preview",
        size: str = "1280*720",
        duration: int = 5,
        negative_prompt: str = "",
        prompt_extend: bool = True,
        watermark: bool = False
    ) -> Dict[str, Any]:
        """
        创建视频生成任务

        Args:
            prompt: 文本提示词
            model: 模型名称
            size: 视频分辨率 (480P: 832*480, 720P: 1280*720, 1080P: 1920*1080)
            duration: 视频时长 (5/10秒)
            negative_prompt: 反向提示词
            prompt_extend: 是否智能改写prompt
            watermark: 是否添加水印

        Returns:
            任务信息，包含 task_id
        """
        if not self.api_key:
            # 模拟模式
            return self._mock_create_task(prompt)

        url = f"{self.base_url}/services/aigc/video-generation/video-synthesis"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"
        }

        data = {
            "model": model,
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "size": size,
                "duration": duration
            }
        }

        # 添加可选参数
        if negative_prompt:
            data["input"]["negative_prompt"] = negative_prompt
        if prompt_extend is not None:
            data["parameters"]["prompt_extend"] = prompt_extend
        if watermark:
            data["parameters"]["watermark"] = watermark

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    result = await response.json()

                    if response.status != 200:
                        logger.error(f"创建视频任务失败: {result}")
                        raise Exception(result.get("message", "创建任务失败"))

                    logger.info(f"视频任务创建成功: {result['output']['task_id']}")
                    return result["output"]
        except Exception as e:
            logger.error(f"调用通义万相API失败: {e}")
            # 降级到模拟模式
            return self._mock_create_task(prompt)

    async def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        查询视频生成任务结果

        Args:
            task_id: 任务ID

        Returns:
            任务结果，包含 task_status 和 video_url
        """
        if not self.api_key:
            return self._mock_get_task_result(task_id)

        url = f"{self.base_url}/tasks/{task_id}"

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    result = await response.json()

                    if response.status != 200:
                        logger.error(f"查询任务失败: {result}")
                        return {"task_status": "FAILED", "code": result.get("code"), "message": result.get("message")}

                    return result["output"]
        except Exception as e:
            logger.error(f"查询任务结果失败: {e}")
            return {"task_status": "UNKNOWN"}

    async def wait_for_completion(
        self,
        task_id: str,
        check_interval: int = 15,
        max_wait: int = 300
    ) -> Optional[str]:
        """
        等待视频生成完成并返回视频URL

        Args:
            task_id: 任务ID
            check_interval: 检查间隔（秒）
            max_wait: 最大等待时间（秒）

        Returns:
            视频URL，失败返回 None
        """
        if not self.api_key:
            # 模拟模式
            await asyncio.sleep(5)
            return f"https://example.com/videos/{task_id}.mp4"

        waited = 0
        while waited < max_wait:
            result = await self.get_task_result(task_id)
            status = result.get("task_status")

            if status == "SUCCEEDED":
                video_url = result.get("video_url")
                logger.info(f"视频生成成功: {video_url}")
                return video_url
            elif status == "FAILED":
                error_msg = result.get("message", "未知错误")
                logger.error(f"视频生成失败: {error_msg}")
                return None
            elif status in ["PENDING", "RUNNING"]:
                logger.info(f"任务状态: {status}, 已等待 {waited} 秒")
                await asyncio.sleep(check_interval)
                waited += check_interval
            else:
                logger.warning(f"未知任务状态: {status}")
                await asyncio.sleep(check_interval)
                waited += check_interval

        logger.error(f"任务超时: {task_id}")
        return None

    async def download_video(self, video_url: str, save_path: str) -> bool:
        """
        下载视频到本地

        Args:
            video_url: 视频URL
            save_path: 保存路径

        Returns:
            是否成功
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url, timeout=aiohttp.ClientTimeout(total=300)) as response:
                    if response.status != 200:
                        logger.error(f"下载视频失败: HTTP {response.status}")
                        return False

                    # 确保目录存在
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)

                    # 写入文件
                    with open(save_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)

                    logger.info(f"视频已下载: {save_path}")
                    return True
        except Exception as e:
            logger.error(f"下载视频异常: {e}")
            return False

    def _mock_create_task(self, prompt: str) -> Dict[str, Any]:
        """模拟创建任务（用于测试）"""
        import time
        task_id = f"mock_{int(time.time())}"
        logger.info(f"[模拟模式] 创建视频任务: {task_id}")
        return {
            "task_id": task_id,
            "task_status": "PENDING"
        }

    def _mock_get_task_result(self, task_id: str) -> Dict[str, Any]:
        """模拟查询任务（用于测试）"""
        if "mock_" not in task_id:
            return {"task_status": "UNKNOWN"}

        # 根据时间模拟不同的状态
        import time
        current_time = int(time.time())
        task_time = int(task_id.replace("mock_", ""))

        if current_time - task_time < 5:
            return {"task_status": "PENDING"}
        elif current_time - task_time < 10:
            return {"task_status": "RUNNING"}
        else:
            return {
                "task_status": "SUCCEEDED",
                "video_url": f"https://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/mock_{task_id}.mp4"
            }


# 全局实例
wanxiang_service = WanxiangVideoService()
