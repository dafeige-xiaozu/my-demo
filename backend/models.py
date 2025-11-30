from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from backend.database import Base


class Todo(Base):
    """
    Todo 数据库模型
    
    代表待办事项表中的一条记录。
    使用 SQLAlchemy ORM 将 Python 类映射到数据库表。
    """
    __tablename__ = "todos"

    # 主键数字段，index=True 改善查询性能
    id = Column(Integer, primary_key=True, index=True)
    
    # 任务文本，最长 500 个字符，不能为空
    text = Column(String(500), nullable=False)
    
    # 是否完成，默认为 False
    completed = Column(Boolean, default=False)
    
    # 创建时间，自动设置为当前时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 更新时间，每次更新记录时自动更新
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def __repr__(self):
        """模型字符串表示，便于调试"""
        return f"<Todo(id={self.id}, text='{self.text}', completed={self.completed})>"

    def to_dict(self):
        """
        将模型实例转换为字典
        
        便于序列化为 JSON 响应。
        日期時间会被转换为 ISO 格式字符串。
        
        Returns:
            dict: 包含模型所有字段的字典
        """
        return {
            "id": self.id,
            "text": self.text,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
