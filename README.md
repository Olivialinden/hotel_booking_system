
---
# Morrow Hotel Booking System

## Project Preview

<img src="backend/static/images/WebsiteScreenshot.jpg" width="800">

## Overview
Morrow Hotel Booking System is a web application for managing hotel room reservations. It allows users to register, log in, view available rooms, and manage their bookings. Admins can manage rooms and review bookings through a dedicated dashboard.

## User Flow

### User
1. Register an account
2. Log in
3. Browse available rooms
4. Filter rooms by check-in/check-out dates
5. Select a room and book
6. View and manage personal bookings (cancel, pay)

### Admin
1. Log in to admin dashboard
2. Add or delete rooms
3. View all bookings


## Features

- User registration & login (session-based)
- View available rooms
- Filter rooms by check-in/check-out dates
- View and manage personal bookings
- Admin dashboard for room management
- Add and delete rooms
- View all bookings

### Booking Rules
- No overlapping bookings for the same room
- Check-out must be after check-in

## Tech Stack

**Backend:**
- FastAPI
- SQLAlchemy ORM
- MariaDB / MySQL
- Jinja2 Templates
- Starlette Sessions
- uvicorn

**Frontend:**
- Jinja2 HTML templates
- CSS (custom or framework-based)

## Requirements

Install all dependencies listed in requirements.txt:
```
fastapi
uvicorn
SQLAlchemy
Jinja2
passlib[bcrypt]
python-dotenv
python-multipart
email-validator
itsdangerous
PyMySQL
```
Install with:
```
pip install -r requirements.txt
```


## Setup & Usage

1. Clone the repository and make sure you are in the project root directory (which contains backend/, static/, requirements.txt, etc.).
2. Create and activate a Python virtual environment.
3. Install dependencies:
  ```
  pip install -r requirements.txt
  ```
4. In the project root, create a `.env` file and configure your database and Stripe keys, for example:
  ```
  STRIPE_SECRET_KEY=sk_test_xxx
  STRIPE_CURRENCY=sek
  # Other database-related settings
  ```
5. For local development/testing, **you must run uvicorn from the project root**:
  ```
  uvicorn backend.main:app --reload
  ```
  - This ensures static files (/static/) and template paths work correctly.
  - For production, use the command in the Procfile.
6. Visit `http://localhost:8000` to view the site.

### Notes
- **Static files**: All CSS/JS/images should be accessed via the `/static/` path. In templates, use:
  ```html
  <link rel="stylesheet" href="{{ url_for('static', path='css/style.css') }}">
  ```
- **Database**: If using SQLite, it is recommended to use an absolute path, or ensure your working directory and database file are at the same level.
- **Module imports**: All Python files use `from backend.xxx import ...` absolute imports, compatible with `uvicorn backend.main:app` startup.
- **If CSS does not work or database connection fails, first check your working directory, static file paths, and .env configuration.**



