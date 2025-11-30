from pydantic import BaseModel, Field
from typing import Optional, Union
from datetime import datetime

# ==================== Pydantic 数据验证模型 ====================

class TodoBase(BaseModel):
    """
    Todo 基础模型
    
    作为后续其他模型的通用业务逻辑中使用：
    - TodoCreate: 创建请求
    - TodoResponse: 基于此扩展
    """
    # 任务文本，至少 1 个字符，最长 500 个
    text: str = Field(..., min_length=1, max_length=500, description="任务文本")
    
    # 是否完成，默认为 False
    completed: Optional[bool] = Field(default=False, description="是否完成")


class TodoCreate(TodoBase):
    """
    创建 Todo 的请求体模型
    
    当客户端 POST /api/todos 时，FastAPI 会自动验证请求体数据。
    """
    pass


class TodoUpdate(BaseModel):
    """
    更新 Todo 的请求体模型
    
    所有字段都是可选的，所以可以不提供也可以仅提供部分需要更新的字段。
    """
    # 任务文本，可不提供或为 None
    text: Optional[str] = Field(None, min_length=1, max_length=500, description="任务文本")
    
    # 是否完成，可不提供或为 None
    completed: Optional[bool] = Field(None, description="是否完成")


class TodoResponse(TodoBase):
    """
    Todo 响应模型
    
    当服务器响应 Todo 数据时，FastAPI 会自动序列化此模型的对象。
    整合了上述的字段以及额外的数据库字段。
    """
    # 任务 ID，这是从数据库返回的
    id: int = Field(..., description="任务 ID")
    
    # 创建时间
    created_at: Optional[datetime] = Field(None, description="创建时间")
    
    # 更新时间
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        # 使用 from_attributes 允许 SQLAlchemy 模型直接序列化
        from_attributes = True


class ApiResponse(BaseModel):
    """
    API 通用响应模型
    
    所有 API 端点都会返回此模型的对象。
    使用统一的响应格式永远维持前后端的一致性。
    """
    # 是否成功
    success: bool
    
    # 响应数据，可以是一个字典或一个数组
    data: Optional[Union[dict, list]] = None
    
    # 成功消息
    message: Optional[str] = None
    
    # 错误信息
    error: Optional[str] = None
