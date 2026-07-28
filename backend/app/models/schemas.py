from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ===== 聊天相关 =====
class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    stream: bool = True


class ChatResponse(BaseModel):
    message: str
    intent: Optional[dict] = None  # 结构化的教学意图


# ===== 文件上传相关 =====
class FileInfo(BaseModel):
    filename: str
    file_type: str
    size: int
    upload_time: datetime
    parsed_content: Optional[str] = None


# ===== 知识库相关 =====
class KnowledgeDoc(BaseModel):
    id: str
    filename: str
    content: str
    chunk_count: int


class KnowledgeQuery(BaseModel):
    query: str
    top_k: int = 5
    task_id: Optional[str] = None


class KnowledgeSearchResult(BaseModel):
    content: str
    source: str
    score: float


# ===== 课件生成相关 =====
class GenerateRequest(BaseModel):
    intent: dict  # 教学意图结构化数据
    style: Optional[str] = "professional"  # 风格
    include_quiz: bool = True  # 是否包含互动小游戏/测验
    language: str = "zh-CN"


class GenerateResponse(BaseModel):
    ppt_url: Optional[str] = None
    doc_url: Optional[str] = None
    html_url: Optional[str] = None
    message: str


# ===== 知识库编辑相关 =====
class KnowledgeUpdate(BaseModel):
    content: str
# ===== 迭代修改相关 =====
class ReviseRequest(BaseModel):
    file_type: str  # "ppt" | "doc"
    file_path: str
    instruction: str  # 修改意见
    context: Optional[str] = None  # 上下文信息


class ReviseResponse(BaseModel):
    new_file_url: str
    changes: List[str]
    message: str
