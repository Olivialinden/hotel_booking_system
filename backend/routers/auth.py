'''
是導入 Python 的正則表達式模組，用來做字串格式驗證與搜尋（例如檢查 email 格式）。
'''
import re

"""
这是 Python 标准库里的函数。
它的作用一句话：把字符串变成“可以安全放进 URL 里”的形式
"""
from urllib.parse import quote
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from backend.database import SessionLocal

#导入新的函数名
from backend.security import generate_password_hash, check_password

from backend.queries import get_user_by_email, create_user
#创建一个"路由收集器"盒子
router = APIRouter()


def validate_email(email: str) -> bool:
    """驗證 email 格式"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """驗證密碼,返回 (是否有效, 錯誤訊息)"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isdigit() for c in password):
        return False, "Password must include at least one number"
    if not any(c.isalpha() for c in password):
        return False, "Password must include at least one letter"
    return True, ""

# 用 @往盒子里放路由
@router.post("/register")
def handle_user_registration(
    user_name: str = Form(None),
    email: str = Form(...),
    password: str = Form(...)
):

    db = SessionLocal()

    # 驗證email
    if not validate_email(email):
        safe_error = quote("Invalid email format")
        return RedirectResponse(f"/register?has_error={safe_error}", status_code=303)

    # 驗證密碼
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        safe_error = quote(error_msg)
        return RedirectResponse(f"/register?has_error={safe_error}", status_code=303)

    # 查询数据库：是否已有这个 email 的用户
    if get_user_by_email(db, email):
        return RedirectResponse("/register?email_exists=1", status_code=303)

    # 不存在 → 对密码做 hash，再创建用户
    hashed_password = generate_password_hash(password)
    create_user(db, email, hashed_password, user_name)

    # 注册成功 → 跳转到登录页
    return RedirectResponse("/login?registration_success=1", status_code=303)


@router.post("/login")
def handle_user_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """
    用户登录
    - 校验 email 是否存在
    - 校验密码是否正确
    - 成功后写入 session（登录态）
    """
    db = SessionLocal()

    # 根据 email 查用户
    user = get_user_by_email(db, email)

    # 用户不存在 或 密码错误 → 回到登录页
    if not user or not check_password(password, user.password):
        return RedirectResponse("/login?has_error=1", status_code=303)

    # 登录成功 → 把关键信息写入 session
    request.session["user"] = {
        "id": user.id,
        "user_name": user.user_name,
        "email": user.email,
        "is_admin": user.is_admin,
    }

    # 跳转到首页
    return RedirectResponse("/", status_code=303)


@router.get("/logout")
def handle_user_logout(request: Request):
    """
    用户登出
    - 清空 session
    - 跳转回首页
    """
    request.session.clear()
    return RedirectResponse("/", status_code=303)
