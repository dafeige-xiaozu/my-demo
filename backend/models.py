from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from backend.database import Base


class Todo(Base):
    """Todo 数据库模型"""
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(500), nullable=False)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def __repr__(self):
        return f"<Todo(id={self.id}, text='{self.text}', completed={self.completed})>"

    def to_dict(self):
        """将模型转换为字典"""
        return {
            "id": self.id,
            "text": self.text,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
