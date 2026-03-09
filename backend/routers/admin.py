import os
from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from backend.database import SessionLocal
from backend.models import Room, Booking
from backend.dependencies import require_admin_user, pop_flash, set_flash
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

router = APIRouter()

@router.get("/admin")
def admin_page(request: Request, user=Depends(require_admin_user)):
    db = SessionLocal()
    rooms = db.query(Room).all()
    bookings = db.query(Booking).all()
    flash = pop_flash(request)
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "rooms": rooms,
            "bookings": bookings,
            "flash": flash,
        }
    )

@router.post("/admin/add-room")
def add_room(
    request: Request,
    name: str = Form(...),
    amenities: str = Form(...),
    price: int = Form(...),
    user=Depends(require_admin_user)
):   
    db = SessionLocal()   
    room = Room(
        name=name,
        amenities=amenities,
        price=price
    )
    db.add(room)
    db.commit()  
    return RedirectResponse("/admin", status_code=303)


@router.post("/admin/delete-room")
def delete_room(
    request: Request,
    room_id: int = Form(...),
    user=Depends(require_admin_user)
):
    db = SessionLocal()

    # Check if there are any active bookings
    active_booking = db.query(Booking).filter(
        Booking.room_id == room_id,
        Booking.status.in_(["active", "paid"])
    ).first()

    # If active booking exists, prevent deletion and return to admin page
    if active_booking:
        set_flash(
            request,
            "Cannot delete room! There are active bookings for this room.",
            "error"
        )
        return RedirectResponse("/admin", status_code=303)

    room = db.query(Room).filter(Room.id == room_id).first()

    if room:  
        db.query(Booking).filter(Booking.room_id == room_id).delete()
        db.delete(room)    
        db.commit()
    return RedirectResponse("/admin", status_code=303)
