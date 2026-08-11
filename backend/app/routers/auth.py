"""认证路由：注册、登录、用户信息"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.user_service import (
    create_user,
    authenticate_user,
    get_user,
    get_unread_count,
    ADMIN_EMAIL,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register")
async def register(request: RegisterRequest):
    """用户注册"""
    username = request.username.strip()
    password = request.password.strip()

    if not username or len(username) < 2:
        raise HTTPException(status_code=400, detail="用户名至少需要2个字符")
    if len(username) > 20:
        raise HTTPException(status_code=400, detail="用户名不能超过20个字符")
    if not password or len(password) < 3:
        raise HTTPException(status_code=400, detail="密码至少需要3个字符")
    if username.lower() == "admin":
        raise HTTPException(status_code=400, detail="该用户名不可用")

    try:
        user = create_user(username, password)
        return {"success": True, "user": user, "message": "注册成功"}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/login")
async def login(request: LoginRequest):
    """用户登录"""
    username = request.username.strip()
    password = request.password.strip()

    if not username or not password:
        raise HTTPException(status_code=400, detail="请输入用户名和密码")

    result = authenticate_user(username, password)

    if not result["success"]:
        if result.get("banned"):
            # 账户被封禁，返回 403 并携带封禁信息
            raise HTTPException(
                status_code=403,
                detail={
                    "reason": "account_banned",
                    "ban_reason": result.get("ban_reason", "您的账户已被管理员封禁"),
                    "banned_at": result.get("banned_at", ""),
                    "admin_email": result.get("admin_email", ADMIN_EMAIL),
                }
            )
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    return {"success": True, "user": result["user"], "message": "登录成功"}


@router.get("/user/{user_id}")
async def get_user_info(user_id: str):
    """获取用户信息"""
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    unread = get_unread_count(user_id)
    return {"success": True, "user": {**user, "unread_count": unread}}
