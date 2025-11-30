from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# ==================== 数据库配置 ====================

# 获取项目根目录，用于构建数据库文件路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SQLite 数据库路径
DATABASE_URL = f"sqlite:///{BASE_DIR}/todos.db"

# 创建数据库引擎
# check_same_thread=False 是 SQLite 必需的配置（允许多线程访问）
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 创建会话工厂
# autocommit=False: 需要手动提交事务
# autoflush=False: 需要手动刷新会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy 声明基类，所有模型都要继承它
Base = declarative_base()


def get_db():
    """
    FastAPI 依赖注入：获取数据库会话
    
    生成器函数，每次请求创建一个新的数据库会话，
    请求完成后自动关闭连接
    
    Yields:
        Session: SQLAlchemy 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库
    
    创建所有已定义的表（todos 表）。
    应用启动时自动调用，如果表已存在则不再创建。
    """
    Base.metadata.create_all(bind=engine)
