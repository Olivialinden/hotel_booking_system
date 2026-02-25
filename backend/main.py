

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from database import Base, engine
from routers import pages, auth, bookings, admin, payment

# 根据 ORM 模型创建数据库表
# 此时 metadata 已经有表信息了，所以能建表

Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用
app = FastAPI()

# 添加 Session 中间件（用于登录状态）
app.add_middleware(
    SessionMiddleware,
    secret_key="hotel_booking_session_key_2026_v1",  # 作业可写死，真实项目应放到 .env
)

# 挂载静态文件   
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(bookings.router)
app.include_router(payment.router)
app.include_router(admin.router)
