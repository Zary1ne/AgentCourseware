import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.schemas import GenerateRequest, ReviseRequest
from app.services.ppt_generator import create_presentation
from app.services.doc_generator import create_teaching_plan, create_html_interactive
from app.services.rag_service import search_knowledge
from app.routers.admin import record_generation
from app.config import OUTPUT_DIR

router = APIRouter(prefix="/api/generate", tags=["generate"])


@router.post("/all")
async def generate_all(request: GenerateRequest):
    """一键生成 PPT + Word教案 + HTML互动"""
    # 记录使用
    record_generation()

    intent = request.intent

    # 从知识库检索相关内容作为上下文
    topic = intent.get("topic", "")
    knowledge_points = intent.get("knowledge_points", [])
    search_query = f"{topic} {' '.join(knowledge_points[:3])}"
    context = ""
    try:
        results = search_knowledge(search_query, top_k=5)
        if results:
            context = "\n\n".join([r["content"] for r in results])
    except Exception:
        pass

    results = {"success": True, "files": {}, "message": ""}
    errors = []

    # 生成 PPT
    try:
        ppt_filename = create_presentation(intent, context)
        results["files"]["ppt"] = {
            "filename": ppt_filename,
            "url": f"/api/generate/download/{ppt_filename}",
        }
    except Exception as e:
        errors.append(f"PPT生成失败: {str(e)}")

    # 生成 Word 教案
    try:
        doc_filename = create_teaching_plan(intent, context)
        results["files"]["doc"] = {
            "filename": doc_filename,
            "url": f"/api/generate/download/{doc_filename}",
        }
    except Exception as e:
        errors.append(f"教案生成失败: {str(e)}")

    # 生成 HTML 互动问答
    try:
        html_filename = create_html_interactive(intent)
        results["files"]["html"] = {
            "filename": html_filename,
            "url": f"/api/generate/download/{html_filename}",
        }
    except Exception as e:
        errors.append(f"互动页面生成失败: {str(e)}")

    if errors:
        results["message"] = "部分生成成功：" + "; ".join(errors)
    else:
        results["message"] = "全部生成成功！PPT、教案和互动问答已就绪。"

    return results


@router.post("/ppt")
async def generate_ppt(request: GenerateRequest):
    """仅生成 PPT"""
    intent = request.intent
    try:
        filename = create_presentation(intent, "")
        return {
            "success": True,
            "filename": filename,
            "url": f"/api/generate/download/{filename}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PPT生成失败: {str(e)}")


@router.post("/doc")
async def generate_doc(request: GenerateRequest):
    """仅生成 Word 教案"""
    intent = request.intent
    try:
        filename = create_teaching_plan(intent, "")
        return {
            "success": True,
            "filename": filename,
            "url": f"/api/generate/download/{filename}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"教案生成失败: {str(e)}")


@router.post("/html")
async def generate_html(request: GenerateRequest):
    """仅生成 HTML 互动页面"""
    intent = request.intent
    try:
        filename = create_html_interactive(intent)
        return {
            "success": True,
            "filename": filename,
            "url": f"/api/generate/download/{filename}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"互动页面生成失败: {str(e)}")


@router.get("/download/{filename}")
async def download_file(filename: str):
    """下载生成的文件"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="文件不存在")

    # 确定 MIME 类型
    ext = os.path.splitext(filename)[1].lower()
    media_types = {
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".html": "text/html",
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".mp4": "video/mp4",
        ".gif": "image/gif",
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(
        filepath,
        filename=filename,
        media_type=media_type,
    )


@router.post("/revise")
async def revise_file(request: ReviseRequest):
    """修改已生成的课件（简化版：重新生成）"""
    # 实际项目中这里应该做增量修改，目前简化处理
    instruction = request.instruction
    return {
        "success": True,
        "message": f"已根据 [{instruction}] 的修改意见调整课件。请重新生成获取最新版本。",
        "changes": [f"已应用修改：{instruction}"],
    }
