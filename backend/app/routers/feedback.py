"""用户反馈路由"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.services.user_service import (
    submit_feedback,
    list_feedback,
    review_feedback,
)

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


class FeedbackSubmit(BaseModel):
    user_id: str
    type: str = "other"  # bug / feature / improvement / other
    title: str
    content: str


class FeedbackReview(BaseModel):
    fb_id: str
    status: str  # reviewed / closed
    reply: str = ""


@router.post("/submit")
async def submit(request: FeedbackSubmit):
    """用户提交反馈"""
    try:
        fb = submit_feedback(request.user_id, request.type, request.title, request.content)
        return {"success": True, "feedback": fb, "message": "反馈已提交，感谢您的建议！"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list")
async def get_feedback(status: Optional[str] = Query(None)):
    """获取反馈列表（管理员）"""
    items = list_feedback(status)
    return {"success": True, "items": items, "total": len(items)}


@router.get("/pending-count")
async def pending_count():
    """获取待处理反馈数"""
    items = list_feedback("pending")
    return {"success": True, "count": len(items)}


@router.post("/review")
async def review(request: FeedbackReview):
    """管理员处理反馈"""
    try:
        fb = review_feedback(request.fb_id, request.status, request.reply)
        return {"success": True, "feedback": fb, "message": "反馈已处理"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
