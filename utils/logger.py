"""
日志配置模块
"""
import sys
import logging
from pathlib import Path
from loguru import logger as loguru_logger
from config.settings import settings


class InterceptHandler(logging.Handler):
    """
    将标准logging重定向到loguru
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        loguru_logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """配置日志系统"""

    # 移除默认处理器
    loguru_logger.remove()

    # 添加控制台输出
    loguru_logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )

    # 添加文件输出
    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        loguru_logger.add(
            settings.log_file,
            rotation=settings.log_rotation,
            retention=settings.log_retention,
            level=settings.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            enqueue=True  # 异步写入
        )

    # 拦截标准logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 设置第三方库日志级别
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    logging.getLogger("fastapi").handlers = [InterceptHandler()]
    logging.getLogger("httpx").setLevel(logging.WARNING)

    loguru_logger.info(f"日志系统已初始化: level={settings.log_level}, file={settings.log_file}")
