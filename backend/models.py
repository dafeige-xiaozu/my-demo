from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class User(Base):
    """
    User 数据库模型
    
    代表系统中的用户账户。
    使用 passlib 和 bcrypt 进行密码安全存储。
    """
    __tablename__ = "users"

    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 用户名，唯一且不为空
    username = Column(String(255), unique=True, nullable=False, index=True)
    
    # 哈希后的密码，不为空
    hashed_password = Column(String(255), nullable=False)
    
    # 创建时间，自动设置为当前时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系：此用户拥有的所有 Todo
    todos = relationship("Todo", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        """用户模型字符串表示，便于调试"""
        return f"<User(id={self.id}, username='{self.username}')>"


class Todo(Base):
    """
    Todo 数据库模型
    
    代表待办事项表中的一条记录。
    包含用户关联和截止日期功能。
    """
    __tablename__ = "todos"

    # 主键数字段，index=True 改善查询性能
    id = Column(Integer, primary_key=True, index=True)
    
    # 外键：关联到 User.id
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 任务文本，最长 500 个字符，不能为空
    text = Column(String(500), nullable=False)
    
    # 是否完成，默认为 False
    completed = Column(Boolean, default=False)
    
    # 截止日期，可选，用于任务时间管理
    due_date = Column(Date, nullable=True)
    
    # 创建时间，自动设置为当前时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 更新时间，每次更新记录时自动更新
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # 关系：此任务所属的用户
    owner = relationship("User", back_populates="todos")

    def __repr__(self):
        """模型字符串表示，便于调试"""
        return f"<Todo(id={self.id}, user_id={self.user_id}, text='{self.text}', completed={self.completed})>"

    def to_dict(self):
        """
        将模型实例转换为字典
        
        便于序列化为 JSON 响应。
        日期时间会被转换为 ISO 格式字符串。
        
        Returns:
            dict: 包含模型所有字段的字典
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "text": self.text,
            "completed": self.completed,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
