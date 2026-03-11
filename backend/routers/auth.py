import re
from urllib.parse import quote
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from backend.database import get_db  
from backend.security import generate_password_hash, check_password
from backend.queries import get_user_by_email, create_user

router = APIRouter()

def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple[bool, str]:
  
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isdigit() for c in password):
        return False, "Password must include at least one number"
    if not any(c.isalpha() for c in password):
        return False, "Password must include at least one letter"
    return True, ""


@router.post("/register")
def handle_user_registration(
    user_name: str = Form(None),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db) 
):

    if not validate_email(email):
        safe_error = quote("Invalid email format")
        return RedirectResponse(f"/register?has_error={safe_error}", status_code=303)
 
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        safe_error = quote(error_msg)
        return RedirectResponse(f"/register?has_error={safe_error}", status_code=303)
    # emails are unique identifiers，duplicate accounts must be rejected
    if get_user_by_email(db, email):
        return RedirectResponse("/register?email_exists=1", status_code=303)

    # If user does not exist, hash password and create user
    hashed_password = generate_password_hash(password)
    create_user(db, email, hashed_password, user_name)
    return RedirectResponse("/login?registration_success=1", status_code=303)


@router.post("/login")
def handle_user_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db) 
):

    user = get_user_by_email(db, email)
 
    if not user or not check_password(password, user.password):
        return RedirectResponse("/login?has_error=1", status_code=303)
  
    request.session["user"] = {
        "id": user.id,
        "user_name": user.user_name,
        "email": user.email,
        "is_admin": user.is_admin,
    }

    return RedirectResponse("/", status_code=303)

@router.get("/logout")
def handle_user_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
