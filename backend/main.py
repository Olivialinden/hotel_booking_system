import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from backend.database import Base, engine
from dotenv import load_dotenv
from backend.routers import pages, auth, bookings, admin, payment
from fastapi.templating import Jinja2Templates
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


Base.metadata.create_all(bind=engine)

app = FastAPI()


# Add Session middleware (for login state)
# "hotel_booking_session_key_2026_v1" Hardcoded for homework
app.add_middleware(
    SessionMiddleware,
    secret_key="hotel_booking_session_key_2026_v1",  
)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(bookings.router)
app.include_router(payment.router)
app.include_router(admin.router)
