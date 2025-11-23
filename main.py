"""
MegaLLM API代理服务 - 主应用入口
支持多密钥轮询、自动重试、故障转移的高可用API代理
"""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.settings import settings
from core.key_manager import KeyManager
from core.http_client import MegaLLMClient
from core.proxy import ProxyService
from api.routes import router
from utils.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""

    # 启动时初始化
    setup_logging()

    from loguru import logger
    logger.info(f"启动 {settings.app_name} v{settings.app_version}")

    # 初始化密钥管理器
    try:
        key_manager = KeyManager(settings.key_file_path)
        logger.info(f"密钥管理器初始化成功: {key_manager.total_keys} 个密钥")
    except Exception as e:
        logger.error(f"密钥管理器初始化失败: {e}")
        raise

    # 初始化HTTP客户端
    http_client = MegaLLMClient(
        base_url=settings.megallm_base_url,
        timeout=settings.megallm_timeout,
        max_retries=settings.megallm_max_retries
    )

    async with http_client:
        # 初始化代理服务
        proxy_service = ProxyService(
            key_manager=key_manager,
            http_client=http_client,
            max_key_retries=settings.max_key_retries
        )

        # 保存到应用状态
        app.state.proxy_service = proxy_service

        logger.info("服务启动完成，所有组件已就绪")

        yield

        # 关闭时清理
        logger.info("服务正在关闭...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="高可用的MegaLLM API代理服务，支持多密钥轮询和自动故障转移",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# 注册路由
app.include_router(router)


# 根路径
@app.get("/", tags=["Root"])
async def root():
    """根路径，返回API信息"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    from loguru import logger
    logger.error(f"未处理的异常: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "内部服务器错误",
                "type": "internal_error",
                "code": 500
            }
        }
    )


if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )