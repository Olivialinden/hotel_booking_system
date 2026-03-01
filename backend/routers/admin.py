import os
from fastapi import APIRouter, Request, Depends, Form
from backend.main import templates
from fastapi.responses import RedirectResponse
from backend.database import SessionLocal
from backend.models import Room, Booking
from backend.dependencies import require_admin_user, pop_flash, set_flash

# 建立「管理後台」路由收集器
router = APIRouter()

# 建立模板渲染器：指定 HTML 模板目錄為 templates/



@router.get("/admin")
def admin_page(request: Request, user=Depends(require_admin_user)):
    """
    管理頁面（GET /admin）

    功能：
    - 顯示房型列表
    - 顯示訂單列表
    - 顯示一次性提示訊息（flash）

    權限：
    - 透過 Depends(require_admin_user) 限制只有管理員可進入
    """

    # 建立資料庫連線
    db = SessionLocal()

    # 查全部房間資料
    rooms = db.query(Room).all()

    # 查全部訂單資料
    bookings = db.query(Booking).all()

    # 取出 flash 訊息（通常讀一次就會清空）
    flash = pop_flash(request)

    # 渲染 admin.html 並把資料傳給模板
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "rooms": rooms,
            "bookings": bookings,
            "flash": flash,
        }
    )

@router.post("/admin/add-room")
def add_room(
    request: Request,
    name: str = Form(...),
    amenities: str = Form(...),
    price: int = Form(...),
    user=Depends(require_admin_user)
):
    """
    新增房間（POST /admin/add-room）

    參數來源：
    - name / amenities / price：來自 HTML 表單 Form

    權限：
    - 僅管理員可操作
    """

    # 建立資料庫連線
    db = SessionLocal()

    # 建立 Room ORM 物件
    room = Room(
        name=name,
        amenities=amenities,
        price=price
    )

    # 寫入資料庫並提交
    db.add(room)
    db.commit()

    # 303 重新導向回 /admin（避免重複送出表單）
    return RedirectResponse("/admin", status_code=303)


@router.post("/admin/delete-room")
def delete_room(
    request: Request,
    room_id: int = Form(...),
    user=Depends(require_admin_user)
):
    """
    刪除房間（POST /admin/delete-room）

    刪除規則：
    1) 若此房間存在 active 訂單，禁止刪除，並顯示錯誤提示
    2) 若無 active 訂單：
       - 先刪除此房間相關 Booking（避免外鍵衝突）
       - 再刪除房間本身

    權限：
    - 僅管理員可操作
    """

    # 建立資料庫連線
    db = SessionLocal()

    # 先檢查是否有「進行中(active)」訂單
    active_booking = db.query(Booking).filter(
        Booking.room_id == room_id,
        Booking.status.in_(["active", "paid"])
    ).first()

    # 若有 active 訂單，阻止刪除並回管理頁
    # "error" 是消息类型，前端可按类型显示红色提示
    if active_booking:
        set_flash(
            request,
            "Cannot delete room! There are active bookings for this room.",
            "error"
        )
        return RedirectResponse("/admin", status_code=303)

    # 查詢要刪除的房間
    room = db.query(Room).filter(Room.id == room_id).first()

    # 找到房間才執行刪除
    if room:
        # 先刪除關聯訂單
        db.query(Booking).filter(Booking.room_id == room_id).delete()

        # 再刪除房間
        db.delete(room)

        # 提交交易
        db.commit()

    # 最後回管理頁
    return RedirectResponse("/admin", status_code=303)
