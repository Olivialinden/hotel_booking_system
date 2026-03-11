from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.database import get_db  
from backend.models import Booking
from backend.dependencies import get_logged_in_user, set_flash
from datetime import date

router = APIRouter()

@router.post("/book")
def create_booking(
    request: Request,
    room_id: int = Form(...),
    check_in: date = Form(...),
    check_out: date = Form(...),
    db: Session = Depends(get_db),   
    user=Depends(get_logged_in_user),
):
   
    today = date.today()
    if check_in < today or check_out <= check_in:
        
        set_flash(request, "Invalid booking dates", "error")
    
        return RedirectResponse(
            "/",
            status_code=303
        )
  
    conflict = db.query(Booking).filter(
        and_(
            Booking.room_id == room_id,
            Booking.status.in_(["active", "paid"]),
            Booking.check_in < check_out,
            Booking.check_out > check_in,
        )
    ).first()
 
    if conflict:
        set_flash(
            request,
            "Room is not available for selected dates",
            "error"
        )
        return RedirectResponse("/", status_code=303)
 
    booking = Booking(
        user_id=user["id"],
        room_id=room_id,
        check_in=check_in,
        check_out=check_out
    )
    db.add(booking)
    db.commit() 
    return RedirectResponse("/my-bookings", status_code=303)


@router.post("/cancel-booking")
def cancel_booking(
    request: Request,
    booking_id: int = Form(...),
    db: Session = Depends(get_db),  
    user=Depends(get_logged_in_user),
):

    # users should only be able to cancel their own active bookings
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == user["id"],
        Booking.status == "active"
    ).first()

    
    if not booking:
        raise HTTPException(status_code=404)
    
    booking.status = "cancelled"
    db.commit()
    return RedirectResponse("/my-bookings", status_code=303)
