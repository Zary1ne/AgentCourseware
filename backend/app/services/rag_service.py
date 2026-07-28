import os
import json
import re
import numpy as np
from typing import List
from app.config import KNOWLEDGE_BASE_DIR
from app.services.file_parser import parse_file

# 向量存储文件路径
VECTOR_STORE_PATH = os.path.join(os.path.dirname(KNOWLEDGE_BASE_DIR), "backend", "vector_store")

# 全局状态
_documents = []      # 文档元数据和内容
_embeddings = None   # numpy 向量矩阵
_vocab = {}          # 词汇表 (用于简单向量化)
_vocab_size = 0


def _load_vector_store():
    """加载持久化的向量存储"""
    global _documents, _embeddings, _vocab, _vocab_size
    try:
        data_path = os.path.join(VECTOR_STORE_PATH, "store.json")
        vec_path = os.path.join(VECTOR_STORE_PATH, "embeddings.npy")
        if os.path.exists(data_path) and os.path.exists(vec_path):
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                _documents = data.get("documents", [])
                _vocab = data.get("vocab", {})
                _vocab_size = data.get("vocab_size", 0)
            _embeddings = np.load(vec_path)
    except Exception:
        _documents = []
        _embeddings = None
        _vocab = {}
        _vocab_size = 0


