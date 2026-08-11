import os
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config import OUTPUT_DIR
from app.services.rag_service import list_documents
from app.services.user_service import (
    get_all_users,
    ban_user,
    unban_user,
    get_admin_stats,
    update_user_info,
    ADMIN_EMAIL,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])

STATS_FILE = os.path.join(OUTPUT_DIR, "..", "stats.json")


def _load_stats() -> dict:
    if not os.path.exists(STATS_FILE):
        return {"conversations": [], "generations": [], "activeUsers": 1}
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"conversations": [], "generations": [], "activeUsers": 1}


def _save_stats(stats: dict):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def record_conversation():
    stats = _load_stats()
    stats["conversations"].append(datetime.now().isoformat())
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    stats["conversations"] = [t for t in stats["conversations"] if t > cutoff]
    _save_stats(stats)


def record_generation():
    stats = _load_stats()
    stats["generations"].append(datetime.now().isoformat())
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    stats["generations"] = [t for t in stats["generations"] if t > cutoff]
    _save_stats(stats)


@router.get("/stats")
async def get_stats():
    """获取管理后台完整统计数据"""
    stats = _load_stats()
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    today_conv = sum(1 for t in stats["conversations"] if t.startswith(today_str))
    yesterday_conv = sum(1 for t in stats["conversations"] if t.startswith(yesterday_str))
    today_gen = sum(1 for t in stats["generations"] if t.startswith(today_str))

    vs_yesterday = 0
    if yesterday_conv > 0:
        vs_yesterday = round((today_conv - yesterday_conv) / yesterday_conv * 100)
    elif today_conv > 0:
        vs_yesterday = 100

    docs = list_documents()
    total_chunks = sum(d.get("chunk_count", 0) for d in docs)

    # 最近活动
    activities = []
    all_events = []
    for t in stats.get("conversations", [])[-20:]:
        all_events.append(("对话交互", t))
    for t in stats.get("generations", [])[-20:]:
        all_events.append(("课件生成", t))
    all_events.sort(key=lambda x: x[1], reverse=True)

    for event_type, t in all_events[:15]:
        try:
            dt = datetime.fromisoformat(t)
            time_str = dt.strftime("%m-%d %H:%M")
        except Exception:
            time_str = t[:16]
        activities.append({"text": event_type, "time": time_str})

    # 汇总统计
    dashboard = get_admin_stats()

    return {
        **dashboard,
        "todayConversations": today_conv,
        "vsYesterday": max(vs_yesterday, 0),
        "totalDocuments": len(docs),
        "totalChunks": total_chunks,
        "todayGenerations": today_gen,
        "recentActivities": activities,
    }


# ===== 用户管理 =====

class BanRequest(BaseModel):
    user_id: str
    reason: str


class UpdateUserRequest(BaseModel):
    user_id: str
    username: str = ""
    password: str = ""


@router.get("/users")
async def list_users():
    """获取所有用户列表（管理员）"""
    users = get_all_users()
    return {"success": True, "users": users, "total": len(users), "admin_email": ADMIN_EMAIL}


@router.post("/ban-user")
async def ban_user_endpoint(request: BanRequest):
    """封禁用户"""
    if not request.reason.strip():
        raise HTTPException(status_code=400, detail="封禁理由不能为空")
    try:
        user = ban_user(request.user_id, request.reason)
        return {"success": True, "user": user, "message": f"用户 {user['username']} 已被封禁"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/unban-user/{user_id}")
async def unban_user_endpoint(user_id: str):
    """解封用户"""
    try:
        user = unban_user(user_id)
        return {"success": True, "user": user, "message": f"用户 {user['username']} 已解封"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update-user")
async def update_user(request: UpdateUserRequest):
    """管理员修改用户信息"""
    try:
        user = update_user_info(request.user_id, {
            "username": request.username,
            "password": request.password,
        })
        return {"success": True, "user": user, "message": "用户信息已更新"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
