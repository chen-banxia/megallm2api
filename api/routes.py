"""
API路由定义
"""
import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any

from models.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ErrorResponse,
    HealthResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/v1/chat/completions",
    response_model=ChatCompletionResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="创建聊天补全",
    description="发送聊天消息并获取AI响应，兼容OpenAI API格式"
)
async def chat_completions(
    request_data: ChatCompletionRequest,
    request: Request
) -> Dict[str, Any]:
    """
    聊天补全API端点

    Args:
        request_data: 聊天补全请求
        request: FastAPI请求对象

    Returns:
        聊天补全响应

    Raises:
        HTTPException: 请求失败时
    """
    try:
        # 从应用状态获取代理服务
        proxy_service = request.app.state.proxy_service

        # 转换消息格式
        messages = [msg.dict() for msg in request_data.messages]

        # 使用默认模型（如果未指定）
        model = request_data.model or "openai-gpt-oss-120b"

        # 后端自动补充默认参数
        extra_params = {
            "temperature": 1.0,
            "top_p": 1.0,
            "n": 1,
            "stream": False,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0
        }

        logger.info(f"收到聊天补全请求: model={model}, messages={len(messages)}")

        # 调用代理服务
        result = await proxy_service.chat_completion(
            model=model,
            messages=messages,
            **extra_params
        )

        return result

    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"所有密钥失败: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "message": "所有API密钥都不可用，请稍后重试",
                    "type": "service_unavailable",
                    "code": 503
                }
            }
        )
    except Exception as e:
        logger.error(f"处理请求时发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": str(e),
                    "type": "internal_error",
                    "code": 500
                }
            }
        )


@router.get(
    "/v1/models",
    summary="获取可用模型列表",
    description="返回所有可用的AI模型"
)
async def list_models(request: Request) -> Dict[str, Any]:
    """
    获取模型列表

    Args:
        request: FastAPI请求对象

    Returns:
        模型列表
    """
    try:
        proxy_service = request.app.state.proxy_service
        models = await proxy_service.get_models()
        return models
    except Exception as e:
        logger.error(f"获取模型列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="健康检查",
    description="检查服务健康状态和密钥可用性"
)
async def health_check(request: Request) -> Dict[str, Any]:
    """
    健康检查端点

    Args:
        request: FastAPI请求对象

    Returns:
        服务健康状态
    """
    try:
        proxy_service = request.app.state.proxy_service
        stats = proxy_service.get_stats()

        return {
            "status": "healthy" if stats["key_stats"]["available"] > 0 else "degraded",
            "key_stats": stats["key_stats"],
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "version": "1.0.0"
            }
        )


@router.post(
    "/admin/reload-keys",
    summary="重新加载密钥",
    description="从文件重新加载API密钥（需要管理员权限）"
)
async def reload_keys(request: Request) -> Dict[str, str]:
    """
    重新加载密钥

    Args:
        request: FastAPI请求对象

    Returns:
        操作结果
    """
    try:
        key_manager = request.app.state.proxy_service.key_manager
        key_manager.reload_keys()

        return {"message": "密钥已成功重新加载"}
    except Exception as e:
        logger.error(f"重新加载密钥失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/admin/reset-failed-keys",
    summary="重置失败密钥",
    description="重置所有标记为失败的密钥（需要管理员权限）"
)
async def reset_failed_keys(request: Request) -> Dict[str, str]:
    """
    重置失败的密钥

    Args:
        request: FastAPI请求对象

    Returns:
        操作结果
    """
    try:
        key_manager = request.app.state.proxy_service.key_manager
        key_manager.reset_failed_keys()

        return {"message": "失败密钥已成功重置"}
    except Exception as e:
        logger.error(f"重置失败密钥失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
