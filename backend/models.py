
from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

# 导入这个 Base，是为了让 SQLAlchemy 知道这些 class 是数据库模型
class User(Base):#  继承 Base
  
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_name = Column(String(255))
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)


class Room(Base):
  
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)
    amenities = Column(String(100))
    price = Column(Integer)


class Booking(Base):

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)

    # 外键：属于哪个用户
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 外键：预订哪个房间
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)

    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)

    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    # ORM 关系（方便通过 booking.user / booking.room 访问）
    user = relationship("User")
    room = relationship("Room")
