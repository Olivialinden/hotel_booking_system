from fastapi import Request, HTTPException

def get_logged_in_user(request: Request):
    current_user = request.session.get("user")
    if not current_user:
        # not logged in
        raise HTTPException(status_code=401)
    return current_user

def require_admin_user(request: Request):
    current_user = get_logged_in_user(request)

    if not current_user.get("is_admin"):
        # logged in, no permission
        raise HTTPException(status_code=403)
    return current_user

def set_flash(request: Request, message: str, level: str = "info"):
    request.session["flash"] = {
        "message": message,
        "level": level,
    }

def pop_flash(request: Request):
    return request.session.pop("flash", None)