def _save_vector_store():
    """持久化向量存储"""
    try:
        os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
        data = {
            "documents": _documents,
            "vocab": _vocab,
            "vocab_size": _vocab_size,
        }
        with open(os.path.join(VECTOR_STORE_PATH, "store.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if _embeddings is not None:
            np.save(os.path.join(VECTOR_STORE_PATH, "embeddings.npy"), _embeddings)
    except Exception as e:
        print(f"Failed to save vector store: {e}")


def _build_vocab(texts: List[str], min_df: int = 2):
    """构建词汇表"""
    global _vocab, _vocab_size
    doc_freq = {}
    for text in texts:
        tokens = set(_tokenize(text))
        for token in tokens:
            doc_freq[token] = doc_freq.get(token, 0) + 1

    # 过滤低频词
    vocab_tokens = [t for t, f in doc_freq.items() if f >= min_df]
    _vocab = {token: i for i, token in enumerate(vocab_tokens)}
    _vocab_size = len(_vocab)


def _tokenize(text: str) -> List[str]:
    """简单的中文+英文分词"""
    # 中文：按字符切分，英文：按空格切分
    tokens = []
    # 提取中文字符
    chinese = re.findall(r'[一-鿿]', text)
    tokens.extend(chinese)
    # 提取英文单词
    english = re.findall(r'[a-zA-Z]+', text.lower())
    tokens.extend(english)
    # 提取数字
    numbers = re.findall(r'\d+', text)
    tokens.extend(numbers)
    return tokens


def _text_to_vector(text: str) -> np.ndarray:
    """将文本转为 TF-IDF 风格的向量"""
    if _vocab_size == 0:
        return np.zeros(384, dtype=np.float32)

    tokens = _tokenize(text)
    vec = np.zeros(_vocab_size, dtype=np.float32)

    if not tokens:
        return vec

    # TF 统计
    tf = {}
    for token in tokens:
        if token in _vocab:
            idx = _vocab[token]
            tf[idx] = tf.get(idx, 0) + 1

    # 归一化
    total = len(tokens) or 1
    for idx, count in tf.items():
        vec[idx] = count / total

    return vec


def _cosine_similarity(query_vec: np.ndarray, doc_vecs: np.ndarray) -> np.ndarray:
    """计算余弦相似度"""
    q_norm = np.linalg.norm(query_vec)
    if q_norm == 0:
        return np.zeros(doc_vecs.shape[0])
    d_norms = np.linalg.norm(doc_vecs, axis=1)
    d_norms[d_norms == 0] = 1
    dots = np.dot(doc_vecs, query_vec)
    return dots / (q_norm * d_norms)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """将文本分割成块"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # 尝试在句子边界处分割
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


def add_document(filepath: str, filename: str, task_id: str = "default") -> dict:
    """向知识库添加文档（支持按任务隔离）"""
    global _documents, _embeddings, _vocab, _vocab_size

    # 解析文件
    parse_result = parse_file(filepath, filename)
    if not parse_result["success"]:
        return {"success": False, "message": parse_result["content"], "chunks": 0}

    content = parse_result["content"]
    chunks = chunk_text(content)

    if not chunks:
        return {"success": False, "message": "无法从文件中提取有效文本", "chunks": 0}

    try:
        # 确保已加载
        if not _documents:
            _load_vector_store()

        doc_id_base = os.path.splitext(filename)[0].replace(" ", "_")

        # 生成文档教学摘要、知识点标签和难度评级
        meta = _generate_summary_and_tags(content)

        # 新建文档块（带 task_id）
        new_docs = []
        for i, chunk in enumerate(chunks):
            new_docs.append({
                "id": f"{doc_id_base}_{i}",
                "source": filename,
                "chunk_index": i,
                "content": chunk,
                "task_id": task_id,
                "summary": meta["summary"] if i == 0 else "",
                "tags": meta["tags"] if i == 0 else [],
                "difficulty": meta["difficulty"] if i == 0 else "",
            })

        # 重建词汇表（包含新文档）
        all_contents = [d["content"] for d in _documents] + [d["content"] for d in new_docs]
        _build_vocab(all_contents)

        # 重建所有向量
        all_vectors = []
        for doc in _documents + new_docs:
            vec = _text_to_vector(doc["content"])
            all_vectors.append(vec)

        _documents = _documents + new_docs
        _embeddings = np.array(all_vectors, dtype=np.float32)

        _save_vector_store()

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
    global _documents, _embeddings

    if not _documents:
        _load_vector_store()

    if not _documents or _embeddings is None:
        return []

    # 构建过滤掩码
    mask = None
    if task_id:
        mask = [d.get("task_id", "default") == task_id for d in _documents]

    try:
        query_vec = _text_to_vector(query)
        scores = _cosine_similarity(query_vec, _embeddings)

        # 非目标任务的文档置零
        if mask is not None:
            for i in range(len(scores)):
                if not mask[i]:
                    scores[i] = 0

        # 取 top_k
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0.01:
                doc = _documents[idx]
                results.append({
                    "content": doc["content"],
                    "source": doc.get("source", "unknown"),
                    "score": round(float(scores[idx]), 4),
                })

        return results
    except Exception as e:
        print(f"Search error: {e}")
        return []


def remove_document(doc_id: str, task_id: str = None) -> dict:
    """从知识库中删除文档（支持按任务过滤）"""
    global _documents, _embeddings

    if not _documents:
        _load_vector_store()

    original_count = len(_documents)

    def should_remove(d):
        if not d["id"].startswith(doc_id):
            return False
        if task_id and d.get("task_id", "default") != task_id:
            return False
        return True

    _documents = [d for d in _documents if not should_remove(d)]
    removed = original_count - len(_documents)

    if removed > 0:
        # 重建词汇表和向量
        if _documents:
            all_contents = [d["content"] for d in _documents]
            _build_vocab(all_contents)
            _embeddings = np.array([_text_to_vector(d["content"]) for d in _documents], dtype=np.float32)
        else:
            _embeddings = None
            _vocab = {}
            _vocab_size = 0

        _save_vector_store()
        return {"success": True, "message": f"已删除文档 '{doc_id}' ({removed} 个文本块)"}
    return {"success": False, "message": f"未找到文档 '{doc_id}'"}


def get_document_content(doc_id: str, task_id: str = None) -> dict:
    """获取文档的完整内容（拼接所有文本块，支持按任务过滤）"""
    global _documents
    if not _documents:
        _load_vector_store()

    chunks = [d for d in _documents if d["id"].startswith(doc_id)]
    if task_id:
        chunks = [d for d in chunks if d.get("task_id", "default") == task_id]
    if not chunks:
        return {"success": False, "message": f"未找到文档 '{doc_id}'"}

    # 按 chunk_index 排序后拼接
    chunks.sort(key=lambda d: d["chunk_index"])
    full_content = "\n\n".join([c["content"] for c in chunks])
    source = chunks[0].get("source", "unknown")

    return {
        "success": True,
        "doc_id": doc_id,
        "source": source,
        "content": full_content,
        "chunk_count": len(chunks),
    }


def update_document_content(doc_id: str, new_content: str, task_id: str = None) -> dict:
    """更新文档内容：删除旧块 -> 重新分块 -> 重建索引（支持按任务过滤）"""
    global _documents, _embeddings, _vocab, _vocab_size

    if not _documents:
        _load_vector_store()

    old_chunks = [d for d in _documents if d["id"].startswith(doc_id)]
    if task_id:
        old_chunks = [d for d in old_chunks if d.get("task_id", "default") == task_id]
    if not old_chunks:
        return {"success": False, "message": f"未找到文档 '{doc_id}'"}

    source = old_chunks[0].get("source", "unknown")
    saved_task_id = old_chunks[0].get("task_id", "default")

    # 删除旧块
    _documents = [d for d in _documents if not (d["id"].startswith(doc_id) and (not task_id or d.get("task_id", "default") == task_id))]

    # 重新分块
    new_chunks = chunk_text(new_content)
    if not new_chunks:
        return {"success": False, "message": "新内容无法提取有效文本"}

    # 创新点：内容更新后重新生成摘要、标签和难度评级
    new_meta = _generate_summary_and_tags(new_content)

    # 添加新块（保留原 task_id）
    for i, chunk in enumerate(new_chunks):
        _documents.append({
            "id": f"{doc_id}_{i}",
            "source": source,
            "chunk_index": i,
            "content": chunk,
            "task_id": saved_task_id,
            "summary": new_meta["summary"] if i == 0 else "",
            "tags": new_meta["tags"] if i == 0 else [],
            "difficulty": new_meta["difficulty"] if i == 0 else "",
        })

    # 重建词汇表和向量
    all_contents = [d["content"] for d in _documents]
    _build_vocab(all_contents)
    _embeddings = np.array([_text_to_vector(d["content"]) for d in _documents], dtype=np.float32)

    _save_vector_store()

    return {
        "success": True,
        "message": f"已更新文档 '{source}'，共 {len(new_chunks)} 个文本块",
        "chunk_count": len(new_chunks),
        "old_chunks": len(old_chunks),
    }


def list_documents(task_id: str = None) -> List[dict]:
    """列出知识库中的文档（支持按任务过滤）"""
    global _documents
    if not _documents:
        _load_vector_store()

    if not _documents:
        return []

    # 按源文件分组（可选 task_id 过滤）
    docs_map = {}
    for doc in _documents:
        if task_id and doc.get("task_id", "default") != task_id:
            continue
        source = doc.get("source", "unknown")
        if source not in docs_map:
            doc_id_base = os.path.splitext(source)[0].replace(" ", "_")
            docs_map[source] = {
                "filename": source, "doc_id": doc_id_base, "chunk_count": 0,
                "sample": "", "summary": "", "tags": [], "difficulty": "",
            }
        docs_map[source]["chunk_count"] += 1
        if not docs_map[source]["sample"]:
            docs_map[source]["sample"] = doc["content"][:200]
        # 从首个文本块读取摘要、标签和难度
        if doc.get("chunk_index", 0) == 0:
            docs_map[source]["summary"] = doc.get("summary", "")
            docs_map[source]["tags"] = doc.get("tags", [])
            docs_map[source]["difficulty"] = doc.get("difficulty", "")

    return list(docs_map.values())


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
            result = add_document(filepath, filename)
            results.append(result)

    return {
        "success": True,
        "message": f"已加载 {len(results)} 个文件",
        "details": results,
    }
