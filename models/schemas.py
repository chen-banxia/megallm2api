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
    """聊天补全请求"""
    model: str = Field(..., description="模型ID", examples=["gpt-4", "gpt-3.5-turbo"])
    messages: List[Message] = Field(..., description="消息列表", min_length=1)

    # 可选参数
    temperature: Optional[float] = Field(1.0, ge=0, le=2, description="采样温度")
    top_p: Optional[float] = Field(1.0, ge=0, le=1, description="核采样")
    n: Optional[int] = Field(1, ge=1, le=10, description="返回结果数量")
    stream: Optional[bool] = Field(False, description="是否流式返回")
    stop: Optional[List[str]] = Field(None, description="停止词")
    max_tokens: Optional[int] = Field(None, ge=1, description="最大token数")
    presence_penalty: Optional[float] = Field(0, ge=-2, le=2, description="存在惩罚")
    frequency_penalty: Optional[float] = Field(0, ge=-2, le=2, description="频率惩罚")
    logit_bias: Optional[Dict[str, float]] = Field(None, description="logit偏置")
    user: Optional[str] = Field(None, description="用户标识")

    class Config:
        json_schema_extra = {
            "example": {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": "你好！"}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
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
