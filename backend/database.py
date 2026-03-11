import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

load_dotenv()  

print(f"DATABASE_URL = {os.getenv('DATABASE_URL')}")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./hotel.db"

if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# Special params needed for SQLite
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # MySQL/PostgreSQL with connection pooling
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,             
        max_overflow=20,           
        pool_timeout=30,          
        pool_recycle=3600,         
        pool_pre_ping=True,       
        echo=False
    )


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM base class
Base = declarative_base()


# added for testing connection
def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Ensure the connection is returned to the pool after use
