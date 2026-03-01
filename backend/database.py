import os
from dotenv import load_dotenv


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
load_dotenv()  # 加这行！

print(f"DATABASE_URL = {os.getenv('DATABASE_URL')}")
# 优先读取 Railway 或生产环境中的 DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

# 如果没有设置环境变量（例如本地开发或 Railway 没配置数据库）
# 自动使用 SQLite，保证项目可以正常启动
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./hotel.db"


if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)



# 如果是 SQLite 需要特殊参数
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=False
    )

# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 基类
Base = declarative_base()