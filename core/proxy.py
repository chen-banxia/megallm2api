"""
代理核心模块 - 整合密钥管理和HTTP客户端
"""
import logging
from typing import Dict, Any, Optional
from .key_manager import KeyManager
from .http_client import MegaLLMClient

logger = logging.getLogger(__name__)


class ProxyService:
    """代理服务核心类，负责密钥轮询和请求转发"""

    def __init__(
        self,
        key_manager: KeyManager,
        http_client: MegaLLMClient,
        max_key_retries: int = 3
    ):
        """
        初始化代理服务

        Args:
            key_manager: 密钥管理器
            http_client: HTTP客户端
            max_key_retries: 密钥失败后最大重试次数
        """
        self.key_manager = key_manager
        self.http_client = http_client
        self.max_key_retries = max_key_retries

    async def chat_completion(
        self,
        model: str,
        messages: list,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行聊天补全请求，支持密钥轮询和故障转移

        Args:
            model: 模型名称
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            API响应

        Raises:
            RuntimeError: 所有密钥都失败时
        """
        last_exception = None
        attempted_keys = []

        # 尝试多个密钥
        for attempt in range(self.max_key_retries):
            try:
                # 获取下一个可用密钥
                api_key = self.key_manager.get_next_key()
                attempted_keys.append(api_key[:8])

                logger.info(f"尝试使用密钥 {api_key[:8]}*** (第{attempt + 1}次)")

                # 发送请求
                result = await self.http_client.chat_completion(
                    api_key=api_key,
                    model=model,
                    messages=messages,
                    **kwargs
                )

                # 请求成功，标记密钥为可用
                self.key_manager.mark_key_success(api_key)

                logger.info(f"请求成功: model={model}, key={api_key[:8]}***")
                return result

            except Exception as e:
                last_exception = e
                logger.warning(f"密钥 {api_key[:8]}*** 请求失败: {e}")

                # 对于客户端错误（4xx），标记密钥失败
                if hasattr(e, 'response') and e.response and 400 <= e.response.status_code < 500:
                    if e.response.status_code == 401:
                        # 认证失败，标记密钥为失败
                        self.key_manager.mark_key_failed(api_key)
                        logger.error(f"密钥认证失败，已禁用: {api_key[:8]}***")
                    elif e.response.status_code == 429:
                        # 速率限制，暂时标记失败，但会在下次重置时恢复
                        logger.warning(f"密钥达到速率限制: {api_key[:8]}***")
                    else:
                        # 其他4xx错误，直接抛出，不重试
                        raise

                # 检查是否还有可用密钥
                if self.key_manager.available_keys == 0:
                    logger.error("所有密钥都已失败，无法继续重试")
                    break

                logger.info(f"切换到下一个密钥重试...")

        # 所有重试都失败
        error_msg = f"请求失败，已尝试 {len(attempted_keys)} 个密钥: {attempted_keys}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from last_exception

    async def get_models(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        获取可用模型列表

        Args:
            api_key: 可选的API密钥，不提供则使用轮询密钥

        Returns:
            模型列表
        """
        if not api_key:
            api_key = self.key_manager.get_next_key()

        # 这里可以调用实际的模型列表API
        # 暂时返回常用模型
        return {
            "object": "list",
            "data": [
                {"id": "openai-gpt-oss-20b", "object": "model"},
                {"id": "llama3.3-70b-instruct", "object": "model"},
                {"id": "deepseek-r1-distill-llama-70b", "object": "model"},
                {"id": "alibaba-qwen3-32b", "object": "model"},
                {"id": "openai-gpt-oss-120b", "object": "model"},
                {"id": "llama3-8b-instruct", "object": "model"},
                {"id": "moonshotai/kimi-k2-instruct-0905", "object": "model"},
                {"id": "deepseek-ai/deepseek-v3.1-terminus", "object": "model"},
                {"id": "qwen/qwen3-next-80b-a3b-instruct", "object": "model"},
                {"id": "deepseek-ai/deepseek-v3.1", "object": "model"},
                {"id": "mistralai/mistral-nemotron", "object": "model"},
                {"id": "minimaxai/minimax-m2", "object": "model"},
            ]
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        获取服务统计信息

        Returns:
            统计信息字典
        """
        return {
            "key_stats": self.key_manager.get_stats(),
            "max_key_retries": self.max_key_retries
        }
