from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
import stripe
from backend.database import SessionLocal
from backend.models import Booking
from backend.dependencies import get_logged_in_user, set_flash


router = APIRouter()


@router.post("/create-checkout-session")
def create_checkout_session(
    request: Request,
    booking_id: int = Form(...),
    user=Depends(get_logged_in_user),
):
   
    db: Session = SessionLocal()

    # 僅查詢「該使用者自己的」訂單 
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == user["id"],
    ).first()

    if not booking:
        # 找不到通常代表：訂單不存在或不屬於目前登入者
        raise HTTPException(status_code=404)

    if booking.status != "active":
        # 僅 active 可付款；cancelled / paid 都不應再次進入付款
        set_flash(request, "This booking cannot be paid", "error")
        return RedirectResponse("/my-bookings", status_code=303)

    # 讀取 Stripe 私鑰；若未設定，直接回前頁提示
    stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
    if not stripe_secret_key:
        set_flash(request, "Stripe is not configured: set STRIPE_SECRET_KEY in .env", "error")
        return RedirectResponse("/my-bookings", status_code=303)

    # 設定 Stripe SDK 的 API 金鑰
    stripe.api_key = stripe_secret_key

    # APP_BASE_URL 用於組合成功/取消回跳網址
    app_base_url = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")

 
    stripe_currency = os.getenv("STRIPE_CURRENCY", "sek").lower()

   
    stay_nights = (booking.check_out - booking.check_in).days
    if stay_nights <= 0:
        set_flash(request, "Invalid booking length", "error")
        return RedirectResponse("/my-bookings", status_code=303)

    # 總價（最小貨幣單位）= 每晚價格 × 晚數 × 100
    total_amount_minor = int(booking.room.price) * stay_nights * 100

    try:

        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": stripe_currency,
                        "product_data": {
                            "name": f"{booking.room.name} booking #{booking.id}",
                        },
                        "unit_amount": total_amount_minor,
                    },
                    "quantity": 1,
                }
            ],
            metadata={
                "booking_id": str(booking.id),
                "user_id": str(user["id"]),
            },
            success_url=f"{app_base_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{app_base_url}/my-bookings",
        )
    except Exception:
        # 任何 Stripe 連線/API 錯誤，統一回前頁顯示友善訊息
        set_flash(request, "Unable to start payment session", "error")
        return RedirectResponse("/my-bookings", status_code=303)

    # 用 303 轉址到 Stripe 託管的結帳頁
    return RedirectResponse(checkout_session.url, status_code=303)


@router.get("/payment/success")
def payment_success(
    request: Request,
    session_id: str,
    user=Depends(get_logged_in_user),
):

    db: Session = SessionLocal()

    # 回跳後仍需有 Stripe 私鑰，才能向 Stripe 查詢 Session
    stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
    if not stripe_secret_key:
        set_flash(request, "Stripe is not configured: set STRIPE_SECRET_KEY in .env", "error")
        return RedirectResponse("/my-bookings", status_code=303)

    stripe.api_key = stripe_secret_key

    try:
        # 向 Stripe 取回這次 checkout session 詳細資訊
        checkout_session = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        set_flash(request, "Payment session is invalid", "error")
        return RedirectResponse("/my-bookings", status_code=303)

    # 僅接受「已付款」狀態，其他狀態一律視為未完成
    if checkout_session.payment_status != "paid":
        set_flash(request, "Payment not completed", "error")
        return RedirectResponse("/my-bookings", status_code=303)

    # metadata 是建立 session 時寫入的追蹤資料
    metadata = checkout_session.metadata or {}
    booking_id = metadata.get("booking_id")
    user_id = metadata.get("user_id")

    # 驗證 metadata 完整性與使用者一致性，防止越權修改他人訂單
    if not booking_id or not user_id or int(user_id) != user["id"]:
        set_flash(request, "Payment verification failed", "error")
        return RedirectResponse("/my-bookings", status_code=303)

    # 再次以「訂單 + 使用者」雙條件查詢，確保資料一致
    booking = db.query(Booking).filter(
        Booking.id == int(booking_id),
        Booking.user_id == user["id"],
    ).first()

    if not booking:
        raise HTTPException(status_code=404)

    # 只有 active 需要改狀態；若已 paid 則不重複更新（冪等）
    if booking.status == "active":
        booking.status = "paid"
        db.commit()

    set_flash(request, "Payment successful", "info")
    return RedirectResponse("/my-bookings", status_code=303)
