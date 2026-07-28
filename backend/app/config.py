import os
from dotenv import load_dotenv

load_dotenv()

# LLM 配置
LLM_API_KEY = os.getenv("LLM_API_KEY", "your-api-key-here")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

# 服务配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# 目录配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_BASE_DIR = os.getenv("KNOWLEDGE_BASE_DIR", os.path.join(os.path.dirname(BASE_DIR), "knowledge_base"))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join(BASE_DIR, "outputs"))

# 向量存储目录
VECTOR_STORE_PATH = os.path.join(BASE_DIR, "vector_store")

# 确保目录存在
for d in [UPLOAD_DIR, OUTPUT_DIR, VECTOR_STORE_PATH]:
    os.makedirs(d, exist_ok=True)
