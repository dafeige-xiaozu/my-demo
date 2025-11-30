from pydantic import BaseModel, Field
from typing import Optional, Union
from datetime import datetime, date

# ==================== Pydantic 数据验证模型 ====================

# ==================== 用户相关模型 ====================

class UserBase(BaseModel):
    """
    用户基础模型
    
    包含所有用户民模式的公共字段。
    """
    # 用户名，唯一且不能为空
    username: str = Field(..., min_length=3, max_length=255, description="用户名")


class UserCreate(UserBase):
    """
    用户注册请求模型
    
    当客户端 POST /api/users 时，
    FastAPI 会自动验证此模式。
    """
    # 密码，至少 6 个字符，不能为空
    password: str = Field(..., min_length=6, max_length=255, description="密码")


class UserResponse(UserBase):
    """
    用户响应模型
    
    当服务器响应用户数据时使用。
    不包含密码或其他敏感信息。
    """
    # 用户 ID
    id: int = Field(..., description="用户 ID")
    
    # 创建时间
    created_at: Optional[datetime] = Field(None, description="创建时间")
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """
    JWT Token 响应模型
    
    用户成功登录后，服务器返回不同类型的 Token。
    """
    # Access Token，用于验证后续请求
    access_token: str = Field(..., description="Access Token")
    
    # Token 类型，常见值为 Bearer
    token_type: str = Field(..., description="Token 类型")


# ==================== Todo 相关模型 ====================

class TodoBase(BaseModel):
    """
    Todo 基础模型
    
    作为后续其他模式的通用业务逻辑中使用。
    """
    # 任务文本，至少 1 个字符，最长 500 个
    text: str = Field(..., min_length=1, max_length=500, description="任务文本")
    
    # 是否完成，默认为 False
    completed: Optional[bool] = Field(default=False, description="是否完成")
    
    # 截止日期，可选，用于任务时间管理
    due_date: Optional[date] = Field(None, description="截止日期")


class TodoCreate(TodoBase):
    """
    创建 Todo 的请求体模型
    
    当客户端 POST /api/todos 时，FastAPI 会自动验证请求体数据。
    注意此模式不提供 user_id，会从简历中自动信期。
    """
    pass


class TodoUpdate(BaseModel):
    """
    更新 Todo 的请求体模型
    
    所有字段都是可选的，可以不提供也可以仅提供部分需要更新的字段。
    """
    # 任务文本，可不提供或为 None
    text: Optional[str] = Field(None, min_length=1, max_length=500, description="任务文本")
    
    # 是否完成，可不提供或为 None
    completed: Optional[bool] = Field(None, description="是否完成")
    
    # 截止日期，可不提供或为 None
    due_date: Optional[date] = Field(None, description="截止日期")


class TodoResponse(TodoBase):
    """
    Todo 响应模型
    
    当服务器响应 Todo 数据时，FastAPI 会自动序列化此模型的对象。
    整合了上述的字段以及额外的数据库字段。
    """
    # 任务 ID，这是从数据库返回的
    id: int = Field(..., description="任务 ID")
    
    # 用户 ID，表示此任务属于哪个用户
    user_id: int = Field(..., description="用户 ID")
    
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
