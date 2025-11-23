"""
密钥管理器单元测试
"""
import pytest
from pathlib import Path
from core.key_manager import KeyManager


@pytest.fixture
def temp_key_file(tmp_path):
    """创建临时密钥文件"""
    key_file = tmp_path / "keys.txt"
    key_file.write_text("key1\nkey2\nkey3\n")
    return str(key_file)


def test_load_keys(temp_key_file):
    """测试加载密钥"""
    manager = KeyManager(temp_key_file)
    assert manager.total_keys == 3
    assert manager.available_keys == 3


def test_get_next_key_rotation(temp_key_file):
    """测试密钥轮询"""
    manager = KeyManager(temp_key_file)

    key1 = manager.get_next_key()
    key2 = manager.get_next_key()
    key3 = manager.get_next_key()
    key4 = manager.get_next_key()

    assert key1 == "key1"
    assert key2 == "key2"
    assert key3 == "key3"
    assert key4 == "key1"  # 回到第一个


def test_mark_key_failed(temp_key_file):
    """测试标记密钥失败"""
    manager = KeyManager(temp_key_file)

    manager.mark_key_failed("key1")
    assert manager.available_keys == 2

    # 下一个密钥应该跳过key1
    next_key = manager.get_next_key()
    assert next_key != "key1"


def test_reset_failed_keys(temp_key_file):
    """测试重置失败的密钥"""
    manager = KeyManager(temp_key_file)

    manager.mark_key_failed("key1")
    manager.mark_key_failed("key2")
    assert manager.available_keys == 1

    manager.reset_failed_keys()
    assert manager.available_keys == 3
