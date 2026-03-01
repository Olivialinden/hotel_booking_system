import os
from fastapi import APIRouter, Request, Depends
from backend.main import templates
from datetime import date
import os
from backend.database import SessionLocal
from backend.dependencies import get_logged_in_user, pop_flash
from backend.queries import (
    get_booked_room_ids,
    get_available_rooms,
    get_booked_rooms,
    get_bookings_by_user,
)

router = APIRouter()





@router.get("/")
def show_home_page(request: Request):
    """
    首页
    - 读取 URL 上的 check_in / check_out
    - 计算哪些房间已被预订
    - 分别得到：可预订房间 / 已预订房间
    """
    db = SessionLocal()

    # 从 URL query string 读取日期（字符串）
    check_in = request.query_params.get("check_in")
    check_out = request.query_params.get("check_out")

    # 2如果用户选择了日期 → 查已被占用的房间 ID
    if check_in and check_out:
        booked_room_ids = get_booked_room_ids(db, check_in, check_out)
        # [(1,), (3,)] → [1, 3]
        booked_room_ids = [r[0] for r in booked_room_ids]
    else:
        booked_room_ids = []

    # 根据房间 ID，分别查可订 / 已订房间
    available_rooms = get_available_rooms(db, booked_room_ids)
    booked_rooms = get_booked_rooms(db, booked_room_ids)
    flash = pop_flash(request)

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "check_in": check_in,
            "check_out": check_out,
            "available_rooms": available_rooms,
            "booked_rooms": booked_rooms,
            "today": date.today(),
            "flash": flash,
        },
    )


@router.get("/login")
def show_login_page(request: Request):
    """
    登录页面
    - 只负责展示页面
    - registration_success / has_error 来自 URL 参数
    """
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "registration_success": request.query_params.get("registration_success"),
            "has_error": request.query_params.get("has_error"),
        },
    )


@router.get("/register")
def show_register_page(request: Request):
    """
    注册页面
    - email_exists=1 表示邮箱已存在
    如果在query string里看到 email_exists=1 → 显示「邮箱已存在」的错误提示
    - has_error=xxx 表示其他错误（比如邮箱格式不对，密码不符合要求等）
    如果在query string里看到 has_error=xxx → 显示 xxx 的错误提示
    """
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "email_exists": request.query_params.get("email_exists"),
            "has_error": request.query_params.get("has_error"),
        },
    )


@router.get("/my-bookings")
def show_my_bookings_page(
    request: Request,
    current_user=Depends(get_logged_in_user),
):
    """
    我的订单页面
    - 必须已登录（Depends get_logged_in_user）
    - 查询当前用户的所有订单
    """
    db = SessionLocal()
    all_bookings = get_bookings_by_user(db, current_user["id"])
    currency_code = os.getenv("STRIPE_CURRENCY", "usd").upper()

    # 為模板補上總金額：總價 = 晚數 * 每晚價格
    for booking in all_bookings:
        stay_nights = (booking.check_out - booking.check_in).days
        if stay_nights < 0:
            stay_nights = 0
        booking.stay_nights = stay_nights
        booking.total_amount = int(booking.room.price) * stay_nights

    flash = pop_flash(request)

    return templates.TemplateResponse(
        "my_bookings.html",
        {
            "request": request,
            "all_bookings": all_bookings,
            "currency_code": currency_code,
            "flash": flash,
        },
    )
