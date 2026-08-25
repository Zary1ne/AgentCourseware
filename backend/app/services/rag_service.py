import os
import json
import re
from typing import List
from app.config import KNOWLEDGE_BASE_DIR
from app.services.file_parser import parse_file
from app.services.chroma_store import (
    _get_collection,
    _where_task,
    _tokenize,
)

# 旧向量存储路径（用于一次性迁移）
LEGACY_STORE_PATH = os.path.join(os.path.dirname(KNOWLEDGE_BASE_DIR), "backend", "vector_store")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """将文本分割成块"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if end < len(text):
            for sep in ["\n\n", "\n", "。", "！", "？", ".", "!", "?"]:
                last_sep = chunk.rfind(sep)
                if last_sep > chunk_size // 2:
                    end = start + last_sep + 1
                    chunk = text[start:end]
                    break
        chunks.append(chunk.strip())
        start = end - overlap if end - overlap > start else end
    return [c for c in chunks if c]


def _generate_summary_and_tags(content: str) -> dict:
    """调用 LLM 生成文档教学摘要、知识点标签和难度评级（带兜底）"""
    fallback_summary = (content[:80].replace("\n", " ").strip() + "…") if content else ""
    try:
        from app.services.llm_service import generate_content
        sample = content[:1500]
        prompt = (
            "请阅读以下教学资料，生成：\n"
            "1. 一句话教学摘要（不超过50字，概括核心教学内容）\n"
            "2. 3-5个知识点标签（简短关键词）\n"
            "3. 难度评级，从以下三个值中选一个：\n"
            '  "基础"：入门概念、无需前置知识、适合初学者\n'
            '  "进阶"：常规教学内容、需要一定基础、适合中等水平学生\n'
            '  "拓展"：深度分析、抽象概念、适合拔高或竞赛准备\n\n'
            "严格按JSON格式输出，不要markdown标记：\n"
            '{"summary": "摘要", "tags": ["标签1", "标签2", "标签3"], "difficulty": "基础"}'
        )
        raw = generate_content(prompt, context=sample)
        raw = raw.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        data = json.loads(raw.strip())
        summary = str(data.get("summary", "")).strip()
        tags = data.get("tags", [])
        if not isinstance(tags, list):
            tags = [t.strip() for t in str(tags).replace("、", ",").split(",") if t.strip()]
        tags = [str(t).strip()[:12] for t in tags if str(t).strip()][:5]
        if not summary:
            summary = fallback_summary
        difficulty = data.get("difficulty", "进阶")
        if difficulty not in ("基础", "进阶", "拓展"):
            difficulty = "进阶"
        return {"summary": summary, "tags": tags, "difficulty": difficulty}
    except Exception as e:
        print(f"[rag_service] 摘要标签生成失败，使用兜底: {e}")
        return {"summary": fallback_summary, "tags": [], "difficulty": "进阶"}


# ===== 旧向量存储迁移（一次性） =====
def _migrate_legacy_store():
    """若 Chroma 为空且存在旧 store.json，则把旧文档重新嵌入并导入。"""
    try:
        col = _get_collection()
        if col.count() > 0:
            return
        data_path = os.path.join(LEGACY_STORE_PATH, "store.json")
        if not os.path.exists(data_path):
            return
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        legacy_docs = data.get("documents", [])
        if not legacy_docs:
            return
        ids, docs, metas = [], [], []
        for d in legacy_docs:
            tid = d.get("task_id", "default")
            meta = {
                "task_id": tid,
                "source": d.get("source", "unknown"),
                "chunk_index": int(d.get("chunk_index", 0)),
                "summary": d.get("summary", "") or "",
                "tags": json.dumps(d.get("tags", []), ensure_ascii=False),
                "difficulty": d.get("difficulty", "") or "",
            }
            ids.append(d.get("id", f"legacy_{len(ids)}"))
            docs.append(d.get("content", ""))
            metas.append(meta)
        if ids:
            col.add(ids=ids, documents=docs, metadatas=metas)
            print(f"[rag_service] 已从旧 store.json 迁移 {len(ids)} 个文本块到 Chroma")
    except Exception as e:
        print(f"[rag_service] 旧数据迁移失败（可忽略）: {e}")


# 对外 API ============================================================

def add_document(filepath: str, filename: str, task_id: str = "default") -> dict:
    """向知识库添加文档（支持按任务隔离）"""
    parse_result = parse_file(filepath, filename)
    if not parse_result["success"]:
        return {"success": False, "message": parse_result["content"], "chunks": 0}

    content = parse_result["content"]
    chunks = chunk_text(content)
    if not chunks:
        return {"success": False, "message": "无法从文件中提取有效文本", "chunks": 0}

    try:
        col = _get_collection()
        doc_id_base = os.path.splitext(filename)[0].replace(" ", "_")
        meta = _generate_summary_and_tags(content)

        ids, docs, metas = [], [], []
        for i, chunk in enumerate(chunks):
            ids.append(f"{doc_id_base}_{i}")
            docs.append(chunk)
            metas.append({
                "task_id": task_id,
                "source": filename,
                "chunk_index": i,
                "summary": meta["summary"] if i == 0 else "",
                "tags": json.dumps(meta["tags"], ensure_ascii=False) if i == 0 else "",
                "difficulty": meta["difficulty"] if i == 0 else "",
            })

        # 先删同 doc_id 的旧块（避免重复）
        try:
            col.delete(where={"source": filename})
        except Exception:
            pass
        col.add(ids=ids, documents=docs, metadatas=metas)

        return {
            "success": True,
            "message": f"成功添加文档 '{filename}'，共 {len(chunks)} 个文本块",
            "chunks": len(chunks),
            "doc_id": doc_id_base,
            "summary": meta["summary"],
            "tags": meta["tags"],
            "difficulty": meta["difficulty"],
        }
    except Exception as e:
        return {"success": False, "message": f"向量化失败: {str(e)}", "chunks": 0}


def search_knowledge(query: str, top_k: int = 5, task_id: str = None) -> List[dict]:
    """搜索知识库（支持按任务过滤）"""
    try:
        col = _get_collection()
        if col.count() == 0:
            _migrate_legacy_store()
        if col.count() == 0:
            return []
        res = col.query(
            query_texts=[query],
            n_results=top_k,
            where=_where_task(task_id),
        )
        results = []
        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        for doc, meta, dist in zip(docs, metas, dists):
            # 余弦距离转相似度
            score = round(1.0 - float(dist), 4)
            if score <= 0.01:
                continue
            results.append({
                "content": doc,
                "source": (meta or {}).get("source", "unknown"),
                "score": score,
            })
        return results
    except Exception as e:
        print(f"[rag_service] 搜索失败: {e}")
        return []


def remove_document(doc_id: str, task_id: str = None) -> dict:
    """从知识库中删除文档（支持按任务过滤）"""
    try:
        col = _get_collection()
        before = col.count()
        # 按 source 删除（source 是文件名，doc_id 是去扩展名的文件名）
        # 先按 source 前缀筛选：用 get 找到匹配的 id
        all_docs = col.get()
        ids_to_delete = []
        for _id, meta in zip(all_docs.get("ids", []), all_docs.get("metadatas", [])):
            source = (meta or {}).get("source", "")
            base = os.path.splitext(source)[0].replace(" ", "_")
            if base != doc_id:
                continue
            if task_id and (meta or {}).get("task_id", "default") != task_id:
                continue
            ids_to_delete.append(_id)
        if ids_to_delete:
            col.delete(ids=ids_to_delete)
            return {"success": True, "message": f"已删除文档 '{doc_id}' ({len(ids_to_delete)} 个文本块)"}
        return {"success": False, "message": f"未找到文档 '{doc_id}'"}
    except Exception as e:
        return {"success": False, "message": f"删除失败: {str(e)}"}


def get_document_content(doc_id: str, task_id: str = None) -> dict:
    """获取文档完整内容（拼接所有块）"""
    try:
        col = _get_collection()
        all_docs = col.get()
        chunks = []
        for _id, meta, doc in zip(all_docs.get("ids", []), all_docs.get("metadatas", []), all_docs.get("documents", [])):
            source = (meta or {}).get("source", "")
            base = os.path.splitext(source)[0].replace(" ", "_")
            if base != doc_id:
                continue
            if task_id and (meta or {}).get("task_id", "default") != task_id:
                continue
            chunks.append((int((meta or {}).get("chunk_index", 0)), (meta or {}).get("source", "unknown"), doc))
        if not chunks:
            return {"success": False, "message": f"未找到文档 '{doc_id}'"}
        chunks.sort(key=lambda x: x[0])
        source = chunks[0][1]
        full = "\n\n".join(c[2] for c in chunks)
        return {"success": True, "doc_id": doc_id, "source": source, "content": full, "chunk_count": len(chunks)}
    except Exception as e:
        return {"success": False, "message": f"读取失败: {str(e)}"}


def update_document_content(doc_id: str, new_content: str, task_id: str = None) -> dict:
    """更新文档内容：删除旧块 -> 重新分块 -> 重建索引"""
    try:
        col = _get_collection()
        # 找旧块
        all_docs = col.get()
        old_ids, saved_task_id, source = [], "default", "unknown"
        for _id, meta in zip(all_docs.get("ids", []), all_docs.get("metadatas", [])):
            src = (meta or {}).get("source", "unknown")
            base = os.path.splitext(src)[0].replace(" ", "_")
            if base != doc_id:
                continue
            if task_id and (meta or {}).get("task_id", "default") != task_id:
                continue
            old_ids.append(_id)
            saved_task_id = (meta or {}).get("task_id", "default")
            source = src
        if not old_ids:
            return {"success": False, "message": f"未找到文档 '{doc_id}'"}
        col.delete(ids=old_ids)

        new_chunks = chunk_text(new_content)
        if not new_chunks:
            return {"success": False, "message": "新内容无法提取有效文本"}
        new_meta = _generate_summary_and_tags(new_content)
        ids, docs, metas = [], [], []
        for i, chunk in enumerate(new_chunks):
            ids.append(f"{doc_id}_{i}")
            docs.append(chunk)
            metas.append({
                "task_id": saved_task_id,
                "source": source,
                "chunk_index": i,
                "summary": new_meta["summary"] if i == 0 else "",
                "tags": json.dumps(new_meta["tags"], ensure_ascii=False) if i == 0 else "",
                "difficulty": new_meta["difficulty"] if i == 0 else "",
            })
        col.add(ids=ids, documents=docs, metadatas=metas)
        return {"success": True, "message": f"已更新文档 '{source}'，共 {len(new_chunks)} 个文本块",
                "chunk_count": len(new_chunks), "old_chunks": len(old_ids)}
    except Exception as e:
        return {"success": False, "message": f"更新失败: {str(e)}"}


def list_documents(task_id: str = None) -> List[dict]:
    """列出知识库中的文档（支持按任务过滤）"""
    try:
        col = _get_collection()
        all_docs = col.get()
        docs_map = {}
        for _id, meta, doc in zip(all_docs.get("ids", []), all_docs.get("metadatas", []), all_docs.get("documents", [])):
            m = meta or {}
            if task_id and m.get("task_id", "default") != task_id:
                continue
            source = m.get("source", "unknown")
            if source not in docs_map:
                doc_id_base = os.path.splitext(source)[0].replace(" ", "_")
                docs_map[source] = {
                    "filename": source, "doc_id": doc_id_base, "chunk_count": 0,
                    "sample": "", "summary": "", "tags": [], "difficulty": "",
                }
            docs_map[source]["chunk_count"] += 1
            if not docs_map[source]["sample"]:
                docs_map[source]["sample"] = (doc or "")[:200]
            if int(m.get("chunk_index", 0)) == 0:
                docs_map[source]["summary"] = m.get("summary", "")
                try:
                    docs_map[source]["tags"] = json.loads(m.get("tags", "[]"))
                except Exception:
                    docs_map[source]["tags"] = []
                docs_map[source]["difficulty"] = m.get("difficulty", "")
        return list(docs_map.values())
    except Exception as e:
        print(f"[rag_service] 列出文档失败: {e}")
        return []


def load_knowledge_base_dir(directory: str = None) -> dict:
    """批量加载知识库目录中的文件"""
    if directory is None:
        directory = KNOWLEDGE_BASE_DIR
    if not os.path.exists(directory):
        return {"success": False, "message": f"目录不存在: {directory}"}
    supported_exts = {".pdf", ".docx", ".doc", ".txt", ".md"}
    results = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath):
            continue
        ext = os.path.splitext(filename)[1].lower()
        if ext in supported_exts:
            results.append(add_document(filepath, filename))
    return {"success": True, "message": f"已加载 {len(results)} 个文件", "details": results}
