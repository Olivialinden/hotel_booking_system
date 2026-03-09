# Morrow Hotel Booking System

<img src="backend/static/images/WebsiteScreenshot.jpg" width="800">

## 🔗 Live Demo

Check it out here: [hotelbookingsystem-production-1d49.up.railway.app](https://hotelbookingsystem-production-1d49.up.railway.app)

## What is this?

A hotel booking website where users can register, browse rooms, and make reservations. Admins can manage rooms and view all bookings.

Built with Python/FastAPI.

## Features

- User registration & login
- Browse and filter rooms by date
- Make/cancel bookings
- Pay for bookings
- Admin dashboard (add/delete rooms, view all bookings)
- No double-booking the same room

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, MySQL/MariaDB
- **Frontend:** Jinja2, HTML/CSS

## How to run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your database and app info:
   ```
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=hotel_booking
   SECRET_KEY=9f3b6e2a7c4d8f1a5b9c0d3e6f7a8b1c
   STRIPE_SECRET_KEY=sk_test_51abcDEFghijkLMNOP
   STRIPE_CURRENCY=sek
   APP_BASE_URL=http://localhost:8000
   DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/hotel_booking
   ```

3. Start the server:
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

4. Go to `http://localhost:8000`

That's it!