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
    """聊天补全请求 - 所有参数都是可选的，未传则使用默认值"""
    model: Optional[str] = Field(None, description="模型ID，不传则使用默认模型 openai-gpt-oss-120b", examples=["gpt-4", "openai-gpt-oss-120b"])
    messages: List[Message] = Field(..., description="消息列表", min_length=1)

    # 可选参数 - 不传则使用后端默认值
    temperature: Optional[float] = Field(None, ge=0, le=2, description="采样温度，默认 1.0")
    top_p: Optional[float] = Field(None, ge=0, le=1, description="核采样，默认 1.0")
    n: Optional[int] = Field(None, ge=1, le=10, description="返回结果数量，默认 1")
    stream: Optional[bool] = Field(None, description="是否流式返回，默认 False")
    max_tokens: Optional[int] = Field(None, ge=1, description="最大token数")
    presence_penalty: Optional[float] = Field(None, ge=-2, le=2, description="存在惩罚，默认 0.0")
    frequency_penalty: Optional[float] = Field(None, ge=-2, le=2, description="频率惩罚，默认 0.0")

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
