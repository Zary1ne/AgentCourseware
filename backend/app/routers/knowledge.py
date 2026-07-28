import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Query
from app.models.schemas import KnowledgeQuery, KnowledgeUpdate
from app.services.rag_service import (
    add_document, search_knowledge, remove_document,
    list_documents, load_knowledge_base_dir,
    get_document_content, update_document_content,
)
from app.services.file_parser import parse_file, get_file_type
from app.config import UPLOAD_DIR

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), task_id: str = Form("default")):
    """上传文件到知识库（按任务隔离）"""
    file_type = get_file_type(file.filename)
    if not file_type:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.filename}")

    file_id = uuid.uuid4().hex[:8]
    safe_filename = f"{file_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, safe_filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    parse_result = parse_file(filepath, file.filename)
    kb_result = add_document(filepath, file.filename, task_id=task_id)

    return {
        "success": True,
        "file_id": file_id,
        "filename": file.filename,
        "file_type": file_type,
        "size": len(content),
        "parsed_content": parse_result["content"] if parse_result["success"] else None,
        "knowledge_base": kb_result,
    }


@router.post("/search")
async def search(query: KnowledgeQuery):
    """搜索知识库（支持按任务过滤）"""
    results = search_knowledge(query.query, query.top_k, task_id=query.task_id)
    return {"success": True, "query": query.query, "results": results}


@router.get("/documents")
async def get_documents(task_id: str = Query(None)):
    """获取知识库文档列表（支持按任务过滤）"""
    docs = list_documents(task_id=task_id)
    return {"success": True, "documents": docs, "total": len(docs)}


@router.get("/documents/{doc_id}")
async def get_document(doc_id: str, task_id: str = Query(None)):
    """查看知识库文档内容（支持按任务过滤）"""
    result = get_document_content(doc_id, task_id=task_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.put("/documents/{doc_id}")
async def update_document(doc_id: str, data: KnowledgeUpdate, task_id: str = Query(None)):
    """更新知识库文档内容（支持按任务过滤）"""
    result = update_document_content(doc_id, data.content, task_id=task_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, task_id: str = Query(None)):
    """删除知识库文档（支持按任务过滤）"""
    result = remove_document(doc_id, task_id=task_id)
    return result


@router.post("/reload")
async def reload_knowledge_base():
    """重新加载知识库目录"""
    result = load_knowledge_base_dir()
    return result


@router.post("/parse-file")
async def parse_uploaded_file(file: UploadFile = File(...)):
    """仅解析文件（不入库），用于参考资料预览"""
    file_id = uuid.uuid4().hex[:8]
    safe_filename = f"temp_{file_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, safe_filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    parse_result = parse_file(filepath, file.filename)

    try:
        os.remove(filepath)
    except Exception:
        pass

    return {
        "success": parse_result["success"],
        "filename": file.filename,
        "file_type": get_file_type(file.filename),
        "content": parse_result["content"][:3000] if parse_result["success"] else parse_result["content"],
    }
