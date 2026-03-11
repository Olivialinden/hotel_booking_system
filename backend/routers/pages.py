import os
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from backend.database import get_db  
from backend.dependencies import get_logged_in_user, pop_flash
from backend.queries import (
    get_booked_room_ids,
    get_available_rooms,
    get_booked_rooms,
    get_bookings_by_user,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

router = APIRouter()

@router.get("/")
def show_home_page(
    request: Request,
    db: Session = Depends(get_db)  
):
   
    check_in = request.query_params.get("check_in")
    check_out = request.query_params.get("check_out")
  
    if check_in and check_out:
        booked_room_ids = get_booked_room_ids(db, check_in, check_out)
        # [(1,), (3,)] → [1, 3]
        booked_room_ids = [r[0] for r in booked_room_ids]
    else:
        booked_room_ids = []

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
    db: Session = Depends(get_db),  
    current_user=Depends(get_logged_in_user),
):
    
    all_bookings = get_bookings_by_user(db, current_user["id"])
    currency_code = os.getenv("STRIPE_CURRENCY", "sek").upper()
  
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
