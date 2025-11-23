"""
HTTP客户端模块 - 支持自动重试和超时控制
"""
import asyncio
import logging
from typing import Optional, Dict, Any
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

logger = logging.getLogger(__name__)


class MegaLLMClient:
    """MegaLLM API客户端，支持自动重试和故障转移"""

    def __init__(
        self,
        base_url: str = "https://ai.megallm.io/v1",
        timeout: float = 120.0,
        max_retries: int = 3,
        retry_multiplier: float = 1.5
    ):
        """
        初始化HTTP客户端

        Args:
            base_url: API基础URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_multiplier: 重试等待时间倍数
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_multiplier = retry_multiplier

        # 使用httpx异步客户端
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
            http2=True  # 启用HTTP/2支持
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self._client:
            await self._client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def chat_completion(
        self,
        api_key: str,
        model: str,
        messages: list,
        **kwargs
    ) -> Dict[str, Any]:
        """
        调用聊天补全API

        Args:
            api_key: API密钥
            model: 模型名称
            messages: 消息列表
            **kwargs: 其他参数（temperature, max_tokens等）

        Returns:
            API响应字典

        Raises:
            httpx.HTTPStatusError: HTTP错误
            httpx.TimeoutException: 超时错误
            httpx.NetworkError: 网络错误
        """
        if not self._client:
            raise RuntimeError("客户端未初始化，请使用async with语句")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }

        logger.info(f"发送请求到MegaLLM API: model={model}, messages_count={len(messages)}")

        try:
            response = await self._client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()
            logger.info(f"请求成功: model={model}, usage={result.get('usage', {})}")
            return result

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP错误 [{e.response.status_code}]: {e.response.text}")
            # 对于4xx错误不重试
            if 400 <= e.response.status_code < 500:
                raise
            # 5xx错误会被重试
            raise

        except httpx.TimeoutException as e:
            logger.warning(f"请求超时: {e}")
            raise

        except httpx.NetworkError as e:
            logger.warning(f"网络错误: {e}")
            raise

        except Exception as e:
            logger.error(f"未知错误: {e}")
            raise

    async def health_check(self, api_key: str) -> bool:
        """
        健康检查

        Args:
            api_key: API密钥

        Returns:
            是否健康
        """
        try:
            await self.chat_completion(
                api_key=api_key,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return False


async def create_client(
    base_url: str = "https://ai.megallm.io/v1",
    timeout: float = 120.0,
    max_retries: int = 3
) -> MegaLLMClient:
    """
    创建HTTP客户端（工厂函数）

    Args:
        base_url: API基础URL
        timeout: 请求超时时间
        max_retries: 最大重试次数

    Returns:
        MegaLLMClient实例
    """
    return MegaLLMClient(
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries
    )
