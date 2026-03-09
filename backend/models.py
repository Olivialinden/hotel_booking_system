from backend.database import Base
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base): 
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)

    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)

    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    room = relationship("Room")
