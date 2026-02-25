#让 Python 可以访问操作系统的环境变量。
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# 读取 .env 文件中的环境变量
PROJECT_ROOT_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(PROJECT_ROOT_ENV)

# 拼接数据库连接 URL（MariaDB）
DATABASE_URL = (
    f"mariadb+mariadbconnector://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

# 创建数据库引擎（engine）
# echo=False 表示不打印 SQL（作业/生产环境更干净）
engine = create_engine(DATABASE_URL, echo=False)

# 4创建会话工厂项目启动时运行一次设置快速拨号
# 以后每次需要访问数据库，都用 SessionLocal()
SessionLocal = sessionmaker(bind=engine)

# 所有 ORM 模型都必须继承这个 Base  创建 ORM 基类项目启动时运行一次制定菜单标准
Base = declarative_base()
