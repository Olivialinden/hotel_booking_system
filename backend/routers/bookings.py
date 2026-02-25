from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database import SessionLocal
from models import Booking
from dependencies import get_logged_in_user, set_flash
from datetime import date

# 建立一個路由器，用來集中管理「訂房相關」API
router = APIRouter()

@router.post("/book")
def create_booking(
    request: Request,
    room_id: int = Form(...),
    check_in: date = Form(...),
    check_out: date = Form(...),
    user=Depends(get_logged_in_user),
):
    """
    建立一筆新訂房（需登入）。

    參數來源：
    - room_id: 前端表單傳入的房型 ID
    - check_in / check_out: 前端日期選擇器提交的入住/退房日期
    - user: 由 Depends(get_logged_in_user) 注入的當前登入使用者資訊

    流程重點：
    1) 做日期基本驗證（不可早於今天、退房不可早於入住）
    2) 查詢是否與現有「active」訂單衝突
    3) 沒衝突才建立訂單，最後導向我的訂房頁
    """

    # 建立資料庫連線（SQLAlchemy Session）
    db: Session = SessionLocal()

    # 取得今天日期，做後續日期合法性判斷
    today = date.today()

    # 日期驗證：
    # - 入住日不能早於今天
    # - 退房日必須晚於入住日（至少住 1 晚）
    if check_in < today or check_out <= check_in:
        # 用 flash 訊息把錯誤顯示到前端
        set_flash(request, "Invalid booking dates", "error")

        # 303 代表「用 GET 重新導向」，避免表單重送
        return RedirectResponse(
            "/",
            status_code=303
        )

    # 核心可用性檢查（非常關鍵）：
    # 判斷同一房間是否存在「時間重疊」且狀態為 active 的訂單
    # 重疊條件：舊訂單.check_in < 新訂單.check_out 且 舊訂單.check_out > 新訂單.check_in
    conflict = db.query(Booking).filter(
        and_(
            Booking.room_id == room_id,
            Booking.status.in_(["active", "paid"]),
            Booking.check_in < check_out,
            Booking.check_out > check_in,
        )
    ).first()

    # 有衝突就不允許建立訂房
    if conflict:
        set_flash(
            request,
            "Room is not available for selected dates",
            "error"
        )
        return RedirectResponse("/", status_code=303)

    # 建立 ORM 物件（尚未寫入資料庫）
    booking = Booking(
        user_id=user["id"],
        room_id=room_id,
        check_in=check_in,
        check_out=check_out
    )

    # 寫入資料庫並提交交易
    db.add(booking)
    db.commit()

    # 訂房成功後導向我的訂房頁
    return RedirectResponse("/my-bookings", status_code=303)


@router.post("/cancel-booking")
def cancel_booking(
    request: Request,
    booking_id: int = Form(...),
    user=Depends(get_logged_in_user),
):
    """
    取消訂房（軟取消）。

    安全限制：
    - 只能取消「自己的」訂單
    - 只能取消狀態為 active 的訂單

    實作方式：
    - 不刪除資料，而是把 status 改為 cancelled
    """

    # 建立資料庫連線
    db = SessionLocal()

    # 只查詢「符合條件」的可取消訂單
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == user["id"],
        Booking.status == "active"
    ).first()

    # 查不到代表：訂單不存在、不是本人、或已不是 active
    if not booking:
        raise HTTPException(status_code=404)

    # 軟取消：更新狀態而非刪除資料
    booking.status = "cancelled"
    db.commit()

    # 取消後回到我的訂房頁
    return RedirectResponse("/my-bookings", status_code=303)
