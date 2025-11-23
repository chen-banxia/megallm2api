"""
数据模型定义 - 基于OpenAI API规范
"""
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class Message(BaseModel):
    """聊天消息"""
    role: Literal["system", "user", "assistant"] = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    name: Optional[str] = Field(None, description="消息发送者名称")


class ChatCompletionRequest(BaseModel):
    """聊天补全请求 - 简化版"""
    model: Optional[str] = Field(None, description="模型ID，不传则使用默认模型", examples=["gpt-4", "openai-gpt-oss-120b"])
    messages: List[Message] = Field(..., description="消息列表", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "你好！"}
                ]
            }
        }


class Usage(BaseModel):
    """使用情况统计"""
    prompt_tokens: int = Field(..., description="输入token数")
    completion_tokens: int = Field(..., description="输出token数")
    total_tokens: int = Field(..., description="总token数")


class ChatCompletionChoice(BaseModel):
    """聊天补全选项"""
    index: int = Field(..., description="选项索引")
    message: Message = Field(..., description="生成的消息")
    finish_reason: str = Field(..., description="结束原因")


class ChatCompletionResponse(BaseModel):
    """聊天补全响应"""
    id: str = Field(..., description="响应ID")
    object: str = Field("chat.completion", description="对象类型")
    created: int = Field(..., description="创建时间戳")
    model: str = Field(..., description="使用的模型")
    choices: List[ChatCompletionChoice] = Field(..., description="生成的选项")
    usage: Usage = Field(..., description="使用情况")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: Dict[str, Any] = Field(..., description="错误详情")

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "message": "Invalid API key",
                    "type": "authentication_error",
                    "code": 401
                }
            }
        }


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    key_stats: Dict[str, Any] = Field(..., description="密钥统计")
    version: str = Field(..., description="服务版本")
