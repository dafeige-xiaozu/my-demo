from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import logging

from backend.database import get_db, init_db
from backend.models import Todo
from backend.schemas import TodoCreate, TodoUpdate, TodoResponse, ApiResponse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="Todo List API",
    description="使用 FastAPI 和 SQLAlchemy 的待办事项应用",
    version="1.0.0"
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（生产环境应该限制）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("初始化数据库...")
    init_db()
    logger.info("应用启动完成")


@app.get("/", tags=["root"])
async def root():
    """根路由"""
    return {
        "message": "Welcome to Todo List API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# ==================== Todo API 路由 ====================

@app.get("/api/todos", response_model=ApiResponse, tags=["todos"])
async def get_todos(db: Session = Depends(get_db)):
    """
    获取所有待办事项
    
    Returns:
        ApiResponse: 包含所有 todo 的响应
    """
    try:
        todos = db.query(Todo).order_by(Todo.id.desc()).all()
        todos_data = [todo.to_dict() for todo in todos]
        return ApiResponse(
            success=True,
            data=todos_data,
            message="获取待办事项成功"
        )
    except Exception as e:
        logger.error(f"获取待办事项失败: {str(e)}")
        return ApiResponse(
            success=False,
            error=str(e),
            message="获取待办事项失败"
        )


@app.post("/api/todos", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, tags=["todos"])
async def create_todo(todo_create: TodoCreate, db: Session = Depends(get_db)):
    """
    创建新的待办事项
    
    Args:
        todo_create: 待办事项创建数据
        db: 数据库会话
        
    Returns:
        ApiResponse: 包含新创建的 todo 的响应
    """
    try:
        if not todo_create.text or not todo_create.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="任务文本不能为空"
            )
        
        # 创建新 todo
        db_todo = Todo(
            text=todo_create.text.strip(),
            completed=todo_create.completed or False
        )
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        
        logger.info(f"创建待办事项: {db_todo.id}")
        
        return ApiResponse(
            success=True,
            data=db_todo.to_dict(),
            message="创建待办事项成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"创建待办事项失败: {str(e)}")
        return ApiResponse(
            success=False,
            error=str(e),
            message="创建待办事项失败"
        )


@app.put("/api/todos/{todo_id}", response_model=ApiResponse, tags=["todos"])
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    db: Session = Depends(get_db)
):
    """
    更新待办事项
    
    Args:
        todo_id: 待办事项 ID
        todo_update: 待办事项更新数据
        db: 数据库会话
        
    Returns:
        ApiResponse: 包含更新后的 todo 的响应
    """
    try:
        # 查找待办事项
        db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
        if not db_todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"待办事项 {todo_id} 不存在"
            )
        
        # 更新字段
        if todo_update.text is not None:
            if not todo_update.text.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="任务文本不能为空"
                )
            db_todo.text = todo_update.text.strip()
        
        if todo_update.completed is not None:
            db_todo.completed = todo_update.completed
        
        db.commit()
        db.refresh(db_todo)
        
        logger.info(f"更新待办事项: {todo_id}")
        
        return ApiResponse(
            success=True,
            data=db_todo.to_dict(),
            message="更新待办事项成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"更新待办事项失败: {str(e)}")
        return ApiResponse(
            success=False,
            error=str(e),
            message="更新待办事项失败"
        )


@app.delete("/api/todos/{todo_id}", response_model=ApiResponse, tags=["todos"])
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """
    删除待办事项
    
    Args:
        todo_id: 待办事项 ID
        db: 数据库会话
        
    Returns:
        ApiResponse: 删除结果
    """
    try:
        # 查找待办事项
        db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
        if not db_todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"待办事项 {todo_id} 不存在"
            )
        
        # 删除待办事项
        db.delete(db_todo)
        db.commit()
        
        logger.info(f"删除待办事项: {todo_id}")
        
        return ApiResponse(
            success=True,
            data={"id": todo_id},
            message="删除待办事项成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"删除待办事项失败: {str(e)}")
        return ApiResponse(
            success=False,
            error=str(e),
            message="删除待办事项失败"
        )


# ==================== 错误处理 ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """处理 HTTP 异常"""
    return ApiResponse(
        success=False,
        error=exc.detail,
        message="请求失败"
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """处理通用异常"""
    logger.error(f"未处理的异常: {str(exc)}")
    return ApiResponse(
        success=False,
        error="服务器内部错误",
        message="请求失败"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
