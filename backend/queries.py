from backend.database import SessionLocal
from backend.models import User, Room, Booking
# User related queries

def get_user_by_email(db, email: str): 
    return db.query(User).filter(User.email == email).first()


def create_user(db, email: str, hashed_password: str, user_name: str | None = None):
    new_user = User(
        user_name=user_name,
        email=email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_booked_room_ids(db, check_in, check_out): 
    return db.query(Booking.room_id).filter(
        Booking.status.in_(["active", "paid"]),
        Booking.check_in < check_out,
        Booking.check_out > check_in
    ).all()


def get_available_rooms(db, booked_room_ids):
    return db.query(Room).filter(
        ~Room.id.in_(booked_room_ids)
    ).all()


def get_booked_rooms(db, booked_room_ids):
    return db.query(Room).filter(
        Room.id.in_(booked_room_ids)
    ).all()


def get_bookings_by_user(db, user_id: int):
    return db.query(Booking).filter(
        Booking.user_id == user_id
    ).all()
