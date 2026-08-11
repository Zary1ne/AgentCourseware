"""开源社区路由：课件上传、列表、审核"""
import os
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from app.services.user_service import (
    upload_courseware,
    list_approved_courseware,
    list_pending_courseware,
    review_courseware,
    get_user_courseware,
)

router = APIRouter(prefix="/api/community", tags=["community"])


class ReviewRequest(BaseModel):
    cw_id: str
    approved: bool
    comment: str = ""


@router.post("/upload")
async def upload(
    user_id: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form("其他"),
    tags_str: str = Form(""),
    file: UploadFile = File(None),
):
    """上传课件到开源社区（必须包含文件）"""
    if not title.strip():
        raise HTTPException(status_code=400, detail="课件标题不能为空")

    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="必须上传课件文件")

    # 读取文件内容
    try:
        file_bytes = await file.read()
        if not file_bytes or len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="上传的文件为空")
    except Exception:
        raise HTTPException(status_code=400, detail="文件读取失败")

    # 限制文件大小 (50MB)
    if len(file_bytes) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过50MB")

    # 解析标签
    tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []

    try:
        cw = upload_courseware(
            user_id=user_id,
            data={
                "title": title.strip(),
                "description": description.strip() if description else "",
                "category": category,
                "tags": tags,
            },
            file_bytes=file_bytes,
            filename=file.filename,
        )
        return {"success": True, "courseware": cw, "message": "上传成功，等待管理员审核"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_courseware(category: Optional[str] = Query(None)):
    """获取已审核通过的课件列表"""
    items = list_approved_courseware(category)
    return {"success": True, "items": items, "total": len(items)}


@router.get("/my/{user_id}")
async def my_courseware(user_id: str):
    """获取某用户上传的课件"""
    items = get_user_courseware(user_id)
    return {"success": True, "items": items, "total": len(items)}


@router.get("/file/{cw_id}")
async def get_courseware_file(cw_id: str):
    """获取课件文件（管理员查看用）"""
    from app.services.user_service import _load_json, COURSEWARE_FILE
    from fastapi.responses import FileResponse

    coursewares = _load_json(COURSEWARE_FILE)
    cw = coursewares.get(cw_id)
    if not cw:
        raise HTTPException(status_code=404, detail="课件不存在")

    files = cw.get("files", {})
    saved_name = files.get("saved_name", "")
    if not saved_name:
        raise HTTPException(status_code=404, detail="文件不存在")

    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "community")
    file_path = os.path.join(uploads_dir, saved_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件已被删除")

    return FileResponse(file_path, filename=files.get("filename", saved_name))


# ===== 管理员接口 =====

@router.get("/pending")
async def pending_courseware(status: Optional[str] = Query("pending")):
    """获取课件列表（管理员）。status=pending 仅待审核，status=all 全部记录"""
    items = list_pending_courseware(status)
    return {"success": True, "items": items, "total": len(items)}


@router.post("/review")
async def review(request: ReviewRequest):
    """审核课件（管理员）。拒绝时必须填写理由"""
    if not request.approved and not request.comment.strip():
        raise HTTPException(status_code=400, detail="拒绝课件时必须填写拒绝理由")

    try:
        cw = review_courseware(request.cw_id, request.approved, request.comment)
        return {"success": True, "courseware": cw, "message": "审核完成"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
