"""通知路由：用户消息/通知管理"""
from fastapi import APIRouter, HTTPException
from app.services.user_service import (
    get_user_notifications,
    mark_notification_read,
    mark_all_read,
    get_unread_count,
)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/{user_id}")
async def list_notifications(user_id: str, unread_only: bool = False):
    """获取用户通知列表"""
    notifications = get_user_notifications(user_id, unread_only=unread_only)
    return {"success": True, "notifications": notifications, "total": len(notifications)}


@router.post("/read/{nid}")
async def read_notification(nid: str):
    """标记单条通知为已读"""
    mark_notification_read(nid)
    return {"success": True, "message": "已标记为已读"}


@router.post("/read-all/{user_id}")
async def read_all_notifications(user_id: str):
    """标记所有通知为已读"""
    mark_all_read(user_id)
    return {"success": True, "message": "已全部标为已读"}


@router.get("/unread-count/{user_id}")
async def unread_count(user_id: str):
    """获取未读通知数量"""
    count = get_unread_count(user_id)
    return {"success": True, "count": count}
