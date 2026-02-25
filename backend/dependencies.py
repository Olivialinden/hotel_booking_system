
"""
dependencies.py
----------------
这个文件专门放【可复用的依赖函数】：

"""

from fastapi import Request, HTTPException




def get_logged_in_user(request: Request):

 
    current_user = request.session.get("user")

    if not current_user:
        # 401 = 未认证（未登录）
        raise HTTPException(status_code=401)

    return current_user


def require_admin_user(request: Request):

    current_user = get_logged_in_user(request)

    if not current_user.get("is_admin"):
        # 403 = 已登录，但没有权限
        raise HTTPException(status_code=403)

    return current_user




def set_flash(request: Request, message: str, level: str = "info"):
    request.session["flash"] = {
        "message": message,
        "level": level,
    }


def pop_flash(request: Request):
    return request.session.pop("flash", None)


