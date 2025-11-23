"""
配置管理模块
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # 服务配置
    app_name: str = "MegaLLM Proxy API"
    app_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False

    # MegaLLM API配置
    megallm_base_url: str = "https://ai.megallm.io/v1"
    megallm_timeout: float = 120.0
    megallm_max_retries: int = 3

    # 密钥配置
    key_file_path: str = "data/keys.txt"
    max_key_retries: int = 3

    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/app.log"
    log_rotation: str = "100 MB"
    log_retention: str = "30 days"

    # CORS配置
    cors_origins: list = ["*"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()
