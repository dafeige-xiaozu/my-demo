# ==================== 安全认证模块 ====================

"""
安全认证模块
处理密码 hash、验证和 JWT Token 生成

包含：
- 密码 hash 和验证（使用 passlib + bcrypt）
- JWT Token 生成和验证（使用 python-jose）
- 依赖注入函数：获取当前用户
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from backend.database import get_db
from backend.models import User
from sqlalchemy.orm import Session

# ==================== 配置 ====================

# 密码 Hash 配置：使用 bcrypt 算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
SECRET_KEY = "your-secret-key-change-this-in-production-env"  # TODO: 改为环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token 有效期：30 分钟

# HTTP Bearer 认证
security = HTTPBearer()

# ==================== 密码操作函数 ====================


def hash_password(password: str) -> str:
    """
    对密码进行 Hash 加密
    
    使用 bcrypt 算法对原始密码进行安全加密。
    
    Args:
        password: 原始密码
        
    Returns:
        str: 加密后的密码 hash
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确
    
    使用 bcrypt 算法比较原始密码和 hash 密码。
    
    Args:
        plain_password: 原始密码
        hashed_password: 加密后的密码 hash
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


# ==================== JWT Token 操作函数 ====================


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    生成 JWT Access Token
    
    创建一个包含用户信息的 JWT Token，用于认证后续请求。
    
    Args:
        data: 要编码到 Token 中的数据字典
        expires_delta: Token 过期时间差，默认为 ACCESS_TOKEN_EXPIRE_MINUTES
        
    Returns:
        str: JWT Token 字符串
    """
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # 使用 SECRET_KEY 和 ALGORITHM 加密
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    验证 JWT Token 并返回其中的数据
    
    解析和验证 JWT Token，提取其中编码的用户信息。
    
    Args:
        token: JWT Token 字符串
        
    Returns:
        dict: Token 中编码的数据
        
    Raises:
        HTTPException: Token 无效或已过期时抛出 401 异常
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ==================== 依赖注入函数 ====================


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    依赖注入函数：获取当前认证的用户
    
    从请求的 Authorization header 中提取 Token，
    验证 Token 并从数据库中获取用户对象。
    
    用于 FastAPI 的依赖注入系统，可直接在路由函数参数中使用。
    
    Args:
        credentials: HTTP Bearer 认证凭证
        db: 数据库会话
        
    Returns:
        User: 当前认证的用户对象
        
    Raises:
        HTTPException: Token 无效或用户不存在时抛出异常
    """
    token = credentials.credentials
    
    # 验证 Token
    payload = verify_token(token)
    username: str = payload.get("sub")
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从数据库查找用户
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
