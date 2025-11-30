from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from backend.database import get_db, init_db
from backend.models import User, Todo
from backend.schemas import (
    UserCreate, UserResponse, Token,
    TodoCreate, TodoUpdate, TodoResponse,
    ApiResponse
)
from backend.security import (
    hash_password, verify_password,
    create_access_token, get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="Todo List API - Multi-User",
    description="使用 FastAPI、SQLAlchemy 和 JWT 认证的多用户待办事项应用",
    version="2.0.0"
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
        "message": "Welcome to Multi-User Todo List API",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "2.0.0"
    }


# ==================== 用户认证 API 路由 ====================

@app.post("/api/users", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, tags=["auth"])
async def register_user(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    
    创建新用户账户。用户名必须唯一。
    
    Args:
        user_create: 用户注册数据（用户名和密码）
        db: 数据库会话
        
    Returns:
        ApiResponse: 包含新用户信息的响应
    """
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user_create.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 创建新用户
        db_user = User(
            username=user_create.username,
            hashed_password=hash_password(user_create.password)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"新用户注册: {db_user.username} (ID: {db_user.id})")
        
        # 返回用户信息（不包含密码）
        user_response = UserResponse.from_orm(db_user)
        return ApiResponse(
            success=True,
            data=user_response.model_dump(),
            message="用户注册成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"用户注册失败: {str(e)}")
        return ApiResponse(
            success=False,
            error=str(e),
            message="用户注册失败"
        )


@app.post("/api/token", response_model=ApiResponse, tags=["auth"])
async def login(username: str, password: str, db: Session = Depends(get_db)):
    """
    用户登录
    
    验证用户凭证并返回 JWT Access Token。
    
    Args:
        username: 用户名
        password: 密码
        db: 数据库会话
        
    Returns:
        ApiResponse: 包含 access_token 的响应
    """
    try:
        # 查找用户
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 创建 Access Token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        
        logger.info(f"用户登录成功: {user.username}")
        
        return ApiResponse(
            success=True,
            data={
                "access_token": access_token,
                "token_type": "bearer"
            },
            message="登录成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败: {str(e)}")
        return ApiResponse(
            success=False,
            error=str(e),
            message="登录失败"
        )


# ==================== 待办事项 API 路由 ====================

@app.get("/api/todos", response_model=ApiResponse, tags=["todos"])
async def get_todos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的所有待办事项
    
    需要有效的 JWT Token（通过 Authorization: Bearer <token>）
    只返回属于当前用户的待办事项。
    
    Returns:
        ApiResponse: 包含用户的所有 todo 的响应
    """
    try:
        # 查询当前用户的所有待办事项
        todos = db.query(Todo).filter(Todo.user_id == current_user.id).order_by(Todo.id.desc()).all()
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
async def create_todo(
    todo_create: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新的待办事项
    
    需要有效的 JWT Token。
    新创建的待办事项会自动关联到当前用户。
    
    Args:
        todo_create: 待办事项创建数据
        db: 数据库会话
        current_user: 当前认证的用户
        
    Returns:
        ApiResponse: 包含新创建的 todo 的响应
    """
    try:
        # 验证任务文本
        if not todo_create.text or not todo_create.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="任务文本不能为空"
            )
        
        # 创建新 todo，关联到当前用户
        db_todo = Todo(
            user_id=current_user.id,
            text=todo_create.text.strip(),
            completed=todo_create.completed or False,
            due_date=todo_create.due_date
        )
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        
        logger.info(f"用户 {current_user.username} 创建待办事项: {db_todo.id}")
        
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新待办事项
    
    需要有效的 JWT Token。
    用户只能更新属于自己的待办事项。
    
    Args:
        todo_id: 待办事项 ID
        todo_update: 待办事项更新数据
        db: 数据库会话
        current_user: 当前认证的用户
        
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
        
        # 检查所有权：确保用户只能修改自己的任务
        if db_todo.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改此待办事项"
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
        
        if todo_update.due_date is not None:
            db_todo.due_date = todo_update.due_date
        
        db.commit()
        db.refresh(db_todo)
        
        logger.info(f"用户 {current_user.username} 更新待办事项: {todo_id}")
        
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
async def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除待办事项
    
    需要有效的 JWT Token。
    用户只能删除属于自己的待办事项。
    
    Args:
        todo_id: 待办事项 ID
        db: 数据库会话
        current_user: 当前认证的用户
        
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
        
        # 检查所有权：确保用户只能删除自己的任务
        if db_todo.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此待办事项"
            )
        
        db.delete(db_todo)
        db.commit()
        
        logger.info(f"用户 {current_user.username} 删除待办事项: {todo_id}")
        
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
