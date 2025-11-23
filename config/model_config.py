"""
模型配置 - 定义各模型的上下文大小和其他参数
"""
from typing import Dict, Optional

# 模型上下文长度配置（单位：tokens）
MODEL_CONTEXT_LIMITS: Dict[str, int] = {
    # OpenAI GPT 系列
    "openai-gpt-oss-20b": 128_000,
    "openai-gpt-oss-120b": 128_000,

    # Llama 系列
    "llama3.3-70b-instruct": 131_000,
    "llama3-8b-instruct": 8_000,

    # DeepSeek 系列
    "deepseek-r1-distill-llama-70b": 128_000,
    "deepseek-ai/deepseek-v3.1-terminus": 164_000,
    "deepseek-ai/deepseek-v3.1": 128_000,

    # Qwen 系列
    "alibaba-qwen3-32b": 131_000,
    "qwen/qwen3-next-80b-a3b-instruct": 262_000,

    # Moonshot 系列
    "moonshotai/kimi-k2-instruct-0905": 256_000,

    # Mistral 系列
    "mistralai/mistral-nemotron": 128_000,

    # MiniMax 系列
    "minimaxai/minimax-m2": 128_000,
}

# 默认上下文长度（用于未知模型）
DEFAULT_CONTEXT_LIMIT = 128_000


def get_model_context_limit(model: str) -> int:
    """
    获取指定模型的上下文限制

    Args:
        model: 模型名称

    Returns:
        上下文长度（tokens）
    """
    return MODEL_CONTEXT_LIMITS.get(model, DEFAULT_CONTEXT_LIMIT)


def estimate_tokens(text: str) -> int:
    """
    估算文本的 token 数量

    简单估算：中文约 1.5 字符/token，英文约 4 字符/token
    实际应使用 tiktoken 库进行准确计算

    Args:
        text: 文本内容

    Returns:
        估算的 token 数量
    """
    # 统计中文字符数量
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    # 统计其他字符数量
    other_chars = len(text) - chinese_chars

    # 中文按 1.5 字符/token，英文按 4 字符/token 估算
    estimated_tokens = int(chinese_chars / 1.5 + other_chars / 4)

    return max(estimated_tokens, 1)  # 至少返回 1


def calculate_messages_tokens(messages: list) -> int:
    """
    计算消息列表的总 token 数

    Args:
        messages: 消息列表

    Returns:
        总 token 数
    """
    total_tokens = 0

    for message in messages:
        # 计算消息内容的 tokens
        content = message.get("content", "")
        total_tokens += estimate_tokens(content)

        # 每条消息的额外开销（role、格式化等）
        total_tokens += 4

    return total_tokens


def check_context_limit(model: str, messages: list) -> tuple[bool, int, int]:
    """
    检查消息是否超出模型上下文限制

    Args:
        model: 模型名称
        messages: 消息列表

    Returns:
        (是否超限, 当前tokens数, 上限tokens数)
    """
    context_limit = get_model_context_limit(model)
    current_tokens = calculate_messages_tokens(messages)

    # 预留 10% 空间给响应和系统提示
    usable_limit = int(context_limit * 0.9)

    is_exceeded = current_tokens > usable_limit

    return is_exceeded, current_tokens, context_limit


def get_context_exceeded_error(model: str, current_tokens: int, limit: int) -> dict:
    """
    生成上下文超限错误响应

    Args:
        model: 模型名称
        current_tokens: 当前 token 数
        limit: 上下文限制

    Returns:
        错误响应字典
    """
    return {
        "error": {
            "message": f"对话上下文已超出模型 '{model}' 的限制。当前: {current_tokens:,} tokens，限制: {limit:,} tokens。请开始新的对话。",
            "type": "context_length_exceeded",
            "code": "context_length_exceeded",
            "param": {
                "model": model,
                "current_tokens": current_tokens,
                "limit": limit,
                "usage_percentage": round((current_tokens / limit) * 100, 2)
            }
        }
    }


def get_all_models_info() -> list[dict]:
    """
    获取所有模型的信息

    Returns:
        模型信息列表
    """
    models_info = []

    for model_id, context_limit in MODEL_CONTEXT_LIMITS.items():
        models_info.append({
            "id": model_id,
            "context_length": context_limit,
            "context_length_formatted": f"{context_limit:,} tokens"
        })

    # 按上下文长度降序排序
    models_info.sort(key=lambda x: x["context_length"], reverse=True)

    return models_info
