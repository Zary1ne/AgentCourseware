"""Chroma 向量库封装。

- 持久化路径：VECTOR_STORE_PATH（见 config.py）
- 嵌入模型：使用本地哈希词袋嵌入（HashBag），无需联网、无需下载 ONNX 模型，
  跨进程稳定，避免首次运行因下载 79MB 模型卡死。
- 对外暴露与原 rag_service 完全一致的函数签名，chat.py / knowledge.py 无需改动。
"""
import os
import json
import re
import hashlib
import threading
from typing import List

import chromadb
from chromadb.config import Settings
from app.config import VECTOR_STORE_PATH

# ===== 嵌入函数：本地哈希词袋（无需联网下载） =====
_embedding_fn = None
_embedding_lock = threading.Lock()


def _tokenize(text: str) -> List[str]:
    """中英混合分词（与旧实现一致）"""
    tokens = []
    tokens.extend(re.findall(r'[一-鿿]', text))
    tokens.extend(re.findall(r'[a-zA-Z]+', text.lower()))
    tokens.extend(re.findall(r'\d+', text))
    return tokens


class _HashBagEmbeddingFunction:
    """离线兜底嵌入：哈希词袋 + L2 归一化，维度 384。

    实现 chromadb 1.x EmbeddingFunction 协议所需方法：
    __call__（文档嵌入）、embed_query（查询嵌入）、name。
    """
    DIM = 384

    def __call__(self, input):
        """嵌入一批文档"""
        return [self._vec(t) for t in input]

    def embed_query(self, input):
        """嵌入查询文本（与文档嵌入用同一逻辑）"""
        return [self._vec(t) for t in input]

    def _vec(self, text: str):
        v = [0.0] * self.DIM
        for tok in _tokenize(text):
            # 用 md5 的前 4 字节做确定性哈希（跨进程稳定，不依赖 PYTHONHASHSEED）
            h = int.from_bytes(hashlib.md5(tok.encode()).digest()[:4], "big")
            v[h % self.DIM] += 1.0
        norm = sum(x * x for x in v) ** 0.5
        if norm > 0:
            v = [x / norm for x in v]
        return v

    def name(self):
        return "hash_bag_fallback"

    def build_from_config(self, config):
        return self

    def get_config(self):
        return {}


def _get_embedding_function():
    """获取嵌入函数。

    注意：原本优先尝试 Chroma 默认 ONNX 嵌入（all-MiniLM-L6-v2），但首次
    运行需联网下载 79MB 模型。为避免在网络差/代理未开的环境下卡住整个
    对话请求，这里直接使用本地确定性 HashBag 嵌入，无需下载、无需联网、
    跨进程稳定。
    """
    global _embedding_fn
    if _embedding_fn is not None:
        return _embedding_fn
    with _embedding_lock:
        if _embedding_fn is not None:
            return _embedding_fn
        _embedding_fn = _HashBagEmbeddingFunction()
        print("[chroma_store] 使用本地哈希词袋嵌入（无需联网下载）")
        return _embedding_fn


# ===== Chroma 客户端（单例） =====
_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    _client = chromadb.PersistentClient(
        path=VECTOR_STORE_PATH,
        settings=Settings(anonymized_telemetry=False, allow_reset=True),
    )
    _collection = _client.get_or_create_collection(
        name="teaching_agent_kb",
        metadata={"hnsw:space": "cosine"},  # 余弦相似度
        embedding_function=_get_embedding_function(),
    )
    return _collection


def _where_task(task_id: str = None):
    """构造 Chroma where 过滤条件"""
    if task_id:
        return {"task_id": task_id}
    return None
