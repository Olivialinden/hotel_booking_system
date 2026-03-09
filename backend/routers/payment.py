import os
import stripe
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
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
   
    db = SessionLocal()
   
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == user["id"],
    ).first()

    if not booking:
       
        raise HTTPException(status_code=404)

    if booking.status != "active":
        # only active bookings can be paid   
        set_flash(request, "This booking cannot be paid", "error")
        return RedirectResponse("/my-bookings", status_code=303)


    stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
    if not stripe_secret_key:
        set_flash(request, "Stripe is not configured: set STRIPE_SECRET_KEY in .env", "error")
        return RedirectResponse("/my-bookings", status_code=303)
    
    stripe.api_key = stripe_secret_key

    app_base_url = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")

    stripe_currency = os.getenv("STRIPE_CURRENCY", "sek").lower() 
    
    stay_nights = (booking.check_out - booking.check_in).days
    
    if stay_nights <= 0:
        set_flash(request, "Invalid booking length", "error")
        return RedirectResponse("/my-bookings", status_code=303)

    # stripe needs amount in cents or öre  
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
    except Exception as e:
        print(f"Stripe error: {e}")
        # Any Stripe connection or API error, return to previous page with a  message
        set_flash(request, "Unable to start payment session", "error")
        return RedirectResponse("/my-bookings", status_code=303) 
    return RedirectResponse(checkout_session.url, status_code=303)


@router.get("/payment/success")
def payment_success(
    request: Request,
    session_id: str,
    user=Depends(get_logged_in_user),
):
    db = SessionLocal()
    stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
    if not stripe_secret_key:
        set_flash(request, "Stripe is not configured: set STRIPE_SECRET_KEY in .env", "error")
        return RedirectResponse("/my-bookings", status_code=303)

    stripe.api_key = stripe_secret_key

    try:
       
        checkout_session = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        set_flash(request, "Payment session is invalid", "error")
        return RedirectResponse("/my-bookings", status_code=303)

    
    if checkout_session.payment_status != "paid":
        set_flash(request, "Payment not completed", "error")
        return RedirectResponse("/my-bookings", status_code=303)
 
    metadata = checkout_session.metadata or {}
    booking_id = metadata.get("booking_id")
    user_id = metadata.get("user_id")

    # make sure it's the right user
    if not booking_id or not user_id or int(user_id) != user["id"]:
        set_flash(request, "Payment verification failed", "error")
        return RedirectResponse("/my-bookings", status_code=303)
 
    booking = db.query(Booking).filter(
        Booking.id == int(booking_id),
        Booking.user_id == user["id"],
    ).first()

    if not booking:
        raise HTTPException(status_code=404)

    # only process once — skip if already paid
    if booking.status == "active":
        booking.status = "paid"
        db.commit()

    set_flash(request, "Payment successful", "info")
    return RedirectResponse("/my-bookings", status_code=303)
