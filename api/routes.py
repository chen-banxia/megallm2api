"""
API路由定义
"""
import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Dict, Any

from models.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ErrorResponse,
    HealthResponse
)
from config.model_config import (
    check_context_limit,
    get_context_exceeded_error,
    get_all_models_info
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
):
    """
    聊天补全API端点

    Args:
        request_data: 聊天补全请求
        request: FastAPI请求对象

    Returns:
        聊天补全响应（非流式）或 StreamingResponse（流式）

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

        # 检查上下文长度限制
        is_exceeded, current_tokens, context_limit = check_context_limit(model, messages)

        if is_exceeded:
            logger.warning(
                f"上下文超限: model={model}, current_tokens={current_tokens}, "
                f"limit={context_limit}, usage={current_tokens/context_limit*100:.2f}%"
            )
            error_response = get_context_exceeded_error(model, current_tokens, context_limit)
            raise HTTPException(status_code=400, detail=error_response)

        logger.info(
            f"上下文检查通过: model={model}, messages={len(messages)}, "
            f"tokens={current_tokens}/{context_limit} ({current_tokens/context_limit*100:.1f}%)"
        )

        # 准备额外参数 - 如果前端传递了就使用前端的值,否则使用默认值
        extra_params = {
            "temperature": request_data.temperature if request_data.temperature is not None else 1.0,
            "top_p": request_data.top_p if request_data.top_p is not None else 1.0,
            "n": request_data.n if request_data.n is not None else 1,
            "stream": request_data.stream if request_data.stream is not None else False,
            "presence_penalty": request_data.presence_penalty if request_data.presence_penalty is not None else 0.0,
            "frequency_penalty": request_data.frequency_penalty if request_data.frequency_penalty is not None else 0.0
        }

        # 如果前端传递了 max_tokens,则添加到参数中
        if request_data.max_tokens is not None:
            extra_params["max_tokens"] = request_data.max_tokens

        is_stream = extra_params["stream"]

        logger.info(f"收到聊天补全请求: model={model}, messages={len(messages)}, params={extra_params}")

        # 调用代理服务
        result = await proxy_service.chat_completion(
            model=model,
            messages=messages,
            **extra_params
        )

        # 如果是流式响应，返回 StreamingResponse
        if is_stream:
            async def generate():
                async for chunk in result.aiter_bytes():
                    yield chunk

            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )

        # 非流式响应直接返回
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
    description="返回所有可用的AI模型及其上下文长度"
)
async def list_models(request: Request) -> Dict[str, Any]:
    """
    获取模型列表（包含上下文长度信息）

    Args:
        request: FastAPI请求对象

    Returns:
        模型列表
    """
    try:
        proxy_service = request.app.state.proxy_service
        models = await proxy_service.get_models()

        # 添加上下文长度信息
        models_info = get_all_models_info()
        context_map = {m["id"]: m for m in models_info}

        # 为每个模型添加上下文信息
        for model in models.get("data", []):
            model_id = model.get("id")
            if model_id in context_map:
                model["context_length"] = context_map[model_id]["context_length"]
                model["context_length_formatted"] = context_map[model_id]["context_length_formatted"]

        return models
    except Exception as e:
        logger.error(f"获取模型列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/v1/models/{model_id}/info",
    summary="获取指定模型信息",
    description="返回指定模型的详细信息，包括上下文长度"
)
async def get_model_info(model_id: str) -> Dict[str, Any]:
    """
    获取指定模型的详细信息

    Args:
        model_id: 模型ID

    Returns:
        模型信息
    """
    try:
        from config.model_config import get_model_context_limit, MODEL_CONTEXT_LIMITS

        if model_id not in MODEL_CONTEXT_LIMITS:
            # 返回默认信息
            return {
                "id": model_id,
                "context_length": get_model_context_limit(model_id),
                "context_length_formatted": f"{get_model_context_limit(model_id):,} tokens",
                "note": "使用默认上下文长度"
            }

        context_limit = get_model_context_limit(model_id)
        return {
            "id": model_id,
            "context_length": context_limit,
            "context_length_formatted": f"{context_limit:,} tokens",
            "usable_limit": int(context_limit * 0.9),
            "usable_limit_formatted": f"{int(context_limit * 0.9):,} tokens (90%)"
        }
    except Exception as e:
        logger.error(f"获取模型信息失败: {e}")
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
