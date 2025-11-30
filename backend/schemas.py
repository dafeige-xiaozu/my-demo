from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TodoBase(BaseModel):
    """Todo 基础模式"""
    text: str = Field(..., min_length=1, max_length=500, description="任务文本")
    completed: Optional[bool] = Field(default=False, description="是否完成")


class TodoCreate(TodoBase):
    """创建 Todo 的请求模式"""
    pass


class TodoUpdate(BaseModel):
    """更新 Todo 的请求模式"""
    text: Optional[str] = Field(None, min_length=1, max_length=500, description="任务文本")
    completed: Optional[bool] = Field(None, description="是否完成")


class TodoResponse(TodoBase):
    """Todo 响应模式"""
    id: int = Field(..., description="任务 ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class ApiResponse(BaseModel):
    """API 通用响应模式"""
    success: bool
    data: Optional[dict | list] = None
    message: Optional[str] = None
    error: Optional[str] = None
