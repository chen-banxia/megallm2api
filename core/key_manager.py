"""
密钥管理模块 - 支持多密钥轮询和健康检查
"""
import threading
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class KeyManager:
    """API密钥管理器，支持轮询和故障转移"""

    def __init__(self, key_file_path: str):
        """
        初始化密钥管理器

        Args:
            key_file_path: 密钥文件路径，每行一个密钥
        """
        self.key_file_path = Path(key_file_path)
        self._keys: List[str] = []
        self._current_index = 0
        self._lock = threading.Lock()
        self._failed_keys: set = set()  # 记录失败的key

        self._load_keys()

    def _load_keys(self) -> None:
        """从文件加载密钥"""
        if not self.key_file_path.exists():
            raise FileNotFoundError(f"密钥文件不存在: {self.key_file_path}")

        with open(self.key_file_path, 'r', encoding='utf-8') as f:
            self._keys = [line.strip() for line in f if line.strip()]

        if not self._keys:
            raise ValueError("密钥文件为空，请至少添加一个API密钥")

        logger.info(f"成功加载 {len(self._keys)} 个API密钥")

    def get_next_key(self) -> str:
        """
        获取下一个可用密钥（轮询算法）

        Returns:
            API密钥

        Raises:
            RuntimeError: 所有密钥都不可用时
        """
        with self._lock:
            if len(self._failed_keys) >= len(self._keys):
                raise RuntimeError("所有API密钥都已失败，无可用密钥")

            # 尝试最多遍历所有key
            attempts = 0
            while attempts < len(self._keys):
                key = self._keys[self._current_index]
                self._current_index = (self._current_index + 1) % len(self._keys)

                # 跳过已失败的key
                if key not in self._failed_keys:
                    logger.debug(f"使用密钥: {key[:8]}***")
                    return key

                attempts += 1

            raise RuntimeError("所有API密钥都已失败，无可用密钥")

    def mark_key_failed(self, key: str) -> None:
        """
        标记密钥失败

        Args:
            key: 失败的API密钥
        """
        with self._lock:
            self._failed_keys.add(key)
            logger.warning(f"密钥已标记为失败: {key[:8]}***，剩余可用密钥: {len(self._keys) - len(self._failed_keys)}")

    def mark_key_success(self, key: str) -> None:
        """
        标记密钥成功（恢复可用状态）

        Args:
            key: 成功的API密钥
        """
        with self._lock:
            if key in self._failed_keys:
                self._failed_keys.remove(key)
                logger.info(f"密钥已恢复可用: {key[:8]}***")

    def reset_failed_keys(self) -> None:
        """重置所有失败的密钥（用于定期健康检查）"""
        with self._lock:
            count = len(self._failed_keys)
            self._failed_keys.clear()
            logger.info(f"已重置 {count} 个失败密钥，全部恢复可用")

    def reload_keys(self) -> None:
        """重新加载密钥文件"""
        with self._lock:
            old_count = len(self._keys)
            self._load_keys()
            self._current_index = 0
            self._failed_keys.clear()
            logger.info(f"密钥已重新加载: {old_count} -> {len(self._keys)}")

    @property
    def total_keys(self) -> int:
        """总密钥数"""
        return len(self._keys)

    @property
    def available_keys(self) -> int:
        """可用密钥数"""
        return len(self._keys) - len(self._failed_keys)

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "total": self.total_keys,
            "available": self.available_keys,
            "failed": len(self._failed_keys),
            "current_index": self._current_index
        }
