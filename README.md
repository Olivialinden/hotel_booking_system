
---
# Morrow Hotel Booking System

## Overview
Morrow Hotel Booking System is a web application for managing hotel room reservations. It allows users to register, log in, view available rooms, and manage their bookings. Admins can manage rooms and bookings through a dedicated dashboard.

## User Flow

### User
1. Register an account
2. Log in
3. Browse available rooms
4. Filter rooms by check-in/check-out dates
5. Select a room and book
6. View and manage personal bookings (cancel, update)

### Admin
1. Log in to admin dashboard
2. Add, edit, or delete rooms
3. View all bookings
4. Manage user accounts and booking status

## Features

- User registration & login (session-based)
- View available rooms
- Filter rooms by check-in/check-out dates
- View and manage personal bookings
- Admin dashboard for room management
- Add, edit, and delete rooms
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

1. Clone the repository and navigate to the project directory.
2. Create and activate a Python virtual environment.
3. Install dependencies with `pip install -r requirements.txt`.
4. Configure your database settings in `.env` or the backend config.
5. Run the backend server:
   ```
   uvicorn backend.main:app --reload
   ```
6. Access the site at `http://localhost:8000`.

## Mobile & Tablet Adaptation

To make the website display well on mobile and tablet devices:
- Add the viewport meta tag in the HTML <head>:
  `<meta name="viewport" content="width=device-width, initial-scale=1">`
- Use responsive CSS (such as @media queries)
- Optimize layouts: avoid fixed widths, use percentage or flex layouts
- Test all pages on different devices

It is recommended to use responsive frameworks like Bootstrap or Tailwind CSS to improve mobile experience.

