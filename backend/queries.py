"""
queries.py
------------
这个文件专门负责数据库操作：
- 查数据
- 新增数据
- 不处理业务逻辑
- 不处理 HTTP / 页面 / session

规则：
只要看到 db.query，就应该在这个文件里
"""

from models import User, Room, Booking



# User 相关查询


def get_user_by_email(db, email: str):
  
    return db.query(User).filter(User.email == email).first()


def create_user(db, email: str, hashed_password: str, user_name: str | None = None):
 
    # 即将写入数据库的对象
    new_user = User(
        user_name=user_name,
        email=email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



# Booking / Room 相关查询


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
